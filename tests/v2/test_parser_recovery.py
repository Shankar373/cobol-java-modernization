"""T-2B-03 Parser Recovery Tests.

Verifies that the parser produces diagnostics for unsupported
constructs and recovers to continue parsing sibling statements.
"""

from __future__ import annotations

import pytest

from modernize_v2.ir.diagnostic import DiagnosticKind
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
# Unsupported features produce UNSUPPORTED_FEATURE diagnostics
# ---------------------------------------------------------------------------

def test_unsupported_read():
    """READ produces UNSUPPORTED_FEATURE diagnostic."""
    result = _lex_and_parse(b"READ FILE-1.")
    assert any(
        d.kind == DiagnosticKind.UNSUPPORTED_FEATURE
        for d in result.diagnostics
    )


def test_unsupported_write():
    """WRITE produces UNSUPPORTED_FEATURE diagnostic."""
    result = _lex_and_parse(b"WRITE RECORD-1.")
    assert any(
        d.kind == DiagnosticKind.UNSUPPORTED_FEATURE
        for d in result.diagnostics
    )


def test_unsupported_rewrite():
    """REWRITE produces UNSUPPORTED_FEATURE diagnostic."""
    result = _lex_and_parse(b"REWRITE RECORD-1.")
    assert any(
        d.kind == DiagnosticKind.UNSUPPORTED_FEATURE
        for d in result.diagnostics
    )


def test_unsupported_delete():
    """DELETE produces UNSUPPORTED_FEATURE diagnostic."""
    result = _lex_and_parse(b"DELETE RECORD-1.")
    assert any(
        d.kind == DiagnosticKind.UNSUPPORTED_FEATURE
        for d in result.diagnostics
    )


def test_unsupported_sort():
    """SORT produces UNSUPPORTED_FEATURE diagnostic."""
    result = _lex_and_parse(b"SORT FILE-1.")
    assert any(
        d.kind == DiagnosticKind.UNSUPPORTED_FEATURE
        for d in result.diagnostics
    )


def test_unsupported_merge():
    """MERGE produces UNSUPPORTED_FEATURE diagnostic."""
    result = _lex_and_parse(b"MERGE FILE-1.")
    assert any(
        d.kind == DiagnosticKind.UNSUPPORTED_FEATURE
        for d in result.diagnostics
    )


# ---------------------------------------------------------------------------
# Recovery continues to following valid statement
# ---------------------------------------------------------------------------

def test_recovery_continues_after_unsupported():
    """After an unsupported construct, the parser continues to the next statement."""
    result = _lex_and_parse(b"READ FILE-1.\nMOVE A TO B.")
    # The MOVE statement should be parsed
    assert len(result.ast.statements) == 1
    # The READ should be diagnosed
    assert any(
        d.kind == DiagnosticKind.UNSUPPORTED_FEATURE
        for d in result.diagnostics
    )


def test_recovery_continues_after_unsupported_complex():
    """Recovery works across multiple unsupported/valid statements."""
    result = _lex_and_parse(
        b"MOVE A TO B.\nREAD FILE-1.\nMOVE C TO D.\nWRITE REC.\nMOVE E TO F."
    )
    # The three MOVE statements should be parsed
    assert len(result.ast.statements) == 3
    # The READ and WRITE should be diagnosed
    unsupported_diags = [
        d for d in result.diagnostics
        if d.kind == DiagnosticKind.UNSUPPORTED_FEATURE
    ]
    assert len(unsupported_diags) >= 2


# ---------------------------------------------------------------------------
# Recovery records
# ---------------------------------------------------------------------------

def test_recovery_record_created():
    """An unsupported construct produces a RecoveryRecord."""
    result = _lex_and_parse(b"READ FILE-1.\nMOVE A TO B.")
    # At least one recovery record should be created
    assert len(result.recovery_records) >= 1


# ---------------------------------------------------------------------------
# Malformed input
# ---------------------------------------------------------------------------

def test_malformed_move_missing_target():
    """MOVE A TO with no target produces a diagnostic."""
    result = _lex_and_parse(b"MOVE A TO")
    # Should have at least one diagnostic
    assert len(result.diagnostics) >= 1


def test_if_without_end_if():
    """IF without END-IF produces a diagnostic."""
    result = _lex_and_parse(b"IF A > B MOVE X TO Y")
    # Should have a diagnostic about missing END-IF
    assert len(result.diagnostics) >= 1
