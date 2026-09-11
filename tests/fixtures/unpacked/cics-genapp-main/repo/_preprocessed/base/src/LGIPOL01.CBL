      ******************************************************************
      *                                                                *
      * (C) Copyright IBM Corp. 2011, 2020                             *
      *                                                                *
      *                    Inquire Policy                              *
      *                                                                *
      *  Business logic for policy inquire                             *
      *   To obtain full details of an individual policy:              *
      *     Endowment, House or Motor                                  *
      *                                                                *
      ******************************************************************
       IDENTIFICATION DIVISION.
       PROGRAM-ID. LGIPOL01.
       ENVIRONMENT DIVISION.
       CONFIGURATION SECTION.
      *
       DATA DIVISION.

       WORKING-STORAGE SECTION.
      *----------------------------------------------------------------*
      * Common defintions                                              *
      *----------------------------------------------------------------*
      * Run time (debug) infomation for this invocation
        01  WS-HEADER.
           03 WS-EYECATCHER            PIC X(16)
                                        VALUE 'LGIPOL01------WS'.
           03 WS-TRANSID               PIC X(4).
           03 WS-TERMID                PIC X(4).
           03 WS-TASKNUM               PIC 9(7).
           03 WS-FILLER                PIC X.
           03 WS-ADDR-DFHCOMMAREA      USAGE is POINTER.
           03 WS-CALEN                 PIC S9(4) COMP.
      * Variables for time/date processing
       01  ABS-TIME                    PIC S9(8) COMP VALUE +0.
       01  TIME1                       PIC X(8)  VALUE SPACES.
       01  DATE1                       PIC X(10) VALUE SPACES.
      * Error Message structure
       01  ERROR-MSG.
           03 EM-DATE                  PIC X(8)  VALUE SPACES.
           03 FILLER                   PIC X     VALUE SPACES.
           03 EM-TIME                  PIC X(6)  VALUE SPACES.
           03 FILLER                   PIC X(9)  VALUE ' LGIPOL01'.
           03 EM-VARIABLE              PIC X(21) VALUE SPACES.

       01  CA-ERROR-MSG.
           03 FILLER                   PIC X(9)  VALUE 'COMMAREA='.
           03 CA-DATA                  PIC X(90) VALUE SPACES.
      *----------------------------------------------------------------*

       01 LGIPDB01                     PIC x(8) Value 'LGIPDB01'.
      *----------------------------------------------------------------*
             COPY LGPOLICY.
      *----------------------------------------------------------------*
      ******************************************************************
      *    L I N K A G E     S E C T I O N
      ******************************************************************
       LINKAGE SECTION.
       01  DFHCOMMAREA             PIC X(200).
      ******************************************************************
      *    P R O C E D U R E S
      ******************************************************************
       PROCEDURE DIVISION.
      *----------------------------------------------------------------*
       MAINLINE SECTION.
      *
           INITIALIZE WS-HEADER.
      *
           MOVE EIBTRNID TO WS-TRANSID.
           MOVE EIBTRMID TO WS-TERMID.
           MOVE EIBTASKN TO WS-TASKNUM.
      *
      * If NO commarea received issue an ABEND
           IF EIBCALEN IS EQUAL TO ZERO
               MOVE ' NO COMMAREA RECEIVED' TO EM-VARIABLE
               PERFORM WRITE-ERROR-MESSAGE
      * [PREPROCESSED: CICS stub]
      * EXEC CICS ABEND ABCODE('LGCA') NODUMP END-EXEC
               CONTINUE
           END-IF
      * initialize commarea return code to zero
           MOVE '00' TO CA-RETURN-CODE
           MOVE EIBCALEN TO WS-CALEN.
           SET WS-ADDR-DFHCOMMAREA TO ADDRESS OF DFHCOMMAREA.
      *

      * [PREPROCESSED: CICS stub]
      * EXEC CICS LINK Program(LGIPDB01)
      * Commarea(DFHCOMMAREA)
      * Length(32500)
      * END-EXEC.
           CONTINUE.

      * [PREPROCESSED: CICS stub]
      * EXEC CICS RETURN END-EXEC.
           CONTINUE.

       MAINLINE-EXIT.
           EXIT.
      *----------------------------------------------------------------*
      *================================================================*
      * Procedure to write error message to Queues                     *
      *   message will include Date, Time, Program Name, Customer      *
      *   Number, Policy Number and SQLCODE.                           *
      *================================================================*
       WRITE-ERROR-MESSAGE.
      * Save SQLCODE in message
      * Obtain and format current time and date
      * [PREPROCESSED: CICS stub]
      * EXEC CICS ASKTIME ABSTIME(ABS-TIME)
      * END-EXEC
           CONTINUE
      * [PREPROCESSED: CICS stub]
      * EXEC CICS FORMATTIME ABSTIME(ABS-TIME)
      * MMDDYYYY(DATE1)
      * TIME(TIME1)
      * END-EXEC
           CONTINUE
           MOVE DATE1 TO EM-DATE
           MOVE TIME1 TO EM-TIME
      * Write output message to TDQ
      * [PREPROCESSED: CICS stub]
      * EXEC CICS LINK PROGRAM('LGSTSQ')
      * COMMAREA(ERROR-MSG)
      * LENGTH(LENGTH OF ERROR-MSG)
      * END-EXEC.
           CONTINUE.
      * Write 90 bytes or as much as we have of commarea to TDQ
           IF EIBCALEN > 0 THEN
             IF EIBCALEN < 91 THEN
               MOVE DFHCOMMAREA(1:EIBCALEN) TO CA-DATA
      * [PREPROCESSED: CICS stub]
      * EXEC CICS LINK PROGRAM('LGSTSQ')
      * COMMAREA(CA-ERROR-MSG)
      * LENGTH(LENGTH OF CA-ERROR-MSG)
      * END-EXEC
               CONTINUE
             ELSE
               MOVE DFHCOMMAREA(1:90) TO CA-DATA
      * [PREPROCESSED: CICS stub]
      * EXEC CICS LINK PROGRAM('LGSTSQ')
      * COMMAREA(CA-ERROR-MSG)
      * LENGTH(LENGTH OF CA-ERROR-MSG)
      * END-EXEC
               CONTINUE
             END-IF
           END-IF.
           EXIT.
