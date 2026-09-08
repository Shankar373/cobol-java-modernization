"""T-2B-04R.2 — Data-item declaration skeleton tests.

These tests verify the T-2B-04R.2 controlled parser-extension
slice: structural recognition of Data Division data-item
declarations (01-49, 66, 77, 78, 88).

R.2 does NOT:
    * resolve identifiers to symbols
    * interpret PIC clauses
    * compute storage layout
    * validate REDEFINES / RENAMES semantics
    * build the semantic DataItem tree
    * construct parent / child hierarchy
    * distinguish elementary items from group items semantically

It ONLY records the declaration boundaries, the level number,
the name, the optional REDEFINES target, and the raw PIC text.
"""

from __future__ import annotations

from modernize_v2.ir.kinds import IRKind
from modernize_v2.lexer import CobolLexer, SourceFormat
from modernize_v2.parser import DataDivisionSubsection, DataItemDeclaration, Parser
from modernize_v2.source import make_source_file


def _lex_and_parse(source: bytes, *, path: str = "test.cbl"):
    sf = make_source_file(path, source)
    lexer = CobolLexer(sf, source, SourceFormat.FREE)
    tokens = lexer.lex()
    parser = Parser(tokens, canonical_path=path)
    return parser.parse()


# ---------------------------------------------------------------------------
# 1-8. Level number recognition
# ---------------------------------------------------------------------------

def test_r2_level_01_recognized():
    """01 declarations produce a DataItemDeclaration with level=1."""
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-A PIC X(10).\n"
    result = _lex_and_parse(source)
    assert len(result.ast.data_items) == 1
    item = result.ast.data_items[0]
    assert item.level == 1
    assert item.name == "WS-A"
    assert item.pic_string == "X(10)"


def test_r2_level_05_recognized():
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n05 WS-NAME PIC X(20).\n"
    result = _lex_and_parse(source)
    assert result.ast.data_items[0].level == 5


def test_r2_level_10_recognized():
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n10 ITEM-10 PIC 9(5).\n"
    result = _lex_and_parse(source)
    assert result.ast.data_items[0].level == 10


def test_r2_level_49_recognized():
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n49 ITEM-49 PIC 9(5).\n"
    result = _lex_and_parse(source)
    assert result.ast.data_items[0].level == 49


def test_r2_level_66_recognized():
    """66-level RENAMES is recognized syntactically."""
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-A PIC X(10).\n"
        b"66 WS-RENAMED RENAMES WS-A.\n"
    )
    result = _lex_and_parse(source)
    assert len(result.ast.data_items) == 2
    renamed = result.ast.data_items[1]
    assert renamed.level == 66
    assert renamed.name == "WS-RENAMED"
    assert renamed.redefines_target == "WS-A"


def test_r2_level_77_recognized():
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n77 WS-FLAG PIC X.\n"
    result = _lex_and_parse(source)
    assert result.ast.data_items[0].level == 77


def test_r2_level_78_recognized():
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n78 WS-CONST PIC 9(5).\n"
    result = _lex_and_parse(source)
    assert result.ast.data_items[0].level == 78


def test_r2_level_88_recognized():
    """88-level condition name has kind=LEVEL_88_ITEM."""
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-FLAG PIC X.\n"
        b"88 WS-VALID VALUE 'Y'.\n"
    )
    result = _lex_and_parse(source)
    assert len(result.ast.data_items) == 2
    cond = result.ast.data_items[1]
    assert cond.level == 88
    assert cond.kind == IRKind.LEVEL_88_ITEM
    assert cond.name == "WS-VALID"


# ---------------------------------------------------------------------------
# 9. Declaration name captured
# ---------------------------------------------------------------------------

def test_r2_name_captured_verbatim():
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-A PIC X(10).\n"
    result = _lex_and_parse(source)
    assert result.ast.data_items[0].name == "WS-A"


def test_r2_name_with_hyphens_preserved():
    """Names with hyphens (COBOL convention) are preserved verbatim."""
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-CUSTOMER-NAME PIC X(30).\n"
    )
    result = _lex_and_parse(source)
    assert result.ast.data_items[0].name == "WS-CUSTOMER-NAME"


# ---------------------------------------------------------------------------
# 10. REDEFINES target captured
# ---------------------------------------------------------------------------

def test_r2_redefines_target_captured():
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-A PIC X(10).\n"
        b"01 WS-B REDEFINES WS-A PIC X(20).\n"
    )
    result = _lex_and_parse(source)
    assert len(result.ast.data_items) == 2
    redefined = result.ast.data_items[1]
    assert redefined.name == "WS-B"
    assert redefined.redefines_target == "WS-A"
    assert redefined.pic_string == "X(20)"


def test_r2_no_redefines_when_absent():
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-A PIC X(10).\n"
    result = _lex_and_parse(source)
    assert result.ast.data_items[0].redefines_target is None


# ---------------------------------------------------------------------------
# 11. PIC raw text captured
# ---------------------------------------------------------------------------

def test_r2_pic_string_captured_verbatim():
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-A PIC X(10).\n"
    result = _lex_and_parse(source)
    assert result.ast.data_items[0].pic_string == "X(10)"


def test_r2_pic_string_9_5():
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-NUM PIC 9(5).\n"
    result = _lex_and_parse(source)
    assert result.ast.data_items[0].pic_string == "9(5)"


def test_r2_pic_string_77():
    """77-level items can have a single-character PIC."""
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n77 WS-FLAG PIC X.\n"
    result = _lex_and_parse(source)
    assert result.ast.data_items[0].pic_string == "X"


def test_r2_no_pic_clause_records_none():
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-A.\n"
    )
    result = _lex_and_parse(source)
    assert result.ast.data_items[0].pic_string is None


# ---------------------------------------------------------------------------
# 12. Declaration ordering preserved
# ---------------------------------------------------------------------------

def test_r2_declaration_order_preserved():
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-A PIC X(10).\n"
        b"05 WS-B PIC X(5).\n"
        b"10 WS-C PIC 9(3).\n"
    )
    result = _lex_and_parse(source)
    levels = [di.level for di in result.ast.data_items]
    assert levels == [1, 5, 10]
    names = [di.name for di in result.ast.data_items]
    assert names == ["WS-A", "WS-B", "WS-C"]


# ---------------------------------------------------------------------------
# 13. Multiple declarations
# ---------------------------------------------------------------------------

def test_r2_multiple_declarations():
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-A PIC X(10).\n"
        b"01 WS-B PIC X(20).\n"
        b"01 WS-C PIC 9(5).\n"
    )
    result = _lex_and_parse(source)
    assert len(result.ast.data_items) == 3
    assert [di.name for di in result.ast.data_items] == ["WS-A", "WS-B", "WS-C"]


# ---------------------------------------------------------------------------
# 14. Declarations across multiple subsections
# ---------------------------------------------------------------------------

def test_r2_declarations_across_multiple_subsections():
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-A PIC X(10).\n"
        b"LINKAGE SECTION.\n"
        b"01 LK-A PIC X(5).\n"
    )
    result = _lex_and_parse(source)
    assert len(result.ast.data_items) == 2
    assert [di.name for di in result.ast.data_items] == ["WS-A", "LK-A"]
    # Subsection order is preserved.
    assert [s.name for s in result.ast.data_division_subsections] == [
        "WORKING-STORAGE",
        "LINKAGE",
    ]


# ---------------------------------------------------------------------------
# 15. No declarations in Procedure Division
# ---------------------------------------------------------------------------

def test_r2_no_declarations_in_procedure_division():
    source = b"PROCEDURE DIVISION.\n01 WS-A PIC X(10).\nMOVE A TO B.\n"
    result = _lex_and_parse(source)
    # No data items should be created because we're not in a
    # Data Division subsection.
    assert result.ast.data_items == ()


def test_r2_01_after_procedure_division_not_a_declaration():
    """After PROCEDURE DIVISION, a '01' token is not a data-item
    declaration; it's a normal token handled by the procedure-
    division dispatch."""
    source = b"MOVE 01 TO 02."
    result = _lex_and_parse(source)
    assert result.ast.data_items == ()


# ---------------------------------------------------------------------------
# 16. No fake declarations from unrelated numeric literals
# ---------------------------------------------------------------------------

def test_r2_no_fake_declarations_from_literals():
    """Numeric tokens outside the data-division-subsection context
    are not treated as data-item declarations."""
    source = b"COMPUTE X = 01 + 02.\n"
    result = _lex_and_parse(source)
    assert result.ast.data_items == ()


# ---------------------------------------------------------------------------
# 17. Existing R.1 subsection recognition still works
# ---------------------------------------------------------------------------

def test_r2_subsection_headers_still_recognized():
    """R.2 preserves R.1's Data Division subsection recognition."""
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-A PIC X(10).\n"
    )
    result = _lex_and_parse(source)
    assert len(result.ast.data_division_subsections) == 1
    assert result.ast.data_division_subsections[0].name == "WORKING-STORAGE"


# ---------------------------------------------------------------------------
# 18-19. Existing statement tests still work
# ---------------------------------------------------------------------------

def test_r2_existing_move_still_works():
    source = b"MOVE A TO B."
    result = _lex_and_parse(source)
    assert len(result.ast.statements) == 1


def test_r2_existing_if_still_works():
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
# 20-21. Pre-existing fields unchanged
# ---------------------------------------------------------------------------

def test_r2_divisions_field_unchanged():
    """The pre-existing divisions field is preserved unchanged."""
    source = (
        b"IDENTIFICATION DIVISION.\n"
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-A PIC X(10).\n"
        b"PROCEDURE DIVISION.\n"
    )
    result = _lex_and_parse(source)
    assert result.ast.divisions == (
        "IDENTIFICATION DIVISION",
        "DATA DIVISION",
        "PROCEDURE DIVISION",
    )


def test_r2_statements_field_unchanged():
    source = b"MOVE A TO B."
    result = _lex_and_parse(source)
    assert len(result.ast.statements) == 1


# ---------------------------------------------------------------------------
# 22-23. Determinism
# ---------------------------------------------------------------------------

def test_r2_deterministic_ids():
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-A PIC X(10).\n"
    r1 = _lex_and_parse(source)
    r2 = _lex_and_parse(source)
    assert r1.ast.data_items[0].node_id == r2.ast.data_items[0].node_id


def test_r2_deterministic_repeated_parsing():
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-A PIC X(10).\n"
        b"01 WS-B PIC X(5).\n"
    )
    r1 = _lex_and_parse(source)
    r2 = _lex_and_parse(source)
    fields1 = [(di.level, di.name, di.redefines_target, di.pic_string,
                di.span.start.byte_offset, di.span.end.byte_offset,
                di.node_id.text) for di in r1.ast.data_items]
    fields2 = [(di.level, di.name, di.redefines_target, di.pic_string,
                di.span.start.byte_offset, di.span.end.byte_offset,
                di.node_id.text) for di in r2.ast.data_items]
    assert fields1 == fields2


# ---------------------------------------------------------------------------
# 24. Source span correctness
# ---------------------------------------------------------------------------

def test_r2_span_covers_full_declaration():
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-A PIC X(10).\n"
    result = _lex_and_parse(source)
    item = result.ast.data_items[0]
    # The span starts at the level number and ends at the period
    # of the data-item declaration (the third period, after PIC).
    expected_start = source.index(b"01")
    # The period of the data-item declaration is the one that
    # follows ``X(10)`` (not the one after DATA DIVISION or after
    # WORKING-STORAGE SECTION).
    expected_end = source.rindex(b".") + 1
    assert item.span.start.byte_offset == expected_start
    assert item.span.end.byte_offset == expected_end


# ---------------------------------------------------------------------------
# 25-27. Architecture invariants
# ---------------------------------------------------------------------------

def test_r2_no_v1_imports():
    import re
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


def test_r2_no_filesystem_io():
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


def test_r2_no_dict_str_any_in_public_api():
    import dataclasses

    from modernize_v2.parser.nodes import (
        CompilationUnit,
        DataItemDeclaration,
        DataDivisionSubsection,
    )

    for cls in (DataItemDeclaration, DataDivisionSubsection, CompilationUnit):
        for f in dataclasses.fields(cls):
            hint = repr(f.type)
            assert "Dict[str, Any]" not in hint, (
                f"{cls.__name__}.{f.name} uses Dict[str, Any]: {hint}"
            )


# ---------------------------------------------------------------------------
# 28. T-2C-0A regression
# ---------------------------------------------------------------------------

def test_r2_t2c0a_scope_graph_still_works():
    """T-2C-0A's scope-graph builder still works after R.2."""
    from modernize_v2.analysis import build_scope_graph

    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-A PIC X(10).\n"
        b"PROCEDURE DIVISION.\n"
        b"MOVE WS-A TO WS-B.\n"
    )
    result = _lex_and_parse(source)
    graph = build_scope_graph(result)
    # The Procedure Division identifiers are still tracked as
    # references by the scope graph.
    texts = [r.text for r in graph.references]
    assert "WS-A" in texts
    assert "WS-B" in texts


# ---------------------------------------------------------------------------
# 29. Recovery: malformed declaration
# ---------------------------------------------------------------------------

def test_r2_malformed_declaration_falls_through():
    """A declaration with no name (level number followed by an
    immediately-period-only sequence, with the lexer producing
    no name token) does NOT create a DataItemDeclaration.  This
    verifies that the parser bails out gracefully when a name
    is missing.

    The lexer treats ``PERIOD`` as an identifier (it tokenizes
    ``.`` as a separate PERIOD token), so the test uses a
    construct that forces no name to be present: a level number
    followed by VALUE (a keyword) without a name first.
    """
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 VALUE 'X'.\n"
    )
    result = _lex_and_parse(source)
    # The parser bails out because there is no identifier after
    # the level number.  The '01' token falls through to the
    # normal unknown-token dispatch and the data-items list
    # is empty.
    assert result.ast.data_items == ()


# ---------------------------------------------------------------------------
# 30. Declaration without PIC remains structurally recoverable
# ---------------------------------------------------------------------------

def test_r2_declaration_without_pic_creates_node():
    """A syntactically valid declaration without a PIC clause is
    still represented as a DataItemDeclaration (with pic_string
    = None)."""
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-A.\n"
    result = _lex_and_parse(source)
    assert len(result.ast.data_items) == 1
    assert result.ast.data_items[0].name == "WS-A"
    assert result.ast.data_items[0].pic_string is None
    assert result.ast.data_items[0].level == 1


# ---------------------------------------------------------------------------
# R.2 does NOT create semantic DataItem trees
# ---------------------------------------------------------------------------

def test_r2_does_not_create_semantic_dataitem():
    """R.2 does NOT build a semantic DataItem tree with hierarchy,
    types, layout, or relationships.  It only creates flat
    syntactic DataItemDeclaration nodes in source order."""
    from modernize_v2.parser.nodes import CompilationUnit, DataItemDeclaration

    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-A PIC X(10).\n"
        b"05 WS-B PIC X(5).\n"
    )
    result = _lex_and_parse(source)
    # Verify the type of the parsed objects.
    for di in result.ast.data_items:
        assert isinstance(di, DataItemDeclaration)
        # No hierarchy field (no parent / child relationship).
        for f in di.__dataclass_fields__:
            assert f not in ("parent", "children", "level_88_value"), (
                f"R.2 must not create hierarchy in {f!r}"
            )
        # No type / layout fields.
        for f in di.__dataclass_fields__:
            assert f not in ("type", "java_type_ref", "layout"), (
                f"R.2 must not create type/layout in {f!r}"
            )
