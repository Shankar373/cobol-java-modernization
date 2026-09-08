"""modernize_v2.ir — Canonical IR package.

Phase 2A: ids, kinds, diagnostics, and module placeholders.
"""

from __future__ import annotations

from .ids import (
    DeterministicId,
    IdContext,
    id_for_node,
    IRID_NAMESPACE,
    KIND_NAMESPACE,
)
from .kinds import IRKind
from .diagnostic import (
    Diagnostic,
    DiagnosticSeverity,
    DiagnosticKind,
    SourceSpan,
    SourcePosition,
)

__all__ = [
    "DeterministicId",
    "IdContext",
    "id_for_node",
    "IRID_NAMESPACE",
    "KIND_NAMESPACE",
    "IRKind",
    "Diagnostic",
    "DiagnosticSeverity",
    "DiagnosticKind",
    "SourceSpan",
    "SourcePosition",
]
