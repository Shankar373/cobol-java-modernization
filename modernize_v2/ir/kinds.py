"""IRKind — the canonical IR node kind vocabulary.

The V2 architecture (§6 of docs/PHASE_2_ARCHITECTURE_V2.md)
defines the kinds the IR must distinguish. The vocabulary below
is the public source of truth.

Kinds are organized into categories:

    * Compilation structure (CompilationUnit, Program, Division,
      Section, Paragraph, Sentence).
    * Data items (DataItem, GroupItem, ElementaryItem, OdoClause,
      OccursClause, RedefinesClause, RenamesClause, Level88Item).
    * Statements (Statement, with semantic subkinds for arithmetic,
      move, control flow, IO, call, sql, cics, jcl).
    * Expressions (Expression, with semantic subkinds for literals,
      refs, operators, intrinsic calls).
    * Sections and storage (WorkingStorageSection, LocalStorageSection,
      LinkageSection, ReportSection, FileSection, FD, SD).
    * SQL (SqlStatement, with subkinds for SELECT, INSERT, UPDATE,
      DELETE, COMMIT, ROLLBACK, OPEN, FETCH, CLOSE).
    * CICS (CicsStatement, with subkinds for LINK, XCTL, RETURN,
      SEND MAP, RECEIVE MAP, SYNCPOINT, ROLLBACK).
    * JCL (JclJob, JclStep, DdStatement).

The kind names use a dotted notation for subkinds
(e.g. ``STATEMENT.ARITHMETIC.ADD``). This keeps the enum flat for
iteration while preserving semantic grouping.

This module implements the **vocabulary and contracts** only. The
typed IR data classes (Phase 2B) will be introduced in
``canonical.py`` and will use these kinds as their type tag.

No IO, no env access. The module is pure.
"""

from __future__ import annotations

from enum import Enum
from typing import Final, Iterator


class IRKind(str, Enum):
    """Canonical IR node kind vocabulary.

    Every IR node carries exactly one kind. The kind is the
    primary discriminator for downstream pattern matching and for
    the kind namespace in ``ids.id_for_node``.
    """

    # ---- Compilation structure ---------------------------------

    COMPILATION_UNIT = "COMPILATION_UNIT"
    PROGRAM = "PROGRAM"
    IDENTIFICATION_DIVISION = "IDENTIFICATION_DIVISION"
    ENVIRONMENT_DIVISION = "ENVIRONMENT_DIVISION"
    DATA_DIVISION = "DATA_DIVISION"
    PROCEDURE_DIVISION = "PROCEDURE_DIVISION"
    SECTION = "SECTION"
    PARAGRAPH = "PARAGRAPH"
    SENTENCE = "SENTENCE"

    # ---- Storage sections ---------------------------------------

    WORKING_STORAGE_SECTION = "WORKING_STORAGE_SECTION"
    LOCAL_STORAGE_SECTION = "LOCAL_STORAGE_SECTION"
    LINKAGE_SECTION = "LINKAGE_SECTION"
    REPORT_SECTION = "REPORT_SECTION"
    FILE_SECTION = "FILE_SECTION"
    FILE_DESCRIPTION = "FD"
    SORT_FILE_DESCRIPTION = "SD"

    # ---- Data items --------------------------------------------

    DATA_ITEM = "DATA_ITEM"
    GROUP_ITEM = "GROUP_ITEM"
    ELEMENTARY_ITEM = "ELEMENTARY_ITEM"
    LEVEL_88_ITEM = "LEVEL_88_ITEM"
    OCCURS_CLAUSE = "OCCURS_CLAUSE"
    ODO_CLAUSE = "ODO_CLAUSE"
    REDEFINES_CLAUSE = "REDEFINES_CLAUSE"
    RENAMES_CLAUSE = "RENAMES_CLAUSE"

    # T-2B-04R.3: Structural data-item clause kinds.
    #: Syntactic recognition of a ``PIC`` / ``PICTURE`` clause
    #: within a Data Division data-item declaration.  R.3 captures
    #: the raw PIC string and a few structural elements
    #: (category, size, sign, scale).  Semantic interpretation
    #: (byte size, Java type, COMP-3 encoding, etc.) is T-2B-08's
    #: responsibility.
    PIC_CLAUSE = "PIC_CLAUSE"
    #: Syntactic recognition of a ``USAGE`` clause within a Data
    #: Division data-item declaration.  R.3 captures the raw
    #: usage form text.  Semantic interpretation of USAGE
    #: (storage layout, COMP/COMP-3 encoding, etc.) is T-2B-08's
    #: responsibility.
    USAGE_CLAUSE = "USAGE_CLAUSE"
    #: Syntactic recognition of a ``VALUE`` clause within a Data
    #: Division data-item declaration.  R.3 captures the raw
    #: literal text.  Semantic interpretation of the literal
    #: (type checking, constant folding, etc.) is T-2B-08's
    #: responsibility.
    VALUE_CLAUSE = "VALUE_CLAUSE"

    # ---- Statements (general + subkinds) -----------------------

    STATEMENT = "STATEMENT"
    STATEMENT_ARITHMETIC_ADD = "STATEMENT.ARITHMETIC.ADD"
    STATEMENT_ARITHMETIC_SUBTRACT = "STATEMENT.ARITHMETIC.SUBTRACT"
    STATEMENT_ARITHMETIC_MULTIPLY = "STATEMENT.ARITHMETIC.MULTIPLY"
    STATEMENT_ARITHMETIC_DIVIDE = "STATEMENT.ARITHMETIC.DIVIDE"
    STATEMENT_ARITHMETIC_COMPUTE = "STATEMENT.ARITHMETIC.COMPUTE"
    STATEMENT_MOVE = "STATEMENT.MOVE"
    STATEMENT_IF = "STATEMENT.IF"
    STATEMENT_EVALUATE = "STATEMENT.EVALUATE"
    STATEMENT_PERFORM = "STATEMENT.PERFORM"
    STATEMENT_GO_TO = "STATEMENT.GO_TO"
    STATEMENT_STOP_RUN = "STATEMENT.STOP_RUN"
    STATEMENT_GOBACK = "STATEMENT.GOBACK"
    STATEMENT_NEXT_SENTENCE = "STATEMENT.NEXT_SENTENCE"
    STATEMENT_EXIT_PERFORM = "STATEMENT.EXIT_PERFORM"
    STATEMENT_EXIT_PARAGRAPH = "STATEMENT.EXIT_PARAGRAPH"
    STATEMENT_CALL_STATIC = "STATEMENT.CALL.STATIC"
    STATEMENT_CALL_DYNAMIC = "STATEMENT.CALL.DYNAMIC"
    STATEMENT_STRING = "STATEMENT.STRING"
    STATEMENT_UNSTRING = "STATEMENT.UNSTRING"
    STATEMENT_INSPECT = "STATEMENT.INSPECT"
    STATEMENT_OPEN = "STATEMENT.OPEN"
    STATEMENT_CLOSE = "STATEMENT.CLOSE"
    STATEMENT_READ = "STATEMENT.READ"
    STATEMENT_WRITE = "STATEMENT.WRITE"
    STATEMENT_REWRITE = "STATEMENT.REWRITE"
    STATEMENT_DELETE = "STATEMENT.DELETE"
    STATEMENT_START = "STATEMENT.START"
    STATEMENT_SORT = "STATEMENT.SORT"
    STATEMENT_MERGE = "STATEMENT.MERGE"
    STATEMENT_DISPLAY = "STATEMENT.DISPLAY"
    STATEMENT_ACCEPT = "STATEMENT.ACCEPT"

    # ---- Expressions (general + subkinds) ----------------------

    EXPRESSION = "EXPRESSION"
    EXPRESSION_LITERAL = "EXPRESSION.LITERAL"
    EXPRESSION_REFERENCE = "EXPRESSION.REFERENCE"
    EXPRESSION_BINARY_OP = "EXPRESSION.BINARY_OP"
    EXPRESSION_UNARY_OP = "EXPRESSION.UNARY_OP"
    EXPRESSION_CONDITION = "EXPRESSION.CONDITION"
    EXPRESSION_LOGICAL = "EXPRESSION.LOGICAL"
    EXPRESSION_INTRINSIC_CALL = "EXPRESSION.INTRINSIC_CALL"
    EXPRESSION_INLINE_CALL = "EXPRESSION.INLINE_CALL"
    EXPRESSION_FIGURATIVE_CONSTANT = "EXPRESSION.FIGURATIVE_CONSTANT"
    EXPRESSION_SUBSCRIPT = "EXPRESSION.SUBSCRIPT"
    EXPRESSION_REFMOD = "EXPRESSION.REFMOD"

    # ---- SQL (embedded) ----------------------------------------

    SQL_STATEMENT = "SQL_STATEMENT"
    SQL_SELECT = "SQL.SELECT"
    SQL_INSERT = "SQL.INSERT"
    SQL_UPDATE = "SQL.UPDATE"
    SQL_DELETE = "SQL.DELETE"
    SQL_CURSOR_DECLARE = "SQL.CURSOR.DECLARE"
    SQL_CURSOR_OPEN = "SQL.CURSOR.OPEN"
    SQL_CURSOR_FETCH = "SQL.CURSOR.FETCH"
    SQL_CURSOR_CLOSE = "SQL.CURSOR.CLOSE"
    SQL_COMMIT = "SQL.COMMIT"
    SQL_ROLLBACK = "SQL.ROLLBACK"
    SQL_CONNECT = "SQL.CONNECT"
    SQL_DDL = "SQL.DDL"

    # ---- CICS ---------------------------------------------------

    CICS_STATEMENT = "CICS_STATEMENT"
    CICS_LINK = "CICS.LINK"
    CICS_XCTL = "CICS.XCTL"
    CICS_RETURN = "CICS.RETURN"
    CICS_SEND_MAP = "CICS.SEND_MAP"
    CICS_RECEIVE_MAP = "CICS.RECEIVE_MAP"
    CICS_SYNCPOINT = "CICS.SYNCPOINT"
    CICS_ROLLBACK = "CICS.ROLLBACK"
    CICS_ENQUEUE = "CICS.ENQUEUE"
    CICS_DEQUEUE = "CICS.DEQUEUE"
    CICS_READ = "CICS.READ"
    CICS_WRITE = "CICS.WRITE"
    CICS_ERASE = "CICS.ERASE"

    # ---- JCL ---------------------------------------------------

    JCL_JOB = "JCL.JOB"
    JCL_STEP = "JCL.STEP"
    JCL_DD_STATEMENT = "JCL.DD"
    JCL_PROC = "JCL.PROC"
    JCL_PEND = "JCL.PEND"
    JCL_IF = "JCL.IF"
    JCL_SET = "JCL.SET"
    JCL_INCLUDE = "JCL.INCLUDE"
    JCL_JOBLIB = "JCL.JOBLIB"
    JCL_STEPLIB = "JCL.STEPLIB"


# --- Categories used by the gate and the diagnostic kinds. ---
# These are plain sets/frozensets, not enums, so they can be
# extended in later phases without churning the enum.

STATEMENT_KINDS: Final[frozenset[IRKind]] = frozenset(
    k for k in IRKind
    if k is IRKind.STATEMENT or k.name.startswith("STATEMENT_")
)
EXPRESSION_KINDS: Final[frozenset[IRKind]] = frozenset(
    k for k in IRKind
    if k is IRKind.EXPRESSION or k.name.startswith("EXPRESSION_")
)
SQL_KINDS: Final[frozenset[IRKind]] = frozenset(
    k for k in IRKind
    if k is IRKind.SQL_STATEMENT or k.name.startswith("SQL_")
)
CICS_KINDS: Final[frozenset[IRKind]] = frozenset(
    k for k in IRKind
    if k is IRKind.CICS_STATEMENT or k.name.startswith("CICS_")
)
JCL_KINDS: Final[frozenset[IRKind]] = frozenset(
    k for k in IRKind
    if k.name.startswith("JCL_")
)
DATA_ITEM_KINDS: Final[frozenset[IRKind]] = frozenset(
    k for k in IRKind
    if k.name in {
        "DATA_ITEM", "GROUP_ITEM", "ELEMENTARY_ITEM",
        "LEVEL_88_ITEM", "OCCURS_CLAUSE", "ODO_CLAUSE",
        "REDEFINES_CLAUSE", "RENAMES_CLAUSE",
        # T-2B-04R.3: structural data-item clause kinds.
        "PIC_CLAUSE", "USAGE_CLAUSE", "VALUE_CLAUSE",
    }
)


def is_statement_kind(kind: IRKind) -> bool:
    return kind in STATEMENT_KINDS


def is_expression_kind(kind: IRKind) -> bool:
    return kind in EXPRESSION_KINDS


def is_sql_kind(kind: IRKind) -> bool:
    return kind in SQL_KINDS


def is_cics_kind(kind: IRKind) -> bool:
    return kind in CICS_KINDS


def is_jcl_kind(kind: IRKind) -> bool:
    return kind in JCL_KINDS


def is_data_item_kind(kind: IRKind) -> bool:
    return kind in DATA_ITEM_KINDS


def iter_categories() -> Iterator[tuple[str, frozenset[IRKind]]]:
    """Yield (category_name, kinds) for every predefined category."""
    return iter([
        ("STATEMENT", STATEMENT_KINDS),
        ("EXPRESSION", EXPRESSION_KINDS),
        ("SQL", SQL_KINDS),
        ("CICS", CICS_KINDS),
        ("JCL", JCL_KINDS),
        ("DATA_ITEM", DATA_ITEM_KINDS),
    ])


__all__ = [
    "IRKind",
    "STATEMENT_KINDS",
    "EXPRESSION_KINDS",
    "SQL_KINDS",
    "CICS_KINDS",
    "JCL_KINDS",
    "DATA_ITEM_KINDS",
    "is_statement_kind",
    "is_expression_kind",
    "is_sql_kind",
    "is_cics_kind",
    "is_jcl_kind",
    "is_data_item_kind",
    "iter_categories",
]
