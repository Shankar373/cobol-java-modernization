"""T-2B-03 Parser Determinism Tests.

Verifies that repeated parser invocations produce identical results.
"""

from __future__ import annotations

import pytest

from modernize_v2.lexer import CobolLexer, SourceFormat
from modernize_v2.parser import Parser
from modernize_v2.source import make_source_file


def _lex_and_parse(source: bytes, *, path: str = "test.cbl", fmt: SourceFormat = SourceFormat.FREE):
    sf = make_source_file(path, source)
    lexer = CobolLexer(sf, source, fmt)
    tokens = lexer.lex()
    parser = Parser(tokens, canonical_path=path)
    return parser.parse()


# ---------------------------------------------------------------------------
# Repeated parse() calls produce identical results
# ---------------------------------------------------------------------------

def test_repeated_parse_identical():
    """Calling parse() twice on the same parser produces identical results."""
    sf = make_source_file("test.cbl", b"MOVE A TO B.")
    lexer = CobolLexer(sf, b"MOVE A TO B.", SourceFormat.FREE)
    tokens = lexer.lex()
    parser = Parser(tokens, canonical_path="test.cbl")
    result1 = parser.parse()
    result2 = parser.parse()
    assert result1.ast == result2.ast
    assert result1.diagnostics == result2.diagnostics
    assert result1.recovery_records == result2.recovery_records
    assert result1.eof_at_byte == result2.eof_at_byte


def test_repeated_parse_with_if_else():
    """Repeated parse() of complex statement is deterministic."""
    source = b"IF A > B MOVE X TO Y ELSE MOVE P TO Q END-IF."
    sf = make_source_file("test.cbl", source)
    lexer = CobolLexer(sf, source, SourceFormat.FREE)
    tokens = lexer.lex()
    parser = Parser(tokens, canonical_path="test.cbl")
    result1 = parser.parse()
    result2 = parser.parse()
    assert result1.ast == result2.ast


def test_repeated_parse_with_unsupported():
    """Repeated parse() of unsupported content is deterministic."""
    source = b"READ FILE-1.\nMOVE A TO B."
    sf = make_source_file("test.cbl", source)
    lexer = CobolLexer(sf, source, SourceFormat.FREE)
    tokens = lexer.lex()
    parser = Parser(tokens, canonical_path="test.cbl")
    result1 = parser.parse()
    result2 = parser.parse()
    assert result1.ast == result2.ast
    assert result1.diagnostics == result2.diagnostics


# ---------------------------------------------------------------------------
# Two separate parser instances produce identical results
# ---------------------------------------------------------------------------

def test_two_parser_instances_identical():
    """Two separate parser instances on the same tokens produce identical results."""
    source = b"MOVE A TO B.\nDISPLAY X."
    sf = make_source_file("test.cbl", source)
    lexer = CobolLexer(sf, source, SourceFormat.FREE)
    tokens = lexer.lex()
    parser1 = Parser(tokens, canonical_path="test.cbl")
    parser2 = Parser(tokens, canonical_path="test.cbl")
    result1 = parser1.parse()
    result2 = parser2.parse()
    assert result1.ast == result2.ast
    assert result1.diagnostics == result2.diagnostics
    assert result1.eof_at_byte == result2.eof_at_byte


def test_two_lexer_instances_identical():
    """Two separate lexer+parser chains on the same source produce identical results."""
    source = b"COMPUTE X = A + B * C."
    result1 = _lex_and_parse(source)
    result2 = _lex_and_parse(source)
    assert result1.ast == result2.ast


# ---------------------------------------------------------------------------
# Deterministic node IDs
# ---------------------------------------------------------------------------

def test_deterministic_node_ids():
    """Identical source produces identical node IDs."""
    source = b"MOVE A TO B."
    result1 = _lex_and_parse(source)
    result2 = _lex_and_parse(source)
    stmt1 = result1.ast.statements[0]
    stmt2 = result2.ast.statements[0]
    assert stmt1.node_id == stmt2.node_id
    assert stmt1.source.node_id == stmt2.source.node_id
    assert stmt1.target.node_id == stmt2.target.node_id


def test_deterministic_node_ids_complex():
    """Identical complex source produces identical node IDs."""
    source = b"IF A > B MOVE X TO Y ELSE MOVE P TO Q END-IF."
    result1 = _lex_and_parse(source)
    result2 = _lex_and_parse(source)
    if1 = result1.ast.statements[0]
    if2 = result2.ast.statements[0]
    assert if1.node_id == if2.node_id
    assert if1.condition.node_id == if2.condition.node_id


# ---------------------------------------------------------------------------
# Deterministic diagnostics
# ---------------------------------------------------------------------------

def test_deterministic_diagnostics():
    """Identical malformed source produces identical diagnostics."""
    source = b"READ FILE-1."
    result1 = _lex_and_parse(source)
    result2 = _lex_and_parse(source)
    assert len(result1.diagnostics) == len(result2.diagnostics)
    for d1, d2 in zip(result1.diagnostics, result2.diagnostics):
        assert d1.diagnostic_id == d2.diagnostic_id
        assert d1.message == d2.message
        assert d1.severity == d2.severity
        assert d1.kind == d2.kind
