       IDENTIFICATION DIVISION.
       PROGRAM-ID. SIGNEDAR.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-GROUP.
          05 A PIC S9(4) SIGN IS TRAILING .
          05 FILLER PIC X VALUE '|'.
          05 B PIC S9(4) SIGN IS TRAILING .
          05 FILLER PIC X VALUE '|'.
          05 C PIC S9(4) SIGN IS TRAILING .
       PROCEDURE DIVISION.
           INITIALIZE A B C.
           MOVE -15 TO A.
           MOVE 25 TO B.
           MOVE 0 TO C.
           ADD A TO B GIVING C.
           DISPLAY WS-GROUP.
           SUBTRACT B FROM A GIVING C.
           DISPLAY WS-GROUP.
           MULTIPLY A BY B GIVING C.
           DISPLAY WS-GROUP.
           GOBACK.