"""Tests for modernize_v2.ir.kinds — IRKind vocabulary.

Acceptance criteria from T-2A-02:

    * the vocabulary is real (not padded to satisfy an arbitrary
      count)
    * the categories are coherent
    * kind names are stable strings
    * helpers correctly classify kinds
"""

from __future__ import annotations

import pytest

from modernize_v2.ir.kinds import (
    CICS_KINDS,
    DATA_ITEM_KINDS,
    EXPRESSION_KINDS,
    IRKind,
    JCL_KINDS,
    SQL_KINDS,
    STATEMENT_KINDS,
    is_cics_kind,
    is_data_item_kind,
    is_expression_kind,
    is_jcl_kind,
    is_sql_kind,
    is_statement_kind,
    iter_categories,
)


def test_kind_names_are_stable_strings() -> None:
    assert IRKind.PROGRAM.value == "PROGRAM"
    assert IRKind.STATEMENT.value == "STATEMENT"
    assert IRKind.STATEMENT_MOVE.value == "STATEMENT.MOVE"
    assert IRKind.SQL_SELECT.value == "SQL.SELECT"
    assert IRKind.CICS_LINK.value == "CICS.LINK"
    assert IRKind.JCL_STEP.value == "JCL.STEP"


def test_division_kinds_present() -> None:
    for k in (
        "IDENTIFICATION_DIVISION",
        "ENVIRONMENT_DIVISION",
        "DATA_DIVISION",
        "PROCEDURE_DIVISION",
    ):
        assert IRKind(k) is not None


def test_storage_section_kinds_present() -> None:
    for k in (
        "WORKING_STORAGE_SECTION",
        "LOCAL_STORAGE_SECTION",
        "LINKAGE_SECTION",
        "REPORT_SECTION",
        "FILE_SECTION",
        "FD",
        "SD",
    ):
        assert IRKind(k) is not None


def test_data_item_clause_kinds_present() -> None:
    for k in (
        "DATA_ITEM",
        "GROUP_ITEM",
        "ELEMENTARY_ITEM",
        "LEVEL_88_ITEM",
        "OCCURS_CLAUSE",
        "ODO_CLAUSE",
        "REDEFINES_CLAUSE",
        "RENAMES_CLAUSE",
    ):
        assert IRKind(k) is not None


def test_statement_arithmetic_subkinds_present() -> None:
    for op in ("ADD", "SUBTRACT", "MULTIPLY", "DIVIDE", "COMPUTE"):
        assert IRKind(f"STATEMENT.ARITHMETIC.{op}") is not None


def test_statement_control_flow_kinds_present() -> None:
    for s in (
        "STATEMENT.MOVE",
        "STATEMENT.IF",
        "STATEMENT.EVALUATE",
        "STATEMENT.PERFORM",
        "STATEMENT.GO_TO",
        "STATEMENT.STOP_RUN",
        "STATEMENT.GOBACK",
        "STATEMENT.NEXT_SENTENCE",
        "STATEMENT.EXIT_PERFORM",
        "STATEMENT.EXIT_PARAGRAPH",
    ):
        assert IRKind(s) is not None


def test_statement_io_kinds_present() -> None:
    for s in (
        "STATEMENT.OPEN",
        "STATEMENT.CLOSE",
        "STATEMENT.READ",
        "STATEMENT.WRITE",
        "STATEMENT.REWRITE",
        "STATEMENT.DELETE",
        "STATEMENT.START",
    ):
        assert IRKind(s) is not None


def test_sql_kinds_present() -> None:
    for s in (
        "SQL_STATEMENT",
        "SQL.SELECT",
        "SQL.INSERT",
        "SQL.UPDATE",
        "SQL.DELETE",
        "SQL.CURSOR.DECLARE",
        "SQL.CURSOR.OPEN",
        "SQL.CURSOR.FETCH",
        "SQL.CURSOR.CLOSE",
        "SQL.COMMIT",
        "SQL.ROLLBACK",
        "SQL.DDL",
    ):
        assert IRKind(s) is not None


def test_cics_kinds_present() -> None:
    for s in (
        "CICS_STATEMENT",
        "CICS.LINK",
        "CICS.XCTL",
        "CICS.RETURN",
        "CICS.SEND_MAP",
        "CICS.RECEIVE_MAP",
        "CICS.SYNCPOINT",
        "CICS.ROLLBACK",
    ):
        assert IRKind(s) is not None


def test_jcl_kinds_present() -> None:
    for s in (
        "JCL.JOB",
        "JCL.STEP",
        "JCL.DD",
        "JCL.PROC",
        "JCL.PEND",
        "JCL.IF",
        "JCL.SET",
    ):
        assert IRKind(s) is not None


def test_categories_are_disjoint() -> None:
    cats = [
        STATEMENT_KINDS, EXPRESSION_KINDS, SQL_KINDS,
        CICS_KINDS, JCL_KINDS, DATA_ITEM_KINDS,
    ]
    seen: dict[IRKind, str] = {}
    for cat in cats:
        for k in cat:
            assert k not in seen, f"{k} in {seen[k]} and {cat}"
            seen[k] = str(cat)


def test_helpers() -> None:
    assert is_statement_kind(IRKind.STATEMENT_MOVE)
    assert is_statement_kind(IRKind.STATEMENT)
    assert not is_statement_kind(IRKind.SQL_SELECT)

    assert is_expression_kind(IRKind.EXPRESSION_LITERAL)
    assert is_expression_kind(IRKind.EXPRESSION)
    assert not is_expression_kind(IRKind.STATEMENT_MOVE)

    assert is_sql_kind(IRKind.SQL_SELECT)
    assert is_sql_kind(IRKind.SQL_STATEMENT)
    assert not is_sql_kind(IRKind.CICS_LINK)

    assert is_cics_kind(IRKind.CICS_LINK)
    assert is_cics_kind(IRKind.CICS_STATEMENT)
    assert not is_cics_kind(IRKind.JCL_STEP)

    assert is_jcl_kind(IRKind.JCL_STEP)
    assert is_jcl_kind(IRKind.JCL_DD_STATEMENT)
    assert not is_jcl_kind(IRKind.SQL_INSERT)

    assert is_data_item_kind(IRKind.DATA_ITEM)
    assert is_data_item_kind(IRKind.GROUP_ITEM)
    assert is_data_item_kind(IRKind.ODO_CLAUSE)
    assert not is_data_item_kind(IRKind.STATEMENT_MOVE)


def test_iter_categories_yields_expected_names() -> None:
    seen = {name for name, _ in iter_categories()}
    assert seen == {
        "STATEMENT", "EXPRESSION", "SQL", "CICS", "JCL", "DATA_ITEM",
    }


def test_unknown_kind_lookup_raises() -> None:
    with pytest.raises(ValueError):
        IRKind("NOPE_NOT_A_KIND")
