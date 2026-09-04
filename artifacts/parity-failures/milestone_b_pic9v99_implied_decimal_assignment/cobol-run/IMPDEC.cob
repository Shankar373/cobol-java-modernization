       IDENTIFICATION DIVISION.
       PROGRAM-ID. IMPDEC.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-GROUP.
          05 A PIC 9(4)V99.
          05 FILLER PIC X VALUE '|'.
          05 B PIC 9(4)V99.
       PROCEDURE DIVISION.
           INITIALIZE A B.
           MOVE 12.34 TO A.
           MOVE 0 TO B.
           MOVE 45.67 TO B.
           DISPLAY WS-GROUP.
           GOBACK.