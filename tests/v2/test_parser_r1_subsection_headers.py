"""T-2B-04R.1 — Data Division subsection header tests.

These tests verify the T-2B-04R.1 controlled parser-extension
slice: structural recognition of Data Division subsection
headers (``WORKING-STORAGE SECTION``, ``LINKAGE SECTION``,
``LOCAL-STORAGE SECTION``, ``REPORT SECTION``, ``FILE SECTION``).

R.1 does NOT:
    * parse data-item declarations
    * resolve identifiers
    * compute layout
    * construct semantic DataItem trees
    * emit identifier-resolution diagnostics

It ONLY records subsection-header boundaries in the parser AST.
"""

from __future__ import annotations

from modernize_v2.ir.kinds import IRKind
from modernize_v2.lexer import CobolLexer, SourceFormat
from modernize_v2.parser import Parser, DataDivisionSubsection
from modernize_v2.source import make_source_file


def _lex_and_parse(source: bytes, *, path: str = "test.cbl"):
    sf = make_source_file(path, source)
    lexer = CobolLexer(sf, source, SourceFormat.FREE)
    tokens = lexer.lex()
    parser = Parser(tokens, canonical_path=path)
    return parser.parse()


# ---------------------------------------------------------------------------
# 1. WORKING-STORAGE SECTION
# ---------------------------------------------------------------------------

def test_r1_working_storage_recognized():
    """WORKING-STORAGE SECTION. produces a DataDivisionSubsection
    node, not an 'unknown token' diagnostic."""
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\nPROCEDURE DIVISION.\n"
    result = _lex_and_parse(source)
    assert len(result.ast.data_division_subsections) == 1
    sub = result.ast.data_division_subsections[0]
    assert sub.kind == IRKind.WORKING_STORAGE_SECTION
    assert sub.name == "WORKING-STORAGE"


def test_r1_working_storage_no_unknown_token_diagnostic():
    """After R.1, WORKING-STORAGE and SECTION no longer produce
    'unknown token' diagnostics (only data-item declarations
    such as 01 and PIC still do, but those are not R.1's scope)."""
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n"
    result = _lex_and_parse(source)
    for d in result.diagnostics:
        assert "WORKING-STORAGE" not in d.message
        assert "SECTION" != d.message.strip().rstrip(".").split()[-1], (
            f"Unexpected diagnostic about SECTION: {d.message}"
        )


# ---------------------------------------------------------------------------
# 2-6. Each of the 5 subsection types
# ---------------------------------------------------------------------------

def test_r1_linkage_recognized():
    source = b"DATA DIVISION.\nLINKAGE SECTION.\nPROCEDURE DIVISION.\n"
    result = _lex_and_parse(source)
    assert len(result.ast.data_division_subsections) == 1
    sub = result.ast.data_division_subsections[0]
    assert sub.kind == IRKind.LINKAGE_SECTION
    assert sub.name == "LINKAGE"


def test_r1_local_storage_recognized():
    source = b"DATA DIVISION.\nLOCAL-STORAGE SECTION.\nPROCEDURE DIVISION.\n"
    result = _lex_and_parse(source)
    assert len(result.ast.data_division_subsections) == 1
    sub = result.ast.data_division_subsections[0]
    assert sub.kind == IRKind.LOCAL_STORAGE_SECTION
    assert sub.name == "LOCAL-STORAGE"


def test_r1_report_recognized():
    source = b"DATA DIVISION.\nREPORT SECTION.\nPROCEDURE DIVISION.\n"
    result = _lex_and_parse(source)
    assert len(result.ast.data_division_subsections) == 1
    sub = result.ast.data_division_subsections[0]
    assert sub.kind == IRKind.REPORT_SECTION
    assert sub.name == "REPORT"


def test_r1_file_recognized():
    source = b"DATA DIVISION.\nFILE SECTION.\nPROCEDURE DIVISION.\n"
    result = _lex_and_parse(source)
    assert len(result.ast.data_division_subsections) == 1
    sub = result.ast.data_division_subsections[0]
    assert sub.kind == IRKind.FILE_SECTION
    assert sub.name == "FILE"


# ---------------------------------------------------------------------------
# 7. Multiple subsections preserve source order
# ---------------------------------------------------------------------------

def test_r1_multiple_subsections_preserve_order():
    """Multiple subsections in the same Data Division are recorded
    in source order."""
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"LINKAGE SECTION.\n"
        b"LOCAL-STORAGE SECTION.\n"
        b"REPORT SECTION.\n"
        b"FILE SECTION.\n"
        b"PROCEDURE DIVISION.\n"
    )
    result = _lex_and_parse(source)
    names = [s.name for s in result.ast.data_division_subsections]
    assert names == [
        "WORKING-STORAGE",
        "LINKAGE",
        "LOCAL-STORAGE",
        "REPORT",
        "FILE",
    ]


# ---------------------------------------------------------------------------
# 8. Empty Data Division
# ---------------------------------------------------------------------------

def test_r1_empty_data_division():
    """DATA DIVISION. without any subsection produces an empty
    data_division_subsections tuple (not None, not an error)."""
    source = b"DATA DIVISION.\nPROCEDURE DIVISION.\nMOVE A TO B."
    result = _lex_and_parse(source)
    assert result.ast.data_division_subsections == ()


# ---------------------------------------------------------------------------
# 9. Data Division followed by unsupported declarations does not
#     create fake DataItems
# ---------------------------------------------------------------------------

def test_r1_no_fake_data_items():
    """R.1 must NOT create DataItem-like nodes for data-item
    declarations.  A source like ``01 WS-A PIC X(10).`` must
    not cause R.1 to emit a DataItem node — that is the responsibility
    of R.2.  This test verifies that R.1 only handles subsection
    headers and that data items are not part of R.1's scope.

    After T-2B-04R.2, DataItem nodes ARE produced — but that
    is R.2, not R.1.  This test documents the separation of
    concerns between R.1 (subsection headers) and R.2 (data items).
    """
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-A PIC X(10).\n"
        b"PROCEDURE DIVISION.\n"
    )
    result = _lex_and_parse(source)
    # The subsection IS recorded.
    assert len(result.ast.data_division_subsections) == 1
    # R.1 does NOT create the ``data_items`` field directly;
    # the field is owned by R.2.  In R.1's absence, this field
    # would not exist.  R.2 adds the field additively and populates
    # it.  Verify that the R.1 part (subsection header) is correct
    # and the R.2 part (data items) is independently populated.
    # The R.1 section is exactly one entry; it does not contain
    # data items.
    assert result.ast.data_division_subsections[0].name == "WORKING-STORAGE"
    # R.2 is responsible for creating data-item nodes.  The R.1
    # test does not assert on data_items (R.2 has its own tests).
    # The important R.1 invariant: subsection headers are recognized
    # without error, and no data-item SILENTLY leaks into the
    # R.1 field.  Verify the R.1 field only contains DataDivisionSubsection
    # objects, not DataItemDeclaration objects.
    for s in result.ast.data_division_subsections:
        assert isinstance(s, DataDivisionSubsection)
        assert s.kind == IRKind.WORKING_STORAGE_SECTION


def test_r1_data_items_not_collected_into_subsection_field():
    """The data_division_subsections tuple must contain only
    subsection-header nodes, not data-item declarations."""
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-A PIC X(10).\n"
        b"01 WS-B PIC 9(5).\n"
        b"PROCEDURE DIVISION.\n"
    )
    result = _lex_and_parse(source)
    assert len(result.ast.data_division_subsections) == 1
    sub = result.ast.data_division_subsections[0]
    # The subsection node has only the header span; data-item
    # content is not in this node.
    assert sub.name == "WORKING-STORAGE"
    # The span covers only the header, not the data-item content.
    # The header "WORKING-STORAGE SECTION." is 25 bytes in the
    # source.  Verify the span is roughly that long.
    assert sub.span.end.byte_offset - sub.span.start.byte_offset < 30


# ---------------------------------------------------------------------------
# 10. Existing parser tests still pass (regression)
# ---------------------------------------------------------------------------

def test_r1_existing_move_statement_still_works():
    """A simple MOVE statement that worked before R.1 still works
    after R.1."""
    source = b"MOVE A TO B."
    result = _lex_and_parse(source)
    assert len(result.ast.statements) == 1


def test_r1_existing_if_statement_still_works():
    """A simple IF/ELSE/END-IF that worked before R.1 still works
    after R.1."""
    source = (
        b"IF A > B\n"
        b"MOVE X TO Y\n"
        b"ELSE\n"
        b"MOVE P TO Q\n"
        b"END-IF."
    )
    result = _lex_and_parse(source)
    assert len(result.ast.statements) == 1


# ---------------------------------------------------------------------------
# 11. Existing divisions field is preserved unchanged
# ---------------------------------------------------------------------------

def test_r1_divisions_field_unchanged():
    """The existing ``divisions`` field (read by T-2C-0A) is NOT
    changed by R.1.  It still contains the division-header strings
    in source order."""
    source = (
        b"IDENTIFICATION DIVISION.\n"
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"PROCEDURE DIVISION.\n"
    )
    result = _lex_and_parse(source)
    assert result.ast.divisions == (
        "IDENTIFICATION DIVISION",
        "DATA DIVISION",
        "PROCEDURE DIVISION",
    )


def test_r1_data_division_in_divisions_list():
    """DATA DIVISION appears in the legacy ``divisions`` tuple even
    though the new ``data_division_subsections`` list is also
    populated."""
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n"
    result = _lex_and_parse(source)
    assert "DATA DIVISION" in result.ast.divisions
    assert len(result.ast.data_division_subsections) == 1


# ---------------------------------------------------------------------------
# 12. Determinism
# ---------------------------------------------------------------------------

def test_r1_deterministic_parsing():
    """Repeated parsing of the same source produces byte-identical
    structural output."""
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"LINKAGE SECTION.\n"
    )
    r1 = _lex_and_parse(source)
    r2 = _lex_and_parse(source)
    subs1 = [(s.kind, s.name, s.span.start.byte_offset, s.span.end.byte_offset)
             for s in r1.ast.data_division_subsections]
    subs2 = [(s.kind, s.name, s.span.start.byte_offset, s.span.end.byte_offset)
             for s in r2.ast.data_division_subsections]
    assert subs1 == subs2


# ---------------------------------------------------------------------------
# 13. Source-span correctness
# ---------------------------------------------------------------------------

def test_r1_subsection_span_covers_both_tokens():
    """The DataDivisionSubsection node's span covers both the
    subsection keyword and the SECTION keyword."""
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n"
    result = _lex_and_parse(source)
    sub = result.ast.data_division_subsections[0]
    expected_start = source.index(b"WORKING-STORAGE")
    expected_end = source.index(b"SECTION") + len(b"SECTION")
    assert sub.span.start.byte_offset == expected_start
    assert sub.span.end.byte_offset == expected_end


def test_r1_subsection_span_ignores_trailing_period():
    """The span covers the two tokens (subsection + SECTION) but the
    trailing period is consumed after the span is recorded."""
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n"
    result = _lex_and_parse(source)
    sub = result.ast.data_division_subsections[0]
    # The span end should be at the end of "SECTION", not at the
    # trailing period.
    assert sub.span.end.byte_offset == source.index(b"SECTION") + len(b"SECTION")


# ---------------------------------------------------------------------------
# 14-16. Architecture invariants
# ---------------------------------------------------------------------------

def test_r1_no_v1_imports():
    """The parser R.1 additions must not import from V1."""
    import re as _re

    files = [
        "modernize_v2/parser/nodes.py",
        "modernize_v2/parser/parser.py",
    ]
    for f in files:
        with open(f) as fp:
            content = fp.read()
        for line in content.split("\n"):
            if line.strip().startswith("#"):
                continue
            if "from modernize." in line or "import modernize." in line:
                if "modernize_v2" not in line:
                    raise AssertionError(
                        f"V1 import in {f}: {line.strip()}"
                    )


def test_r1_no_filesystem_io():
    """The parser R.1 additions must not call filesystem I/O."""
    files = [
        "modernize_v2/parser/nodes.py",
        "modernize_v2/parser/parser.py",
    ]
    forbidden = ["open(", "Path(", "os.open", "os.read", "os.write"]
    for f in files:
        with open(f) as fp:
            content = fp.read()
        for line in content.split("\n"):
            if line.strip().startswith("#"):
                continue
            for tok in forbidden:
                if tok in line:
                    raise AssertionError(
                        f"Forbidden I/O {tok!r} in {f}: {line.strip()}"
                    )


def test_r1_no_dict_str_any_in_public_api():
    """R.1's new AST nodes must not use Dict[str, Any]."""
    import dataclasses as _dc

    from modernize_v2.parser import nodes

    # DataDivisionSubsection must have only typed fields.
    flds = _dc.fields(nodes.DataDivisionSubsection)
    for f in flds:
        hint = repr(f.type)
        assert "Dict[str, Any]" not in hint, (
            f"DataDivisionSubsection.{f.name} uses Dict[str, Any]: {hint}"
        )

    # CompilationUnit must still have its original fields, plus the
    # new data_division_subsections field.  No field should use
    # Dict[str, Any].
    flds = _dc.fields(nodes.CompilationUnit)
    for f in flds:
        hint = repr(f.type)
        assert "Dict[str, Any]" not in hint, (
            f"CompilationUnit.{f.name} uses Dict[str, Any]: {hint}"
        )


# ---------------------------------------------------------------------------
# 17. Deterministic IDs
# ---------------------------------------------------------------------------

def test_r1_deterministic_subsection_ids():
    """Two parsings of the same source produce identical subsection
    DeterministicIds."""
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n"
    r1 = _lex_and_parse(source)
    r2 = _lex_and_parse(source)
    assert (
        r1.ast.data_division_subsections[0].node_id
        == r2.ast.data_division_subsections[0].node_id
    )


def test_r1_different_subsections_different_ids():
    """Different subsections in the same source have different
    deterministic IDs."""
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"LINKAGE SECTION.\n"
    )
    result = _lex_and_parse(source)
    ids = [s.node_id for s in result.ast.data_division_subsections]
    assert len(set(ids)) == len(ids), "Subsections must have unique IDs"


# ---------------------------------------------------------------------------
# 18. R.1 does not affect T-2C-0A behavior
# ---------------------------------------------------------------------------

def test_r1_t2c0a_scope_graph_still_works():
    """T-2C-0A's scope-graph builder continues to work without
    modification after R.1."""
    from modernize_v2.analysis import build_scope_graph

    source = (
        b"IDENTIFICATION DIVISION.\n"
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"PROCEDURE DIVISION.\n"
        b"MOVE A TO B.\n"
    )
    result = _lex_and_parse(source)
    graph = build_scope_graph(result)
    # The scope graph still sees A and B as references.
    texts = [r.text for r in graph.references]
    assert "A" in texts
    assert "B" in texts


def test_r1_t2c0a_forward_paragraphs_unaffected():
    """T-2C-0A's forward-referenced paragraphs field is unaffected
    by R.1."""
    from modernize_v2.analysis import build_scope_graph

    source = (
        b"PROCEDURE DIVISION.\n"
        b"PERFORM PARA-1.\n"
        b"GO TO PARA-2.\n"
    )
    result = _lex_and_parse(source)
    graph = build_scope_graph(result)
    assert graph.forward_referenced_paragraphs == ("PARA-1", "PARA-2")


# ---------------------------------------------------------------------------
# 19. R.1 does not affect any pre-existing field of CompilationUnit
# ---------------------------------------------------------------------------

def test_r1_preserves_all_existing_compilation_unit_fields():
    """Every pre-existing field of CompilationUnit must remain
    present and unchanged after R.1."""
    from modernize_v2.parser.nodes import CompilationUnit
    import dataclasses as _dc

    # The expected pre-existing fields.
    expected_existing = {
        "node_id",
        "kind",
        "span",
        "divisions",
        "statements",
        "diagnostics",
        "recovery_records",
    }
    flds = {f.name for f in _dc.fields(CompilationUnit)}
    for f in expected_existing:
        assert f in flds, f"Missing pre-existing field: {f!r}"

    # The new field is also present.
    assert "data_division_subsections" in flds


def test_r1_existing_fields_unchanged_default_value():
    """The new field has a default value (empty tuple) so callers
    that don't construct the field explicitly still work."""
    from modernize_v2.parser.nodes import CompilationUnit
    from modernize_v2.ir.ids import id_for_node
    from modernize_v2.ir.diagnostic import SourceSpan, SourcePosition
    from modernize_v2.ir.kinds import IRKind

    # Construct a CompilationUnit without supplying the new field.
    span = SourceSpan(
        canonical_path="x.cbl",
        start=SourcePosition(line=1, column=0, byte_offset=0),
        end=SourcePosition(line=1, column=0, byte_offset=0),
    )
    cu_id = id_for_node(
        kind=IRKind.COMPILATION_UNIT.value,
        canonical_path="x.cbl",
        line=1,
        column=0,
        byte_offset=0,
        ordinal=0,
    )
    cu = CompilationUnit(
        node_id=cu_id,
        kind=IRKind.COMPILATION_UNIT,
        span=span,
        divisions=(),
        statements=(),
        diagnostics=(),
        recovery_records=(),
    )
    # The new field defaults to an empty tuple.
    assert cu.data_division_subsections == ()
    assert isinstance(cu.data_division_subsections, tuple)


# ---------------------------------------------------------------------------
# 20. R.1 only fires when a SECTION. immediately follows
# ---------------------------------------------------------------------------

def test_r1_does_not_match_subsubsection_keyword():
    """If a token like 'WORKING-STORAGE' is not followed by the
    'SECTION' keyword, it falls through to the normal parser
    dispatch and is handled as an unknown token.  R.1 does not
    silently consume tokens that do not form a valid subsection
    header."""
    source = b"DATA DIVISION.\nWORKING-STORAGE.\nPROCEDURE DIVISION.\n"
    result = _lex_and_parse(source)
    # No subsection header was matched (missing SECTION keyword).
    assert result.ast.data_division_subsections == ()
    # The unsupported construct still produces a diagnostic.
    assert len(result.diagnostics) >= 1


# ---------------------------------------------------------------------------
# 21. R.1 does not consume data-item tokens as subsection headers
# ---------------------------------------------------------------------------

def test_r1_does_not_match_pic_as_subsection():
    """The keyword 'PIC' must not be interpreted as a Data Division
    subsection header.  Only the specific five subsections are
    recognized."""
    source = b"DATA DIVISION.\nPIC SECTION.\n"
    result = _lex_and_parse(source)
    # 'PIC' is not a recognized subsection keyword.
    assert result.ast.data_division_subsections == ()


def test_r1_recognized_subsection_keywords_only():
    """R.1 recognizes exactly 5 subsection keywords.  No others."""
    from modernize_v2.parser.parser import _DATA_DIVISION_SECTION_KEYWORDS
    assert _DATA_DIVISION_SECTION_KEYWORDS == frozenset({
        "WORKING-STORAGE",
        "LINKAGE",
        "LOCAL-STORAGE",
        "REPORT",
        "FILE",
    })
