       IDENTIFICATION DIVISION.
       PROGRAM-ID. BCMAIN01.

       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-RETURN-CODE PIC 9(02) VALUE ZERO.

       PROCEDURE DIVISION.
       MAIN-SECTION.
           DISPLAY "=========================================="
           DISPLAY " BANKCORE ENTERPRISE LEGACY BATCH"
           DISPLAY " STARTING NIGHTLY PROCESS"
           DISPLAY "=========================================="

           CALL "BCLOAD01" RETURNING WS-RETURN-CODE
           IF WS-RETURN-CODE NOT = 0
               DISPLAY "MASTER LOAD FAILED"
               MOVE 12 TO RETURN-CODE
               GOBACK
           END-IF

           CALL "BCPROC01" RETURNING WS-RETURN-CODE
           IF WS-RETURN-CODE NOT = 0
               DISPLAY "TRANSACTION PROCESSING FAILED"
               MOVE 12 TO RETURN-CODE
               GOBACK
           END-IF

           CALL "BCREPT01" RETURNING WS-RETURN-CODE
           IF WS-RETURN-CODE NOT = 0
               DISPLAY "REPORT GENERATION FAILED"
               MOVE 12 TO RETURN-CODE
               GOBACK
           END-IF

           DISPLAY "=========================================="
           DISPLAY " BANKCORE NIGHTLY PROCESS COMPLETED"
           DISPLAY "=========================================="
           MOVE 0 TO RETURN-CODE
           GOBACK.
