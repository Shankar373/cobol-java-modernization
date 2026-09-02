"""Negative Tests for Reference Runtimes & Fail-Closed Certification Policy."""

import pytest
from tools.reference_runtimes.base import ReferenceExecutionResult, RuntimeStatus
from tools.reference_runtimes.certification_policy import (
    CertificationPolicy,
    WorkloadCertificationStatus,
)
from tools.reference_runtimes.differential_verifier import MultiOracleDifferentialVerifier
from tools.reference_runtimes.database import DatabaseReferenceRuntime, DatabaseValidationMode


def test_negative_java_missing_expected_file():
    gnu_res = ReferenceExecutionResult(
        runtime_name="GnuCOBOL",
        status=RuntimeStatus.EXECUTED,
        output_files={"data/out/missing.txt": b"DATA\n"},
    )
    gnu_res.calculate_hashes()

    java_outputs = {}  # Empty

    report = MultiOracleDifferentialVerifier.compare_multi_oracle(
        java_outputs=java_outputs,
        gnucobol_result=gnu_res,
    )
    assert report.is_match is False
    assert report.status == "MISMATCH"
    assert any("missing" in m for m in report.mismatches)


def test_negative_java_content_mismatch():
    gnu_res = ReferenceExecutionResult(
        runtime_name="GnuCOBOL",
        status=RuntimeStatus.EXECUTED,
        output_files={"data/out/out.txt": b"EXPECTED\n"},
    )
    gnu_res.calculate_hashes()

    java_outputs = {"data/out/out.txt": b"ACTUAL_MUTATED\n"}

    report = MultiOracleDifferentialVerifier.compare_multi_oracle(
        java_outputs=java_outputs,
        gnucobol_result=gnu_res,
    )
    assert report.is_match is False
    assert report.status == "MISMATCH"


def test_certification_policy_cics_simulation_enforcement():
    """Workload requiring CICS without physical CICS TS must classify CICS as SIMULATED."""
    manifest = {
        "requires": {"batch": True, "sql": False, "vsam": False, "cics": True, "ebcdic": False}
    }
    result = CertificationPolicy.evaluate(
        workload_manifest=manifest,
        gate1_passed=True,
        gate2_passed=True,
        real_ibm_cics_tested=False,
    )
    assert result.verdict == WorkloadCertificationStatus.VERIFIED_FOR_DEFINED_SCOPE
    assert result.subsystem_evaluations.get("cics") == "SIMULATED"
    assert result.is_universal_mainframe_replacement is False


def test_certification_policy_vsam_simulation_enforcement():
    """Workload requiring VSAM without physical hardware must classify VSAM as SIMULATED."""
    manifest = {
        "requires": {"batch": True, "sql": False, "vsam": True, "cics": False, "ebcdic": False}
    }
    result = CertificationPolicy.evaluate(
        workload_manifest=manifest,
        gate1_passed=True,
        gate2_passed=True,
        physical_vsam_tested=False,
    )
    assert result.verdict == WorkloadCertificationStatus.VERIFIED_FOR_DEFINED_SCOPE
    assert result.subsystem_evaluations.get("vsam") == "SIMULATED"
    assert result.is_universal_mainframe_replacement is False


def test_certification_policy_ebcdic_unsupported_enforcement():
    """Workload requiring EBCDIC separates charset/collation from unproven native mainframe semantics."""
    manifest = {
        "requires": {"batch": True, "sql": False, "vsam": False, "cics": False, "ebcdic": True}
    }
    result = CertificationPolicy.evaluate(
        workload_manifest=manifest,
        gate1_passed=True,
        gate2_passed=True,
        ebcdic_differential_passed=False,
    )
    assert result.subsystem_evaluations.get("ebcdic_charset") == "PROVEN_FOR_TESTED_SCOPE"
    assert result.subsystem_evaluations.get("ebcdic_collation") == "PROVEN_FOR_TESTED_SCOPE"
    assert result.subsystem_evaluations.get("native_mainframe_ebcdic_semantics") == "UNPROVEN"
    assert result.subsystem_evaluations.get("ebcdic") == "PARTIALLY_PROVEN"


def test_certification_policy_gate_failure_fails_closed():
    """If Gate 1 or Gate 2 fails, verdict must be NOT_READY."""
    manifest = {"requires": {"batch": True}}
    result = CertificationPolicy.evaluate(
        workload_manifest=manifest,
        gate1_passed=False,
        gate2_passed=True,
    )
    assert result.verdict == WorkloadCertificationStatus.NOT_READY


def test_database_mode_classification():
    local_db = DatabaseReferenceRuntime(DatabaseValidationMode.LOCAL_RELATIONAL)
    assert local_db.certification_classification == "PROVEN_FOR_TESTED_SCOPE"

    real_db2 = DatabaseReferenceRuntime(DatabaseValidationMode.REAL_DB2_ZOS)
    assert real_db2.certification_classification == "UNPROVEN"
