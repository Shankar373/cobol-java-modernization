       IDENTIFICATION DIVISION.
       PROGRAM-ID. DROPSIGN.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-GROUP.
          05 A PIC 9(3).
       PROCEDURE DIVISION.
           INITIALIZE A.
           MOVE 0 TO A.
           MOVE -5 TO A.
           DISPLAY WS-GROUP.
           GOBACK.