      ******************************************************************
      *                                                                *
      * (C) Copyright IBM Corp. 2011, 2020                             *
      *                                                                *
      *               Commercial Policy Menu                           *
      *                                                                *
      * Menu for Commercial Policy Transactions                        *
      *                                                                *
      ******************************************************************
       IDENTIFICATION DIVISION.
       PROGRAM-ID. LGTESTP4.
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

           Initialize SSMAPP4I.
           Initialize SSMAPP4O.
           Initialize COMM-AREA.
           MOVE '0000000000'   To ENP4CNOO.
           MOVE '0000000000'   To ENP4PNOO.
           MOVE LOW-VALUES     To ENP4FPEO.
           MOVE LOW-VALUES     To ENP4FPRO.
           MOVE LOW-VALUES     To ENP4CPEO.
           MOVE LOW-VALUES     To ENP4CPRO.
           MOVE LOW-VALUES     To ENP4XPEO.
           MOVE LOW-VALUES     To ENP4XPRO.
           MOVE LOW-VALUES     To ENP4WPEO.
           MOVE LOW-VALUES     To ENP4WPRO.
           MOVE LOW-VALUES     To ENP4STAO.
      * Display Main Menu
      * [PREPROCESSED: CICS stub]
      * EXEC CICS SEND MAP ('SSMAPP4')
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
      * EXEC CICS RECEIVE MAP('SSMAPP4')
      * INTO(SSMAPP4I)
      * MAPSET('SSMAP') END-EXEC.
           CONTINUE.


           EVALUATE ENP4OPTO

             WHEN '1'
                 If (
                     ENP4CNOO Not = Spaces      AND
                     ENP4CNOO Not = Low-Values  AND
                     ENP4CNOO Not = 0           AND
                     ENP4CNOO Not = 0000000000
                                                   )
                                                    AND
                    (
                     ENP4PNOO Not = Spaces      AND
                     ENP4PNOO Not = Low-Values  AND
                     ENP4PNOO Not = 0           AND
                     ENP4PNOO Not = 0000000000
                                                   )
                        Move '01ICOM'   To CA-REQUEST-ID
                        Move ENP4CNOO   To CA-CUSTOMER-NUM
                        Move ENP4PNOO   To CA-POLICY-NUM
                 Else
                 If (
                     ENP4PNOO Not = Spaces      AND
                     ENP4PNOO Not = Low-Values  AND
                     ENP4PNOO Not = 0           AND
                     ENP4PNOO Not = 0000000000
                                                   )
                        Move '02ICOM'   To CA-REQUEST-ID
                        Move ENP4PNOO   To CA-POLICY-NUM
                 Else
                 If (
                     ENP4CNOO Not = Spaces      AND
                     ENP4CNOO Not = Low-Values  AND
                     ENP4CNOO Not = 0           AND
                     ENP4CNOO Not = 0000000000
                                                   )
                        Move '03ICOM'   To CA-REQUEST-ID
                        Move ENP4CNOO   To CA-CUSTOMER-NUM
                 Else
                 If (
                     ENP4HPCO NOT = Spaces      AND
                     ENP4HPCO NOT = Low-Values  AND
                     ENP4HPCO Not = 0           AND
                     ENP4HPCO NOT = 00000000
                                                   )
                        Move '05ICOM'   To CA-REQUEST-ID
                        Move ENP4HPCO   To CA-B-PostCode
                 End-If
                 End-If
                 End-If
                 End-If

      * [PREPROCESSED: CICS stub]
      * EXEC CICS LINK PROGRAM('LGIPOL01')
      * COMMAREA(COMM-AREA)
      * LENGTH(32500)
      * END-EXEC
                 CONTINUE
                 IF CA-RETURN-CODE > 0
                   GO TO NO-DATA
                 END-IF
              
                 Move CA-POLICY-NUM        To  ENP4PNOI
                 Move CA-CUSTOMER-NUM      To  ENP4CNOI
                 Move CA-ISSUE-DATE        To  ENP4IDAI
                 Move CA-EXPIRY-DATE       To  ENP4EDAI
                 Move CA-B-Address         To  ENP4ADDI
                 Move CA-B-Postcode        To  ENP4HPCI
                 Move CA-B-Latitude        To  ENP4LATI
                 Move CA-B-Longitude       To  ENP4LONI
                 Move CA-B-Customer        To  ENP4CUSI
                 Move CA-B-PropType        To  ENP4PTYI
                 Move CA-B-FirePeril       To  ENP4FPEI
                 Move CA-B-FirePremium     To  ENP4FPRI
                 Move CA-B-CrimePeril      To  ENP4CPEI
                 Move CA-B-CrimePremium    To  ENP4CPRI
                 Move CA-B-FloodPeril      To  ENP4XPEI
                 Move CA-B-FloodPremium    To  ENP4XPRI
                 Move CA-B-WeatherPeril    To  ENP4WPEI
                 Move CA-B-WeatherPremium  To  ENP4WPRI
                 Move CA-B-Status          To  ENP4STAI
                 Move CA-B-RejectReason    To  ENP4REJI
      * [PREPROCESSED: CICS stub]
      * EXEC CICS SEND MAP ('SSMAPP4')
      * FROM(SSMAPP4O)
      * MAPSET ('SSMAP')
      * END-EXEC
                 CONTINUE
                 GO TO ENDIT-STARTIT

             WHEN '2'
                 Move '01ACOM'             To  CA-REQUEST-ID
                 Move ENP4CNOO             To  CA-CUSTOMER-NUM
                 Move ENP4IDAO             To  CA-ISSUE-DATE
                 Move ENP4EDAO             To  CA-EXPIRY-DATE
                 Move ENP4ADDO             To  CA-B-Address
                 Move ENP4HPCO             To  CA-B-Postcode
                 Move ENP4LATO             To  CA-B-Latitude
                 Move ENP4LONO             To  CA-B-Longitude
                 Move ENP4CUSO             To  CA-B-Customer
                 Move ENP4PTYO             To  CA-B-PropType
                 Move ENP4FPEO             To  CA-B-FirePeril
                 Move ENP4FPRO             To  CA-B-FirePremium
                 Move ENP4CPEO             To  CA-B-CrimePeril
                 Move ENP4CPRO             To  CA-B-CrimePremium
                 Move ENP4XPEO             To  CA-B-FloodPeril
                 Move ENP4XPRO             To  CA-B-FloodPremium
                 Move ENP4WPEO             To  CA-B-WeatherPeril
                 Move ENP4WPRO             To  CA-B-WeatherPremium
                 Move ENP4STAO             To  CA-B-Status
                 Move ENP4REJO             To  CA-B-RejectReason

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
                 Move CA-CUSTOMER-NUM To ENP4CNOI
                 Move CA-POLICY-NUM   To ENP4PNOI
                 Move ' '             To ENP4OPTI
                 Move 'New Commercial Policy Inserted'
                   To  ERP4FLDO
      * [PREPROCESSED: CICS stub]
      * EXEC CICS SEND MAP ('SSMAPP4')
      * FROM(SSMAPP4O)
      * MAPSET ('SSMAP')
      * END-EXEC
                 CONTINUE
                 GO TO ENDIT-STARTIT

             WHEN '3'
                 Move '01DCOM'   To CA-REQUEST-ID
                 Move ENP4CNOO   To CA-CUSTOMER-NUM
                 Move ENP4PNOO   To CA-POLICY-NUM
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

                 Move Spaces             To ENP4EDAI
                 Move Spaces             To ENP4ADDI
                 Move Spaces             To ENP4HPCI
                 Move Spaces             To ENP4LATI
                 Move Spaces             To ENP4LONI
                 Move Spaces             To ENP4CUSI
                 Move Spaces             To ENP4PTYI
                 Move Spaces             To ENP4FPEI
                 Move Spaces             To ENP4FPRI
                 Move Spaces             To ENP4CPEI
                 Move Spaces             To ENP4CPRI
                 Move Spaces             To ENP4XPEI
                 Move Spaces             To ENP4XPRI
                 Move Spaces             To ENP4WPEI
                 Move Spaces             To ENP4WPRI
                 Move Spaces             To ENP4STAI
                 Move Spaces             To ENP4REJI
                 Move ' '             To ENP4OPTI
                 Move 'Commercial Policy Deleted'
                   To  ERP4FLDO
      * [PREPROCESSED: CICS stub]
      * EXEC CICS SEND MAP ('SSMAPP4')
      * FROM(SSMAPP4O)
      * MAPSET ('SSMAP')
      * END-EXEC
                 CONTINUE
                 GO TO ENDIT-STARTIT

             WHEN OTHER

                 Move 'Please enter a valid option'
                   To  ERP4FLDO
                 Move -1 To ENP4OPTL

      * [PREPROCESSED: CICS stub]
      * EXEC CICS SEND MAP ('SSMAPP4')
      * FROM(SSMAPP4O)
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
      * TRANSID('SSP4')
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

           Initialize SSMAPP4I.
      * [PREPROCESSED: CICS stub]
      * EXEC CICS SEND MAP ('SSMAPP4')
      * MAPSET ('SSMAP')
      * MAPONLY
      * END-EXEC
           CONTINUE

      * [PREPROCESSED: CICS stub]
      * EXEC CICS RETURN
      * TRANSID('SSP4')
      * COMMAREA(COMM-AREA)
      * END-EXEC.
           CONTINUE.

       NO-ADD.
           Evaluate CA-RETURN-CODE
             When 70
               Move 'Customer does not exist'        To  ERP4FLDO
               Go To ERROR-OUT
             When Other
               Move 'Error Adding Commercial Policy' To  ERP4FLDO
               Go To ERROR-OUT
           End-Evaluate.

       NO-UPD.
           Move 'Error Updating Commercial Policy'   To  ERP4FLDO
           Go To ERROR-OUT.

       NO-DELETE.
           Move 'Error Deleting Commercial Policy'   To  ERP4FLDO
           Go To ERROR-OUT.

       NO-DATA.
           Move 'No data was returned.'              To  ERP4FLDO
           Go To ERROR-OUT.

       ERROR-OUT.
      * [PREPROCESSED: CICS stub]
      * EXEC CICS SEND MAP ('SSMAPP4')
      * FROM(SSMAPP4O)
      * MAPSET ('SSMAP')
      * END-EXEC.
           CONTINUE.

           Initialize SSMAPP4I.
           Initialize SSMAPP4O.
           Initialize COMM-AREA.

           GO TO ENDIT-STARTIT.
