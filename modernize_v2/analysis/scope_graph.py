"""T-2C-0A Scope Graph Builder.

Consumes a ``ParserResult`` (from T-2B-03) and produces a
``ScopeGraph`` (frozen, deterministic).

Scope hierarchy produced
========================

::

    PROGRAM
      └─ SECTION  ("PROCEDURE_DIVISION")
           └─ BLOCK  ("PROCEDURE_BLOCK")

This is the most reliable scope structure derivable from the
current parser output.  The T-2B-03 parser does not emit
paragraph-header AST nodes; paragraph names appear only as
forward references in ``PerformStatement.paragraph_name`` and
``GoToStatement.target``.

What this builder does
======================

1. Walks the parser AST in deterministic source order.
2. Collects every ``IdentifierExpression`` reference and assigns
   it to the enclosing BLOCK scope, preserving the source span and
   the raw identifier text.
3. Collects every paragraph-name reference in
   ``PerformStatement`` and ``GoToStatement`` as forward
   paragraph references.
4. Emits no diagnostic for unresolved symbols (that is T-2B-05's
   responsibility).  The scope graph only records *what is
   referenced*, not *whether the reference is satisfiable*.

Determinism
===========

* No random, uuid, time, or hash-randomization.
* Identifier IDs are produced via ``id_for_node`` (deterministic
  per kind+path+position+ordinal).
* All collection iteration is in source order (statements are
  emitted in source order; references are visited in statement
  order; child scopes are emitted in pre-order).
* The output is purely a function of the input ``ParserResult``.

FROZEN contracts preserved
=========================

* The parser AST is read, not mutated.
* No lexer re-scans of the source are performed (which would
  duplicate logic and risk drift).  The scope graph is built
  *only* from the parser's existing AST output.
"""

from __future__ import annotations

import dataclasses
from typing import Any, List, Tuple

from modernize_v2.ir.ids import DeterministicId, id_for_node
from modernize_v2.ir.kinds import IRKind
from modernize_v2.parser.nodes import (
    DisplayStatement,
    GoToStatement,
    IdentifierExpression,
    ParserResult,
    PerformStatement,
)

from .scope_types import (
    Reference,
    ReferenceKind,
    Scope,
    ScopeGraph,
    ScopeKind,
)


# ------------------------------------------------------------------
# Internal helpers
# ------------------------------------------------------------------


# ------------------------------------------------------------------
# Internal helpers
# ------------------------------------------------------------------


def ordinal_to_kind_str(ordinal: int) -> str:
    """Return the id_for_node kind string for a scope ordinal.

    The ordinal encodes the scope role in the source:
      0 = PROGRAM
      1 = SECTION
      2 = BLOCK (uses PARAGRAPH as a placeholder kind string; the
                  scope's ``kind`` field still reports ``BLOCK``)
    Future paragraphs would use 3, 4, ...
    """
    if ordinal == 0:
        return IRKind.PROGRAM.value
    if ordinal == 1:
        return IRKind.SECTION.value
    if ordinal == 2:
        return IRKind.PARAGRAPH.value  # BLOCK scope kind namespace
    raise ValueError(f"unknown scope ordinal: {ordinal}")


def _make_scope_id(
    *,
    canonical_path: str,
    line: int,
    column: int,
    byte_offset: int,
    ordinal: int,
) -> DeterministicId:
    """Construct a deterministic scope ID."""
    return id_for_node(
        kind=ordinal_to_kind_str(ordinal),
        canonical_path=canonical_path,
        line=line,
        column=column,
        byte_offset=byte_offset,
        ordinal=ordinal,
    )


def _make_ref_id(
    *,
    canonical_path: str,
    line: int,
    column: int,
    byte_offset: int,
    ordinal: int,
) -> DeterministicId:
    """Construct a deterministic reference ID."""
    return id_for_node(
        kind="REFERENCE",
        canonical_path=canonical_path,
        line=line,
        column=column,
        byte_offset=byte_offset,
        ordinal=ordinal,
    )


# ------------------------------------------------------------------
# Identifier expression discovery
# ------------------------------------------------------------------


def _iter_fields(node: Any):
    """Yield each dataclass field of *node*.

    Yields ``(field_name, value)`` for every non-init-only field.
    """
    if not dataclasses.is_dataclass(node):
        return
    for f in dataclasses.fields(node):
        if f.name.startswith("_"):
            continue
        try:
            yield f.name, getattr(node, f.name)
        except AttributeError:
            continue


def _walk(node: Any):
    """Recursively walk a node, yielding all nested nodes.

    This is a strict, deterministic pre-order traversal.
    """
    yield node
    for _, value in _iter_fields(node):
        if isinstance(value, (list, tuple)):
            for item in value:
                yield from _walk(item)
        else:
            yield from _walk(value)


def _collect_data_references(node: Any) -> List[IdentifierExpression]:
    """Collect every IdentifierExpression under *node* in source
    order.

    The parser embeds nested statements inside compound
    statements (e.g. ``IfStatement.then_body``).  We walk the
    entire node tree so that references inside nested statements
    are also collected.  The caller must ensure each top-level
    statement is processed **exactly once**.
    """
    found: List[IdentifierExpression] = []
    for n in _walk(node):
        if isinstance(n, IdentifierExpression):
            found.append(n)
    return found


# ------------------------------------------------------------------
# Forward paragraph reference collection
# ------------------------------------------------------------------


def _iter_top_level_statements(statements: Tuple[Any, ...]):
    """Yield every top-level statement in deterministic source order.

    The caller invokes this exactly once for the parser's
    ``ast.statements`` tuple.  Compound statements (IF, EVALUATE)
    are processed in the same pass via the recursive
    ``_walk_identifier_references`` helper; nested statements are
    **not** yielded separately here, so each top-level statement
    is visited exactly once.
    """
    for stmt in statements:
        yield stmt


def _collect_paragraph_forward_refs(
    statements: Tuple[Any, ...],
) -> List[str]:
    """Collect the set of paragraph names referenced by PERFORM or
    GO TO, in first-seen source order.

    Visits the full statement tree so that PERFORM/GO TO inside
    IF/EVALUATE bodies are also captured.
    """
    seen: List[str] = []
    seen_set: set = set()
    for stmt in statements:
        for n in _walk(stmt):
            if isinstance(n, PerformStatement):
                name = n.paragraph_name
                if name not in seen_set:
                    seen.append(name)
                    seen_set.add(name)
            elif isinstance(n, GoToStatement):
                name = n.target
                if name not in seen_set:
                    seen.append(name)
                    seen_set.add(name)
    return seen


# ------------------------------------------------------------------
# Public entry point
# ------------------------------------------------------------------


def build_scope_graph(parser_result: ParserResult) -> ScopeGraph:
    """Build a deterministic scope graph from a ``ParserResult``.

    The parser's ``CompilationUnit.divisions`` is a tuple of
    division-header strings.  We rely on the parser to have
    classified the divisions structurally.  The scope graph
    builder does not re-parse or re-lex anything.

    Parameters
    ----------
    parser_result:
        The output of ``Parser.parse()`` on a token stream.

    Returns
    -------
    ScopeGraph
        The deterministic scope graph for the compilation unit.
    """
    ast = parser_result.ast
    canonical_path = ast.span.canonical_path

    # Find the byte range covered by the Procedure Division, if
    # present.  The parser records division headers as strings,
    # not spans; we use the statement spans to determine the
    # procedure-division extent conservatively.
    proc_start: int | None = None
    proc_end: int | None = None
    in_procedure = False
    for div in ast.divisions:
        if div == "PROCEDURE DIVISION":
            in_procedure = True
        # We do not have header spans here; we rely on the
        # statement spans to find the procedure-division region.
    if ast.statements:
        # Assume all statements are in the procedure division if
        # the parser emitted them.  The parser emits statements
        # only from PROCEDURE DIVISION in its current form.
        proc_start = ast.statements[0].span.start.byte_offset
        proc_end = ast.statements[-1].span.end.byte_offset
        in_procedure = True

    # --- Build scope tree ----------------------------------------

    # PROGRAM scope spans the entire compilation unit.
    program_id = _make_scope_id(
        canonical_path=canonical_path,
        line=1,
        column=0,
        byte_offset=0,
        ordinal=0,
    )
    program = Scope(
        id=program_id,
        kind=ScopeKind.PROGRAM,
        name="PROGRAM",
        span=ast.span,
        parent_id=None,
        children_ids=(),
    )

    # SECTION scope for the Procedure Division.
    section_id: Any = None
    section: Scope | None = None
    if in_procedure and proc_start is not None and proc_end is not None:
        section_id = _make_scope_id(
            canonical_path=canonical_path,
            line=1,
            column=0,
            byte_offset=proc_start,
            ordinal=1,
        )
        from modernize_v2.ir.diagnostic import SourceSpan

        section_span = SourceSpan(
            canonical_path=canonical_path,
            start=_position_at(canonical_path, proc_start),
            end=_position_at(canonical_path, proc_end),
        )
        section = Scope(
            id=section_id,
            kind=ScopeKind.SECTION,
            name="PROCEDURE_DIVISION",
            span=section_span,
            parent_id=program_id,
            children_ids=(),
        )

    # BLOCK scope inside the section.
    block_id: Any = None
    block: Scope | None = None
    if section is not None and proc_start is not None and proc_end is not None:
        block_id = _make_scope_id(
            canonical_path=canonical_path,
            line=1,
            column=0,
            byte_offset=proc_start,
            ordinal=2,
        )
        from modernize_v2.ir.diagnostic import SourceSpan

        block_span = SourceSpan(
            canonical_path=canonical_path,
            start=_position_at(canonical_path, proc_start),
            end=_position_at(canonical_path, proc_end),
        )
        block = Scope(
            id=block_id,
            kind=ScopeKind.BLOCK,
            name="PROCEDURE_BLOCK",
            span=block_span,
            parent_id=section_id,
            children_ids=(),
        )

    # --- Collect references ---------------------------------------

    block_for_ref = block.id if block is not None else (
        section.id if section is not None else program.id
    )

    references: List[Reference] = []
    ref_ordinal = 0
    # Walk each top-level statement exactly once.  _walk descends
    # into nested statements (e.g. IfStatement.then_body) so that
    # references inside compound statements are also collected
    # without double-counting.
    for stmt in _iter_top_level_statements(ast.statements):
        ids = _collect_data_references(stmt)
        for ident in ids:
            ref_id = _make_ref_id(
                canonical_path=canonical_path,
                line=ident.span.start.line,
                column=ident.span.start.column,
                byte_offset=ident.span.start.byte_offset,
                ordinal=ref_ordinal,
            )
            ref_ordinal += 1
            references.append(
                Reference(
                    id=ref_id,
                    kind=ReferenceKind.DATA_REFERENCE,
                    scope_id=block_for_ref,
                    text=ident.identifier_text,
                    span=ident.span,
                )
            )

    # --- Collect forward paragraph references --------------------

    forward_paragraphs = tuple(
        _collect_paragraph_forward_refs(ast.statements)
    )

    # --- Build final scope list with child IDs -------------------

    scopes_list: List[Scope] = [program]
    if section is not None:
        scopes_list.append(section)
    if block is not None:
        scopes_list.append(block)

    # Wire child_ids: PROGRAM has SECTION as a child; SECTION has
    # BLOCK as a child.  This is done after construction to keep
    # the dataclasses immutable.  The new PROGRAM object is also
    # used in the returned ScopeGraph so that the public ``program``
    # field carries the wired children_ids.
    new_scopes: List[Scope] = []
    new_program: Scope = program
    for s in scopes_list:
        if s.id == program_id and section is not None:
            wired = Scope(
                id=s.id,
                kind=s.kind,
                name=s.name,
                span=s.span,
                parent_id=s.parent_id,
                children_ids=(section.id,),
            )
            new_scopes.append(wired)
            if s.id == program_id:
                new_program = wired
        elif s.id == section_id and block is not None:
            new_scopes.append(
                Scope(
                    id=s.id,
                    kind=s.kind,
                    name=s.name,
                    span=s.span,
                    parent_id=s.parent_id,
                    children_ids=(block.id,),
                )
            )
        else:
            new_scopes.append(s)

    return ScopeGraph(
        program=new_program,
        scopes=tuple(new_scopes),
        references=tuple(references),
        forward_referenced_paragraphs=forward_paragraphs,
        paragraph_detection_available=False,
    )


def _position_at(canonical_path: str, byte_offset: int):
    """Return a ``SourcePosition`` for a byte offset.

    For T-2C-0A we use a minimal position with line=1 and
    column=byte_offset.  Subsequent phases (T-2B-05) will refine
    this using the existing ``SourceMap`` infrastructure.
    """
    from modernize_v2.ir.diagnostic import SourcePosition

    return SourcePosition(
        line=1,
        column=byte_offset,
        byte_offset=byte_offset,
    )


__all__ = ["build_scope_graph"]
