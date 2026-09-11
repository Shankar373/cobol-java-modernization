       IDENTIFICATION DIVISION.
       PROGRAM-ID. TWODISP.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-GROUP.
          05 A PIC 9(4).
          05 FILLER PIC X VALUE '|'.
          05 B PIC 9(4).
       PROCEDURE DIVISION.
           INITIALIZE A B.
           MOVE 1234 TO A.
           MOVE 5678 TO B.
           DISPLAY A B.
           GOBACK.