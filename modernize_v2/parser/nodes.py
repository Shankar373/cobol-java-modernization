"""T-2B-03 Parser AST — syntax-only node types.

All nodes are frozen dataclasses with deterministic IDs and exact
SourceSpan provenance.  Nodes carry syntactic information only; semantic
fields (DataItemId, JavaTypeRef, Layout, CobolType, etc.) are deferred
to later phases (T-2B-04+).

Reuses existing IR infrastructure:
  - IRKind (modernize_v2.ir.kinds)
  - DeterministicId (modernize_v2.ir.ids)
  - SourceSpan / SourcePosition (modernize_v2.ir.diagnostic)
  - Diagnostic (modernize_v2.ir.diagnostic)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional, Tuple, Union

from modernize_v2.ir.diagnostic import Diagnostic, SourceSpan, SourcePosition
from modernize_v2.ir.ids import DeterministicId
from modernize_v2.ir.kinds import IRKind
from modernize_v2.lexer.tokens import TokenKind


# ==================================================================
# Helper: construct a deterministic ID from kind + path + position
# ==================================================================

def _make_node_id(
    kind: IRKind,
    canonical_path: str,
    line: int,
    column: int,
    byte_offset: int,
    ordinal: int = 0,
) -> DeterministicId:
    """Produce a DeterministicId using the existing id_for_node utility."""
    from modernize_v2.ir.ids import id_for_node
    return id_for_node(
        kind=kind.value,
        canonical_path=canonical_path,
        line=line,
        column=column,
        byte_offset=byte_offset,
        ordinal=ordinal,
    )


# ==================================================================
# Base – every node carries ID, kind, and span
# ==================================================================

@dataclass(frozen=True)
class _NodeBase:
    """Minimal shared fields for all parser AST nodes."""

    node_id: DeterministicId
    kind: IRKind
    span: SourceSpan


# ==================================================================
# Identifier expression – syntactic only
# ==================================================================

@dataclass(frozen=True)
class IdentifierExpression:
    """A COBOL identifier as seen by the lexer.

    Syntactic fields:
    - identifier_text: the original source spelling (case-preserved).
    - NO resolved DataItemId – resolution is T-2B-05.

    Semantic fields (deferred):
    - target: DataItemId
    - java_type_ref: JavaTypeRef
    - cobol_type: CobolType
    - layout: Layout
    """

    node_id: DeterministicId
    kind: IRKind
    span: SourceSpan
    identifier_text: str


# ==================================================================
# Literal expression – syntactic only
# ==================================================================

@dataclass(frozen=True)
class LiteralExpression:
    """ACOBOL literal as seen by the lexer.

    Syntactic fields:
    - literal_raw_text: the raw source text (e.g. "123", "ZERO").
    - literal_kind: syntactic category (INTEGER, FIGURATIVE).

    Semantic typing (deferred to T-2B-07):
    - cobol_type: CobolType
    - promoting scale/precision
    """

    node_id: DeterministicId
    kind: IRKind
    span: SourceSpan
    literal_raw_text: str
    literal_kind: str  # e.g. "INTEGER", "FIGURATIVE"


# ==================================================================
# Binary operator expression
# ==================================================================

@dataclass(frozen=True)
class BinaryOpExpression:
    """A binary infix expression (e.g. A + B, A = B)."""

    node_id: DeterministicId
    kind: IRKind
    span: SourceSpan
    operator_text: str  # "+", "-", "*", "/", "=", "<", ">", etc.
    left: Any  # IdentifierExpression | LiteralExpression | BinaryOpExpression | etc.
    right: Any  # same types as left


# ==================================================================
# Unary operator expression
# ==================================================================

@dataclass(frozen=True)
class UnaryOpExpression:
    """A unary prefix expression (e.g. -A)."""

    node_id: DeterministicId
    kind: IRKind
    span: SourceSpan
    operator_text: str  # "-", "NOT"
    operand: Any  # IdentifierExpression | LiteralExpression | etc.


# ==================================================================
# Condition expression (comparison)
# ==================================================================

@dataclass(frozen=True)
class CondExpression:
    """A comparison expression (e.g. A > B, A = B)."""

    node_id: DeterministicId
    kind: IRKind
    span: SourceSpan
    operator_text: str  # "=", "<", ">", "<=", ">=", "!="
    left: Any  # IdentifierExpression | LiteralExpression | etc.
    right: Any  # same types as left


# ==================================================================
# Logical expression (AND/OR)
# ==================================================================

@dataclass(frozen=True)
class LogicalExpression:
    """A logical expression (e.g. A AND B, A OR C)."""

    node_id: DeterministicId
    kind: IRKind
    span: SourceSpan
    operator_text: str  # "AND", "OR"
    operands: Tuple[Any, ...]  # 2–3 IdentifierExpression/LiteralExpression/etc.


# ==================================================================
# Statement nodes – syntactic structure only
# ==================================================================

@dataclass(frozen=True)
class MoveStatement:
    """MOVE <source> TO <target>."""

    node_id: DeterministicId
    kind: IRKind
    span: SourceSpan
    source: IdentifierExpression
    target: IdentifierExpression


@dataclass(frozen=True)
class DisplayStatement:
    """DISPLAY <operand>."""

    node_id: DeterministicId
    kind: IRKind
    span: SourceSpan
    operand: IdentifierExpression | LiteralExpression


@dataclass(frozen=True)
class AddStatement:
    """ADD <left> TO <right> [GIVING <result>]."""

    node_id: DeterministicId
    kind: IRKind
    span: SourceSpan
    left: IdentifierExpression
    right: IdentifierExpression
    giving: IdentifierExpression | None = field(default=None, compare=False)


@dataclass(frozen=True)
class SubtractStatement:
    """SUBTRACT <left> FROM <right> [GIVING <result>]."""

    node_id: DeterministicId
    kind: IRKind
    span: SourceSpan
    left: IdentifierExpression
    right: IdentifierExpression
    giving: IdentifierExpression | None = field(default=None, compare=False)


@dataclass(frozen=True)
class MultiplyStatement:
    """MULTIPLY <left> BY <right> [GIVING <result>]."""

    node_id: DeterministicId
    kind: IRKind
    span: SourceSpan
    left: IdentifierExpression
    right: IdentifierExpression
    giving: IdentifierExpression | None = field(default=None, compare=False)


@dataclass(frozen=True)
class DivideStatement:
    """DIVIDE <left> INTO <right> [GIVING <result>]."""

    node_id: DeterministicId
    kind: IRKind
    span: SourceSpan
    left: IdentifierExpression
    right: IdentifierExpression
    giving: IdentifierExpression | None = field(default=None, compare=False)


@dataclass(frozen=True)
class ComputeStatement:
    """COMPUTE <target> = <expr>."""

    node_id: DeterministicId
    kind: IRKind
    span: SourceSpan
    target: IdentifierExpression
    expression: Any  # BinOpExpression, IdentifierExpression, LiteralExpression, etc.


@dataclass(frozen=True)
class IfStatement:
    """IF <condition> [ELSE [IF <cond2>] ...] END-IF."""

    node_id: DeterministicId
    kind: IRKind
    span: SourceSpan
    condition: Any  # CondExpression or BinOpExpression
    then_body: Tuple[Any, ...]  # Statement nodes (MoveStatement, etc.)
    else_body: Tuple[Any, ...]  # Tuple of Statement nodes (may be empty)


@dataclass(frozen=True)
class EvaluateStatement:
    """EVALUATE <expr> [WHEN <value> ...] END-EVALUATE."""

    node_id: DeterministicId
    kind: IRKind
    span: SourceSpan
    expression: Any  # Any expression node
    when_arms: Tuple[Tuple[str, Any], ...]  # ((value, statement_node), ...)
    else_arm: Tuple[Any, ...]  # may be empty


@dataclass(frozen=True)
class PerformStatement:
    """PERFORM <para> [TIMES] [UNTIL <cond>] [VARYING ...].

    T-2B-03 supports simple PERFORM only.
    """

    node_id: DeterministicId
    kind: IRKind
    span: SourceSpan
    paragraph_name: str
    # Per T-2B-03 scope: only simple PERFORM (no VARYING, UNTIL with complex expr)
    times: int | None = field(default=None, compare=False)
    until_cond: Any | None = field(default=None, compare=False)


@dataclass(frozen=True)
class GoToStatement:
    """GO TO <paragraph> | <label>."""

    node_id: DeterministicId
    kind: IRKind
    span: SourceSpan
    target: str  # paragraph name or label text


@dataclass(frozen=True)
class StopRunStatement:
    """STOP RUN."""

    node_id: DeterministicId
    kind: IRKind
    span: SourceSpan


@dataclass(frozen=True)
class GoBackStatement:
    """GOBACK."""

    node_id: DeterministicId
    kind: IRKind
    span: SourceSpan


@dataclass(frozen=True)
class ExitPerformStatement:
    """EXIT PERFORM."""

    node_id: DeterministicId
    kind: IRKind
    span: SourceSpan


@dataclass(frozen=True)
class ExitParagraphStatement:
    """EXIT PARAGRAPH."""

    node_id: DeterministicId
    kind: IRKind
    span: SourceSpan


# ==================================================================
# T-2B-04R.1: Data Division subsection structural node
# ==================================================================

@dataclass(frozen=True)
class DataDivisionSubsection:
    """A Data Division subsection header recognized by the parser.

    T-2B-04R.1 introduces this node to represent the *syntactic*
    presence of a Data Division subsection header such as
    ``WORKING-STORAGE SECTION.`` or ``LINKAGE SECTION.``.

    This is a structural-only node.  It does *not*:
      * parse data-item declarations inside the subsection,
      * resolve any symbol or identifier,
      * construct a semantic DataItem tree,
      * compute any layout or type.

    Subsequent tickets (T-2B-04R.2 and T-2B-06) are responsible
    for those concerns.  R.1 only records the subsection
    boundaries in the parser AST so that downstream phases do not
    need to re-scan the source.

    The ``kind`` field is one of the existing
    ``IRKind.WORKING_STORAGE_SECTION``,
    ``IRKind.LINKAGE_SECTION``,
    ``IRKind.LOCAL_STORAGE_SECTION``,
    ``IRKind.REPORT_SECTION``,
    ``IRKind.FILE_SECTION`` values.  No new IRKind values are
    introduced.
    """

    node_id: DeterministicId
    kind: IRKind
    span: SourceSpan
    #: The subsection name (uppercased, no hyphens collapsed),
    #: e.g. ``"WORKING-STORAGE"``.  Preserved verbatim from source
    #: to remain faithful to the source spelling.
    name: str


# ==================================================================
# T-2B-04R.3: Data-item clause structural nodes
# ==================================================================

@dataclass(frozen=True)
class PicClause:
    """A syntactic PIC (PICTURE) clause within a data-item
    declaration.

    T-2B-04R.3 introduces this node to represent the structural
    form of a ``PIC`` / ``PICTURE`` clause such as ``PIC X(10)``,
    ``PIC 9(7)V99``, or ``PIC S9(5)``.

    This is a structural-only node.  It does *not*:
      * compute the storage size in bytes
      * determine the Java type (long, BigDecimal, String, etc.)
      * interpret COMP / COMP-3 / BINARY / PACKED-DECIMAL encoding
      * perform signed / unsigned / decimal-point semantics
      * evaluate level-88 VALUE clauses
    Those concerns belong to T-2B-06 / T-2B-07 / T-2B-08.

    The ``raw_text`` field preserves the complete PIC string as it
    appears in the source.  The other fields capture the
    *structural* components: the category (``X``, ``9``, ``A``,
    ...), the size in parentheses, the sign indicator (``S``), and
    the scale portion after the ``V`` decimal-point marker.  The
    sign marker is reported through ``sign``, not ``category``; for
    example ``PIC S9(7)V99`` decomposes to category ``"9"``, sign
    ``"S"``, size ``"7"``, scale ``"99"``.  These structural
    components are preserved only when they can be reliably
    extracted; otherwise they are ``None``.
    """

    node_id: DeterministicId
    kind: IRKind
    span: SourceSpan
    #: The complete PIC string as it appears in the source,
    #: for example ``"X(10)"`` or ``"9(7)V99"`` or ``"S9(5)"``.
    raw_text: str
    #: The PIC category after separating the leading sign and the
    #: size/scale components (e.g. ``"X"``, ``"9"``, ``"A"``).
    #: The leading ``S`` sign marker is reported through ``sign``,
    #: not ``category``; a parenthesis size is reported through
    #: ``size``; a ``V`` scale is reported through ``scale``.
    #: None if a category cannot be reliably extracted.
    category: str | None = None
    #: The size portion in parentheses (e.g. ``"10"`` or ``"5"``).
    #: None when no size is present (e.g. plain ``PIC X``).
    size: str | None = None
    #: The sign indicator: ``"S"`` if a sign marker is present,
    #: otherwise ``None``.
    sign: str | None = None
    #: The scale portion after the ``V`` decimal-point marker
    #: (e.g. ``"99"`` for ``PIC 9(7)V99``).  None when no scale
    #: is present.
    scale: str | None = None


@dataclass(frozen=True)
class UsageClause:
    """A syntactic USAGE clause within a data-item declaration.

    T-2B-04R.3 introduces this node to represent the structural
    form of a ``USAGE`` clause such as ``USAGE DISPLAY``,
    ``USAGE COMP``, ``USAGE COMP-3``, ``USAGE BINARY``, or
    ``USAGE PACKED-DECIMAL``.

    This is a structural-only node.  It does *not*:
      * compute the storage size in bytes
      * determine the binary representation (COMP, COMP-3, BINARY)
      * determine the Java type
      * perform arithmetic behavior

    The ``usage_form`` field captures the recognized usage form
    (e.g. ``"DISPLAY"``, ``"COMP"``, ``"COMP-3"``,
    ``"BINARY"``, ``"PACKED-DECIMAL"``).  For forms that are
    not in the supported vocabulary, ``usage_form`` is set to
    the raw text and the diagnostic remains the responsibility
    of downstream semantic phases.
    """

    node_id: DeterministicId
    kind: IRKind
    span: SourceSpan
    #: The complete USAGE clause text as it appears in the
    #: source, for example ``"DISPLAY"`` or ``"COMP-3"``.
    raw_text: str
    #: The recognized usage form, e.g. ``"DISPLAY"``,
    #: ``"COMP"``, ``"COMP-3"``, ``"BINARY"``,
    #: ``"PACKED-DECIMAL"``.  This is the normalized
    #: form; ``raw_text`` preserves the original.
    usage_form: str


@dataclass(frozen=True)
class ValueClause:
    """A syntactic VALUE clause within a data-item declaration.

    T-2B-04R.3 introduces this node to represent the structural
    form of a ``VALUE`` clause such as ``VALUE 'Y'``, ``VALUE 123``,
    or ``VALUE "HELLO"``.

    Lexer contract (T-2B-02, frozen): the lexer drops the quote
    delimiter bytes of quoted literals before they reach the
    parser.  Both ``VALUE 'HELLO'`` and ``VALUE "HELLO"`` tokenize
    to ``KEYWORD(VALUE)`` ``IDENTIFIER(HELLO)`` — the two quote
    styles are indistinguishable at the token level.  As a result,
    the R.3 ValueClause:

      * stores the *lexer-observable* literal content only;
      * does NOT preserve quote delimiters or quote style;
      * cannot reliably reconstruct punctuation inside quoted
        literals (e.g. ``VALUE "A.B".`` tokenizes to
        ``IDENTIFIER(A)`` ``PERIOD`` ``IDENTIFIER(B)``);
      * does NOT guarantee exact source spelling.

    R.3 never fabricates quote information; it represents only what
    the frozen lexer exposes.  Restoring full string-literal
    fidelity is tracked by future lexer ticket T-2B-02R.1 (not
    implemented in R.3).

    This is a structural-only node.  It does *not*:
      * convert the literal to a typed Java value
      * perform type checking against the data item's type
      * perform constant folding
      * infer the CobolType of the literal

    The ``literal_kind`` field captures the broad syntactic
    category of the lexer-observable literal: ``"numeric"`` for a
    digits-only token (e.g. ``VALUE 123``) or ``"alphanumeric"``
    otherwise (e.g. ``VALUE Y`` or the quote-stripped content of
    ``VALUE "HELLO"``).  The ``literal_value`` field holds the same
    lexer-observable content as ``raw_text``.
    """

    node_id: DeterministicId
    kind: IRKind
    span: SourceSpan
    #: The lexer-observable literal content.  Quote delimiters are
    #: dropped by the frozen T-2B-02 lexer and are not available to
    #: R.3; exact source spelling is NOT guaranteed (see class
    #: docstring).
    raw_text: str
    #: The broad syntactic category of the lexer-observable literal:
    #: ``"numeric"`` (digits-only) or ``"alphanumeric"`` (anything
    #: else).  A quote-style ``"string"`` category is not available
    #: because the frozen lexer strips quote delimiters.
    literal_kind: str
    #: The lexer-observable literal content (same value as
    #: ``raw_text``).  No quote reconstruction is performed.
    literal_value: str


# ==================================================================
# T-2B-04R.2: Data-item declaration skeleton (parser-level)
# ==================================================================

@dataclass(frozen=True)
class DataItemDeclaration:
    """A syntactic Data Item declaration recognized by the parser.

    T-2B-04R.2 introduces this node to represent the *syntactic*
    structure of a data-item declaration such as
    ``01 WS-A PIC X(10).`` or
    ``01 WS-B REDEFINES WS-A PIC X(20).``.

    This is a structural-only node.  It does *not*:
      * resolve the declaration's name to a symbol
      * interpret PIC clauses (X(10), 9(5), S9(5)V99, COMP-3, etc.)
      * compute storage layout or byte offsets
      * validate REDEFINES / RENAMES semantics
      * establish parent / child hierarchy
      * distinguish elementary items from group items semantically

    Those concerns belong to T-2B-06 (DataItem tree) and beyond.
    R.2 only records the declaration boundaries, the level number,
    the name, the optional REDEFINES target, and the raw PIC text.

    The ``kind`` field is one of the existing IRKind values:
    ``DATA_ITEM`` (default for levels 01-49, 66, 77, 78),
    ``GROUP_ITEM`` (placeholder for group items — R.2 does not
    distinguish groups from elementary items; T-2B-06 will),
    ``ELEMENTARY_ITEM`` (placeholder for elementary items),
    or ``LEVEL_88_ITEM`` (for level-88 condition names).
    """

    node_id: DeterministicId
    kind: IRKind
    span: SourceSpan
    #: The COBOL level number (01-49, 66, 77, 78, or 88) as a
    #: plain Python int.  Stored as structured data, not as a string.
    level: int
    #: The data-item name, exactly as it appears in the source
    #: (preserved verbatim, case-preserved).
    name: str
    #: The optional REDEFINES target name (string or None).
    #: This is the raw name as it appears in the source; no
    #: symbol resolution is performed.
    redefines_target: str | None = None
    #: The optional raw PIC text (string or None).  This is the
    #: complete PIC clause text as it appears in the source,
    #: for example ``"PIC X(10)"`` or ``"PIC 9(5)V99"``.
    #: No PIC parsing is performed in R.2.
    pic_string: str | None = None

    # ----- T-2B-04R.3 additive fields (structured syntax) -----
    #: Optional structured PIC clause.  This is a parser-level
    #: representation of the PIC / PICTURE clause.  The
    #: raw PIC text remains available in the R.2 ``pic_string``
    #: field for backward compatibility.
    pic_clause: "PicClause | None" = None
    #: Optional structured USAGE clause.  This is a parser-level
    #: representation of the USAGE clause.  R.3 does not
    #: interpret the USAGE form; that is T-2B-08's
    #: responsibility.
    usage_clause: "UsageClause | None" = None
    #: Optional structured VALUE clause.  This is a parser-level
    #: representation of the VALUE literal.  R.3 does not
    #: convert the literal to a typed value; that is T-2B-08's
    #: responsibility.
    value_clause: "ValueClause | None" = None

    # ----- T-2B-04R.4 additive fields (structured OCCURS / ODO) -----
    #: Optional structured OCCURS clause.  This is a parser-level
    #: representation of ``OCCURS n TIMES`` or
    #: ``OCCURS l TO u TIMES``.  R.4 records the integer bounds
    #: syntactically; it does not compute array layout, subscript
    #: mapping, or Java array sizing (those are later-phase
    #: concerns).
    occurs_clause: "OccursClause | None" = None
    #: Optional structured OCCURS DEPENDING ON (ODO) clause.
    #: R.4 records the DEPENDING ON identifier as raw text, in
    #: its own node, without resolving it to a symbol (symbol
    #: resolution is T-2B-05's responsibility).  When non-None
    #: the corresponding ``occurs_clause`` is also non-None.
    odo_clause: "OdoClause | None" = None


# ==================================================================
# T-2B-04R.4: OCCURS / ODO / level-88 structural nodes
# ==================================================================

@dataclass(frozen=True)
class OccursClause:
    """A syntactic OCCURS clause recognized by the parser.

    T-2B-04R.4 introduces this node to represent the *syntactic*
    structure of an OCCURS clause:

        * fixed count:    ``OCCURS 10 TIMES``
        * range:          ``OCCURS 1 TO 10 TIMES``

    The clause is attached to its ``DataItemDeclaration`` through
    the additive ``occurs_clause`` field.  A valid clause sets
    exactly one of ``occurs`` (fixed count) or ``lower_bound`` /
    ``upper_bound`` (range); the other fields are ``None``.

    This is a structural-only node.  It does *not*:

        * resolve the DEPENDING ON identifier to a symbol
        * compute array storage / Java array sizing
        * validate the bounds (e.g. lower <= upper)

    Those concerns belong to T-2B-06 / T-2B-08 and beyond.
    """

    node_id: DeterministicId
    kind: IRKind  # OCCURS_CLAUSE
    span: SourceSpan
    #: Fixed count for ``OCCURS n TIMES``; ``None`` when the
    #: clause is a range form.
    occurs: int | None = None
    #: Range lower bound for ``OCCURS l TO u TIMES``; ``None``
    #: when the clause is a fixed-count form.
    lower_bound: int | None = None
    #: Range upper bound for ``OCCURS l TO u TIMES``; ``None``
    #: when the clause is a fixed-count form.
    upper_bound: int | None = None


@dataclass(frozen=True)
class OdoClause:
    """A syntactic OCCURS DEPENDING ON (ODO) clause.

    T-2B-04R.4 introduces this node to represent the DEPENDING ON
    portion of an OCCURS clause (e.g. ``DEPENDING ON WS-COUNT``).
    R.4 captures the identifier as verbatim raw text only; it does
    NOT resolve the identifier to a symbol (T-2B-05 will).

    The clause is attached to the same ``DataItemDeclaration`` as
    its OCCURS clause through the additive ``odo_clause`` field.
    """

    node_id: DeterministicId
    kind: IRKind  # ODO_CLAUSE
    span: SourceSpan
    #: The DEPENDING ON identifier name, exactly as it appears in
    #: the source (verbatim, case-preserved).  No symbol resolution
    #: is performed.
    identifier: str


@dataclass(frozen=True)
class Level88Declaration:
    """A dedicated syntactic representation of an 88-level condition name.

    T-2B-04R.4 introduces this node so that an 88-level condition
    name (e.g. ``88 WS-VALID VALUE 'Y'``) is represented by its own
    node type rather than an ordinary data-item declaration.  The
    node retains the parser-level fields that the R.2/R.3 contract
    already exposes for level-88 items (``level`` == 88, ``kind`` ==
    LEVEL_88_ITEM, ``name`` == the condition name) so the existing
    data-items collection contract is unchanged.

    The node is placed in the same ``data_items`` tuple (source
    order) as ordinary declarations.  It carries the condition
    name and the optional VALUE clause.  R.4 does NOT:

        * resolve the condition name to a symbol
        * interpret or type-check the VALUE literal
        * build a parent / child (condition-on-item) relationship

    Those concerns belong to T-2B-05 / T-2B-06 / T-2B-08.
    """

    node_id: DeterministicId
    kind: IRKind  # LEVEL_88_ITEM
    span: SourceSpan
    #: The COBOL level number (== 88 for a condition name).
    level: int
    #: The condition name, exactly as it appears in the source
    #: (verbatim, case-preserved).
    name: str
    #: The optional VALUE clause carrying the condition value
    #: literal (verbatim lexer-observable text).  ``None`` means no
    #: VALUE clause was recognized; R.4 reports a malformed-88
    #: diagnostic in that case.
    value_clause: "ValueClause | None" = None


# ==================================================================
# Compilation unit – root of the syntax tree
# ==================================================================

@dataclass(frozen=True)
class CompilationUnit:
    """Root of the parser AST.

    Holds the structured representation of one COBOL compilation
    unit.  All fields are immutable; the whole structure is
    deterministic given the same token stream.

    T-2B-04R.1 added ``data_division_subsections`` as an additive
    field.  T-2B-04R.2 adds ``data_items`` as another additive
    field.  All pre-existing fields (``divisions``,
    ``statements``, ``diagnostics``, ``recovery_records``) are
    preserved unchanged so that T-2B-03, T-2C-0A, and all earlier
    V2 tests continue to pass without modification.
    """

    node_id: DeterministicId
    kind: IRKind
    span: SourceSpan
    divisions: Tuple[Any, ...]  # structural division nodes (structural only)
    statements: Tuple[Any, ...]  # Statement nodes in procedure division order
    diagnostics: Tuple[Diagnostic, ...]  # UNSUPPORTED_FEATURE etc.
    recovery_records: Tuple[Any, ...]  # RecoveryRecord instances

    # ----- T-2B-04R.1 additive fields -----
    #: Structured Data Division subsection headers recognized by
    #: the parser.  This is a *syntax-only* structural field; no
    #: semantic data-item construction is performed here.  The
    #: list is in source order.
    data_division_subsections: Tuple["DataDivisionSubsection", ...] = ()

    # ----- T-2B-04R.2 additive fields -----
    #: Structured Data Division data-item declarations recognized
    #: by the parser.  This is a *syntax-only* structural field;
    #: no semantic resolution, PIC interpretation, layout
    #: computation, or hierarchy construction is performed here.
    #: The list is in source order.  T-2B-06 will build the
    #: canonical semantic DataItem tree from these.
    #:
    #: T-2B-04R.4 adds ``Level88Declaration`` entries: level-88
    #: condition names keep their source-order position here (the
    #: R.2 contract) but use a dedicated node type.
    data_items: Tuple[
        Union["DataItemDeclaration", "Level88Declaration"], ...
    ] = ()


# ==================================================================
# ParserResult – the output of Parser.parse()
# ==================================================================

@dataclass(frozen=True)
class ParserResult:
    """The deterministic result of a single parse invocation.

    Fields:
    - ast: the CompilationUnit root of the parser AST.
    - diagnostics: all diagnostics accumulated during parsing.
    - recovery_records: RecoveryRecord instances for skipped syntax.
    - eof_at_byte: byte offset where EOF was detected.
    """

    ast: CompilationUnit
    diagnostics: Tuple[Diagnostic, ...]
    recovery_records: Tuple[Any, ...]  # tuple of RecoveryRecord
    eof_at_byte: int