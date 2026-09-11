       IDENTIFICATION DIVISION.
       PROGRAM-ID. TRUNCAR.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-GROUP.
          05 A PIC 9(4)V999.
          05 FILLER PIC X VALUE '|'.
          05 B PIC 9(4)V99.
       PROCEDURE DIVISION.
           INITIALIZE A B.
           MOVE 1.236 TO A.
           MOVE 0 TO B.
           COMPUTE B = A.
           DISPLAY WS-GROUP.
           GOBACK.