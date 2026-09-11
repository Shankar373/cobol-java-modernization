"""SourceMap — byte-offset to (line, column) translation.

The architecture (§6 of docs/PHASE_2_ARCHITECTURE_V2.md) requires
that source provenance be stable across encodings. We translate
**byte offsets** to (line, column) positions, not Python
character indices.

Indexing convention:

    line:    1-based. The first line of a file is line 1.
    column:  0-based. The first byte of a line is at column 0.
             (This matches the existing ``modernize_v2.ir.diagnostic.SourcePosition``
             convention.)
    byte_offset:
             0-based. The first byte of the file is at byte_offset 0.

Edge cases:

    offset 0         -> line 1, column 0
    offset at '\n'   -> the newline is on the current line; the
                        next byte starts the next line.
    offset at EOF    -> the position one-past the last byte.
                        line is the number of the last line;
                        column is the length of that line in bytes.
    offset > EOF     -> rejected.
    negative offset  -> rejected.

UTF-8 handling:

    The map is built from the raw bytes. Newline detection
    uses a single-byte check (``b"\n"``); a CR-only file
    (``b"\\r"``) is not treated as line-oriented. The map
    does **not** decode the file to characters. The column
    is the byte offset from the start of the line, which is
    what the rest of the V2 pipeline (e.g. ``id_for_node``)
    needs to construct deterministic ids.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final

from modernize_v2.ir.diagnostic import SourcePosition
from modernize_v2.source.workspace import SourceFile


# Sentinel used as the column "after the last byte of a line".
# We never store a column greater than the line's length in
# bytes; EOF is the only place where column can equal the line
# length.
MAX_LINE_BYTES: Final[int] = 16 * 1024 * 1024  # 16 MiB per line


class SourceMapError(ValueError):
    """Raised for invalid source-map queries.

    ``ValueError`` is the base so callers may catch either.
    """


def _build_line_starts(raw_bytes: bytes) -> tuple[int, ...]:
    """Compute the byte offset where each line begins.

    The result is a tuple of byte offsets, in strictly
    increasing order. The first entry is 0. There is one entry
    per line. A trailing newline introduces the start of a
    (possibly empty) final line at offset ``len(raw_bytes)``.

    The tuple contains **line starts only**; it does not
    contain an end-of-file sentinel unless the file ends with
    a newline. The file's total size is stored separately on
    ``SourceMap.byte_size`` and is the authoritative bound for
    offset validation.
    """
    if not isinstance(raw_bytes, bytes):
        raise SourceMapError("raw_bytes must be bytes")
    starts = [0]
    for i, b in enumerate(raw_bytes):
        if b == 0x0A:  # b"\n"
            starts.append(i + 1)
    return tuple(starts)


def byte_to_position(
    line_starts: tuple[int, ...],
    byte_offset: int,
    *,
    file_size: int | None = None,
) -> SourcePosition:
    """Translate a byte offset to a ``SourcePosition``.

    The ``line_starts`` tuple is a precomputed index. The
    function is pure: it does no IO and does no decoding.

    The function is exposed for callers that want to compute
    positions without instantiating a ``SourceMap``. The
    ``SourceMap`` class is the typical user.
    """
    if not isinstance(line_starts, tuple):
        raise SourceMapError("line_starts must be a tuple of ints")
    if not line_starts:
        raise SourceMapError("line_starts must be non-empty")
    if line_starts[0] != 0:
        raise SourceMapError("line_starts must begin at 0")
    if any(line_starts[i] >= line_starts[i + 1] for i in range(len(line_starts) - 1)):
        raise SourceMapError("line_starts must be strictly increasing")
    if not isinstance(byte_offset, int) or byte_offset < 0:
        raise SourceMapError(
            f"byte_offset must be a non-negative int, got {byte_offset!r}"
        )
    # Locate the line. The byte offset must be within
    # [0, file_size]; offsets beyond are rejected.
    if file_size is not None and byte_offset > file_size:
        raise SourceMapError(
            f"byte_offset {byte_offset} is past file size {file_size}"
        )
    if file_size is None and byte_offset > line_starts[-1]:
        raise SourceMapError(
            f"byte_offset {byte_offset} is past the last line start "
            f"{line_starts[-1]} and no file_size was provided"
        )

    # Find the line containing byte_offset. Linear scan is
    # sufficient for the file sizes we expect; a binary search
    # could be added in T-2B-02+ if profiling demands it.
    line_index = 0
    for i in range(len(line_starts) - 1):
        if line_starts[i + 1] > byte_offset:
            line_index = i
            break
    else:
        # byte_offset is at or past the last line start; if
        # exactly equal, the line index is the last line.
        line_index = len(line_starts) - 1

    line = line_index + 1  # 1-based
    column = byte_offset - line_starts[line_index]
    return SourcePosition(line=line, column=column, byte_offset=byte_offset)


@dataclass(frozen=True)
class SourceMap:
    """An immutable byte-offset index for a ``SourceFile``.

    The map is built once from the source bytes. Once built,
    all queries are O(line) in the number of newlines (linear
    scan over ``line_starts``). For typical COBOL/JCL files
    (a few hundred to a few thousand lines), this is fine; a
    binary search can be added later if profiling demands.

    The map is *immutable*: the underlying tuple of line
    starts cannot change. Adding a new file to a workspace
    produces a new ``SourceMap``, not a mutation.
    """

    source_file: SourceFile
    line_starts: tuple[int, ...]
    byte_size: int

    def __post_init__(self) -> None:
        if not isinstance(self.source_file, SourceFile):
            raise TypeError("source_file must be a SourceFile")
        if not isinstance(self.line_starts, tuple):
            raise TypeError("line_starts must be a tuple of ints")
        if not self.line_starts:
            raise ValueError("line_starts must be non-empty")
        if self.line_starts[0] != 0:
            raise ValueError("line_starts[0] must be 0")
        for i in range(len(self.line_starts) - 1):
            if self.line_starts[i] >= self.line_starts[i + 1]:
                raise ValueError(
                    f"line_starts not strictly increasing at index {i}: "
                    f"{self.line_starts[i]} >= {self.line_starts[i + 1]}"
                )
        if not isinstance(self.byte_size, int) or self.byte_size < 0:
            raise ValueError("byte_size must be a non-negative int")
        if self.line_starts[-1] > self.byte_size:
            raise ValueError(
                f"last line start ({self.line_starts[-1]}) exceeds "
                f"byte_size ({self.byte_size})"
            )

    @classmethod
    def from_bytes(
        cls,
        source_file: SourceFile,
        raw_bytes: bytes,
    ) -> "SourceMap":
        """Build a ``SourceMap`` for ``source_file`` from bytes.

        The byte size of ``raw_bytes`` is verified against
        ``source_file.byte_size``. A mismatch is a hard error:
        the workspace invariant is that ``SourceFile.byte_size``
        equals the actual byte count of the source.
        """
        if not isinstance(source_file, SourceFile):
            raise TypeError("source_file must be a SourceFile")
        if not isinstance(raw_bytes, bytes):
            raise TypeError("raw_bytes must be bytes")
        if len(raw_bytes) != source_file.byte_size:
            raise SourceMapError(
                f"raw_bytes length {len(raw_bytes)} does not match "
                f"source_file.byte_size {source_file.byte_size} for "
                f"{source_file.canonical_path!r}"
            )
        # Verify the content hash too. The map is the only
        # point that sees the bytes after the workspace has
        # accepted the file; if the hash is wrong, the file
        # identity is compromised.
        import hashlib
        actual_hash = hashlib.sha256(raw_bytes).hexdigest()
        if actual_hash != source_file.content_hash:
            raise SourceMapError(
                f"content hash mismatch for {source_file.canonical_path!r}: "
                f"file says {source_file.content_hash}, bytes say "
                f"{actual_hash}"
            )
        line_starts = _build_line_starts(raw_bytes)
        return cls(
            source_file=source_file,
            line_starts=line_starts,
            byte_size=len(raw_bytes),
        )

    def line_count(self) -> int:
        """Return the number of lines in the source.

        A file with no newlines has one line. A file ending
        with a newline has ``len(newlines)`` lines (the trailing
        newline does not start a new empty line, but a file
        ending with ``a\nb\n`` has two lines and the
        line_starts tuple is ``[0, 2, 4]``).
        """
        # The number of lines is the number of line starts.
        return len(self.line_starts)

    def position_at(self, byte_offset: int) -> SourcePosition:
        """Translate a byte offset to a ``SourcePosition``.

        ``byte_offset`` must be in ``[0, byte_size]``. The
        position at ``byte_size`` is the EOF position.
        """
        return byte_to_position(
            self.line_starts,
            byte_offset,
            file_size=self.byte_size,
        )

    def position_at_line_column(
        self, line: int, column: int
    ) -> SourcePosition:
        """Translate a (line, column) pair to a ``SourcePosition``.

        ``line`` is 1-based; ``column`` is 0-based. The column
        is interpreted as a **byte offset** from the start of
        the line, not a character offset. UTF-8 callers must
        pass the byte offset of the column.
        """
        if not isinstance(line, int) or line < 1:
            raise SourceMapError(f"line must be >= 1, got {line!r}")
        if not isinstance(column, int) or column < 0:
            raise SourceMapError(f"column must be >= 0, got {column!r}")
        if line > len(self.line_starts):
            raise SourceMapError(
                f"line {line} exceeds line count {len(self.line_starts)}"
            )
        start = self.line_starts[line - 1]
        # The line ends at the next line start (or at byte_size
        # for the last line). The newline itself belongs to the
        # line that it terminates, so a column equal to the full
        # line length is only a valid position at end-of-file
        # (i.e. on the final line); on earlier lines it would
        # alias the first byte of the following line and is
        # rejected.
        is_last_line = line == len(self.line_starts)
        next_start = (
            self.byte_size
            if is_last_line
            else self.line_starts[line]
        )
        line_length = next_start - start
        max_column = line_length if is_last_line else line_length - 1
        if column > max_column:
            raise SourceMapError(
                f"column {column} exceeds line length "
                f"{line_length} on line {line}"
            )
        return SourcePosition(
            line=line,
            column=column,
            byte_offset=start + column,
        )

    def line_start_byte(self, line: int) -> int:
        """Return the byte offset where ``line`` begins.

        ``line`` is 1-based. This is useful for the lexer
        (T-2B-02) to slice a line out of the raw bytes.
        """
        if not isinstance(line, int) or line < 1:
            raise SourceMapError(f"line must be >= 1, got {line!r}")
        if line > len(self.line_starts):
            raise SourceMapError(
                f"line {line} exceeds line count {len(self.line_starts)}"
            )
        return self.line_starts[line - 1]


__all__ = [
    "MAX_LINE_BYTES",
    "SourceMap",
    "SourceMapError",
    "byte_to_position",
]
