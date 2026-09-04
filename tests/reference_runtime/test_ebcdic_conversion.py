"""Tests for EBCDIC Charset Conversions and Code Page Round-tripping."""

import pytest
from tools.reference_runtimes.ebcdic.charset import CobolCharsetAdapter


def test_ebcdic_space_byte_value():
    """EBCDIC space is 0x40 (64 decimal), compared to ASCII 0x20 (32 decimal)."""
    b = CobolCharsetAdapter.to_ebcdic(" ", "CP037")
    assert b == b"\x40"
    assert CobolCharsetAdapter.get_ebcdic_byte(" ", "CP037") == 0x40


def test_ebcdic_digits_byte_values():
    """EBCDIC digits '0'-'9' map to 0xF0-0xF9 (240-249 decimal)."""
    digits = "0123456789"
    ebcdic_bytes = CobolCharsetAdapter.to_ebcdic(digits, "CP037")
    assert ebcdic_bytes == bytes([0xF0 + i for i in range(10)])


def test_ebcdic_uppercase_letters():
    """EBCDIC 'A'-'I' is 0xC1-0xC9, 'J'-'R' is 0xD1-0xD9, 'S'-'Z' is 0xE2-0xE9."""
    b_a = CobolCharsetAdapter.to_ebcdic("A", "CP037")
    assert b_a == b"\xC1"
    b_z = CobolCharsetAdapter.to_ebcdic("Z", "CP037")
    assert b_z == b"\xE9"


def test_ebcdic_roundtrip_all_supported_codepages():
    text = "HELLO WORLD 12345 !?#$*-/+"
    for cp in ["CP037", "CP1047", "CP500", "CP273", "CP1140"]:
        assert CobolCharsetAdapter.roundtrip_verify(text, cp), f"Roundtrip failed for {cp}"
        decoded = CobolCharsetAdapter.to_unicode(CobolCharsetAdapter.to_ebcdic(text, cp), cp)
        assert decoded == text


def test_ebcdic_fail_closed_on_unsupported_codepage():
    """Verify that an unsupported or unproven codepage raises ValueError."""
    with pytest.raises(ValueError, match="Unsupported or unproven EBCDIC code page"):
        CobolCharsetAdapter.to_ebcdic("HELLO", "CP9999_UNKNOWN")
    
    with pytest.raises(ValueError, match="Unsupported or unproven EBCDIC code page"):
        CobolCharsetAdapter.to_unicode(b"\xC1", "CP9999_UNKNOWN")


def test_ebcdic_fixed_record_padding():
    """Fixed-width records must be padded with EBCDIC spaces (0x40)."""
    raw = CobolCharsetAdapter.to_ebcdic("REC01", "CP037")
    padded = CobolCharsetAdapter.pad_record_ebcdic(raw, 10)
    assert len(padded) == 10
    # Remaining 5 bytes must all be 0x40
    assert padded[5:] == b"\x40\x40\x40\x40\x40"
    
    # Truncation if longer than fixed length
    truncated = CobolCharsetAdapter.pad_record_ebcdic(raw, 3)
    assert len(truncated) == 3
    assert truncated == raw[:3]


def test_ebcdic_zoned_decimal_inspection():
    """Verify zoned decimal detection for digits and sign nibbles."""
    # Digits '0' (0xF0) to '9' (0xF9)
    for b in range(0xF0, 0xFA):
        assert CobolCharsetAdapter.is_zoned_decimal_ebcdic(b) is True
    # Signed positive 'A'..'I' representing 1..9 with positive sign (0xC1..0xC9)
    for b in range(0xC1, 0xCA):
        assert CobolCharsetAdapter.is_zoned_decimal_ebcdic(b) is True
    # Signed negative 'J'..'R' representing 1..9 with negative sign (0xD1..0xD9)
    for b in range(0xD1, 0xDA):
        assert CobolCharsetAdapter.is_zoned_decimal_ebcdic(b) is True
    # Non-digit byte e.g. 0x40 (space)
    assert CobolCharsetAdapter.is_zoned_decimal_ebcdic(0x40) is False

