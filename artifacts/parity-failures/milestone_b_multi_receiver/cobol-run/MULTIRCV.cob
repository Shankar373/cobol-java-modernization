       IDENTIFICATION DIVISION.
       PROGRAM-ID. MULTIRCV.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-GROUP.
          05 A PIC 9(4)V99.
          05 FILLER PIC X VALUE '|'.
          05 B PIC 9(4)V9.
          05 FILLER PIC X VALUE '|'.
          05 C PIC 9(4)V99.
       PROCEDURE DIVISION.
           INITIALIZE A B C.
           MOVE 1.236 TO A.
           MOVE 0 TO B.
           MOVE 0 TO C.
           ADD A TO B C.
           DISPLAY WS-GROUP.
           GOBACK.