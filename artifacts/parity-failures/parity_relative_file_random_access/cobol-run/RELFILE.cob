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
