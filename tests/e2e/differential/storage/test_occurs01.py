"""OCCURS / OCCURS DEPENDING ON differential test.

COBOL: OCCURS 5 TIMES array with OCCURS DEPENDING ON alternative view.
Compares array iteration, values, and alternative view behavior.

Compares:
  - stdout: array values displayed during loop
  - exit code
"""
import os
import pytest

from tests.utils.parity_harness import ParityFixture, run_parity


# COBOL fixture: OCCURS array test
OCCURS01_CODE = """\
       IDENTIFICATION DIVISION.
       PROGRAM-ID. OCCURS01.
       ENVIRONMENT DIVISION.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-DAYS.
           05 WS-DAY-NUM OCCURS 5 TIMES PIC 9(2).
           05 WS-DAY-NAME OCCURS 5 TIMES PIC X(10).
       01 WS-ODO-TABLE.
           05 WS-ODO-SLOT OCCURS 1 TO 5 TIMES
               DEPENDING ON WS-ODO-COUNT PIC 9(2).
       01 WS-ODO-COUNT PIC 9(1) VALUE 0.
       01 WS-INDEX PIC 9(2) VALUE 1.
       01 WS-SUM PIC 9(3) VALUE 0.
       PROCEDURE DIVISION.
       MAIN-SECTION.
           MOVE 'SUN' TO WS-DAY-NAME(1)
           MOVE 'MON' TO WS-DAY-NAME(2)
           MOVE 'TUE' TO WS-DAY-NAME(3)
           MOVE 'WED' TO WS-DAY-NAME(4)
           MOVE 'THU' TO WS-DAY-NAME(5)
           PERFORM VARYING WS-INDEX FROM 1 BY 1 UNTIL WS-INDEX > 5
               MOVE WS-INDEX TO WS-DAY-NUM(WS-INDEX)
               DISPLAY 'Day ' WS-INDEX ': ' WS-DAY-NAME(WS-INDEX)
                   ' is day number ' WS-DAY-NUM(WS-INDEX)
               ADD WS-DAY-NUM(WS-INDEX) TO WS-SUM
           END-PERFORM
           DISPLAY '---'
           DISPLAY 'Sum of all days: ' WS-SUM
           MOVE 3 TO WS-ODO-COUNT
           PERFORM VARYING WS-INDEX FROM 1 BY 1
               UNTIL WS-INDEX > WS-ODO-COUNT
               MOVE WS-INDEX TO WS-ODO-SLOT(WS-INDEX)
               DISPLAY 'ODO slot ' WS-INDEX ' = ' WS-ODO-SLOT(WS-INDEX)
           END-PERFORM
           DISPLAY 'ODO count: ' WS-ODO-COUNT
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
_OCCURS01_SKIP = (not _is_docker_parity_available()) and _ALLOW_SKIP


@pytest.mark.skipif(_OCCURS01_SKIP, reason="Docker parity images not available on host.")
def test_occurs01_parity():
    """Run OCCURS01 through the parity harness and compare COBOL vs Java outputs."""
    fixture = ParityFixture(
        name="OCCURS01",
        program_name="OCCURS01",
        cobol_code=OCCURS01_CODE,
        declared_outputs=[],
        input_files={},
        env={},
    )
    comparison = run_parity(fixture)
    if comparison.status == "SKIP":
        pytest.skip(comparison.skip_reason)
    assert comparison.status == "PASS", (
        f"OCCURS01 parity FAILED:\n"
        + "".join(
            f"  target={m.target!r}  offset={m.offset}\n"
            f"  cobol_hex=[{m.cobol_hex}]  java_hex=[{m.java_hex}]\n"
            f"  explanation: {m.explanation}\n"
            for m in comparison.mismatches
        )
    )