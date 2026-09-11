       IDENTIFICATION DIVISION.
       PROGRAM-ID. FILESTAT01.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT SEQ-FILE ASSIGN TO "outfile.txt"
               FILE STATUS IS WS-FILE-STATUS.
       DATA DIVISION.
       FILE SECTION.
       FD  SEQ-FILE.
       01  FILE-REC PIC X(30).
       WORKING-STORAGE SECTION.
       01  WS-FILE-STATUS PIC XX.
       01  WS-EOF-FLAG PIC X VALUE 'N'.
       01  WS-COUNT PIC 9(3) VALUE 0.
       01  WS-R1 PIC X(30) VALUE 'RECORD_01                     '.
       01  WS-R2 PIC X(30) VALUE 'RECORD_02                     '.
       01  WS-R3 PIC X(30) VALUE 'RECORD_03                     '.
       PROCEDURE DIVISION.
       MAIN-PARA.
           OPEN OUTPUT SEQ-FILE
           PERFORM VARYING WS-COUNT FROM 1 BY 1 UNTIL WS-COUNT > 3
               IF WS-COUNT = 1
                   MOVE WS-R1 TO FILE-REC
               END-IF
               IF WS-COUNT = 2
                   MOVE WS-R2 TO FILE-REC
               END-IF
               IF WS-COUNT = 3
                   MOVE WS-R3 TO FILE-REC
               END-IF
               WRITE FILE-REC
               DISPLAY 'Write: ' WS-FILE-STATUS
           END-PERFORM
           CLOSE SEQ-FILE
           DISPLAY 'Close: ' WS-FILE-STATUS
           OPEN INPUT SEQ-FILE
           DISPLAY 'Reopen: ' WS-FILE-STATUS
           MOVE 'N' TO WS-EOF-FLAG
           PERFORM UNTIL WS-EOF-FLAG = 'Y'
               READ SEQ-FILE
               AT END
                   DISPLAY 'EOF: ' WS-FILE-STATUS
                   MOVE 'Y' TO WS-EOF-FLAG
               NOT AT END
                   DISPLAY 'Rec: ' FILE-REC
                   DISPLAY 'FS: ' WS-FILE-STATUS
               END-READ
           END-PERFORM
           READ SEQ-FILE
           AT END
               DISPLAY 'Past EOF: ' WS-FILE-STATUS
           NOT AT END
               DISPLAY 'Error: should not read'
           END-READ
           CLOSE SEQ-FILE
           STOP RUN.
