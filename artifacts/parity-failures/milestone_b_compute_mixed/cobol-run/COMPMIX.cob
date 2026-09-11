       IDENTIFICATION DIVISION.
       PROGRAM-ID. COMPMIX.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-GROUP.
          05 A PIC 9(4)V99.
          05 FILLER PIC X VALUE '|'.
          05 B PIC 9(4)V999.
          05 FILLER PIC X VALUE '|'.
          05 C PIC 9(4)V9.
       PROCEDURE DIVISION.
           INITIALIZE A B C.
           MOVE 12.34 TO A.
           MOVE 5.678 TO B.
           MOVE 0 TO C.
           COMPUTE C = A * B + 1.2.
           DISPLAY WS-GROUP.
           GOBACK.