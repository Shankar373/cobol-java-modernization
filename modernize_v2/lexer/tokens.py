"""Token model for the V2 COBOL lexer (T-2B-02).

A ``Token`` is an immutable lexical unit with:

    * ``kind`` — a ``TokenKind`` enum value.
    * ``text`` — the exact source text of the token (normalized
      only by the lexical rules of the format: continued literals
      are reassembled; nothing else is rewritten).
    * ``span`` — a ``modernize_v2.ir.diagnostic.SourceSpan``
      giving the precise byte-level provenance of the token in
      the source file. Spans are never synthesized at position 0;
      they always point at the real bytes that produced the
      token.
    * ``debug`` — ``True`` if the token originates from a
      fixed-format "D" debug line. The parser decides what to do
      with debug lines; the lexer merely preserves the fact.

Tokens are ordered: the token stream is a tuple in source order.
The ordering is deterministic by construction and by the
``tokens_to_canonical_json`` serializer.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any

from modernize_v2.ir.diagnostic import SourceSpan


class TokenKind(str, Enum):
    """Lexical token kinds for COBOL source.

    This is the *lexical* vocabulary only. Whether a kind is
    meaningful in a given syntactic position is a parser concern
    (T-2B-04, not implemented yet).
    """

    IDENTIFIER = "IDENTIFIER"
    KEYWORD = "KEYWORD"
    NUMERIC_LITERAL = "NUMERIC_LITERAL"
    STRING_LITERAL = "STRING_LITERAL"
    HEX_STRING_LITERAL = "HEX_STRING_LITERAL"

    # Punctuation
    PERIOD = "PERIOD"
    COMMA = "COMMA"
    SEMICOLON = "SEMICOLON"
    COLON = "COLON"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"

    # Operators
    PLUS = "PLUS"
    MINUS = "MINUS"
    ASTERISK = "ASTERISK"          # multiplication
    SLASH = "SLASH"                # division
    DOUBLE_ASTERISK = "DOUBLE_ASTERISK"  # exponentiation
    EQUALS = "EQUALS"
    LESS_THAN = "LESS_THAN"
    GREATER_THAN = "GREATER_THAN"
    LESS_EQUAL = "LESS_EQUAL"
    GREATER_EQUAL = "GREATER_EQUAL"
    NOT_EQUAL = "NOT_EQUAL"


@dataclass(frozen=True)
class Token:
    """An immutable lexical token."""

    kind: TokenKind
    text: str
    span: SourceSpan
    debug: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.kind, TokenKind):
            raise TypeError("kind must be a TokenKind")
        if not isinstance(self.text, str):
            raise TypeError("text must be a string")
        if not isinstance(self.span, SourceSpan):
            raise TypeError("span must be a SourceSpan")
        if not isinstance(self.debug, bool):
            raise TypeError("debug must be a bool")

    def to_dict(self) -> dict[str, Any]:
        s = self.span
        return {
            "kind": self.kind.value,
            "text": self.text,
            "debug": self.debug,
            "span": {
                "canonical_path": s.canonical_path,
                "start": {
                    "line": s.start.line,
                    "column": s.start.column,
                    "byte_offset": s.start.byte_offset,
                },
                "end": {
                    "line": s.end.line,
                    "column": s.end.column,
                    "byte_offset": s.end.byte_offset,
                },
            },
        }


def tokens_to_canonical_json(tokens: tuple[Token, ...]) -> str:
    """Serialize a token stream deterministically.

    Two token streams that are lexically equivalent (same kinds,
    same text, same spans) serialize to the same canonical JSON,
    regardless of how they were produced. This is the basis for
    the determinism tests of T-2B-02.
    """
    return json.dumps(
        [t.to_dict() for t in tokens],
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


__all__ = [
    "TokenKind",
    "Token",
    "tokens_to_canonical_json",
]
