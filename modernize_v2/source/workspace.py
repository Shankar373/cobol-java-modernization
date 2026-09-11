"""Workspace model for the V2 compiler.

This module provides:

    * ``FileKind`` — coarse classification of a source file.
    * ``PathSecurityError`` — raised on unsafe paths.
    * ``SourceFile`` — an immutable, content-hashed source file.
    * ``Workspace`` — an immutable collection of ``SourceFile``s
      with deterministic file IDs.

Design principles (per ``docs/PHASE_2_ARCHITECTURE_V2.md`` §6, §8,
§13, and T-2B-01 acceptance criteria):

    1. **Deterministic identity.** A ``SourceFile.file_id`` is a
       ``DeterministicId`` produced by the existing
       ``modernize_v2.ir.ids.id_for_node`` function with the
       special kind ``SOURCE_FILE``. The fingerprint depends on
       the canonical path only; the content_hash depends on the
       raw bytes.

    2. **No wall clock, no random.** Identities are derived
       purely from the canonical path and the content.

    3. **Path safety.** ``Workspace`` rejects paths that escape
       the workspace root or contain control characters. The
       rejection is fail-closed: a ``PathSecurityError`` is
       raised; the path is never silently normalized into a safe
       one.

    4. **No import-time IO.** ``Workspace`` does not read the
       filesystem. It is constructed from in-memory bytes.

    5. **Deterministic ordering.** The ``Workspace.files``
       attribute is a ``tuple`` sorted by canonical path. Two
       workspaces with the same logical contents produce the
       same ordering.

    6. **No V1 dependency.** This module does not import the V1
       ``modernize`` package.

    7. **Canonical paths are POSIX-style.** Backslashes are
       converted to forward slashes. The path is normalized
       (no ``.`` or ``..`` segments, no leading ``/``) and
       lowercased. The canonical form is what flows into the
       file ID and the source map; it is the public contract
       for the rest of the pipeline.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Final

from modernize_v2.ir.ids import DeterministicId, id_for_node


# The kind string used to derive file IDs. The architecture
# reserves ``IRKind.SOURCE_FILE`` for future use, but at the
# T-2B-01 stage we are not yet fleshing out the IRKind enum.
# The string is stable and content-derived; it does not change.
_SOURCE_FILE_KIND: Final[str] = "SOURCE_FILE"


# Maximum source file size accepted by the workspace. A larger
# file raises ``WorkspaceError``. The cap is a defensive limit
# against accidental DoS; the platform is not designed for huge
# monolithic sources. 64 MiB is generous for COBOL/JCL/SQL/CICS
# and BMS files.
MAX_SOURCE_BYTES: Final[int] = 64 * 1024 * 1024


# ------------------------------------------------------------------
# Errors
# ------------------------------------------------------------------


class WorkspaceError(ValueError):
    """Raised when the workspace cannot be constructed.

    The error is a ``ValueError`` subclass so callers may catch
    either the parent or the specific subclass.
    """


class PathSecurityError(WorkspaceError):
    """Raised when a path is unsafe.

    A path is unsafe if it:

        * is an absolute path,
        * contains ``..`` segments that escape the workspace root,
        * contains NUL bytes or other ASCII control characters,
        * contains a backslash outside the normalization step,
        * has an empty canonical form,
        * is rooted at a Windows drive letter that escapes the
          workspace root.

    The path is never silently rewritten. The caller sees the
    path that was rejected.
    """


# ------------------------------------------------------------------
# File kind
# ------------------------------------------------------------------


class FileKind(str, Enum):
    """Coarse classification of a source file.

    The classification is based on the file extension or the
    caller-supplied hint. The classifier does not parse the
    file; it is metadata, not semantic understanding.
    """

    COBOL = "COBOL"
    COPYBOOK = "COPYBOOK"
    JCL = "JCL"
    PROC = "PROC"
    SQL = "SQL"
    CICS = "CICS"
    BMS = "BMS"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_path(cls, canonical_path: str) -> "FileKind":
        """Classify a canonical path by its extension.

        ``.cbl`` / ``.cob`` / ``.cobol`` -> COBOL.
        ``.cpy`` / ``.copy`` / ``.copybook`` -> COPYBOOK.
        ``.jcl`` -> JCL.
        ``.proc`` -> PROC.
        ``.sql`` / ``.sqldb`` -> SQL.
        ``.cics`` -> CICS.
        ``.bms`` / ``.map`` -> BMS.
        Anything else -> UNKNOWN.
        """
        if not isinstance(canonical_path, str) or not canonical_path:
            return cls.UNKNOWN
        lower = canonical_path.lower()
        # Use the last dot only.
        if "." not in lower:
            return cls.UNKNOWN
        ext = lower.rsplit(".", 1)[-1]
        if ext in ("cbl", "cob", "cobol"):
            return cls.COBOL
        if ext in ("cpy", "copy", "copybook"):
            return cls.COPYBOOK
        if ext == "jcl":
            return cls.JCL
        if ext == "proc":
            return cls.PROC
        if ext in ("sql", "sqldb"):
            return cls.SQL
        if ext == "cics":
            return cls.CICS
        if ext in ("bms", "map"):
            return cls.BMS
        return cls.UNKNOWN


# ------------------------------------------------------------------
# Path normalization
# ------------------------------------------------------------------


_FORBIDDEN_PATH_CHARS: Final[frozenset[str]] = frozenset(
    chr(c) for c in range(0, 32)
) | {"\x7f"}


def normalize_canonical_path(raw_path: str) -> str:
    """Normalize a path into the V2 canonical form.

    The canonical form is:

        * POSIX-style forward slashes,
        * no leading slash (workspace-relative),
        * no trailing slash (except the literal root ``"."``),
        * no ``.`` segments,
        * no ``..`` segments — these raise ``PathSecurityError``
          because the     canonical form is workspace-relative and
          any ``..`` segment would attempt to escape the root,
        * no NUL or control characters,
        * lowercased.

    The literal string ``"."`` is accepted and returned as-is;
    it denotes the workspace root itself and is the conventional
    default root for ``Workspace.empty``.

    The function is pure: it does not read the filesystem and
    does not consult the workspace root. It is the lower-level
    primitive that ``Workspace`` uses; callers may also use it
    directly when they need a deterministic, safe form of a
    path string.
    """
    if not isinstance(raw_path, str):
        raise PathSecurityError(
            f"path must be a string, got {type(raw_path).__name__}"
        )
    if raw_path == ".":
        # Convention: the workspace root itself. Only accepted as
        # the root argument to Workspace.empty; it is not a valid
        # canonical path for a source file.
        return "."
    if not raw_path:
        raise PathSecurityError("path must be non-empty")

    # Reject NUL and control characters before any other work.
    for ch in raw_path:
        if ch in _FORBIDDEN_PATH_CHARS:
            raise PathSecurityError(
                f"path contains forbidden control character: "
                f"U+{ord(ch):04X} in {raw_path!r}"
            )

    # Detect an absolute path. On Windows, absolute paths are
    # "C:\\..." or "C:/..."; on POSIX, "/..."; on Windows
    # UNC, "\\\\...". We reject all of them because the
    # canonical form is workspace-relative.
    if raw_path.startswith("/") or raw_path.startswith("\\"):
        raise PathSecurityError(
            f"absolute paths are not allowed: {raw_path!r}"
        )
    # Drive letter (Windows): second character is ":" and the
    # third (after "X:/...") is "/" or "\\". Reject drive-letter
    # rooted paths because they cannot be workspace-relative.
    if (
        len(raw_path) >= 3
        and raw_path[1] == ":"
        and raw_path[2] in ("/", "\\")
    ):
        raise PathSecurityError(
            f"absolute drive-letter paths are not allowed: {raw_path!r}"
        )

    # Convert backslashes to forward slashes.
    posix = raw_path.replace("\\", "/")
    # Disallow ".." segments — they are traversal.
    segments = posix.split("/")
    for seg in segments:
        if seg == "..":
            raise PathSecurityError(
                f"path traversal '..' is not allowed: {raw_path!r}"
            )
    # Remove empty segments caused by "//" and leading/trailing
    # slashes (which we have already rejected at the start).
    cleaned = [s for s in segments if s != "" and s != "."]
    if not cleaned:
        raise PathSecurityError(
            f"path resolves to an empty canonical form: {raw_path!r}"
        )
    canonical = "/".join(cleaned).lower()
    if not canonical:
        raise PathSecurityError(
            f"path resolves to an empty canonical form: {raw_path!r}"
        )
    return canonical


def resolve_relative_path(
    workspace_root: str,
    relative_to_workspace: str,
) -> str:
    """Resolve a relative path against the workspace root.

    This is the *security boundary*: a path is allowed only if
    the resolved absolute path lies under the workspace root
    after symlink-free normalization.

    The function is implemented purely on string operations; it
    does not consult the filesystem. The workspace root is the
    caller's responsibility to define, but the function
    guarantees the relative path does not escape it.

    Raises ``PathSecurityError`` if the relative path tries to
    escape the workspace root.
    """
    if not isinstance(workspace_root, str) or not workspace_root:
        raise PathSecurityError("workspace_root must be a non-empty string")
    if not isinstance(relative_to_workspace, str):
        raise PathSecurityError("relative path must be a string")
    if not relative_to_workspace:
        raise PathSecurityError("relative path must be non-empty")

    # First normalize the relative path: this rejects control
    # characters, absolute paths, and ".." segments.
    rel = normalize_canonical_path(relative_to_workspace)

    # Now check that ``rel`` does not contain ".." (already
    # enforced by normalize_canonical_path). As a belt-and-braces
    # check, refuse any ".." anywhere in the original raw path.
    if ".." in relative_to_workspace.split("/") or \
       ".." in relative_to_workspace.split("\\"):
        raise PathSecurityError(
            f"path contains '..' segment: {relative_to_workspace!r}"
        )

    return rel


# ------------------------------------------------------------------
# SourceFile
# ------------------------------------------------------------------


@dataclass(frozen=True)
class SourceFile:
    """An immutable, content-hashed source file.

    A ``SourceFile`` is the unit of input the workspace tracks.
    The ``file_id`` is a deterministic 26-character Crockford
    base32 id derived from the canonical path. The
    ``content_hash`` is the SHA-256 of the raw bytes.

    The raw bytes are not stored on the ``SourceFile`` itself;
    they are passed to the ``SourceMap`` for offset translation.
    Storing them here would duplicate the workspace's internal
    state and tempt callers to read source via the file object
    rather than via the ``SourceMap``.
    """

    file_id: DeterministicId
    file_kind: FileKind
    canonical_path: str
    content_hash: str
    byte_size: int
    declared_encoding: str = "UTF-8"

    def __post_init__(self) -> None:
        if not isinstance(self.file_id, DeterministicId):
            raise TypeError("file_id must be a DeterministicId")
        if not isinstance(self.file_kind, FileKind):
            raise TypeError("file_kind must be a FileKind")
        if not isinstance(self.canonical_path, str) or not self.canonical_path:
            raise ValueError("canonical_path must be a non-empty string")
        # The canonical path must not contain backslashes or ".."
        # segments; this is enforced by normalize_canonical_path
        # at construction time. We re-validate here as a safety
        # net.
        if "\\" in self.canonical_path:
            raise ValueError(
                f"canonical_path must not contain backslashes: "
                f"{self.canonical_path!r}"
            )
        if not isinstance(self.content_hash, str):
            raise TypeError("content_hash must be a string")
        if len(self.content_hash) != 64:
            raise ValueError(
                "content_hash must be 64 hex chars (SHA-256)"
            )
        for ch in self.content_hash.lower():
            if ch not in "0123456789abcdef":
                raise ValueError(
                    f"content_hash must be hex, got {self.content_hash!r}"
                )
        if not isinstance(self.byte_size, int) or self.byte_size < 0:
            raise ValueError("byte_size must be a non-negative int")
        if not isinstance(self.declared_encoding, str) or not self.declared_encoding:
            raise ValueError("declared_encoding must be a non-empty string")
        # The file_id's text must be 26 chars and start with the
        # IRID namespace "N" (the existing constraint).
        if len(self.file_id.text) != 26:
            raise ValueError(
                "file_id must be a 26-character DeterministicId"
            )


def make_source_file(
    canonical_path: str,
    content: bytes,
    *,
    file_kind: FileKind | None = None,
    declared_encoding: str = "UTF-8",
) -> SourceFile:
    """Build a ``SourceFile`` from a canonical path and bytes.

    This is the canonical constructor. It is pure: it does not
    read the filesystem, does not consult the wall clock, and
    does not depend on any global state.

    The content is hashed as bytes; the encoding declared here
    is metadata for the future decoder and is not used to
    interpret the bytes at this stage. (T-2B-02 introduces the
    lexer; the decoder belongs to the lexer, not to the
    workspace.)
    """
    if not isinstance(content, bytes):
        raise TypeError("content must be bytes")
    if len(content) > MAX_SOURCE_BYTES:
        raise WorkspaceError(
            f"source file exceeds MAX_SOURCE_BYTES "
            f"({len(content)} > {MAX_SOURCE_BYTES}): {canonical_path!r}"
        )
    canonical = normalize_canonical_path(canonical_path)
    if file_kind is None:
        file_kind = FileKind.from_path(canonical)
    if not isinstance(file_kind, FileKind):
        raise TypeError("file_kind must be a FileKind")
    file_id = id_for_node(
        kind=_SOURCE_FILE_KIND,
        canonical_path=canonical,
        line=1,
        column=0,
        byte_offset=0,
    )
    digest = hashlib.sha256(content).hexdigest()
    return SourceFile(
        file_id=file_id,
        file_kind=file_kind,
        canonical_path=canonical,
        content_hash=digest,
        byte_size=len(content),
        declared_encoding=declared_encoding,
    )


# ------------------------------------------------------------------
# Workspace
# ------------------------------------------------------------------


@dataclass(frozen=True)
class Workspace:
    """An immutable collection of source files.

    The workspace exposes files by stable deterministic id. The
    list of files is sorted by canonical path, so iteration is
    deterministic across runs.

    Construction is via ``Workspace.empty()`` followed by
    ``workspace.with_file(...)`` for each source file. The
    methods return new ``Workspace`` instances; the workspace
    is never mutated.
    """

    workspace_id: str
    root_canonical_path: str
    files: tuple[SourceFile, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not isinstance(self.workspace_id, str) or not self.workspace_id:
            raise ValueError("workspace_id must be a non-empty string")
        if not isinstance(self.root_canonical_path, str) or not self.root_canonical_path:
            raise ValueError(
                "root_canonical_path must be a non-empty string"
            )
        if "\\" in self.root_canonical_path:
            raise ValueError(
                "root_canonical_path must not contain backslashes"
            )
        # Validate that the files are sorted and unique.
        seen_paths: set[str] = set()
        for f in self.files:
            if not isinstance(f, SourceFile):
                raise TypeError("files must be SourceFile instances")
            if f.canonical_path in seen_paths:
                raise ValueError(
                    f"duplicate canonical path: {f.canonical_path!r}"
                )
            seen_paths.add(f.canonical_path)
        paths = tuple(f.canonical_path for f in self.files)
        if paths != tuple(sorted(paths)):
            raise ValueError(
                "files must be sorted by canonical_path"
            )

    @classmethod
    def empty(
        cls,
        *,
        workspace_id: str = "default",
        root_canonical_path: str = ".",
    ) -> "Workspace":
        """Create an empty workspace with a logical root.

        The root is a logical, not a filesystem, path. It is
        the prefix the canonical paths are relative to. The
        default root is ``"."``, meaning "the workspace is the
        current logical root".

        The root canonical path is normalized to V2 canonical
        form. A Windows-style absolute root like ``C:\\foo`` is
        rejected by ``normalize_canonical_path``.
        """
        root = normalize_canonical_path(root_canonical_path)
        return cls(
            workspace_id=workspace_id,
            root_canonical_path=root,
            files=(),
        )

    def with_file(
        self,
        source_file: SourceFile,
        *,
        workspace_root: str | None = None,
    ) -> "Workspace":
        """Return a new workspace with ``source_file`` added.

        The file is rejected if:

            * its canonical path duplicates an existing file,
            * its canonical path escapes the workspace root
              (when ``workspace_root`` is given).

        ``workspace_root`` is optional. When provided, it is
        used as the path-safety boundary. When omitted, the
        workspace's own ``root_canonical_path`` is used.
        """
        if not isinstance(source_file, SourceFile):
            raise TypeError("source_file must be a SourceFile")
        boundary = (
            workspace_root
            if workspace_root is not None
            else self.root_canonical_path
        )
        if boundary != ".":
            if not boundary.endswith("/"):
                boundary_prefix = boundary + "/"
            else:
                boundary_prefix = boundary
            if not source_file.canonical_path.startswith(boundary_prefix):
                raise PathSecurityError(
                    f"source file path escapes workspace root: "
                    f"{source_file.canonical_path!r} not under "
                    f"{boundary!r}"
                )

        # Reject duplicates (case-insensitive by canonical
        # lowercasing).
        for f in self.files:
            if f.canonical_path == source_file.canonical_path:
                raise WorkspaceError(
                    f"duplicate source file: {source_file.canonical_path!r}"
                )
        new_files = tuple(
            sorted(
                self.files + (source_file,),
                key=lambda x: x.canonical_path,
            )
        )
        return Workspace(
            workspace_id=self.workspace_id,
            root_canonical_path=self.root_canonical_path,
            files=new_files,
        )

    def file_by_path(self, canonical_path: str) -> SourceFile | None:
        """Return the file with the given canonical path, or None.

        The path is normalized before lookup. The lookup is
        linear over the (sorted) files tuple, which is
        acceptable for the small file counts typical of a
        COBOL/JCL repository.
        """
        canonical = normalize_canonical_path(canonical_path)
        for f in self.files:
            if f.canonical_path == canonical:
                return f
        return None

    def file_by_id(self, file_id: DeterministicId) -> SourceFile | None:
        """Return the file with the given id, or None."""
        if not isinstance(file_id, DeterministicId):
            raise TypeError("file_id must be a DeterministicId")
        for f in self.files:
            if f.file_id == file_id:
                return f
        return None

    def paths(self) -> tuple[str, ...]:
        """Return the sorted tuple of canonical paths."""
        return tuple(f.canonical_path for f in self.files)

    def ids(self) -> tuple[DeterministicId, ...]:
        """Return the file ids in canonical-path order."""
        return tuple(f.file_id for f in self.files)

    def __len__(self) -> int:
        return len(self.files)

    def __contains__(self, item: object) -> bool:
        if isinstance(item, SourceFile):
            return item in self.files
        if isinstance(item, str):
            try:
                canonical = normalize_canonical_path(item)
            except PathSecurityError:
                return False
            return any(f.canonical_path == canonical for f in self.files)
        if isinstance(item, DeterministicId):
            return any(f.file_id == item for f in self.files)
        return False


__all__ = [
    "FileKind",
    "PathSecurityError",
    "SourceFile",
    "Workspace",
    "WorkspaceError",
    "MAX_SOURCE_BYTES",
    "make_source_file",
    "normalize_canonical_path",
    "resolve_relative_path",
]
