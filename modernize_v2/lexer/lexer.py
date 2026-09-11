"""COBOL lexer (T-2B-02).

Deterministic lexer that consumes ``SourceFile`` + ``raw_bytes`` and
emits a typed token stream with ``SourceSpan`` provenance.

No filesystem I/O, no V1 imports, no legacy runtime dependencies,
no ``Dict[str, Any]``, no clock, no randomness.

Source positions are always derived from the **raw byte** stream.
UTF-8 multibyte characters are preserved in the token text but
their spans are byte-accurate.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Final, List, Optional, Tuple

from modernize_v2.ir.diagnostic import (
    Diagnostic,
    DiagnosticKind,
    DiagnosticSeverity,
    SourcePosition,
    SourceSpan,
)
from modernize_v2.lexer.keywords import is_keyword
from modernize_v2.lexer.tokens import Token, TokenKind, tokens_to_canonical_json
from modernize_v2.source.source_map import SourceMap, SourceMapError


# ------------------------------------------------------------------
# Operator / punctuation longest-match table
# Ordered by descending length so the first match is the longest.
# Patterns are strings; we attempt to match them as raw bytes so
# that byte positions remain authoritative.
# ------------------------------------------------------------------

# Patterns as raw-byte literals (Python supports this).
_OP_PATTERNS: Final[list[tuple[bytes, TokenKind]]] = [
    (b"**", TokenKind.DOUBLE_ASTERISK),  # exponentiation
    (b"<=", TokenKind.LESS_EQUAL),
    (b">=", TokenKind.GREATER_EQUAL),
    (b"!=", TokenKind.NOT_EQUAL),
    (b".", TokenKind.PERIOD),
    (b",", TokenKind.COMMA),
    (b";", TokenKind.SEMICOLON),
    (b":", TokenKind.COLON),
    (b"(", TokenKind.LPAREN),
    (b")", TokenKind.RPAREN),
    (b"+", TokenKind.PLUS),
    (b"-", TokenKind.MINUS),
    (b"*", TokenKind.ASTERISK),  # multiplication (single, after **)
    (b"/", TokenKind.SLASH),
    (b"=", TokenKind.EQUALS),
    (b"<", TokenKind.LESS_THAN),
    (b">", TokenKind.GREATER_THAN),
]

# Also keep str patterns for compatibility with the str-based
# _scan_operator_at when it is called from str contexts.
_OP_STR_PATTERNS: Final[list[tuple[str, TokenKind]]] = [
    (r"\*\*", TokenKind.DOUBLE_ASTERISK),
    (r"<=", TokenKind.LESS_EQUAL),
    (r">=", TokenKind.GREATER_EQUAL),
    (r"!=", TokenKind.NOT_EQUAL),
    (r"\.", TokenKind.PERIOD),
    (r",", TokenKind.COMMA),
    (r";", TokenKind.SEMICOLON),
    (r":", TokenKind.COLON),
    (r"\(", TokenKind.LPAREN),
    (r"\)", TokenKind.RPAREN),
    (r"\+", TokenKind.PLUS),
    (r"-", TokenKind.MINUS),
    (r"\*", TokenKind.ASTERISK),
    (r"/", TokenKind.SLASH),
    (r"=", TokenKind.EQUALS),
    (r"<", TokenKind.LESS_THAN),
    (r">", TokenKind.GREATER_THAN),
]


# ------------------------------------------------------------------
# Helpers (module-level, no self. needed)
# ------------------------------------------------------------------

# ASCII byte classes (single-byte classification, UTF-8 multibyte
# bytes are handled by the leading-byte range 0xC0-0xFD).
_IS_ASCII_UPPER: Final = tuple(range(0x41, 0x5B))  # A-Z
_IS_ASCII_LOWER: Final = tuple(range(0x61, 0x7B))  # a-z
_IS_ASCII_DIGIT: Final = tuple(range(0x30, 0x3A))  # 0-9
_IS_ASCII_ALPHA: Final = _IS_ASCII_UPPER + _IS_ASCII_LOWER
_IS_ASCII_ALNUM: Final = _IS_ASCII_ALPHA + _IS_ASCII_DIGIT
_IS_ASCII_WS: Final = (0x20, 0x09, 0x0A)  # space, tab, newline
_IS_ASCII_HYPHEN: Final = (0x2D,)


def _is_identifier_text(text: str) -> bool:
    """COBOL identifiers start with a letter; may contain letters,
    digits, and hyphens.  Syntactic check only — no semantic
    interpretation.
    """
    if not text:
        return False
    if not text[0].isalpha():
        return False
    return all(c.isalnum() or c == "-" for c in text)


def _is_operator_byte_at(data: bytes, pos: int) -> Optional[Tuple[bytes, int, TokenKind]]:
    """Try to match an operator pattern at byte position *pos* in
    *data*.  Returns ``(matched_bytes, byte_length, token_kind)`` or
    ``None``.

    Operates directly on the raw bytes, so byte positions remain
    authoritative.
    """
    if pos >= len(data):
        return None
    # Try longest match first; ordered by length in _OP_PATTERNS.
    for pattern, kind in _OP_PATTERNS:
        end = pos + len(pattern)
        if data[pos:end] == pattern:
            return pattern, len(pattern), kind
    return None


# ------------------------------------------------------------------
# SourceFormat enum
# ------------------------------------------------------------------

class SourceFormat(Enum):
    FIXED = "fixed"
    FREE = "free"


# ------------------------------------------------------------------
# LexerError — carry a V2 Diagnostic
# ------------------------------------------------------------------

class LexerError(Exception):
    """Fail-closed lexer error carrying a V2 ``Diagnostic``."""

    def __init__(self, diagnostic: Diagnostic) -> None:
        super().__init__(str(diagnostic))
        self.diagnostic = diagnostic

    def __str__(self) -> str:
        return f"LexerError: {self.diagnostic}"


# ------------------------------------------------------------------
# CobolLexer
# ------------------------------------------------------------------

class CobolLexer:
    """Deterministic COBOL source lexer.

    ``CobolLexer(source_file, raw_bytes, format)`` validates that
    ``raw_bytes`` matches ``source_file`` (byte‑size + SHA‑256) via
    ``SourceMap.from_bytes``.  ``lex()`` returns a ``tuple[Token, ...]``
    in source order; every token carries a ``SourceSpan`` pointing at
    the original bytes.

    The scanner is pure — no IO, no clock, no randomness.

    The cursor advances through ``raw_bytes`` one byte at a time.
    Word content (which may include UTF-8 multibyte characters) is
    decoded from the bytes for the keyword/identifier classification,
    but the byte positions in the token ``SourceSpan`` always reflect
    the actual byte offsets in ``raw_bytes``.
    """

    def __init__(
        self,
        source_file: "SourceFile",
        raw_bytes: bytes,
        format: SourceFormat,
    ) -> None:
        # --- validate raw bytes against source file -----------------
        if not isinstance(raw_bytes, bytes):
            raise LexerError(
                Diagnostic(
                    severity=DiagnosticSeverity.ERROR,
                    kind=DiagnosticKind.INVALID_SOURCE,
                    message="raw_bytes must be bytes",
                    span=SourceSpan(
                        canonical_path=source_file.canonical_path,
                        start=SourcePosition(line=1, column=0, byte_offset=0),
                        end=SourcePosition(line=1, column=0, byte_offset=0),
                    ),
                )
            )
        if len(raw_bytes) != source_file.byte_size:
            raise LexerError(
                Diagnostic(
                    severity=DiagnosticSeverity.ERROR,
                    kind=DiagnosticKind.INVALID_SOURCE,
                    message=f"raw_bytes length {len(raw_bytes)} differs from "
                            f"source_file.byte_size {source_file.byte_size}",
                    span=SourceSpan(
                        canonical_path=source_file.canonical_path,
                        start=SourcePosition(line=1, column=0, byte_offset=0),
                        end=SourcePosition(line=1, column=0, byte_offset=0),
                    ),
                )
            )
        actual_hash = hashlib.sha256(raw_bytes).hexdigest()
        if actual_hash != source_file.content_hash:
            raise LexerError(
                Diagnostic(
                    severity=DiagnosticSeverity.ERROR,
                    kind=DiagnosticKind.INVALID_SOURCE,
                    message=f"content hash mismatch for "
                            f"{source_file.canonical_path!r}",
                    span=SourceSpan(
                        canonical_path=source_file.canonical_path,
                        start=SourcePosition(line=1, column=0, byte_offset=0),
                        end=SourcePosition(line=1, column=0, byte_offset=0),
                    ),
                )
            )

        # --- build SourceMap for byte‑offset → position translation --
        self._sm: SourceMap = SourceMap.from_bytes(source_file, raw_bytes)

        self._source_file = source_file
        self._raw_bytes: bytes = raw_bytes
        self._format = format
        self._declared_encoding: str = getattr(
            source_file, "declared_encoding", "UTF-8"
        )
        # Decode the whole file for keyword classification.  This
        # decoded text is ONLY used for keyword lookup; byte positions
        # always come from raw_bytes.
        try:
            self._text: str = raw_bytes.decode(self._declared_encoding)
        except UnicodeDecodeError:
            self._text = raw_bytes.decode("utf-8", errors="replace")
        self._eof_byte: int = len(raw_bytes)

        # Byte cursor: next byte to process (0‑based in the file).
        # All token spans and cursor arithmetic are computed in bytes
        # against _raw_bytes, never against _text characters.
        self._byte_cursor: int = 0

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def lex(self) -> Tuple[Token, ...]:
        """Return the deterministic token stream for this source.

        The byte cursor is reset at the start of every call so
        ``lex()`` is safe to call repeatedly on the same instance.
        """
        self._byte_cursor = 0
        tokens: List[Token] = []

        data = self._raw_bytes
        eof = self._eof_byte

        while self._byte_cursor < eof:
            # --- Fixed-format indicator column handling ---------------
            if self._format == SourceFormat.FIXED:
                handled = self._handle_fixed_indicator(data, eof)
                if handled:
                    continue

            # Try to match an operator first (longest match on raw bytes).
            op_result = _is_operator_byte_at(data, self._byte_cursor)
            if op_result is not None:
                op_text, op_byte_len, op_kind = op_result
                tok_start = self._byte_cursor
                tok_end = tok_start + op_byte_len
                tok_span = self._make_span(tok_start, tok_end)
                # Decode the operator text for token.text; the bytes
                # are ASCII so this is lossless and stable.
                tokens.append(Token(
                    kind=op_kind,
                    text=op_text.decode("ascii"),
                    span=tok_span,
                    debug=False,
                ))
                self._byte_cursor = tok_end
                continue

            # Try to match a word (keyword / identifier / numeric).
            tok_start, tok_end, kind, text = self._scan_word(data, eof)
            if tok_end > tok_start:
                tok_span = self._make_span(tok_start, tok_end)
                tokens.append(Token(
                    kind=kind,
                    text=text,
                    span=tok_span,
                    debug=False,
                ))
                self._byte_cursor = tok_end
                continue

            # No operator and no word match: advance past one byte.
            # This handles unsupported characters and embedded
            # whitespace that the word scan decided to skip.  We
            # must NEVER silently lose source content, so we advance
            # one byte at a time.
            self._byte_cursor += 1

        # EOF sentinel
        eof_span = self._make_span(self._byte_cursor, eof)
        tokens.append(Token(
            kind=TokenKind.IDENTIFIER, text="", span=eof_span, debug=False
        ))

        return tuple(tokens)

    # ------------------------------------------------------------------
    # Fixed-format indicator column helper
    # ------------------------------------------------------------------

    def _handle_fixed_indicator(self, data: bytes, eof: int) -> bool:
        """If at the start of a new physical line in fixed format,
        apply indicator-column semantics.  Returns True if the
        indicator caused the cursor to advance (and the main loop
        should ``continue``).

        In fixed format, columns 1-6 are the sequence area
        (provenance only — must NOT be tokenized) and column 7 is
        the indicator column.  This helper advances past both.
        The indicator column character is consumed without becoming
        a token in the main stream (it only affects how the rest of
        the line is interpreted).

        Returns True if the cursor was advanced (and the main loop
        should ``continue``).  Returns False if the cursor was not
        at a line start, in which case the main loop should proceed
        with normal scanning.
        """
        cur = self._byte_cursor
        at_line_start = (cur == 0 or data[cur - 1:cur] == b"\n")
        if not at_line_start:
            return False
        # Skip the sequence area (columns 1-6, bytes cur..cur+5)
        # plus the indicator column (column 7, byte cur+6).  This
        # is 7 bytes total in normal fixed format.
        if cur + 7 > eof:
            # Truncated final line: consume whatever remains.
            self._byte_cursor = eof
            return True
        indicator_byte = data[cur + 6:cur + 7]
        if indicator_byte == b"*":
            # Full-line comment: skip to end of line.  Then the
            # main loop will resume at the next line.
            nl = data.find(b"\n", cur)
            if nl == -1:
                self._byte_cursor = eof
            else:
                self._byte_cursor = nl + 1
            return True
        if indicator_byte == b"-":
            # Continuation: skip past indicator and let the next
            # iteration scan the content as if it were part of the
            # previous logical line.  We skip 7 bytes (sequence
            # area + indicator); the next line's column 8+ content
            # becomes the rest of the current logical line.
            self._byte_cursor = cur + 7
            return True
        # Indicator is a space (or anything other than '*' or '-'):
        # consume the sequence area + indicator and continue.  The
        # main word scan will start at column 8 (Area A).
        self._byte_cursor = cur + 7
        return True

    # ------------------------------------------------------------------
    # Word scanning — returns (start_byte, end_byte, kind, text) or
    # (0, 0, _MISS, "") if no word at the current cursor.
    # ------------------------------------------------------------------

    # Sentinel for "no word" — we use (0, 0, IDENTIFIER, "") and check
    # tok_end > tok_start at the caller.
    _MISS = TokenKind.IDENTIFIER

    def _scan_word(
        self,
        data: bytes,
        eof: int,
    ) -> Tuple[int, int, TokenKind, str]:
        """Scan a word at the current byte cursor.

        Returns (start_byte, end_byte, kind, text) where
        start_byte < end_byte on success.  Returns (0, 0, ...) when
        no word starts at the current cursor (e.g. whitespace).

        The word may contain letters, digits, and hyphens.  A word
        starting with a letter may be a keyword or identifier.  A
        word consisting only of digits (e.g. ``123``) is emitted as
        ``TokenKind.IDENTIFIER`` so that the parser can syntactically
        classify it.  This fixes the previously-reported P0 defect
        where purely-numeric words were silently consumed.
        """
        cur = self._byte_cursor
        # Quick reject: must start with a letter, digit, hyphen, or
        # UTF-8 leading byte.
        if cur >= eof:
            return 0, 0, self._MISS, ""

        start = cur
        first = data[cur:cur + 1]
        first_byte = first[0]
        # Acceptable first bytes: ASCII alnum, hyphen, or UTF-8
        # leading byte (>= 0xC0 covers all 2-, 3-, and 4-byte UTF-8
        # sequences; 0x80-0xBF are continuation bytes and would only
        # appear mid-sequence, not at a word boundary).
        is_word_starter = (
            first_byte in _IS_ASCII_ALNUM
            or first_byte == 0x2D  # hyphen
            or first_byte >= 0xC0  # UTF-8 leading byte
        )
        if not is_word_starter:
            return 0, 0, self._MISS, ""

        # Collect word characters (alphanumeric or hyphen), counting
        # bytes — NOT characters.  This is critical for UTF-8
        # correctness: each byte either starts a new ASCII char or
        # is a continuation byte of a UTF-8 multibyte char.  We accept
        # any byte >= 0x80 as a valid word continuation byte.
        end = start
        while end < eof:
            b = data[end]
            if (
                b in _IS_ASCII_ALNUM
                or b == 0x2D  # hyphen
                or b >= 0x80  # UTF-8 multibyte continuation/leading
            ):
                end += 1
                continue
            break

        if end == start:
            # Nothing collected (e.g. a lone '-'); return miss.
            return 0, 0, self._MISS, ""

        # Decode the word bytes for keyword/identifier classification.
        # Errors here are replaced; the original bytes are authoritative
        # for span computation.
        word_bytes = data[start:end]
        try:
            word_str = word_bytes.decode("utf-8")
        except UnicodeDecodeError:
            word_str = word_bytes.decode("utf-8", errors="replace")

        # Context-sensitive classification:
        #
        # - Word starts with a letter and contains at least one
        #   alpha character -> keyword (if in reserved list) or
        #   identifier.
        # - Word starts with a digit -> numeric literal, emitted as
        #   IDENTIFIER (the parser can classify syntactically).
        # - Word is exactly "-" (single hyphen byte) -> MINUS operator.
        # - Word starts with hyphen followed by alnum -> identifier
        #   starting with hyphen is invalid in COBOL; we emit it as
        #   IDENTIFIER so the parser can decide.
        if word_str and word_str[0].isalpha():
            if is_keyword(word_str):
                return start, end, TokenKind.KEYWORD, word_str
            if _is_identifier_text(word_str):
                return start, end, TokenKind.IDENTIFIER, word_str
            # Defensive: word is alpha-led but not a valid identifier
            # (would mean it has an embedded disallowed character). Emit
            # as IDENTIFIER so source content is never silently lost.
            return start, end, TokenKind.IDENTIFIER, word_str

        if word_str and word_str[0].isdigit():
            # Purely numeric word -> IDENTIFIER.  This is the FIX for
            # the P0 numeric-literal defect.
            return start, end, TokenKind.IDENTIFIER, word_str

        if len(word_bytes) == 1 and word_bytes == b"-":
            # Single-byte hyphen -> MINUS operator.
            return start, end, TokenKind.MINUS, "-"

        # Hyphen-led but not a single hyphen -> emit as IDENTIFIER so
        # no source content is silently consumed.
        return start, end, TokenKind.IDENTIFIER, word_str

    # ------------------------------------------------------------------
    # Span construction helper
    # ------------------------------------------------------------------

    def _make_span(self, start_byte: int, end_byte: int) -> SourceSpan:
        """Create a ``SourceSpan`` from byte offsets using the SourceMap.

        The span is anchored on the canonical path of the source file.
        Start is inclusive, end is exclusive.  All offsets are
        authoritative raw-byte positions.
        """
        start_pos = self._sm.position_at(start_byte)
        end_pos = self._sm.position_at(end_byte)
        return SourceSpan(
            canonical_path=self._source_file.canonical_path,
            start=start_pos,
            end=end_pos,
        )


# ------------------------------------------------------------------
# EOF helper
# ------------------------------------------------------------------

def _eof_token(sm: SourceMap, canonical_path: str, byte_size: int) -> Token:
    """Return the EOF token (empty text, span at byte_size)."""
    eof_span = SourceSpan(
        canonical_path=canonical_path,
        start=sm.position_at(byte_size),
        end=sm.position_at(byte_size),
    )
    return Token(
        kind=TokenKind.IDENTIFIER, text="", span=eof_span, debug=False
    )


# ------------------------------------------------------------------
# Operator scanning helper (str-based, kept for backwards compatibility)
# ------------------------------------------------------------------

def _scan_operator_at(text: str, pos: int) -> Optional[Tuple[str, int, TokenKind]]:
    """Try to match an operator at position *pos* in *text* (str form).

    Returns ``(matched_text, byte_length, token_kind)`` or ``None``.

    NOTE: Prefer ``_is_operator_byte_at`` for byte-accurate operation.
    """
    remaining = text[pos:]
    for pattern, kind in _OP_STR_PATTERNS:
        m = re.match(pattern, remaining)
        if m:
            matched = m.group(0)
            return matched, len(matched), kind
    return None
