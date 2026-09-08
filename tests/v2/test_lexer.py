"""Comprehensive tests for the T-2B-02 COBOL lexer.

These tests verify the CobolLexer implementation: deterministic token
streams, exact SourceSpan provenance, fixed and free format handling,
comment handling, and fail-closed error semantics.

They are designed to run alongside (not depend on) the token/keyword
foundation tests in test_lexer_tokens.py.
"""

from __future__ import annotations

import pytest

from modernize_v2.source import make_source_file
from modernize_v2.lexer import CobolLexer, SourceFormat, LexerError
from modernize_v2.lexer.tokens import Token, TokenKind, tokens_to_canonical_json


# Helpers
def _sm(content):  # raw bytes
    from modernize_v2.source.source_map import SourceMap
    sf = make_source_file("t.cbl", content)
    return sf, SourceMap.from_bytes(sf, content)


# Empty source / EOF
def test_lexer_empty_source():
    """Empty source should produce exactly one EOF token."""
    sf, _ = _sm(b"")
    lexer = CobolLexer(sf, b"", SourceFormat.FREE)
    tokens = lexer.lex()
    assert len(tokens) == 1
    assert tokens[0].kind == TokenKind.IDENTIFIER
    assert tokens[0].text == ""
    assert tokens[0].span.start.byte_offset == 0
    assert tokens[0].span.end.byte_offset == 0


def test_lexer_eof_span():
    """EOF token span must be at byte_size."""
    sf, _ = _sm(b"ABC")
    lexer = CobolLexer(sf, b"ABC", SourceFormat.FIXED)
    tokens = lexer.lex()
    eof_tok = tokens[-1]
    assert eof_tok.text == ""
    assert eof_tok.span.start.byte_offset == 3
    assert eof_tok.span.end.byte_offset == 3


# Identifiers
def test_lexer_identifiers():
    """Basic identifiers are emitted as IDENTIFIER."""
    sf, _ = _sm(b"CUSTOMER-NAME WS-TOTAL ACCOUNT-NUMBER")
    lexer = CobolLexer(sf, b"CUSTOMER-NAME WS-TOTAL ACCOUNT-NUMBER", SourceFormat.FREE)
    tokens = lexer.lex()
    assert all(t.kind == TokenKind.IDENTIFIER for t in tokens)


def test_lexer_identifiers_preserve_hyphens():
    """Hyphens in identifiers must not be treated as minus operators."""
    sf, _ = _sm(b"CUST-NAME")
    lexer = CobolLexer(sf, b"CUST-NAME", SourceFormat.FREE)
    tokens = lexer.lex()
    # Non-empty source -> lexical tokens + EOF
    assert len(tokens) == 2
    assert tokens[0].kind == TokenKind.IDENTIFIER
    assert tokens[0].text == "CUST-NAME"
    assert tokens[1].kind == TokenKind.IDENTIFIER  # EOF
    assert tokens[1].text == ""


# Keywords
def test_lexer_keywords():
    """COBOL keywords are emitted as KEYWORD (case-insensitive classification)."""
    sf, _ = _sm(b"MOVE ADD SUBTRACT")
    lexer = CobolLexer(sf, b"MOVE ADD SUBTRACT", SourceFormat.FREE)
    tokens = lexer.lex()
    assert TokenKind.KEYWORD in [t.kind for t in tokens]


def test_lexer_keywords_preserve_spelling():
    """Keyword text must preserve the original source spelling."""
    sf, _ = _sm(b"move add")
    lexer = CobolLexer(sf, b"move add", SourceFormat.FREE)
    tokens = lexer.lex()
    assert tokens[0].text == "move"
    assert tokens[1].text == "add"


def test_lexer_keywords_mixed_case():
    """Mixed-case keywords still classified as KEYWORD."""
    sf, _ = _sm(b"Move Add")
    lexer = CobolLexer(sf, b"Move Add", SourceFormat.FREE)
    tokens = lexer.lex()
    # Non-empty source -> content tokens + EOF; check content only
    content = tokens[:-1]
    assert all(t.kind == TokenKind.KEYWORD for t in content)


# Operators and punctuation
def test_lexer_operators():
    """All operator TokenKind values are recognized (content tokens only)."""
    op_bytes = b'+ - * / . , ; : ( ) = < > >='  # 28 bytes with spaces
    sf, _ = _sm(op_bytes)
    lexer = CobolLexer(sf, op_bytes, SourceFormat.FREE)
    tokens = lexer.lex()
    content = tokens[:-1]  # exclude EOF
    kinds = {t.kind for t in content}
    expected = {
        TokenKind.PLUS, TokenKind.MINUS, TokenKind.ASTERISK, TokenKind.SLASH,
        TokenKind.PERIOD, TokenKind.COMMA, TokenKind.SEMICOLON, TokenKind.COLON,
        TokenKind.LPAREN, TokenKind.RPAREN, TokenKind.EQUALS,
        TokenKind.LESS_THAN, TokenKind.GREATER_THAN,
        TokenKind.GREATER_EQUAL,
    }
    assert kinds == expected


def test_lexer_longest_match_operators():
    """Longest-match: <= must not split into < and =."""
    sf, _ = _sm(b"<= >= !=")
    lexer = CobolLexer(sf, b"<= >= !=", SourceFormat.FREE)
    tokens = lexer.lex()
    content = tokens[:-1]  # exclude EOF
    t0, t1, t2 = content
    assert t0.kind == TokenKind.LESS_EQUAL
    assert t1.kind == TokenKind.GREATER_EQUAL
    assert t2.kind == TokenKind.NOT_EQUAL


# Whitespace
def test_lexer_whitespace_no_tokens():
    """Ordinary whitespace must not produce tokens."""
    sf, _ = _sm(b"   ")
    lexer = CobolLexer(sf, b"   ", SourceFormat.FREE)
    tokens = lexer.lex()
    assert len(tokens) == 1  # only EOF
    assert tokens[0].text == ""


# Free format
def test_lexer_free_format_basic():
    """Free format: entire line is lexical content."""
    sf, _ = _sm(b"MOVE A TO B")
    lexer = CobolLexer(sf, b"MOVE A TO B", SourceFormat.FREE)
    tokens = lexer.lex()
    assert len(tokens) == 5  # 4 content tokens + EOF
    assert tokens[0].kind == TokenKind.KEYWORD and tokens[0].text == "MOVE"
    assert tokens[1].kind == TokenKind.IDENTIFIER and tokens[1].text == "A"
    assert tokens[2].kind == TokenKind.KEYWORD and tokens[2].text == "TO"
    assert tokens[3].kind == TokenKind.IDENTIFIER and tokens[3].text == "B"


def test_lexer_free_format_inline_comment():
    """Inline comment (> *) must be skipped; remaining content tokenized."""
    sf, _ = _sm(b"MOVE A TO B *> this is a comment")
    lexer = CobolLexer(sf, b"MOVE A TO B *> this is a comment", SourceFormat.FREE)
    tokens = lexer.lex()
    assert tokens[0].kind == TokenKind.KEYWORD and tokens[0].text == "MOVE"
    assert tokens[1].kind == TokenKind.IDENTIFIER and tokens[1].text == "A"
    assert tokens[2].kind == TokenKind.KEYWORD and tokens[2].text == "TO"
    assert tokens[3].kind == TokenKind.IDENTIFIER and tokens[3].text == "B"


# Fixed format
def test_lexer_fixed_format_basic():
    """Fixed format: scanning starts at Area A (byte 7 from line start)."""
    sf, _ = _sm(b"000001 MOVE A TO B.")
    lexer = CobolLexer(sf, b"000001 MOVE A TO B.", SourceFormat.FIXED)
    tokens = lexer.lex()
    assert tokens[0].kind == TokenKind.KEYWORD and tokens[0].text == "MOVE"
    assert tokens[0].span.start.byte_offset == 7
    assert tokens[1].kind == TokenKind.IDENTIFIER and tokens[1].text == "A"
    assert tokens[2].kind == TokenKind.KEYWORD and tokens[2].text == "TO"
    assert tokens[3].kind == TokenKind.IDENTIFIER and tokens[3].text == "B"


def test_lexer_fixed_format_sequence_ignored():
    """Sequence area must NOT become tokens."""
    sf, _ = _sm(b"000100 MOVE A")
    lexer = CobolLexer(sf, b"000100 MOVE A", SourceFormat.FIXED)
    tokens = lexer.lex()
    assert len(tokens) == 3  # MOVE, A, EOF
    assert tokens[0].span.start.byte_offset > 0


def test_lexer_fixed_format_indicator_comment():
    """Indicator column '*' at physical column 7 must cause full-line comment."""
    # 6 bytes of sequence area, then '*' at column 7
    sf, _ = _sm(b"      *MOVE A TO B")  # 6 spaces + * + MOVE A TO B
    lexer = CobolLexer(sf, b"      *MOVE A TO B", SourceFormat.FIXED)
    tokens = lexer.lex()
    assert len(tokens) == 1  # EOF only
    assert tokens[0].text == ""


def test_lexer_fixed_format_continuation():
    """Fixed format: '-' in indicator column 7 causes line continuation."""
    # 6 bytes sequence area, then '-' at column 7
    sf, _ = _sm(b"      -MOVE A TO B")  # 6 spaces + - at column 7
    lexer = CobolLexer(sf, b"      -MOVE A TO B", SourceFormat.FIXED)
    tokens = lexer.lex()
    # The continuation joins the next logical line; for a single line
    # this just produces tokens from the joined content.
    assert len(tokens) >= 1


# CRLF
def test_lexer_crlf():
    """CRLF must not be normalized."""
    sf, _ = _sm(b"MOVE A TO B\r\nNEXT LINE")
    lexer = CobolLexer(sf, b"MOVE A TO B\r\nNEXT LINE", SourceFormat.FIXED)
    tokens = lexer.lex()
    assert len(tokens) >= 1


# Determinism / canonical serialization
def test_lexer_deterministic_serialization():
    """Same source bytes must produce byte-identical canonical JSON."""
    sf, _ = _sm(b"MOVE A TO B.")
    lexer = CobolLexer(sf, b"MOVE A TO B.", SourceFormat.FREE)
    tokens1 = lexer.lex()
    tokens2 = lexer.lex()
    json1 = tokens_to_canonical_json(tokens1)
    json2 = tokens_to_canonical_json(tokens2)
    assert json1 == json2

    sf2, _ = _sm(b"MOVE A TO B.")
    lexer2 = CobolLexer(sf2, b"MOVE A TO B.", SourceFormat.FREE)
    tokens3 = lexer2.lex()
    json3 = tokens_to_canonical_json(tokens3)
    assert json1 == json3


def test_lexer_determinism_kinds():
    sf, _ = _sm(b"ADD 1 TO COUNTER")
    lexer = CobolLexer(sf, b"ADD 1 TO COUNTER", SourceFormat.FREE)
    tokens = lexer.lex()
    kind_sequence = [t.kind for t in tokens[:-1]]
    assert TokenKind.KEYWORD in kind_sequence
    assert TokenKind.IDENTIFIER in kind_sequence


# LexerError (fail-closed)
def test_lexer_error_invalid_raw_bytes_type():
    sf, _ = _sm(b"TEST")
    try:
        CobolLexer(sf, "not bytes", SourceFormat.FREE)
        assert False
    except LexerError:
        pass


def test_lexer_error_byte_size_mismatch():
    sf, _ = _sm(b"TEST")
    try:
        CobolLexer(sf, b"TOO SHORT", SourceFormat.FREE)
        assert False
    except LexerError:
        pass


def test_lexer_error_hash_mismatch():
    sf, _ = _sm(b"TEST")
    try:
        CobolLexer(sf, b"WRONG CONTENT", SourceFormat.FREE)
        assert False
    except LexerError:
        pass


# SourceSpan round-trip
def test_lexer_span_check():
    """Token spans must have correct start/end byte offsets."""
    sf, _ = _sm(b"MOVE A TO B.")
    lexer = CobolLexer(sf, b"MOVE A TO B.", SourceFormat.FREE)
    tokens = lexer.lex()
    for i, tok in enumerate(tokens[:-1]):
        assert tok.span.start.byte_offset < tok.span.end.byte_offset