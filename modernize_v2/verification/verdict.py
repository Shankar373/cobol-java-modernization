"""V2 Verdict and ComparisonResult.

The verdict is the result of a differential comparison. It is
fail-closed: a missing required dimension produces ``UNVERIFIED``,
not ``PASS``. An observation mismatch produces ``FAILED``.

Per the architecture (§24.4 of
docs/PHASE_2_ARCHITECTURE_V2.md), the verdict is one of:

    PASS         — the comparison succeeded on every required
                   dimension.
    FAILED       — the comparison found a mismatch on a required
                   dimension.
    UNVERIFIED   — a required dimension is missing from the
                   observation, or the comparator cannot complete.
    PARTIAL      — some dimensions matched; others were skipped
                   by explicit user opt-in (out of scope for the
                   default comparator).
    ENVIRONMENT_BLOCKED
                — the comparison could not run because of a
                   missing environment (e.g. real DB2).
    SKIPPED      — the comparison was explicitly skipped by a
                   user opt-in with documented reason.

The verdict is immutable. Each dimension result is recorded
separately so the report can show *which* dimension failed.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Final


class ComparisonStatus(str, Enum):
    """The high-level verdict of a comparison.

    The ordering in the enum is significant: ``PASS`` is the
    strongest outcome; ``UNVERIFIED``, ``PARTIAL``,
    ``ENVIRONMENT_BLOCKED``, and ``SKIPPED`` are weaker than
    ``FAILED`` in the sense that they do not declare a mismatch.
    """

    PASS = "PASS"
    FAILED = "FAILED"
    UNVERIFIED = "UNVERIFIED"
    PARTIAL = "PARTIAL"
    ENVIRONMENT_BLOCKED = "ENVIRONMENT_BLOCKED"
    SKIPPED = "SKIPPED"

    @property
    def is_success(self) -> bool:
        return self is ComparisonStatus.PASS

    @property
    def is_failure(self) -> bool:
        return self is ComparisonStatus.FAILED

    @property
    def is_unverified(self) -> bool:
        return self is ComparisonStatus.UNVERIFIED


class DimensionStatus(str, Enum):
    """The status of a single dimension within a comparison."""

    PASS = "PASS"
    FAILED = "FAILED"
    UNVERIFIED = "UNVERIFIED"
    SKIPPED = "SKIPPED"


@dataclass(frozen=True)
class DimensionResult:
    """The result of comparing one observation dimension."""

    dimension: str
    status: DimensionStatus
    detail: str = ""
    expected_hash: str = ""
    observed_hash_cobol: str = ""
    observed_hash_java: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.dimension, str) or not self.dimension:
            raise ValueError("dimension must be a non-empty string")
        for f in (
            self.expected_hash,
            self.observed_hash_cobol,
            self.observed_hash_java,
        ):
            if f and (
                len(f) != 64
                or not all(
                    c in "0123456789abcdef" for c in f.lower()
                )
            ):
                raise ValueError("hash fields must be 64 hex chars when set")

    def to_dict(self) -> dict[str, Any]:
        return {
            "dimension": self.dimension,
            "status": self.status.value,
            "detail": self.detail,
            "expected_hash": self.expected_hash,
            "observed_hash_cobol": self.observed_hash_cobol,
            "observed_hash_java": self.observed_hash_java,
        }


@dataclass(frozen=True)
class ComparisonResult:
    """The result of comparing two observations.

    The result is the per-dimension set of outcomes plus the
    overall status. The status is computed from the dimension
    results using the rules in
    ``compute_overall_status``.
    """

    status: ComparisonStatus
    dimension_results: tuple[DimensionResult, ...] = field(
        default_factory=tuple
    )
    contract_id: str = ""
    observed_hash_cobol: str = ""
    observed_hash_java: str = ""
    verifier_version: str = "2.0.0-alpha.0"
    detail: str = ""

    def __post_init__(self) -> None:
        for f in (
            self.observed_hash_cobol,
            self.observed_hash_java,
        ):
            if f and (
                len(f) != 64
                or not all(
                    c in "0123456789abcdef" for c in f.lower()
                )
            ):
                raise ValueError("observed hashes must be 64 hex chars")

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "dimension_results": [d.to_dict() for d in self.dimension_results],
            "contract_id": self.contract_id,
            "observed_hash_cobol": self.observed_hash_cobol,
            "observed_hash_java": self.observed_hash_java,
            "verifier_version": self.verifier_version,
            "detail": self.detail,
        }

    def to_canonical_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )

    @property
    def is_pass(self) -> bool:
        return self.status is ComparisonStatus.PASS

    @property
    def is_failed(self) -> bool:
        return self.status is ComparisonStatus.FAILED

    @property
    def is_unverified(self) -> bool:
        return self.status is ComparisonStatus.UNVERIFIED

    def failing_dimensions(self) -> tuple[DimensionResult, ...]:
        return tuple(
            d for d in self.dimension_results
            if d.status is DimensionStatus.FAILED
        )

    def unverified_dimensions(self) -> tuple[DimensionResult, ...]:
        return tuple(
            d for d in self.dimension_results
            if d.status is DimensionStatus.UNVERIFIED
        )


def compute_overall_status(
    dimension_results: tuple[DimensionResult, ...],
    *,
    on_missing: ComparisonStatus = ComparisonStatus.UNVERIFIED,
) -> ComparisonStatus:
    """Compute the overall status from the per-dimension results.

    Rules (fail-closed):

        1. If any dimension is FAILED, the overall is FAILED.
        2. If any required dimension is missing or UNVERIFIED,
           the overall is UNVERIFIED (the default ``on_missing``).
        3. If all dimensions are PASS, the overall is PASS.
        4. If a required dimension is SKIPPED, the overall is
           UNVERIFIED (SKIPPED is not a clean PASS).
    """
    has_pass = False
    for d in dimension_results:
        if d.status is DimensionStatus.FAILED:
            return ComparisonStatus.FAILED
        if d.status is DimensionStatus.UNVERIFIED:
            return on_missing
        if d.status is DimensionStatus.SKIPPED:
            return on_missing
        if d.status is DimensionStatus.PASS:
            has_pass = True
    if has_pass:
        return ComparisonStatus.PASS
    return on_missing


@dataclass(frozen=True)
class Verdict:
    """The platform's verdict for a single workload.

    The verdict is the final answer for a workload. It is a
    tuple of the ``ComparisonResult`` and the capability decision
    that produced the verdict. The verdict cannot be
    ``PASS``/``VERIFIED`` if the capability decision was not
    ``ALLOW``.
    """

    workload_id: str
    comparison: ComparisonResult
    capability_outcome: str  # GateOutcome.value
    capability_considered: tuple[str, ...] = field(default_factory=tuple)
    capability_blocking: tuple[str, ...] = field(default_factory=tuple)
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "workload_id": self.workload_id,
            "comparison": self.comparison.to_dict(),
            "capability_outcome": self.capability_outcome,
            "capability_considered": list(self.capability_considered),
            "capability_blocking": list(self.capability_blocking),
            "notes": self.notes,
        }

    def to_canonical_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )

    def content_hash(self) -> str:
        return hashlib.sha256(
            self.to_canonical_json().encode("utf-8")
        ).hexdigest()


# Statuses reserved for future expansion. The list is the
# closed set per AGENTS.md §9. Adding a status is a non-breaking
# change; renaming is a breaking change.
RESERVED_STATUSES: Final[tuple[ComparisonStatus, ...]] = (
    ComparisonStatus.PASS,
    ComparisonStatus.FAILED,
    ComparisonStatus.UNVERIFIED,
    ComparisonStatus.PARTIAL,
    ComparisonStatus.ENVIRONMENT_BLOCKED,
    ComparisonStatus.SKIPPED,
)


__all__ = [
    "ComparisonStatus",
    "DimensionStatus",
    "DimensionResult",
    "ComparisonResult",
    "Verdict",
    "compute_overall_status",
    "RESERVED_STATUSES",
]
