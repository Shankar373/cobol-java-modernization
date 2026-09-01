"""Negative Verification Gates Test Suite.

Ensures that intentional discrepancies, missing artifacts, tampered logs,
stale baselines, compilation errors, and unsupported mainframe constructs
are caught with 0% false PASS results.
"""
from pathlib import Path
import pytest

from modernize.native_pipeline import NativePipeline
from audit.evidence import Verdict, EvidenceBundle, TierEvidence, collect_evidence
from audit.certify import evaluate_certification


def make_pipeline(tmp_path: Path) -> NativePipeline:
    repo = tmp_path / "repo"
    out = tmp_path / "out"
    repo.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    return NativePipeline(str(repo), str(out))


# ---------------------------------------------------------------------------
# 1. Missing baseline
# ---------------------------------------------------------------------------
def test_gate_01_missing_baseline(tmp_path):
    p = make_pipeline(tmp_path)
    native = Path(p.out) / "results" / "native"
    native.mkdir(parents=True, exist_ok=True)
    (native / "stdout.txt").write_text("RESULT\n", encoding="utf-8")
    
    # Baseline directory does not exist
    verdict = p.stage_equivalence_gate("test_src")
    assert verdict in ["UNVERIFIED", "FAIL"]


# ---------------------------------------------------------------------------
# 2. Stale baseline (not generated in current run)
# ---------------------------------------------------------------------------
def test_gate_02_stale_baseline(tmp_path):
    p = make_pipeline(tmp_path)
    baseline = Path(p.out) / "baseline" / "legacy"
    native = Path(p.out) / "results" / "native"
    baseline.mkdir(parents=True, exist_ok=True)
    native.mkdir(parents=True, exist_ok=True)
    (baseline / "stdout.txt").write_text("MATCH\n", encoding="utf-8")
    (native / "stdout.txt").write_text("MATCH\n", encoding="utf-8")

    # p.baseline_verified is False
    assert p.stage_equivalence_gate("test_src") == "UNVERIFIED"


# ---------------------------------------------------------------------------
# 3. Modified stdout
# ---------------------------------------------------------------------------
def test_gate_03_modified_stdout(tmp_path):
    p = make_pipeline(tmp_path)
    p.baseline_verified = True
    baseline = Path(p.out) / "baseline" / "legacy"
    native = Path(p.out) / "results" / "native"
    baseline.mkdir(parents=True, exist_ok=True)
    native.mkdir(parents=True, exist_ok=True)
    (baseline / "stdout.txt").write_text("TOTAL: 500.00\n", encoding="utf-8")
    (native / "stdout.txt").write_text("TOTAL: 500.01\n", encoding="utf-8")

    assert p.stage_equivalence_gate("test_src") == "FAIL"


# ---------------------------------------------------------------------------
# 4. Changed exit code
# ---------------------------------------------------------------------------
def test_gate_04_changed_exit_code(tmp_path):
    bundle = EvidenceBundle(workload="TEST_EXIT_CODE")
    bundle.add_tier(TierEvidence(
        tier=4,
        name="Runtime Differential Equivalence",
        verdict=Verdict.FAIL,
        errors=["Exit code mismatch: baseline=0, java=1"],
    ))
    scorecard = evaluate_certification(bundle)
    assert scorecard["certification_verdict"] == "FAIL"
    assert "Exit code mismatch: baseline=0, java=1" in scorecard["blockers"]


# ---------------------------------------------------------------------------
# 5. Missing output file
# ---------------------------------------------------------------------------
def test_gate_05_missing_output_file(tmp_path):
    p = make_pipeline(tmp_path)
    p.baseline_verified = True
    baseline = Path(p.out) / "baseline" / "legacy"
    native = Path(p.out) / "results" / "native"
    baseline.mkdir(parents=True, exist_ok=True)
    native.mkdir(parents=True, exist_ok=True)
    (baseline / "stdout.txt").write_text("OK\n", encoding="utf-8")
    (native / "stdout.txt").write_text("OK\n", encoding="utf-8")
    (baseline / "report.dat").write_text("RECORDS\n", encoding="utf-8")
    # native missing report.dat

    assert p.stage_equivalence_gate("test_src") == "FAIL"


# ---------------------------------------------------------------------------
# 6. Extra output file
# ---------------------------------------------------------------------------
def test_gate_06_extra_output_file(tmp_path):
    p = make_pipeline(tmp_path)
    p.baseline_verified = True
    baseline = Path(p.out) / "baseline" / "legacy"
    native = Path(p.out) / "results" / "native"
    baseline.mkdir(parents=True, exist_ok=True)
    native.mkdir(parents=True, exist_ok=True)
    (baseline / "stdout.txt").write_text("OK\n", encoding="utf-8")
    (native / "stdout.txt").write_text("OK\n", encoding="utf-8")
    (native / "unexpected.dat").write_text("EXTRA\n", encoding="utf-8")

    assert p.stage_equivalence_gate("test_src") == "FAIL"


# ---------------------------------------------------------------------------
# 7. Changed output file contents
# ---------------------------------------------------------------------------
def test_gate_07_changed_output_file(tmp_path):
    p = make_pipeline(tmp_path)
    p.baseline_verified = True
    baseline = Path(p.out) / "baseline" / "legacy"
    native = Path(p.out) / "results" / "native"
    baseline.mkdir(parents=True, exist_ok=True)
    native.mkdir(parents=True, exist_ok=True)
    (baseline / "stdout.txt").write_text("OK\n", encoding="utf-8")
    (native / "stdout.txt").write_text("OK\n", encoding="utf-8")
    (baseline / "data.out").write_text("ACCOUNT_BALANCE=1000\n", encoding="utf-8")
    (native / "data.out").write_text("ACCOUNT_BALANCE=1001\n", encoding="utf-8")

    assert p.stage_equivalence_gate("test_src") == "FAIL"


# ---------------------------------------------------------------------------
# 8. Compilation failure
# ---------------------------------------------------------------------------
def test_gate_08_compilation_failure(tmp_path):
    bundle = collect_evidence(
        workload="TEST_COMPILATION_FAIL",
        pipeline_out=tmp_path,
        compilation_result={"success": False, "error": "cannot find symbol: class UnknownType"},
    )
    scorecard = evaluate_certification(bundle)
    assert scorecard["certification_verdict"] == "FAIL"
    assert scorecard["tier_breakdown"]["tier_2"]["verdict"] == "FAIL"


# ---------------------------------------------------------------------------
# 9. Java runtime failure
# ---------------------------------------------------------------------------
def test_gate_09_java_runtime_failure(tmp_path):
    bundle = collect_evidence(
        workload="TEST_JAVA_RUNTIME_FAIL",
        pipeline_out=tmp_path,
        differential_result={"status": "FAIL", "errors": ["java.lang.NullPointerException"]},
    )
    scorecard = evaluate_certification(bundle)
    assert scorecard["certification_verdict"] == "FAIL"
    assert scorecard["tier_breakdown"]["tier_4"]["verdict"] == "FAIL"


# ---------------------------------------------------------------------------
# 10. Different initial state
# ---------------------------------------------------------------------------
def test_gate_10_different_initial_state(tmp_path):
    bundle = collect_evidence(
        workload="TEST_INITIAL_STATE_DIFF",
        pipeline_out=tmp_path,
        differential_result={"status": "FAIL", "errors": ["Initial database row count mismatch: expected 10, got 8"]},
    )
    scorecard = evaluate_certification(bundle)
    assert scorecard["certification_verdict"] == "FAIL"


# ---------------------------------------------------------------------------
# 11. Mock SQL cannot yield PASS for real DB requirement
# ---------------------------------------------------------------------------
def test_gate_11_mock_sql_cannot_pass(tmp_path):
    bundle = collect_evidence(
        workload="DB2SELECT01",
        pipeline_out=tmp_path,
        differential_result={
            "status": "WARNING",
            "warnings": ["Execution performed against MockSqlService; real PostgreSQL unverified"],
        },
    )
    scorecard = evaluate_certification(bundle)
    assert scorecard["certification_verdict"] in ["WARNING", "UNPROVEN"]
    assert scorecard["certification_verdict"] != "PASS"


# ---------------------------------------------------------------------------
# 12. Unsupported construct (IMS / MQ) fails closed
# ---------------------------------------------------------------------------
def test_gate_12_unsupported_construct_fails_closed(tmp_path):
    bundle = EvidenceBundle(
        workload="TEST_IMS_UNSUPPORTED",
        unsupported_constructs=[{"type": "IMS_DLI", "line": 42, "statement": "ENTRY 'DLITCBL'"}],
    )
    bundle.add_tier(TierEvidence(
        tier=1,
        name="Syntax & AST Parsing",
        verdict=Verdict.BLOCKED,
        errors=["Unsupported construct IMS_DLI on line 42"],
    ))
    scorecard = evaluate_certification(bundle)
    assert scorecard["certification_verdict"] in ["FAIL", "BLOCKED"]
    assert len(scorecard["unsupported_constructs"]) == 1
