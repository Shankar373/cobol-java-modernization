"""P1-003: DISPLAY Comparator Normalization Hardening Unit Tests.

Verifies that normalize_display():
1. Normalizes CRLF (\\r\\n) to LF (\\n).
2. Strictly preserves leading spaces (prevents false-pass on indentation/margin shifts).
3. Strictly preserves trailing spaces/padding (prevents false-pass on truncated fields).
4. Strictly preserves multiple internal spaces (prevents false-pass on column misalignment).
5. Strictly preserves internal blank lines (prevents false-pass on dropped lines/headers).
6. Handles empty input cleanly.
"""

import pytest
from tests.utils.parity_harness import normalize_display, compare_raw_bytes


def test_crlf_lf_equivalence():
    """Case E: CRLF and LF representations of identical text are equivalent."""
    cobol = b"LINE1\r\nLINE2\r\nLINE3\r\n"
    java = b"LINE1\nLINE2\nLINE3\n"
    assert normalize_display(cobol) == normalize_display(java)
    mismatch = compare_raw_bytes("stdout", normalize_display(cobol), normalize_display(java))
    assert mismatch is None


def test_leading_space_mismatch_detected():
    """Case A: Leading spaces indicate positional indentation and must not be stripped."""
    cobol = b"    TOTAL 100\n"
    java = b"TOTAL 100\n"
    assert normalize_display(cobol) != normalize_display(java)
    mismatch = compare_raw_bytes("stdout", normalize_display(cobol), normalize_display(java))
    assert mismatch is not None
    assert mismatch.target == "stdout"


def test_trailing_padding_mismatch_detected():
    """Case B: Trailing padding in fixed-width fields must not be stripped."""
    cobol = b"NAME    \n"
    java = b"NAME\n"
    assert normalize_display(cobol) != normalize_display(java)
    mismatch = compare_raw_bytes("stdout", normalize_display(cobol), normalize_display(java))
    assert mismatch is not None


def test_multiple_internal_spaces_preserved():
    """Case C: Multiple internal spaces define column boundaries and must not collapse."""
    cobol = b"CUSTOMER-ID      BALANCE\n"
    java = b"CUSTOMER-ID BALANCE\n"
    assert normalize_display(cobol) != normalize_display(java)
    mismatch = compare_raw_bytes("stdout", normalize_display(cobol), normalize_display(java))
    assert mismatch is not None


def test_blank_internal_lines_preserved():
    """Case D: Blank lines separate report sections and must not be deleted."""
    cobol = b"HEADER\n\nDETAIL\n"
    java = b"HEADER\nDETAIL\n"
    assert normalize_display(cobol) != normalize_display(java)
    mismatch = compare_raw_bytes("stdout", normalize_display(cobol), normalize_display(java))
    assert mismatch is not None


def test_fixed_width_column_shift_detected():
    """Case F (columns): Positional field shift by even 1 space must cause divergence."""
    cobol = b"ID    AMOUNT\n1234  00500\n"
    java = b"ID     AMOUNT\n1234  00500\n"
    assert normalize_display(cobol) != normalize_display(java)
    mismatch = compare_raw_bytes("stdout", normalize_display(cobol), normalize_display(java))
    assert mismatch is not None


def test_empty_input_handling():
    """Empty bytes input returns empty bytes without error."""
    assert normalize_display(b"") == b""
