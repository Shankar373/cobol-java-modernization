"""T-2B-04R.3 — PIC / USAGE / VALUE structural clauses tests.

These tests verify the T-2B-04R.3 controlled parser-extension
slice: structured recognition of PIC/PICTURE, USAGE, and VALUE
clauses within data-item declarations.

R.3 does NOT:
    * interpret PIC clauses
    * compute storage layout
    * interpret USAGE forms (semantic equivalence)
    * type-check VALUE literals
    * perform constant folding
    * build the semantic DataItem tree
    * distinguish elementary items from group items semantically

It ONLY records the structural form of these clauses alongside the
R.2 raw-text representation.

The R.2 ``pic_string`` field on ``DataItemDeclaration`` is preserved
for backward compatibility.  R.3 adds structured ``pic_clause``,
``usage_clause``, and ``value_clause`` fields.
"""

from __future__ import annotations

import pytest

from modernize_v2.ir.kinds import IRKind
from modernize_v2.lexer import CobolLexer, SourceFormat
from modernize_v2.parser import (
    DataDivisionSubsection,
    DataItemDeclaration,
    Parser,
    PicClause,
    UsageClause,
    ValueClause,
)
from modernize_v2.source import make_source_file


def _lex_and_parse(source: bytes, *, path: str = "test.cbl"):
    sf = make_source_file(path, source)
    lexer = CobolLexer(sf, source, SourceFormat.FREE)
    tokens = lexer.lex()
    parser = Parser(tokens, canonical_path=path)
    return parser.parse()


# ---------------------------------------------------------------------------
# 1-10. PIC clause tests
# ---------------------------------------------------------------------------

def test_r3_pic_x_recognized():
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-X PIC X.\n"
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    assert di.pic_clause is not None
    assert di.pic_clause.kind == IRKind.PIC_CLAUSE
    assert di.pic_clause.raw_text == "X"
    assert di.pic_clause.category == "X"
    assert di.pic_clause.size is None
    assert di.pic_clause.sign is None
    assert di.pic_clause.scale is None


def test_r3_pic_x_10_recognized():
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-X PIC X(10).\n"
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    assert di.pic_clause is not None
    assert di.pic_clause.raw_text == "X(10)"
    assert di.pic_clause.category == "X"
    assert di.pic_clause.size == "10"


def test_r3_pic_9_recognized():
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-9 PIC 9.\n"
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    assert di.pic_clause is not None
    assert di.pic_clause.raw_text == "9"
    assert di.pic_clause.category == "9"


def test_r3_pic_9_5_recognized():
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-9 PIC 9(5).\n"
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    assert di.pic_clause is not None
    assert di.pic_clause.raw_text == "9(5)"
    assert di.pic_clause.category == "9"
    assert di.pic_clause.size == "5"


def test_r3_pic_9_7_v99_recognized():
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-V PIC 9(7)V99.\n"
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    assert di.pic_clause is not None
    assert di.pic_clause.raw_text == "9(7)V99"
    assert di.pic_clause.category == "9"
    assert di.pic_clause.size == "7"
    assert di.pic_clause.scale == "99"


def test_r3_pic_s9_7_v99_recognized():
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-S PIC S9(7)V99.\n"
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    assert di.pic_clause is not None
    assert di.pic_clause.raw_text == "S9(7)V99"
    assert di.pic_clause.sign == "S"
    assert di.pic_clause.category == "9"
    assert di.pic_clause.size == "7"
    assert di.pic_clause.scale == "99"


def test_r3_picture_alias_recognized():
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-P PICTURE X(10).\n"
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    assert di.pic_clause is not None
    assert di.pic_clause.raw_text == "X(10)"
    assert di.pic_clause.category == "X"
    assert di.pic_clause.size == "10"


def test_r3_pic_string_preserved_alongside_structured():
    """R.3 preserves the R.2 ``pic_string`` field for backward
    compatibility, alongside the new ``pic_clause`` structured
    field."""
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-X PIC X(10).\n"
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    # R.2 compatibility: raw string is still there
    assert di.pic_string == "X(10)"
    # R.3 enhancement: structured clause is also there
    assert di.pic_clause is not None
    assert di.pic_clause.raw_text == "X(10)"
    # Both agree
    assert di.pic_string == di.pic_clause.raw_text


def test_r3_pic_string_and_structured_agree():
    """The raw pic_string and the structured pic_clause should
    always agree on the raw text content."""
    for raw_pic in ["X", "9", "9(5)", "9(7)V99", "S9(5)V99", "X(10)"]:
        source = (
            b"DATA DIVISION.\n"
            b"WORKING-STORAGE SECTION.\n"
            b"01 WS-X PIC " + raw_pic.encode() + b".\n"
        )
        result = _lex_and_parse(source)
        di = result.ast.data_items[0]
        assert di.pic_string == raw_pic
        assert di.pic_clause is not None
        assert di.pic_clause.raw_text == raw_pic


def test_r3_pic_source_span_correct():
    """The PicClause span covers the entire PIC clause from the
    PIC keyword to the end of the PIC tokens."""
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-A PIC X(10).\n"
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    pic = di.pic_clause
    assert pic is not None
    expected_start = source.index(b"PIC")
    # End should be the end of the last PIC token (before the
    # period that ends the declaration).
    expected_end = source.rindex(b")") + 1
    assert pic.span.start.byte_offset == expected_start
    assert pic.span.end.byte_offset == expected_end


# ---------------------------------------------------------------------------
# 11-17. USAGE clause tests
# ---------------------------------------------------------------------------

def test_r3_usage_display():
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-D PIC 9 USAGE DISPLAY.\n"
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    assert di.usage_clause is not None
    assert di.usage_clause.kind == IRKind.USAGE_CLAUSE
    assert di.usage_clause.raw_text == "DISPLAY"
    assert di.usage_clause.usage_form == "DISPLAY"


def test_r3_usage_comp():
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-C PIC 9 USAGE COMP.\n"
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    assert di.usage_clause is not None
    assert di.usage_clause.usage_form == "COMP"


def test_r3_usage_comp_3():
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-C3 PIC 9 USAGE COMP-3.\n"
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    assert di.usage_clause is not None
    assert di.usage_clause.usage_form == "COMP-3"


def test_r3_usage_binary():
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-B PIC 9 USAGE BINARY.\n"
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    assert di.usage_clause is not None
    assert di.usage_clause.usage_form == "BINARY"


def test_r3_usage_packed_decimal():
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-PD PIC 9 USAGE PACKED-DECIMAL.\n"
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    assert di.usage_clause is not None
    assert di.usage_clause.usage_form == "PACKED-DECIMAL"


def test_r3_unsupported_usage_handled_safely():
    """An unknown USAGE form does NOT create a UsageClause
    node (R.3 only records recognized forms).  The parser
    falls through to normal handling."""
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-X PIC 9 USAGE UNKNOWN-FORM.\n"
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    # R.3 does not create a UsageClause for unknown forms
    assert di.usage_clause is None


def test_r3_usage_source_span_correct():
    """The UsageClause span covers the USAGE keyword and the form
    token."""
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-A PIC 9 USAGE DISPLAY.\n"
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    u = di.usage_clause
    assert u is not None
    expected_start = source.index(b"USAGE")
    expected_end = source.index(b"DISPLAY") + len(b"DISPLAY")
    assert u.span.start.byte_offset == expected_start
    assert u.span.end.byte_offset == expected_end


def test_r3_usage_is_display():
    """``USAGE IS DISPLAY`` is captured with form ``DISPLAY``."""
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-D PIC 9 USAGE IS DISPLAY.\n"
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    assert di.usage_clause is not None
    assert di.usage_clause.usage_form == "DISPLAY"
    assert di.usage_clause.raw_text == "DISPLAY"


def test_r3_usage_is_comp_3():
    """``USAGE IS COMP-3`` is captured with form ``COMP-3``."""
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-C3 PIC 9 USAGE IS COMP-3.\n"
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    assert di.usage_clause is not None
    assert di.usage_clause.usage_form == "COMP-3"


def test_r3_usage_is_binary():
    """``USAGE IS BINARY`` is captured with form ``BINARY``."""
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-B PIC 9 USAGE IS BINARY.\n"
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    assert di.usage_clause is not None
    assert di.usage_clause.usage_form == "BINARY"


def test_r3_usage_is_packed_decimal():
    """``USAGE IS PACKED-DECIMAL`` is captured with form
    ``PACKED-DECIMAL``."""
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-PD PIC 9 USAGE IS PACKED-DECIMAL.\n"
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    assert di.usage_clause is not None
    assert di.usage_clause.usage_form == "PACKED-DECIMAL"


def test_r3_usage_is_source_span_correct():
    """The UsageClause span for ``USAGE IS <form>`` covers the
    USAGE keyword through the form token (including the ``IS``
    connector)."""
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-A PIC 9 USAGE IS COMP-3.\n"
    result = _lex_and_parse(source)
    u = result.ast.data_items[0].usage_clause
    assert u is not None
    expected_start = source.index(b"USAGE")
    expected_end = source.index(b"COMP-3") + len(b"COMP-3")
    assert u.span.start.byte_offset == expected_start
    assert u.span.end.byte_offset == expected_end


def test_r3_usage_is_combined_with_pic_value():
    """``PIC + USAGE IS + VALUE`` combined in one declaration."""
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-A PIC 9(3) USAGE IS COMP-3 VALUE 0.\n"
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    assert di.pic_clause is not None
    assert di.usage_clause is not None
    assert di.usage_clause.usage_form == "COMP-3"
    assert di.value_clause is not None
    assert di.value_clause.literal_value == "0"


# ---------------------------------------------------------------------------
# 18-21. VALUE clause tests
# ---------------------------------------------------------------------------

def test_r3_value_alphanumeric_literal():
    """A VALUE clause with an alphanumeric literal (unquoted)."""
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-F PIC X VALUE Y.\n"
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    assert di.value_clause is not None
    assert di.value_clause.kind == IRKind.VALUE_CLAUSE
    assert di.value_clause.raw_text == "Y"
    assert di.value_clause.literal_kind == "alphanumeric"
    assert di.value_clause.literal_value == "Y"


def test_r3_value_numeric_literal():
    """A VALUE clause with a numeric literal."""
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-N PIC 9(3) VALUE 123.\n"
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    assert di.value_clause is not None
    assert di.value_clause.raw_text == "123"
    assert di.value_clause.literal_kind == "numeric"
    assert di.value_clause.literal_value == "123"


def test_r3_value_quoted_literal_is_lexer_stripped():
    """A VALUE clause with a quoted string literal.

    The frozen T-2B-02 lexer drops the quote delimiter bytes, so
    R.3 observes only ``HELLO``.  The literal is reported as
    ``alphanumeric`` (no fabricated ``"string"`` category) and
    ``literal_value`` equals ``raw_text`` (no fabricated quote
    reconstruction).  Full string-literal fidelity is tracked by
    future lexer ticket T-2B-02R.1, not by R.3.
    """
    source = b'DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-S PIC X(10) VALUE "HELLO".\n'
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    assert di.value_clause is not None
    assert di.value_clause.literal_kind == "alphanumeric"
    assert di.value_clause.raw_text == "HELLO"
    assert di.value_clause.literal_value == "HELLO"


def test_r3_quote_styles_are_lexer_equivalent():
    """A regression guard for the frozen lexer contract: single and
    double quotes are dropped identically, so ``VALUE 'HELLO'`` and
    ``VALUE "HELLO"`` produce identical ValueClause nodes, spans and
    all."""
    single = (
        b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n"
        b"01 WS-A PIC X(10) VALUE 'HELLO'.\n"
    )
    double = (
        b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n"
        b'01 WS-A PIC X(10) VALUE "HELLO".\n'
    )
    result_single = _lex_and_parse(single)
    result_double = _lex_and_parse(double)
    v_single = result_single.ast.data_items[0].value_clause
    v_double = result_double.ast.data_items[0].value_clause
    assert v_single is not None
    assert v_double is not None
    assert v_single.raw_text == v_double.raw_text == "HELLO"
    assert v_single.literal_kind == v_double.literal_kind == "alphanumeric"
    assert v_single.literal_value == v_double.literal_value == "HELLO"
    # The quote bytes are at the same offsets in both sources, so the
    # (quote-free) literal spans are identical.
    assert v_single.span.start.byte_offset == v_double.span.start.byte_offset
    assert v_single.span.end.byte_offset == v_double.span.end.byte_offset


def test_r3_value_decimal_literal_lexer_accurate():
    """``VALUE 123.45.`` — the frozen lexer tokenizes the period as
    a PERIOD, so the VALUE clause captures only ``123`` and R.3 does
    NOT fabricate the decimal fraction ``.45``.

    The remaining ``45`` is consumed by the existing level-number
    matching path (``45`` is a recognized data-item level number) and
    its following period ends the aborted declaration, so no second
    data item is created and no error is raised: this round-trips the
    verified pre-R.3 recovery behavior without inventing a decimal
    literal."""
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-N PIC 9(5)V99 VALUE 123.45.\n"
    result = _lex_and_parse(source)
    assert len(result.ast.data_items) == 1
    di = result.ast.data_items[0]
    assert di.name == "WS-N"
    v = di.value_clause
    assert v is not None
    assert v.raw_text == "123"
    assert v.literal_kind == "numeric"
    assert v.literal_value == "123"


def test_r3_pic_with_no_pic_string_safe():
    """``PIC .`` — no PIC content after the keyword.  R.3 returns
    ``(None, None)``: pic_string stays None and no PicClause is
    fabricated; the parser does not crash."""
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-A PIC.\n"
    result = _lex_and_parse(source)
    assert len(result.ast.data_items) == 1
    di = result.ast.data_items[0]
    assert di.pic_string is None
    assert di.pic_clause is None


def test_r3_value_source_span_correct():
    """The ValueClause span covers the VALUE keyword and the
    literal."""
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-A PIC X VALUE Y.\n"
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    v = di.value_clause
    assert v is not None
    expected_start = source.index(b"VALUE")
    expected_end = source.index(b"Y") + 1
    assert v.span.start.byte_offset == expected_start
    assert v.span.end.byte_offset == expected_end


def test_r3_malformed_value_recovery():
    """A VALUE clause with no literal (e.g. 'PIC X VALUE.') is
    handled safely (the parser falls through)."""
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-A PIC X VALUE.\n"
    # We just verify this does not crash the parser.
    result = _lex_and_parse(source)
    assert result is not None


# ---------------------------------------------------------------------------
# 23-30. Combined declarations
# ---------------------------------------------------------------------------

def test_r3_pic_and_usage_combined():
    """PIC + USAGE combined."""
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-A PIC X(10) USAGE DISPLAY.\n"
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    assert di.pic_clause is not None
    assert di.usage_clause is not None
    assert di.value_clause is None


def test_r3_pic_and_value_combined():
    """PIC + VALUE combined."""
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-A PIC X VALUE Y.\n"
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    assert di.pic_clause is not None
    assert di.value_clause is not None
    assert di.usage_clause is None


def test_r3_pic_usage_value_combined():
    """PIC + USAGE + VALUE combined."""
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-A PIC X(10) USAGE DISPLAY VALUE Y.\n"
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    assert di.pic_clause is not None
    assert di.usage_clause is not None
    assert di.value_clause is not None


def test_r3_picture_usage_value_combined():
    """PICTURE + USAGE + VALUE combined (PICTURE is an alias)."""
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-A PICTURE X(10) USAGE DISPLAY VALUE Y.\n"
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    assert di.pic_clause is not None
    assert di.pic_clause.raw_text == "X(10)"
    assert di.usage_clause is not None
    assert di.value_clause is not None


def test_r3_multiple_data_items_preserve_source_order():
    """Multiple data items in the same Data Division subsection
    preserve source order with their clauses attached to the
    correct declaration."""
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-A PIC X.\n"
        b"01 WS-B PIC 9 VALUE 0.\n"
        b"01 WS-C PIC 9 USAGE COMP.\n"
    )
    result = _lex_and_parse(source)
    assert len(result.ast.data_items) == 3
    assert result.ast.data_items[0].name == "WS-A"
    assert result.ast.data_items[0].pic_clause is not None
    assert result.ast.data_items[0].usage_clause is None
    assert result.ast.data_items[0].value_clause is None
    assert result.ast.data_items[1].name == "WS-B"
    assert result.ast.data_items[1].pic_clause is not None
    assert result.ast.data_items[1].value_clause is not None
    assert result.ast.data_items[2].name == "WS-C"
    assert result.ast.data_items[2].usage_clause is not None
    assert result.ast.data_items[2].pic_clause is not None


def test_r3_clauses_attached_to_correct_declaration():
    """Clauses are attached only to their own data item, not to
    subsequent declarations."""
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-A PIC X VALUE Y.\n"
        b"01 WS-B PIC 9.\n"
    )
    result = _lex_and_parse(source)
    ws_a, ws_b = result.ast.data_items
    assert ws_a.value_clause is not None
    assert ws_a.value_clause.raw_text == "Y"
    assert ws_b.value_clause is None


def test_r3_clauses_across_multiple_subsections():
    """Clauses in declarations across different Data Division
    subsections are tracked independently."""
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-A PIC X VALUE Y.\n"
        b"LINKAGE SECTION.\n"
        b"01 LK-A PIC 9 USAGE BINARY.\n"
    )
    result = _lex_and_parse(source)
    assert len(result.ast.data_items) == 2
    assert result.ast.data_items[0].name == "WS-A"
    assert result.ast.data_items[0].value_clause is not None
    assert result.ast.data_items[0].usage_clause is None
    assert result.ast.data_items[1].name == "LK-A"
    assert result.ast.data_items[1].usage_clause is not None
    assert result.ast.data_items[1].value_clause is None


def test_r3_no_clause_leakage_between_declarations():
    """A clause is attached only to its own declaration; it is
    never leaked to subsequent declarations."""
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-A PIC X.\n"
        b"01 WS-B PIC 9 VALUE 99.\n"
    )
    result = _lex_and_parse(source)
    ws_a, ws_b = result.ast.data_items
    assert ws_a.value_clause is None
    assert ws_b.value_clause is not None
    assert ws_b.value_clause.raw_text == "99"


# ---------------------------------------------------------------------------
# 31-41. Compatibility
# ---------------------------------------------------------------------------

def test_r3_r1_subsection_recognition_still_works():
    """R.1's subsection recognition is preserved."""
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-A PIC X.\n"
    result = _lex_and_parse(source)
    assert len(result.ast.data_division_subsections) == 1
    assert result.ast.data_division_subsections[0].name == "WORKING-STORAGE"


def test_r3_r2_data_item_declaration_still_works():
    """R.2's DataItemDeclaration fields are preserved."""
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-A PIC X(10).\n"
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    assert di.level == 1
    assert di.name == "WS-A"
    assert di.redefines_target is None
    assert di.pic_string == "X(10)"


def test_r3_compilation_unit_divisions_unchanged():
    """CompilationUnit.divisions (R.1 contract) is unchanged."""
    source = (
        b"IDENTIFICATION DIVISION.\n"
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-A PIC X.\n"
        b"PROCEDURE DIVISION.\n"
        b"MOVE A TO B.\n"
    )
    result = _lex_and_parse(source)
    assert result.ast.divisions == (
        "IDENTIFICATION DIVISION",
        "DATA DIVISION",
        "PROCEDURE DIVISION",
    )


def test_r3_compilation_unit_statements_unchanged():
    source = b"PROCEDURE DIVISION.\nMOVE A TO B.\n"
    result = _lex_and_parse(source)
    assert len(result.ast.statements) == 1


def test_r3_compilation_unit_diagnostics_preserved():
    """R.3 does not mask nor suppress diagnostics for unrecognized
    syntax: an unknown token still surfaces as a diagnostic."""
    source = b"PROCEDURE DIVISION.\nUNKNOWN-X.\n"
    result = _lex_and_parse(source)
    assert len(result.diagnostics) >= 1


def test_r3_valid_data_item_suppresses_no_diagnostics():
    """A fully-recognized R.3 declaration produces no parser
    diagnostics (no false positives, and nothing is swallowed)."""
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-A PIC X(10) USAGE IS DISPLAY VALUE Y.\n"
    result = _lex_and_parse(source)
    assert result.ast.diagnostics == ()


def test_r3_compilation_unit_recovery_records_preserved():
    """Recovery records are preserved."""
    source = b"PROCEDURE DIVISION.\nUNKNOWN-X.\n"
    result = _lex_and_parse(source)
    assert result.ast.recovery_records is not None


def test_r3_data_division_subsections_preserved():
    """R.1's data_division_subsections field is preserved."""
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\nLINKAGE SECTION.\n"
    result = _lex_and_parse(source)
    assert len(result.ast.data_division_subsections) == 2


def test_r3_data_items_field_compatible():
    """The R.2 data_items field is preserved (R.3 just adds clause
    fields to each item)."""
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-A PIC X.\n"
    result = _lex_and_parse(source)
    assert len(result.ast.data_items) == 1


def test_r3_t2c0a_scope_graph_unchanged():
    """T-2C-0A's scope graph still works without modification."""
    from modernize_v2.analysis import build_scope_graph
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-A PIC X.\n"
        b"PROCEDURE DIVISION.\n"
        b"MOVE WS-A TO WS-B.\n"
    )
    result = _lex_and_parse(source)
    graph = build_scope_graph(result)
    texts = [r.text for r in graph.references]
    assert "WS-A" in texts
    assert "WS-B" in texts


def test_r3_existing_move_regression():
    """Existing MOVE statement test (regression)."""
    source = b"MOVE A TO B."
    result = _lex_and_parse(source)
    assert len(result.ast.statements) == 1


def test_r3_existing_if_regression():
    """Existing IF statement test (regression)."""
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
# 42-44. Determinism
# ---------------------------------------------------------------------------

def test_r3_deterministic_clause_ids():
    """Clause IDs are deterministic for the same source."""
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-A PIC X(10) USAGE DISPLAY VALUE Y.\n"
    r1 = _lex_and_parse(source)
    r2 = _lex_and_parse(source)
    assert r1.ast.data_items[0].pic_clause.node_id == r2.ast.data_items[0].pic_clause.node_id
    assert r1.ast.data_items[0].usage_clause.node_id == r2.ast.data_items[0].usage_clause.node_id
    assert r1.ast.data_items[0].value_clause.node_id == r2.ast.data_items[0].value_clause.node_id


def test_r3_deterministic_repeated_parsing():
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-A PIC X(10) USAGE DISPLAY.\n"
    r1 = _lex_and_parse(source)
    r2 = _lex_and_parse(source)
    fields1 = (
        r1.ast.data_items[0].level,
        r1.ast.data_items[0].name,
        r1.ast.data_items[0].pic_string,
        r1.ast.data_items[0].pic_clause.raw_text,
        r1.ast.data_items[0].usage_clause.raw_text,
    )
    fields2 = (
        r2.ast.data_items[0].level,
        r2.ast.data_items[0].name,
        r2.ast.data_items[0].pic_string,
        r2.ast.data_items[0].pic_clause.raw_text,
        r2.ast.data_items[0].usage_clause.raw_text,
    )
    assert fields1 == fields2


def test_r3_two_parser_instances_produce_identical_clauses():
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-A PIC X(10) USAGE DISPLAY VALUE Y.\n"
    sf = make_source_file("test.cbl", source)
    lexer1 = CobolLexer(sf, source, SourceFormat.FREE)
    lexer2 = CobolLexer(sf, source, SourceFormat.FREE)
    p1 = Parser(lexer1.lex(), canonical_path="test.cbl")
    p2 = Parser(lexer2.lex(), canonical_path="test.cbl")
    r1 = p1.parse()
    r2 = p2.parse()
    di1, di2 = r1.ast.data_items[0], r2.ast.data_items[0]
    assert di1.pic_clause.node_id == di2.pic_clause.node_id
    assert di1.usage_clause.node_id == di2.usage_clause.node_id
    assert di1.value_clause.node_id == di2.value_clause.node_id


def test_r3_two_parsers_produce_identical_full_clause_state():
    """Determinism at the structural level: two independent Parser
    instances over the same source produce byte-identical clause
    triples (ids, spans, raw text, structural fields) for every
    data item, and identical diagnostic counts."""
    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-A PIC 9(5) USAGE IS COMP-3 VALUE 0.\n"
        b"01 WS-B PIC X(10) VALUE HELLO.\n"
        b"01 WS-C PIC S9(7)V99.\n"
    )
    sf = make_source_file("test.cbl", source)
    lexer1 = CobolLexer(sf, source, SourceFormat.FREE)
    lexer2 = CobolLexer(sf, source, SourceFormat.FREE)
    r1 = Parser(lexer1.lex(), canonical_path="test.cbl").parse()
    r2 = Parser(lexer2.lex(), canonical_path="test.cbl").parse()
    assert len(r1.ast.data_items) == len(r2.ast.data_items) == 3

    def clause_state(di):
        pic = di.pic_clause
        usage = di.usage_clause
        value = di.value_clause
        return (
            di.level,
            di.name,
            di.pic_string,
            (
                pic.node_id,
                pic.span.start.byte_offset,
                pic.span.end.byte_offset,
                pic.raw_text,
                pic.category,
                pic.sign,
                pic.size,
                pic.scale,
            )
            if pic is not None
            else None,
            (
                usage.node_id,
                usage.span.start.byte_offset,
                usage.span.end.byte_offset,
                usage.raw_text,
                usage.usage_form,
            )
            if usage is not None
            else None,
            (
                value.node_id,
                value.span.start.byte_offset,
                value.span.end.byte_offset,
                value.raw_text,
                value.literal_kind,
                value.literal_value,
            )
            if value is not None
            else None,
        )

    assert [clause_state(d) for d in r1.ast.data_items] == [
        clause_state(d) for d in r2.ast.data_items
    ]
    assert len(r1.diagnostics) == len(r2.diagnostics)


# ---------------------------------------------------------------------------
# 45-52. Architecture invariants
# ---------------------------------------------------------------------------

def test_r3_new_nodes_are_frozen():
    """PicClause, UsageClause, and ValueClause are frozen
    (immutable) dataclasses: attribute assignment raises
    FrozenInstanceError."""
    from dataclasses import FrozenInstanceError, is_dataclass

    source = (
        b"DATA DIVISION.\n"
        b"WORKING-STORAGE SECTION.\n"
        b"01 WS-A PIC X(10) USAGE IS DISPLAY VALUE Y.\n"
    )
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    assert di.pic_clause is not None
    assert di.usage_clause is not None
    assert di.value_clause is not None
    for node in (di.pic_clause, di.usage_clause, di.value_clause):
        assert is_dataclass(node)
        with pytest.raises(FrozenInstanceError):
            node.raw_text = "MUTATED"


def test_r3_clause_kinds_are_data_item_kinds():
    """The R.3 structural clause kinds are registered in
    DATA_ITEM_KINDS alongside the existing clause kinds
    (``is_data_item_kind`` returns True for all of them)."""
    from modernize_v2.ir.kinds import is_data_item_kind

    for kind in (IRKind.PIC_CLAUSE, IRKind.USAGE_CLAUSE, IRKind.VALUE_CLAUSE):
        assert is_data_item_kind(kind)


def test_r3_no_dict_str_any_in_public_api():
    """The new R.3 fields do not use Dict[str, Any]."""
    import dataclasses
    for cls in (PicClause, UsageClause, ValueClause, DataItemDeclaration):
        for f in dataclasses.fields(cls):
            hint = repr(f.type)
            assert "Dict[str, Any]" not in hint, (
                f"{cls.__name__}.{f.name} uses Dict[str, Any]"
            )


def test_r3_no_v1_imports():
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


def test_r3_no_filesystem_io():
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


def test_r3_no_semantic_dataitem_creation():
    """R.3 does NOT create a semantic DataItem tree; it only
    creates syntax-level clause nodes."""
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-A PIC 9(5) USAGE COMP-3.\n"
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    # R.3 does not compute storage size, Java type, or
    # COMP-3 encoding.  The pic_clause and usage_clause only
    # hold structural text.
    for f in di.__dataclass_fields__:
        assert f not in ("storage_size", "java_type", "encoding", "byte_length"), (
            f"R.3 must not create semantic field {f!r}"
        )


def test_r3_no_coboltype_creation():
    """R.3 does NOT create or infer CobolType."""
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-A PIC 9(5).\n"
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    for f in di.__dataclass_fields__:
        assert f not in ("cobol_type", "java_type_ref"), (
            f"R.3 must not create {f!r}"
        )


def test_r3_no_java_type_mapping():
    """R.3 does NOT perform Java type mapping."""
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-A PIC 9(5) USAGE COMP-3.\n"
    result = _lex_and_parse(source)
    # The parser produces no Java-related output
    assert result.ast.data_items[0].pic_clause is not None
    # No java field anywhere
    import dataclasses
    for cls in (PicClause, UsageClause, ValueClause, DataItemDeclaration):
        for f in dataclasses.fields(cls):
            assert "java" not in f.name.lower(), (
                f"{cls.__name__}.{f.name} has 'java' in its name"
            )


def test_r3_no_layout_computation():
    """R.3 does NOT compute storage layout."""
    source = b"DATA DIVISION.\nWORKING-STORAGE SECTION.\n01 WS-A PIC X(10) USAGE COMP-3.\n"
    result = _lex_and_parse(source)
    di = result.ast.data_items[0]
    for f in di.__dataclass_fields__:
        assert f not in ("offset", "length", "byte_length", "byte_offset"), (
            f"R.3 must not create layout field {f!r}"
        )
