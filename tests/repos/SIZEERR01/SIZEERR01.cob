IDENTIFICATION DIVISION.
       PROGRAM-ID. SIZEERR01.
       
       ENVIRONMENT DIVISION.
       CONFIGURATION SECTION.
       SPECIAL-NAMES.
           .                                                        
       
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-SMALL PIC 9(2) VALUE 0.
       01 WS-LARGE PIC 99 VALUE 0.
       01 WS-OVERFLOW FLAG PIC TRUE FALSE.
       01 WS-DISPLAY-NUM PIC 9(2).
       
       PROCEDURE DIVISION.
       MAIN-SECTION.
           * Test 1: ADD that overflows ON SIZE ERROR
           DISPLAY 'Before ADD: WS-SMALL = ' WS-SMALL
           ADD 1000 TO WS-SMALL ON SIZE ERROR
               MOVE 'Y' TO WS-OVERFLOW
               DISPLAY 'ON SIZE ERROR triggered'
           ELSE
               DISPLAY 'No overflow occurred'
           END-ADD
           
           DISPLAY 'After ADD: WS-SMALL = ' WS-SMALL
           DISPLAY 'WS-OVERFLOW = ' WS-OVERFLOW
           
           * Test 2: SUBTRACT that underflows
           MOVE 0 TO WS-OVERFLOW
           SUBTRACT 100 FROM WS-SMALL ON SIZE ERROR
               MOVE 'Y' TO WS-OVERFLOW
               DISPLAY 'ON SIZE ERROR underflow triggered'
           ELSE
               DISPLAY 'No underflow occurred'
           END-SUBTRACT
           
           DISPLAY 'After SUBTRACT: WS-SMALL = ' WS-SMALL
           DISPLAY 'WS-OVERFLOW = ' WS-OVERFLOW
           
           STOP RUN.