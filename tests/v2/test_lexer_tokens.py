"""Focused tests for the T-2B-02 token/keyword foundation.

These tests verify the Token model, TokenKind enum, and keyword
classification without requiring the lexer engine (lexer.py). They
are intentionally narrow so they can run before the scanner is
built.
"""

from __future__ import annotations

import json

import pytest

from modernize_v2.lexer.keywords import is_keyword, keyword_count
from modernize_v2.lexer.tokens import Token, TokenKind, tokens_to_canonical_json
from modernize_v2.ir.diagnostic import SourcePosition, SourceSpan


# ---------------------------------------------------------------------------
# TokenKind tests
# ---------------------------------------------------------------------------

def test_token_kind_has_expected_members() -> None:
    """TokenKind must expose the canonical lexical categories."""
    members = list(TokenKind.__members__.values())
    # Core categories required for T-2B-02
    assert TokenKind.IDENTIFIER in members
    assert TokenKind.KEYWORD in members
    assert TokenKind.NUMERIC_LITERAL in members
    assert TokenKind.STRING_LITERAL in members
    assert TokenKind.PERIOD in members
    assert TokenKind.COMMA in members
    assert TokenKind.SEMICOLON in members
    assert TokenKind.LPAREN in members
    assert TokenKind.RPAREN in members
    assert TokenKind.PLUS in members
    assert TokenKind.MINUS in members
    assert TokenKind.ASTERISK in members
    assert TokenKind.SLASH in members
    assert TokenKind.EQUALS in members


def test_token_kind_is_string_enum() -> None:
    """TokenKind values are strings for easy comparison."""
    assert TokenKind.IDENTIFIER.value == "IDENTIFIER"
    assert TokenKind.KEYWORD.value == "KEYWORD"


# ---------------------------------------------------------------------------
# Token construction / immutability
# ---------------------------------------------------------------------------

def test_token_construction_uses_sourceposition() -> None:
    """A Token can be created with SourcePosition-backed spans."""
    span = SourceSpan(
        canonical_path="test.cbl",
        start=SourcePosition(line=1, column=1, byte_offset=0),
        end=SourcePosition(line=1, column=10, byte_offset=9),
    )
    tok = Token(
        kind=TokenKind.IDENTIFIER,
        text="MOVE",
        span=span,
        debug=False,
    )
    assert tok.kind == TokenKind.IDENTIFIER
    assert tok.text == "MOVE"
    assert tok.debug is False


def test_token_is_immutable() -> None:
    """Token fields cannot be modified after construction (normal assignment)."""
    span = SourceSpan(
        canonical_path="test.cbl",
        start=SourcePosition(line=1, column=1, byte_offset=0),
        end=SourcePosition(line=1, column=10, byte_offset=9),
    )
    tok = Token(
        kind=TokenKind.IDENTIFIER,
        text="MOVE",
        span=span,
        debug=False,
    )

    with pytest.raises(Exception):  # frozen dataclass raises FrozenInstanceError
        tok.text = "MOVED"  # type: ignore


# ---------------------------------------------------------------------------
# SourceSpan integration
# ---------------------------------------------------------------------------

def test_token_span_fields_roundtrip() -> None:
    """Token span must expose start/end line/column/byte_offset via to_dict."""
    span = SourceSpan(
        canonical_path="test.cbl",
        start=SourcePosition(line=3, column=5, byte_offset=20),
        end=SourcePosition(line=3, column=12, byte_offset=27),
    )
    tok = Token(
        kind=TokenKind.KEYWORD,
        text="ADD",
        span=span,
        debug=False,
    )
    d = tok.to_dict()
    assert d["span"]["canonical_path"] == "test.cbl"
    assert d["span"]["start"]["line"] == 3
    assert d["span"]["start"]["column"] == 5
    assert d["span"]["start"]["byte_offset"] == 20
    assert d["span"]["end"]["line"] == 3
    assert d["span"]["end"]["column"] == 12
    assert d["span"]["end"]["byte_offset"] == 27


# ---------------------------------------------------------------------------
# Canonical serialization
# ---------------------------------------------------------------------------

def test_canonical_json_determinism() -> None:
    """Two tokens with identical data produce byte-identical JSON."""
    span_a = SourceSpan(
        canonical_path="copybook.cbl",
        start=SourcePosition(line=1, column=1, byte_offset=0),
        end=SourcePosition(line=1, column=4, byte_offset=3),
    )
    span_b = SourceSpan(
        canonical_path="copybook.cbl",
        start=SourcePosition(line=1, column=1, byte_offset=0),
        end=SourcePosition(line=1, column=4, byte_offset=3),
    )

    tok1 = Token(kind=TokenKind.KEYWORD, text="MOVE", span=span_a, debug=False)
    tok2 = Token(kind=TokenKind.KEYWORD, text="MOVE", span=span_b, debug=False)

    json1 = tokens_to_canonical_json((tok1,))
    json2 = tokens_to_canonical_json((tok2,))

    assert json1 == json2
    # Serializing the same token twice must give identical output
    assert json1 == tokens_to_canonical_json((tok1,))


def test_canonical_json_compact_separators() -> None:
    """Canonical JSON uses compact separators (no spaces)."""
    span = SourceSpan(
        canonical_path="copybook.cbl",
        start=SourcePosition(line=1, column=1, byte_offset=0),
        end=SourcePosition(line=1, column=4, byte_offset=3),
    )
    tok = Token(kind=TokenKind.IDENTIFIER, text="XYZ", span=span, debug=False)
    payload = tokens_to_canonical_json((tok,))
    # json.dumps with separators=(",",":") produces no whitespace
    # after commas or colons
    assert "\n" not in payload


# ---------------------------------------------------------------------------
# Keyword lookup
# ---------------------------------------------------------------------------

def test_is_keyword_case_insensitive() -> None:
    """Keyword lookup is case-insensitive."""
    assert is_keyword("MOVE") is True
    assert is_keyword("move") is True
    assert is_keyword("Move") is True


def test_is_keyword_negative() -> None:
    """Non-keywords return False."""
    assert is_keyword("XYZ") is False
    assert is_keyword("") is False


def test_is_keyword_no_phrases() -> None:
    """Multi-word phrases are NOT single lexical keywords."""
    assert is_keyword("LENGTH OF") is False


def test_keyword_count() -> None:
    """keyword_count reports the table size."""
    n = keyword_count()
    assert isinstance(n, int)
    assert n > 0


# ---------------------------------------------------------------------------
# Duplicate / mutation prevention
# ---------------------------------------------------------------------------

def test_keyword_table_no_duplicates() -> None:
    """The source tuple must contain no duplicate entries."""
    from modernize_v2.lexer.keywords import _KEYWORD_WORDS

    seen: dict[str, int] = {}
    for w in _KEYWORD_WORDS:
        seen[w] = seen.get(w, 0) + 1
    duplicates = [w for w, c in seen.items() if c > 1]
    assert not duplicates, f"duplicate keywords found: {duplicates}"


def test_no_multiword_keyword_entries() -> None:
    """No keyword entry may contain a space (phrase)."""
    from modernize_v2.lexer.keywords import _KEYWORD_WORDS

    bad = [w for w in _KEYWORD_WORDS if " " in w]
    assert not bad, f"multi-word entries found: {bad}"


# ---------------------------------------------------------------------------
# Representative COBOL keywords
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "word, expected",
    [
        ("IDENTIFICATION", True),
        ("PROCEDURE", True),
        ("DATA", True),
        ("ADD", True),
        ("MOVE", True),
        ("SUBTRACT", True),
        ("DISPLAY", True),
        ("READ", True),
        ("WRITE", True),
        ("IF", True),
        ("ELSE", True),
        ("END-IF", True),
        ("PERFORM", True),
        ("COMPUTE", True),
        ("PICTURE", True),
        ("USAGE", True),
        ("VALUE", True),
        ("OPEN", True),
        ("CLOSE", True),
    ],
)
def test_representative_keywords(word: str, expected: bool) -> None:
    """A selection of common COBOL reserved words must be recognised."""
    assert is_keyword(word) is expected, (
        f"is_keyword({word!r}) = {is_keyword(word)!r}, expected {expected}"
    )