"""T-2B-03 Parser Grammar Tests.

Verifies which grammar constructs the parser supports and
which are explicitly diagnosed as unsupported.
"""

from __future__ import annotations

import pytest

from modernize_v2.ir.diagnostic import DiagnosticKind
from modernize_v2.lexer import CobolLexer, SourceFormat
from modernize_v2.parser import (
    AddStatement,
    DisplayStatement,
    DivideStatement,
    ExitParagraphStatement,
    ExitPerformStatement,
    GoToStatement,
    GoBackStatement,
    IfStatement,
    MoveStatement,
    MultiplyStatement,
    Parser,
    PerformStatement,
    StopRunStatement,
    SubtractStatement,
)
from modernize_v2.source import make_source_file


def _lex_and_parse(source: bytes, *, path: str = "test.cbl", fmt: SourceFormat = SourceFormat.FREE):
    sf = make_source_file(path, source)
    lexer = CobolLexer(sf, source, fmt)
    tokens = lexer.lex()
    parser = Parser(tokens, canonical_path=path)
    return parser.parse()


# ---------------------------------------------------------------------------
# Supported core statements
# ---------------------------------------------------------------------------

def test_move_supported():
    """MOVE is supported."""
    result = _lex_and_parse(b"MOVE A TO B.")
    assert len(result.ast.statements) == 1
    assert isinstance(result.ast.statements[0], MoveStatement)
    assert not any(
        d.kind == DiagnosticKind.UNSUPPORTED_FEATURE
        for d in result.diagnostics
    )


def test_display_supported():
    """DISPLAY is supported."""
    result = _lex_and_parse(b"DISPLAY X.")
    assert len(result.ast.statements) == 1
    assert isinstance(result.ast.statements[0], DisplayStatement)


def test_add_supported():
    """ADD is supported."""
    result = _lex_and_parse(b"ADD A TO B.")
    assert len(result.ast.statements) == 1
    assert isinstance(result.ast.statements[0], AddStatement)


def test_subtract_supported():
    """SUBTRACT is supported."""
    result = _lex_and_parse(b"SUBTRACT A FROM B.")
    assert len(result.ast.statements) == 1
    assert isinstance(result.ast.statements[0], SubtractStatement)


def test_multiply_supported():
    """MULTIPLY is supported."""
    result = _lex_and_parse(b"MULTIPLY A BY B.")
    assert len(result.ast.statements) == 1
    assert isinstance(result.ast.statements[0], MultiplyStatement)


def test_divide_supported():
    """DIVIDE is supported."""
    result = _lex_and_parse(b"DIVIDE A INTO B.")
    assert len(result.ast.statements) == 1
    assert isinstance(result.ast.statements[0], DivideStatement)


def test_if_supported():
    """IF is supported."""
    result = _lex_and_parse(b"IF A > B MOVE X TO Y END-IF.")
    assert len(result.ast.statements) == 1
    assert isinstance(result.ast.statements[0], IfStatement)


def test_stop_run_supported():
    """STOP RUN is supported."""
    result = _lex_and_parse(b"STOP RUN.")
    assert len(result.ast.statements) == 1
    assert isinstance(result.ast.statements[0], StopRunStatement)


def test_goback_supported():
    """GOBACK is supported."""
    result = _lex_and_parse(b"GOBACK.")
    assert len(result.ast.statements) == 1
    assert isinstance(result.ast.statements[0], GoBackStatement)


def test_goto_supported():
    """GO TO is supported."""
    result = _lex_and_parse(b"GO TO PARA-1.")
    assert len(result.ast.statements) == 1
    assert isinstance(result.ast.statements[0], GoToStatement)


def test_perform_simple_supported():
    """Simple PERFORM is supported."""
    result = _lex_and_parse(b"PERFORM PARA-1.")
    assert len(result.ast.statements) == 1
    assert isinstance(result.ast.statements[0], PerformStatement)


def test_exit_perform_supported():
    """EXIT PERFORM is supported."""
    result = _lex_and_parse(b"EXIT PERFORM.")
    assert len(result.ast.statements) == 1
    assert isinstance(result.ast.statements[0], ExitPerformStatement)


def test_exit_paragraph_supported():
    """EXIT PARAGRAPH is supported."""
    result = _lex_and_parse(b"EXIT PARAGRAPH.")
    assert len(result.ast.statements) == 1
    assert isinstance(result.ast.statements[0], ExitParagraphStatement)


# ---------------------------------------------------------------------------
# Unsupported statements produce diagnostics
# ---------------------------------------------------------------------------

def test_read_unsupported():
    """READ is explicitly unsupported."""
    result = _lex_and_parse(b"READ FILE-1.")
    assert any(
        d.kind == DiagnosticKind.UNSUPPORTED_FEATURE
        for d in result.diagnostics
    )


def test_write_unsupported():
    """WRITE is explicitly unsupported."""
    result = _lex_and_parse(b"WRITE REC-1.")
    assert any(
        d.kind == DiagnosticKind.UNSUPPORTED_FEATURE
        for d in result.diagnostics
    )


def test_sort_unsupported():
    """SORT is explicitly unsupported."""
    result = _lex_and_parse(b"SORT FILE-1.")
    assert any(
        d.kind == DiagnosticKind.UNSUPPORTED_FEATURE
        for d in result.diagnostics
    )


def test_merge_unsupported():
    """MERGE is explicitly unsupported."""
    result = _lex_and_parse(b"MERGE FILE-1.")
    assert any(
        d.kind == DiagnosticKind.UNSUPPORTED_FEATURE
        for d in result.diagnostics
    )


# ---------------------------------------------------------------------------
# Grammar classification helpers
# ---------------------------------------------------------------------------

def test_grammar_is_supported_move():
    """grammar.is_supported('MOVE') returns True."""
    from modernize_v2.parser.grammar import is_supported
    assert is_supported("MOVE")


def test_grammar_is_unsupported_read():
    """grammar.is_supported('READ') returns False."""
    from modernize_v2.parser.grammar import is_supported
    assert not is_supported("READ")


def test_grammar_classify_supported():
    """grammar.classify('MOVE') returns 'SUPPORTED'."""
    from modernize_v2.parser.grammar import classify
    assert classify("MOVE") == "SUPPORTED"


def test_grammar_classify_unsupported():
    """grammar.classify('READ') returns 'UNSUPPORTED'."""
    from modernize_v2.parser.grammar import classify
    assert classify("READ") == "UNSUPPORTED"
