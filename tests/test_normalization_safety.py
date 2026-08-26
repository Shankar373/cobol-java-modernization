"""
Independent verification that output normalization (used by Gate 2 equivalence)
cannot mask a genuine numeric difference.

Normalization only deals with line endings and trailing whitespace; it must
never alter numeric content. The payroll01 defect (25864 vs 258648, i.e. an
off-by-one in NET) must remain detectable after normalization.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cobol_migrate import normalize


def _gate2_normalize(content_bytes):
    """Exact replica of the Gate 2 `_normalize_text` closure in cobol_migrate."""
    text = content_bytes.decode("utf-8", errors="replace")
    lines = [line.rstrip(" \t\r\n\x00") for line in text.splitlines()]
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines).strip()


def test_normalize_only_whitespace_and_line_endings():
    assert normalize(b"a\r\nb\r\n") == b"a\nb"
    assert normalize(b"x  \n") == b"x"
    # numeric content is preserved verbatim
    assert normalize(b"25864") == b"25864"
    assert normalize(b"258648") == b"258648"


def test_normalize_cannot_hide_numeric_mismatch():
    a = normalize(b"NET=25864\r\n")
    b = normalize(b"NET=258648\r\n")
    assert a != b, "numeric off-by-one must survive normalization"

    # Identical numeric content with differing line endings must match.
    assert normalize(b"NET=25864\r\n") == normalize(b"NET=25864\n")


def test_gate2_normalize_preserves_numeric_difference():
    baseline = _gate2_normalize(b"E00129324002586400103460\r\n")
    native_buggy = _gate2_normalize(b"E00129324002586480103459\r\n")
    native_fixed = _gate2_normalize(b"E00129324002586400103460\r\n")
    # buggy native still differs from baseline
    assert baseline != native_buggy
    # fixed native now matches baseline
    assert baseline == native_fixed
