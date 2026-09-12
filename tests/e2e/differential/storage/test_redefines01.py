"""REDEFINES overlap differential test.

COBOL: REDEFINES overlap — writes via one view, reads via the other,
verifies the overlap of memory and correct display of redefined values.

Compares:
  - stdout: displayed field values from both views
  - exit code
  - file outputs (if any)
"""
import os
import pytest

from tests.utils.parity_harness import ParityFixture, run_parity


# COBOL fixture sourced from tests/repos/REDEFINES01/REDEFINES01.cob
REDEFINES01_CODE = """\
       IDENTIFICATION DIVISION.
       PROGRAM-ID. REDEFINES01.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT OUT-FILE ASSIGN TO "redefines-output.txt"
               FILE STATUS IS WS-FS.
       DATA DIVISION.
       FILE SECTION.
       FD  OUT-FILE.
       01  OUT-REC PIC X(10).
       WORKING-STORAGE SECTION.
       01  WS-FS PIC XX.
       01  WS-BUF-X PIC X(10).
       01  WS-BUF-9 REDEFINES WS-BUF-X PIC 9(10).
       01  WS-DISPLAY PIC X(20).
       PROCEDURE DIVISION.
       MAIN-PARA.
           MOVE '1234567890' TO WS-BUF-X
           DISPLAY 'WS-BUF-9: ' WS-BUF-9
           MOVE WS-BUF-9 TO WS-DISPLAY
           DISPLAY 'WS-DISPLAY: ' WS-DISPLAY
           MOVE '9999999999' TO WS-BUF-9
           DISPLAY 'After MOVE:'
           DISPLAY 'WS-BUF-X: ' WS-BUF-X
           DISPLAY 'WS-BUF-9: ' WS-BUF-9
           MOVE WS-BUF-X TO OUT-REC
           OPEN OUTPUT OUT-FILE
           WRITE OUT-REC
           CLOSE OUT-FILE
           STOP RUN.
"""

def _is_docker_parity_available() -> bool:
    try:
        from tests.utils.parity_harness import (
            check_docker_available,
            check_docker_image_cached,
            PARITY_GNUCOBOL_IMAGE,
            PARITY_JDK_IMAGE,
        )
        return (
            check_docker_available()
            and check_docker_image_cached(PARITY_GNUCOBOL_IMAGE)
            and check_docker_image_cached(PARITY_JDK_IMAGE)
        )
    except Exception:
        return False


_ALLOW_SKIP = os.environ.get("PARITY_ALLOW_SKIP", "true").lower() == "true"
_REDEFINES01_SKIP = (not _is_docker_parity_available()) and _ALLOW_SKIP


@pytest.mark.skipif(_REDEFINES01_SKIP, reason="Docker parity images not available on host.")
def test_redefines01_parity():
    """Run REDEFINES01 through the parity harness and compare COBOL vs Java outputs."""
    fixture = ParityFixture(
        name="REDEFINES01",
        program_name="REDEFINES01",
        cobol_code=REDEFINES01_CODE,
        declared_outputs=["redefines-output.txt"],
        input_files={},
        env={},
    )
    comparison = run_parity(fixture)
    if comparison.status == "SKIP":
        pytest.skip(comparison.skip_reason)
    assert comparison.status == "PASS", (
        f"REDEFINES01 parity FAILED:\n"
        + "".join(
            f"  target={m.target!r}  offset={m.offset}\n"
            f"  cobol_hex=[{m.cobol_hex}]  java_hex=[{m.java_hex}]\n"
            f"  explanation: {m.explanation}\n"
            for m in comparison.mismatches
        )
    )