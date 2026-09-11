       IDENTIFICATION DIVISION.
       PROGRAM-ID. NEGSUB.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-GROUP.
          05 A PIC S9(4) SIGN IS TRAILING .
          05 FILLER PIC X VALUE '|'.
          05 X PIC S9(4) SIGN IS TRAILING .
       PROCEDURE DIVISION.
           INITIALIZE A X.
           MOVE 10 TO A.
           MOVE 0 TO X.
           COMPUTE X = A - 1.
           DISPLAY WS-GROUP.
           COMPUTE X = A - -1.
           DISPLAY WS-GROUP.
           SUBTRACT 1 FROM A GIVING X.
           DISPLAY WS-GROUP.
           GOBACK.