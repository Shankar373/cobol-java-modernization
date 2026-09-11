"""Tests for EBCDIC vs ASCII Collating Sequence Strategies."""

import pytest
from tools.reference_runtimes.ebcdic.collation import CobolCollationStrategy, CollationMode


def test_letter_vs_digit_collation_difference():
    """In ASCII: '1' (0x31) < 'A' (0x41). In EBCDIC: 'A' (0xC1) < '1' (0xF1)."""
    ascii_strategy = CobolCollationStrategy(CollationMode.ASCII)
    ebcdic_strategy = CobolCollationStrategy(CollationMode.EBCDIC)

    assert ascii_strategy.compare("A", "1") == 1     # 'A' > '1' in ASCII
    assert ebcdic_strategy.compare("A", "1") == -1   # 'A' < '1' in EBCDIC

    assert ebcdic_strategy.is_ebcdic_different_from_ascii("A", "1") is True


def test_case_collation_difference():
    """In ASCII: 'A' (0x41) < 'a' (0x61). In EBCDIC: 'a' (0x81) < 'A' (0xC1)."""
    ascii_strategy = CobolCollationStrategy(CollationMode.ASCII)
    ebcdic_strategy = CobolCollationStrategy(CollationMode.EBCDIC)

    assert ascii_strategy.compare("a", "A") == 1     # 'a' > 'A' in ASCII
    assert ebcdic_strategy.compare("a", "A") == -1   # 'a' < 'A' in EBCDIC

    assert ebcdic_strategy.is_ebcdic_different_from_ascii("a", "A") is True


def test_sorting_order_difference():
    items = ["ITEM_9", "ITEM_A", "ITEM_a", "ITEM_1"]
    ascii_sorted = CobolCollationStrategy(CollationMode.ASCII).sort_keys(items)
    ebcdic_sorted = CobolCollationStrategy(CollationMode.EBCDIC).sort_keys(items)

    # In ASCII: digits ('1', '9') come before uppercase ('A') before lowercase ('a')
    assert ascii_sorted == ["ITEM_1", "ITEM_9", "ITEM_A", "ITEM_a"]

    # In EBCDIC: lowercase ('a') comes before uppercase ('A') before digits ('1', '9')
    assert ebcdic_sorted == ["ITEM_a", "ITEM_A", "ITEM_1", "ITEM_9"]
