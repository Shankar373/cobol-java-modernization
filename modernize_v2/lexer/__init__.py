"""V2 COBOL lexer package.

Public API for T-2B-02:

- ``TokenKind`` — lexical token kinds enum
- ``Token`` — immutable token dataclass (kind, text, span, debug)
- ``tokens_to_canonical_json`` — deterministic token-stream serialization
- ``is_keyword`` — case-insensitive COBOL reserved-word test
- ``SourceFormat`` — FIXED / FREE format selection
- ``CobolLexer`` — deterministic lexer producing typed token streams
- ``LexerError`` — fail-closed error with embedded V2 Diagnostic
"""

from __future__ import annotations

from .keywords import is_keyword
from .tokens import Token, TokenKind, tokens_to_canonical_json
from .lexer import SourceFormat, CobolLexer, LexerError

__all__ = [
    "TokenKind",
    "Token",
    "tokens_to_canonical_json",
    "is_keyword",
    "SourceFormat",
    "CobolLexer",
    "LexerError",
]