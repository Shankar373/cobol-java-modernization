"""T-2B-03 Deterministic COBOL Syntax Parser — main implementation.

The parser converts T-2B-02 token streams into a syntax-only AST.
It does NOT perform semantic analysis, symbol resolution, type
mapping, or any other later-phase concern.

API:
    Parser(tokens: tuple[Token, ...])
    result = parser.parse() -> ParserResult

ParserResult contains:
    ast: CompilationUnit
    diagnostics: tuple[Diagnostic, ...]
    recovery_records: tuple[RecoveryRecord, ...]
    eof_at_byte: int

The parser is deterministic: repeated calls with the same token
stream produce identical results.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Final, List, Optional, Tuple

from modernize_v2.ir.diagnostic import (
    Diagnostic,
    DiagnosticKind,
    DiagnosticSeverity,
    SourcePosition,
    SourceSpan,
)
from modernize_v2.ir.ids import DeterministicId, id_for_node
from modernize_v2.ir.kinds import IRKind
from modernize_v2.lexer.tokens import Token, TokenKind

from .grammar import (
    SUPPORTED_LOOKUP,
    classify,
    is_supported,
)
from .nodes import (
    AddStatement,
    BinaryOpExpression,
    CompilationUnit,
    ComputeStatement,
    CondExpression,
    DataDivisionSubsection,
    DataItemDeclaration,
    DisplayStatement,
    DivideStatement,
    EvaluateStatement,
    ExitParagraphStatement,
    ExitPerformStatement,
    GoBackStatement,
    GoToStatement,
    IdentifierExpression,
    IfStatement,
    LiteralExpression,
    LogicalExpression,
    MoveStatement,
    MultiplyStatement,
    ParserResult,
    PerformStatement,
    PicClause,
    StopRunStatement,
    SubtractStatement,
    UnaryOpExpression,
    UsageClause,
    ValueClause,
)
from .recovery import (
    RecoveryRecord,
    is_eof_token,
    make_recovery_record,
    make_unsupported_diagnostic,
)


# ==================================================================
# Constants
# ==================================================================

#: Operator tokens for each precedence level
_MULTIPLICATIVE_OPS: Final = frozenset(["*", "/"])
_ADDITIVE_OPS: Final = frozenset(["+", "-"])
_COMPARISON_OPS: Final = frozenset(["=", "<", ">", "<=", ">=", "!="])
_LOGICAL_OPS: Final = frozenset(["AND", "OR"])
_UNARY_OPS: Final = frozenset(["NOT", "-"])

#: Figurative constants recognized syntactically
_FIGURATIVE_CONSTANTS: Final = frozenset([
    "ZERO", "ZEROS", "ZEROES",
    "SPACE", "SPACES",
    "HIGH-VALUE", "HIGH-VALUES",
    "LOW-VALUE", "LOW-VALUES",
    "QUOTE", "QUOTES",
    "ALL", "NULL", "NULLS",
])

#: Division/section header phrases
_DIVISION_HEADERS: Final = frozenset([
    "IDENTIFICATION DIVISION",
    "ENVIRONMENT DIVISION",
    "DATA DIVISION",
    "PROCEDURE DIVISION",
])


# T-2B-04R.1: Data Division subsection-header keyword set.
#: The uppercased token text for each Data Division subsection
#: header.  These are recognized by the parser to suppress the
#: "unknown token" diagnostic that the previous parser produced.
_DATA_DIVISION_SECTION_KEYWORDS: Final = frozenset({
    "WORKING-STORAGE",
    "LINKAGE",
    "LOCAL-STORAGE",
    "REPORT",
    "FILE",
})

#: Mapping from subsection keyword (uppercased) to the existing
#: IRKind for that subsection.  Reuses existing IRKind values
#: (no new kinds are introduced).
_DATA_DIVISION_SECTION_KIND: Final = {
    "WORKING-STORAGE": IRKind.WORKING_STORAGE_SECTION,
    "LINKAGE": IRKind.LINKAGE_SECTION,
    "LOCAL-STORAGE": IRKind.LOCAL_STORAGE_SECTION,
    "REPORT": IRKind.REPORT_SECTION,
    "FILE": IRKind.FILE_SECTION,
}


# T-2B-04R.2: Data Item declaration constants.
#: COBOL level numbers recognized as data-item declaration
#: starters.  The parser only treats a token as a level number
#: if it is exactly two digits long (per COBOL standard
#: formatting) and falls in one of these sets.
_DATA_ITEM_LEVEL_NUMBERS: Final = frozenset({
    # 01-49
    *(f"{n:02d}" for n in range(1, 50)),
    # 66, 77, 78
    "66", "77", "78",
    # 88
    "88",
})

#: The IRKind emitted for a recognized level number.  Level 88
#: gets the special LEVEL_88_ITEM kind; all other levels get
#: DATA_ITEM.  Group-vs-elementary distinction is deferred to
#: T-2B-06.
_DATA_ITEM_LEVEL_KIND: Final = {
    **{f"{n:02d}": IRKind.DATA_ITEM for n in range(1, 50)},
    "66": IRKind.DATA_ITEM,
    "77": IRKind.DATA_ITEM,
    "78": IRKind.DATA_ITEM,
    "88": IRKind.LEVEL_88_ITEM,
}

# T-2B-04R.3: USAGE clause vocabulary.
#: Recognized USAGE forms.
_USAGE_FORMS: Final = frozenset({
    "DISPLAY",
    "COMP",
    "COMP-1",
    "COMP-2",
    "COMP-3",
    "COMP-4",
    "COMP-5",
    "BINARY",
    "PACKED-DECIMAL",
    "INDEX",
    "POINTER",
    "FUNCTION-POINTER",
})


# ==================================================================
# Parser
# ==================================================================

class Parser:
    """Deterministic syntax-only COBOL parser.

    Consumes T-2B-02 token streams and produces a CompilationUnit
    AST.  Re-entrant: parse() can be called repeatedly with
    identical results.
    """

    def __init__(
        self,
        tokens: Tuple[Token, ...],
        *,
        canonical_path: str = "source.cbl",
    ) -> None:
        self._tokens: Tuple[Token, ...] = tokens
        self._canonical_path: str = canonical_path
        # EOF detection requires the source byte size; infer it from
        # the last token's span when the token is the EOF sentinel.
        self._byte_size: int = self._infer_byte_size(tokens)
        # Mutable cursor state, reset by parse().
        self._pos: int = 0

    @staticmethod
    def _infer_byte_size(tokens: Tuple[Token, ...]) -> int:
        """Determine the source byte_size from the token stream.

        For the lexer EOF contract the last token is the EOF sentinel
        with start.byte_offset == end.byte_offset == byte_size.
        """
        if not tokens:
            return 0
        last = tokens[-1]
        if is_eof_token(last):
            return last.span.start.byte_offset
        # If no explicit EOF sentinel, fall back to end of last token.
        return last.span.end.byte_offset

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def parse(self) -> ParserResult:
        """Parse the token stream and return a deterministic ParserResult.

        Re-entrant: cursor is reset at the start of every call.
        """
        self._pos = 0
        diagnostics: List[Diagnostic] = []
        recovery_records: List[RecoveryRecord] = []
        statements: List[Any] = []
        divisions: List[Any] = []
        data_division_subsections: List[Any] = []
        data_items: List[Any] = []

        # Locate structural divisions.
        # For T-2B-03 we parse a flat sequence of statements that may
        # appear in any of the supported divisions, but we track
        # division boundaries syntactically.
        current_division: Optional[str] = None

        # T-2B-04R.2: Track whether the parser is currently inside a
        # Data Division subsection.  Data-item declarations are
        # only matched in this context, so that arbitrary
        # numeric-looking tokens in the Procedure Division are
        # not misinterpreted as data items.
        in_data_division_subsection: bool = False

        while not self._is_eof():
            tok = self._current()
            # Handle division headers structurally.
            division_phrase = self._match_division_header()
            if division_phrase is not None:
                current_division = division_phrase
                divisions.append(division_phrase)
                # Leaving the data-division context when a
                # non-data division header is encountered.
                if division_phrase != "DATA DIVISION":
                    in_data_division_subsection = False
                # Consume any trailing period.
                if not self._is_eof() and self._current().kind == TokenKind.PERIOD:
                    self._advance()
                continue
            # T-2B-04R.1: Handle Data Division subsection headers
            # structurally.  These are recognized as the two-token
            # pattern ``<SUBSECTION> SECTION.`` (or
            # ``<SUBSECTION> SECTION``).  We do NOT parse the body
            # of the subsection; data-item declarations continue
            # to produce parser diagnostics as before.  Only the
            # subsection header itself is suppressed.
            subsection_match = self._match_data_division_subsection_header()
            if subsection_match is not None:
                sub_name, sub_kind, sub_start, sub_end = subsection_match
                sub_span = self._make_span(sub_start, sub_end)
                if not self._is_eof() and self._current().kind == TokenKind.PERIOD:
                    self._advance()
                sub_id = self._make_id(sub_kind, sub_start)
                data_division_subsections.append(
                    DataDivisionSubsection(
                        node_id=sub_id,
                        kind=sub_kind,
                        span=sub_span,
                        name=sub_name,
                    )
                )
                # We are now inside a Data Division subsection and
                # can recognize data-item declarations.
                in_data_division_subsection = True
                continue
            # T-2B-04R.2: Handle Data Division data-item declarations
            # structurally.  These are recognized only when we are
            # inside a Data Division subsection.  We do NOT perform
            # semantic resolution, PIC interpretation, layout
            # computation, or hierarchy construction here.
            item_match = self._match_data_item_declaration(
                in_data_division_subsection
            )
            if item_match is not None:
                (level, name, redefines_target, pic_string,
                 pic_clause_node, usage_clause_node, value_clause_node,
                 item_start, item_end) = item_match
                item_span = self._make_span(item_start, item_end)
                item_kind = _DATA_ITEM_LEVEL_KIND[f"{level:02d}"]
                item_id = self._make_id(item_kind, item_start)
                data_items.append(
                    DataItemDeclaration(
                        node_id=item_id,
                        kind=item_kind,
                        span=item_span,
                        level=level,
                        name=name,
                        redefines_target=redefines_target,
                        pic_string=pic_string,
                        pic_clause=pic_clause_node,
                        usage_clause=usage_clause_node,
                        value_clause=value_clause_node,
                    )
                )
                continue
            # Handle period at top level (no statement in progress).
            if tok.kind == TokenKind.PERIOD:
                self._advance()
                continue
            # Try to parse a statement.
            stmt, stmt_diags, stmt_recovs = self._parse_statement()
            if stmt is not None:
                statements.append(stmt)
            diagnostics.extend(stmt_diags)
            recovery_records.extend(stmt_recovs)
            # If we are at EOF after this, stop.
            if self._is_eof():
                break
            # If we did not advance, force a step to avoid infinite loops.
            if not stmt_recovs and stmt is None:
                # Defensive: this should not happen if recovery is correct.
                self._advance()

        # Determine the total span of the compilation unit.
        cu_span = self._make_span(0, self._byte_size)
        cu_id = self._make_id(IRKind.COMPILATION_UNIT, 0)

        ast = CompilationUnit(
            node_id=cu_id,
            kind=IRKind.COMPILATION_UNIT,
            span=cu_span,
            divisions=tuple(divisions),
            statements=tuple(statements),
            diagnostics=tuple(diagnostics),
            recovery_records=tuple(recovery_records),
            data_division_subsections=tuple(data_division_subsections),
            data_items=tuple(data_items),
        )

        return ParserResult(
            ast=ast,
            diagnostics=tuple(diagnostics),
            recovery_records=tuple(recovery_records),
            eof_at_byte=self._byte_size,
        )

    # ------------------------------------------------------------------
    # Cursor operations
    # ------------------------------------------------------------------

    def _is_eof(self) -> bool:
        """True if cursor has reached EOF (past the last token or at
        the EOF sentinel)."""
        if self._pos >= len(self._tokens):
            return True
        # The lexer EOF is a token with text == "" and IDENTIFIER kind.
        tok = self._tokens[self._pos]
        return is_eof_token(tok)

    def _current(self) -> Token:
        """Return the token at the cursor (never EOF — caller checks
        _is_eof() first)."""
        if self._pos < len(self._tokens):
            tok = self._tokens[self._pos]
            if not is_eof_token(tok):
                return tok
        # Past end: return the EOF sentinel.
        return self._tokens[-1] if self._tokens else _EMPTY_EOF

    def _peek(self, offset: int = 1) -> Optional[Token]:
        """Look ahead *offset* tokens; None if at/past EOF."""
        idx = self._pos + offset
        if idx >= len(self._tokens):
            return None
        tok = self._tokens[idx]
        if is_eof_token(tok):
            return None
        return tok

    def _advance(self) -> None:
        """Move the cursor forward by one position (skipping EOF)."""
        if self._pos < len(self._tokens):
            tok = self._tokens[self._pos]
            if not is_eof_token(tok):
                self._pos += 1
            else:
                # Don't advance past EOF.
                pass
        else:
            # Already at end; nothing to do.
            pass

    def _match(self, token_kind: TokenKind, text: Optional[str] = None) -> bool:
        """If current token matches *token_kind* (and optional *text*),
        advance past it and return True.  Otherwise leave cursor and
        return False."""
        if self._is_eof():
            return False
        tok = self._current()
        if tok.kind != token_kind:
            return False
        if text is not None and tok.text.upper() != text.upper():
            return False
        self._advance()
        return True

    def _expect(
        self,
        token_kind: TokenKind,
        text: Optional[str] = None,
    ) -> Token:
        """Consume the current token if it matches; otherwise raise
        ValueError (the parser should never see this in normal
        operation — it is a sanity check)."""
        if self._is_eof():
            raise ValueError(
                f"expected {token_kind.name}/{text!r}, got EOF"
            )
        tok = self._current()
        if tok.kind != token_kind:
            raise ValueError(
                f"expected {token_kind.name}/{text!r}, got "
                f"{tok.kind.name}/{tok.text!r}"
            )
        if text is not None and tok.text.upper() != text.upper():
            raise ValueError(
                f"expected text {text!r}, got {tok.text!r}"
            )
        self._advance()
        return tok

    # ------------------------------------------------------------------
    # Statement parsing
    # ------------------------------------------------------------------

    def _parse_statement(
        self,
    ) -> Tuple[Optional[Any], List[Diagnostic], List[RecoveryRecord]]:
        """Parse a single statement starting at the current cursor.

        Returns (stmt_or_None, diagnostics, recovery_records).
        On unsupported or malformed input, returns a diagnostic and
        a recovery record, and synchronizes to the next safe point.
        """
        if self._is_eof():
            return None, [], []

        tok = self._current()
        text_upper = tok.text.upper()

        # ---- Period at statement start: skip ----
        if tok.kind == TokenKind.PERIOD:
            self._advance()
            return None, [], []

        # ---- Structural scope terminators outside their context ----
        if text_upper in ("END-IF", "END-EVALUATE", "WHEN"):
            diag = self._diagnose_misplaced(text_upper)
            self._sync_after_statement()
            return None, [diag], []

        # ---- MOVE ----
        if text_upper == "MOVE":
            return self._parse_move()

        # ---- DISPLAY ----
        if text_upper == "DISPLAY":
            return self._parse_display()

        # ---- Arithmetic verbs ----
        if text_upper == "ADD":
            return self._parse_add()
        if text_upper == "SUBTRACT":
            return self._parse_subtract()
        if text_upper == "MULTIPLY":
            return self._parse_multiply()
        if text_upper == "DIVIDE":
            return self._parse_divide()
        if text_upper == "COMPUTE":
            return self._parse_compute()

        # ---- IF / END-IF ----
        if text_upper == "IF":
            return self._parse_if()

        # ---- EVALUATE / WHEN / END-EVALUATE ----
        if text_upper == "EVALUATE":
            return self._parse_evaluate()

        # ---- PERFORM ----
        if text_upper == "PERFORM":
            return self._parse_perform()

        # ---- GO TO ----
        if text_upper == "GO":
            peeked = self._peek(1)
            if peeked is not None and peeked.text.upper() == "TO":
                return self._parse_goto()

        # ---- STOP RUN ----
        if text_upper == "STOP":
            peeked = self._peek(1)
            if peeked is not None and peeked.text.upper() == "RUN":
                return self._parse_stop_run()

        # ---- GOBACK ----
        if text_upper == "GOBACK":
            return self._parse_goback()

        # ---- EXIT PERFORM / EXIT PARAGRAPH ----
        if text_upper == "EXIT":
            peeked = self._peek(1)
            if peeked is not None and peeked.text.upper() == "PERFORM":
                return self._parse_exit_perform()
            if peeked is not None and peeked.text.upper() == "PARAGRAPH":
                return self._parse_exit_paragraph()

        # ---- Unsupported constructs ----
        unsupported = self._classify_unsupported(text_upper)
        if unsupported is not None:
            diag = make_unsupported_diagnostic(
                message=f"COBOL construct not supported in T-2B-03: {unsupported}",
                span=tok.span,
            )
            self._sync_after_statement()
            recov = make_recovery_record(
                skipped_construct=unsupported,
                span=tok.span,
                sync_byte=self._current_span_start(),
            )
            return None, [diag], [recov]

        # ---- Unknown keyword or identifier: treat as unrecognized,
        # produce a parser diagnostic, and skip to next period. ----
        diag = self._diagnose_unknown(tok)
        self._sync_after_statement()
        recov = make_recovery_record(
            skipped_construct=tok.text,
            span=tok.span,
            sync_byte=self._current_span_start(),
        )
        return None, [diag], [recov]

    def _parse_move(
        self,
    ) -> Tuple[Optional[MoveStatement], List[Diagnostic], List[RecoveryRecord]]:
        diags: List[Diagnostic] = []
        recovs: List[RecoveryRecord] = []
        start_tok = self._expect_keyword("MOVE")
        span_start = start_tok.span.start.byte_offset

        source = self._parse_expression()
        if source is None:
            diags.append(self._diagnose_missing("MOVE", "source"))
            self._sync_after_statement()
            return None, diags, recovs

        to_tok = self._expect_keyword("TO")

        target = self._parse_expression()
        if target is None:
            diags.append(self._diagnose_missing("MOVE", "target"))
            self._sync_after_statement()
            return None, diags, recovs

        self._consume_period()
        span_end = self._last_consumed_end_byte()
        if span_end is None:
            span_end = target.span.end.byte_offset

        stmt_id = self._make_id(IRKind.STATEMENT_MOVE, span_start)
        stmt = MoveStatement(
            node_id=stmt_id,
            kind=IRKind.STATEMENT_MOVE,
            span=self._make_span(span_start, span_end),
            source=source,
            target=target,
        )
        return stmt, diags, recovs

    def _parse_display(
        self,
    ) -> Tuple[Optional[DisplayStatement], List[Diagnostic], List[RecoveryRecord]]:
        diags: List[Diagnostic] = []
        recovs: List[RecoveryRecord] = []
        start_tok = self._expect_keyword("DISPLAY")
        span_start = start_tok.span.start.byte_offset

        operand = self._parse_expression()
        if operand is None:
            diags.append(self._diagnose_missing("DISPLAY", "operand"))
            self._sync_after_statement()
            return None, diags, recovs

        self._consume_period()
        span_end = self._last_consumed_end_byte() or operand.span.end.byte_offset
        stmt_id = self._make_id(IRKind.STATEMENT_DISPLAY, span_start)
        stmt = DisplayStatement(
            node_id=stmt_id,
            kind=IRKind.STATEMENT_DISPLAY,
            span=self._make_span(span_start, span_end),
            operand=operand,
        )
        return stmt, diags, recovs

    def _parse_add(
        self,
    ) -> Tuple[Optional[AddStatement], List[Diagnostic], List[RecoveryRecord]]:
        diags: List[Diagnostic] = []
        recovs: List[RecoveryRecord] = []
        start_tok = self._expect_keyword("ADD")
        span_start = start_tok.span.start.byte_offset

        left = self._parse_expression()
        if left is None:
            diags.append(self._diagnose_missing("ADD", "left operand"))
            self._sync_after_statement()
            return None, diags, recovs

        self._expect_keyword("TO")
        right = self._parse_expression()
        if right is None:
            diags.append(self._diagnose_missing("ADD", "right operand"))
            self._sync_after_statement()
            return None, diags, recovs

        giving: Optional[IdentifierExpression] = None
        if not self._is_eof() and self._current().text.upper() == "GIVING":
            self._expect_keyword("GIVING")
            giving_expr = self._parse_expression()
            if isinstance(giving_expr, IdentifierExpression):
                giving = giving_expr
            else:
                diags.append(self._diagnose_missing("ADD", "GIVING identifier"))

        self._consume_period()
        span_end = self._last_consumed_end_byte() or right.span.end.byte_offset
        stmt_id = self._make_id(IRKind.STATEMENT_ARITHMETIC_ADD, span_start)
        stmt = AddStatement(
            node_id=stmt_id,
            kind=IRKind.STATEMENT_ARITHMETIC_ADD,
            span=self._make_span(span_start, span_end),
            left=left if isinstance(left, IdentifierExpression) else IdentifierExpression(
                node_id=left.node_id, kind=IRKind.EXPRESSION_REFERENCE, span=left.span, identifier_text=str(left)
            ),
            right=right if isinstance(right, IdentifierExpression) else IdentifierExpression(
                node_id=right.node_id, kind=IRKind.EXPRESSION_REFERENCE, span=right.span, identifier_text=str(right)
            ),
            giving=giving,
        )
        return stmt, diags, recovs

    def _parse_subtract(
        self,
    ) -> Tuple[Optional[SubtractStatement], List[Diagnostic], List[RecoveryRecord]]:
        diags: List[Diagnostic] = []
        recovs: List[RecoveryRecord] = []
        start_tok = self._expect_keyword("SUBTRACT")
        span_start = start_tok.span.start.byte_offset

        left = self._parse_expression()
        if left is None:
            diags.append(self._diagnose_missing("SUBTRACT", "left operand"))
            self._sync_after_statement()
            return None, diags, recovs

        self._expect_keyword("FROM")
        right = self._parse_expression()
        if right is None:
            diags.append(self._diagnose_missing("SUBTRACT", "right operand"))
            self._sync_after_statement()
            return None, diags, recovs

        giving: Optional[IdentifierExpression] = None
        if not self._is_eof() and self._current().text.upper() == "GIVING":
            self._expect_keyword("GIVING")
            giving_expr = self._parse_expression()
            if isinstance(giving_expr, IdentifierExpression):
                giving = giving_expr

        self._consume_period()
        span_end = self._last_consumed_end_byte() or right.span.end.byte_offset
        stmt_id = self._make_id(IRKind.STATEMENT_ARITHMETIC_SUBTRACT, span_start)
        stmt = SubtractStatement(
            node_id=stmt_id,
            kind=IRKind.STATEMENT_ARITHMETIC_SUBTRACT,
            span=self._make_span(span_start, span_end),
            left=left if isinstance(left, IdentifierExpression) else IdentifierExpression(
                node_id=left.node_id, kind=IRKind.EXPRESSION_REFERENCE, span=left.span, identifier_text=str(left)
            ),
            right=right if isinstance(right, IdentifierExpression) else IdentifierExpression(
                node_id=right.node_id, kind=IRKind.EXPRESSION_REFERENCE, span=right.span, identifier_text=str(right)
            ),
            giving=giving,
        )
        return stmt, diags, recovs

    def _parse_multiply(
        self,
    ) -> Tuple[Optional[MultiplyStatement], List[Diagnostic], List[RecoveryRecord]]:
        diags: List[Diagnostic] = []
        recovs: List[RecoveryRecord] = []
        start_tok = self._expect_keyword("MULTIPLY")
        span_start = start_tok.span.start.byte_offset

        left = self._parse_expression()
        if left is None:
            diags.append(self._diagnose_missing("MULTIPLY", "left operand"))
            self._sync_after_statement()
            return None, diags, recovs

        self._expect_keyword("BY")
        right = self._parse_expression()
        if right is None:
            diags.append(self._diagnose_missing("MULTIPLY", "right operand"))
            self._sync_after_statement()
            return None, diags, recovs

        giving: Optional[IdentifierExpression] = None
        if not self._is_eof() and self._current().text.upper() == "GIVING":
            self._expect_keyword("GIVING")
            giving_expr = self._parse_expression()
            if isinstance(giving_expr, IdentifierExpression):
                giving = giving_expr

        self._consume_period()
        span_end = self._last_consumed_end_byte() or right.span.end.byte_offset
        stmt_id = self._make_id(IRKind.STATEMENT_ARITHMETIC_MULTIPLY, span_start)
        stmt = MultiplyStatement(
            node_id=stmt_id,
            kind=IRKind.STATEMENT_ARITHMETIC_MULTIPLY,
            span=self._make_span(span_start, span_end),
            left=left if isinstance(left, IdentifierExpression) else IdentifierExpression(
                node_id=left.node_id, kind=IRKind.EXPRESSION_REFERENCE, span=left.span, identifier_text=str(left)
            ),
            right=right if isinstance(right, IdentifierExpression) else IdentifierExpression(
                node_id=right.node_id, kind=IRKind.EXPRESSION_REFERENCE, span=right.span, identifier_text=str(right)
            ),
            giving=giving,
        )
        return stmt, diags, recovs

    def _parse_divide(
        self,
    ) -> Tuple[Optional[DivideStatement], List[Diagnostic], List[RecoveryRecord]]:
        diags: List[Diagnostic] = []
        recovs: List[RecoveryRecord] = []
        start_tok = self._expect_keyword("DIVIDE")
        span_start = start_tok.span.start.byte_offset

        left = self._parse_expression()
        if left is None:
            diags.append(self._diagnose_missing("DIVIDE", "left operand"))
            self._sync_after_statement()
            return None, diags, recovs

        self._expect_keyword("INTO")
        right = self._parse_expression()
        if right is None:
            diags.append(self._diagnose_missing("DIVIDE", "right operand"))
            self._sync_after_statement()
            return None, diags, recovs

        giving: Optional[IdentifierExpression] = None
        if not self._is_eof() and self._current().text.upper() == "GIVING":
            self._expect_keyword("GIVING")
            giving_expr = self._parse_expression()
            if isinstance(giving_expr, IdentifierExpression):
                giving = giving_expr

        self._consume_period()
        span_end = self._last_consumed_end_byte() or right.span.end.byte_offset
        stmt_id = self._make_id(IRKind.STATEMENT_ARITHMETIC_DIVIDE, span_start)
        stmt = DivideStatement(
            node_id=stmt_id,
            kind=IRKind.STATEMENT_ARITHMETIC_DIVIDE,
            span=self._make_span(span_start, span_end),
            left=left if isinstance(left, IdentifierExpression) else IdentifierExpression(
                node_id=left.node_id, kind=IRKind.EXPRESSION_REFERENCE, span=left.span, identifier_text=str(left)
            ),
            right=right if isinstance(right, IdentifierExpression) else IdentifierExpression(
                node_id=right.node_id, kind=IRKind.EXPRESSION_REFERENCE, span=right.span, identifier_text=str(right)
            ),
            giving=giving,
        )
        return stmt, diags, recovs

    def _parse_compute(
        self,
    ) -> Tuple[Optional[ComputeStatement], List[Diagnostic], List[RecoveryRecord]]:
        diags: List[Diagnostic] = []
        recovs: List[RecoveryRecord] = []
        start_tok = self._expect_keyword("COMPUTE")
        span_start = start_tok.span.start.byte_offset

        # Parse target as a single identifier (not a full expression).
        if self._is_eof() or self._current().kind not in (TokenKind.IDENTIFIER, TokenKind.KEYWORD):
            diags.append(self._diagnose_missing("COMPUTE", "target identifier"))
            self._sync_after_statement()
            return None, diags, recovs
        target_tok = self._current()
        target = IdentifierExpression(
            node_id=self._make_id(IRKind.EXPRESSION_REFERENCE, target_tok.span.start.byte_offset),
            kind=IRKind.EXPRESSION_REFERENCE,
            span=target_tok.span,
            identifier_text=target_tok.text,
        )
        self._advance()

        # Expect '=' (tokenized as TokenKind.EQUALS)
        if self._is_eof() or self._current().kind != TokenKind.EQUALS:
            diags.append(self._diagnose_missing("COMPUTE", "="))
            self._sync_after_statement()
            return None, diags, recovs
        self._advance()  # consume '='

        expression = self._parse_expression()
        if expression is None:
            diags.append(self._diagnose_missing("COMPUTE", "expression"))
            self._sync_after_statement()
            return None, diags, recovs

        self._consume_period()
        span_end = self._last_consumed_end_byte() or expression.span.end.byte_offset
        stmt_id = self._make_id(IRKind.STATEMENT_ARITHMETIC_COMPUTE, span_start)
        stmt = ComputeStatement(
            node_id=stmt_id,
            kind=IRKind.STATEMENT_ARITHMETIC_COMPUTE,
            span=self._make_span(span_start, span_end),
            target=target,
            expression=expression,
        )
        return stmt, diags, recovs

    def _parse_if(
        self,
    ) -> Tuple[Optional[IfStatement], List[Diagnostic], List[RecoveryRecord]]:
        diags: List[Diagnostic] = []
        recovs: List[RecoveryRecord] = []
        start_tok = self._expect_keyword("IF")
        span_start = start_tok.span.start.byte_offset

        condition = self._parse_expression()
        if condition is None:
            diags.append(self._diagnose_missing("IF", "condition"))
            self._sync_after_statement()
            return None, diags, recovs

        then_body = self._parse_statement_list(terminals=("ELSE", "END-IF", "END-IF."))

        else_body: List[Any] = []
        if not self._is_eof() and self._current().text.upper() == "ELSE":
            self._expect_keyword("ELSE")
            else_body = self._parse_statement_list(terminals=("END-IF", "END-IF."))

        # Expect END-IF
        if self._is_eof():
            diags.append(self._diagnose_unexpected_eof("IF"))
            return None, diags, recovs

        end_tok = self._current()
        if end_tok.text.upper() != "END-IF":
            diags.append(self._diagnose_missing("IF", "END-IF"))
            self._sync_after_statement()
            return None, diags, recovs
        self._advance()  # consume END-IF
        self._consume_period()
        span_end = self._last_consumed_end_byte() or end_tok.span.end.byte_offset

        stmt_id = self._make_id(IRKind.STATEMENT_IF, span_start)
        stmt = IfStatement(
            node_id=stmt_id,
            kind=IRKind.STATEMENT_IF,
            span=self._make_span(span_start, span_end),
            condition=condition,
            then_body=tuple(then_body),
            else_body=tuple(else_body),
        )
        return stmt, diags, recovs

    def _parse_evaluate(
        self,
    ) -> Tuple[Optional[EvaluateStatement], List[Diagnostic], List[RecoveryRecord]]:
        diags: List[Diagnostic] = []
        recovs: List[RecoveryRecord] = []
        start_tok = self._expect_keyword("EVALUATE")
        span_start = start_tok.span.start.byte_offset

        expression = self._parse_expression()
        if expression is None:
            diags.append(self._diagnose_missing("EVALUATE", "expression"))
            self._sync_after_statement()
            return None, diags, recovs

        when_arms: List[Tuple[str, Any]] = []
        else_arm: List[Any] = []

        while not self._is_eof() and self._current().text.upper() == "WHEN":
            self._advance()  # consume WHEN
            # Parse the value (single identifier or literal).
            value_expr = self._parse_expression()
            value_text = (
                value_expr.identifier_text
                if isinstance(value_expr, IdentifierExpression)
                else (
                    value_expr.literal_raw_text
                    if isinstance(value_expr, LiteralExpression)
                    else "?"
                )
            )
            body = self._parse_statement_list(terminals=("WHEN", "END-EVALUATE", "END-EVALUATE."))
            when_arms.append((value_text, body))

        # Optional WHEN OTHER
        if not self._is_eof() and self._current().text.upper() == "WHEN":
            # already handled above
            pass

        # Expect END-EVALUATE
        if self._is_eof():
            diags.append(self._diagnose_unexpected_eof("EVALUATE"))
            return None, diags, recovs
        if self._current().text.upper() != "END-EVALUATE":
            diags.append(self._diagnose_missing("EVALUATE", "END-EVALUATE"))
            self._sync_after_statement()
            return None, diags, recovs
        end_tok = self._current()
        self._advance()
        self._consume_period()
        span_end = self._last_consumed_end_byte() or end_tok.span.end.byte_offset

        stmt_id = self._make_id(IRKind.STATEMENT_EVALUATE, span_start)
        stmt = EvaluateStatement(
            node_id=stmt_id,
            kind=IRKind.STATEMENT_EVALUATE,
            span=self._make_span(span_start, span_end),
            expression=expression,
            when_arms=tuple(when_arms),
            else_arm=tuple(else_arm),
        )
        return stmt, diags, recovs

    def _parse_perform(
        self,
    ) -> Tuple[Optional[PerformStatement], List[Diagnostic], List[RecoveryRecord]]:
        diags: List[Diagnostic] = []
        recovs: List[RecoveryRecord] = []
        start_tok = self._expect_keyword("PERFORM")
        span_start = start_tok.span.start.byte_offset

        if self._is_eof():
            diags.append(self._diagnose_missing("PERFORM", "paragraph name"))
            return None, diags, recovs

        tok = self._current()
        # PERFORM VARYING is unsupported in T-2B-03.
        if tok.text.upper() == "VARYING":
            diag = make_unsupported_diagnostic(
                message="PERFORM VARYING not supported in T-2B-03",
                span=tok.span,
            )
            self._sync_after_statement()
            recov = make_recovery_record(
                skipped_construct="PERFORM VARYING",
                span=tok.span,
                sync_byte=self._current_span_start(),
            )
            return None, [diag], [recov]

        # Parse paragraph name (identifier).
        para_name = self._parse_paragraph_name()
        if para_name is None:
            diags.append(self._diagnose_missing("PERFORM", "paragraph name"))
            self._sync_after_statement()
            return None, diags, recovs

        # Reject UNTIL / TIMES / VARYING for T-2B-03.
        if not self._is_eof():
            next_text = self._current().text.upper()
            if next_text in ("UNTIL", "TIMES", "VARYING"):
                diag = make_unsupported_diagnostic(
                    message=f"PERFORM with {next_text} not supported in T-2B-03",
                    span=self._current().span,
                )
                self._sync_after_statement()
                recov = make_recovery_record(
                    skipped_construct=f"PERFORM {next_text}",
                    span=self._current().span,
                    sync_byte=self._current_span_start(),
                )
                return None, [diag], [recov]

        self._consume_period()
        span_end = self._last_consumed_end_byte() or tok.span.end.byte_offset
        stmt_id = self._make_id(IRKind.STATEMENT_PERFORM, span_start)
        stmt = PerformStatement(
            node_id=stmt_id,
            kind=IRKind.STATEMENT_PERFORM,
            span=self._make_span(span_start, span_end),
            paragraph_name=para_name,
            times=None,
            until_cond=None,
        )
        return stmt, diags, recovs

    def _parse_goto(
        self,
    ) -> Tuple[Optional[GoToStatement], List[Diagnostic], List[RecoveryRecord]]:
        diags: List[Diagnostic] = []
        recovs: List[RecoveryRecord] = []
        start_tok = self._expect_keyword("GO")
        span_start = start_tok.span.start.byte_offset
        self._expect_keyword("TO")

        if self._is_eof():
            diags.append(self._diagnose_missing("GO TO", "target"))
            return None, diags, recovs

        target_tok = self._current()
        if target_tok.kind not in (TokenKind.IDENTIFIER, TokenKind.KEYWORD):
            diags.append(self._diagnose_missing("GO TO", "target paragraph"))
            self._sync_after_statement()
            return None, diags, recovs
        target = target_tok.text
        self._advance()

        self._consume_period()
        span_end = self._last_consumed_end_byte() or target_tok.span.end.byte_offset
        stmt_id = self._make_id(IRKind.STATEMENT_GO_TO, span_start)
        stmt = GoToStatement(
            node_id=stmt_id,
            kind=IRKind.STATEMENT_GO_TO,
            span=self._make_span(span_start, span_end),
            target=target,
        )
        return stmt, diags, recovs

    def _parse_stop_run(
        self,
    ) -> Tuple[Optional[StopRunStatement], List[Diagnostic], List[RecoveryRecord]]:
        diags: List[Diagnostic] = []
        recovs: List[RecoveryRecord] = []
        start_tok = self._expect_keyword("STOP")
        span_start = start_tok.span.start.byte_offset
        self._expect_keyword("RUN")
        self._consume_period()
        span_end = self._last_consumed_end_byte() or self._tokens[self._pos - 1].span.end.byte_offset
        stmt_id = self._make_id(IRKind.STATEMENT_STOP_RUN, span_start)
        stmt = StopRunStatement(
            node_id=stmt_id,
            kind=IRKind.STATEMENT_STOP_RUN,
            span=self._make_span(span_start, span_end),
        )
        return stmt, diags, recovs

    def _parse_goback(
        self,
    ) -> Tuple[Optional[GoBackStatement], List[Diagnostic], List[RecoveryRecord]]:
        diags: List[Diagnostic] = []
        recovs: List[RecoveryRecord] = []
        start_tok = self._expect_keyword("GOBACK")
        span_start = start_tok.span.start.byte_offset
        self._consume_period()
        span_end = self._last_consumed_end_byte() or start_tok.span.end.byte_offset
        stmt_id = self._make_id(IRKind.STATEMENT_GOBACK, span_start)
        stmt = GoBackStatement(
            node_id=stmt_id,
            kind=IRKind.STATEMENT_GOBACK,
            span=self._make_span(span_start, span_end),
        )
        return stmt, diags, recovs

    def _parse_exit_perform(
        self,
    ) -> Tuple[Optional[ExitPerformStatement], List[Diagnostic], List[RecoveryRecord]]:
        diags: List[Diagnostic] = []
        recovs: List[RecoveryRecord] = []
        start_tok = self._expect_keyword("EXIT")
        span_start = start_tok.span.start.byte_offset
        self._expect_keyword("PERFORM")
        self._consume_period()
        span_end = self._last_consumed_end_byte() or self._tokens[self._pos - 1].span.end.byte_offset
        stmt_id = self._make_id(IRKind.STATEMENT_EXIT_PERFORM, span_start)
        stmt = ExitPerformStatement(
            node_id=stmt_id,
            kind=IRKind.STATEMENT_EXIT_PERFORM,
            span=self._make_span(span_start, span_end),
        )
        return stmt, diags, recovs

    def _parse_exit_paragraph(
        self,
    ) -> Tuple[Optional[ExitParagraphStatement], List[Diagnostic], List[RecoveryRecord]]:
        diags: List[Diagnostic] = []
        recovs: List[RecoveryRecord] = []
        start_tok = self._expect_keyword("EXIT")
        span_start = start_tok.span.start.byte_offset
        self._expect_keyword("PARAGRAPH")
        self._consume_period()
        span_end = self._last_consumed_end_byte() or self._tokens[self._pos - 1].span.end.byte_offset
        stmt_id = self._make_id(IRKind.STATEMENT_EXIT_PARAGRAPH, span_start)
        stmt = ExitParagraphStatement(
            node_id=stmt_id,
            kind=IRKind.STATEMENT_EXIT_PARAGRAPH,
            span=self._make_span(span_start, span_end),
        )
        return stmt, diags, recovs

    # ------------------------------------------------------------------
    # Statement list parsing (for IF/EVALUATE bodies)
    # ------------------------------------------------------------------

    def _parse_statement_list(
        self,
        terminals: Tuple[str, ...],
    ) -> List[Any]:
        """Parse statements until a terminal token is reached.

        The terminal is one of the strings in *terminals* (e.g.
        'ELSE', 'END-IF').  Periods and EOF also terminate.
        """
        stmts: List[Any] = []
        while not self._is_eof():
            tok = self._current()
            if tok.text.upper() in terminals:
                break
            if tok.kind == TokenKind.PERIOD:
                # Consume a stray period.
                self._advance()
                continue
            stmt, diags, recovs = self._parse_statement()
            if stmt is not None:
                stmts.append(stmt)
        return stmts

    # ------------------------------------------------------------------
    # Expression parsing with precedence
    # ------------------------------------------------------------------

    def _parse_expression(self) -> Optional[Any]:
        """Parse an expression starting from the current cursor.

        The top-level dispatch is the lowest-precedence level
        (logical OR) so that A OR B AND C groups correctly.
        """
        if self._is_eof():
            return None
        return self._parse_logical_or()

    def _parse_logical_or(self) -> Optional[Any]:
        left = self._parse_logical_and()
        if left is None:
            return None
        while not self._is_eof() and self._current().text.upper() == "OR":
            op_tok = self._current()
            self._advance()
            right = self._parse_logical_and()
            if right is None:
                return left
            span_end = right.span.end.byte_offset
            span = self._make_span(left.span.start.byte_offset, span_end)
            left = LogicalExpression(
                node_id=self._make_id(IRKind.EXPRESSION_LOGICAL, left.span.start.byte_offset),
                kind=IRKind.EXPRESSION_LOGICAL,
                span=span,
                operator_text="OR",
                operands=(left, right),
            )
        return left

    def _parse_logical_and(self) -> Optional[Any]:
        left = self._parse_comparison()
        if left is None:
            return None
        while not self._is_eof() and self._current().text.upper() == "AND":
            self._advance()
            right = self._parse_comparison()
            if right is None:
                return left
            span = self._make_span(left.span.start.byte_offset, right.span.end.byte_offset)
            left = LogicalExpression(
                node_id=self._make_id(IRKind.EXPRESSION_LOGICAL, left.span.start.byte_offset),
                kind=IRKind.EXPRESSION_LOGICAL,
                span=span,
                operator_text="AND",
                operands=(left, right),
            )
        return left

    def _parse_comparison(self) -> Optional[Any]:
        left = self._parse_additive()
        if left is None:
            return None
        while not self._is_eof():
            tok = self._current()
            if tok.text not in _COMPARISON_OPS:
                break
            op_text = tok.text
            self._advance()
            right = self._parse_additive()
            if right is None:
                return left
            span = self._make_span(left.span.start.byte_offset, right.span.end.byte_offset)
            left = CondExpression(
                node_id=self._make_id(IRKind.EXPRESSION_CONDITION, left.span.start.byte_offset),
                kind=IRKind.EXPRESSION_CONDITION,
                span=span,
                operator_text=op_text,
                left=left,
                right=right,
            )
        return left

    def _parse_additive(self) -> Optional[Any]:
        left = self._parse_multiplicative()
        if left is None:
            return None
        while not self._is_eof():
            tok = self._current()
            if tok.text not in _ADDITIVE_OPS:
                break
            op_text = tok.text
            self._advance()
            right = self._parse_multiplicative()
            if right is None:
                return left
            span = self._make_span(left.span.start.byte_offset, right.span.end.byte_offset)
            left = BinaryOpExpression(
                node_id=self._make_id(IRKind.EXPRESSION_BINARY_OP, left.span.start.byte_offset),
                kind=IRKind.EXPRESSION_BINARY_OP,
                span=span,
                operator_text=op_text,
                left=left,
                right=right,
            )
        return left

    def _parse_multiplicative(self) -> Optional[Any]:
        left = self._parse_unary()
        if left is None:
            return None
        while not self._is_eof():
            tok = self._current()
            if tok.text not in _MULTIPLICATIVE_OPS:
                break
            op_text = tok.text
            self._advance()
            right = self._parse_unary()
            if right is None:
                return left
            span = self._make_span(left.span.start.byte_offset, right.span.end.byte_offset)
            left = BinaryOpExpression(
                node_id=self._make_id(IRKind.EXPRESSION_BINARY_OP, left.span.start.byte_offset),
                kind=IRKind.EXPRESSION_BINARY_OP,
                span=span,
                operator_text=op_text,
                left=left,
                right=right,
            )
        return left

    def _parse_unary(self) -> Optional[Any]:
        if self._is_eof():
            return None
        tok = self._current()
        if tok.text.upper() in _UNARY_OPS:
            op_text = tok.text
            self._advance()
            operand = self._parse_unary()
            if operand is None:
                return None
            span = self._make_span(tok.span.start.byte_offset, operand.span.end.byte_offset)
            return UnaryOpExpression(
                node_id=self._make_id(IRKind.EXPRESSION_UNARY_OP, tok.span.start.byte_offset),
                kind=IRKind.EXPRESSION_UNARY_OP,
                span=span,
                operator_text=op_text,
                operand=operand,
            )
        return self._parse_primary()

    def _parse_primary(self) -> Optional[Any]:
        if self._is_eof():
            return None
        tok = self._current()

        # Parenthesized expression
        if tok.kind == TokenKind.LPAREN:
            self._advance()
            inner = self._parse_expression()
            if self._is_eof() or self._current().kind != TokenKind.RPAREN:
                # Mismatched parens; best-effort return.
                return inner
            self._advance()
            return inner

        # Figurative constant
        if tok.text.upper() in _FIGURATIVE_CONSTANTS:
            return self._consume_figurative(tok)

        # Purely numeric identifier -> INTEGER literal
        if tok.kind == TokenKind.IDENTIFIER and tok.text.isdigit():
            return self._consume_numeric_literal(tok)

        # Otherwise identifier
        if tok.kind in (TokenKind.IDENTIFIER, TokenKind.KEYWORD):
            return self._consume_identifier(tok)

        return None

    # ------------------------------------------------------------------
    # Primary expression consumers
    # ------------------------------------------------------------------

    def _consume_identifier(self, tok: Token) -> IdentifierExpression:
        self._advance()
        return IdentifierExpression(
            node_id=self._make_id(IRKind.EXPRESSION_REFERENCE, tok.span.start.byte_offset),
            kind=IRKind.EXPRESSION_REFERENCE,
            span=tok.span,
            identifier_text=tok.text,
        )

    def _consume_numeric_literal(self, tok: Token) -> LiteralExpression:
        self._advance()
        return LiteralExpression(
            node_id=self._make_id(IRKind.EXPRESSION_LITERAL, tok.span.start.byte_offset),
            kind=IRKind.EXPRESSION_LITERAL,
            span=tok.span,
            literal_raw_text=tok.text,
            literal_kind="INTEGER",
        )

    def _consume_figurative(self, tok: Token) -> LiteralExpression:
        self._advance()
        return LiteralExpression(
            node_id=self._make_id(IRKind.EXPRESSION_LITERAL, tok.span.start.byte_offset),
            kind=IRKind.EXPRESSION_LITERAL,
            span=tok.span,
            literal_raw_text=tok.text,
            literal_kind="FIGURATIVE",
        )

    def _parse_paragraph_name(self) -> Optional[str]:
        if self._is_eof():
            return None
        tok = self._current()
        if tok.kind not in (TokenKind.IDENTIFIER, TokenKind.KEYWORD):
            return None
        text = tok.text
        self._advance()
        return text

    # ------------------------------------------------------------------
    # Helpers — keyword matching, division headers
    # ------------------------------------------------------------------

    def _match_division_header(self) -> Optional[str]:
        """If the current token (and the next, if applicable) match a
        division header, consume them and return the phrase.

        Division headers in free format are single tokens with text
        like 'IDENTIFICATION', 'ENVIRONMENT', etc., or full phrases.
        We handle both single-token and two-token (e.g. 'IDENTIFICATION'
        + 'DIVISION') forms.
        """
        if self._is_eof():
            return None
        tok = self._current()
        text = tok.text.upper()

        # Single-token division header (lexer may emit as one token)
        if text in _DIVISION_HEADERS:
            self._advance()
            return text

        # Two-token form: KEYWORD 'IDENTIFICATION' then KEYWORD 'DIVISION.'
        if text in ("IDENTIFICATION", "ENVIRONMENT", "DATA", "PROCEDURE"):
            peeked = self._peek(1)
            if peeked is not None and peeked.text.upper().startswith("DIVISION"):
                phrase = f"{text} {peeked.text.upper()}"
                # Consume both tokens.
                self._advance()
                self._advance()
                # If the division text was 'DIVISION.' (includes period),
                # don't consume period again.
                return phrase

        return None

    def _match_data_division_subsection_header(
        self,
    ) -> Optional[Tuple[str, IRKind, int, int]]:
        """T-2B-04R.1: Recognize a Data Division subsection header.

        Matches the two-token form ``<SUBSECTION> SECTION.`` (or
        ``<SUBSECTION> SECTION``) at the current cursor.  Returns
        ``(name, kind, start_byte, end_byte)`` on success and
        advances past the two tokens, or ``None`` if the cursor
        is not at a subsection header.

        The recognized subsections are: WORKING-STORAGE, LINKAGE,
        LOCAL-STORAGE, REPORT, FILE.  These are recorded
        syntactically only; no data-item declarations are parsed
        in R.1 (that is T-2B-04R.2 and beyond).
        """
        if self._is_eof():
            return None
        tok = self._current()
        text = tok.text.upper()
        if text not in _DATA_DIVISION_SECTION_KEYWORDS:
            return None
        peeked = self._peek(1)
        if peeked is None:
            return None
        if peeked.text.upper() != "SECTION":
            return None
        # Capture the byte span of the two-token header before
        # advancing the cursor.
        start_byte = tok.span.start.byte_offset
        end_byte = peeked.span.end.byte_offset
        # Consume the subsection keyword and the SECTION keyword.
        self._advance()
        self._advance()
        kind = _DATA_DIVISION_SECTION_KIND[text]
        return (text, kind, start_byte, end_byte)

    def _match_data_item_declaration(
        self,
        in_data_division_subsection: bool,
    ) -> Optional[Tuple[int, str, Optional[str], Optional[str], Optional[PicClause], Optional[UsageClause], Optional[ValueClause], int, int]]:
        """T-2B-04R.2 + T-2B-04R.3: Recognize a Data Item declaration
        with optional PIC, USAGE, and VALUE clauses.

        Matches a COBOL data-item declaration that begins with a
        recognized level number (01-49, 66, 77, 78, 88) followed
        by a data-item name and optional clauses in any order
        (REDEFINES, PIC, USAGE, VALUE).

        R.2 captures only the *syntactic* structure:
          * the level number (as a Python int)
          * the data-item name (verbatim)
          * the optional REDEFINES target name (verbatim, if present)
          * the optional raw PIC text (verbatim, if present)

        R.3 additionally captures structured PIC, USAGE, and VALUE
        clause nodes alongside the raw text.  The raw ``pic_string``
        field is preserved for R.2 compatibility.

        R.2 and R.3 do NOT:
          * resolve any name to a symbol
          * interpret the PIC clause
          * compute storage layout
          * validate REDEFINES semantics
          * construct parent / child hierarchy
        """
        if not in_data_division_subsection:
            return None
        if self._is_eof():
            return None
        tok = self._current()
        # The level number is an IDENTIFIER token whose text is
        # exactly one of the recognized level strings.
        if tok.kind != TokenKind.IDENTIFIER:
            return None
        if tok.text not in _DATA_ITEM_LEVEL_NUMBERS:
            return None
        level = int(tok.text)
        start_byte = tok.span.start.byte_offset

        # Advance past the level number.
        self._advance()

        # The data-item name MUST be present.  It is an
        # IDENTIFIER token (COBOL names may include hyphens).
        if self._is_eof():
            return None
        name_tok = self._current()
        if name_tok.kind != TokenKind.IDENTIFIER:
            return None
        name = name_tok.text
        self._advance()

        # Optional REDEFINES or RENAMES clause.
        redefines_target: Optional[str] = None
        if (
            not self._is_eof()
            and self._current().kind == TokenKind.KEYWORD
            and self._current().text.upper() in ("REDEFINES", "RENAMES")
        ):
            self._advance()
            if not self._is_eof() and self._current().kind == TokenKind.IDENTIFIER:
                redefines_target = self._current().text
                self._advance()

        # R.3: Optional PIC / PICTURE / USAGE / VALUE clauses in
        # any order.  Each clause is parsed structurally but no
        # semantic interpretation is performed.
        pic_string: Optional[str] = None
        pic_clause_node: Optional[PicClause] = None
        usage_clause_node: Optional[UsageClause] = None
        value_clause_node: Optional[ValueClause] = None

        # Continue consuming clauses until we reach the trailing
        # period.  The order of clauses is not enforced by R.3
        # (COBOL allows PIC, USAGE, VALUE in any order with
        # REDEFINES).
        while not self._is_eof() and self._current().kind != TokenKind.PERIOD:
            cur = self._current()

            # Handle PIC / PICTURE clause.
            if cur.kind == TokenKind.KEYWORD and cur.text.upper() in ("PIC", "PICTURE"):
                if pic_string is not None:
                    # Duplicate PIC clause: stop processing
                    # additional clauses (fall through to the
                    # normal parser dispatch for the second one).
                    break
                pic_string, pic_clause_node = self._parse_pic_clause()
                continue

            # Handle USAGE clause.
            if cur.kind == TokenKind.KEYWORD and cur.text.upper() == "USAGE":
                if usage_clause_node is not None:
                    # Duplicate USAGE clause.
                    break
                usage_clause_node = self._parse_usage_clause()
                continue

            # Handle VALUE clause.
            if cur.kind == TokenKind.KEYWORD and cur.text.upper() == "VALUE":
                if value_clause_node is not None:
                    # Duplicate VALUE clause.
                    break
                value_clause_node = self._parse_value_clause()
                continue

            # Unknown clause-starting keyword: stop processing
            # additional clauses so the unknown token can be
            # handled by the normal parser dispatch (which will
            # produce an "unknown token" diagnostic).
            break

        # The trailing period ends the declaration.
        if not self._is_eof() and self._current().kind == TokenKind.PERIOD:
            self._advance()

        end_byte = self._last_consumed_end_byte()
        if end_byte is None:
            end_byte = start_byte

        return (
            level,
            name,
            redefines_target,
            pic_string,
            pic_clause_node,
            usage_clause_node,
            value_clause_node,
            start_byte,
            end_byte,
        )

    def _parse_pic_clause(
        self,
    ) -> Tuple[Optional[str], Optional[PicClause]]:
        """T-2B-04R.3: Parse a PIC / PICTURE clause.

        Returns ``(raw_text, PicClause)``.  The raw text is the
        concatenation of the PIC tokens.  The PicClause captures
        structural elements: category, size, sign, scale.

        A PIC keyword with no following PIC content (e.g. ``PIC .``)
        returns ``(None, None)`` so the declaration keeps
        ``pic_string=None``; R.3 never fabricates an empty PIC
        string.
        """
        pic_start = self._current().span.start.byte_offset
        self._advance()  # consume PIC / PICTURE
        pic_tokens: List[str] = []
        while not self._is_eof():
            cur = self._current()
            if cur.kind == TokenKind.PERIOD:
                break
            if cur.kind == TokenKind.KEYWORD and cur.text.upper() in (
                "USAGE", "VALUE", "REDEFINES", "OCCURS", "RENAMES",
            ):
                break
            pic_tokens.append(cur.text)
            self._advance()
        pic_raw = "".join(pic_tokens)
        if not pic_raw:
            return None, None
        # Structural decomposition of the PIC string.
        category, sign, size, scale = self._decompose_pic(pic_raw)
        pic_end = self._last_consumed_end_byte()
        if pic_end is None:
            pic_end = pic_start
        pic_span = self._make_span(pic_start, pic_end)
        pic_id = self._make_id(IRKind.PIC_CLAUSE, pic_start)
        node = PicClause(
            node_id=pic_id,
            kind=IRKind.PIC_CLAUSE,
            span=pic_span,
            raw_text=pic_raw,
            category=category,
            size=size,
            sign=sign,
            scale=scale,
        )
        return pic_raw, node

    def _decompose_pic(
        self, pic_raw: str
    ) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
        """T-2B-04R.3: Decompose a PIC string into its structural
        elements.

        Returns ``(category, sign, size, scale)``.  The category
        captures the leading alphanumeric run; ``S`` at the start
        indicates signed.  The size is the content in parentheses;
        the scale is the content after the ``V`` decimal-point
        marker.
        """
        sign: Optional[str] = None
        rest = pic_raw
        if rest.startswith("S"):
            sign = "S"
            rest = rest[1:]
        # Split on V to separate the integer and decimal parts.
        if "V" in rest:
            int_part, _, dec_part = rest.partition("V")
            category = int_part
            scale = dec_part
        else:
            category = rest
            scale = None
        # Extract the size in parentheses, if present.
        size: Optional[str] = None
        if "(" in category and category.endswith(")"):
            open_idx = category.index("(")
            size = category[open_idx + 1:-1]
            category = category[:open_idx]
        return category or None, sign, size, scale

    def _parse_usage_clause(self) -> Optional[UsageClause]:
        """T-2B-04R.3: Parse a USAGE clause.

        Supports both ``USAGE <form>`` and ``USAGE IS <form>``.
        Returns the structured UsageClause node, or ``None`` when
        the form is not in the recognized vocabulary (R.3 records
        only recognized forms; unrecognized forms fall through to
        the normal parser dispatch, which produces diagnostics).

        R.3 does NOT interpret the usage form (storage layout,
        COMP/COMP-3 encoding, Java type); that is T-2B-08's
        responsibility.
        """
        usage_start = self._current().span.start.byte_offset
        self._advance()  # consume USAGE
        # Optional ``IS`` connector between USAGE and the form
        # (e.g. ``USAGE IS BINARY``).  ``IS`` is a single KEYWORD
        # token.
        if (
            not self._is_eof()
            and self._current().kind == TokenKind.KEYWORD
            and self._current().text.upper() == "IS"
        ):
            self._advance()
        # The usage form is a single KEYWORD or IDENTIFIER token
        # (e.g. ``DISPLAY``, ``COMP``, ``COMP-3``, ``BINARY``,
        # ``PACKED-DECIMAL``).  Hyphenated forms such as COMP-3 are
        # single keyword tokens produced by the frozen T-2B-02
        # lexer.
        if self._is_eof():
            return None
        cur = self._current()
        if cur.kind not in (TokenKind.KEYWORD, TokenKind.IDENTIFIER):
            return None
        usage_form = cur.text.upper()
        if usage_form not in _USAGE_FORMS:
            # Unknown usage form: do not produce a UsageClause
            # node.  R.3's minimal syntax layer only records
            # recognized forms.  The tokens are left in the
            # stream and the normal parser dispatch will
            # produce diagnostics.
            return None
        self._advance()  # consume the usage form token
        usage_end = self._last_consumed_end_byte()
        if usage_end is None:
            usage_end = usage_start + len("USAGE")
        usage_span = self._make_span(usage_start, usage_end)
        usage_id = self._make_id(IRKind.USAGE_CLAUSE, usage_start)
        return UsageClause(
            node_id=usage_id,
            kind=IRKind.USAGE_CLAUSE,
            span=usage_span,
            raw_text=usage_form,
            usage_form=usage_form,
        )

    def _parse_value_clause(self) -> Optional[ValueClause]:
        """T-2B-04R.3: Parse a VALUE clause.

        Returns the structured ValueClause node.  R.3 does not
        interpret the literal value; that is T-2B-08's
        responsibility.
        """
        value_start = self._current().span.start.byte_offset
        self._advance()  # consume VALUE
        if self._is_eof():
            return None
        cur = self._current()
        if cur.kind == TokenKind.PERIOD:
            return None
        # Capture the literal token as the value.  This is the
        # lexer-observable content: quote delimiters (if any) were
        # already dropped by the frozen T-2B-02 lexer, so exact
        # source spelling is NOT preserved (see the ValueClause
        # contract).
        literal_raw = cur.text
        literal_kind = self._classify_value_literal(literal_raw)
        self._advance()
        value_end = self._last_consumed_end_byte()
        if value_end is None:
            value_end = value_start + len("VALUE")
        value_span = self._make_span(value_start, value_end)
        value_id = self._make_id(IRKind.VALUE_CLAUSE, value_start)
        return ValueClause(
            node_id=value_id,
            kind=IRKind.VALUE_CLAUSE,
            span=value_span,
            raw_text=literal_raw,
            literal_kind=literal_kind,
            literal_value=literal_raw,
        )

    @staticmethod
    def _classify_value_literal(literal: str) -> str:
        """T-2B-04R.3: Classify a VALUE literal syntactically.

        The frozen T-2B-02 lexer drops quote delimiters before the
        parser sees them, so R.3 only observes the token content.
        Returns ``"numeric"`` for a digits-only literal and
        ``"alphanumeric"`` otherwise.  Quote style is not available
        to R.3 and is never fabricated.
        """
        if not literal:
            return "alphanumeric"
        if all(c.isdigit() for c in literal):
            return "numeric"
        return "alphanumeric"

    def _expect_keyword(self, text: str) -> Token:
        """Consume the current token if it matches (case-insensitive)
        the keyword *text* and has kind KEYWORD.

        Raises ValueError if the token doesn't match — the parser
        should always check via dispatch before calling expect.
        """
        if self._is_eof():
            raise ValueError(f"expected {text!r}, got EOF")
        tok = self._current()
        if tok.text.upper() != text.upper():
            raise ValueError(f"expected {text!r}, got {tok.text!r}")
        self._advance()
        return tok

    def _consume_period(self) -> bool:
        """If current token is a period, consume it and return True.
        Otherwise return False (period is optional in some contexts)."""
        if self._is_eof():
            return False
        if self._current().kind == TokenKind.PERIOD:
            self._advance()
            return True
        return False

    def _last_consumed_end_byte(self) -> Optional[int]:
        """Return the end byte of the most recently consumed token, if any."""
        idx = self._pos - 1
        if idx < 0 or idx >= len(self._tokens):
            return None
        return self._tokens[idx].span.end.byte_offset

    def _current_span_start(self) -> int:
        """Return the start byte of the current token (or byte_size at EOF)."""
        if self._is_eof():
            return self._byte_size
        return self._current().span.start.byte_offset

    # ------------------------------------------------------------------
    # Synchronization / recovery
    # ------------------------------------------------------------------

    def _sync_after_statement(self) -> None:
        """Advance past tokens until the next safe synchronization
        point: Period, EOF, or one of the structural control
        keywords.
        """
        sync_keys = {
            "IF", "EVALUATE", "PERFORM", "GO", "STOP", "GOBACK",
            "ELSE", "END-IF", "WHEN", "END-EVALUATE",
        }
        while not self._is_eof():
            tok = self._current()
            if tok.kind == TokenKind.PERIOD:
                self._advance()
                return
            if tok.text.upper() in sync_keys:
                return
            self._advance()

    def _classify_unsupported(self, text_upper: str) -> Optional[str]:
        """Return a human-readable name if *text_upper* identifies an
        unsupported construct, else None."""
        unsupported_map = {
            "EXEC": "EXEC SQL / EXEC CICS",
            "READ": "READ",
            "WRITE": "WRITE",
            "REWRITE": "REWRITE",
            "DELETE": "DELETE",
            "START": "START",
            "SORT": "SORT",
            "MERGE": "MERGE",
        }
        if text_upper in unsupported_map:
            return unsupported_map[text_upper]
        return None

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def _diagnose_missing(self, verb: str, what: str) -> Diagnostic:
        tok = self._current() if not self._is_eof() else None
        span = tok.span if tok else self._make_span(self._byte_size, self._byte_size)
        return Diagnostic(
            severity=DiagnosticSeverity.ERROR,
            kind=DiagnosticKind.PARSER_RECOVERY,
            message=f"{verb}: missing {what}",
            span=span,
        )

    def _diagnose_unexpected_eof(self, verb: str) -> Diagnostic:
        return Diagnostic(
            severity=DiagnosticSeverity.ERROR,
            kind=DiagnosticKind.PARSER_RECOVERY,
            message=f"{verb}: unexpected EOF before completion",
            span=self._make_span(self._byte_size, self._byte_size),
        )

    def _diagnose_unknown(self, tok: Token) -> Diagnostic:
        return Diagnostic(
            severity=DiagnosticSeverity.ERROR,
            kind=DiagnosticKind.PARSER_RECOVERY,
            message=f"unknown token: {tok.text!r}",
            span=tok.span,
        )

    def _diagnose_misplaced(self, phrase: str) -> Diagnostic:
        tok = self._current()
        return Diagnostic(
            severity=DiagnosticSeverity.ERROR,
            kind=DiagnosticKind.PARSER_RECOVERY,
            message=f"misplaced scope terminator: {phrase!r}",
            span=tok.span,
        )

    # ------------------------------------------------------------------
    # Span / ID construction
    # ------------------------------------------------------------------

    def _make_span(self, start_byte: int, end_byte: int) -> SourceSpan:
        start_pos = SourcePosition(
            line=1,  # simplified: line/column metadata available via
                     # tokens but for T-2B-03 we expose a basic
                     # SourceSpan.  Later phases can refine this.
            column=start_byte,
            byte_offset=start_byte,
        )
        end_pos = SourcePosition(
            line=1,
            column=end_byte,
            byte_offset=end_byte,
        )
        return SourceSpan(
            canonical_path=self._canonical_path,
            start=start_pos,
            end=end_pos,
        )

    def _make_id(
        self,
        kind: IRKind,
        byte_offset: int,
        column: int = 0,
        line: int = 1,
    ) -> DeterministicId:
        return id_for_node(
            kind=kind.value,
            canonical_path=self._canonical_path,
            line=line,
            column=column,
            byte_offset=byte_offset,
            ordinal=0,
        )


# ==================================================================
# Module-level constants
# ==================================================================

# A minimal placeholder for the EOF sentinel when the token stream
# is empty.  The parser should never see this in normal operation.
_EMPTY_EOF: Final[Token] = Token(
    kind=TokenKind.IDENTIFIER,
    text="",
    span=SourceSpan(
        canonical_path="source.cbl",
        start=SourcePosition(line=1, column=0, byte_offset=0),
        end=SourcePosition(line=1, column=0, byte_offset=0),
    ),
    debug=False,
)


# Module exports
__all__ = ["Parser"]
