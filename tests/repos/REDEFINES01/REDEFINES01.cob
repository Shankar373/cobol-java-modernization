IDENTIFICATION DIVISION.
       PROGRAM-ID. REDEFINES01.
       
       ENVIRONMENT DIVISION.
       CONFIGURATION SECTION.
       SPECIAL-NAMES.
           .                                                        
       
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-BUF-X PIC X(10).
       01 WS-BUF-9 REDEFINES WS-BUF-X PIC 9(10).
       
       01 WS-DISPLAY PIC X(20).
       01 WS-FILE-OUT PIC X(10) VALUE SPACES.
       
       PROCEDURE DIVISION.
       MAIN-SECTION.
           * View 1: Write alphanumeric value via WS-BUF-X
           MOVE 'HELLO1234' TO WS-BUF-X
           
           * View 2: Read via WS-BUF-9 (redefines)
           DISPLAY 'WS-BUF-9 as numeric: ' WS-BUF-9
           
           * View 2 alternative: numeric interpret of the same memory
           MOVE WS-BUF-9 TO WS-DISPLAY
           DISPLAY 'WS-DISPLAY (buf redefines view): ' WS-DISPLAY
           
           * Verify the redefinition: WS-BUF-9 should contain the same bytes as WS-BUF-X
           MOVE '9999999999' TO WS-BUF-9
           DISPLAY 'After MOVE 9999999999 to WS-BUF-9:'
           DISPLAY 'WS-BUF-X: ' WS-BUF-X
           DISPLAY 'WS-BUF-9: ' WS-BUF-9
           
           * Write to file showing the redefined view
           MOVE WS-BUF-X TO WS-FILE-OUT
           OPEN OUTPUT WS-OUTPUT-FILE
           WRITE WS-FILE-OUT RECORD
           CLOSE WS-OUTPUT-FILE
           
           STOP RUN.