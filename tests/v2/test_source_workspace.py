"""Tests for modernize_v2.source — T-2B-01.

Coverage:

    * workspace creation
    * registering a source file
    * stable file IDs (deterministic, cross-process)
    * distinct identity for distinct path/content
    * deterministic file ordering
    * safe relative paths and normalization
    * .. traversal rejection
    * absolute outside-root path rejection (POSIX + Windows)
    * NUL / control-character rejection
    * SourceMap offset 0 / middle / newline boundary / EOF
    * negative / beyond-EOF offset rejection
    * UTF-8 multibyte (byte offsets, not char indices)
    * LF / CRLF / CR line handling
    * empty and single-line files
    * immutability
    * position_at_line_column round-trip
"""

from __future__ import annotations

import os
import subprocess
import sys

import pytest

from modernize_v2.source import (
    FileKind,
    PathSecurityError,
    SourceFile,
    SourceMap,
    SourceMapError,
    Workspace,
    WorkspaceError,
    byte_to_position,
    make_source_file,
    normalize_canonical_path,
    resolve_relative_path,
)


EURO = "\u20ac"  # € — 3 bytes in UTF-8


# -----------------------------------------------------------------
# Workspace / SourceFile basics
# -----------------------------------------------------------------


def test_empty_workspace() -> None:
    w = Workspace.empty()
    assert len(w) == 0
    assert w.files == ()
    assert w.paths() == ()
    assert w.ids() == ()


def test_register_one_source_file() -> None:
    w = Workspace.empty()
    sf = make_source_file("src/a.cbl", b"DISPLAY 1.")
    w2 = w.with_file(sf)
    assert len(w2) == 1
    assert w2.file_by_path("src/a.cbl") is sf
    assert w2.file_by_id(sf.file_id) is sf


def test_stable_file_id() -> None:
    a = make_source_file("src/a.cbl", b"X")
    b = make_source_file("src/a.cbl", b"X")
    assert a.file_id == b.file_id
    assert a.content_hash == b.content_hash


def test_different_path_different_id() -> None:
    a = make_source_file("src/a.cbl", b"X")
    b = make_source_file("src/b.cbl", b"X")
    assert a.file_id != b.file_id


def test_different_content_same_path_same_id_but_different_hash() -> None:
    # Identity is path-derived; integrity is content-derived.
    a = make_source_file("src/a.cbl", b"ONE")
    b = make_source_file("src/a.cbl", b"TWO")
    assert a.file_id == b.file_id
    assert a.content_hash != b.content_hash


def test_deterministic_ordering() -> None:
    w = Workspace.empty()
    for p in ("z/z.cbl", "a/a.cbl", "m/m.cbl", "a0.cbl"):
        w = w.with_file(make_source_file(p, b"X"))
    assert w.paths() == tuple(sorted(w.paths()))
    ids1 = tuple(str(i) for i in w.ids())
    # Rebuild in different insertion order.
    w2 = Workspace.empty()
    for p in reversed(("z/z.cbl", "a/a.cbl", "m/m.cbl", "a0.cbl")):
        w2 = w2.with_file(make_source_file(p, b"X"))
    assert tuple(str(i) for i in w2.ids()) == ids1


def test_duplicate_path_rejected() -> None:
    w = Workspace.empty().with_file(make_source_file("a.cbl", b"X"))
    with pytest.raises(WorkspaceError):
        w.with_file(make_source_file("a.cbl", b"X"))


def test_duplicate_path_case_insensitive_rejected() -> None:
    w = Workspace.empty().with_file(make_source_file("SRC/A.cbl", b"X"))
    with pytest.raises(WorkspaceError):
        w.with_file(make_source_file("src/a.CBL", b"Y"))


def test_workspace_containment() -> None:
    sf = make_source_file("a.cbl", b"X")
    w = Workspace.empty().with_file(sf)
    assert sf in w
    assert sf.file_id in w
    assert "a.cbl" in w
    assert "b.cbl" not in w
    assert 123 not in w


def test_workspace_immutable() -> None:
    w = Workspace.empty()
    with pytest.raises(Exception):
        w.files = ()  # type: ignore[misc]
    sf = make_source_file("a.cbl", b"X")
    with pytest.raises(Exception):
        sf.byte_size = 99  # type: ignore[misc]


def test_source_map_line_starts_are_tuple() -> None:
    sf = make_source_file("a.cbl", b"line1\nline2\n")
    sm = SourceMap.from_bytes(sf, b"line1\nline2\n")
    assert isinstance(sm.line_starts, tuple)
    with pytest.raises(Exception):
        sm.line_starts = (0,)  # type: ignore[misc]


def test_file_kind_classification() -> None:
    assert FileKind.from_path("a.cbl") is FileKind.COBOL
    assert FileKind.from_path("a.cob") is FileKind.COBOL
    assert FileKind.from_path("a.cpy") is FileKind.COPYBOOK
    assert FileKind.from_path("job.jcl") is FileKind.JCL
    assert FileKind.from_path("p.proc") is FileKind.PROC
    assert FileKind.from_path("s.sql") is FileKind.SQL
    assert FileKind.from_path("m.bms") is FileKind.BMS
    assert FileKind.from_path("x.cics") is FileKind.CICS
    assert FileKind.from_path("noext") is FileKind.UNKNOWN
    assert FileKind.from_path("a.weird") is FileKind.UNKNOWN


# -----------------------------------------------------------------
# Path security
# -----------------------------------------------------------------


@pytest.mark.parametrize(
    "bad",
    [
        "../secret",
        "../../etc/passwd",
        "src/../../evil.cbl",
        "..\\evil.cbl",
        "src/..\\..\\evil.cbl",
        "/etc/passwd",
        "\\server\\share\\x.cbl",
        "C:/windows/system32/x.cbl",
        "C:\\tools\\x.cbl",
        "d:\\x.cbl",
    ],
)
def test_path_traversal_and_absolute_rejected(bad: str) -> None:
    with pytest.raises(PathSecurityError):
        make_source_file(bad, b"X")


@pytest.mark.parametrize(
    "bad",
    [
        "a\x00b.cbl",
        "a\x01b.cbl",
        "a\x1fb.cbl",
        "a\x7fb.cbl",
        "a\nb.cbl",
        "a\rb.cbl",
        "a\tb.cbl",
    ],
)
def test_control_characters_rejected(bad: str) -> None:
    with pytest.raises(PathSecurityError):
        make_source_file(bad, b"X")


def test_empty_path_rejected() -> None:
    with pytest.raises(PathSecurityError):
        make_source_file("", b"X")


def test_path_normalization() -> None:
    assert normalize_canonical_path("SRC\\A.CBL") == "src/a.cbl"
    assert normalize_canonical_path("src//a.cbl") == "src/a.cbl"
    assert normalize_canonical_path("./src/a.cbl") == "src/a.cbl"
    assert normalize_canonical_path("src/./a.cbl") == "src/a.cbl"


def test_resolve_relative_path() -> None:
    assert resolve_relative_path(".", "src/a.cbl") == "src/a.cbl"
    with pytest.raises(PathSecurityError):
        resolve_relative_path("repo", "../outside.cbl")


def test_with_file_boundary() -> None:
    w = Workspace.empty(root_canonical_path="repo")
    w = w.with_file(make_source_file("repo/src/a.cbl", b"X"))
    assert "repo/src/a.cbl" in w
    with pytest.raises(PathSecurityError):
        w.with_file(make_source_file("other/b.cbl", b"X"))


def test_workspace_rejects_duplicate_after_iteration() -> None:
    """Unsorted/duplicate files tuple in constructor is rejected."""
    a = make_source_file("a.cbl", b"X")
    b = make_source_file("b.cbl", b"X")
    with pytest.raises(ValueError):
        Workspace(workspace_id="w", root_canonical_path=".", files=(b, a))
    with pytest.raises(ValueError):
        Workspace(workspace_id="w", root_canonical_path=".", files=(a, a))


# -----------------------------------------------------------------
# SourceMap — LF / CRLF / empty / single-line
# -----------------------------------------------------------------


def _sm(content: bytes) -> tuple[SourceFile, SourceMap]:
    sf = make_source_file("t.cbl", content)
    return sf, SourceMap.from_bytes(sf, content)


def test_empty_file() -> None:
    sf, sm = _sm(b"")
    assert sm.line_count() == 1
    p = sm.position_at(0)
    assert (p.line, p.column, p.byte_offset) == (1, 0, 0)
    with pytest.raises(SourceMapError):
        sm.position_at(1)


def test_single_line_no_newline() -> None:
    sf, sm = _sm(b"ABC")
    assert sm.line_count() == 1
    assert sm.position_at(0).column == 0
    assert sm.position_at(2).column == 2
    eof = sm.position_at(3)
    assert (eof.line, eof.column, eof.byte_offset) == (1, 3, 3)


def test_lf_multiline() -> None:
    content = b"one\ntwo\nthree"
    sf, sm = _sm(content)
    assert sm.line_count() == 3
    # start of line 2
    p = sm.position_at(4)
    assert (p.line, p.column) == (2, 0)
    # start of line 3
    p = sm.position_at(8)
    assert (p.line, p.column) == (3, 0)
    # newline itself belongs to the previous line
    p = sm.position_at(3)
    assert (p.line, p.column) == (1, 3)


def test_crlf_multiline() -> None:
    content = b"one\r\ntwo\r\nthree"
    sf, sm = _sm(content)
    # Line starts are right after each \n; \r is content of the
    # preceding line.
    p = sm.position_at(5)  # just past "one\r\n"
    assert (p.line, p.column) == (2, 0)
    p = sm.position_at(3)  # the '\r'
    assert (p.line, p.column) == (1, 3)
    p = sm.position_at(4)  # the '\n'
    assert (p.line, p.column) == (1, 4)


def test_trailing_newline() -> None:
    sf, sm = _sm(b"a\n")
    assert sm.line_count() == 2  # "a" and the empty final line
    p = sm.position_at(2)
    assert (p.line, p.column) == (2, 0)


def test_negative_offset_rejected() -> None:
    _, sm = _sm(b"abc")
    with pytest.raises(SourceMapError):
        sm.position_at(-1)


def test_offset_beyond_eof_rejected() -> None:
    _, sm = _sm(b"abc")
    with pytest.raises(SourceMapError):
        sm.position_at(4)


def test_byte_to_position_validates_line_starts() -> None:
    with pytest.raises(SourceMapError):
        byte_to_position((), 0)
    with pytest.raises(SourceMapError):
        byte_to_position((1, 2), 0)  # doesn't start at 0
    with pytest.raises(SourceMapError):
        byte_to_position((0, 0), 0)  # not strictly increasing


def test_position_at_line_column_roundtrip() -> None:
    _, sm = _sm(b"abc\ndef\n")
    p = sm.position_at_line_column(2, 1)
    assert (p.line, p.column, p.byte_offset) == (2, 1, 5)
    p2 = sm.position_at(p.byte_offset)
    assert (p2.line, p2.column) == (2, 1)
    with pytest.raises(SourceMapError):
        sm.position_at_line_column(0, 0)
    with pytest.raises(SourceMapError):
        sm.position_at_line_column(1, -1)
    with pytest.raises(SourceMapError):
        sm.position_at_line_column(99, 0)
    with pytest.raises(SourceMapError):
        sm.position_at_line_column(1, 4)  # line 1 length is 3+\n


# -----------------------------------------------------------------
# UTF-8 byte-offset behavior
# -----------------------------------------------------------------


def test_utf8_multibyte_byte_offsets() -> None:
    src = (
        "       IDENTIFICATION DIVISION.\n"
        f"       DISPLAY '{EURO}'.\n"
        "       STOP RUN.\n"
    )
    raw = src.encode("utf-8")
    sf, sm = _sm(raw)
    # The euro sign starts right after the opening quote.
    e_index = raw.find(EURO.encode("utf-8"))
    assert e_index > 0
    # Each byte of the 3-byte euro sign has its own position with
    # distinct, increasing byte offsets on the same line.
    p0 = sm.position_at(e_index)
    p1 = sm.position_at(e_index + 1)
    p2 = sm.position_at(e_index + 2)
    assert p0.line == p1.line == p2.line == 2
    assert (p1.column - p0.column) == 1
    assert (p2.column - p1.column) == 1
    # Next char (the closing quote) is 3 columns past the euro start.
    p3 = sm.position_at(e_index + 3)
    assert p3.line == 2
    assert (p3.column - p0.column) == 3


def test_utf8_line_positions_across_lines() -> None:
    raw = f"DISPLAY '{EURO}'\nDISPLAY 'X'\n".encode("utf-8")
    _, sm = _sm(raw)
    first_line_len = len(f"DISPLAY '{EURO}'\n".encode("utf-8"))
    p = sm.position_at(first_line_len)
    assert (p.line, p.column) == (2, 0)


# -----------------------------------------------------------------
# Determinism / cross-process reproducibility
# -----------------------------------------------------------------


def test_source_file_hash_is_sha256() -> None:
    import hashlib
    sf = make_source_file("a.cbl", b"CONTENT")
    assert sf.content_hash == hashlib.sha256(b"CONTENT").hexdigest()


def test_cross_process_reproducibility(tmp_path) -> None:  # type: ignore[no-untyped-def]
    code = (
        "import sys; sys.path.insert(0, " + repr(os.getcwd()) + ");"
        "from modernize_v2.source import Workspace, make_source_file, SourceMap;"
        "w = Workspace.empty();"
        "sf = make_source_file('src/a.cbl', b'A\\nB\\n');"
        "w = w.with_file(sf);"
        "sm = SourceMap.from_bytes(sf, b'A\\nB\\n');"
        "print(sf.file_id.text, sf.content_hash, sm.position_at(2).line, sm.position_at(2).column)"
    )
    out1 = subprocess.check_output([sys.executable, "-c", code])
    out2 = subprocess.check_output([sys.executable, "-c", code])
    assert out1 == out2
    local = make_source_file("src/a.cbl", b"A\nB\n")
    parts = out1.decode().split()
    assert parts[0] == local.file_id.text
    assert parts[1] == local.content_hash


def test_content_integrity_checked_on_source_map() -> None:
    sf = make_source_file("a.cbl", b"REAL")
    with pytest.raises(SourceMapError):
        SourceMap.from_bytes(sf, b"FORGED!")
    with pytest.raises(SourceMapError):
        SourceMap.from_bytes(sf, b"REAL\nEXTRA")
