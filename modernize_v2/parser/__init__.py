"""T-2B-03 Deterministic COBOL Syntax Parser package.

A syntax-only parser that consumes T-2B-02 token streams and produces
a typed, immutable AST. Does NOT perform semantic analysis, symbol
resolution, or type mapping.

See PHASE_2B_T3_IMPLEMENTATION_REPORT.md for full design documentation.
"""

from __future__ import annotations

from .recovery import RecoveryRecord
from .nodes import (
    IdentifierExpression,
    LiteralExpression,
    BinaryOpExpression,
    UnaryOpExpression,
    CondExpression,
    LogicalExpression,
    MoveStatement,
    DisplayStatement,
    AddStatement,
    SubtractStatement,
    MultiplyStatement,
    DivideStatement,
    ComputeStatement,
    IfStatement,
    EvaluateStatement,
    PerformStatement,
    GoToStatement,
    StopRunStatement,
    GoBackStatement,
    ExitPerformStatement,
    ExitParagraphStatement,
    DataDivisionSubsection,
    DataItemDeclaration,
    PicClause,
    UsageClause,
    ValueClause,
    CompilationUnit,
    ParserResult,
)
from .parser import Parser

__all__ = [
    "Parser",
    "ParserResult",
    "RecoveryRecord",
    "IdentifierExpression",
    "LiteralExpression",
    "BinaryOpExpression",
    "UnaryOpExpression",
    "CondExpression",
    "LogicalExpression",
    "MoveStatement",
    "DisplayStatement",
    "AddStatement",
    "SubtractStatement",
    "MultiplyStatement",
    "DivideStatement",
    "ComputeStatement",
    "IfStatement",
    "EvaluateStatement",
    "PerformStatement",
    "GoToStatement",
    "StopRunStatement",
    "GoBackStatement",
    "ExitPerformStatement",
    "ExitParagraphStatement",
    "DataDivisionSubsection",
    "DataItemDeclaration",
    "PicClause",
    "UsageClause",
    "ValueClause",
    "CompilationUnit",
]
