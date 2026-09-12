"""P1-002: File Comparator Substring Containment Remediation Unit Tests.

Verifies that:
1. is_indexed_or_relative_file() accurately identifies files declared as
   INDEXED or RELATIVE, and rejects SEQUENTIAL / LINE SEQUENTIAL / RECORD SEQUENTIAL.
2. Generic output file comparison requires byte-exact equality for non-INDEXED /
   non-RELATIVE files, eliminating false-PASS vectors:
   - Missing records (subset matching)
   - Extra records
   - Reordered records (order insensitivity)
   - Duplicate record mismatches (missing or extra duplicates)
3. Logical containment equivalence is strictly preserved for INDEXED / RELATIVE files
   (where GnuCOBOL produces ISAM/B-tree container pages with binary headers).
"""

import pytest
from tests.utils.parity_harness import (
    ParityFixture,
    compare_raw_bytes,
    is_indexed_or_relative_file,
)


def _simulate_comparison(fixture: ParityFixture, f_name: str, c_bytes: bytes, j_bytes: bytes, use_old_logic: bool = False):
    """Simulate harness file comparison under either old (unrestricted) or new (restricted) logic."""
    m_file = compare_raw_bytes(f"file:{f_name}", c_bytes, j_bytes)
    if m_file:
        should_containment = True if use_old_logic else is_indexed_or_relative_file(fixture, f_name)
        if should_containment:
            lines = [line.strip(b"\r") for line in j_bytes.split(b"\n") if line.strip(b"\r")]
            if lines and all(rec in c_bytes for rec in lines):
                m_file = None
    return m_file


def test_is_indexed_or_relative_file_detection():
    """Verify that is_indexed_or_relative_file distinguishes file organizations."""
    # 1. Line sequential
    f_line_seq = ParityFixture(
        name="test_line_seq",
        program_name="PROG1",
        cobol_code="""
           SELECT OUT-FILE ASSIGN TO "OUTFILE.TXT"
               ORGANIZATION IS LINE SEQUENTIAL.
        """,
        declared_outputs=["OUTFILE.TXT"],
    )
    assert is_indexed_or_relative_file(f_line_seq, "OUTFILE.TXT") is False

    # 2. Record sequential
    f_rec_seq = ParityFixture(
        name="test_rec_seq",
        program_name="PROG2",
        cobol_code="""
           SELECT DATA-FILE ASSIGN TO "DATA.BIN"
               ORGANIZATION IS RECORD SEQUENTIAL.
        """,
        declared_outputs=["DATA.BIN"],
    )
    assert is_indexed_or_relative_file(f_rec_seq, "DATA.BIN") is False

    # 3. Default organization (omitted -> SEQUENTIAL)
    f_default_seq = ParityFixture(
        name="test_def_seq",
        program_name="PROG3",
        cobol_code="""
           SELECT DEF-FILE ASSIGN TO "REPORT.DAT".
        """,
        declared_outputs=["REPORT.DAT"],
    )
    assert is_indexed_or_relative_file(f_default_seq, "REPORT.DAT") is False

    # 4. Indexed file
    f_indexed = ParityFixture(
        name="test_idx",
        program_name="PROG4",
        cobol_code="""
           SELECT IDX-FILE ASSIGN TO "IDX.DAT"
               ORGANIZATION IS INDEXED
               RECORD KEY IS REC-KEY.
        """,
        declared_outputs=["IDX.DAT"],
    )
    assert is_indexed_or_relative_file(f_indexed, "IDX.DAT") is True

    # 5. Relative file
    f_relative = ParityFixture(
        name="test_rel",
        program_name="PROG5",
        cobol_code="""
           SELECT REL-FILE ASSIGN TO "REL.DAT"
               ORGANIZATION IS RELATIVE
               RELATIVE KEY IS WS-KEY.
        """,
        declared_outputs=["REL.DAT"],
    )
    assert is_indexed_or_relative_file(f_relative, "REL.DAT") is True

    # 6. Multi-file program: SEQUENTIAL file must NOT inherit INDEXED from sibling file
    f_mixed = ParityFixture(
        name="test_mixed",
        program_name="PROG6",
        cobol_code="""
           SELECT SEQ-FILE ASSIGN TO "OUTFILE.TXT"
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT IDX-FILE ASSIGN TO "IDX.DAT"
               ORGANIZATION IS INDEXED
               RECORD KEY IS REC-KEY.
        """,
        declared_outputs=["OUTFILE.TXT", "IDX.DAT"],
    )
    assert is_indexed_or_relative_file(f_mixed, "OUTFILE.TXT") is False
    assert is_indexed_or_relative_file(f_mixed, "IDX.DAT") is True

    # 7. Assigned via variable with VALUE
    f_var = ParityFixture(
        name="test_var",
        program_name="PROG7",
        cobol_code="""
           SELECT REL-FILE ASSIGN TO WS-FNAME
               ORGANIZATION IS RELATIVE.
           WORKING-STORAGE SECTION.
           01 WS-FNAME PIC X(10) VALUE "REL.DAT".
        """,
        declared_outputs=["REL.DAT"],
    )
    assert is_indexed_or_relative_file(f_var, "REL.DAT") is True


def test_missing_record_false_pass_eliminated():
    """Case 1: Expected [A, B], Actual [A] (missing record).
    Old comparator: FALSE PASS (subset of lines matched).
    New comparator: FAIL (byte length and content mismatch).
    """
    fixture = ParityFixture(
        name="test_seq",
        program_name="PROG",
        cobol_code="""
           SELECT OUT-FILE ASSIGN TO "OUT.TXT"
               ORGANIZATION IS LINE SEQUENTIAL.
        """,
        declared_outputs=["OUT.TXT"],
    )
    c_bytes = b"REC-A\nREC-B\n"
    j_bytes = b"REC-A\n"

    # Old logic falsely passed
    old_result = _simulate_comparison(fixture, "OUT.TXT", c_bytes, j_bytes, use_old_logic=True)
    assert old_result is None, "Old logic should have falsely passed"

    # New logic correctly fails
    new_result = _simulate_comparison(fixture, "OUT.TXT", c_bytes, j_bytes, use_old_logic=False)
    assert new_result is not None, "New logic must reject missing record"
    assert new_result.target == "file:OUT.TXT"


def test_extra_record_mismatch_detected():
    """Case 2: Expected [A], Actual [A, B] (extra record).
    Both comparators: FAIL.
    """
    fixture = ParityFixture(
        name="test_seq",
        program_name="PROG",
        cobol_code="""
           SELECT OUT-FILE ASSIGN TO "OUT.TXT"
               ORGANIZATION IS LINE SEQUENTIAL.
        """,
        declared_outputs=["OUT.TXT"],
    )
    c_bytes = b"REC-A\n"
    j_bytes = b"REC-A\nREC-B\n"

    old_result = _simulate_comparison(fixture, "OUT.TXT", c_bytes, j_bytes, use_old_logic=True)
    assert old_result is not None

    new_result = _simulate_comparison(fixture, "OUT.TXT", c_bytes, j_bytes, use_old_logic=False)
    assert new_result is not None


def test_reordered_records_false_pass_eliminated():
    """Case 3: Expected [A, B], Actual [B, A] (out of order).
    Old comparator: FALSE PASS (all lines in c_bytes).
    New comparator: FAIL (byte mismatch at offset 0).
    """
    fixture = ParityFixture(
        name="test_seq",
        program_name="PROG",
        cobol_code="""
           SELECT OUT-FILE ASSIGN TO "OUT.TXT"
               ORGANIZATION IS LINE SEQUENTIAL.
        """,
        declared_outputs=["OUT.TXT"],
    )
    c_bytes = b"REC-A\nREC-B\n"
    j_bytes = b"REC-B\nREC-A\n"

    # Old logic falsely passed
    old_result = _simulate_comparison(fixture, "OUT.TXT", c_bytes, j_bytes, use_old_logic=True)
    assert old_result is None, "Old logic should have falsely passed on reordered records"

    # New logic correctly fails
    new_result = _simulate_comparison(fixture, "OUT.TXT", c_bytes, j_bytes, use_old_logic=False)
    assert new_result is not None, "New logic must reject reordered records"


def test_duplicate_record_mismatch_false_pass_eliminated():
    """Case 4 & 5: Duplicate record count divergence.
    Expected [A, A], Actual [A] (dropped duplicate):
    Old comparator: FALSE PASS.
    New comparator: FAIL.

    Expected [A], Actual [A, A] (unwanted duplicate):
    Old comparator: FALSE PASS.
    New comparator: FAIL.
    """
    fixture = ParityFixture(
        name="test_seq",
        program_name="PROG",
        cobol_code="""
           SELECT OUT-FILE ASSIGN TO "OUT.TXT"
               ORGANIZATION IS LINE SEQUENTIAL.
        """,
        declared_outputs=["OUT.TXT"],
    )

    # Missing duplicate in actual
    c_bytes_dup = b"REC-A\nREC-A\n"
    j_bytes_single = b"REC-A\n"
    assert _simulate_comparison(fixture, "OUT.TXT", c_bytes_dup, j_bytes_single, use_old_logic=True) is None
    assert _simulate_comparison(fixture, "OUT.TXT", c_bytes_dup, j_bytes_single, use_old_logic=False) is not None

    # Extra duplicate in actual
    c_bytes_single = b"REC-A\n"
    j_bytes_dup = b"REC-A\nREC-A\n"
    assert _simulate_comparison(fixture, "OUT.TXT", c_bytes_single, j_bytes_dup, use_old_logic=True) is None
    assert _simulate_comparison(fixture, "OUT.TXT", c_bytes_single, j_bytes_dup, use_old_logic=False) is not None


def test_differing_record_content_detected():
    """Case 6: Expected [A], Actual [B] (different content).
    Both comparators: FAIL.
    """
    fixture = ParityFixture(
        name="test_seq",
        program_name="PROG",
        cobol_code="""
           SELECT OUT-FILE ASSIGN TO "OUT.TXT"
               ORGANIZATION IS LINE SEQUENTIAL.
        """,
        declared_outputs=["OUT.TXT"],
    )
    c_bytes = b"REC-A\n"
    j_bytes = b"REC-B\n"
    assert _simulate_comparison(fixture, "OUT.TXT", c_bytes, j_bytes, use_old_logic=True) is not None
    assert _simulate_comparison(fixture, "OUT.TXT", c_bytes, j_bytes, use_old_logic=False) is not None


def test_empty_expected_vs_nonempty_actual():
    """Case 7: Expected empty, Actual has records.
    Both comparators: FAIL.
    """
    fixture = ParityFixture(
        name="test_seq",
        program_name="PROG",
        cobol_code="""
           SELECT OUT-FILE ASSIGN TO "OUT.TXT"
               ORGANIZATION IS LINE SEQUENTIAL.
        """,
        declared_outputs=["OUT.TXT"],
    )
    assert _simulate_comparison(fixture, "OUT.TXT", b"", b"REC-A\n", use_old_logic=True) is not None
    assert _simulate_comparison(fixture, "OUT.TXT", b"", b"REC-A\n", use_old_logic=False) is not None


def test_empty_actual_vs_nonempty_expected():
    """Case 8: Expected records, Actual empty.
    Both comparators: FAIL.
    """
    fixture = ParityFixture(
        name="test_seq",
        program_name="PROG",
        cobol_code="""
           SELECT OUT-FILE ASSIGN TO "OUT.TXT"
               ORGANIZATION IS LINE SEQUENTIAL.
        """,
        declared_outputs=["OUT.TXT"],
    )
    assert _simulate_comparison(fixture, "OUT.TXT", b"REC-A\n", b"", use_old_logic=True) is not None
    assert _simulate_comparison(fixture, "OUT.TXT", b"REC-A\n", b"", use_old_logic=False) is not None


def test_exact_byte_match_passes():
    """Exact byte equality passes under both comparators."""
    fixture = ParityFixture(
        name="test_seq",
        program_name="PROG",
        cobol_code="""
           SELECT OUT-FILE ASSIGN TO "OUT.TXT"
               ORGANIZATION IS LINE SEQUENTIAL.
        """,
        declared_outputs=["OUT.TXT"],
    )
    c_bytes = b"REC-A\nREC-B\nREC-C\n"
    j_bytes = b"REC-A\nREC-B\nREC-C\n"
    assert _simulate_comparison(fixture, "OUT.TXT", c_bytes, j_bytes, use_old_logic=True) is None
    assert _simulate_comparison(fixture, "OUT.TXT", c_bytes, j_bytes, use_old_logic=False) is None


def test_indexed_file_container_equivalence_preserved():
    """INDEXED files: GnuCOBOL ISAM container with B-tree metadata matches Java flat records."""
    fixture = ParityFixture(
        name="test_idx",
        program_name="PROG",
        cobol_code="""
           SELECT IDX-FILE ASSIGN TO "IDX.DAT"
               ORGANIZATION IS INDEXED
               RECORD KEY IS REC-KEY.
        """,
        declared_outputs=["IDX.DAT"],
    )
    # Simulated 8KB B-Tree page with embedded records
    c_isam_container = (
        b"\x00\x01\x00\x00\x10\x00\x00\x00B-TREE-HEADER-METADATA"
        + b"\x00" * 128
        + b"REC-KEY01RECORD VALUE ONE"
        + b"\x00" * 64
        + b"REC-KEY02RECORD VALUE TWO"
        + b"\x00" * 4096
    )
    j_records = b"REC-KEY01RECORD VALUE ONE\nREC-KEY02RECORD VALUE TWO\n"

    # Both old and new pass for INDEXED files
    assert _simulate_comparison(fixture, "IDX.DAT", c_isam_container, j_records, use_old_logic=True) is None
    assert _simulate_comparison(fixture, "IDX.DAT", c_isam_container, j_records, use_old_logic=False) is None


def test_sequential_file_with_container_payload_fails():
    """If a SEQUENTIAL file has container-like mismatch, new comparator must reject it."""
    fixture = ParityFixture(
        name="test_seq",
        program_name="PROG",
        cobol_code="""
           SELECT SEQ-FILE ASSIGN TO "DATA.TXT"
               ORGANIZATION IS LINE SEQUENTIAL.
        """,
        declared_outputs=["DATA.TXT"],
    )
    c_bytes = b"HEADER\nREC-A\nTRAILER\n"
    j_bytes = b"REC-A\n"

    # Old logic falsely passed because REC-A is a substring of c_bytes
    assert _simulate_comparison(fixture, "DATA.TXT", c_bytes, j_bytes, use_old_logic=True) is None
    # New logic correctly fails because file is LINE SEQUENTIAL
    assert _simulate_comparison(fixture, "DATA.TXT", c_bytes, j_bytes, use_old_logic=False) is not None


# ---------------------------------------------------------------------------
# P1-002 Review: 12 Rigorous Forensic Validation Test Cases
# ---------------------------------------------------------------------------

def test_forensic_case_1_multiple_select_blocks():
    """Case 1: Multiple SELECT blocks — indexed target + sequential sibling, sequential target + indexed sibling."""
    code = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. CASE1.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT SEQ-FILE ASSIGN TO "SEQ.DAT"
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT IDX-FILE ASSIGN TO "IDX.DAT"
               ORGANIZATION IS INDEXED
               RECORD KEY IS REC-KEY.
       DATA DIVISION.
       FILE SECTION.
       FD SEQ-FILE.
       01 SEQ-REC PIC X(10).
       FD IDX-FILE.
       01 IDX-REC.
          05 REC-KEY PIC X(5).
          05 REC-VAL PIC X(5).
       PROCEDURE DIVISION.
           GOBACK.
    """
    fixture = ParityFixture(name="case1", program_name="CASE1", cobol_code=code, declared_outputs=["SEQ.DAT", "IDX.DAT"])
    # Sequential sibling must NEVER be detected as indexed/relative
    assert is_indexed_or_relative_file(fixture, "SEQ.DAT") is False
    # Indexed target must be detected
    assert is_indexed_or_relative_file(fixture, "IDX.DAT") is True

    # Sequential sibling with missing record must FAIL
    res_seq = _simulate_comparison(fixture, "SEQ.DAT", b"REC-A\nREC-B\n", b"REC-A\n")
    assert res_seq is not None

    # Indexed target with container equivalence must PASS
    res_idx = _simulate_comparison(fixture, "IDX.DAT", b"CONTAINER-REC1", b"REC1\n")
    assert res_idx is None


def test_forensic_case_2_indexed_input_sequential_output():
    """Case 2: Indexed input + sequential output."""
    code = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. CASE2.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT IN-FILE ASSIGN TO "INPUT.IDX"
               ORGANIZATION IS INDEXED
               RECORD KEY IS IN-KEY.
           SELECT OUT-FILE ASSIGN TO "OUTPUT.DAT"
               ORGANIZATION IS LINE SEQUENTIAL.
       DATA DIVISION.
       FILE SECTION.
       FD IN-FILE.
       01 IN-REC.
          05 IN-KEY PIC X(5).
       FD OUT-FILE.
       01 OUT-REC PIC X(10).
       PROCEDURE DIVISION.
           GOBACK.
    """
    fixture = ParityFixture(name="case2", program_name="CASE2", cobol_code=code, declared_outputs=["OUTPUT.DAT"])
    assert is_indexed_or_relative_file(fixture, "OUTPUT.DAT") is False
    assert is_indexed_or_relative_file(fixture, "INPUT.IDX") is True
    # Sequential output must FAIL on missing record
    res = _simulate_comparison(fixture, "OUTPUT.DAT", b"REC-A\nREC-B\n", b"REC-A\n")
    assert res is not None


def test_forensic_case_3_relative_and_sequential_same_program():
    """Case 3: Relative + sequential files in the same program."""
    code = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. CASE3.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT REL-FILE ASSIGN TO "REL.DAT"
               ORGANIZATION IS RELATIVE
               RELATIVE KEY IS WS-RRN.
           SELECT SEQ-FILE ASSIGN TO "SEQ.DAT"
               ORGANIZATION IS SEQUENTIAL.
       DATA DIVISION.
       FILE SECTION.
       FD REL-FILE.
       01 REL-REC PIC X(10).
       FD SEQ-FILE.
       01 SEQ-REC PIC X(10).
       WORKING-STORAGE SECTION.
       01 WS-RRN PIC 9(4).
       PROCEDURE DIVISION.
           GOBACK.
    """
    fixture = ParityFixture(name="case3", program_name="CASE3", cobol_code=code, declared_outputs=["REL.DAT", "SEQ.DAT"])
    assert is_indexed_or_relative_file(fixture, "REL.DAT") is True
    assert is_indexed_or_relative_file(fixture, "SEQ.DAT") is False


def test_forensic_case_4_assign_to_literal():
    """Case 4: ASSIGN TO literal with path and single/double quotes."""
    code = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. CASE4.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT OUT-FILE ASSIGN TO 'reports/summary.txt'
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT IDX-FILE ASSIGN TO "data/store.idx"
               ORGANIZATION IS INDEXED
               RECORD KEY IS K.
       DATA DIVISION.
       FILE SECTION.
       FD OUT-FILE.
       01 OUT-REC PIC X(20).
       FD IDX-FILE.
       01 I-REC.
          05 K PIC X(5).
       PROCEDURE DIVISION.
           GOBACK.
    """
    fixture = ParityFixture(name="case4", program_name="CASE4", cobol_code=code, declared_outputs=["reports/summary.txt", "data/store.idx"])
    assert is_indexed_or_relative_file(fixture, "reports/summary.txt") is False
    assert is_indexed_or_relative_file(fixture, "data/store.idx") is True


def test_forensic_case_5_assign_to_working_storage_variable():
    """Case 5: ASSIGN TO WORKING-STORAGE variable containing filename."""
    code = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. CASE5.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT REL-FILE ASSIGN TO WS-REL-NAME
               ORGANIZATION IS RELATIVE
               RELATIVE KEY IS WS-KEY.
           SELECT SEQ-FILE ASSIGN TO WS-SEQ-NAME
               ORGANIZATION IS LINE SEQUENTIAL.
       DATA DIVISION.
       FILE SECTION.
       FD REL-FILE.
       01 REL-REC PIC X(10).
       FD SEQ-FILE.
       01 SEQ-REC PIC X(10).
       WORKING-STORAGE SECTION.
       01 WS-KEY PIC 9(4).
       01 WS-REL-NAME PIC X(10) VALUE "REL.DAT".
       01 WS-SEQ-NAME PIC X(10) VALUE "SEQ.TXT".
       PROCEDURE DIVISION.
           GOBACK.
    """
    fixture = ParityFixture(name="case5", program_name="CASE5", cobol_code=code, declared_outputs=["REL.DAT", "SEQ.TXT"])
    assert is_indexed_or_relative_file(fixture, "REL.DAT") is True
    assert is_indexed_or_relative_file(fixture, "SEQ.TXT") is False


def test_forensic_case_6_case_differences():
    """Case 6: Case differences (lowercase COBOL source)."""
    code = """       identification division.
       program-id. case6.
       environment division.
       input-output section.
       file-control.
           select idx-file assign to "out.dat"
               organization is indexed
               record key is rec-key.
       data division.
       file section.
       fd idx-file.
       01 idx-rec.
          05 rec-key pic x(5).
          05 rec-val pic x(5).
       procedure division.
           goback.
    """
    fixture = ParityFixture(name="case6", program_name="case6", cobol_code=code, declared_outputs=["out.dat"])
    assert is_indexed_or_relative_file(fixture, "out.dat") is True
    assert is_indexed_or_relative_file(fixture, "OUT.DAT") is True


def test_forensic_case_7_multiple_indexed_relative_files():
    """Case 7: Multiple indexed/relative files in the same program."""
    code = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. CASE7.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT IDX-1 ASSIGN TO "IDX1.DAT"
               ORGANIZATION IS INDEXED
               RECORD KEY IS K1.
           SELECT REL-2 ASSIGN TO "REL2.DAT"
               ORGANIZATION IS RELATIVE
               RELATIVE KEY IS K2.
           SELECT SEQ-3 ASSIGN TO "SEQ3.DAT"
               ORGANIZATION IS SEQUENTIAL.
       DATA DIVISION.
       FILE SECTION.
       FD IDX-1.
       01 R1.
          05 K1 PIC X(5).
       FD REL-2.
       01 R2.
          05 K2 PIC 9(4).
       FD SEQ-3.
       01 R3 PIC X(10).
       PROCEDURE DIVISION.
           GOBACK.
    """
    fixture = ParityFixture(name="case7", program_name="CASE7", cobol_code=code, declared_outputs=["IDX1.DAT", "REL2.DAT", "SEQ3.DAT"])
    assert is_indexed_or_relative_file(fixture, "IDX1.DAT") is True
    assert is_indexed_or_relative_file(fixture, "REL2.DAT") is True
    assert is_indexed_or_relative_file(fixture, "SEQ3.DAT") is False


def test_forensic_case_8_unrelated_occurrences_of_indexed_relative():
    """Case 8: Unrelated occurrences of INDEXED/RELATIVE elsewhere in COBOL source."""
    code = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. CASE8.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT OUT-FILE ASSIGN TO "OUTFILE.TXT"
               ORGANIZATION IS LINE SEQUENTIAL.
       DATA DIVISION.
       FILE SECTION.
       FD OUT-FILE.
       01 OUT-REC PIC X(20).
       WORKING-STORAGE SECTION.
       01 MY-TABLE.
          05 TAB-ITEM PIC X(10) OCCURS 10 TIMES INDEXED BY TAB-IDX.
       01 WS-RELATIVE-FLAG PIC X VALUE 'Y'.
       PROCEDURE DIVISION.
           * Comment: This procedure processes RELATIVE and INDEXED items
           MOVE 'A' TO WS-RELATIVE-FLAG.
           GOBACK.
    """
    fixture = ParityFixture(name="case8", program_name="CASE8", cobol_code=code, declared_outputs=["OUTFILE.TXT"])
    # Must NOT be fooled by OCCURS ... INDEXED BY, WS-RELATIVE-FLAG, or comments
    assert is_indexed_or_relative_file(fixture, "OUTFILE.TXT") is False


def test_forensic_case_9_missing_implicit_organization():
    """Case 9: Missing/implicit ORGANIZATION defaults to SEQUENTIAL."""
    code = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. CASE9.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT OUT-FILE ASSIGN TO "DEFAULT.DAT".
       DATA DIVISION.
       FILE SECTION.
       FD OUT-FILE.
       01 OUT-REC PIC X(20).
       PROCEDURE DIVISION.
           GOBACK.
    """
    fixture = ParityFixture(name="case9", program_name="CASE9", cobol_code=code, declared_outputs=["DEFAULT.DAT"])
    assert is_indexed_or_relative_file(fixture, "DEFAULT.DAT") is False


def test_forensic_case_10_target_filename_not_corresponding():
    """Case 10: Target filename that does not correspond to an indexed/relative SELECT."""
    code = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. CASE10.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT IDX-FILE ASSIGN TO "IDX.DAT"
               ORGANIZATION IS INDEXED
               RECORD KEY IS K.
       DATA DIVISION.
       FILE SECTION.
       FD IDX-FILE.
       01 R.
          05 K PIC X(5).
       PROCEDURE DIVISION.
           GOBACK.
    """
    fixture = ParityFixture(name="case10", program_name="CASE10", cobol_code=code, declared_outputs=["OTHER.DAT"])
    assert is_indexed_or_relative_file(fixture, "OTHER.DAT") is False


def test_forensic_case_11_comments_and_continuation_formatting():
    """Case 11: Comments and multi-line continuation formatting in SELECT clause."""
    code = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. CASE11.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT
      * Comment between SELECT and file name
               OUT-FILE
      * Comment between file name and ASSIGN
               ASSIGN TO "OUTFILE.TXT"
      * Comment before ORGANIZATION
               ORGANIZATION IS
      * Comment before LINE SEQUENTIAL
               LINE SEQUENTIAL.
       DATA DIVISION.
       FILE SECTION.
       FD OUT-FILE.
       01 OUT-REC PIC X(20).
       PROCEDURE DIVISION.
           GOBACK.
    """
    fixture = ParityFixture(name="case11", program_name="CASE11", cobol_code=code, declared_outputs=["OUTFILE.TXT"])
    assert is_indexed_or_relative_file(fixture, "OUTFILE.TXT") is False


def test_forensic_case_12_sequential_cannot_reach_fallback_with_indexed_relative_sibling():
    """Case 12: Ensure ordinary sequential file can NEVER reach fallback when sibling is INDEXED/RELATIVE."""
    code = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. CASE12.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT AUDIT-LOG ASSIGN TO "AUDIT.LOG"
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT MASTER-IDX ASSIGN TO "MASTER.DAT"
               ORGANIZATION IS INDEXED
               RECORD KEY IS M-KEY.
           SELECT TRANSACTION-REL ASSIGN TO "TRANS.DAT"
               ORGANIZATION IS RELATIVE
               RELATIVE KEY IS T-KEY.
       DATA DIVISION.
       FILE SECTION.
       FD AUDIT-LOG.
       01 A-REC PIC X(50).
       FD MASTER-IDX.
       01 M-REC.
          05 M-KEY PIC X(10).
       FD TRANSACTION-REL.
       01 T-REC PIC X(20).
       WORKING-STORAGE SECTION.
       01 T-KEY PIC 9(4).
       PROCEDURE DIVISION.
           GOBACK.
    """
    fixture = ParityFixture(
        name="case12",
        program_name="CASE12",
        cobol_code=code,
        declared_outputs=["AUDIT.LOG", "MASTER.DAT", "TRANS.DAT"],
    )

    # AUDIT.LOG must be strictly sequential
    assert is_indexed_or_relative_file(fixture, "AUDIT.LOG") is False
    assert is_indexed_or_relative_file(fixture, "MASTER.DAT") is True
    assert is_indexed_or_relative_file(fixture, "TRANS.DAT") is True

    # Missing log line: Java only has START line, missing END line
    c_bytes = b"LOG1: START\nLOG2: END\n"
    j_bytes = b"LOG1: START\n"

    # Under old logic, this was a FALSE PASS
    old_res = _simulate_comparison(fixture, "AUDIT.LOG", c_bytes, j_bytes, use_old_logic=True)
    assert old_res is None, "Old logic falsely passed"

    # Under remediated logic, it MUST FAIL
    new_res = _simulate_comparison(fixture, "AUDIT.LOG", c_bytes, j_bytes, use_old_logic=False)
    assert new_res is not None, "Remediated logic must reject missing record"
    assert new_res.target == "file:AUDIT.LOG"


def test_forensic_case_13_forced_ast_parser_failure_safety_check(monkeypatch):
    """Case 13 (Final Gate): Force AST failure and prove fallback safety.
    Verifies that when CobolParser fails:
    1. Sequential target + indexed sibling -> False (NO bleed)
    2. Sequential target + relative sibling -> False (NO bleed)
    3. Sequential target + both siblings -> False (NO bleed)
    4. Indexed target -> True
    5. Relative target -> True
    6. Uncertainty resolves to non-indexed (False), byte-exact comparison enforced.
    """
    import modernize.parser

    def mock_parse_fail(self):
        raise RuntimeError("Simulated CobolParser failure")

    monkeypatch.setattr(modernize.parser.CobolParser, "parse", mock_parse_fail)

    # Program with both Indexed and Relative files plus a Sequential target
    code = """       IDENTIFICATION DIVISION.
       PROGRAM-ID. GATE13.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT SEQ-LOG ASSIGN TO "SEQ.LOG"
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT IDX-DB ASSIGN TO "IDX.DB"
               ORGANIZATION IS INDEXED
               RECORD KEY IS M-KEY.
           SELECT REL-DATA ASSIGN TO "REL.DATA"
               ORGANIZATION IS RELATIVE
               RELATIVE KEY IS R-KEY.
       DATA DIVISION.
       FILE SECTION.
       FD SEQ-LOG.
       01 S-REC PIC X(50).
       FD IDX-DB.
       01 M-REC.
          05 M-KEY PIC X(10).
       FD REL-DATA.
       01 R-REC PIC X(20).
       WORKING-STORAGE SECTION.
       01 R-KEY PIC 9(4).
       PROCEDURE DIVISION.
           GOBACK.
    """
    fixture = ParityFixture(
        name="gate13",
        program_name="GATE13",
        cobol_code=code,
        declared_outputs=["SEQ.LOG", "IDX.DB", "REL.DATA"],
    )

    # 1. Sequential target with indexed sibling -> False
    assert is_indexed_or_relative_file(fixture, "SEQ.LOG") is False

    # 2. Sequential target with relative sibling -> False
    assert is_indexed_or_relative_file(fixture, "SEQ.LOG") is False

    # 3. Sequential target with both siblings -> False
    assert is_indexed_or_relative_file(fixture, "SEQ.LOG") is False

    # 4. Indexed target -> True
    assert is_indexed_or_relative_file(fixture, "IDX.DB") is True

    # 5. Relative target -> True
    assert is_indexed_or_relative_file(fixture, "REL.DATA") is True

    # 6. Target not in program -> False
    assert is_indexed_or_relative_file(fixture, "UNKNOWN.DAT") is False

    # 7. Sequential comparison with missing records MUST fail under AST failure
    c_bytes = b"REC-A\nREC-B\n"
    j_bytes = b"REC-A\n"
    res = _simulate_comparison(fixture, "SEQ.LOG", c_bytes, j_bytes, use_old_logic=False)
    assert res is not None, "Fallback must enforce byte-exact match on sequential file"
    assert res.target == "file:SEQ.LOG"
