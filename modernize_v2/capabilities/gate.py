"""Capability gate.

The gate consumes a ``CapabilityRegistry`` and produces a
``CapabilityDecision`` for a workload. The decision is
fail-closed: an ``UNSUPPORTED`` capability blocks the workload
from continuing, and the gate produces an
``UNSUPPORTED_FEATURE`` ``ERROR`` diagnostic that the
verification machinery will surface as ``FAILED``/``UNVERIFIED``.

Per the architecture (§20):

    * ``SUPPORTED_AND_VERIFIED`` may continue and the final
      verdict may be ``VERIFIED``/``PASS``.
    * ``SUPPORTED_UNVERIFIED`` may continue but the final
      verdict cannot become ``VERIFIED``/``PASS``.
    * ``PARTIAL`` may continue where the architecture permits
      (the caller decides which partial features are admitted);
      the final verdict cannot become ``VERIFIED``/``PASS``.
    * ``SIMULATED`` is allowed to continue but the workload is
      reported as ``EMULATED`` and never as ``VERIFIED``.
    * ``UNSUPPORTED`` blocks the workload; an
      ``UNSUPPORTED_FEATURE`` ``ERROR`` diagnostic is produced.

A capability decision is the per-workload, per-call summary of
the gate's reasoning. It is consumed by the report and the
verifier.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable

from modernize_v2.ir.diagnostic import (
    Diagnostic,
    DiagnosticKind,
    DiagnosticSeverity,
    SourceSpan,
)

from .registry import (
    CapabilityRecord,
    CapabilityRegistry,
    CapabilityState,
    STATE_ORDER,
)


class GateOutcome(str, Enum):
    """The gate's outcome for a single gate call."""

    ALLOW = "ALLOW"
    ALLOW_BUT_NOT_VERIFIED = "ALLOW_BUT_NOT_VERIFIED"
    ALLOW_BUT_EMULATED = "ALLOW_BUT_EMULATED"
    BLOCK = "BLOCK"

    @property
    def is_blocking(self) -> bool:
        return self is GateOutcome.BLOCK


@dataclass(frozen=True)
class CapabilityDecision:
    """A single decision produced by the gate.

    The decision records:

        * which capabilities were considered
        * the overall outcome
        * the diagnostics produced
        * whether the workload may still claim ``VERIFIED``
    """

    outcome: GateOutcome
    considered: tuple[CapabilityRecord, ...] = field(default_factory=tuple)
    blocking: tuple[CapabilityRecord, ...] = field(default_factory=tuple)
    diagnostics: tuple[Diagnostic, ...] = field(default_factory=tuple)

    @property
    def is_blocking(self) -> bool:
        return self.outcome.is_blocking

    @property
    def can_be_verified(self) -> bool:
        return self.outcome is GateOutcome.ALLOW


class CapabilityGate:
    """A fail-closed capability gate.

    The gate is constructed with the policy that decides which
    ``PARTIAL`` and ``SIMULATED`` features are admitted; the
    default policy is to admit them but to refuse the final
    ``VERIFIED``/``PASS`` verdict.
    """

    def __init__(
        self,
        *,
        allow_partial: bool = True,
        allow_simulated: bool = True,
    ) -> None:
        if not isinstance(allow_partial, bool):
            raise TypeError("allow_partial must be a bool")
        if not isinstance(allow_simulated, bool):
            raise TypeError("allow_simulated must be a bool")
        self._allow_partial = allow_partial
        self._allow_simulated = allow_simulated

    @property
    def allows_partial(self) -> bool:
        return self._allow_partial

    @property
    def allows_simulated(self) -> bool:
        return self._allow_simulated

    def check(
        self,
        registry: CapabilityRegistry,
        *,
        workload_id: str | None = None,
        span: SourceSpan | None = None,
    ) -> CapabilityDecision:
        """Evaluate the registry and produce a decision.

        The decision is fail-closed. If the registry has any
        ``UNSUPPORTED`` records, the decision is ``BLOCK`` and
        each such record produces an ``UNSUPPORTED_FEATURE``
        ``ERROR`` diagnostic.

        If the registry has only non-blocking records, the
        decision is one of the ``ALLOW_*`` outcomes depending
        on whether the weakest state is
        ``SUPPORTED_AND_VERIFIED`` (ALLOW), a partial/unverified
        state (ALLOW_BUT_NOT_VERIFIED), or simulated
        (ALLOW_BUT_EMULATED).
        """
        if not isinstance(registry, CapabilityRegistry):
            raise TypeError("check() expects a CapabilityRegistry")

        considered = list(registry.all_records())
        blocking_records = list(registry.blocking_records())

        if blocking_records:
            diagnostics = tuple(
                self._build_blocking_diagnostic(
                    r, workload_id=workload_id, span=span
                )
                for r in blocking_records
            )
            return CapabilityDecision(
                outcome=GateOutcome.BLOCK,
                considered=tuple(considered),
                blocking=tuple(blocking_records),
                diagnostics=diagnostics,
            )

        if not considered:
            return CapabilityDecision(outcome=GateOutcome.ALLOW)

        # Find the weakest state across all considered records.
        weakest_idx = min(
            STATE_ORDER.index(r.state) for r in considered
        )  # 0 is strongest; we want max index for weakest
        weakest_idx = max(
            STATE_ORDER.index(r.state) for r in considered
        )
        weakest = STATE_ORDER[weakest_idx]

        if weakest is CapabilityState.SUPPORTED_AND_VERIFIED:
            outcome = GateOutcome.ALLOW
        elif weakest is CapabilityState.SIMULATED:
            if not self._allow_simulated:
                # The gate has been configured to refuse
                # simulation outright. Produce a diagnostic
                # anyway to keep the decision auditable.
                diagnostics = tuple(
                    self._build_capability_mismatch_diagnostic(
                        r, workload_id=workload_id, span=span
                    )
                    for r in considered
                    if r.state is CapabilityState.SIMULATED
                )
                return CapabilityDecision(
                    outcome=GateOutcome.BLOCK,
                    considered=tuple(considered),
                    blocking=tuple(
                        r for r in considered
                        if r.state is CapabilityState.SIMULATED
                    ),
                    diagnostics=diagnostics,
                )
            outcome = GateOutcome.ALLOW_BUT_EMULATED
        elif weakest is CapabilityState.PARTIAL:
            if not self._allow_partial:
                diagnostics = tuple(
                    self._build_capability_mismatch_diagnostic(
                        r, workload_id=workload_id, span=span
                    )
                    for r in considered
                    if r.state is CapabilityState.PARTIAL
                )
                return CapabilityDecision(
                    outcome=GateOutcome.BLOCK,
                    considered=tuple(considered),
                    blocking=tuple(
                        r for r in considered
                        if r.state is CapabilityState.PARTIAL
                    ),
                    diagnostics=diagnostics,
                )
            outcome = GateOutcome.ALLOW_BUT_NOT_VERIFIED
        else:
            # SUPPORTED_UNVERIFIED is the only remaining state.
            outcome = GateOutcome.ALLOW_BUT_NOT_VERIFIED

        return CapabilityDecision(
            outcome=outcome,
            considered=tuple(considered),
            diagnostics=(),
        )

    @staticmethod
    def _build_blocking_diagnostic(
        record: CapabilityRecord,
        *,
        workload_id: str | None,
        span: SourceSpan | None,
    ) -> Diagnostic:
        return Diagnostic(
            severity=DiagnosticSeverity.ERROR,
            kind=DiagnosticKind.UNSUPPORTED_FEATURE,
            message=(
                f"Feature {record.capability.name!r} is UNSUPPORTED; "
                f"migration is blocked. Notes: {record.notes or 'none'}."
            ),
            span=span,
            workload_id=workload_id,
            related_ids=record.evidence,
        )

    @staticmethod
    def _build_capability_mismatch_diagnostic(
        record: CapabilityRecord,
        *,
        workload_id: str | None,
        span: SourceSpan | None,
    ) -> Diagnostic:
        return Diagnostic(
            severity=DiagnosticSeverity.ERROR,
            kind=DiagnosticKind.CAPABILITY_MISMATCH,
            message=(
                f"Feature {record.capability.name!r} is "
                f"{record.state.value}; gate policy refuses it. "
                f"Notes: {record.notes or 'none'}."
            ),
            span=span,
            workload_id=workload_id,
            related_ids=record.evidence,
        )


__all__ = [
    "GateOutcome",
    "CapabilityDecision",
    "CapabilityGate",
]
