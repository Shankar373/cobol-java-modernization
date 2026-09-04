       IDENTIFICATION DIVISION.
       PROGRAM-ID. DIVSCALE.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-GROUP.
          05 A PIC 9(4)V99.
          05 FILLER PIC X VALUE '|'.
          05 B PIC 9(4)V99.
          05 FILLER PIC X VALUE '|'.
          05 C PIC 9(4)V99.
       PROCEDURE DIVISION.
           INITIALIZE A B C.
           MOVE 10.00 TO A.
           MOVE 3.00 TO B.
           MOVE 0 TO C.
           DIVIDE A BY B GIVING C.
           DISPLAY WS-GROUP.
           GOBACK.