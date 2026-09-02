"""EBCDIC Charset Adapter for COBOL Modernization.

In accordance with the Ponytail Global AI Software Engineering Constitution:
- Charset conversion support != complete native mainframe semantic equivalence.
- Explicit fail-closed behavior on unsupported codepages and malformed byte sequences.
- Supports CP037, CP1047, CP500, CP273, and CP1140.
- Handles fixed-width record padding (EBCDIC 0x40 space) and zoned decimal byte mappings.
"""

import codecs
from typing import Dict, List, Optional, Tuple


class CobolCharsetAdapter:
    """Handles EBCDIC code page conversions, record layout padding, and binary inspections."""

    SUPPORTED_CODEPAGES = {
        "CP037": "cp037",      # IBM EBCDIC US-Canada
        "CP1047": "cp1047",    # IBM Open Edition (Latin 1)
        "CP500": "cp500",      # IBM EBCDIC International
        "CP273": "cp273",      # IBM EBCDIC Germany
        "CP1140": "cp1140",    # IBM EBCDIC US-Canada with Euro
    }

    EBCDIC_SPACE_BYTE = 0x40

    @classmethod
    def normalize_codepage(cls, name: str, fail_closed: bool = True) -> str:
        """Resolve codepage name. If fail_closed is True, raise ValueError on unknown codepages."""
        key = name.upper().replace("-", "").replace("_", "")
        if key in cls.SUPPORTED_CODEPAGES:
            return cls.SUPPORTED_CODEPAGES[key]
        if fail_closed:
            raise ValueError(f"Unsupported or unproven EBCDIC code page: '{name}'. Supported: {list(cls.SUPPORTED_CODEPAGES.keys())}")
        return "cp037"

    @classmethod
    def to_ebcdic(cls, text: str, codepage: str = "CP037", strict: bool = False) -> bytes:
        """Convert Unicode Python string to EBCDIC byte sequence.
        
        Args:
            text: Input string.
            codepage: EBCDIC code page name.
            strict: If True, raise ValueError on unmappable characters; if False, use replacement.
        """
        cp = cls.normalize_codepage(codepage, fail_closed=True)
        errors = "strict" if strict else "replace"
        try:
            return text.encode(cp, errors=errors)
        except LookupError:
            for alt in ("cp037", "cp500"):
                try:
                    return text.encode(alt, errors=errors)
                except LookupError:
                    continue
            raise ValueError(f"No usable EBCDIC codec found on platform for {codepage}")
        except UnicodeEncodeError as e:
            raise ValueError(f"EBCDIC transcoding error for codepage {codepage}: {e}")

    @classmethod
    def to_unicode(cls, data: bytes, codepage: str = "CP037", strict: bool = False) -> str:
        """Convert EBCDIC byte sequence to Unicode Python string.
        
        Args:
            data: Input EBCDIC bytes.
            codepage: EBCDIC code page name.
            strict: If True, raise ValueError on invalid byte sequences; if False, use replacement.
        """
        cp = cls.normalize_codepage(codepage, fail_closed=True)
        errors = "strict" if strict else "replace"
        try:
            return data.decode(cp, errors=errors)
        except LookupError:
            for alt in ("cp037", "cp500"):
                try:
                    return data.decode(alt, errors=errors)
                except LookupError:
                    continue
            raise ValueError(f"No usable EBCDIC codec found on platform for {codepage}")
        except UnicodeDecodeError as e:
            raise ValueError(f"EBCDIC decode error for codepage {codepage}: {e}")

    @classmethod
    def pad_record_ebcdic(cls, record_bytes: bytes, length: int) -> bytes:
        """Pad record with EBCDIC space bytes (0x40) or truncate to fixed record length."""
        if len(record_bytes) >= length:
            return record_bytes[:length]
        return record_bytes + (bytes([cls.EBCDIC_SPACE_BYTE]) * (length - len(record_bytes)))

    @classmethod
    def roundtrip_verify(cls, text: str, codepage: str = "CP037") -> bool:
        """Check whether text survives round-trip transcoding without data loss."""
        encoded = cls.to_ebcdic(text, codepage, strict=False)
        decoded = cls.to_unicode(encoded, codepage, strict=False)
        return decoded == text

    @classmethod
    def get_ebcdic_byte(cls, char: str, codepage: str = "CP037") -> int:
        """Return the integer byte value of a single character in EBCDIC."""
        if not char:
            return cls.EBCDIC_SPACE_BYTE
        b = cls.to_ebcdic(char[0], codepage)
        return b[0] if b else cls.EBCDIC_SPACE_BYTE

    @classmethod
    def is_zoned_decimal_ebcdic(cls, b: int) -> bool:
        """Check if byte represents an EBCDIC zoned decimal digit (0xF0-0xF9 or signed 0xC0-0xD9)."""
        high_nibble = b >> 4
        low_nibble = b & 0x0F
        if low_nibble > 9:
            return False
        # Standard unsigned/positive is 0xF0..0xF9, signed positive 0xC0..0xC9, signed negative 0xD0..0xD9
        return high_nibble in (0xF, 0xC, 0xD)
