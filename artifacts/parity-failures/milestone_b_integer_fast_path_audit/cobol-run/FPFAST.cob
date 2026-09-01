       IDENTIFICATION DIVISION.
           PROGRAM-ID. FPFAST.
           DATA DIVISION.
           WORKING-STORAGE SECTION.
           01 WS-VARS.
              05 WS-INT PIC S9(9).
              05 WS-LONG PIC S9(15).
           PROCEDURE DIVISION.
               MOVE 123456789 TO WS-INT.
               MOVE -987654321012345 TO WS-LONG.
               DISPLAY WS-INT.
               DISPLAY WS-LONG.
               ADD 10 TO WS-INT.
               SUBTRACT 100 FROM WS-LONG.
               DISPLAY WS-INT.
               DISPLAY WS-LONG.
               GOBACK.
