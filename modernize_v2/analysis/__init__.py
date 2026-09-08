"""T-2C-0A Semantic Analysis Package.

This package provides the foundational semantic analysis layer
that consumes the T-2B-03 parser AST and produces deterministic
scope information.

The package is intentionally minimal in this ticket:

* ``scope_types`` defines the immutable scope and reference types.
* ``scope_graph`` provides the deterministic scope-graph builder.

Future tickets (T-2B-05, T-2B-06, etc.) will extend this package
with identifier resolution, DataItem construction, and other
semantic analyses.

Architectural invariants
=========================

* All public types are frozen dataclasses.
* No filesystem, network, or environment access.
* No V1 imports.
* No ``Dict[str, Any]`` in the public surface.
* All collections are tuples; iteration is in deterministic
  source order.
"""

from __future__ import annotations

from .scope_graph import build_scope_graph
from .scope_types import (
    Reference,
    ReferenceKind,
    Scope,
    ScopeGraph,
    ScopeKind,
)

__all__ = [
    "build_scope_graph",
    "Reference",
    "ReferenceKind",
    "Scope",
    "ScopeGraph",
    "ScopeKind",
]
