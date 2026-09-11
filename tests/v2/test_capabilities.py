"""Tests for modernize_v2.capabilities — registry and gate.

Acceptance criteria from T-2A-04:

    * capability states: SUPPORTED_AND_VERIFIED,
      SUPPORTED_UNVERIFIED, PARTIAL, SIMULATED, UNSUPPORTED
    * CapabilityRecord contains feature, state, workload,
      evidence, diagnostics
    * CapabilityGate fails closed
    * UNSUPPORTED → ERROR diagnostic, blocks migration
    * SIMULATED → EMULATED label, never VERIFIED
    * PARTIAL/SUPPORTED_UNVERIFIED → cannot become VERIFIED
    * SUPPORTED_AND_VERIFIED → may continue
"""

from __future__ import annotations

import pytest

from modernize_v2.capabilities import (
    Capability,
    CapabilityDecision,
    CapabilityGate,
    CapabilityRecord,
    CapabilityRegistry,
    CapabilityState,
    GateOutcome,
)
from modernize_v2.ir.diagnostic import (
    DiagnosticKind,
    DiagnosticSeverity,
)


def _cap(name: str) -> Capability:
    return Capability(name)


def _record(
    name: str,
    state: CapabilityState,
    *,
    workload_id: str | None = "W",
    notes: str = "",
) -> CapabilityRecord:
    return CapabilityRecord(
        capability=_cap(name),
        state=state,
        workload_id=workload_id,
        evidence=(f"test://{name}",),
        notes=notes,
    )


def test_state_properties() -> None:
    assert CapabilityState.SUPPORTED_AND_VERIFIED.is_verifiable
    assert not CapabilityState.SUPPORTED_UNVERIFIED.is_verifiable
    assert not CapabilityState.PARTIAL.is_verifiable
    assert not CapabilityState.SIMULATED.is_verifiable
    assert not CapabilityState.UNSUPPORTED.is_verifiable

    assert CapabilityState.UNSUPPORTED.is_blocking
    assert not CapabilityState.PARTIAL.is_blocking
    assert not CapabilityState.SIMULATED.is_blocking

    assert CapabilityState.SIMULATED.is_emulated
    assert not CapabilityState.PARTIAL.is_emulated


def test_capability_canonicalizes_to_uppercase() -> None:
    c = Capability("cics.link")
    assert c.name == "CICS.LINK"


def test_capability_must_be_nonempty() -> None:
    with pytest.raises(ValueError):
        Capability("")


def test_registry_records_per_capability() -> None:
    r = CapabilityRegistry()
    r.register(_record("PIC.X", CapabilityState.SUPPORTED_AND_VERIFIED))
    r.register(_record("SQL.SELECT_INTO", CapabilityState.PARTIAL))
    assert r.weakest_state("PIC.X") is CapabilityState.SUPPORTED_AND_VERIFIED
    assert r.weakest_state("SQL.SELECT_INTO") is CapabilityState.PARTIAL
    assert r.weakest_state("UNKNOWN") is None
    assert "pic.x" in r
    assert "unknown" not in r
    assert len(r) == 2


def test_registry_weakest_wins() -> None:
    r = CapabilityRegistry()
    r.register(_record("X", CapabilityState.SUPPORTED_AND_VERIFIED))
    r.register(_record("X", CapabilityState.PARTIAL))
    r.register(_record("X", CapabilityState.UNSUPPORTED))
    assert r.weakest_state("X") is CapabilityState.UNSUPPORTED
    assert r.has_blocking()
    assert len(r.blocking_records()) == 1


def test_gate_empty_registry_allows() -> None:
    gate = CapabilityGate()
    decision = gate.check(CapabilityRegistry(), workload_id="W")
    assert decision.outcome is GateOutcome.ALLOW
    assert decision.can_be_verified


def test_gate_supported_and_verified_allows_and_verifies() -> None:
    r = CapabilityRegistry()
    r.register(_record("PIC.X", CapabilityState.SUPPORTED_AND_VERIFIED))
    gate = CapabilityGate()
    decision = gate.check(r, workload_id="W")
    assert decision.outcome is GateOutcome.ALLOW
    assert decision.can_be_verified
    assert not decision.is_blocking


def test_gate_unsupported_blocks() -> None:
    r = CapabilityRegistry()
    r.register(_record("REPORT_WRITER", CapabilityState.UNSUPPORTED))
    gate = CapabilityGate()
    decision = gate.check(r, workload_id="W")
    assert decision.outcome is GateOutcome.BLOCK
    assert decision.is_blocking
    assert not decision.can_be_verified
    assert len(decision.diagnostics) == 1
    diag = decision.diagnostics[0]
    assert diag.severity is DiagnosticSeverity.ERROR
    assert diag.kind is DiagnosticKind.UNSUPPORTED_FEATURE
    assert diag.workload_id == "W"


def test_gate_unsupported_cannot_be_warning() -> None:
    """No path through the gate downgrades UNSUPPORTED."""
    r = CapabilityRegistry()
    r.register(_record("REPORT_WRITER", CapabilityState.UNSUPPORTED))
    gate = CapabilityGate()
    decision = gate.check(r)
    for d in decision.diagnostics:
        assert d.severity is DiagnosticSeverity.ERROR
        assert d.kind is DiagnosticKind.UNSUPPORTED_FEATURE


def test_gate_simulated_yields_emulated_outcome() -> None:
    r = CapabilityRegistry()
    r.register(_record("CICS.LINK", CapabilityState.SIMULATED))
    gate = CapabilityGate()
    decision = gate.check(r)
    assert decision.outcome is GateOutcome.ALLOW_BUT_EMULATED
    assert not decision.can_be_verified


def test_gate_simulated_can_be_refused_by_policy() -> None:
    r = CapabilityRegistry()
    r.register(_record("CICS.LINK", CapabilityState.SIMULATED))
    gate = CapabilityGate(allow_simulated=False)
    decision = gate.check(r)
    assert decision.outcome is GateOutcome.BLOCK
    assert decision.diagnostics
    for d in decision.diagnostics:
        assert d.kind is DiagnosticKind.CAPABILITY_MISMATCH
        assert d.severity is DiagnosticSeverity.ERROR


def test_gate_partial_yields_not_verified() -> None:
    r = CapabilityRegistry()
    r.register(_record("REDEFINES.NESTED", CapabilityState.PARTIAL))
    gate = CapabilityGate()
    decision = gate.check(r)
    assert decision.outcome is GateOutcome.ALLOW_BUT_NOT_VERIFIED
    assert not decision.can_be_verified


def test_gate_partial_can_be_refused_by_policy() -> None:
    r = CapabilityRegistry()
    r.register(_record("REDEFINES.NESTED", CapabilityState.PARTIAL))
    gate = CapabilityGate(allow_partial=False)
    decision = gate.check(r)
    assert decision.outcome is GateOutcome.BLOCK


def test_gate_supported_unverified_yields_not_verified() -> None:
    r = CapabilityRegistry()
    r.register(_record("DB2.SQLCODE", CapabilityState.SUPPORTED_UNVERIFIED))
    gate = CapabilityGate()
    decision = gate.check(r)
    assert decision.outcome is GateOutcome.ALLOW_BUT_NOT_VERIFIED


def test_gate_weakest_wins() -> None:
    r = CapabilityRegistry()
    r.register(_record("A", CapabilityState.SUPPORTED_AND_VERIFIED))
    r.register(_record("B", CapabilityState.SIMULATED))
    r.register(_record("C", CapabilityState.UNSUPPORTED))
    gate = CapabilityGate()
    decision = gate.check(r)
    # UNSUPPORTED dominates.
    assert decision.outcome is GateOutcome.BLOCK


def test_gate_unsupported_not_present_does_not_block() -> None:
    """If no record is UNSUPPORTED, the workload may continue."""
    r = CapabilityRegistry()
    r.register(_record("A", CapabilityState.PARTIAL))
    r.register(_record("B", CapabilityState.SIMULATED))
    gate = CapabilityGate()
    decision = gate.check(r)
    # SIMULATED is weakest, but it's allow-but-emulated.
    assert decision.outcome is GateOutcome.ALLOW_BUT_EMULATED


def test_registry_snapshot_is_frozen_view() -> None:
    r = CapabilityRegistry()
    r.register(_record("A", CapabilityState.SUPPORTED_AND_VERIFIED))
    snap = r.snapshot()
    assert "A" in snap
    assert len(snap["A"]) == 1


def test_registry_merge_combines_records() -> None:
    a = CapabilityRegistry()
    b = CapabilityRegistry()
    a.register(_record("A", CapabilityState.SUPPORTED_AND_VERIFIED))
    b.register(_record("B", CapabilityState.PARTIAL))
    merged = a.merge(b)
    assert "A" in merged
    assert "B" in merged


def test_gate_rejects_non_registry() -> None:
    gate = CapabilityGate()
    with pytest.raises(TypeError):
        gate.check("not a registry")  # type: ignore[arg-type]


def test_evidence_and_diagnostics_default_to_empty() -> None:
    rec = CapabilityRecord(
        capability=_cap("X"),
        state=CapabilityState.SUPPORTED_AND_VERIFIED,
    )
    assert rec.evidence == ()
    assert rec.diagnostics == ()
