       IDENTIFICATION DIVISION.
       PROGRAM-ID. DIVREM.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-GROUP.
          05 A PIC 9(4).
          05 FILLER PIC X VALUE '|'.
          05 B PIC 9(4).
          05 FILLER PIC X VALUE '|'.
          05 Q PIC 9(4).
          05 FILLER PIC X VALUE '|'.
          05 R PIC 9(4).
       PROCEDURE DIVISION.
           INITIALIZE A B Q R.
           MOVE 10 TO A.
           MOVE 3 TO B.
           MOVE 0 TO Q.
           MOVE 0 TO R.
           DIVIDE A BY B GIVING Q REMAINDER R.
           DISPLAY WS-GROUP.
           GOBACK.