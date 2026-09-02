"""Tests for Multi-Oracle Differential Verification."""

import pytest
from tools.reference_runtimes.base import ReferenceExecutionResult, RuntimeStatus
from tools.reference_runtimes.differential_verifier import MultiOracleDifferentialVerifier


def test_multi_oracle_perfect_match():
    gnu_res = ReferenceExecutionResult(
        runtime_name="GnuCOBOL",
        status=RuntimeStatus.EXECUTED,
        output_files={"data/out/out.txt": b"1001|ITEM_A\n1002|ITEM_B\n"},
    )
    gnu_res.calculate_hashes()

    z390_res = ReferenceExecutionResult(
        runtime_name="z390",
        status=RuntimeStatus.EXECUTED,
        output_files={"data/out/out.txt": b"1001|ITEM_A\n1002|ITEM_B\n"},
    )
    z390_res.calculate_hashes()

    java_outputs = {"data/out/out.txt": b"1001|ITEM_A\n1002|ITEM_B\n"}

    report = MultiOracleDifferentialVerifier.compare_multi_oracle(
        java_outputs=java_outputs,
        gnucobol_result=gnu_res,
        z390_result=z390_res,
    )
    assert report.is_match is True
    assert report.status == "MATCH"
    assert len(report.mismatches) == 0
    assert len(report.disagreements) == 0


def test_multi_oracle_reference_disagreement_detection():
    gnu_res = ReferenceExecutionResult(
        runtime_name="GnuCOBOL",
        status=RuntimeStatus.EXECUTED,
        output_files={"data/out/out.txt": b"1001|ITEM_A\n1002|ITEM_B\n"},
    )
    gnu_res.calculate_hashes()

    z390_res = ReferenceExecutionResult(
        runtime_name="z390",
        status=RuntimeStatus.EXECUTED,
        output_files={"data/out/out.txt": b"1001|ITEM_A   \n1002|ITEM_B   \n"},
    )
    z390_res.calculate_hashes()

    java_outputs = {"data/out/out.txt": b"1001|ITEM_A\n1002|ITEM_B\n"}

    report = MultiOracleDifferentialVerifier.compare_multi_oracle(
        java_outputs=java_outputs,
        gnucobol_result=gnu_res,
        z390_result=z390_res,
    )
    # Java matches GnuCOBOL baseline, but GnuCOBOL vs z390 has a reference disagreement
    assert report.is_match is True
    assert report.status == "MATCH_WITH_REFERENCE_DISAGREEMENT"
    assert len(report.disagreements) > 0


def test_multi_oracle_unavailable_fails_closed():
    """Missing or unavailable GnuCOBOL must return REFERENCE_UNAVAILABLE and never pass."""
    gnu_res = ReferenceExecutionResult(
        runtime_name="GnuCOBOL",
        status=RuntimeStatus.UNAVAILABLE,
        error_message="GnuCOBOL docker container unavailable",
    )
    report = MultiOracleDifferentialVerifier.compare_multi_oracle(
        java_outputs={"out.txt": b"123"},
        gnucobol_result=gnu_res,
    )
    assert report.is_match is False
    assert report.status == "REFERENCE_UNAVAILABLE"
    assert "Cannot certify" in report.mismatches[0]


def test_multi_oracle_execution_failure():
    """GnuCOBOL compilation or execution failure must report REFERENCE_EXECUTION_FAILURE."""
    gnu_res = ReferenceExecutionResult(
        runtime_name="GnuCOBOL",
        status=RuntimeStatus.FAILED,
        error_message="Syntax error in COBOL input",
    )
    report = MultiOracleDifferentialVerifier.compare_multi_oracle(
        java_outputs={"out.txt": b"123"},
        gnucobol_result=gnu_res,
    )
    assert report.is_match is False
    assert report.status == "REFERENCE_EXECUTION_FAILURE"


def test_multi_oracle_return_code_mismatch():
    gnu_res = ReferenceExecutionResult(
        runtime_name="GnuCOBOL",
        status=RuntimeStatus.EXECUTED,
        exit_code=0,
        output_files={"out.txt": b"DATA"},
    )
    report = MultiOracleDifferentialVerifier.compare_multi_oracle(
        java_outputs={"out.txt": b"DATA"},
        gnucobol_result=gnu_res,
        java_return_code=4,
    )
    assert report.is_match is False
    assert "Return code mismatch" in report.mismatches[0]


def test_multi_oracle_record_count_mismatch():
    gnu_res = ReferenceExecutionResult(
        runtime_name="GnuCOBOL",
        status=RuntimeStatus.EXECUTED,
        output_files={"out.txt": b"REC1\nREC2\nREC3\n"},
    )
    report = MultiOracleDifferentialVerifier.compare_multi_oracle(
        java_outputs={"out.txt": b"REC1\nREC2\n"},
        gnucobol_result=gnu_res,
    )
    assert report.is_match is False
    assert any("line count mismatch" in m for m in report.mismatches)


def test_multi_oracle_ordering_mismatch():
    gnu_res = ReferenceExecutionResult(
        runtime_name="GnuCOBOL",
        status=RuntimeStatus.EXECUTED,
        output_files={"out.txt": b"REC_A\nREC_B\n"},
    )
    report = MultiOracleDifferentialVerifier.compare_multi_oracle(
        java_outputs={"out.txt": b"REC_B\nREC_A\n"},
        gnucobol_result=gnu_res,
    )
    assert report.is_match is False
    assert any("ordering mismatch" in m for m in report.mismatches)

