       IDENTIFICATION DIVISION.
       PROGRAM-ID. DIVZEROWO.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-GROUP.
          05 A PIC 9(4).
          05 FILLER PIC X VALUE '|'.
          05 B PIC 9(4).
          05 FILLER PIC X VALUE '|'.
          05 C PIC 9(4).
       PROCEDURE DIVISION.
           INITIALIZE A B C.
           MOVE 10 TO A.
           MOVE 0 TO B.
           MOVE 5 TO C.
           DIVIDE A BY B GIVING C.
           DISPLAY WS-GROUP.
           GOBACK.