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
