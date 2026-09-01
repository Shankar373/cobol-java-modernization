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
