"""EBCDIC Charset Adapter for COBOL Modernization."""

import codecs
from typing import Dict, List, Optional, Tuple


class CobolCharsetAdapter:
    """Handles EBCDIC code page conversions and binary byte inspections."""

    SUPPORTED_CODEPAGES = {
        "CP037": "cp037",      # IBM EBCDIC US-Canada
        "CP1047": "cp1047",    # IBM Open Edition (Latin 1)
        "CP500": "cp500",      # IBM EBCDIC International
        "CP273": "cp273",      # IBM EBCDIC Germany
        "CP1140": "cp1140",    # IBM EBCDIC US-Canada with Euro
    }

    @classmethod
    def normalize_codepage(cls, name: str) -> str:
        key = name.upper().replace("-", "").replace("_", "")
        return cls.SUPPORTED_CODEPAGES.get(key, "cp037")

    @classmethod
    def to_ebcdic(cls, text: str, codepage: str = "CP037") -> bytes:
        """Convert Unicode Python string to EBCDIC byte sequence."""
        cp = cls.normalize_codepage(codepage)
        return text.encode(cp, errors="replace")

    @classmethod
    def to_unicode(cls, data: bytes, codepage: str = "CP037") -> str:
        """Convert EBCDIC byte sequence to Unicode Python string."""
        cp = cls.normalize_codepage(codepage)
        return data.decode(cp, errors="replace")

    @classmethod
    def roundtrip_verify(cls, text: str, codepage: str = "CP037") -> bool:
        """Check whether text survives round-trip transcoding without data loss."""
        encoded = cls.to_ebcdic(text, codepage)
        decoded = cls.to_unicode(encoded, codepage)
        return decoded == text

    @classmethod
    def get_ebcdic_byte(cls, char: str, codepage: str = "CP037") -> int:
        """Return the integer byte value of a single character in EBCDIC."""
        if not char:
            return 0x40  # EBCDIC space
        b = cls.to_ebcdic(char[0], codepage)
        return b[0] if b else 0x40
