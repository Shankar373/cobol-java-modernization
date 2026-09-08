"""T-2C-0A Semantic Scope Types.

Immutable, deterministic scope types consumed by the scope graph
builder and produced as part of the semantic analysis pass.

This module is **purely structural**.  It does not perform
resolution, type checking, or any other semantic interpretation.
The scope graph records *which scopes exist* and *which references
appear in each scope*.  The next ticket (T-2B-05) is responsible
for actually resolving references to DataItems.

Architectural contract
======================

* Every public type is a frozen dataclass.  No mutation.
* Every scope has a stable ``DeterministicId`` derived solely from
  source-fingerprint + path + position + ordinal via
  ``id_for_node``.
* Source spans are preserved using the existing ``SourceSpan`` /
  ``SourcePosition`` types from ``modernize_v2.ir.diagnostic``.
* No ``Dict[str, Any]`` in the public surface.
* No filesystem, network, or environment access.
* No imports from the V1 production tree.

Paragraph-detection limitation
=============================

The current T-2B-03 syntax parser does **not** emit paragraph-header
AST nodes.  Paragraph names appear only as forward references in
``PerformStatement.paragraph_name`` and ``GoToStatement.target``.

Therefore, this scope layer:

* Builds a single ``PROGRAM`` scope.
* Builds a single ``SECTION`` scope for the Procedure Division.
* Builds a single ``BLOCK`` scope inside the Section.
* **Does not** infer paragraph-definition boundaries from the
  parser AST.
* Records the *names* of paragraphs referenced by ``PERFORM`` and
  ``GO TO`` in the result's ``forward_referenced_paragraphs`` set
  for downstream use.

The decision to *not* infer paragraph definitions is explicit and
fail-safe.  Downstream phases (T-2B-05, T-2B-06) consume the
``forward_referenced_paragraphs`` set; they do **not** rely on
paragraph scopes being present.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple

from modernize_v2.ir.diagnostic import SourceSpan
from modernize_v2.ir.ids import DeterministicId


# ------------------------------------------------------------------
# Scope and reference kinds
# ------------------------------------------------------------------


class ScopeKind(str, Enum):
    """Kind of a semantic scope.

    The set is intentionally minimal for T-2C-0A.  Section and
    Paragraph kinds are reserved for future use but are not yet
    emitted by the scope-graph builder because the parser does not
    expose paragraph definition boundaries.
    """

    PROGRAM = "PROGRAM"
    SECTION = "SECTION"
    PARAGRAPH = "PARAGRAPH"
    BLOCK = "BLOCK"


class ReferenceKind(str, Enum):
    """Kind of a syntactic reference recorded in the scope graph.

    * ``DATA_REFERENCE`` — an identifier used in a statement or
      expression (e.g. ``MOVE A TO B`` references ``A`` and ``B``).
    * ``PARAGRAPH_REFERENCE`` — a paragraph name used as the target
      of ``PERFORM`` or ``GO TO`` (forward reference; not yet
      resolved to a paragraph definition).
    """

    DATA_REFERENCE = "DATA_REFERENCE"
    PARAGRAPH_REFERENCE = "PARAGRAPH_REFERENCE"


# ------------------------------------------------------------------
# Scope
# ------------------------------------------------------------------


@dataclass(frozen=True)
class Scope:
    """A semantic scope.

    Every scope has a deterministic identity derived from its
    source position.  Scopes are organized as a tree through
    ``parent_id`` and ``children_ids``.

    The ``name`` is a human-readable identifier (e.g. ``"PROGRAM"``,
    ``"PROCEDURE_DIVISION"``) that survives ``repr()`` and is
    useful in diagnostics.  The ``span`` identifies the source
    region covered by the scope; for the PROGRAM scope this is
    the entire source, for the SECTION scope it is the
    Procedure-Division region, and for the BLOCK scope it is the
    same (paragraph boundaries are not yet available).
    """

    id: DeterministicId
    kind: ScopeKind
    name: str
    span: SourceSpan
    parent_id: DeterministicId | None
    children_ids: Tuple[DeterministicId, ...] = field(default_factory=tuple)


# ------------------------------------------------------------------
# Reference
# ------------------------------------------------------------------


@dataclass(frozen=True)
class Reference:
    """A syntactic reference recorded in the scope graph.

    A reference captures the *raw* text of an identifier as it
    appears in the source, the scope in which it appears, and the
    exact source span.  No resolution to a DataItem or Paragraph
    definition is performed here.
    """

    id: DeterministicId
    kind: ReferenceKind
    scope_id: DeterministicId
    text: str
    span: SourceSpan


# ------------------------------------------------------------------
# Scope graph
# ------------------------------------------------------------------


@dataclass(frozen=True)
class ScopeGraph:
    """The deterministic scope graph for a single compilation unit.

    The graph is built by ``build_scope_graph`` from a
    ``ParserResult``.  The graph contains:

    * a single ``PROGRAM`` scope (``program``)
    * one or more child scopes (sections, blocks, paragraphs)
    * a tuple of references in deterministic source order
    * a tuple of forward-referenced paragraph names

    The graph is immutable.  All collections are tuples; iteration
    order is source order.
    """

    program: Scope
    scopes: Tuple[Scope, ...]  # program + all child scopes, deterministic order
    references: Tuple[Reference, ...]  # source order
    forward_referenced_paragraphs: Tuple[str, ...]  # unique, source-ordered
    # Indicator that paragraph definition detection is unavailable.
    # This is a structural fact about the current parser; it is
    # *not* a diagnostic.  Future work (T-2B-05 / T-2B-06) may
    # resolve paragraph names; until then, the absence of paragraph
    # scopes is the source of truth.
    paragraph_detection_available: bool

    def scope_by_id(
        self, scope_id: DeterministicId
    ) -> Scope | None:
        """Look up a scope by its deterministic ID.

        Returns None if the scope is not in the graph.
        """
        for s in self.scopes:
            if s.id == scope_id:
                return s
        return None

    def scopes_in_source_order(self) -> Tuple[Scope, ...]:
        """Return all scopes in deterministic source order.

        Scopes are emitted in pre-order depth-first traversal so
        the program appears first, then its sections, then their
        blocks (and, in the future, paragraphs).
        """
        return self.scopes

    def references_in_scope(
        self, scope_id: DeterministicId
    ) -> Tuple[Reference, ...]:
        """Return all references whose scope is ``scope_id``.

        Returned in deterministic source order.
        """
        return tuple(r for r in self.references if r.scope_id == scope_id)


__all__ = [
    "ScopeKind",
    "ReferenceKind",
    "Scope",
    "Reference",
    "ScopeGraph",
]
