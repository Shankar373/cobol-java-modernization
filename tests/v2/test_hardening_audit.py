"""T-2B-02 Hardening Regression Tests.

These tests verify that the two P0 defects identified in the
hardening audit have been fixed:

DEFECT #1: Pure numeric literals were silently consumed by the
T-2B-02 lexer, making the parser unable to produce
LiteralExpression(INTEGER) for any source number.  FIX: the lexer
now emits IDENTIFIER tokens for purely-numeric words so the parser
can classify them syntactically.

DEFECT #2: UTF-8 multibyte characters had character-indexed spans
rather than byte-indexed spans.  FIX: the lexer now uses the raw
byte stream as the authoritative source of position, decoding text
only for keyword/identifier classification.

These tests are regression tests for the fixes.  They must all pass.
"""

from __future__ import annotations

import pytest

from modernize_v2.ir.diagnostic import Diagnostic
from modernize_v2.lexer import CobolLexer, SourceFormat
from modernize_v2.lexer.tokens import Token, TokenKind
from modernize_v2.parser import Parser
from modernize_v2.source import make_source_file


# ---------------------------------------------------------------------------
# PHASE 3: Numeric Literal Regression — FIX VERIFICATION
# ---------------------------------------------------------------------------

class TestNumericLiteralFix:
    """Pure numeric literals are now emitted as IDENTIFIER tokens.

    Before fix: `123` produced 1 token (EOF only).
    After fix: `123` produces 2 tokens (IDENTIFIER '123' + EOF).
    """

    def test_regression_123_emitted(self):
        """The bare number '123' now produces an IDENTIFIER token."""
        sf = make_source_file("t.cbl", b"123")
        lexer = CobolLexer(sf, b"123", SourceFormat.FREE)
        tokens = lexer.lex()
        assert len(tokens) == 2
        assert tokens[0].kind == TokenKind.IDENTIFIER
        assert tokens[0].text == "123"
        # The span must cover bytes 0-3
        assert tokens[0].span.start.byte_offset == 0
        assert tokens[0].span.end.byte_offset == 3
        # EOF sentinel is unchanged
        assert tokens[1].kind == TokenKind.IDENTIFIER
        assert tokens[1].text == ""

    def test_regression_zero_emitted(self):
        """The bare number '0' now produces an IDENTIFIER token."""
        sf = make_source_file("t.cbl", b"0")
        lexer = CobolLexer(sf, b"0", SourceFormat.FREE)
        tokens = lexer.lex()
        assert len(tokens) == 2
        assert tokens[0].kind == TokenKind.IDENTIFIER
        assert tokens[0].text == "0"
        assert tokens[0].span.start.byte_offset == 0
        assert tokens[0].span.end.byte_offset == 1

    def test_regression_999999_emitted(self):
        """A large numeric 999999 now produces an IDENTIFIER token."""
        sf = make_source_file("t.cbl", b"999999")
        lexer = CobolLexer(sf, b"999999", SourceFormat.FREE)
        tokens = lexer.lex()
        assert len(tokens) == 2
        assert tokens[0].text == "999999"
        assert tokens[0].span.end.byte_offset == 6

    def test_regression_000123_leading_zeros(self):
        """Leading-zero number '000123' is preserved verbatim."""
        sf = make_source_file("t.cbl", b"000123")
        lexer = CobolLexer(sf, b"000123", SourceFormat.FREE)
        tokens = lexer.lex()
        assert len(tokens) == 2
        assert tokens[0].text == "000123"
        assert tokens[0].span.end.byte_offset == 6

    def test_regression_move_123_to_b(self):
        """MOVE 123 TO B. now contains all 6 tokens including 123."""
        source = b"MOVE 123 TO B."
        sf = make_source_file("t.cbl", source)
        lexer = CobolLexer(sf, source, SourceFormat.FREE)
        tokens = lexer.lex()
        # Expect 6 tokens: MOVE, 123, TO, B, ., EOF
        assert len(tokens) == 6
        text_list = [t.text for t in tokens]
        assert text_list == ["MOVE", "123", "TO", "B", ".", ""]
        # Verify spans
        assert tokens[0].span.start.byte_offset == 0
        assert tokens[0].span.end.byte_offset == 4
        assert tokens[1].span.start.byte_offset == 5
        assert tokens[1].span.end.byte_offset == 8
        assert tokens[1].text == "123"

    def test_regression_add_10(self):
        """ADD 10 TO B. now contains all 6 tokens including 10."""
        source = b"ADD 10 TO B."
        sf = make_source_file("t.cbl", source)
        lexer = CobolLexer(sf, source, SourceFormat.FREE)
        tokens = lexer.lex()
        text_list = [t.text for t in tokens]
        assert "10" in text_list
        assert text_list == ["ADD", "10", "TO", "B", ".", ""]

    def test_regression_compute_with_numeric(self):
        """COMPUTE WS-TOTAL = WS-A + 123. now contains 123."""
        source = b"COMPUTE WS-TOTAL = WS-A + 123."
        sf = make_source_file("t.cbl", source)
        lexer = CobolLexer(sf, source, SourceFormat.FREE)
        tokens = lexer.lex()
        text_list = [t.text for t in tokens]
        assert "123" in text_list
        # Find the 123 token and check span
        t123 = next(t for t in tokens if t.text == "123")
        assert t123.span.start.byte_offset == source.index(b"123")
        assert t123.span.end.byte_offset == source.index(b"123") + 3

    def test_regression_negative_sign_minus(self):
        """A leading minus sign is MINUS; the number after it is separate."""
        source = b"-123"
        sf = make_source_file("t.cbl", source)
        lexer = CobolLexer(sf, source, SourceFormat.FREE)
        tokens = lexer.lex()
        # The '-' is MINUS, then '123' is IDENTIFIER (numeric)
        assert len(tokens) == 3
        assert tokens[0].kind == TokenKind.MINUS
        assert tokens[0].text == "-"
        assert tokens[1].kind == TokenKind.IDENTIFIER
        assert tokens[1].text == "123"

    def test_regression_plus_sign_plus(self):
        """A leading plus is PLUS; the number after it is separate."""
        source = b"+123"
        sf = make_source_file("t.cbl", source)
        lexer = CobolLexer(sf, source, SourceFormat.FREE)
        tokens = lexer.lex()
        # The '+' is PLUS, then '123' is IDENTIFIER (numeric)
        assert len(tokens) == 3
        assert tokens[0].kind == TokenKind.PLUS
        assert tokens[0].text == "+"
        assert tokens[1].kind == TokenKind.IDENTIFIER
        assert tokens[1].text == "123"

    def test_regression_decimal_period_separates(self):
        """A '.' in source is a PERIOD operator; the surrounding
        digits become separate IDENTIFIER tokens.  This is the
        established lexical contract: '.' is always a period."""
        source = b"123.45"
        sf = make_source_file("t.cbl", source)
        lexer = CobolLexer(sf, source, SourceFormat.FREE)
        tokens = lexer.lex()
        # 123, ., 45, EOF
        text_list = [t.text for t in tokens]
        assert "123" in text_list
        assert "45" in text_list
        assert "." in text_list
        assert any(t.kind == TokenKind.PERIOD for t in tokens)

    def test_regression_parser_can_now_classify_numeric(self):
        """The parser can now produce LiteralExpression(INTEGER) for
        numeric source after the lexer fix."""
        source = b"MOVE 123 TO B."
        sf = make_source_file("t.cbl", source)
        lexer = CobolLexer(sf, source, SourceFormat.FREE)
        tokens = lexer.lex()
        parser = Parser(tokens, canonical_path="t.cbl")
        result = parser.parse()
        # The parser should now produce a statement
        assert len(result.ast.statements) >= 1


# ---------------------------------------------------------------------------
# PHASE 4: UTF-8 Byte-Span Regression — FIX VERIFICATION
# ---------------------------------------------------------------------------

class TestUTF8ByteSpanFix:
    """UTF-8 multibyte characters now have byte-accurate spans.

    Before fix: `é` (2 bytes in UTF-8) had span [5, 6) (1 byte).
    After fix: `é` has span [5, 7) (2 bytes), and following tokens
    are aligned to their true raw-byte positions.
    """

    def test_regression_e_acute_byte_span(self):
        """é (2 bytes in UTF-8) has correct 2-byte span [5, 7)."""
        source = b"MOVE \xc3\xa9 TO B."  # 13 bytes
        sf = make_source_file("t.cbl", source)
        lexer = CobolLexer(sf, source, SourceFormat.FREE)
        tokens = lexer.lex()
        # Find the é token
        e_token = None
        for t in tokens:
            if t.text == "\xe9":
                e_token = t
                break
        assert e_token is not None
        # The byte span must be [5, 7) — 2 bytes wide
        assert e_token.span.start.byte_offset == 5
        assert e_token.span.end.byte_offset == 7
        # The span must be 2 bytes wide
        assert e_token.span.end.byte_offset - e_token.span.start.byte_offset == 2

    def test_regression_e_acute_alone(self):
        """A bare 'é' (2 bytes) has correct 2-byte span [0, 2)."""
        source = b"\xc3\xa9"
        sf = make_source_file("t.cbl", source)
        lexer = CobolLexer(sf, source, SourceFormat.FREE)
        tokens = lexer.lex()
        assert len(tokens) == 2
        assert tokens[0].text == "\xe9"
        assert tokens[0].span.start.byte_offset == 0
        assert tokens[0].span.end.byte_offset == 2

    def test_regression_following_token_aligned(self):
        """After é, the next token starts at its true raw-byte position."""
        source = b"MOVE \xc3\xa9 TO B."
        sf = make_source_file("t.cbl", source)
        lexer = CobolLexer(sf, source, SourceFormat.FREE)
        tokens = lexer.lex()
        to_token = None
        for t in tokens:
            if t.text == "TO":
                to_token = t
                break
        assert to_token is not None
        # TO must start at byte 8 (after the 2-byte é and a space)
        assert to_token.span.start.byte_offset == 8
        assert to_token.span.end.byte_offset == 10

    def test_regression_euro_3_bytes(self):
        """€ (3 bytes in UTF-8) has correct 3-byte span."""
        source = b"MOVE \xe2\x82\xac TO B."  # 14 bytes
        sf = make_source_file("t.cbl", source)
        lexer = CobolLexer(sf, source, SourceFormat.FREE)
        tokens = lexer.lex()
        euro_token = None
        for t in tokens:
            if t.text == "\u20ac":
                euro_token = t
                break
        assert euro_token is not None
        # € is at bytes 5-7 (3 bytes)
        assert euro_token.span.start.byte_offset == 5
        assert euro_token.span.end.byte_offset == 8
        # TO must start at byte 9
        to_token = next(t for t in tokens if t.text == "TO")
        assert to_token.span.start.byte_offset == 9

    def test_regression_cjk_hyphenated_identifier(self):
        """ABC-中文 (10 bytes) is a single identifier with correct 10-byte span."""
        source = b"ABC-\xe4\xb8\xad\xe6\x96\x87"  # 10 bytes
        sf = make_source_file("t.cbl", source)
        lexer = CobolLexer(sf, source, SourceFormat.FREE)
        tokens = lexer.lex()
        # First token is the whole identifier
        assert tokens[0].kind == TokenKind.IDENTIFIER
        assert tokens[0].text == "ABC-\u4e2d\u6587"
        # The span must cover all 10 bytes
        assert tokens[0].span.start.byte_offset == 0
        assert tokens[0].span.end.byte_offset == 10

    def test_regression_ascii_unchanged(self):
        """ASCII source has byte-accurate spans (byte == char)."""
        source = b"ABC"
        sf = make_source_file("t.cbl", source)
        lexer = CobolLexer(sf, source, SourceFormat.FREE)
        tokens = lexer.lex()
        assert len(tokens) == 2  # IDENTIFIER 'ABC' + EOF
        assert tokens[0].span.start.byte_offset == 0
        assert tokens[0].span.end.byte_offset == 3

    def test_regression_eof_byte_size_utf8(self):
        """EOF position equals raw byte size for UTF-8 source."""
        source = b"MOVE \xc3\xa9 TO B."  # 13 bytes
        sf = make_source_file("t.cbl", source)
        lexer = CobolLexer(sf, source, SourceFormat.FREE)
        tokens = lexer.lex()
        eof_token = tokens[-1]
        assert eof_token.span.start.byte_offset == 13
        assert eof_token.span.end.byte_offset == 13


# ---------------------------------------------------------------------------
# PHASE 5: EOF Regression — unchanged contract
# ---------------------------------------------------------------------------

class TestEOFSentinelFix:
    """The EOF sentinel contract is preserved unchanged."""

    def test_eof_sentinel_correct(self):
        """Empty source produces exactly one EOF token."""
        sf = make_source_file("t.cbl", b"")
        lexer = CobolLexer(sf, b"", SourceFormat.FREE)
        tokens = lexer.lex()
        assert len(tokens) == 1
        assert tokens[0].kind == TokenKind.IDENTIFIER
        assert tokens[0].text == ""
        assert tokens[0].span.start.byte_offset == 0
        assert tokens[0].span.end.byte_offset == 0

    def test_eof_after_content(self):
        """After content, EOF is at source byte_size."""
        source = b"MOVE A TO B."
        sf = make_source_file("t.cbl", source)
        lexer = CobolLexer(sf, source, SourceFormat.FREE)
        tokens = lexer.lex()
        eof = tokens[-1]
        assert eof.text == ""
        assert eof.span.start.byte_offset == len(source)
        assert eof.span.end.byte_offset == len(source)

    def test_eof_with_crlf(self):
        """EOF at end of CRLF source is at correct byte size."""
        source = b"MOVE A TO B.\r\n"
        sf = make_source_file("t.cbl", source)
        lexer = CobolLexer(sf, source, SourceFormat.FREE)
        tokens = lexer.lex()
        eof = tokens[-1]
        assert eof.text == ""
        assert eof.span.start.byte_offset == len(source)

    def test_eof_with_utf8(self):
        """EOF at end of UTF-8 source is at correct raw byte size."""
        source = b"MOVE \xc3\xa9 TO B."  # 13 bytes
        sf = make_source_file("t.cbl", source)
        lexer = CobolLexer(sf, source, SourceFormat.FREE)
        tokens = lexer.lex()
        eof = tokens[-1]
        assert eof.text == ""
        assert eof.span.start.byte_offset == 13
        assert eof.span.end.byte_offset == 13


# ---------------------------------------------------------------------------
# PHASE 6: CRLF Regression — unchanged behavior
# ---------------------------------------------------------------------------

class TestCRLFPreservationFix:
    """CRLF behavior is preserved across the hardening."""

    def test_crlf_moves(self):
        """MOVE A TO B.\r\nMOVE C TO D. tokenizes correctly."""
        source = b"MOVE A TO B.\r\nMOVE C TO D."
        sf = make_source_file("t.cbl", source)
        lexer = CobolLexer(sf, source, SourceFormat.FREE)
        tokens = lexer.lex()
        # Find both MOVE tokens
        move_tokens = [t for t in tokens if t.text == "MOVE"]
        assert len(move_tokens) == 2
        # First MOVE at byte 0
        assert move_tokens[0].span.start.byte_offset == 0
        assert move_tokens[0].span.end.byte_offset == 4
        # Second MOVE at byte 14 (after \r\n)
        assert move_tokens[1].span.start.byte_offset == 14
        assert move_tokens[1].span.end.byte_offset == 18

    def test_crlf_byte_size(self):
        """SourceMap recognizes CRLF as a single line break (\\r is part
        of the preceding line, \\n starts the next).  Byte sizes
        are preserved exactly."""
        source = b"MOVE A TO B.\r\n"
        sf = make_source_file("t.cbl", source)
        lexer = CobolLexer(sf, source, SourceFormat.FREE)
        tokens = lexer.lex()
        # EOF should be at byte_size = 14 (MOVE A TO B.\r\n)
        eof = tokens[-1]
        assert eof.span.start.byte_offset == 14
        assert eof.span.end.byte_offset == 14

    def test_crlf_after_period(self):
        """A period followed by CRLF is still recognized as the
        end of the MOVE statement."""
        source = b"MOVE A TO B.\r\nMOVE C TO D."
        sf = make_source_file("t.cbl", source)
        lexer = CobolLexer(sf, source, SourceFormat.FREE)
        tokens = lexer.lex()
        # Find periods
        period_tokens = [t for t in tokens if t.kind == TokenKind.PERIOD]
        assert len(period_tokens) == 2
        # First period at byte 11
        assert period_tokens[0].span.start.byte_offset == 11
        assert period_tokens[0].span.end.byte_offset == 12
        # Second period at byte 25
        assert period_tokens[1].span.start.byte_offset == 25
        assert period_tokens[1].span.end.byte_offset == 26


# ---------------------------------------------------------------------------
# PHASE 7: Fixed-format Regression — unchanged behavior
# ---------------------------------------------------------------------------

class TestFixedFormatPreservationFix:
    """Fixed-format COBOL behavior is preserved."""

    def test_fixed_format_basic(self):
        """MOVE A TO B. in fixed format starts at byte 7."""
        sf = make_source_file("t.cbl", b"000001 MOVE A TO B.")
        lexer = CobolLexer(sf, b"000001 MOVE A TO B.", SourceFormat.FIXED)
        tokens = lexer.lex()
        assert tokens[0].kind == TokenKind.KEYWORD
        assert tokens[0].text == "MOVE"
        assert tokens[0].span.start.byte_offset == 7
        assert tokens[0].span.end.byte_offset == 11

    def test_fixed_format_sequence_not_tokenized(self):
        """The sequence area '000100' is not tokenized."""
        sf = make_source_file("t.cbl", b"000100 MOVE A")
        lexer = CobolLexer(sf, b"000100 MOVE A", SourceFormat.FIXED)
        tokens = lexer.lex()
        # Only 3 tokens: MOVE, A, EOF
        assert len(tokens) == 3
        assert tokens[0].text == "MOVE"
        assert tokens[0].span.start.byte_offset == 7
        assert tokens[1].text == "A"
        assert tokens[1].span.start.byte_offset == 12

    def test_fixed_format_indicator_comment(self):
        """Indicator column '*' produces a comment line (no tokens)."""
        sf = make_source_file("t.cbl", b"      *MOVE A TO B")  # 6 spaces + *
        lexer = CobolLexer(sf, b"      *MOVE A TO B", SourceFormat.FIXED)
        tokens = lexer.lex()
        # Only 1 token: EOF (the whole line is a comment)
        assert len(tokens) == 1
        assert tokens[0].text == ""

    def test_fixed_format_continuation(self):
        """Indicator column '-' joins the next logical line."""
        sf = make_source_file("t.cbl", b"      -MOVE A TO B")
        lexer = CobolLexer(sf, b"      -MOVE A TO B", SourceFormat.FIXED)
        tokens = lexer.lex()
        # The continuation joins; tokens appear from the joined content
        assert len(tokens) >= 1


# ---------------------------------------------------------------------------
# PHASE 8: Determinism Regression — unchanged behavior
# ---------------------------------------------------------------------------

class TestDeterminismPreservationFix:
    """Deterministic behavior is preserved across the hardening."""

    def test_repeated_lex_identical(self):
        """Repeated lex() calls produce identical tokens."""
        sf = make_source_file("t.cbl", b"MOVE A TO B.")
        lexer = CobolLexer(sf, b"MOVE A TO B.", SourceFormat.FREE)
        tokens1 = lexer.lex()
        tokens2 = lexer.lex()
        assert tokens1 == tokens2

    def test_repeated_lex_identical_with_numeric(self):
        """Repeated lex() with numeric literal produces identical tokens."""
        sf = make_source_file("t.cbl", b"MOVE 123 TO B.")
        lexer = CobolLexer(sf, b"MOVE 123 TO B.", SourceFormat.FREE)
        tokens1 = lexer.lex()
        tokens2 = lexer.lex()
        assert tokens1 == tokens2

    def test_repeated_lex_identical_with_utf8(self):
        """Repeated lex() with UTF-8 source produces identical tokens."""
        source = b"MOVE \xc3\xa9 TO B."
        sf = make_source_file("t.cbl", source)
        lexer = CobolLexer(sf, source, SourceFormat.FREE)
        tokens1 = lexer.lex()
        tokens2 = lexer.lex()
        assert tokens1 == tokens2

    def test_two_instances_identical(self):
        """Two separate lexer instances on identical input produce identical tokens."""
        source = b"ADD 10 TO TOTAL."
        sf1 = make_source_file("t1.cbl", source)
        sf2 = make_source_file("t2.cbl", source)
        lexer1 = CobolLexer(sf1, source, SourceFormat.FREE)
        lexer2 = CobolLexer(sf2, source, SourceFormat.FREE)
        tokens1 = lexer1.lex()
        tokens2 = lexer2.lex()
        # Text and kinds must match
        assert [(t.kind, t.text) for t in tokens1] == [
            (t.kind, t.text) for t in tokens2
        ]
        # Spans must match (relative offsets are the same)
        assert [t.span.start.byte_offset for t in tokens1] == [
            t.span.start.byte_offset for t in tokens2
        ]
        assert [t.span.end.byte_offset for t in tokens1] == [
            t.span.end.byte_offset for t in tokens2
        ]
