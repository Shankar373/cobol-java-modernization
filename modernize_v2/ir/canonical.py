"""Canonical IR — Phase 2A placeholder.

The full typed IR is implemented in Phase 2B (T-2B-04..09). This
module exists to provide the package surface and to host the
``CanonicalIR`` root type when it is introduced.

The placeholder documents the invariants Phase 2B will uphold:

    * Every node has a stable, deterministic
      ``DeterministicId`` (modernize_v2.ir.ids).
    * Every node has a single ``IRKind`` (modernize_v2.ir.kinds).
    * Every node has a source ``SourceSpan``
      (modernize_v2.ir.diagnostic) for diagnostics.
    * Every node has a frozen attribute bag keyed by
      ``AttrKey`` (Phase 2B); no ``Dict[str, Any]`` is permitted
      in the public surface.
    * The whole ``CanonicalIR`` is hash-stable via canonical JSON.

This module is intentionally minimal. Do not extend it with the
full IR until Phase 2B.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from .diagnostic import SourceSpan
from .ids import DeterministicId
from .kinds import IRKind


@dataclass(frozen=True)
class IRNodeBase:
    """Frozen attribute base for every IR node.

    The actual semantic fields are introduced in Phase 2B. The
    base here exists so that diagnostic and id types can talk
    about nodes without depending on the full IR data model.
    """

    id: DeterministicId
    kind: IRKind
    span: SourceSpan


# Reserved for Phase 2B. Importing the symbol keeps
# backwards-compatibility for code that wants to reference the
# canonical IR root.
CANONICAL_IR_PHASE: Final[str] = "2A-placeholder"


__all__ = [
    "IRNodeBase",
    "CANONICAL_IR_PHASE",
]
