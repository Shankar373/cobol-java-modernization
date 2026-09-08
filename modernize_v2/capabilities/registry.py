"""Capability registry for the V2 platform.

A capability is a declarative statement that the platform either
supports a feature or does not, with an honest classification of
the support level. The registry is the single source of truth for
"what is verified vs. emulated vs. unsupported".

The architecture (§15-17, §20 of docs/PHASE_2_ARCHITECTURE_V2.md)
mandates the following capability states:

    SUPPORTED_AND_VERIFIED
        The feature is implemented and was end-to-end verified
        against an independent oracle on at least one workload.
        The verdict may become ``PASS``/``VERIFIED``.

    SUPPORTED_UNVERIFIED
        The feature is implemented but no end-to-end differential
        verification exists. The verdict cannot become
        ``VERIFIED``; it can become ``PARTIAL`` or
        ``ENVIRONMENT_BLOCKED``.

    PARTIAL
        The feature is partially implemented; some constructs
        work, some are not supported. The workload may continue
        only where the architecture permits, and the verdict
        cannot become ``VERIFIED``/``PASS`` for the unsupported
        portion.

    SIMULATED
        The feature is emulated by an in-process facility (e.g.
        the in-memory CICS runtime). The verdict is reported as
        ``EMULATED`` and cannot become ``VERIFIED``.

    UNSUPPORTED
        The feature is not implemented. A capability gate refuses
        to allow the workload to continue; an
        ``UNSUPPORTED_FEATURE`` ERROR diagnostic is produced.
        ``UNSUPPORTED`` is never downgraded to a warning or a
        comment.

A capability record is immutable. The registry is append-safe.
The gate consumes a registry and produces a per-workload decision
(``CapabilityGate`` in ``gate.py``).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Final, Iterable, Mapping


class CapabilityState(str, Enum):
    """Capability state.

    The state is the architecture's strict classification. The
    ordering in the enum is significant: a state is "weaker" than
    any state above it (see ``is_verifiable``).
    """

    SUPPORTED_AND_VERIFIED = "SUPPORTED_AND_VERIFIED"
    SUPPORTED_UNVERIFIED = "SUPPORTED_UNVERIFIED"
    PARTIAL = "PARTIAL"
    SIMULATED = "SIMULATED"
    UNSUPPORTED = "UNSUPPORTED"

    @property
    def is_verifiable(self) -> bool:
        """Whether the state allows the verdict to become VERIFIED/PASS.

        Only ``SUPPORTED_AND_VERIFIED`` allows the verdict to
        become a verified success. All other states keep the
        verdict below ``VERIFIED``/``PASS``.
        """
        return self is CapabilityState.SUPPORTED_AND_VERIFIED

    @property
    def is_blocking(self) -> bool:
        """Whether the state blocks the workload from continuing.

        ``UNSUPPORTED`` is blocking. ``PARTIAL`` and ``SIMULATED``
        are not blocking but they prevent the verdict from
        becoming verified.
        """
        return self is CapabilityState.UNSUPPORTED

    @property
    def is_emulated(self) -> bool:
        return self is CapabilityState.SIMULATED


# Ordered from strongest to weakest, used for reporting and tests.
STATE_ORDER: Final[tuple[CapabilityState, ...]] = (
    CapabilityState.SUPPORTED_AND_VERIFIED,
    CapabilityState.SUPPORTED_UNVERIFIED,
    CapabilityState.PARTIAL,
    CapabilityState.SIMULATED,
    CapabilityState.UNSUPPORTED,
)


# Names that V2 reserves for capability keys. Other keys are
# allowed but should follow the dotted convention.
CAPABILITY_KEY_PATTERN_HINT: Final[str] = "DOMAIN.FEATURE"


@dataclass(frozen=True)
class Capability:
    """A named capability.

    The name is the dotted identifier of the feature (e.g.
    ``"PIC.DISPLAY_NUMERIC"`` or ``"SQL.SELECT_INTO"``). Names
    are case-insensitive on lookup but stored canonicalized as
    uppercase.
    """

    name: str

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("capability name must be a non-empty string")
        # Canonicalize to uppercase; this is the public form.
        object.__setattr__(self, "name", self.name.upper())


@dataclass(frozen=True)
class CapabilityRecord:
    """An immutable record describing a capability's state.

    A record ties a feature (``capability``) to its current
    state, the workload it has been verified for (if any), the
    evidence supporting the state, and the diagnostics
    accumulated for the feature.

    Records are produced when a feature is exercised; they are
    consumed by the report and the gate.
    """

    capability: Capability
    state: CapabilityState
    workload_id: str | None = None
    evidence: tuple[str, ...] = field(default_factory=tuple)
    diagnostics: tuple[str, ...] = field(default_factory=tuple)
    notes: str = ""

    def __post_init__(self) -> None:
        if self.evidence is None:  # type: ignore[unreachable]
            object.__setattr__(self, "evidence", ())
        if self.diagnostics is None:  # type: ignore[unreachable]
            object.__setattr__(self, "diagnostics", ())

    @property
    def is_verifiable(self) -> bool:
        return self.state.is_verifiable

    @property
    def is_blocking(self) -> bool:
        return self.state.is_blocking


class CapabilityRegistry:
    """Append-only registry of capability records.

    The registry is the single source of truth. The
    ``CapabilityGate`` consults the registry before letting a
    workload proceed.

    Records are keyed by capability name. If a capability is
    registered multiple times for the same workload, the
    *weakest* state wins (``min`` over ``STATE_ORDER``). This is
    fail-closed: if one part of the system reports
    ``UNSUPPORTED``, the registry records ``UNSUPPORTED`` and
    the gate blocks the workload.
    """

    def __init__(self) -> None:
        self._records: dict[str, list[CapabilityRecord]] = {}

    @staticmethod
    def _key(name: str) -> str:
        if not isinstance(name, str) or not name:
            raise ValueError("capability name must be a non-empty string")
        return name.upper()

    def register(self, record: CapabilityRecord) -> None:
        """Append a record to the registry."""
        if not isinstance(record, CapabilityRecord):
            raise TypeError("register() expects a CapabilityRecord")
        key = self._key(record.capability.name)
        self._records.setdefault(key, []).append(record)

    def records_for(self, name: str) -> tuple[CapabilityRecord, ...]:
        return tuple(self._records.get(self._key(name), ()))

    def weakest_state(self, name: str) -> CapabilityState | None:
        """Return the weakest state for the capability.

        Returns ``None`` if the capability has no records.
        """
        records = self._records.get(self._key(name))
        if not records:
            return None
        weakest = records[0].state
        for r in records[1:]:
            if STATE_ORDER.index(r.state) > STATE_ORDER.index(weakest):
                weakest = r.state
        return weakest

    def has_blocking(self) -> bool:
        for records in self._records.values():
            for r in records:
                if r.is_blocking:
                    return True
        return False

    def blocking_records(self) -> tuple[CapabilityRecord, ...]:
        out: list[CapabilityRecord] = []
        for records in self._records.values():
            for r in records:
                if r.is_blocking:
                    out.append(r)
        return tuple(out)

    def all_records(self) -> tuple[CapabilityRecord, ...]:
        out: list[CapabilityRecord] = []
        for records in self._records.values():
            out.extend(records)
        return tuple(out)

    def snapshot(self) -> Mapping[str, tuple[CapabilityRecord, ...]]:
        """Return a frozen view of the registry contents."""
        return {k: tuple(v) for k, v in self._records.items()}

    def merge(self, other: "CapabilityRegistry") -> "CapabilityRegistry":
        """Return a new registry with both sets of records."""
        out = CapabilityRegistry()
        for r in self.all_records():
            out.register(r)
        for r in other.all_records():
            out.register(r)
        return out

    def __len__(self) -> int:
        return sum(len(v) for v in self._records.values())

    def __contains__(self, name: object) -> bool:
        if not isinstance(name, str):
            return False
        return self._key(name) in self._records


def iter_capabilities(
    registry: CapabilityRegistry,
) -> Iterable[CapabilityRecord]:
    """Iterate over all records in insertion order."""
    for records in registry.snapshot().values():
        yield from records


__all__ = [
    "CapabilityState",
    "STATE_ORDER",
    "Capability",
    "CapabilityRecord",
    "CapabilityRegistry",
    "iter_capabilities",
    "CAPABILITY_KEY_PATTERN_HINT",
]
