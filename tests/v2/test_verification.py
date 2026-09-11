"""Tests for modernize_v2.verification — observation, verdict, contract.

Acceptance criteria from T-2A-05 and T-2A-06:

    Observation:
        * complete observation tuple per architecture §24.1
        * no implicit truncation of stdout
        * content_hash is computed and stable

    Verdict:
        * PASS / FAILED / UNVERIFIED plus PARTIAL,
          ENVIRONMENT_BLOCKED, SKIPPED are first-class statuses
        * status computation is fail-closed
        * verdict is reproducible

    Contract:
        * required dimensions declared
        * comparison mode per dimension is explicit
        * seed data is declared, not auto-executed
        * missing required dimension fails the contract
"""

from __future__ import annotations

import json

import pytest

from modernize_v2.verification import (
    ArtifactExpectation,
    BatchStateObservation,
    CicsStateObservation,
    ComparisonMode,
    ComparisonResult,
    ComparisonStatus,
    ContractValidationError,
    DatabaseStateObservation,
    DimensionResult,
    DimensionStatus,
    Encoding,
    FileStatusObservation,
    NullIndicatorObservation,
    Observation,
    RequiredDimensions,
    SeedDeclaration,
    SqlOperationObservation,
    TransactionObservation,
    Verdict,
    VerificationContract,
    compute_overall_status,
    default_contract,
)


# ------------------------------------------------------------------
# Observation
# ------------------------------------------------------------------


def _basic_observation() -> Observation:
    return Observation(
        run_id="run-1",
        workload_id="W1",
        exit_code=0,
        stdout="hello\n",
        stderr="",
    )


def test_observation_minimal() -> None:
    obs = _basic_observation()
    assert obs.run_id == "run-1"
    assert obs.workload_id == "W1"
    assert obs.exit_code == 0
    assert obs.stdout == "hello\n"
    assert obs.stderr == ""
    assert len(obs.content_hash) == 64


def test_observation_does_not_truncate_stdout() -> None:
    long = "x" * 100_000
    obs = Observation(
        run_id="run-2",
        workload_id="W2",
        exit_code=0,
        stdout=long,
        stderr="",
    )
    assert len(obs.stdout) == 100_000
    # No field is named "tail_only" or similar.
    assert not hasattr(obs, "tail_only")


def test_observation_content_hash_is_stable() -> None:
    a = _basic_observation()
    b = _basic_observation()
    assert a.content_hash == b.content_hash
    # Mutation of the input yields a different hash.
    c = Observation(
        run_id="run-1",
        workload_id="W1",
        exit_code=0,
        stdout="different\n",
        stderr="",
    )
    assert a.content_hash != c.content_hash


def test_observation_full_tuple_dimensions() -> None:
    obs = Observation(
        run_id="r",
        workload_id="w",
        exit_code=0,
        stdout="",
        stderr="",
        output_files=(),
        db_state=(
            DatabaseStateObservation(
                table="ACCOUNTS", row_count=3,
            ),
        ),
        sqlcode_seq=(
            SqlOperationObservation(
                operation_index=0, sqlcode=0, sqlstate="00000",
            ),
        ),
        sqlstate_seq=(
            SqlOperationObservation(
                operation_index=0, sqlcode=0, sqlstate="00000",
            ),
        ),
        null_indicator_seq=(
            NullIndicatorObservation(
                call_site=0, host_var="HV1", indicator=0,
            ),
        ),
        transaction_state=(
            TransactionObservation(boundary_index=0, committed=True),
        ),
        file_status_seq=(
            FileStatusObservation(
                operation_index=0, path="CUSTFILE", status="00",
            ),
        ),
        cics_state=(
            CicsStateObservation(
                boundary_index=0,
                channel="CHAN1",
                commarea_summary_hash="0" * 64,
            ),
        ),
        batch_state=(
            BatchStateObservation(
                step_index=0, step_name="S1", exit_status="COMPLETED",
            ),
        ),
        encoding=Encoding(source_codepage="UTF-8", java_charset="UTF-8"),
    )
    data = obs.to_dict()
    # Every required dimension field is present and populated
    # in the dict that feeds the canonical JSON.
    for key in (
        "run_id", "workload_id", "exit_code", "stdout", "stderr",
        "output_files", "db_state", "sqlcode_seq", "sqlstate_seq",
        "null_indicator_seq", "transaction_state", "file_status_seq",
        "cics_state", "batch_state", "observed_at", "encoding",
    ):
        assert key in data, key
    # ``content_hash`` is part of the canonical JSON but not the
    # dict the hash itself is computed over.
    parsed = json.loads(obs.to_canonical_json())
    assert "content_hash" in parsed
    assert parsed["content_hash"] == obs.content_hash


def test_observation_validates_run_id() -> None:
    with pytest.raises(ValueError):
        Observation(
            run_id="", workload_id="w", exit_code=0, stdout="", stderr=""
        )


def test_observation_validates_workload_id() -> None:
    with pytest.raises(ValueError):
        Observation(
            run_id="r", workload_id="", exit_code=0, stdout="", stderr=""
        )


def test_observation_validates_stdout_type() -> None:
    with pytest.raises(TypeError):
        Observation(
            run_id="r", workload_id="w",
            exit_code=0, stdout=b"bytes-not-allowed",  # type: ignore[arg-type]
            stderr="",
        )


def test_observation_canonical_json_is_deterministic() -> None:
    a = _basic_observation()
    b = _basic_observation()
    assert a.to_canonical_json() == b.to_canonical_json()


# ------------------------------------------------------------------
# Verdict / ComparisonResult
# ------------------------------------------------------------------


def test_comparison_status_properties() -> None:
    assert ComparisonStatus.PASS.is_success
    assert not ComparisonStatus.FAILED.is_success
    assert ComparisonStatus.FAILED.is_failure
    assert ComparisonStatus.UNVERIFIED.is_unverified
    assert not ComparisonStatus.PASS.is_unverified


def test_compute_overall_status_all_pass() -> None:
    dims = (
        DimensionResult(dimension="exit_code", status=DimensionStatus.PASS),
        DimensionResult(dimension="stdout", status=DimensionStatus.PASS),
    )
    assert compute_overall_status(dims) is ComparisonStatus.PASS


def test_compute_overall_status_failed_dominates() -> None:
    dims = (
        DimensionResult(dimension="exit_code", status=DimensionStatus.PASS),
        DimensionResult(dimension="stdout", status=DimensionStatus.FAILED),
    )
    assert compute_overall_status(dims) is ComparisonStatus.FAILED


def test_compute_overall_status_missing_is_unverified() -> None:
    dims = (
        DimensionResult(
            dimension="db_state", status=DimensionStatus.UNVERIFIED,
            detail="missing",
        ),
        DimensionResult(dimension="exit_code", status=DimensionStatus.PASS),
    )
    assert compute_overall_status(dims) is ComparisonStatus.UNVERIFIED


def test_compute_overall_status_skipped_is_unverified() -> None:
    dims = (
        DimensionResult(dimension="stdout", status=DimensionStatus.PASS),
        DimensionResult(
            dimension="cics_state", status=DimensionStatus.SKIPPED,
        ),
    )
    # A skipped required dimension cannot be a clean PASS.
    assert compute_overall_status(dims) is ComparisonStatus.UNVERIFIED


def test_comparison_result_to_dict() -> None:
    cr = ComparisonResult(
        status=ComparisonStatus.FAILED,
        dimension_results=(
            DimensionResult(
                dimension="stdout",
                status=DimensionStatus.FAILED,
                detail="line 1 differs",
                expected_hash="a" * 64,
                observed_hash_cobol="b" * 64,
                observed_hash_java="c" * 64,
            ),
        ),
        contract_id="C1",
        observed_hash_cobol="b" * 64,
        observed_hash_java="c" * 64,
    )
    data = cr.to_dict()
    assert data["status"] == "FAILED"
    assert data["dimension_results"][0]["dimension"] == "stdout"
    parsed = json.loads(cr.to_canonical_json())
    assert parsed["status"] == "FAILED"


def test_comparison_result_rejects_short_hash() -> None:
    with pytest.raises(ValueError):
        ComparisonResult(
            status=ComparisonStatus.PASS,
            observed_hash_cobol="tooshort",
        )


def test_verdict_content_hash_is_stable() -> None:
    cr = ComparisonResult(status=ComparisonStatus.PASS)
    v = Verdict(
        workload_id="W1",
        comparison=cr,
        capability_outcome="ALLOW",
        notes="ok",
    )
    h1 = v.content_hash()
    h2 = v.content_hash()
    assert h1 == h2
    assert len(h1) == 64


# ------------------------------------------------------------------
# VerificationContract
# ------------------------------------------------------------------


def test_default_contract() -> None:
    c = default_contract("W1")
    assert c.workload_id == "W1"
    assert "exit_code" in c.required.dimensions
    assert "stdout" in c.required.dimensions
    assert "db_state" in c.required.dimensions
    assert "sqlcode_seq" in c.required.dimensions
    assert "sqlstate_seq" in c.required.dimensions
    assert "null_indicator_seq" in c.required.dimensions
    assert "transaction_state" in c.required.dimensions
    assert "file_status_seq" in c.required.dimensions
    assert "cics_state" in c.required.dimensions
    assert "batch_state" in c.required.dimensions


def test_default_contract_modes_default_to_physical() -> None:
    c = default_contract("W1")
    # Default for most dimensions is PHYSICAL.
    assert c.required.mode_for("exit_code") is ComparisonMode.PHYSICAL
    assert c.required.mode_for("stdout") is ComparisonMode.PHYSICAL
    assert c.required.mode_for("sqlcode_seq") is ComparisonMode.PHYSICAL


def test_required_dimensions_rejects_unknown() -> None:
    with pytest.raises(ContractValidationError):
        RequiredDimensions(dimensions=("NOPE",))


def test_required_dimensions_rejects_bad_mode() -> None:
    with pytest.raises(ContractValidationError):
        RequiredDimensions(
            dimensions=("stdout",),
            modes={"stdout": "PHYSICAL"},  # type: ignore[arg-type]
        )


def test_seed_declaration_rejects_bad_kind() -> None:
    with pytest.raises(ContractValidationError):
        SeedDeclaration(
            name="seed-1",
            table="CUST",
            source_path="data/seed.sql",
            allowed_statement_kinds=("DROP",),
        )


def test_seed_declaration_rejects_empty() -> None:
    with pytest.raises(ValueError):
        SeedDeclaration(
            name="",
            table="CUST",
            source_path="data/seed.sql",
        )


def test_contract_requires_at_least_one_dimension() -> None:
    with pytest.raises(ContractValidationError):
        VerificationContract(
            contract_id="C1",
            workload_id="W1",
            required=RequiredDimensions(dimensions=()),
            encoding=Encoding(
                source_codepage="UTF-8", java_charset="UTF-8"
            ),
        )


def test_contract_rejects_unknown_artifact_kind() -> None:
    with pytest.raises(ContractValidationError):
        ArtifactExpectation(name="x", artifact_kind="weird")


def test_contract_to_canonical_json() -> None:
    c = default_contract("W1")
    j = c.to_canonical_json()
    parsed = json.loads(j)
    assert parsed["workload_id"] == "W1"
    assert parsed["required"]["dimensions"]
    h = c.content_hash()
    assert len(h) == 64


def test_contract_must_have_nonempty_ids() -> None:
    with pytest.raises(ValueError):
        VerificationContract(
            contract_id="",
            workload_id="W1",
            required=RequiredDimensions(dimensions=("exit_code",)),
            encoding=Encoding(
                source_codepage="UTF-8", java_charset="UTF-8"
            ),
        )


def test_default_modes_map_is_well_formed() -> None:
    """Every default mode is a known comparison mode."""
    c = default_contract("W1")
    for d in c.required.dimensions:
        m = c.required.mode_for(d)
        assert isinstance(m, ComparisonMode)


def test_comparison_modes_have_strictness() -> None:
    assert ComparisonMode.PHYSICAL.is_strict
    assert not ComparisonMode.KEY_SORTED.is_strict
    assert not ComparisonMode.SET.is_strict
