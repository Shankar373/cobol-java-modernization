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
