"""COBOL Collation Strategy: ASCII vs EBCDIC Collating Sequences."""

from enum import Enum
from typing import Callable, List, Optional
from .charset import CobolCharsetAdapter


class CollationMode(str, Enum):
    ASCII = "ASCII"
    EBCDIC = "EBCDIC"
    CUSTOM = "CUSTOM"


class CobolCollationStrategy:
    """Implements collation comparisons for COBOL character sequences."""

    def __init__(self, mode: CollationMode = CollationMode.ASCII, codepage: str = "CP037"):
        self.mode = mode
        self.codepage = codepage

    def compare(self, s1: str, s2: str) -> int:
        """Compare two strings under the active collation mode.

        Returns:
            -1 if s1 < s2
             0 if s1 == s2
             1 if s1 > s2
        """
        if self.mode == CollationMode.ASCII:
            if s1 < s2:
                return -1
            elif s1 > s2:
                return 1
            return 0
        elif self.mode == CollationMode.EBCDIC:
            # Under EBCDIC, compare byte-for-byte in EBCDIC encoding
            b1 = CobolCharsetAdapter.to_ebcdic(s1, self.codepage)
            b2 = CobolCharsetAdapter.to_ebcdic(s2, self.codepage)
            if b1 < b2:
                return -1
            elif b1 > b2:
                return 1
            return 0
        else:
            # Custom default
            if s1 < s2:
                return -1
            elif s1 > s2:
                return 1
            return 0

    def sort_keys(self, strings: List[str]) -> List[str]:
        """Sort a list of strings using the active collation strategy."""
        if self.mode == CollationMode.ASCII:
            return sorted(strings)
        elif self.mode == CollationMode.EBCDIC:
            return sorted(strings, key=lambda s: CobolCharsetAdapter.to_ebcdic(s, self.codepage))
        return sorted(strings)

    def is_ebcdic_different_from_ascii(self, s1: str, s2: str) -> bool:
        """Check if EBCDIC collation produces a different relational outcome than ASCII."""
        cmp_ascii = 1 if s1 > s2 else (-1 if s1 < s2 else 0)
        b1 = CobolCharsetAdapter.to_ebcdic(s1, self.codepage)
        b2 = CobolCharsetAdapter.to_ebcdic(s2, self.codepage)
        cmp_ebcdic = 1 if b1 > b2 else (-1 if b1 < b2 else 0)
        return cmp_ascii != cmp_ebcdic
