"""Tests for modernize_v2.ir.ids — deterministic 26-character IDs.

Acceptance criteria from T-2A-01:

    * deterministic output
    * 26 characters
    * Crockford alphabet
    * same input = same ID
    * different semantic identity = different ID
    * kind partitioning
    * reproducibility across processes
"""

from __future__ import annotations

import os
import subprocess
import sys

import pytest

from modernize_v2.ir.ids import (
    ID_CHARSET,
    ID_LENGTH,
    IRID_NAMESPACE,
    DeterministicId,
    id_for_node,
)


VALID_CHARS = set(ID_CHARSET)


def _is_crockford_charset(text: str) -> bool:
    return all(c in VALID_CHARS for c in text.upper())


def test_id_is_26_chars() -> None:
    nid = id_for_node(
        kind="STATEMENT.MOVE",
        canonical_path="src/prog.cbl",
        line=1,
        column=1,
        byte_offset=0,
    )
    assert isinstance(nid, DeterministicId)
    assert len(nid.text) == 26
    assert len(str(nid)) == 26


def test_id_uses_crockford_alphabet() -> None:
    for path, line in [
        ("a.cbl", 1),
        ("some/longer/path.cbl", 99),
        ("path/with/dashes-and.dots", 7),
    ]:
        nid = id_for_node(
            kind="DATA_ITEM",
            canonical_path=path,
            line=line,
            column=0,
            byte_offset=0,
        )
        assert _is_crockford_charset(nid.text), nid.text


def test_id_namespace_prefix() -> None:
    nid = id_for_node(
        kind="PROGRAM",
        canonical_path="x.cbl",
        line=1,
        column=0,
        byte_offset=0,
    )
    assert nid.text.startswith(IRID_NAMESPACE)


def test_id_is_deterministic() -> None:
    a = id_for_node(
        kind="STATEMENT.IF",
        canonical_path="src/a.cbl",
        line=42,
        column=7,
        byte_offset=1234,
    )
    b = id_for_node(
        kind="STATEMENT.IF",
        canonical_path="src/a.cbl",
        line=42,
        column=7,
        byte_offset=1234,
    )
    assert a == b
    assert a.text == b.text
    assert hash(a) == hash(b)


def test_kind_partitioning() -> None:
    same_pos = dict(
        canonical_path="src/a.cbl",
        line=1,
        column=0,
        byte_offset=0,
    )
    a = id_for_node(kind="STATEMENT.MOVE", **same_pos)
    b = id_for_node(kind="STATEMENT.IF", **same_pos)
    c = id_for_node(kind="STATEMENT.PERFORM", **same_pos)
    assert a != b != c
    # pairwise distinctness
    assert a != c


def test_source_path_partitioning() -> None:
    same_kind_pos = dict(kind="DATA_ITEM", line=1, column=0, byte_offset=0)
    a = id_for_node(canonical_path="src/a.cbl", **same_kind_pos)
    b = id_for_node(canonical_path="src/b.cbl", **same_kind_pos)
    c = id_for_node(canonical_path="lib/a.cbl", **same_kind_pos)
    assert a != b != c
    assert a != c


def test_source_position_partitioning() -> None:
    same_kind_path = dict(kind="DATA_ITEM", canonical_path="src/a.cbl")
    a = id_for_node(line=1, column=0, byte_offset=0, **same_kind_path)
    b = id_for_node(line=2, column=0, byte_offset=0, **same_kind_path)
    c = id_for_node(line=1, column=1, byte_offset=1, **same_kind_path)
    assert a != b
    assert a != c


def test_ordinal_distinguishes_siblings() -> None:
    same_inputs = dict(
        kind="STATEMENT.MOVE",
        canonical_path="src/a.cbl",
        line=1,
        column=0,
        byte_offset=0,
    )
    a = id_for_node(ordinal=0, **same_inputs)
    b = id_for_node(ordinal=1, **same_inputs)
    c = id_for_node(ordinal=2, **same_inputs)
    assert a != b != c


def test_rejects_invalid_construction() -> None:
    with pytest.raises(ValueError):
        DeterministicId("abc")
    with pytest.raises(ValueError):
        DeterministicId("X" * 26)  # wrong namespace
    with pytest.raises(ValueError):
        DeterministicId("N" + "I" * 25)  # 'I' is decoded but not canonical
    with pytest.raises(TypeError):
        DeterministicId(123)  # type: ignore[arg-type]


def test_source_path_must_be_nonempty() -> None:
    with pytest.raises(ValueError):
        id_for_node(
            kind="PROGRAM",
            canonical_path="",
            line=1,
            column=0,
            byte_offset=0,
        )


def test_line_must_be_positive() -> None:
    with pytest.raises(ValueError):
        id_for_node(
            kind="PROGRAM",
            canonical_path="x.cbl",
            line=0,
            column=0,
            byte_offset=0,
        )


def test_column_must_be_nonnegative() -> None:
    with pytest.raises(ValueError):
        id_for_node(
            kind="PROGRAM",
            canonical_path="x.cbl",
            line=1,
            column=-1,
            byte_offset=0,
        )


def test_byte_offset_must_be_nonnegative() -> None:
    with pytest.raises(ValueError):
        id_for_node(
            kind="PROGRAM",
            canonical_path="x.cbl",
            line=1,
            column=0,
            byte_offset=-1,
        )


def test_id_int_form_is_deterministic() -> None:
    a = id_for_node(
        kind="PARAGRAPH",
        canonical_path="src/p.cbl",
        line=10,
        column=4,
        byte_offset=99,
    )
    b = id_for_node(
        kind="PARAGRAPH",
        canonical_path="src/p.cbl",
        line=10,
        column=4,
        byte_offset=99,
    )
    assert a.as_int() == b.as_int()
    assert a.as_int() >= 0


def test_id_string_equality() -> None:
    nid = id_for_node(
        kind="X",
        canonical_path="x.cbl",
        line=1,
        column=0,
        byte_offset=0,
    )
    assert nid == nid.text
    assert nid == DeterministicId(nid.text)


def test_reproducibility_across_processes() -> None:
    """Run id_for_node in a child process and assert the same result."""
    script = (
        "import sys;"
        "sys.path.insert(0, "
        "r'" + os.path.abspath(".") + "');"
        "from modernize_v2.ir.ids import id_for_node;"
        "print(id_for_node("
        "kind='STATEMENT.MOVE',"
        "canonical_path='src/a.cbl',"
        "line=10, column=4, byte_offset=99"
        ").text)"
    )
    out = subprocess.check_output(
        [sys.executable, "-c", script],
        stderr=subprocess.STDOUT,
    )
    child_text = out.decode("utf-8").strip()
    assert len(child_text) == 26
    assert child_text.startswith(IRID_NAMESPACE)
    assert _is_crockford_charset(child_text)

    local = id_for_node(
        kind="STATEMENT.MOVE",
        canonical_path="src/a.cbl",
        line=10,
        column=4,
        byte_offset=99,
    )
    assert child_text == local.text


def test_id_length_constant_matches() -> None:
    assert ID_LENGTH == 26
