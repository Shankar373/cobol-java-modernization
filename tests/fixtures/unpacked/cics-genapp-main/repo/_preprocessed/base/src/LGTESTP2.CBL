      ******************************************************************
      *                                                                *
      * (C) Copyright IBM Corp. 2011, 2020                             *
      *                                                                *
      *                Endowment Policy Menu                           *
      *                                                                *
      * Menu for Endowment Policy Transactions                         *
      *                                                                *
      ******************************************************************
       IDENTIFICATION DIVISION.
       PROGRAM-ID. LGTESTP2.
       ENVIRONMENT DIVISION.
       CONFIGURATION SECTION.
      *
       DATA DIVISION.
       WORKING-STORAGE SECTION.

       77 MSGEND                       PIC X(24) VALUE
                                        'Transaction ended      '.

       COPY SSMAP.
       01 COMM-AREA.
       COPY LGCMAREA.
      *----------------------------------------------------------------*
      *****************************************************************
       PROCEDURE DIVISION.
      *---------------------------------------------------------------*
       MAINLINE SECTION.

           IF EIBCALEN > 0
              GO TO A-GAIN.

           Initialize SSMAPP2I.
           Initialize SSMAPP2O.
           Initialize COMM-AREA.
           MOVE '0000000000'   To ENP2CNOO.
           MOVE '0000000000'   To ENP2PNOO.
      * Display Main Menu
      * [PREPROCESSED: CICS stub]
      * EXEC CICS SEND MAP ('SSMAPP2')
      * MAPSET ('SSMAP')
      * ERASE
      * END-EXEC.
           CONTINUE.

       A-GAIN.

      * [PREPROCESSED: CICS stub]
      * EXEC CICS HANDLE AID
      * CLEAR(CLEARIT)
      * PF3(ENDIT) END-EXEC.
           CONTINUE.
      * [PREPROCESSED: CICS stub]
      * EXEC CICS HANDLE CONDITION
      * MAPFAIL(ENDIT)
      * END-EXEC.
           CONTINUE.

      * [PREPROCESSED: CICS stub]
      * EXEC CICS RECEIVE MAP('SSMAPP2')
      * INTO(SSMAPP2I)
      * MAPSET('SSMAP') END-EXEC.
           CONTINUE.


           EVALUATE ENP2OPTO

             WHEN '1'
                 Move '01IEND'   To CA-REQUEST-ID
                 Move ENP2CNOO   To CA-CUSTOMER-NUM
                 Move ENP2PNOO   To CA-POLICY-NUM
      * [PREPROCESSED: CICS stub]
      * EXEC CICS LINK PROGRAM('LGIPOL01')
      * COMMAREA(COMM-AREA)
      * LENGTH(32500)
      * END-EXEC
                 CONTINUE
                 IF CA-RETURN-CODE > 0
                   GO TO NO-DATA
                 END-IF

                 Move CA-ISSUE-DATE     To  ENP2IDAI
                 Move CA-EXPIRY-DATE    To  ENP2EDAI
                 Move CA-E-FUND-NAME    To  ENP2FNMI
                 Move CA-E-TERM         To  ENP2TERI
                 Move CA-E-SUM-ASSURED  To  ENP2SUMI
                 Move CA-E-LIFE-ASSURED To  ENP2LIFI
                 Move CA-E-WITH-PROFITS To  ENP2WPRI
                 Move CA-E-MANAGED-FUND To  ENP2MANI
                 Move CA-E-EQUITIES     To  ENP2EQUI
      * [PREPROCESSED: CICS stub]
      * EXEC CICS SEND MAP ('SSMAPP2')
      * FROM(SSMAPP2O)
      * MAPSET ('SSMAP')
      * END-EXEC
                 CONTINUE
                 GO TO ENDIT-STARTIT

             WHEN '2'
                 Move '01AEND'          To CA-REQUEST-ID
                 Move ENP2CNOI          To CA-CUSTOMER-NUM
                 Move 0                 To CA-PAYMENT
                 Move 0                 To CA-BROKERID
                 Move '        '        To CA-BROKERSREF
                 Move ENP2IDAI          To CA-ISSUE-DATE
                 Move ENP2EDAI          To CA-EXPIRY-DATE
                 Move ENP2FNMI          To CA-E-FUND-NAME
                 Move ENP2TERI          To CA-E-TERM
                 Move ENP2SUMI          To CA-E-SUM-ASSURED
                 Move ENP2LIFI          To CA-E-LIFE-ASSURED
                 Move ENP2WPRI          To CA-E-WITH-PROFITS
                 Move ENP2MANI          To CA-E-MANAGED-FUND
                 Move ENP2EQUI          To CA-E-EQUITIES
      * [PREPROCESSED: CICS stub]
      * EXEC CICS LINK PROGRAM('LGAPOL01')
      * COMMAREA(COMM-AREA)
      * LENGTH(32500)
      * END-EXEC
                 CONTINUE
                 IF CA-RETURN-CODE > 0
      * [PREPROCESSED: CICS stub]
      * Exec CICS Syncpoint Rollback End-Exec
                   CONTINUE
                   GO TO NO-ADD
                 END-IF
                 Move CA-CUSTOMER-NUM To ENP2CNOI
                 Move CA-POLICY-NUM   To ENP2PNOI
                 Move CA-E-FUND-NAME  To ENP2FNMI
                 Move ' '             To ENP2OPTI
                 Move 'New Life Policy Inserted'
                   To  ERP2FLDO
      * [PREPROCESSED: CICS stub]
      * EXEC CICS SEND MAP ('SSMAPP2')
      * FROM(SSMAPP2O)
      * MAPSET ('SSMAP')
      * END-EXEC
                 CONTINUE
                 GO TO ENDIT-STARTIT

             WHEN '3'
                 Move '01DEND'   To CA-REQUEST-ID
                 Move ENP2CNOO   To CA-CUSTOMER-NUM
                 Move ENP2PNOO   To CA-POLICY-NUM
      * [PREPROCESSED: CICS stub]
      * EXEC CICS LINK PROGRAM('LGDPOL01')
      * COMMAREA(COMM-AREA)
      * LENGTH(32500)
      * END-EXEC
                 CONTINUE
                 IF CA-RETURN-CODE > 0
      * [PREPROCESSED: CICS stub]
      * Exec CICS Syncpoint Rollback End-Exec
                   CONTINUE
                   GO TO NO-DELETE
                 END-IF

                 Move Spaces            To  ENP2IDAI
                 Move Spaces            To  ENP2EDAI
                 Move Spaces            To  ENP2FNMI
                 Move Spaces            To  ENP2TERI
                 Move Spaces            To  ENP2SUMI
                 Move Spaces            To  ENP2LIFI
                 Move Spaces            To  ENP2WPRI
                 Move Spaces            To  ENP2MANI
                 Move Spaces            To  ENP2EQUI
                 Move 'Life Policy Deleted'
                   To  ERP2FLDO
      * [PREPROCESSED: CICS stub]
      * EXEC CICS SEND MAP ('SSMAPP2')
      * FROM(SSMAPP2O)
      * MAPSET ('SSMAP')
      * END-EXEC
                 CONTINUE
                 GO TO ENDIT-STARTIT

             WHEN '4'
                 Move '01IEND'   To CA-REQUEST-ID
                 Move ENP2CNOO   To CA-CUSTOMER-NUM
                 Move ENP2PNOO   To CA-POLICY-NUM
      * [PREPROCESSED: CICS stub]
      * EXEC CICS LINK PROGRAM('LGIPOL01')
      * COMMAREA(COMM-AREA)
      * LENGTH(32500)
      * END-EXEC
                 CONTINUE
                 IF CA-RETURN-CODE > 0
                   GO TO NO-DATA
                 END-IF

                 Move CA-ISSUE-DATE     To  ENP2IDAI
                 Move CA-EXPIRY-DATE    To  ENP2EDAI
                 Move CA-E-FUND-NAME    To  ENP2FNMI
                 Move CA-E-TERM         To  ENP2TERI
                 Move CA-E-SUM-ASSURED  To  ENP2SUMI
                 Move CA-E-LIFE-ASSURED To  ENP2LIFI
                 Move CA-E-WITH-PROFITS To  ENP2WPRI
                 Move CA-E-MANAGED-FUND To  ENP2MANI
                 Move CA-E-EQUITIES     To  ENP2EQUI
      * [PREPROCESSED: CICS stub]
      * EXEC CICS SEND MAP ('SSMAPP2')
      * FROM(SSMAPP2O)
      * MAPSET ('SSMAP')
      * END-EXEC
                 CONTINUE
      * [PREPROCESSED: CICS stub]
      * EXEC CICS RECEIVE MAP('SSMAPP2')
      * INTO(SSMAPP2I)
      * MAPSET('SSMAP') END-EXEC
                 CONTINUE

                 Move '01UEND'          To CA-REQUEST-ID
                 Move ENP2CNOI          To CA-CUSTOMER-NUM
                 Move 0                 To CA-PAYMENT
                 Move 0                 To CA-BROKERID
                 Move '        '        To CA-BROKERSREF
                 Move ENP2IDAI          To CA-ISSUE-DATE
                 Move ENP2EDAI          To CA-EXPIRY-DATE
                 Move ENP2FNMI          To CA-E-FUND-NAME
                 Move ENP2TERI          To CA-E-TERM
                 Move ENP2SUMI          To CA-E-SUM-ASSURED
                 Move ENP2LIFI          To CA-E-LIFE-ASSURED
                 Move ENP2WPRI          To CA-E-WITH-PROFITS
                 Move ENP2MANI          To CA-E-MANAGED-FUND
                 Move ENP2EQUI          To CA-E-EQUITIES
      * [PREPROCESSED: CICS stub]
      * EXEC CICS LINK PROGRAM('LGUPOL01')
      * COMMAREA(COMM-AREA)
      * LENGTH(32500)
      * END-EXEC
                 CONTINUE
                 IF CA-RETURN-CODE > 0
                   GO TO NO-UPD
                 END-IF

                 Move CA-CUSTOMER-NUM To ENP2CNOI
                 Move CA-POLICY-NUM   To ENP2PNOI
                 Move ' '             To ENP2OPTI
                 Move 'Life Policy Updated'
                   To  ERP2FLDO
      * [PREPROCESSED: CICS stub]
      * EXEC CICS SEND MAP ('SSMAPP2')
      * FROM(SSMAPP2O)
      * MAPSET ('SSMAP')
      * END-EXEC
                 CONTINUE

                 GO TO ENDIT-STARTIT

             WHEN OTHER

                 Move 'Please enter a valid option'
                   To  ERP2FLDO
                 Move -1 To ENP2OPTL

      * [PREPROCESSED: CICS stub]
      * EXEC CICS SEND MAP ('SSMAPP2')
      * FROM(SSMAPP2O)
      * MAPSET ('SSMAP')
      * CURSOR
      * END-EXEC
                 CONTINUE
                 GO TO ENDIT-STARTIT

           END-EVALUATE.
      *    Send message to terminal and return

      * [PREPROCESSED: CICS stub]
      * EXEC CICS RETURN
      * END-EXEC.
           CONTINUE.

       ENDIT-STARTIT.
      * [PREPROCESSED: CICS stub]
      * EXEC CICS RETURN
      * TRANSID('SSP2')
      * COMMAREA(COMM-AREA)
      * END-EXEC.
           CONTINUE.

       ENDIT.
      * [PREPROCESSED: CICS stub]
      * EXEC CICS SEND TEXT
      * FROM(MSGEND)
      * LENGTH(LENGTH OF MSGEND)
      * ERASE
      * FREEKB
      * END-EXEC
           CONTINUE
      * [PREPROCESSED: CICS stub]
      * EXEC CICS RETURN
      * END-EXEC.
           CONTINUE.

       CLEARIT.

           Initialize SSMAPP2I.
      * [PREPROCESSED: CICS stub]
      * EXEC CICS SEND MAP ('SSMAPP2')
      * MAPSET ('SSMAP')
      * MAPONLY
      * END-EXEC
           CONTINUE

      * [PREPROCESSED: CICS stub]
      * EXEC CICS RETURN
      * TRANSID('SSP2')
      * COMMAREA(COMM-AREA)
      * END-EXEC.
           CONTINUE.

       NO-ADD.
           Evaluate CA-RETURN-CODE
             When 70
               Move 'Customer does not exist'          To  ERP1FLDO
               Go To ERROR-OUT
             When Other
               Move 'Error Adding Life Policy'        To  ERP1FLDO
               Go To ERROR-OUT
           End-Evaluate.

       NO-UPD.
           Move 'Error Updating Life Policy'       To  ERP2FLDO
           Go To ERROR-OUT.

       NO-DELETE.
           Move 'Error Deleting Life Policy'       To  ERP2FLDO
           Go To ERROR-OUT.

       NO-DATA.
           Move 'No data was returned.'            To  ERP2FLDO
           Go To ERROR-OUT.

       ERROR-OUT.
      * [PREPROCESSED: CICS stub]
      * EXEC CICS SEND MAP ('SSMAPP2')
      * FROM(SSMAPP2O)
      * MAPSET ('SSMAP')
      * END-EXEC.
           CONTINUE.

           Initialize SSMAPP2I.
           Initialize SSMAPP2O.
           Initialize COMM-AREA.

           GO TO ENDIT-STARTIT.
