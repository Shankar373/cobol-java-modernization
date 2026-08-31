IDENTIFICATION DIVISION.
       PROGRAM-ID. FILESTAT01.
       
       ENVIRONMENT DIVISION.
       FILE CONTROL.
           SELECT WS-ASSIGN ASSIGN TO "ws-output-file.txt"
               FILE STATUS IS WS-FILE-STATUS.
       
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-FILE-STATUS PIC 9(2).
       01 WS-RECORD PIC X(30) VALUE SPACES.
       01 WS-COUNT PIC 9(3) VALUE 0.
       01 WS-EOF-FLAG PIC TRUE FALSE VALUE FALSE.
       
       PROCEDURE DIVISION.
       MAIN-SECTION.
           * Open the file for OUTPUT
           OPEN OUTPUT WS-ASSIGN
           
           * Write 3 records
           PERFORM VARYING WS-COUNT FROM 1 BY 1 UNTIL WS-COUNT > 3
               MOVE 'RECORD_' TO WS-RECORD
               MOVE WS-COUNT TO WS-RECORD(11:2)
               WRITE WS-RECORD RECORD
               DISPLAY 'Write ' WS-COUNT ': FILE_STATUS = ' WS-FILE-STATUS
           END-PERFORM
           
           * Close and reopen for INPUT
           CLOSE WS-ASSIGN
           DISPLAY 'After close: FILE_STATUS = ' WS-FILE-STATUS
           
           * Reopen for INPUT
           OPEN INPUT WS-ASSIGN
           DISPLAY 'After reopen INPUT: FILE_STATUS = ' WS-FILE-STATUS
           
           * Read records back
           PERFORM
               READ WS-ASSIGN
               AT END
                   DISPLAY 'EOF reached, FILE_STATUS = ' WS-FILE-STATUS
                   MOVE TRUE TO WS-EOF-FLAG
               NOT AT END
                   DISPLAY 'Read record: ' WS-RECORD
                   DISPLAY 'FILE_STATUS after read = ' WS-FILE-STATUS
           END-PERFORM
           
           * Attempt one more read past EOF
           READ WS-ASSIGN
           AT END
               DISPLAY 'Past EOF read: FILE_STATUS = ' WS-FILE-STATUS ' (expected 10)'
           NOT AT END
               DISPLAY 'Should not reach here'
           END-READ
           
           CLOSE WS-ASSIGN
           STOP RUN.