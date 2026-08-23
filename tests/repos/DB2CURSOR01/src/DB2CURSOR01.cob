       IDENTIFICATION DIVISION.
       PROGRAM-ID. DB2CUR01.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  SQLCA-VARIABLES.
           05  SQLCODE    PIC S9(9) COMP.
           05  SQLSTATE   PIC X(5).
       01  WS-CUSTOMER.
           05  WS-CUST-ID   PIC S9(9) COMP.
           05  WS-CUST-NAME PIC X(20).
       PROCEDURE DIVISION.
           EXEC SQL
               DECLARE C1 CURSOR FOR
               SELECT CUST_ID, CUST_NAME
               FROM CUSTOMER
           END-EXEC.
           EXEC SQL
               OPEN C1
           END-EXEC.
           DISPLAY "OPEN SQLCODE: " SQLCODE
           
           PERFORM UNTIL SQLCODE = 100
               EXEC SQL
                   FETCH C1 INTO :WS-CUST-ID, :WS-CUST-NAME
               END-EXEC
               IF SQLCODE = 0
                   DISPLAY "FETCHED: " WS-CUST-ID " " WS-CUST-NAME
               END-IF
           END-PERFORM.
           
           EXEC SQL
               CLOSE C1
           END-EXEC.
           DISPLAY "CLOSE SQLCODE: " SQLCODE
           GOBACK.
