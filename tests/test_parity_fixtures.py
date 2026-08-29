"""
Differential Parity Fixture Suite — Phase 0/1 Hardening
========================================================
Each test uses run_parity() to:
  1. Compile + run the COBOL with GnuCOBOL (Docker canonical).
  2. Transpile to Java, compile, run.
  3. Compare: exit code, stdout (bytes), stderr (normalized), output files (bytes).

Environment:
  PARITY_ALLOW_SKIP=true   → skip gracefully when Docker is unavailable.
  PARITY_ALLOW_SKIP=false  → fail hard (CI canonical mode).

Evidence level: tests that PASS grant DIFFERENTIALLY_VERIFIED status to the
covered construct in modernize/capability_matrix.py.
"""

import json
import os
import pytest

from tests.utils.parity_harness import (
    ParityFixture,
    run_parity,
    compare_fixed_records,
    normalize_stderr,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def verify_comparison(comparison, *, record_len: int = 0):
    """Assert PASS, skip on SKIP, fail with actionable detail on FAIL."""
    if comparison.status == "SKIP":
        pytest.skip(comparison.skip_reason)
    if comparison.status == "FAIL":
        details = []
        for m in comparison.mismatches:
            details.append(
                f"  target={m.target!r}  offset={m.offset}\n"
                f"  cobol_hex=[{m.cobol_hex}]  java_hex=[{m.java_hex}]\n"
                f"  record={m.record_number}  likely_cause={m.likely_cause!r}\n"
                f"  explanation: {m.explanation}"
            )
        pytest.fail("Parity FAIL:\n" + "\n".join(details))


def load_fixtures_spec():
    spec_path = os.path.join(os.path.dirname(__file__), "fixtures_spec.json")
    with open(spec_path, "r", encoding="utf-8") as f:
        return json.load(f)


FIXTURES = load_fixtures_spec()


def generate_cobol_source(spec):
    """Generate a minimal COBOL program from a fixtures_spec.json entry."""
    lines = [
        "       IDENTIFICATION DIVISION.",
        f"       PROGRAM-ID. {spec['program_name']}.",
        "       DATA DIVISION.",
        "       WORKING-STORAGE SECTION.",
        "       01 WS-GROUP.",
    ]

    for i, var in enumerate(spec["variables"]):
        pic_clause = f"PIC {var['pic']}" if var.get("pic") else ""
        redef_clause = f"REDEFINES {var['redefines']}" if var.get("redefines") else ""
        usage = var.get("usage", "")
        usage_clause = f"USAGE {usage}" if usage else ""
        sign_clause = ""
        if (
            var.get("signed", False)
            or (pic_clause and "S" in var.get("pic", ""))
        ) and usage not in ("COMP-3", "PACKED-DECIMAL"):
            sign_pos = var.get("sign_position", "TRAILING")
            sign_sep = "SEPARATE CHARACTER" if var.get("sign_separate", False) else ""
            sign_clause = f"SIGN IS {sign_pos} {sign_sep}".strip()

        parts = [p for p in ["05", var["name"], redef_clause, pic_clause, usage_clause, sign_clause] if p]
        lines.append("          " + " ".join(parts) + ".")
        if i < len(spec["variables"]) - 1:
            next_var = spec["variables"][i + 1]
            if not next_var.get("redefines"):
                lines.append("          05 FILLER PIC X VALUE '|'.")

    lines.append("       PROCEDURE DIVISION.")
    init_vars = [v["name"] for v in spec["variables"] if not v.get("redefines")]
    lines.append(f"           INITIALIZE {' '.join(init_vars)}.")
    for var in spec["variables"]:
        val = var.get("value")
        if val:
            lines.append(f"           MOVE {val} TO {var['name']}.")
    for stmt in spec["statements"]:
        lines.append(f"           {stmt}.")
    lines.append("           GOBACK.")
    return "\n".join(lines)


# ===========================================================================
# MILESTONE A — Existing hand-written fixtures (carry over from prior phase)
# ===========================================================================

def test_milestone_a_basic_move():
    """Fixture A1: Basic PIC X / PIC 9 MOVE verification."""
    cobol_code = """\
       IDENTIFICATION DIVISION.
       PROGRAM-ID. MOVEPROG.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-STR-A PIC X(10) VALUE "ABC".
       01 WS-STR-B PIC X(5).
       01 WS-NUM-A PIC 9(4) VALUE 123.
       01 WS-NUM-B PIC 9(6).
       PROCEDURE DIVISION.
           MOVE WS-STR-A TO WS-STR-B
           MOVE WS-NUM-A TO WS-NUM-B
           DISPLAY WS-STR-B
           DISPLAY WS-NUM-B
           GOBACK.
"""
    fixture = ParityFixture(
        name="milestone_a_basic_move",
        program_name="MOVEPROG",
        cobol_code=cobol_code,
    )
    verify_comparison(run_parity(fixture))


def test_milestone_a_integer_compute_add():
    """Fixture A2: Basic COMPUTE and ADD verification (integer only)."""
    cobol_code = """\
       IDENTIFICATION DIVISION.
       PROGRAM-ID. ARITHPROG.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-NUM-A PIC 9(4) VALUE 10.
       01 WS-NUM-B PIC 9(4) VALUE 20.
       01 WS-NUM-C PIC 9(4) VALUE 0.
       PROCEDURE DIVISION.
           ADD WS-NUM-A TO WS-NUM-B GIVING WS-NUM-C
           DISPLAY WS-NUM-C
           COMPUTE WS-NUM-C = WS-NUM-A * 5 + WS-NUM-B
           DISPLAY WS-NUM-C
           GOBACK.
"""
    fixture = ParityFixture(
        name="milestone_a_integer_compute_add",
        program_name="ARITHPROG",
        cobol_code=cobol_code,
    )
    verify_comparison(run_parity(fixture))


def test_milestone_a_line_sequential_file():
    """Fixture A3: Simple line-sequential output file (ASCII records)."""
    cobol_code = """\
       IDENTIFICATION DIVISION.
       PROGRAM-ID. SEQFILEPROG.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT OUT-FILE ASSIGN TO "OUTFILE.TXT"
           ORGANIZATION IS LINE SEQUENTIAL.
       DATA DIVISION.
       FILE SECTION.
       FD OUT-FILE.
       01 OUT-REC PIC X(20).
       PROCEDURE DIVISION.
           OPEN OUTPUT OUT-FILE
           MOVE "HELLO WORLD 1" TO OUT-REC
           WRITE OUT-REC
           MOVE "HELLO WORLD 2" TO OUT-REC
           WRITE OUT-REC
           CLOSE OUT-FILE
           DISPLAY "FILE WRITTEN"
           GOBACK.
"""
    fixture = ParityFixture(
        name="milestone_a_line_sequential_file",
        program_name="SEQFILEPROG",
        cobol_code=cobol_code,
        declared_outputs=["OUTFILE.TXT"],
    )
    verify_comparison(run_parity(fixture))


def test_milestone_b_fixed_binary_file_io():
    """Fixture A4: Fixed-length binary sequential file with COMP-3 and signed zoned decimal."""
    cobol_code = """\
       IDENTIFICATION DIVISION.
       PROGRAM-ID. BINIO.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT BIN-FILE ASSIGN TO "BINFILE.DAT"
           ORGANIZATION IS SEQUENTIAL.
       DATA DIVISION.
       FILE SECTION.
       FD BIN-FILE.
       01 BIN-REC.
          05 FIELD-COMP3 PIC S9(4)V99 COMP-3.
          05 FIELD-ZONED PIC S9(4) SIGN IS TRAILING SEPARATE CHARACTER.
       WORKING-STORAGE SECTION.
       01 WS-VAR.
          05 WS-COMP3 PIC S9(4)V99 COMP-3.
          05 WS-ZONED PIC S9(4) SIGN IS TRAILING SEPARATE CHARACTER.
       PROCEDURE DIVISION.
           OPEN OUTPUT BIN-FILE.
           MOVE -12.34 TO WS-COMP3.
           MOVE -5678 TO WS-ZONED.
           MOVE WS-COMP3 TO FIELD-COMP3.
           MOVE WS-ZONED TO FIELD-ZONED.
           WRITE BIN-REC.
           CLOSE BIN-FILE.

           INITIALIZE BIN-REC.
           OPEN INPUT BIN-FILE.
           READ BIN-FILE.
           CLOSE BIN-FILE.
           DISPLAY FIELD-COMP3.
           DISPLAY FIELD-ZONED.
           GOBACK.
"""
    fixture = ParityFixture(
        name="milestone_b_fixed_binary_file_io",
        program_name="BINIO",
        cobol_code=cobol_code,
        declared_outputs=["BINFILE.DAT"],
    )
    verify_comparison(run_parity(fixture))


def test_milestone_b_integer_fast_path_audit():
    """Fixture A5: Fast-path signed integer DISPLAY parity validation."""
    cobol_code = """\
       IDENTIFICATION DIVISION.
       PROGRAM-ID. FPFAST.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-VARS.
          05 WS-INT PIC S9(9).
          05 WS-LONG PIC S9(15).
       PROCEDURE DIVISION.
           MOVE 123456789 TO WS-INT.
           MOVE -987654321012345 TO WS-LONG.
           DISPLAY WS-INT.
           DISPLAY WS-LONG.
           ADD 10 TO WS-INT.
           SUBTRACT 100 FROM WS-LONG.
           DISPLAY WS-INT.
           DISPLAY WS-LONG.
           GOBACK.
"""
    fixture = ParityFixture(
        name="milestone_b_integer_fast_path_audit",
        program_name="FPFAST",
        cobol_code=cobol_code,
    )
    verify_comparison(run_parity(fixture))


# ===========================================================================
# MILESTONE B — Parametrized numeric fixture suite (23 from fixtures_spec.json)
# ===========================================================================

@pytest.mark.parametrize("spec", FIXTURES, ids=lambda s: s["name"])
def test_milestone_b_parity(spec):
    """Phase B1: Wire all 23 numeric fixtures from fixtures_spec.json to run_parity()."""
    cobol_code = generate_cobol_source(spec)
    fixture = ParityFixture(
        name=spec["name"],
        program_name=spec["program_name"],
        cobol_code=cobol_code,
    )
    res = run_parity(fixture)
    verify_comparison(res)


# ===========================================================================
# MILESTONE C — New Phase B fixtures (file I/O, linkage, PERFORM, SQL, JCL)
# These fixtures reach 28+ total differential tests.
# ===========================================================================

# --- Fixture 10: Fixed-length records (record-by-record comparison) ----------

def test_parity_fixed_length_records():
    """Fixture 10: Fixed-length sequential records — byte-exact comparison per record."""
    cobol_code = """\
       IDENTIFICATION DIVISION.
       PROGRAM-ID. FIXREC.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT FIXED-FILE ASSIGN TO "FIXED.DAT"
           ORGANIZATION IS SEQUENTIAL.
       DATA DIVISION.
       FILE SECTION.
       FD FIXED-FILE.
       01 FIXED-REC.
          05 REC-ID  PIC 9(4).
          05 REC-AMT PIC S9(6)V99 COMP-3.
          05 REC-NAM PIC X(20).
       PROCEDURE DIVISION.
           OPEN OUTPUT FIXED-FILE.
           MOVE 0001 TO REC-ID.
           MOVE 12345.67 TO REC-AMT.
           MOVE "ALICE SMITH" TO REC-NAM.
           WRITE FIXED-REC.
           MOVE 0002 TO REC-ID.
           MOVE -99.01 TO REC-AMT.
           MOVE "BOB JONES" TO REC-NAM.
           WRITE FIXED-REC.
           MOVE 0003 TO REC-ID.
           MOVE 0 TO REC-AMT.
           MOVE "ZERO AMOUNT" TO REC-NAM.
           WRITE FIXED-REC.
           CLOSE FIXED-FILE.
           DISPLAY "RECORDS WRITTEN".
           GOBACK.
"""
    fixture = ParityFixture(
        name="parity_fixed_length_records",
        program_name="FIXREC",
        cobol_code=cobol_code,
        declared_outputs=["FIXED.DAT"],
    )
    res = run_parity(fixture)
    verify_comparison(res)


# --- Fixture 11: Trailing spaces in alphanumeric fields ---------------------

def test_parity_trailing_spaces():
    """Fixture 11: Trailing space preservation in PIC X fields."""
    cobol_code = """\
       IDENTIFICATION DIVISION.
       PROGRAM-ID. TRAILSP.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-FULL PIC X(10) VALUE "AB".
       01 WS-OUT  PIC X(10).
       PROCEDURE DIVISION.
           MOVE WS-FULL TO WS-OUT.
           DISPLAY "|" WS-OUT "|".
           MOVE "XYZ" TO WS-FULL.
           DISPLAY "|" WS-FULL "|".
           GOBACK.
"""
    fixture = ParityFixture(
        name="parity_trailing_spaces",
        program_name="TRAILSP",
        cobol_code=cobol_code,
    )
    verify_comparison(run_parity(fixture))


# --- Fixture 12: COMP-3 in-file round trip ----------------------------------

def test_parity_comp3_file_roundtrip():
    """Fixture 12/13: Write COMP-3 field to file, read back, verify value + display."""
    cobol_code = """\
       IDENTIFICATION DIVISION.
       PROGRAM-ID. C3FILE.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT C3-FILE ASSIGN TO "C3.DAT"
           ORGANIZATION IS SEQUENTIAL.
       DATA DIVISION.
       FILE SECTION.
       FD C3-FILE.
       01 C3-REC.
          05 C3-VAL PIC S9(7)V99 COMP-3.
       WORKING-STORAGE SECTION.
       01 WS-VAL PIC S9(7)V99 COMP-3 VALUE -9876543.21.
       PROCEDURE DIVISION.
           OPEN OUTPUT C3-FILE.
           MOVE WS-VAL TO C3-VAL.
           WRITE C3-REC.
           CLOSE C3-FILE.
           INITIALIZE C3-REC.
           OPEN INPUT C3-FILE.
           READ C3-FILE.
           CLOSE C3-FILE.
           DISPLAY C3-VAL.
           GOBACK.
"""
    fixture = ParityFixture(
        name="parity_comp3_file_roundtrip",
        program_name="C3FILE",
        cobol_code=cobol_code,
        declared_outputs=["C3.DAT"],
    )
    verify_comparison(run_parity(fixture))


# --- Fixture 14: REDEFINES group view (write via one, read via other) --------

@pytest.mark.skip(reason="Group view redefines require shared byte-backed storage; planned for Phase 3")
def test_parity_redefines_group_view():
    """Fixture 15: REDEFINES group view — write through group, read back as scalar."""
    cobol_code = """\
       IDENTIFICATION DIVISION.
       PROGRAM-ID. REFGRP.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-GROUP-A.
          05 GA-HIGH PIC 9(2).
          05 GA-LOW  PIC 9(2).
       01 WS-GROUP-B REDEFINES WS-GROUP-A.
          05 GB-FULL PIC 9(4).
       PROCEDURE DIVISION.
           MOVE 12 TO GA-HIGH.
           MOVE 34 TO GA-LOW.
           DISPLAY GB-FULL.
           MOVE 5678 TO GB-FULL.
           DISPLAY GA-HIGH.
           DISPLAY GA-LOW.
           GOBACK.
"""
    fixture = ParityFixture(
        name="parity_redefines_group_view",
        program_name="REFGRP",
        cobol_code=cobol_code,
    )
    verify_comparison(run_parity(fixture))


# --- Fixture 15: OCCURS DEPENDING ON ----------------------------------------

def test_parity_occurs_depending_on():
    """Fixture 17: OCCURS DEPENDING ON with variable bound — verify element access."""
    cobol_code = """\
       IDENTIFICATION DIVISION.
       PROGRAM-ID. ODOPROG.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-BOUND PIC 9(2) VALUE 3.
       01 WS-TABLE.
          05 WS-ELEM PIC 9(4) OCCURS 1 TO 5 TIMES
             DEPENDING ON WS-BOUND.
       PROCEDURE DIVISION.
           MOVE 10 TO WS-ELEM(1).
           MOVE 20 TO WS-ELEM(2).
           MOVE 30 TO WS-ELEM(3).
           DISPLAY WS-ELEM(1).
           DISPLAY WS-ELEM(2).
           DISPLAY WS-ELEM(3).
           GOBACK.
"""
    fixture = ParityFixture(
        name="parity_occurs_depending_on",
        program_name="ODOPROG",
        cobol_code=cobol_code,
    )
    verify_comparison(run_parity(fixture))


# --- Fixture 16: PERFORM THRU -----------------------------------------------

def test_parity_perform_thru():
    """Fixture 18: PERFORM THRU paragraph range — verify all paragraphs execute in order."""
    cobol_code = """\
       IDENTIFICATION DIVISION.
       PROGRAM-ID. PERFTHRU.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-CTR PIC 9(2) VALUE 0.
       PROCEDURE DIVISION.
           PERFORM PARA-A THRU PARA-C.
           DISPLAY WS-CTR.
           GOBACK.
       PARA-A.
           ADD 1 TO WS-CTR.
       PARA-B.
           ADD 10 TO WS-CTR.
       PARA-C.
           ADD 100 TO WS-CTR.
"""
    fixture = ParityFixture(
        name="parity_perform_thru",
        program_name="PERFTHRU",
        cobol_code=cobol_code,
    )
    verify_comparison(run_parity(fixture))


# --- Fixture 17: GO TO within performed range --------------------------------

def test_parity_goto_in_perform_range():
    """Fixture 19: GO TO within a PERFORM THRU range — verify correct exit."""
    cobol_code = """\
       IDENTIFICATION DIVISION.
       PROGRAM-ID. GOTOTHRU.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-FLAG PIC 9 VALUE 0.
       01 WS-OUT  PIC 9(4) VALUE 0.
       PROCEDURE DIVISION.
           MOVE 1 TO WS-FLAG.
           PERFORM SECT-A THRU SECT-B.
           DISPLAY WS-OUT.
           GOBACK.
       SECT-A.
           ADD 100 TO WS-OUT.
           IF WS-FLAG = 1
               GO TO SECT-B.
           ADD 999 TO WS-OUT.
       SECT-B.
           ADD 10 TO WS-OUT.
"""
    fixture = ParityFixture(
        name="parity_goto_in_perform_range",
        program_name="GOTOTHRU",
        cobol_code=cobol_code,
    )
    verify_comparison(run_parity(fixture))


# --- Fixture 18: CALL BY REFERENCE mutation ---------------------------------

def test_parity_call_by_reference():
    """Fixture 21: CALL BY REFERENCE — verify caller sees mutation made by callee."""
    # Callee program
    callee_code = """\
       IDENTIFICATION DIVISION.
       PROGRAM-ID. CALLEE.
       DATA DIVISION.
       LINKAGE SECTION.
       01 LS-VALUE PIC S9(9).
       PROCEDURE DIVISION USING LS-VALUE.
           ADD 1000 TO LS-VALUE.
           GOBACK.
"""
    # Caller program
    caller_code = """\
       IDENTIFICATION DIVISION.
       PROGRAM-ID. CALLER.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-AMOUNT PIC S9(9) VALUE 42.
       PROCEDURE DIVISION.
           CALL "CALLEE" USING BY REFERENCE WS-AMOUNT.
           DISPLAY WS-AMOUNT.
           GOBACK.
"""
    # For parity: combine into single source (nested program)
    combined_code = """\
       IDENTIFICATION DIVISION.
       PROGRAM-ID. CALLER.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-AMOUNT PIC S9(9) VALUE 42.
       PROCEDURE DIVISION.
           CALL "CALLEE" USING BY REFERENCE WS-AMOUNT.
           DISPLAY WS-AMOUNT.
           GOBACK.
       IDENTIFICATION DIVISION.
       PROGRAM-ID. CALLEE.
       DATA DIVISION.
       LINKAGE SECTION.
       01 LS-VALUE PIC S9(9).
       PROCEDURE DIVISION USING LS-VALUE.
           ADD 1000 TO LS-VALUE.
           GOBACK.
       END PROGRAM CALLEE.
       END PROGRAM CALLER.
"""
    fixture = ParityFixture(
        name="parity_call_by_reference",
        program_name="CALLER",
        cobol_code=combined_code,
    )
    verify_comparison(run_parity(fixture))


# --- Fixture 19: CALL BY CONTENT isolation ----------------------------------

@pytest.mark.skip(reason="CALL BY CONTENT parameter isolation requires layout copy; planned for Phase 3")
def test_parity_call_by_content():
    """Fixture 22: CALL BY CONTENT — verify caller value unchanged after callee mutation."""
    combined_code = """\
       IDENTIFICATION DIVISION.
       PROGRAM-ID. CALLCONT.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-ORIGINAL PIC 9(6) VALUE 999.
       PROCEDURE DIVISION.
           CALL "MUTATOR" USING BY CONTENT WS-ORIGINAL.
           DISPLAY WS-ORIGINAL.
           GOBACK.
       IDENTIFICATION DIVISION.
       PROGRAM-ID. MUTATOR.
       DATA DIVISION.
       LINKAGE SECTION.
       01 LS-PARAM PIC 9(6).
       PROCEDURE DIVISION USING LS-PARAM.
           ADD 1 TO LS-PARAM.
           GOBACK.
       END PROGRAM MUTATOR.
       END PROGRAM CALLCONT.
"""
    fixture = ParityFixture(
        name="parity_call_by_content",
        program_name="CALLCONT",
        cobol_code=combined_code,
    )
    verify_comparison(run_parity(fixture))


# --- Fixture 20: PERFORM VARYING ---------------------------------------------

@pytest.mark.skip(reason="PERFORM VARYING paragraph loop requires procedure pointer mapping; planned for Phase 3")
def test_parity_perform_varying():
    """Fixture 16: PERFORM VARYING with FROM/BY/UNTIL — verify loop count and accumulator."""
    cobol_code = """\
       IDENTIFICATION DIVISION.
       PROGRAM-ID. PVARY.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-I   PIC 9(4) VALUE 0.
       01 WS-SUM PIC 9(6) VALUE 0.
       PROCEDURE DIVISION.
           PERFORM ADD-LOOP
               VARYING WS-I FROM 1 BY 1 UNTIL WS-I > 5.
           DISPLAY WS-SUM.
           GOBACK.
       ADD-LOOP.
           ADD WS-I TO WS-SUM.
"""
    fixture = ParityFixture(
        name="parity_perform_varying",
        program_name="PVARY",
        cobol_code=cobol_code,
    )
    verify_comparison(run_parity(fixture))


# --- Fixture 21: String operations ------------------------------------------

def test_parity_string_operations():
    """Fixture: STRING INTO and UNSTRING — verify output strings match GnuCOBOL."""
    cobol_code = """\
       IDENTIFICATION DIVISION.
       PROGRAM-ID. STROPS.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-FIRST  PIC X(10) VALUE "HELLO".
       01 WS-SECOND PIC X(10) VALUE "WORLD".
       01 WS-JOINED PIC X(25).
       01 WS-P1     PIC X(10).
       01 WS-P2     PIC X(10).
       PROCEDURE DIVISION.
           STRING WS-FIRST " " WS-SECOND INTO WS-JOINED.
           DISPLAY WS-JOINED.
           UNSTRING WS-JOINED DELIMITED BY " " INTO WS-P1 WS-P2.
           DISPLAY WS-P1.
           DISPLAY WS-P2.
           GOBACK.
"""
    fixture = ParityFixture(
        name="parity_string_operations",
        program_name="STROPS",
        cobol_code=cobol_code,
    )
    verify_comparison(run_parity(fixture))


# --- Fixture 22: Signed display with arithmetic overflow ---------------------

def test_parity_signed_overflow_truncation():
    """Fixture: Signed overflow truncation (silent high-order drop, no SIZE ERROR)."""
    cobol_code = """\
       IDENTIFICATION DIVISION.
       PROGRAM-ID. SIGOVER.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-A PIC S9(3) VALUE 999.
       01 WS-B PIC S9(3) VALUE 0.
       PROCEDURE DIVISION.
           ADD 1 TO WS-A GIVING WS-B.
           DISPLAY WS-B.
           GOBACK.
"""
    fixture = ParityFixture(
        name="parity_signed_overflow_truncation",
        program_name="SIGOVER",
        cobol_code=cobol_code,
    )
    verify_comparison(run_parity(fixture))


# --- Fixture 23: ON SIZE ERROR path -----------------------------------------

def test_parity_on_size_error_explicit():
    """Fixture 9: ON SIZE ERROR fires and target unchanged — differential verification."""
    cobol_code = """\
       IDENTIFICATION DIVISION.
       PROGRAM-ID. SIZEERR.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-TGT PIC 9(2) VALUE 50.
       PROCEDURE DIVISION.
            ADD 60 TO WS-TGT
                ON SIZE ERROR DISPLAY "OVERFLOW"
            END-ADD
            DISPLAY WS-TGT.
           GOBACK.
"""
    fixture = ParityFixture(
        name="parity_on_size_error_explicit",
        program_name="SIZEERR",
        cobol_code=cobol_code,
    )
    verify_comparison(run_parity(fixture))


# --- Fixture 24: EBCDIC records (skip — unsupported) ------------------------

@pytest.mark.skip(reason="EBCDIC file I/O is UNSUPPORTED — no codec in file path")
def test_parity_ebcdic_records():
    """Fixture 12: EBCDIC sequential file — skipped pending codec implementation."""
    pass


# --- Fixture 25: Relative file random access --------------------------------

@pytest.mark.skip(reason="RELATIVE file storage emulation requires Spring Boot/SQL database integration in harness; planned for Phase 4")
def test_parity_relative_file_random_access():
    """Fixture 23: Relative file — write 3 records, read back by RRN."""
    cobol_code = """\
       IDENTIFICATION DIVISION.
       PROGRAM-ID. RELFILE.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT REL-FILE ASSIGN TO "REL.DAT"
           ORGANIZATION IS RELATIVE
           ACCESS IS RANDOM
           RELATIVE KEY IS WS-RRN.
       DATA DIVISION.
       FILE SECTION.
       FD REL-FILE.
       01 REL-REC.
          05 R-DATA PIC X(20).
       WORKING-STORAGE SECTION.
       01 WS-RRN PIC 9(4).
       PROCEDURE DIVISION.
           OPEN OUTPUT REL-FILE.
           MOVE 1 TO WS-RRN.
           MOVE "RECORD ONE" TO R-DATA.
           WRITE REL-REC.
           MOVE 2 TO WS-RRN.
           MOVE "RECORD TWO" TO R-DATA.
           WRITE REL-REC.
           MOVE 3 TO WS-RRN.
           MOVE "RECORD THREE" TO R-DATA.
           WRITE REL-REC.
           CLOSE REL-FILE.

           OPEN INPUT REL-FILE.
           MOVE 2 TO WS-RRN.
           READ REL-FILE.
           DISPLAY R-DATA.
           MOVE 1 TO WS-RRN.
           READ REL-FILE.
           DISPLAY R-DATA.
           CLOSE REL-FILE.
           GOBACK.
"""
    fixture = ParityFixture(
        name="parity_relative_file_random_access",
        program_name="RELFILE",
        cobol_code=cobol_code,
        declared_outputs=["REL.DAT"],
    )
    verify_comparison(run_parity(fixture))


# --- Fixture 26: Indexed file missing + duplicate key -----------------------

@pytest.mark.skip(reason="INDEXED file storage emulation requires Spring Boot/SQL database integration in harness; planned for Phase 4")
def test_parity_indexed_file_missing_key():
    """Fixture 24a: Indexed file — read missing key yields FILE STATUS 23."""
    cobol_code = """\
       IDENTIFICATION DIVISION.
       PROGRAM-ID. IDXMISS.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT IDX-FILE ASSIGN TO "IDX.DAT"
           ORGANIZATION IS INDEXED
           ACCESS IS RANDOM
           RECORD KEY IS REC-KEY
           FILE STATUS IS WS-STATUS.
       DATA DIVISION.
       FILE SECTION.
       FD IDX-FILE.
       01 IDX-REC.
          05 REC-KEY PIC X(5).
          05 REC-VAL PIC X(20).
       WORKING-STORAGE SECTION.
       01 WS-STATUS PIC XX.
       PROCEDURE DIVISION.
           OPEN OUTPUT IDX-FILE.
           MOVE "KEY01" TO REC-KEY.
           MOVE "VALUE ONE" TO REC-VAL.
           WRITE IDX-REC.
           CLOSE IDX-FILE.

           OPEN INPUT IDX-FILE.
           MOVE "NOKEY" TO REC-KEY.
           READ IDX-FILE.
           DISPLAY WS-STATUS.
           CLOSE IDX-FILE.
           GOBACK.
"""
    fixture = ParityFixture(
        name="parity_indexed_file_missing_key",
        program_name="IDXMISS",
        cobol_code=cobol_code,
        declared_outputs=["IDX.DAT"],
    )
    verify_comparison(run_parity(fixture))


# --- Fixture 27: JCL conditional execution (step COND routing) --------------

@pytest.mark.skip(reason="JCL conditional parity requires JCL pipeline Docker integration; planned for Phase 6")
def test_parity_jcl_conditional():
    """Fixture 28: JCL COND conditional execution — skipped pending JCL Docker harness."""
    pass


# --- Fixture 28: Evaluate with WHEN OTHER -----------------------------------

def test_parity_evaluate_when_other():
    """Fixture: EVALUATE with WHEN OTHER branch — verify branch selection."""
    cobol_code = """\
       IDENTIFICATION DIVISION.
       PROGRAM-ID. EVALOTH.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-CODE PIC 9 VALUE 7.
       01 WS-OUT  PIC X(10).
       PROCEDURE DIVISION.
           EVALUATE WS-CODE
               WHEN 1 MOVE "ONE" TO WS-OUT
               WHEN 2 MOVE "TWO" TO WS-OUT
               WHEN OTHER MOVE "OTHER" TO WS-OUT
           END-EVALUATE.
           DISPLAY WS-OUT.
           GOBACK.
"""
    fixture = ParityFixture(
        name="parity_evaluate_when_other",
        program_name="EVALOTH",
        cobol_code=cobol_code,
    )
    verify_comparison(run_parity(fixture))


# --- Fixture 29: INSPECT TALLYING -------------------------------------------

def test_parity_inspect_tallying():
    """Fixture: INSPECT TALLYING — count occurrences of a character."""
    cobol_code = """\
       IDENTIFICATION DIVISION.
       PROGRAM-ID. INSPTAL.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-STR   PIC X(20) VALUE "HELLO WORLD HELLO".
       01 WS-COUNT PIC 9(4)  VALUE 0.
       PROCEDURE DIVISION.
           INSPECT WS-STR TALLYING WS-COUNT FOR ALL "L".
           DISPLAY WS-COUNT.
           GOBACK.
"""
    fixture = ParityFixture(
        name="parity_inspect_tallying",
        program_name="INSPTAL",
        cobol_code=cobol_code,
    )
    verify_comparison(run_parity(fixture))


# ---------------------------------------------------------------------------
# Unit / semantic validation tests (non-differential — kept from prior phase)
# ---------------------------------------------------------------------------

def test_unsupported_precision_guard_unit():
    """Assert UnsupportedPrecisionException fires for > 34 digit + guard combination."""
    spec = {
        "name": "milestone_b_unsupported_precision_guard",
        "program_name": "UNSUPPGD",
        "variables": [{"name": "A", "pic": "9(30)V9(5)", "value": "0"}],
        "statements": ["DIVIDE 1 BY 3 GIVING A", "DISPLAY WS-GROUP"],
    }
    cobol_code = generate_cobol_source(spec)
    fixture = ParityFixture(
        name=spec["name"],
        program_name=spec["program_name"],
        cobol_code=cobol_code,
    )

    from tests.utils.parity_harness import run_java_transpiled, run_cobol_baseline
    import tempfile
    import shutil

    temp_root = tempfile.mkdtemp(prefix="parity_unsupported_precision_")
    try:
        cobol_run_dir = os.path.join(temp_root, "cobol")
        java_run_dir = os.path.join(temp_root, "java")
        os.makedirs(cobol_run_dir, exist_ok=True)
        os.makedirs(java_run_dir, exist_ok=True)

        cobol_res = run_cobol_baseline(fixture, cobol_run_dir)
        assert cobol_res.termination_status != "error", f"COBOL compilation failed: {cobol_res.error_message}"

        java_res = run_java_transpiled(fixture, java_run_dir)
        assert (
            b"UnsupportedPrecisionException" in java_res.stderr
            or b"UnsupportedPrecisionException" in java_res.stdout
        )
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def test_unchecked_and_abs_assign_result_semantics_unit():
    """Assert UNCHECKED overflow truncates and abs() applied before unsigned bounds check."""
    from tests.utils.parity_harness import run_java_transpiled, run_cmd_bytes, PARITY_JDK_IMAGE
    import tempfile
    import shutil

    java_src = """\
package com.systema.modernized.native_gen;
import java.math.BigDecimal;
import com.systema.modernized.runtime.*;

public class Testuncheckedandabs {
    public void execute() {
        CobolNumericSpec specA = new CobolNumericSpec(false, 3, 0, CobolUsage.DISPLAY);
        CobolNumeric varA = new CobolNumeric(BigDecimal.ZERO, specA);
        AssignResult resA = varA.assign(new BigDecimal("1234"), CobolRoundingMode.TRUNCATION, SizeErrorPolicy.UNCHECKED);
        if (!resA.sizeError)
            throw new RuntimeException("Test A failed: sizeError was false under UNCHECKED");
        if (resA.storedValue.compareTo(new BigDecimal("234")) != 0)
            throw new RuntimeException("Test A failed: storedValue was not 234");

        CobolNumericSpec specB = new CobolNumericSpec(false, 3, 0, CobolUsage.DISPLAY);
        CobolNumeric varB = new CobolNumeric(BigDecimal.ZERO, specB);
        AssignResult resB = varB.assign(new BigDecimal("-5"), CobolRoundingMode.TRUNCATION, SizeErrorPolicy.UNCHECKED);
        if (resB.sizeError)
            throw new RuntimeException("Test B failed: sizeError was true for unsigned with negative input");
        if (resB.storedValue.compareTo(new BigDecimal("5")) != 0)
            throw new RuntimeException("Test B failed: storedValue was not 5");

        System.out.println("SEMANTICS_OK");
    }
    public static void main(String[] args) { new Testuncheckedandabs().execute(); }
}
"""
    dummy_fixture = ParityFixture(name="dummy", program_name="Dummy", cobol_code="")
    temp_root = tempfile.mkdtemp(prefix="unchecked_abs_semantics_")
    try:
        java_run_dir = os.path.join(temp_root, "java")
        os.makedirs(java_run_dir, exist_ok=True)
        run_java_transpiled(dummy_fixture, java_run_dir)
        pkg_dir = os.path.join(java_run_dir, "com", "systema", "modernized", "native_gen")
        os.makedirs(pkg_dir, exist_ok=True)
        with open(os.path.join(pkg_dir, "Testuncheckedandabs.java"), "w", encoding="utf-8") as f:
            f.write(java_src)
        run_dir_abs = os.path.abspath(java_run_dir).replace("\\", "/")
        inner_compile = (
            "javac -cp /run "
            "/run/com/systema/modernized/JclExecutionContext.java "
            "/run/com/systema/modernized/CicsProgramRegistry.java "
            "/run/com/systema/modernized/SpringContextHelper.java "
            "/run/com/systema/modernized/CobolFormatHelper.java "
            "/run/com/systema/modernized/runtime/*.java "
            "/run/com/systema/modernized/native_gen/Testuncheckedandabs.java"
        )
        compile_cmd = [
            "docker", "run", "--rm",
            "-v", f"{run_dir_abs}:/run",
            "-w", "/run",
            PARITY_JDK_IMAGE,
            "sh", "-c", inner_compile,
        ]
        rc, out, err, term = run_cmd_bytes(compile_cmd)
        assert rc == 0, f"Compilation failed: {err.decode('utf-8')}"
        run_cmd_args = [
            "docker", "run", "--rm",
            "-v", f"{run_dir_abs}:/run",
            "-w", "/run",
            PARITY_JDK_IMAGE,
            "java", "-cp", "/run", "com.systema.modernized.native_gen.Testuncheckedandabs",
        ]
        rc, out, err, term = run_cmd_bytes(run_cmd_args)
        assert rc == 0, f"Execution failed: {err.decode('utf-8')}"
        assert b"SEMANTICS_OK" in out
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def test_compiler_fingerprint_drift():
    """Assert the running GnuCOBOL Docker image matches the pinned fingerprint."""
    from tests.utils.check_fingerprint import EXPECTED_HASH, IMAGE, PARITY_ALLOW_SKIP
    import subprocess
    import hashlib

    try:
        docker_check = subprocess.run(["docker", "info"], capture_output=True, timeout=5)
        if docker_check.returncode != 0:
            if PARITY_ALLOW_SKIP:
                pytest.skip("Docker not available and PARITY_ALLOW_SKIP is true")
            else:
                pytest.fail("Docker not available and PARITY_ALLOW_SKIP is false")
    except Exception:
        if PARITY_ALLOW_SKIP:
            pytest.skip("Docker check failed and PARITY_ALLOW_SKIP is true")
        else:
            pytest.fail("Docker check failed and PARITY_ALLOW_SKIP is false")

    cmd = ["docker", "run", "--rm", IMAGE, "cobc", "--info"]
    res = subprocess.run(cmd, capture_output=True, timeout=30)
    assert res.returncode == 0, f"GnuCOBOL check exited {res.returncode}: {res.stderr.decode('utf-8')}"
    h = hashlib.sha256(res.stdout).hexdigest().lower()
    assert h == EXPECTED_HASH, f"GnuCOBOL fingerprint mismatch! Expected {EXPECTED_HASH}, got {h}"
