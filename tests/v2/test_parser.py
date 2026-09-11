"""T-2B-03 Parser Core Tests.

Verifies the deterministic COBOL syntax parser produces correct
AST structures for the supported grammar.

These tests do NOT exercise the lexer directly; they use the
lexer to build a token stream, then call the parser.
"""

from __future__ import annotations

import pytest

from modernize_v2.ir.kinds import IRKind
from modernize_v2.lexer import CobolLexer, SourceFormat
from modernize_v2.parser import (
    AddStatement,
    BinaryOpExpression,
    ComputeStatement,
    DisplayStatement,
    DivideStatement,
    IfStatement,
    LiteralExpression,
    MoveStatement,
    MultiplyStatement,
    Parser,
    PerformStatement,
    StopRunStatement,
    SubtractStatement,
)
from modernize_v2.source import make_source_file


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _lex_and_parse(source: bytes, *, path: str = "test.cbl", fmt: SourceFormat = SourceFormat.FREE):
    """Lex and parse *source*, returning the ParserResult."""
    sf = make_source_file(path, source)
    lexer = CobolLexer(sf, source, fmt)
    tokens = lexer.lex()
    parser = Parser(tokens, canonical_path=path)
    return parser.parse()


# ---------------------------------------------------------------------------
# Empty input / EOF handling
# ---------------------------------------------------------------------------

def test_empty_source():
    """Empty source produces an empty AST with no statements."""
    result = _lex_and_parse(b"")
    assert len(result.ast.statements) == 0
    assert result.eof_at_byte == 0
    assert len(result.diagnostics) == 0


def test_only_period():
    """A source with only a period produces no statements."""
    result = _lex_and_parse(b".")
    assert len(result.ast.statements) == 0


# ---------------------------------------------------------------------------
# MOVE
# ---------------------------------------------------------------------------

def test_simple_move():
    """MOVE A TO B produces a MoveStatement."""
    result = _lex_and_parse(b"MOVE A TO B.")
    assert len(result.ast.statements) == 1
    stmt = result.ast.statements[0]
    assert isinstance(stmt, MoveStatement)
    assert stmt.source.identifier_text == "A"
    assert stmt.target.identifier_text == "B"


def test_move_with_hyphenated_identifiers():
    """MOVE CUST-NAME TO WS-OUTPUT."""
    result = _lex_and_parse(b"MOVE CUST-NAME TO WS-OUTPUT.")
    assert len(result.ast.statements) == 1
    stmt = result.ast.statements[0]
    assert isinstance(stmt, MoveStatement)
    assert stmt.source.identifier_text == "CUST-NAME"
    assert stmt.target.identifier_text == "WS-OUTPUT"


# ---------------------------------------------------------------------------
# DISPLAY
# ---------------------------------------------------------------------------

def test_simple_display():
    """DISPLAY <identifier> produces a DisplayStatement."""
    result = _lex_and_parse(b"DISPLAY WS-MESSAGE.")
    assert len(result.ast.statements) == 1
    stmt = result.ast.statements[0]
    assert isinstance(stmt, DisplayStatement)
    assert stmt.operand.identifier_text == "WS-MESSAGE"


# ---------------------------------------------------------------------------
# Arithmetic verbs
# ---------------------------------------------------------------------------

def test_add_statement():
    """ADD A TO B."""
    result = _lex_and_parse(b"ADD A TO B.")
    assert len(result.ast.statements) == 1
    stmt = result.ast.statements[0]
    assert isinstance(stmt, AddStatement)
    assert stmt.left.identifier_text == "A"
    assert stmt.right.identifier_text == "B"
    assert stmt.giving is None


def test_add_with_giving():
    """ADD A TO B GIVING C."""
    result = _lex_and_parse(b"ADD A TO B GIVING C.")
    stmt = result.ast.statements[0]
    assert isinstance(stmt, AddStatement)
    assert stmt.giving is not None
    assert stmt.giving.identifier_text == "C"


def test_subtract_statement():
    """SUBTRACT A FROM B."""
    result = _lex_and_parse(b"SUBTRACT A FROM B.")
    stmt = result.ast.statements[0]
    assert isinstance(stmt, SubtractStatement)
    assert stmt.left.identifier_text == "A"
    assert stmt.right.identifier_text == "B"


def test_multiply_statement():
    """MULTIPLY A BY B."""
    result = _lex_and_parse(b"MULTIPLY A BY B.")
    stmt = result.ast.statements[0]
    assert isinstance(stmt, MultiplyStatement)
    assert stmt.left.identifier_text == "A"
    assert stmt.right.identifier_text == "B"


def test_divide_statement():
    """DIVIDE A INTO B."""
    result = _lex_and_parse(b"DIVIDE A INTO B.")
    stmt = result.ast.statements[0]
    assert isinstance(stmt, DivideStatement)
    assert stmt.left.identifier_text == "A"
    assert stmt.right.identifier_text == "B"


def test_compute_statement():
    """COMPUTE X = A + B."""
    result = _lex_and_parse(b"COMPUTE X = A + B.")
    stmt = result.ast.statements[0]
    assert isinstance(stmt, ComputeStatement)
    assert stmt.target.identifier_text == "X"
    assert isinstance(stmt.expression, BinaryOpExpression)
    assert stmt.expression.operator_text == "+"


# ---------------------------------------------------------------------------
# Control flow: IF / ELSE / END-IF
# ---------------------------------------------------------------------------

def test_if_statement():
    """IF <cond> MOVE X TO Y END-IF."""
    result = _lex_and_parse(b"IF A > B MOVE X TO Y END-IF.")
    assert len(result.ast.statements) == 1
    stmt = result.ast.statements[0]
    assert isinstance(stmt, IfStatement)
    assert len(stmt.then_body) == 1
    assert len(stmt.else_body) == 0


def test_if_else_statement():
    """IF <cond> THEN MOVE X TO Y ELSE MOVE P TO Q END-IF."""
    result = _lex_and_parse(
        b"IF A > B MOVE X TO Y ELSE MOVE P TO Q END-IF."
    )
    assert len(result.ast.statements) == 1
    stmt = result.ast.statements[0]
    assert isinstance(stmt, IfStatement)
    assert len(stmt.then_body) == 1
    assert len(stmt.else_body) == 1
    # First then statement
    then_stmt = stmt.then_body[0]
    assert isinstance(then_stmt, MoveStatement)
    assert then_stmt.source.identifier_text == "X"
    # First else statement
    else_stmt = stmt.else_body[0]
    assert isinstance(else_stmt, MoveStatement)
    assert else_stmt.source.identifier_text == "P"


def test_if_with_comparison_condition():
    """IF A = B ... END-IF."""
    result = _lex_and_parse(b"IF A = B MOVE X TO Y END-IF.")
    stmt = result.ast.statements[0]
    assert isinstance(stmt, IfStatement)
    # Condition is a comparison
    cond = stmt.condition
    assert cond.operator_text == "="
    assert cond.left.identifier_text == "A"
    assert cond.right.identifier_text == "B"


# ---------------------------------------------------------------------------
# Stop/Goback
# ---------------------------------------------------------------------------

def test_stop_run():
    """STOP RUN."""
    result = _lex_and_parse(b"STOP RUN.")
    assert len(result.ast.statements) == 1
    assert isinstance(result.ast.statements[0], StopRunStatement)


# ---------------------------------------------------------------------------
# Expression precedence
# ---------------------------------------------------------------------------

def test_expression_precedence_add_mul():
    """A + B * C must parse as A + (B * C)."""
    result = _lex_and_parse(b"COMPUTE X = A + B * C.")
    stmt = result.ast.statements[0]
    expr = stmt.expression
    assert isinstance(expr, BinaryOpExpression)
    assert expr.operator_text == "+"
    # Left should be identifier A
    assert expr.left.identifier_text == "A"
    # Right should be BinaryOp with op '*'
    assert isinstance(expr.right, BinaryOpExpression)
    assert expr.right.operator_text == "*"
    assert expr.right.left.identifier_text == "B"
    assert expr.right.right.identifier_text == "C"


def test_expression_precedence_mul_add():
    """A * B + C must parse as (A * B) + C."""
    result = _lex_and_parse(b"COMPUTE X = A * B + C.")
    stmt = result.ast.statements[0]
    expr = stmt.expression
    assert isinstance(expr, BinaryOpExpression)
    assert expr.operator_text == "+"
    # Left should be BinaryOp with op '*'
    assert isinstance(expr.left, BinaryOpExpression)
    assert expr.left.operator_text == "*"


def test_parenthesized_expression():
    """(A + B) * C must preserve parentheses grouping."""
    result = _lex_and_parse(b"COMPUTE X = (A + B) * C.")
    stmt = result.ast.statements[0]
    expr = stmt.expression
    assert isinstance(expr, BinaryOpExpression)
    assert expr.operator_text == "*"
    # Left should be the parenthesized BinaryOp(A + B)
    assert isinstance(expr.left, BinaryOpExpression)
    assert expr.left.operator_text == "+"


# ---------------------------------------------------------------------------
# Numeric literal classification
# ---------------------------------------------------------------------------

def test_figurative_constant():
    """ZERO is a figurative constant (lexer-emitted as KEYWORD)."""
    result = _lex_and_parse(b"MOVE ZERO TO X.")
    stmt = result.ast.statements[0]
    assert isinstance(stmt.source, LiteralExpression)
    assert stmt.source.literal_kind == "FIGURATIVE"
    assert stmt.source.literal_raw_text == "ZERO"
