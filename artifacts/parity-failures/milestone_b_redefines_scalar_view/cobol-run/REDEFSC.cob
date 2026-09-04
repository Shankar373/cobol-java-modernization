       IDENTIFICATION DIVISION.
       PROGRAM-ID. REDEFSC.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-GROUP.
          05 A PIC X(4).
          05 B REDEFINES A PIC 9(4).
       PROCEDURE DIVISION.
           INITIALIZE A.
           MOVE '1234' TO A.
           DISPLAY WS-GROUP.
           MOVE 5678 TO B.
           DISPLAY WS-GROUP.
           GOBACK.