       IDENTIFICATION DIVISION.
       PROGRAM-ID. BCLEGACYX.
      *
      * Legacy syntax fixture for modernization parser testing.
      * Not required by the runtime build.
      *
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-AREA.
          05 WS-CODE PIC X(02).
          05 WS-AMOUNT PIC S9(7)V99 COMP-3.
          05 WS-FLAGS PIC X(10) VALUE SPACES.
          05 WS-FLAG-TABLE REDEFINES WS-FLAGS.
             10 WS-FLAG OCCURS 10 TIMES PIC X.
       01 WS-RESULT PIC X(20).
       01 WS-COUNT PIC 9(4) COMP VALUE ZERO.

       PROCEDURE DIVISION.
       0000-START.
           PERFORM 1000-VALIDATE THRU 1000-EXIT
           GO TO 9000-END.

       1000-VALIDATE.
           EVALUATE TRUE
              WHEN WS-CODE = "01"
                 MOVE "VALID" TO WS-RESULT
              WHEN WS-CODE = "02"
                 MOVE "REVIEW" TO WS-RESULT
              WHEN OTHER
                 MOVE "REJECT" TO WS-RESULT
           END-EVALUATE
           PERFORM VARYING WS-COUNT FROM 1 BY 1
               UNTIL WS-COUNT > 10
               MOVE "Y" TO WS-FLAG(WS-COUNT)
           END-PERFORM.
       1000-EXIT.
           EXIT.

       9000-END.
           GOBACK.
