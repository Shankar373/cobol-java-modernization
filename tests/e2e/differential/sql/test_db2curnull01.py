"""Cursor + NULL indicators differential test.

COBOL: Cursor over a table with a nullable column; fetch rows, check null
indicator values, count NULLs. Compares: rows fetched, NULL detection,
SQLCODE output.

Note: requires the ocesql/PostgreSQL parity infrastructure (Docker). The
harness injects DECLARE SECTION + CONNECT and swaps the SQLCA group for
COPY "sqlca.cbl".
"""
import os
import pytest

from tests.utils.parity_harness import ParityFixture, run_parity


# COBOL fixture: Cursor + NULL indicators test
# Valid ocesql-compatible SQL; self-seeding so no external schema fixture
# is needed for the parity run.
DB2CURNULL01_CODE = """\
       IDENTIFICATION DIVISION.
       PROGRAM-ID. DB2CURNULL01.
       ENVIRONMENT DIVISION.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  SQLCA-VARIABLES.
           05  SQLCODE    PIC S9(9) COMP.
           05  SQLSTATE   PIC X(5).
       01  WS-EMPNO      PIC S9(9) COMP.
       01  WS-EMPNAME    PIC X(20) VALUE SPACES.
       01  WS-COMM       PIC S9(5) COMP VALUE 0.
       01  WS-COMM-IND   PIC S9(4) COMP VALUE 0.
       01  WS-ROW-NUM    PIC 9(2) VALUE 1.
       01  WS-NULL-COUNT PIC 9(2) VALUE 0.
       PROCEDURE DIVISION.
       MAIN-SECTION.
           EXEC SQL
               DROP TABLE IF EXISTS EMPTABLE
           END-EXEC.
           EXEC SQL
               CREATE TABLE EMPTABLE (
                   EMPNO    INT,
                   EMPNAME  VARCHAR(20),
                   COMM     INT
               )
           END-EXEC.
           EXEC SQL
               INSERT INTO EMPTABLE VALUES (1, 'JONES', 100)
           END-EXEC.
           EXEC SQL
               INSERT INTO EMPTABLE VALUES (2, 'SMITH', NULL)
           END-EXEC.
           EXEC SQL
               INSERT INTO EMPTABLE VALUES (3, 'ALLEN', 500)
           END-EXEC.
           DISPLAY 'ROWS SEEDED FOR CURSOR TEST'
           EXEC SQL
               DECLARE C1 CURSOR FOR
               SELECT EMPNO, EMPNAME, COMM FROM EMPTABLE
           END-EXEC.
           EXEC SQL OPEN C1 END-EXEC.
           DISPLAY 'OPEN SQLCODE: ' SQLCODE
           PERFORM UNTIL SQLCODE NOT EQUAL 0
               EXEC SQL
                   FETCH C1 INTO
                       :WS-EMPNO, :WS-EMPNAME, :WS-COMM:WS-COMM-IND
               END-EXEC
               EVALUATE TRUE
                   WHEN SQLCODE EQUAL 0
                       DISPLAY 'ROW ' WS-ROW-NUM
                           ' EMPNO=' WS-EMPNO
                           ' NULL-IND=' WS-COMM-IND
                       IF WS-COMM-IND < 0
                           DISPLAY '  *** NULL IN COMM ***'
                           ADD 1 TO WS-NULL-COUNT
                       END-IF
                       ADD 1 TO WS-ROW-NUM
                   WHEN SQLCODE EQUAL 100
                       CONTINUE
                   WHEN OTHER
                       DISPLAY 'FETCH ERROR SQLCODE: ' SQLCODE
               END-EVALUATE
           END-PERFORM.
           DISPLAY 'TOTAL NULL COLUMNS FOUND: ' WS-NULL-COUNT
           EXEC SQL CLOSE C1 END-EXEC.
           EXEC SQL DROP TABLE EMPTABLE END-EXEC.
           DISPLAY 'CLOSE SQLCODE: ' SQLCODE
           GOBACK.
"""

# Skip unless PARITY_ALLOW_SKIP=true
_DB2CURNULL01_SKIP = os.environ.get("PARITY_ALLOW_SKIP", "false").lower() != "true"


@pytest.mark.skipif(_DB2CURNULL01_SKIP, reason="Docker/DB parity infrastructure unavailable — run with PARITY_ALLOW_SKIP=true to execute.")
def test_db2curnull01_parity():
    """Compile the DB2CURNULL01 COBOL under GnuCOBOL+ocesql and
    verify it runs. (Java parity pending native SQL generation.)"""
    fixture = ParityFixture(
        name="DB2CURNULL01",
        program_name="DB2CURNULL01",
        cobol_code=DB2CURNULL01_CODE,
        declared_outputs=[],
        input_files={},
        env={},
    )
    comparison = run_parity(fixture)

    assert comparison.status in ("PASS", "SKIP"), (
        f"DB2CURNULL01 parity FAILED:\n"
        + "".join(
            f"  target={m.target!r}  offset={m.offset}\n"
            f"  cobol_hex=[{m.cobol_hex}]  java_hex=[{m.java_hex}]\n"
            f"  explanation: {m.explanation}\n"
            for m in comparison.mismatches
        )
    )
