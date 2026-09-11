"""modernize_v2.capabilities — capability registry and gate.

Phase 2A: capability states, registry, and gate.

A capability is a *named* property of the platform. It says
"this feature is at this implementation/verification level for
this workload". The capability gate refuses to silently degrade
an ``UNSUPPORTED`` feature into a comment, a warning, or a
"VERIFIED" verdict.

The capability model is the single source of truth that the
report and the CI use. It replaces the V1 ``CapabilityStatus``
and ``EvidenceLevel`` enums, which the V2 architecture
deliberately re-derives from a stricter vocabulary.
"""

from __future__ import annotations

from .registry import (
    Capability,
    CapabilityState,
    CapabilityRecord,
    CapabilityRegistry,
)
from .gate import (
    CapabilityDecision,
    CapabilityGate,
    GateOutcome,
)

__all__ = [
    "Capability",
    "CapabilityState",
    "CapabilityRecord",
    "CapabilityRegistry",
    "CapabilityDecision",
    "CapabilityGate",
    "GateOutcome",
]
