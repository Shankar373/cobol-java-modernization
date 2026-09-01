       IDENTIFICATION DIVISION.
       PROGRAM-ID. DIVTERM.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-GROUP.
          05 C1 PIC V9(2).
          05 FILLER PIC X VALUE '|'.
          05 C2 PIC 9(2)V9(9).
       PROCEDURE DIVISION.
           INITIALIZE C1 C2.
           MOVE 0 TO C1.
           MOVE 0 TO C2.
           DIVIDE 1 BY 3 GIVING C1.
           DIVIDE 10 BY 3 GIVING C2.
           DISPLAY WS-GROUP.
           GOBACK.