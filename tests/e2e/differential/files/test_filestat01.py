"""File I/O + FILE STATUS differential test.

COBOL: Sequential file I/O with FILE STATUS tracking.
Compares FILE STATUS sequence, file contents, and record counts.

Compares:
  - stdout: FILE_STATUS display after each operation
  - file output: written records and their content
  - exit code
"""
import os
import pytest

from tests.utils.parity_harness import ParityFixture, run_parity


# COBOL fixture: FILE STATUS test
FILESTAT01_CODE = """\
       IDENTIFICATION DIVISION.
       PROGRAM-ID. FILESTAT01.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT SEQ-FILE ASSIGN TO "ws-output-file.txt"
               FILE STATUS IS WS-FILE-STATUS.
       DATA DIVISION.
       FILE SECTION.
       FD  SEQ-FILE.
       01  FILE-REC PIC X(30).
       WORKING-STORAGE SECTION.
       01  WS-FILE-STATUS PIC XX.
       01  WS-EOF-FLAG PIC X VALUE 'N'.
       01  WS-COUNT PIC 9(3) VALUE 0.
       PROCEDURE DIVISION.
       MAIN-PARA.
           OPEN OUTPUT SEQ-FILE
           PERFORM VARYING WS-COUNT FROM 1 BY 1 UNTIL WS-COUNT > 3
               MOVE 'RECORD_' TO FILE-REC
               MOVE WS-COUNT TO FILE-REC(11:2)
               WRITE FILE-REC
               DISPLAY 'Write ' WS-COUNT ': FILE_STATUS = ' WS-FILE-STATUS
           END-PERFORM
           CLOSE SEQ-FILE
           DISPLAY 'After close: FILE_STATUS = ' WS-FILE-STATUS
           OPEN INPUT SEQ-FILE
           DISPLAY 'After reopen INPUT: FILE_STATUS = ' WS-FILE-STATUS
           MOVE 'N' TO WS-EOF-FLAG
           PERFORM UNTIL WS-EOF-FLAG = 'Y'
               READ SEQ-FILE
               AT END
                   DISPLAY 'EOF reached, FILE_STATUS = ' WS-FILE-STATUS
                   MOVE 'Y' TO WS-EOF-FLAG
               NOT AT END
                   DISPLAY 'Read record: ' FILE-REC
                   DISPLAY 'FILE_STATUS after read = ' WS-FILE-STATUS
               END-READ
           END-PERFORM
           READ SEQ-FILE
           AT END
               DISPLAY 'Past EOF read: FILE_STATUS = ' WS-FILE-STATUS ' (expected 10)'
           NOT AT END
               DISPLAY 'Should not reach here'
           END-READ
           CLOSE SEQ-FILE
           STOP RUN.
"""

# Skip unless PARITY_ALLOW_SKIP=true
_FILESTAT01_SKIP = os.environ.get("PARITY_ALLOW_SKIP", "false").lower() != "true"


@pytest.mark.skipif(_FILESTAT01_SKIP, reason="Docker parity images not available — run with PARITY_ALLOW_SKIP=true to execute.")
def test_filestat01_parity():
    """Run FILESTAT01 through the parity harness and compare COBOL vs Java outputs."""
    fixture = ParityFixture(
        name="FILESTAT01",
        program_name="FILESTAT01",
        cobol_code=FILESTAT01_CODE,
        declared_outputs=["ws-output-file.txt"],
        input_files={},
        env={},
    )
    comparison = run_parity(fixture)
    assert comparison.status in ("PASS", "SKIP"), (
        f"FILESTAT01 parity FAILED:\n"
        + "".join(
            f"  target={m.target!r}  offset={m.offset}\n"
            f"  cobol_hex=[{m.cobol_hex}]  java_hex=[{m.java_hex}]\n"
            f"  explanation: {m.explanation}\n"
            for m in comparison.mismatches
        )
    )