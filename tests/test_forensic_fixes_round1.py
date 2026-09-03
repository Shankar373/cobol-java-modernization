"""Regression tests for forensic audit round-1 fixes.

Covers:
1. data_flow.py identifier-boundary matching (no false DERIVES_FROM/USES edges)
2. equivalence.py one-sided DB evidence must FAIL (fail-closed), not pass
3. lexer.py missing/failed copybook expansion must be recorded in unsupported
"""

import pytest

from execution.contracts import ExecutionContract
from execution.equivalence import EquivalenceEngine
from execution.observations import ExecutionObservation
from modernize import CobolLexer, CobolParser
from modernize.control_flow import ControlFlowModel
from modernize.data_flow import DataFlowModel, _var_in_expr


# ---------------------------------------------------------------------------
# 1. data_flow identifier boundaries
# ---------------------------------------------------------------------------

def test_var_in_expr_identifier_boundaries():
    assert _var_in_expr("WS-A", "WS-A + 1")
    assert _var_in_expr("WS-A", "(WS-A) * 2")
    assert _var_in_expr("WS-A", "WS-AB + 1") is False      # prefix false match
    assert _var_in_expr("WS-A", "X" + "WS-A1") is False    # suffix false match
    assert _var_in_expr("WS-A", "") is False
    assert _var_in_expr("", "WS-A") is False


def test_dataflow_no_false_positive_derives_from():
    # Variables WS-RATE and WS-RATE-ADJUSTED; the COMPUTE only touches the
    # longer name. A substring matcher would wrongly create an edge from both.
    source = (
        "000100 IDENTIFICATION DIVISION.\n"
        "000200 PROGRAM-ID. DF-BOUNDARY-TEST.\n"
        "000300 DATA DIVISION.\n"
        "000400 WORKING-STORAGE SECTION.\n"
        "000500 01  WS-RATE PIC 9(3).\n"
        "000600 01  WS-RATE-ADJUSTED PIC 9(5).\n"
        "000700 01  WS-RESULT PIC 9(5).\n"
        "000800 PROCEDURE DIVISION.\n"
        "000900 MAIN-PARA.\n"
        "001000     COMPUTE WS-RESULT = WS-RATE-ADJUSTED + 1\n"
        "001100     STOP RUN.\n"
    )
    lexer = CobolLexer("inline.cob")
    tokens = lexer.tokenize(source)
    parser = CobolParser(tokens, "df_boundary_test.cob")
    ir = parser.parse()
    cfg = ControlFlowModel.build_from_ir(ir)
    model = DataFlowModel.build_from_ir(ir, cfg)
    derives = [e for e in model.edges if e.classification == "DERIVES_FROM"]
    assert any(e.from_node == "df_var_WS-RATE-ADJUSTED" for e in derives), \
        "actual operand edge missing"
    assert not any(e.from_node == "df_var_WS-RATE" for e in derives), \
        "false-positive edge from WS-RATE must not exist"
    assert not any(
        e.from_node.endswith("WS-RATE") and "ADJUSTED" not in e.from_node
        for e in derives
    ), "prefix-derived phantom edge detected"


# ---------------------------------------------------------------------------
# 2. equivalence fail-closed on one-sided DB evidence
# ---------------------------------------------------------------------------

def _db_observation(scenario_id, db_state):
    return ExecutionObservation(
        scenario_id=scenario_id,
        exit_code=0,
        stdout="",
        stderr="",
        files=[],
        database_state=db_state,
        execution_status="completed",
    )


def test_equivalence_one_sided_row_counts_fails():
    contract = ExecutionContract(expected_output_modes=["EXPECTED_DATABASE_STATE"])
    cobol = _db_observation("S1", {"ctx": {"row_counts": {"CUSTOMER": 5}}})
    java = _db_observation("S1", {"ctx": {}})
    result = EquivalenceEngine.compare(cobol, java, contract)
    assert result.status == "FAIL"
    assert result.checks["database_state"] == "FAIL"
    assert any(d["type"] == "database_row_counts_one_sided"
               for d in result.differences)


def test_equivalence_symmetric_empty_db_evidence_does_not_fail():
    # Neither side captured data: nothing to compare, no spurious one-sided FAIL
    # (the check remains UNVERIFIED, which is correctly non-PASS).
    contract = ExecutionContract(expected_output_modes=["EXPECTED_DATABASE_STATE"])
    cobol = _db_observation("S1", {"ctx": {}})
    java = _db_observation("S1", {"ctx": {}})
    result = EquivalenceEngine.compare(cobol, java, contract)
    assert result.checks["database_state"] != "FAIL"
    assert result.status in ("UNVERIFIED", "NOT_APPLICABLE", "PASS")


def test_equivalence_matching_row_counts_passes_db_check():
    contract = ExecutionContract(expected_output_modes=["EXPECTED_DATABASE_STATE"])
    state = {"ctx": {"row_counts": {"CUSTOMER": 5}}}
    cobol = _db_observation("S1", dict(state))
    java = _db_observation("S1", dict(state))
    result = EquivalenceEngine.compare(cobol, java, contract)
    assert result.checks["database_state"] == "PASS"


# ---------------------------------------------------------------------------
# 3. lexer copybook visibility
# ---------------------------------------------------------------------------

def test_lexer_missing_copybook_is_recorded():
    source = (
        "       IDENTIFICATION DIVISION.\n"
        "       PROGRAM-ID. CP-TEST.\n"
        "       DATA DIVISION.\n"
        "       WORKING-STORAGE SECTION.\n"
        "       COPY NOSUCHBOOK-XYZ.\n"
        "       PROCEDURE DIVISION.\n"
        "       MAIN-PARA.\n"
        "           STOP RUN.\n"
    )
    lexer = CobolLexer("inline.cob")
    lexer.tokenize(source)
    reasons = [u.get("reason", "") for u in lexer.unsupported]
    assert any("COPYBOOK_NOT_FOUND" in r and "NOSUCHBOOK-XYZ" in r
               for r in reasons), f"missing-record copybook not surfaced: {reasons}"
