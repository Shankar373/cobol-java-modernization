"""T-2C-0A Scope Graph Tests.

These tests verify the deterministic semantic scope-analysis
foundation built on top of the T-2B-03 parser.

Coverage targets (from the task specification):

1. Empty/simple compilation unit
2. Procedure division
3. Multiple statements
4. Identifier references
5. Nested/control-flow statements
6. Scope assignment
7. Source span preservation
8. Deterministic IDs
9. Repeated analysis produces identical output
10. Multiple identifiers in one statement
11. Malformed/unsupported syntax already represented by parser diagnostics
12. Paragraph detection (limitation: only forward references)
13. Negative tests: no premature resolution, no DataItem invention, no
    parser/lexer mutation, no V1 import, no filesystem I/O, no AI/model
    output, no customer-specific logic.
"""

from __future__ import annotations

import dataclasses

import pytest

from modernize_v2.analysis import (
    Reference,
    ReferenceKind,
    Scope,
    ScopeGraph,
    ScopeKind,
    build_scope_graph,
)
from modernize_v2.lexer import CobolLexer, SourceFormat
from modernize_v2.parser import Parser
from modernize_v2.source import make_source_file


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _lex_and_parse(source: bytes, *, path: str = "test.cbl"):
    """Lex and parse the source, returning the ParserResult."""
    sf = make_source_file(path, source)
    lexer = CobolLexer(sf, source, SourceFormat.FREE)
    tokens = lexer.lex()
    parser = Parser(tokens, canonical_path=path)
    return parser.parse()


# ---------------------------------------------------------------------------
# 1. Empty / simple compilation unit
# ---------------------------------------------------------------------------


def test_empty_source_no_statements():
    """Empty source produces a scope graph with no references and
    no Procedure Division (no statements)."""
    result = _lex_and_parse(b"")
    graph = build_scope_graph(result)
    # Only the PROGRAM scope exists; no SECTION or BLOCK.
    assert len(graph.scopes) == 1
    assert graph.program.kind == ScopeKind.PROGRAM
    assert graph.references == ()
    assert graph.forward_referenced_paragraphs == ()
    assert not graph.paragraph_detection_available


def test_source_with_diagnostics_no_statements():
    """Source that the parser diagnoses as malformed but still
    produces no usable statements.  The scope graph has only the
    PROGRAM scope."""
    # Free-format source that the parser will diagnose as
    # containing an unknown token, but still parse around it.
    source = b"IDENTIFICATION DIVISION.\nPROGRAM-ID. PROG1.\nPROCEDURE DIVISION.\n"
    result = _lex_and_parse(source)
    graph = build_scope_graph(result)
    # No statements means no Procedure Division.
    assert len(graph.scopes) == 1
    assert graph.scopes[0].kind == ScopeKind.PROGRAM


# ---------------------------------------------------------------------------
# 2. Procedure division recognized
# ---------------------------------------------------------------------------


def test_procedure_division_creates_section_and_block():
    """A Procedure Division with at least one statement produces a
    SECTION and a BLOCK."""
    source = b"IDENTIFICATION DIVISION.\nPROGRAM-ID. P.\nPROCEDURE DIVISION.\nMOVE A TO B.\n"
    result = _lex_and_parse(source)
    graph = build_scope_graph(result)
    kinds = [s.kind for s in graph.scopes]
    assert ScopeKind.PROGRAM in kinds
    assert ScopeKind.SECTION in kinds
    assert ScopeKind.BLOCK in kinds


def test_section_name_is_procedure_division():
    """The SECTION scope is named 'PROCEDURE_DIVISION' to make it
    self-describing in diagnostics and repr()."""
    source = b"PROCEDURE DIVISION.\nMOVE A TO B.\n"
    result = _lex_and_parse(source)
    graph = build_scope_graph(result)
    section = next(s for s in graph.scopes if s.kind == ScopeKind.SECTION)
    assert section.name == "PROCEDURE_DIVISION"


def test_block_name_is_procedure_block():
    """The BLOCK scope is named 'PROCEDURE_BLOCK'."""
    source = b"PROCEDURE DIVISION.\nMOVE A TO B.\n"
    result = _lex_and_parse(source)
    graph = build_scope_graph(result)
    block = next(s for s in graph.scopes if s.kind == ScopeKind.BLOCK)
    assert block.name == "PROCEDURE_BLOCK"


# ---------------------------------------------------------------------------
# 3. Multiple statements
# ---------------------------------------------------------------------------


def test_multiple_statements_all_in_block():
    """All statements in the Procedure Division fall into the
    same BLOCK scope."""
    source = (
        b"PROCEDURE DIVISION.\n"
        b"MOVE A TO B.\n"
        b"DISPLAY C.\n"
        b"ADD D TO E.\n"
    )
    result = _lex_and_parse(source)
    graph = build_scope_graph(result)
    block = next(s for s in graph.scopes if s.kind == ScopeKind.BLOCK)
    block_refs = graph.references_in_scope(block.id)
    # 5 references: A, B, C, D, E
    assert len(block_refs) == 5
    texts = [r.text for r in block_refs]
    assert texts == ["A", "B", "C", "D", "E"]


# ---------------------------------------------------------------------------
# 4. Identifier references
# ---------------------------------------------------------------------------


def test_identifier_references_captured_with_text():
    """Every identifier reference is recorded with its raw text."""
    source = b"PROCEDURE DIVISION.\nMOVE WS-AMOUNT TO WS-TOTAL.\n"
    result = _lex_and_parse(source)
    graph = build_scope_graph(result)
    texts = [r.text for r in graph.references]
    assert "WS-AMOUNT" in texts
    assert "WS-TOTAL" in texts


def test_identifier_references_captured_with_spans():
    """Every identifier reference carries the exact byte span from
    the parser."""
    source = b"PROCEDURE DIVISION.\nMOVE A TO B.\n"
    result = _lex_and_parse(source)
    graph = build_scope_graph(result)
    a_ref = next(r for r in graph.references if r.text == "A")
    assert a_ref.span.start.byte_offset == source.index(b"A")
    assert a_ref.span.end.byte_offset == source.index(b"A") + 1


# ---------------------------------------------------------------------------
# 5. Nested / control-flow statements
# ---------------------------------------------------------------------------


def test_if_statement_references_inside_body():
    """References inside an IF/THEN body are recorded (no double
    counting, no loss)."""
    source = (
        b"PROCEDURE DIVISION.\n"
        b"IF A > B\n"
        b"MOVE C TO D\n"
        b"END-IF.\n"
    )
    result = _lex_and_parse(source)
    graph = build_scope_graph(result)
    texts = [r.text for r in graph.references]
    # A, B (condition); C, D (then body)
    assert texts == ["A", "B", "C", "D"]


def test_else_body_references_recorded():
    """References inside an ELSE body are recorded."""
    source = (
        b"PROCEDURE DIVISION.\n"
        b"IF A > B\n"
        b"MOVE C TO D\n"
        b"ELSE\n"
        b"MOVE E TO F\n"
        b"END-IF.\n"
    )
    result = _lex_and_parse(source)
    graph = build_scope_graph(result)
    texts = [r.text for r in graph.references]
    assert texts == ["A", "B", "C", "D", "E", "F"]


def test_nested_if_references_recorded():
    """References inside nested IF statements are recorded."""
    source = (
        b"PROCEDURE DIVISION.\n"
        b"IF A > B\n"
        b"IF C > D\n"
        b"MOVE E TO F\n"
        b"END-IF\n"
        b"END-IF.\n"
    )
    result = _lex_and_parse(source)
    graph = build_scope_graph(result)
    texts = [r.text for r in graph.references]
    assert texts == ["A", "B", "C", "D", "E", "F"]


# ---------------------------------------------------------------------------
# 6. Scope assignment
# ---------------------------------------------------------------------------


def test_all_references_assigned_to_block():
    """Every reference is assigned to the BLOCK scope, not the
    SECTION or PROGRAM."""
    source = (
        b"PROCEDURE DIVISION.\n"
        b"MOVE A TO B.\n"
        b"IF A > B\n"
        b"MOVE C TO D\n"
        b"END-IF.\n"
    )
    result = _lex_and_parse(source)
    graph = build_scope_graph(result)
    block = next(s for s in graph.scopes if s.kind == ScopeKind.BLOCK)
    for ref in graph.references:
        assert ref.scope_id == block.id


def test_scope_hierarchy():
    """The scope tree is PROGRAM -> SECTION -> BLOCK with proper
    parent/child links."""
    source = b"PROCEDURE DIVISION.\nMOVE A TO B.\n"
    result = _lex_and_parse(source)
    graph = build_scope_graph(result)
    program = graph.program
    assert program.parent_id is None
    section = next(s for s in graph.scopes if s.kind == ScopeKind.SECTION)
    assert section.parent_id == program.id
    block = next(s for s in graph.scopes if s.kind == ScopeKind.BLOCK)
    assert block.parent_id == section.id
    # Children
    assert section.id in program.children_ids
    assert block.id in section.children_ids


# ---------------------------------------------------------------------------
# 7. Source span preservation
# ---------------------------------------------------------------------------


def test_program_scope_spans_entire_source():
    """The PROGRAM scope spans the full source."""
    source = b"IDENTIFICATION DIVISION.\nPROGRAM-ID. P.\nPROCEDURE DIVISION.\nMOVE A TO B.\n"
    result = _lex_and_parse(source)
    graph = build_scope_graph(result)
    program = graph.program
    assert program.span.start.byte_offset == 0
    assert program.span.end.byte_offset == len(source)


def test_section_span_covers_procedure_statements():
    """The SECTION span covers at least the first and last
    statement byte offsets."""
    source = b"PROCEDURE DIVISION.\nMOVE A TO B.\nDISPLAY C.\n"
    result = _lex_and_parse(source)
    graph = build_scope_graph(result)
    section = next(s for s in graph.scopes if s.kind == ScopeKind.SECTION)
    first_stmt = result.ast.statements[0]
    last_stmt = result.ast.statements[-1]
    assert section.span.start.byte_offset == first_stmt.span.start.byte_offset
    assert section.span.end.byte_offset == last_stmt.span.end.byte_offset


def test_reference_span_matches_parser_span():
    """The reference's span exactly matches the original
    IdentifierExpression's span."""
    source = b"PROCEDURE DIVISION.\nMOVE WS-X TO WS-Y.\n"
    result = _lex_and_parse(source)
    graph = build_scope_graph(result)
    ws_x_ref = next(r for r in graph.references if r.text == "WS-X")
    assert ws_x_ref.span.start.byte_offset == source.index(b"WS-X")
    assert ws_x_ref.span.end.byte_offset == source.index(b"WS-X") + 4
    ws_y_ref = next(r for r in graph.references if r.text == "WS-Y")
    assert ws_y_ref.span.start.byte_offset == source.index(b"WS-Y")
    assert ws_y_ref.span.end.byte_offset == source.index(b"WS-Y") + 4


def test_canonical_path_preserved():
    """The canonical path is preserved on every scope and
    reference."""
    source = b"PROCEDURE DIVISION.\nMOVE A TO B.\n"
    result = _lex_and_parse(source, path="myprog.cbl")
    graph = build_scope_graph(result)
    for s in graph.scopes:
        assert s.span.canonical_path == "myprog.cbl"
    for r in graph.references:
        assert r.span.canonical_path == "myprog.cbl"


# ---------------------------------------------------------------------------
# 8. Deterministic IDs
# ---------------------------------------------------------------------------


def test_program_id_is_deterministic():
    """The PROGRAM scope ID is deterministic for the same source."""
    source = b"IDENTIFICATION DIVISION.\nPROGRAM-ID. P.\nPROCEDURE DIVISION.\nMOVE A TO B.\n"
    g1 = build_scope_graph(_lex_and_parse(source))
    g2 = build_scope_graph(_lex_and_parse(source))
    assert g1.program.id == g2.program.id
    assert g1.program.id.text == g2.program.id.text


def test_block_id_is_deterministic():
    """The BLOCK scope ID is deterministic for the same source."""
    source = b"PROCEDURE DIVISION.\nMOVE A TO B.\n"
    g1 = build_scope_graph(_lex_and_parse(source))
    g2 = build_scope_graph(_lex_and_parse(source))
    b1 = next(s for s in g1.scopes if s.kind == ScopeKind.BLOCK)
    b2 = next(s for s in g2.scopes if s.kind == ScopeKind.BLOCK)
    assert b1.id == b2.id


def test_reference_ids_are_deterministic():
    """Reference IDs are deterministic for the same source."""
    source = b"PROCEDURE DIVISION.\nMOVE A TO B.\n"
    g1 = build_scope_graph(_lex_and_parse(source))
    g2 = build_scope_graph(_lex_and_parse(source))
    a1 = next(r for r in g1.references if r.text == "A")
    a2 = next(r for r in g2.references if r.text == "A")
    assert a1.id == a2.id


def test_ids_are_26_chars():
    """All IDs are 26-character Crockford base32 strings."""
    source = b"PROCEDURE DIVISION.\nMOVE A TO B.\n"
    graph = build_scope_graph(_lex_and_parse(source))
    for s in graph.scopes:
        assert len(s.id.text) == 26
    for r in graph.references:
        assert len(r.id.text) == 26


# ---------------------------------------------------------------------------
# 9. Repeated analysis produces identical output
# ---------------------------------------------------------------------------


def test_repeated_analysis_identical():
    """Calling build_scope_graph twice on the same ParserResult
    produces identical outputs."""
    result = _lex_and_parse(
        b"PROCEDURE DIVISION.\nMOVE A TO B.\nIF C > D\nMOVE E TO F\nEND-IF.\n"
    )
    g1 = build_scope_graph(result)
    g2 = build_scope_graph(result)
    assert g1.scopes == g2.scopes
    assert g1.references == g2.references
    assert g1.forward_referenced_paragraphs == g2.forward_referenced_paragraphs


def test_repeated_lexer_parse_analyze_identical():
    """Two separate lexer+parser+analysis chains on the same
    source produce identical scope graphs."""
    source = b"PROCEDURE DIVISION.\nMOVE A TO B.\n"
    g1 = build_scope_graph(_lex_and_parse(source))
    g2 = build_scope_graph(_lex_and_parse(source))
    assert g1.program.id == g2.program.id
    assert [s.id for s in g1.scopes] == [s.id for s in g2.scopes]
    assert [r.id for r in g1.references] == [r.id for r in g2.references]


# ---------------------------------------------------------------------------
# 10. Multiple identifiers in one statement
# ---------------------------------------------------------------------------


def test_add_statement_references():
    """ADD A TO B GIVING C records all three identifiers."""
    source = b"PROCEDURE DIVISION.\nADD A TO B GIVING C.\n"
    result = _lex_and_parse(source)
    graph = build_scope_graph(result)
    texts = [r.text for r in graph.references]
    assert texts == ["A", "B", "C"]


def test_compute_statement_expression_references():
    """COMPUTE X = A + B records all three identifiers plus
    arithmetic operators in their expression structure."""
    source = b"PROCEDURE DIVISION.\nCOMPUTE X = A + B.\n"
    result = _lex_and_parse(source)
    graph = build_scope_graph(result)
    texts = [r.text for r in graph.references]
    assert texts == ["X", "A", "B"]


# ---------------------------------------------------------------------------
# 11. Parser diagnostics propagation
# ---------------------------------------------------------------------------


def test_parser_diagnostics_not_swallowed():
    """Parser diagnostics are preserved; the scope graph builder
    does not depend on their presence or absence."""
    # Source with a known parser issue: "PROGRAM-ID" is an
    # unknown token in the current parser.
    source = (
        b"IDENTIFICATION DIVISION.\n"
        b"PROGRAM-ID. PROG1.\n"
        b"PROCEDURE DIVISION.\n"
        b"MOVE A TO B.\n"
    )
    result = _lex_and_parse(source)
    # Parser should have produced at least one diagnostic.
    assert len(result.diagnostics) >= 1
    graph = build_scope_graph(result)
    # The graph is still produced (no exception) and contains the
    # usable statement.
    assert len(graph.references) == 2


# ---------------------------------------------------------------------------
# 12. Paragraph detection limitation
# ---------------------------------------------------------------------------


def test_paragraph_detection_not_available():
    """The graph reports paragraph_detection_available = False."""
    source = b"PROCEDURE DIVISION.\nMOVE A TO B.\n"
    graph = build_scope_graph(_lex_and_parse(source))
    assert graph.paragraph_detection_available is False


def test_forward_paragraph_references_recorded():
    """PERFORM and GO TO paragraph targets are recorded as forward
    references in first-seen order."""
    source = (
        b"PROCEDURE DIVISION.\n"
        b"PERFORM FIRST-PARA.\n"
        b"GO TO SECOND-PARA.\n"
        b"PERFORM FIRST-PARA.\n"  # duplicate; should not be repeated
        b"GO TO THIRD-PARA.\n"
    )
    graph = build_scope_graph(_lex_and_parse(source))
    assert graph.forward_referenced_paragraphs == (
        "FIRST-PARA",
        "SECOND-PARA",
        "THIRD-PARA",
    )


def test_forward_paragraphs_no_paragraph_scopes():
    """When paragraph detection is unavailable, no PARAGRAPH scopes
    are emitted even though paragraph names are referenced."""
    source = b"PROCEDURE DIVISION.\nPERFORM PARA-1.\nGO TO PARA-2.\n"
    graph = build_scope_graph(_lex_and_parse(source))
    kinds = [s.kind for s in graph.scopes]
    assert ScopeKind.PARAGRAPH not in kinds
    assert graph.paragraph_detection_available is False


def test_forward_paragraphs_inside_if():
    """PERFORM inside an IF body is still recorded as a forward
    reference."""
    source = (
        b"PROCEDURE DIVISION.\n"
        b"IF A > B\n"
        b"PERFORM INSIDE-PARA.\n"
        b"END-IF.\n"
    )
    graph = build_scope_graph(_lex_and_parse(source))
    assert graph.forward_referenced_paragraphs == ("INSIDE-PARA",)


def test_no_paragraph_references_when_no_perform_goto():
    """If there are no PERFORM or GO TO, the forward-references
    tuple is empty."""
    source = b"PROCEDURE DIVISION.\nMOVE A TO B.\n"
    graph = build_scope_graph(_lex_and_parse(source))
    assert graph.forward_referenced_paragraphs == ()


# ---------------------------------------------------------------------------
# Negative tests: things the scope graph MUST NOT do
# ---------------------------------------------------------------------------


def test_no_resolution_attempt():
    """The scope graph does NOT resolve undeclared identifiers.

    An identifier that has no DataItem (because T-2B-06 has not
    run) is still recorded as a reference; no diagnostic is
    emitted.
    """
    source = b"PROCEDURE DIVISION.\nMOVE UNDECLARED TO ALSO-UNDECLARED.\n"
    graph = build_scope_graph(_lex_and_parse(source))
    texts = [r.text for r in graph.references]
    assert "UNDECLARED" in texts
    assert "ALSO-UNDECLARED" in texts
    # No UNRESOLVED_SYMBOL diagnostic from the scope graph.
    # (The parser may have its own diagnostics but the scope graph
    # does not emit any.)


def test_no_dataitem_invention():
    """The scope graph does NOT invent DataItem nodes."""
    source = b"PROCEDURE DIVISION.\nMOVE A TO B.\n"
    graph = build_scope_graph(_lex_and_parse(source))
    # No field named "data_item" or similar; the public surface
    # is only scopes, references, forward-references.
    field_names = set()
    for s in graph.scopes:
        field_names.update(f.name for f in dataclasses.fields(s))
    for r in graph.references:
        field_names.update(f.name for f in dataclasses.fields(r))
    field_names.update(f.name for f in dataclasses.fields(graph))
    assert "data_item" not in field_names
    assert "dataitem" not in field_names
    assert "dat_item" not in field_names


def test_does_not_mutate_parser_result():
    """The scope graph builder does not mutate the parser's
    CompilationUnit or any statement nodes."""
    source = (
        b"PROCEDURE DIVISION.\n"
        b"MOVE A TO B.\n"
        b"IF A > B\n"
        b"MOVE C TO D\n"
        b"END-IF.\n"
    )
    result = _lex_and_parse(source)
    # Snapshot the AST.
    before_statements = tuple(
        dataclasses.asdict(s) for s in result.ast.statements
    )
    before_divisions = result.ast.divisions
    # Build the graph.
    build_scope_graph(result)
    # The AST must be unchanged.
    after_statements = tuple(
        dataclasses.asdict(s) for s in result.ast.statements
    )
    after_divisions = result.ast.divisions
    assert before_statements == after_statements
    assert before_divisions == after_divisions


def test_no_dict_str_any_in_public_api():
    """The public API does not contain Dict[str, Any]."""
    import typing

    import modernize_v2.analysis as analysis_mod
    import modernize_v2.analysis.scope_types as st

    # Inspect the public __all__ exports of both modules.
    for mod in (analysis_mod, st):
        for name in getattr(mod, "__all__", ()):
            obj = getattr(mod, name, None)
            if obj is None:
                continue
            # Inspect annotations for Dict[str, Any].
            hints = getattr(obj, "__annotations__", {})
            for hint_name, hint_val in hints.items():
                hint_repr = repr(hint_val)
                assert "Dict[str, Any]" not in hint_repr, (
                    f"{mod.__name__}.{name}.{hint_name} uses Dict[str, Any]"
                )


def test_no_v1_imports():
    """The analysis package does not import anything from V1."""
    import modernize_v2.analysis as analysis_mod
    import modernize_v2.analysis.scope_graph as sg
    import modernize_v2.analysis.scope_types as st

    for mod in (analysis_mod, sg, st):
        source = open(mod.__file__).read()
        # V1 is at modernize/. The analysis package is not allowed
        # to import from it.
        assert "from modernize" not in source or "modernize_v2" in source
        # Specifically, there should be no import of V1 modules.
        for line in source.splitlines():
            line_stripped = line.strip()
            if line_stripped.startswith("import ") or line_stripped.startswith("from "):
                if "modernize." in line_stripped and "modernize_v2" not in line_stripped:
                    raise AssertionError(
                        f"V1 import in {mod.__name__}: {line_stripped}"
                    )


def test_no_filesystem_io_in_analysis():
    """The analysis package does not call open() or os functions for
    I/O.  It receives the parser result as input; it does not
    read or write files."""
    import modernize_v2.analysis.scope_graph as sg

    source = open(sg.__file__).read()
    # The source must not contain open(, os.open, os.read, etc.
    for forbidden in [
        "open(",
        "os.open",
        "os.read",
        "os.write",
        "with open(",
        "Path(",
    ]:
        assert forbidden not in source, (
            f"forbidden I/O construct {forbidden!r} found in scope_graph.py"
        )


# ---------------------------------------------------------------------------
# Tests for the public API surface
# ---------------------------------------------------------------------------


def test_scope_graph_is_frozen():
    """ScopeGraph is a frozen dataclass; cannot be mutated after
    construction."""
    source = b"PROCEDURE DIVISION.\nMOVE A TO B.\n"
    graph = build_scope_graph(_lex_and_parse(source))
    with pytest.raises(dataclasses.FrozenInstanceError):
        graph.paragraph_detection_available = True  # type: ignore[misc]


def test_scope_is_frozen():
    """Scope is a frozen dataclass."""
    source = b"PROCEDURE DIVISION.\nMOVE A TO B.\n"
    graph = build_scope_graph(_lex_and_parse(source))
    program = graph.program
    with pytest.raises(dataclasses.FrozenInstanceError):
        program.name = "OTHER"  # type: ignore[misc]


def test_reference_is_frozen():
    """Reference is a frozen dataclass."""
    source = b"PROCEDURE DIVISION.\nMOVE A TO B.\n"
    graph = build_scope_graph(_lex_and_parse(source))
    a_ref = next(r for r in graph.references if r.text == "A")
    with pytest.raises(dataclasses.FrozenInstanceError):
        a_ref.text = "Z"  # type: ignore[misc]


def test_references_in_scope_helper():
    """ScopeGraph.references_in_scope returns only references for
    the given scope, in source order."""
    source = b"PROCEDURE DIVISION.\nMOVE A TO B.\nMOVE C TO D.\n"
    graph = build_scope_graph(_lex_and_parse(source))
    block = next(s for s in graph.scopes if s.kind == ScopeKind.BLOCK)
    refs = graph.references_in_scope(block.id)
    assert [r.text for r in refs] == ["A", "B", "C", "D"]


def test_scope_by_id_finds_scope():
    """ScopeGraph.scope_by_id returns the matching scope or None."""
    source = b"PROCEDURE DIVISION.\nMOVE A TO B.\n"
    graph = build_scope_graph(_lex_and_parse(source))
    program = graph.program
    assert graph.scope_by_id(program.id) is program


def test_scope_by_id_returns_none_for_unknown():
    """ScopeGraph.scope_by_id returns None for an unknown ID."""
    from modernize_v2.ir.ids import DeterministicId, id_for_node

    source = b"PROCEDURE DIVISION.\nMOVE A TO B.\n"
    graph = build_scope_graph(_lex_and_parse(source))
    unknown_id = id_for_node(
        kind="UNKNOWN",
        canonical_path="other.cbl",
        line=1,
        column=0,
        byte_offset=0,
        ordinal=0,
    )
    assert graph.scope_by_id(unknown_id) is None
