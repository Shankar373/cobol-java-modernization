"""ON SIZE ERROR / numeric overflow differential test.

COBOL: ADD/SUBTRACT with ON SIZE ERROR trigger verification.
Compares whether overflow is detected and final numeric values.

Compares:
  - stdout: ON SIZE ERROR triggered messages
  - exit code
  - final numeric values
"""
import os
import pytest

from tests.utils.parity_harness import ParityFixture, run_parity


# COBOL fixture: ON SIZE ERROR test
SIZEERR01_CODE = """\
       IDENTIFICATION DIVISION.
       PROGRAM-ID. SIZEERR01.
       ENVIRONMENT DIVISION.
       CONFIGURATION SECTION.
       SPECIAL-NAMES.
           .
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-SMALL PIC 9(2) VALUE 0.
       01 WS-OVERFLOW PIC X VALUE 'N'.
       PROCEDURE DIVISION.
       MAIN-PARA.
           DISPLAY 'Before ADD: WS-SMALL = ' WS-SMALL
           ADD 1000 TO WS-SMALL ON SIZE ERROR
               MOVE 'Y' TO WS-OVERFLOW
               DISPLAY 'ON SIZE ERROR triggered'
           END-ADD
           DISPLAY 'After ADD: WS-SMALL = ' WS-SMALL
           DISPLAY 'WS-OVERFLOW = ' WS-OVERFLOW
           MOVE 'N' TO WS-OVERFLOW
           SUBTRACT 100 FROM WS-SMALL ON SIZE ERROR
               MOVE 'Y' TO WS-OVERFLOW
               DISPLAY 'ON SIZE ERROR underflow triggered'
           END-SUBTRACT
           DISPLAY 'After SUBTRACT: WS-SMALL = ' WS-SMALL
           DISPLAY 'WS-OVERFLOW = ' WS-OVERFLOW
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
_SIZEERR01_SKIP = (not _is_docker_parity_available()) and _ALLOW_SKIP


@pytest.mark.skipif(_SIZEERR01_SKIP, reason="Docker parity images not available on host.")
def test_sizeerr01_parity():
    """Run SIZEERR01 through the parity harness and compare COBOL vs Java outputs."""
    fixture = ParityFixture(
        name="SIZEERR01",
        program_name="SIZEERR01",
        cobol_code=SIZEERR01_CODE,
        declared_outputs=[],
        input_files={},
        env={},
    )
    comparison = run_parity(fixture)
    if comparison.status == "SKIP":
        pytest.skip(comparison.skip_reason)
    assert comparison.status == "PASS", (
        f"SIZEERR01 parity FAILED:\n"
        + "".join(
            f"  target={m.target!r}  offset={m.offset}\n"
            f"  cobol_hex=[{m.cobol_hex}]  java_hex=[{m.java_hex}]\n"
            f"  explanation: {m.explanation}\n"
            for m in comparison.mismatches
        )
    )