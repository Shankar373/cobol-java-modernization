       IDENTIFICATION DIVISION.
       PROGRAM-ID. PIC9BASE.
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
           MOVE 15 TO A.
           MOVE 25 TO B.
           MOVE 0 TO C.
           ADD A TO B GIVING C.
           DISPLAY WS-GROUP.
           SUBTRACT A FROM B GIVING C.
           DISPLAY WS-GROUP.
           MULTIPLY A BY B GIVING C.
           DISPLAY WS-GROUP.
           GOBACK.