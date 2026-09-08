"""T-2B-04R.4 — OCCURS / ODO / level-88 structural clause tests.

These tests verify the T-2B-04R.4 controlled parser-extension slice:
structured recognition of the OCCURS clause (fixed-count and range
forms, optional TIMES), the OCCURS DEPENDING ON (ODO) clause, and
level-88 condition-name declarations within data-item declarations.

R.4 does NOT:
    * resolve OCCURS counts or DEPENDING ON names to symbols
    * validate OCCURS bounds (positive counts, lower <= upper, etc.)
    * bind the DEPENDING ON identifier to an indexed object
    * compute storage layout / array sizes
    * interpret the VALUE clause of a condition name
    * build the semantic DataItem tree
    * introduce new IR vocabulary (``OCCURS_CLAUSE``, ``ODO_CLAUSE``,
      and ``LEVEL_88_ITEM`` already exist as IRKinds)

It ONLY records the structural form of these clauses alongside the
R.2/R.3 representation, and reparses malformed OCCURS / ODO /
level-88 syntax into PARSER_RECOVERY diagnostics instead of silently
swallowing it.

Type change: ``CompilationUnit.data_items`` is now
``Tuple[Union[DataItemDeclaration, Level88Declaration], ...]``.
``Level88Declaration`` lives in the same source-ordered flat list,
mirroring the R.2 behaviour asserted by
``test_r2_level_88_recognized``.
"""

from __future__ import annotations

import pytest

from modernize_v2.ir.kinds import IRKind, is_data_item_kind
from modernize_v2.lexer import CobolLexer, SourceFormat
from modernize_v2.parser import (
    DataItemDeclaration,
    Level88Declaration,
    OccursClause,
    OdoClause,
    Parser,
)
from modernize_v2.source import make_source_file


def _lex_and_parse(source: bytes, *, path: str = "test.cbl"):
    sf = make_source_file(path, source)
    lexer = CobolLexer(sf, source, SourceFormat.FREE)
    tokens = lexer.lex()
    parser = Parser(tokens, canonical_path=path)
    return parser.parse()


# ---------------------------------------------------------------------------
# 1-8. OCCURS clause tests
# ---------------------------------------------------------------------------

def test_r4_occurs_fixed_times_recognized():
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-T OCCURS 10 TIMES.\n"
    )
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    assert di.occurs_clause is not None
    oc = di.occurs_clause
    assert isinstance(oc, OccursClause)
    assert oc.kind == IRKind.OCCURS_CLAUSE
    assert oc.occurs == 10
    assert oc.lower_bound is None
    assert oc.upper_bound is None
    assert di.odo_clause is None


def test_r4_occurs_range_recognized():
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-T OCCURS 1 TO 10 TIMES.\n"
    )
    result = _lex_and_parse(source)
    oc = result.ast.data_items[0].occurs_clause
    assert oc is not None
    assert oc.occurs is None
    assert oc.lower_bound == 1
    assert oc.upper_bound == 10


def test_r4_occurs_fixed_and_range_forms_are_exclusive():
    """Exactly one form is populated: either ``occurs`` (fixed count)
    or ``lower_bound``/``upper_bound`` (range)."""
    fixed = _lex_and_parse(
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-T OCCURS 10 TIMES.\n"
    ).ast.data_items[0].occurs_clause
    rng = _lex_and_parse(
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-T OCCURS 1 TO 10 TIMES.\n"
    ).ast.data_items[0].occurs_clause
    assert fixed.occurs == 10
    assert fixed.lower_bound is None and fixed.upper_bound is None
    assert rng.occurs is None
    assert rng.lower_bound == 1 and rng.upper_bound == 10


def test_r4_occurs_times_is_optional():
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-T OCCURS 10.\n"
    )
    result = _lex_and_parse(source)
    oc = result.ast.data_items[0].occurs_clause
    assert oc is not None
    assert oc.occurs == 10
    assert result.ast.diagnostics == ()


def test_r4_occurs_without_clause_is_absent():
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-T PIC X(10).\n"
    )
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    assert di.occurs_clause is None
    assert di.odo_clause is None


def test_r4_occurs_combined_with_pic_any_order():
    """OCCURS may appear before or after PIC in the clause stream."""
    ordered = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-T PIC X OCCURS 10 TIMES.\n"
    )
    reversed_ = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-T OCCURS 10 TIMES PIC X.\n"
    )
    for src in (ordered, reversed_):
        result = _lex_and_parse(src)
        di = result.ast.data_items[0]
        assert di.pic_clause is not None
        assert di.occurs_clause is not None
        assert di.occurs_clause.occurs == 10
        assert result.ast.diagnostics == ()


def test_r4_occurs_combined_with_usage():
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-T OCCURS 10 TIMES USAGE IS COMP-3.\n"
    )
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    assert di.occurs_clause is not None
    assert di.usage_clause is not None
    assert di.odo_clause is None
    assert result.ast.diagnostics == ()


def test_r4_occurs_combined_with_value():
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-T OCCURS 10 TIMES VALUE 0.\n"
    )
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    assert di.occurs_clause is not None
    assert di.value_clause is not None
    assert result.ast.diagnostics == ()


# ---------------------------------------------------------------------------
# 9-14. ODO (OCCURS DEPENDING ON) tests
# ---------------------------------------------------------------------------

def test_r4_odo_recognized():
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-T OCCURS 10 TIMES DEPENDING ON WS-COUNT.\n"
    )
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    od = di.odo_clause
    assert isinstance(od, OdoClause)
    assert od.kind == IRKind.ODO_CLAUSE
    assert od.identifier == "WS-COUNT"
    assert di.occurs_clause is not None
    assert di.occurs_clause.occurs == 10
    assert result.ast.diagnostics == ()


def test_r4_odo_identifier_is_verbatim():
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-T OCCURS 10 TIMES DEPENDING ON WS-COUNT.\n"
    )
    result = _lex_and_parse(source)
    od = result.ast.data_items[0].odo_clause
    assert od.identifier == "WS-COUNT"
    # R.4 does NOT resolve the identifier to anything: it is verbatim
    # text shaped like a COBOL user word (starts with a letter).
    assert od.identifier
    assert od.identifier[0].isalpha()
    assert " " not in od.identifier


def test_r4_odo_requires_occurs():
    """An ODO clause is only ever produced inside a valid OCCURS
    clause; it is never attached to a bare declaration."""
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-T PIC X.\n"
    )
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    assert di.odo_clause is None


def test_r4_range_occurs_with_odo():
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-T OCCURS 1 TO 10 TIMES DEPENDING ON WS-CNT.\n"
    )
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    oc = di.occurs_clause
    od = di.odo_clause
    assert oc.lower_bound == 1
    assert oc.upper_bound == 10
    assert od.identifier == "WS-CNT"
    assert result.ast.diagnostics == ()


def test_r4_odo_lower_case_sensitive_words():
    """DEPENDING ON is case-insensitive; the identifier is preserved
    verbatim."""
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 ws-t OCCURS 5 TIMES depending on ws-count.\n"
    )
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    assert di.occurs_clause is not None
    assert di.odo_clause.identifier == "ws-count"
    assert result.ast.diagnostics == ()


def test_r4_odo_syntactic_target_only():
    """The DEPENDING ON identifier is stored as raw text; no symbol
    resolution, data-item lookup, or bound validation is performed."""
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-T OCCURS 10 TIMES DEPENDING ON NO-SUCH-ITEM.\n"
    )
    result = _lex_and_parse(source)
    od = result.ast.data_items[0].odo_clause
    assert od.identifier == "NO-SUCH-ITEM"
    assert result.ast.diagnostics == ()


# ---------------------------------------------------------------------------
# 15-17. Spans
# ---------------------------------------------------------------------------

def test_r4_occurs_span_exact():
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-T OCCURS 10 TIMES.\n"
    )
    result = _lex_and_parse(source)
    oc = result.ast.data_items[0].occurs_clause
    start = source.find(b"OCCURS 10 TIMES")
    end = start + len(b"OCCURS 10 TIMES")
    assert oc.span.start.byte_offset == start
    assert oc.span.end.byte_offset == end


def test_r4_range_occurs_span_exact():
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-T OCCURS 1 TO 10 TIMES.\n"
    )
    result = _lex_and_parse(source)
    oc = result.ast.data_items[0].occurs_clause
    start = source.find(b"OCCURS 1 TO 10 TIMES")
    end = start + len(b"OCCURS 1 TO 10 TIMES")
    assert oc.span.start.byte_offset == start
    assert oc.span.end.byte_offset == end


def test_r4_odo_span_exact_and_exclusive_of_occurs():
    """The OdoClause span covers ``DEPENDING ON <name>`` only; OCCURS
    text is excluded (the clauses are stored as siblings, per the T4R
    §5.1 structural design)."""
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-T OCCURS 10 TIMES DEPENDING ON WS-COUNT.\n"
    )
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    oc = di.occurs_clause
    od = di.odo_clause
    occ_start = source.find(b"OCCURS 10 TIMES")
    dep_start = source.find(b"DEPENDING ON WS-COUNT")
    dep_end = dep_start + len(b"DEPENDING ON WS-COUNT")
    assert oc.span.start.byte_offset == occ_start
    assert oc.span.end.byte_offset == occ_start + len(b"OCCURS 10 TIMES")
    assert od.span.start.byte_offset == dep_start
    assert od.span.end.byte_offset == dep_end


def test_r4_data_item_span_covers_declaration():
    """The DataItemDeclaration span still covers the whole declaration
    including OCCURS and ODO clauses."""
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-T OCCURS 10 TIMES DEPENDING ON WS-COUNT.\n"
    )
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    start = source.find(b"01 WS-T")
    # The item span extends through the trailing period (R.2
    # behaviour: end is the byte after the final consumed token).
    end = source.find(b"WS-COUNT.") + len(b"WS-COUNT.")
    assert di.span.start.byte_offset == start
    assert di.span.end.byte_offset == end


# ---------------------------------------------------------------------------
# 18-23. Level-88 / condition name tests
# ---------------------------------------------------------------------------

def test_r4_level88_dedicated_node():
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-FLAG PIC X.\n"
        b"88 WS-VALID VALUE 'Y'.\n"
    )
    result = _lex_and_parse(source)
    assert len(result.ast.data_items) == 2
    item = result.ast.data_items[1]
    assert isinstance(item, Level88Declaration)
    assert not isinstance(item, DataItemDeclaration)
    assert item.level == 88
    assert item.kind == IRKind.LEVEL_88_ITEM
    assert item.name == "WS-VALID"
    assert item.value_clause is not None
    assert item.value_clause.literal_value == "Y"
    assert result.ast.diagnostics == ()


def test_r4_level88_stays_in_source_ordered_flat_list():
    """Level-88 nodes remain in the same source-ordered ``data_items``
    tuple the R.2 ``test_r2_level_88_recognized`` expects; no separate
    collection is introduced."""
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-A PIC X.\n"
        b"05 WS-B PIC 9.\n"
        b"88 WS-B-OK VALUE 1.\n"
        b"88 WS-B-ERR VALUES 0, 2.\n"
        b"77 WS-C PIC X.\n"
    )
    result = _lex_and_parse(source)
    names = [d.name for d in result.ast.data_items]
    assert names == ["WS-A", "WS-B", "WS-B-OK", "WS-B-ERR", "WS-C"]
    assert isinstance(result.ast.data_items[2], Level88Declaration)
    assert isinstance(result.ast.data_items[3], Level88Declaration)
    assert isinstance(result.ast.data_items[4], DataItemDeclaration)


def test_r4_level88_multiple_condition_names():
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-RESP PIC 9(4).\n"
        b"88 WS-OK VALUE 0.\n"
        b"88 WS-NOTFOUND VALUE 12.\n"
        b"88 WS-BAD VALUE 9.\n"
    )
    result = _lex_and_parse(source)
    conds = result.ast.data_items[1:]
    assert len(conds) == 3
    assert all(isinstance(c, Level88Declaration) for c in conds)
    assert [c.name for c in conds] == ["WS-OK", "WS-NOTFOUND", "WS-BAD"]
    assert all(c.value_clause is not None for c in conds)
    assert result.ast.diagnostics == ()


def test_r4_level88_no_parent_child_structuring():
    """R.4 creates NO hierarchy: level-88 nodes are sibling nodes in
    the flat source-ordered list (hierarchy is a T-2B-05 concern)."""
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-A PIC X.\n"
        b"88 WS-ON VALUE 1.\n"
    )
    result = _lex_and_parse(source)
    for name in dir(result.ast.data_items[0]):
        assert "parent" not in name and "child" not in name, name
    assert isinstance(result.ast.data_items[1], Level88Declaration)


def test_r4_level88_empty_data_items_still_flat():
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
    )
    result = _lex_and_parse(source)
    assert result.ast.data_items == ()


def test_r4_compilation_unit_type_annotation_mentions_level88():
    """The ``data_items`` field type is a Union of the data-item and
    level-88 declarations."""
    import dataclasses
    from modernize_v2.parser import CompilationUnit
    fields = {f.name: f for f in dataclasses.fields(CompilationUnit)}
    hint = repr(fields["data_items"].type)
    assert "Level88Declaration" in hint
    assert "DataItemDeclaration" in hint


# ---------------------------------------------------------------------------
# 24-30. Recovery: malformed OCCURS / ODO / level-88
# ---------------------------------------------------------------------------

def test_r4_malformed_occurs_missing_count():
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"05 WS-X OCCURS.\n"
    )
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    assert di.occurs_clause is None
    assert di.odo_clause is None
    assert len(result.diagnostics) >= 1
    assert any(
        d.message == "OCCURS: missing integer count"
        for d in result.diagnostics
    )


def test_r4_malformed_occurs_range_missing_upper():
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"05 WS-X OCCURS 10 TO.\n"
    )
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    # Recovered as a fixed count.
    assert di.occurs_clause is not None
    assert di.occurs_clause.occurs == 10
    assert any(
        d.message == "OCCURS: range requires an upper count after TO"
        for d in result.diagnostics
    )


def test_r4_malformed_occurs_lower_bound_missing():
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"05 WS-X OCCURS TO 10 TIMES.\n"
    )
    result = _lex_and_parse(source)
    # ``TO 10 TIMES`` is not a valid fixed count, so OCCURS is
    # malformed (missing integer count) and the remainder is
    # dispatched normally.
    assert result.ast.data_items[0].occurs_clause is None
    assert len(result.diagnostics) >= 1


def test_r4_malformed_odo_depending_without_on():
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"05 WS-X OCCURS 10 TIMES DEPENDING WS-C.\n"
    )
    result = _lex_and_parse(source)
    assert result.ast.data_items[0].occurs_clause is not None
    assert result.ast.data_items[0].odo_clause is None
    assert any(
        d.message == "OCCURS: DEPENDING must be followed by ON"
        for d in result.diagnostics
    )


def test_r4_malformed_odo_on_without_identifier():
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"05 WS-X OCCURS 10 TIMES DEPENDING ON.\n"
    )
    result = _lex_and_parse(source)
    assert result.ast.data_items[0].occurs_clause is not None
    assert result.ast.data_items[0].odo_clause is None
    assert any(
        d.message == "OCCURS: DEPENDING ON requires an identifier"
        for d in result.diagnostics
    )


def test_r4_malformed_level88_missing_value():
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-X PIC X.\n"
        b"88 WS-COND.\n"
    )
    result = _lex_and_parse(source)
    assert len(result.ast.data_items) == 2
    cond = result.ast.data_items[1]
    assert isinstance(cond, Level88Declaration)
    assert cond.value_clause is None
    assert any(
        "missing VALUE clause" in d.message for d in result.diagnostics
    )


def test_r4_level88_with_forbidden_clause_diag():
    """Only a VALUE clause is valid on a condition name; OCCURS / PIC
    are diagnosed (R.4 does not silently drop them)."""
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-X PIC X.\n"
        b"88 WS-COND PIC 9.\n"
    )
    result = _lex_and_parse(source)
    cond = result.ast.data_items[1]
    assert isinstance(cond, Level88Declaration)
    assert cond.value_clause is None
    assert any(
        "only a VALUE clause is valid" in d.message
        for d in result.diagnostics
    )


def test_r4_malformed_does_not_swallow_unknown_tokens():
    """Diagnostics for OCCURS grammar errors fall through to normal
    parser dispatch and are all reported; nothing is swallowed."""
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"05 WS-X OCCURS TO 10 TIMES.\n"
    )
    result = _lex_and_parse(source)
    messages = [d.message for d in result.diagnostics]
    assert any("missing integer count" in m for m in messages)
    assert any("'TO'" in m for m in messages)


def test_r4_valid_declarations_suppress_no_diagnostics():
    """A fully-recognized R.4 declaration (OCCURS + ODO + 88) yields
    zero parser diagnostics."""
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-TABLE OCCURS 1 TO 20 TIMES DEPENDING ON WS-COUNT.\n"
        b"   05 WS-ROW PIC X.\n"
        b"88 WS-DONE VALUE 'D'.\n"
    )
    result = _lex_and_parse(source)
    assert result.ast.diagnostics == ()
    assert len(result.ast.data_items) == 3


# ---------------------------------------------------------------------------
# 31-34. Determinism
# ---------------------------------------------------------------------------

def test_r4_deterministic_occurs_and_odo_ids():
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-T OCCURS 1 TO 10 TIMES DEPENDING ON WS-COUNT.\n"
    )
    r1 = _lex_and_parse(source)
    r2 = _lex_and_parse(source)
    d1 = r1.ast.data_items[0]
    d2 = r2.ast.data_items[0]
    assert d1.occurs_clause.node_id == d2.occurs_clause.node_id
    assert d1.odo_clause.node_id == d2.odo_clause.node_id
    assert d1.occurs_clause.span == d2.occurs_clause.span
    assert d1.odo_clause.span == d2.odo_clause.span


def test_r4_deterministic_level88_nodes():
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-X PIC X.\n"
        b"88 WS-OK VALUE 0.\n"
    )
    r1 = _lex_and_parse(source)
    r2 = _lex_and_parse(source)
    c1 = r1.ast.data_items[1]
    c2 = r2.ast.data_items[1]
    assert (c1.level, c1.name, c1.node_id, c1.span, c1.kind) == (
        c2.level, c2.name, c2.node_id, c2.span, c2.kind,
    )
    assert c1.value_clause.node_id == c2.value_clause.node_id


def test_r4_deterministic_repeated_parsing():
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-T OCCURS 10 TIMES DEPENDING ON WS-CNT.\n"
    )
    r1 = _lex_and_parse(source)
    r2 = _lex_and_parse(source)
    fields1 = (
        r1.ast.data_items[0].level,
        r1.ast.data_items[0].name,
        r1.ast.data_items[0].occurs_clause.occurs,
        r1.ast.data_items[0].odo_clause.identifier,
    )
    fields2 = (
        r2.ast.data_items[0].level,
        r2.ast.data_items[0].name,
        r2.ast.data_items[0].occurs_clause.occurs,
        r2.ast.data_items[0].odo_clause.identifier,
    )
    assert fields1 == fields2


def test_r4_two_parser_instances_identical_clause_state():
    """Two independent Parser instances over the same source produce
    byte-identical OCCURS / ODO / level-88 triples."""
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-T OCCURS 5 TIMES DEPENDING ON WS-CNT.\n"
        b"88 WS-LOW VALUE 1 THRU 3.\n"
    )
    sf = make_source_file("test.cbl", source)
    lexer1 = CobolLexer(sf, source, SourceFormat.FREE)
    lexer2 = CobolLexer(sf, source, SourceFormat.FREE)
    p1 = Parser(lexer1.lex(), canonical_path="test.cbl")
    p2 = Parser(lexer2.lex(), canonical_path="test.cbl")
    r1 = p1.parse()
    r2 = p2.parse()

    def state(r):
        out = []
        for d in r.ast.data_items:
            oc = d.occurs_clause if hasattr(d, "occurs_clause") else None
            od = d.odo_clause if hasattr(d, "odo_clause") else None
            out.append((
                d.node_id,
                d.level,
                d.name,
                d.span.start.byte_offset,
                d.span.end.byte_offset,
                (
                    oc.node_id, oc.span.start.byte_offset,
                    oc.span.end.byte_offset, oc.occurs,
                    oc.lower_bound, oc.upper_bound,
                ) if oc is not None else None,
                (
                    od.node_id, od.span.start.byte_offset,
                    od.span.end.byte_offset, od.identifier,
                ) if od is not None else None,
            ))
        return out

    assert state(r1) == state(r2)
    assert len(r1.diagnostics) == len(r2.diagnostics)


# ---------------------------------------------------------------------------
# 35-39. Architecture invariants
# ---------------------------------------------------------------------------

def test_r4_new_nodes_are_frozen():
    from dataclasses import FrozenInstanceError, is_dataclass

    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-T OCCURS 10 TIMES DEPENDING ON WS-CNT.\n"
        b"88 WS-OK VALUE 0.\n"
    )
    result = _lex_and_parse(source)
    nodes = [
        result.ast.data_items[0].occurs_clause,
        result.ast.data_items[0].odo_clause,
        result.ast.data_items[1],
    ]
    for node in nodes:
        assert is_dataclass(node)
        with pytest.raises(FrozenInstanceError):
            node.node_id = "MUTATED"


def test_r4_new_nodes_reuse_existing_kinds():
    """R.4 adds NO new IR vocabulary: the new nodes are built from the
    pre-existing ``OCCURS_CLAUSE`` / ``ODO_CLAUSE`` / ``LEVEL_88_ITEM``
    enum members."""
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-T OCCURS 10 TIMES DEPENDING ON WS-CNT.\n"
        b"88 WS-OK VALUE 0.\n"
    )
    result = _lex_and_parse(source)
    d0 = result.ast.data_items[0]
    assert d0.occurs_clause.kind is IRKind.OCCURS_CLAUSE
    assert d0.odo_clause.kind is IRKind.ODO_CLAUSE
    assert result.ast.data_items[1].kind is IRKind.LEVEL_88_ITEM


def test_r4_data_item_kind_vocabulary_unchanged():
    """The DATA_ITEM category still contains exactly the baseline set
    of kinds (R.3's PIC/USAGE/VALUE added previously, none by R.4)."""
    from modernize_v2.ir.kinds import DATA_ITEM_KINDS

    expected = frozenset({
        IRKind.DATA_ITEM,
        IRKind.GROUP_ITEM,
        IRKind.ELEMENTARY_ITEM,
        IRKind.LEVEL_88_ITEM,
        IRKind.OCCURS_CLAUSE,
        IRKind.ODO_CLAUSE,
        IRKind.REDEFINES_CLAUSE,
        IRKind.RENAMES_CLAUSE,
        IRKind.PIC_CLAUSE,
        IRKind.USAGE_CLAUSE,
        IRKind.VALUE_CLAUSE,
    })
    assert DATA_ITEM_KINDS == expected


def test_r4_occurs_kinds_are_data_item_kinds():
    assert is_data_item_kind(IRKind.OCCURS_CLAUSE)
    assert is_data_item_kind(IRKind.ODO_CLAUSE)
    assert is_data_item_kind(IRKind.LEVEL_88_ITEM)


def test_r4_no_dict_str_any_in_public_api():
    import dataclasses

    for cls in (
        OccursClause,
        OdoClause,
        Level88Declaration,
        DataItemDeclaration,
    ):
        for f in dataclasses.fields(cls):
            hint = repr(f.type)
            assert "Dict[str, Any]" not in hint, (
                f"{cls.__name__}.{f.name} uses Dict[str, Any]"
            )


def test_r4_no_v1_imports():
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


def test_r4_no_filesystem_io():
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


def test_r4_no_semantic_dataitem_creation():
    """R.4 does NOT create a semantic DataItem tree."""
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-T OCCURS 10 TIMES DEPENDING ON WS-CNT.\n"
    )
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    for f in di.__dataclass_fields__:
        assert f not in (
            "storage_size", "java_type", "encoding", "byte_length",
        ), f"R.4 must not create semantic field {f!r}"


def test_r4_no_layout_computation():
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-T OCCURS 10 TIMES DEPENDING ON WS-CNT.\n"
    )
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    for f in di.__dataclass_fields__:
        assert f not in ("offset", "length", "byte_length", "byte_offset"), (
            f"R.4 must not create layout field {f!r}"
        )


def test_r4_no_java_type_mapping():
    import dataclasses

    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-T OCCURS 10 TIMES DEPENDING ON WS-CNT.\n"
        b"88 WS-OK VALUE 0.\n"
    )
    result = _lex_and_parse(source)
    assert result.ast.data_items[0].occurs_clause is not None
    for cls in (
        OccursClause,
        OdoClause,
        Level88Declaration,
        DataItemDeclaration,
    ):
        for f in dataclasses.fields(cls):
            assert "java" not in f.name.lower(), (
                f"{cls.__name__}.{f.name} has 'java' in its name"
            )


def test_r4_no_symbol_resolution():
    """R.4 performs no symbol resolution: DEPENDING ON identifiers and
    88 condition names are stored as raw names only."""
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-T OCCURS 10 TIMES DEPENDING ON WS-CNT.\n"
        b"88 WS-OK VALUE 0.\n"
    )
    result = _lex_and_parse(source)
    d0 = result.ast.data_items[0]
    cond = result.ast.data_items[1]
    assert "__symbol__" not in d0.odo_clause.__dataclass_fields__
    assert "__resolved__" not in d0.odo_clause.__dataclass_fields__
    assert not hasattr(cond.value_clause, "resolved_value")