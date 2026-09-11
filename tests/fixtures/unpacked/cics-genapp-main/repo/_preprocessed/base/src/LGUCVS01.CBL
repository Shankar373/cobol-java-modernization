      ******************************************************************
      *                                                                *
      * (C) Copyright IBM Corp. 2011, 2020                             *
      *                                                                *
      *                    UPDATE Customer                                *
      *                                                                *
      * VSAM KSDS Customer record UPDATE                                  *
      *                                                                *
      ******************************************************************
       IDENTIFICATION DIVISION.
       PROGRAM-ID. LGUCVS01.
       ENVIRONMENT DIVISION.
       CONFIGURATION SECTION.
      *
       DATA DIVISION.
       WORKING-STORAGE SECTION.

       01  WS-RESP                   PIC S9(8) COMP.
       01  WS-RESP2                  PIC S9(8) COMP.
       01  WS-Comm-Len               PIC S9(8) COMP.
       01  WS-STARTCODE              PIC XX Value spaces.
       01  WS-SYSID                  PIC X(4) Value spaces.
       01  WS-Commarea-Len           PIC S9(4) COMP.
       01  WS-Customer-Area          PIC X(1024) value Spaces.
      ******************************
      * Variables for time/date processing
       01  WS-ABSTIME                  PIC S9(8) COMP VALUE +0.
       01  WS-TIME                     PIC X(8)  VALUE SPACES.
       01  WS-DATE                     PIC X(10) VALUE SPACES.
      * Error Message structure
       01  ERROR-MSG.
           03 EM-DATE                  PIC X(8)  VALUE SPACES.
           03 FILLER                   PIC X     VALUE SPACES.
           03 EM-TIME                  PIC X(6)  VALUE SPACES.
           03 FILLER                   PIC X(9)  VALUE ' LGUCVS01'.
           03 EM-VARIABLE.
             05 FILLER                 PIC X(6)  VALUE ' CNUM='.
             05 EM-CUSNUM              PIC X(10)  VALUE SPACES.
             05 FILLER                 PIC X(20)
                                        Value ' Re-write  KSDSCUST '.
             05 FILLER                 PIC X(6)  VALUE ' RESP='.
             05 EM-RESPRC              PIC +9(5) USAGE DISPLAY.
             05 FILLER                 PIC X(7)  VALUE ' RESP2='.
             05 EM-RESP2RC             PIC +9(5) USAGE DISPLAY.

       01  CA-ERROR-MSG.
           03 FILLER                   PIC X(9)  VALUE 'COMMAREA='.
           03 CA-DATA                  PIC X(90) VALUE SPACES.

       01  CUSTOMER-RECORD-SIZE        PIC S9(4) BINARY VALUE 0225.
      *****************************************************************
      *    L I N K A G E     S E C T I O N
      *****************************************************************
       01  EIBRESP                     PIC S9(8) COMP VALUE ZERO.
       01  EIBRESP2                    PIC S9(8) COMP VALUE ZERO.

       LINKAGE SECTION.
       01  DFHCOMMAREA             PIC X(200).
      *----------------------------------------------------------------*
      *****************************************************************
       PROCEDURE DIVISION.
      *---------------------------------------------------------------*
       MAINLINE SECTION.
      *
      *---------------------------------------------------------------*
           Move EIBCALEN To WS-Commarea-Len.
      *---------------------------------------------------------------*
      * [PREPROCESSED: CICS stub]
      * Exec CICS Read File('KSDSCUST')
      * Into(WS-Customer-Area)
      * Length(WS-Commarea-Len)
      * Ridfld(CA-Customer-Num)
      * KeyLength(10)
      * RESP(WS-RESP)
      * Update
      * End-Exec.
           CONTINUE.
           If WS-RESP Not = 0
             Move EIBRESP2 To WS-RESP2
             MOVE '81' TO CA-RETURN-CODE
             PERFORM WRITE-ERROR-MESSAGE
      * [PREPROCESSED: CICS stub]
      * EXEC CICS ABEND ABCODE('LGV1') NODUMP END-EXEC
             CONTINUE
      * [PREPROCESSED: CICS stub]
      * EXEC CICS RETURN END-EXEC
             CONTINUE
           End-If.
      *---------------------------------------------------------------*
      * [PREPROCESSED: CICS stub]
      * Exec CICS ReWrite File('KSDSCUST')
      * From(CA-Customer-Num)
      * Length(CUSTOMER-RECORD-SIZE)
      * RESP(WS-RESP)
      * End-Exec.
           CONTINUE.
           If WS-RESP Not = 0
             Move EIBRESP2 To WS-RESP2
             MOVE '82' TO CA-RETURN-CODE
             PERFORM WRITE-ERROR-MESSAGE
      * [PREPROCESSED: CICS stub]
      * EXEC CICS ABEND ABCODE('LGV2') NODUMP END-EXEC
             CONTINUE
      * [PREPROCESSED: CICS stub]
      * EXEC CICS RETURN END-EXEC
             CONTINUE
           End-If.
      *---------------------------------------------------------------*

       A-EXIT.
           EXIT.
           GOBACK.
      *---------------------------------------------------------------*
       WRITE-ERROR-MESSAGE.
      * [PREPROCESSED: CICS stub]
      * EXEC CICS ASKTIME ABSTIME(WS-ABSTIME)
      * END-EXEC
           CONTINUE
      * [PREPROCESSED: CICS stub]
      * EXEC CICS FORMATTIME ABSTIME(WS-ABSTIME)
      * MMDDYYYY(WS-DATE)
      * TIME(WS-TIME)
      * END-EXEC
           CONTINUE
      *
           MOVE WS-DATE TO EM-DATE
           MOVE WS-TIME TO EM-TIME
           Move CA-Customer-Num To EM-Cusnum
           Move WS-RESP         To EM-RespRC
           Move WS-RESP2        To EM-Resp2RC
      * [PREPROCESSED: CICS stub]
      * EXEC CICS LINK PROGRAM('LGSTSQ')
      * COMMAREA(ERROR-MSG)
      * LENGTH(LENGTH OF ERROR-MSG)
      * END-EXEC.
           CONTINUE.
           IF EIBCALEN > 0 THEN
             IF EIBCALEN < 91 THEN
               MOVE DFHCOMMAREA(1:EIBCALEN) TO CA-DATA
      * [PREPROCESSED: CICS stub]
      * EXEC CICS LINK PROGRAM('LGSTSQ')
      * COMMAREA(CA-ERROR-MSG)
      * LENGTH(Length Of CA-ERROR-MSG)
      * END-EXEC
               CONTINUE
             ELSE
               MOVE DFHCOMMAREA(1:90) TO CA-DATA
      * [PREPROCESSED: CICS stub]
      * EXEC CICS LINK PROGRAM('LGSTSQ')
      * COMMAREA(CA-ERROR-MSG)
      * LENGTH(Length Of CA-ERROR-MSG)
      * END-EXEC
               CONTINUE
             END-IF
           END-IF.
           EXIT.
