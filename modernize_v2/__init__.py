"""modernize_v2 — Canonical COBOL → Native Java Modernization Platform (V2).

Phase 2A — Foundation Contracts.

This package implements the typed foundation for the V2 architecture
described in docs/PHASE_2_ARCHITECTURE_V2.md. It is structurally
independent of the V1 implementation in ``modernize/`` and does not
import V1 internals.

The public surface of V2 lives in these subpackages:

    modernize_v2.ir
        Canonical IR: ids, kinds, diagnostics, and the placeholder
        canonical IR types. The actual IR data model is fleshed out
        in Phase 2B.

    modernize_v2.capabilities
        Capability registry and gate. Every feature has an
        explicit capability record; unsupported features cannot
        silently degrade to a comment or a warning.

    modernize_v2.verification
        Observation model, verdict, and verification contract. The
        comparator itself is implemented in Phase 2J.

V2 is fail-closed. An ``UNSUPPORTED`` feature is a hard error; a
required observation dimension that is missing turns a verdict into
``UNVERIFIED``, never ``PASS``.

Stability note: until Phase 2L is complete, V2 is intended to be a
**foundation** for the architecture. No part of V2 is wired into
the V1 pipeline.
"""

from __future__ import annotations

__version__ = "2.0.0-alpha.0"
__phase__ = "2A"

__all__ = ["__version__", "__phase__"]
