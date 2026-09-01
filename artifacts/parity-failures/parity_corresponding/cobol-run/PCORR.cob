       IDENTIFICATION DIVISION.
       PROGRAM-ID. PCORR.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-A.
           05 WS-X PIC 9(2) VALUE 10.
           05 WS-Y PIC 9(2) VALUE 20.
           05 WS-Z PIC X(5) VALUE "HELLO".
       01 WS-B.
           05 WS-X PIC 9(2) VALUE 1.
           05 WS-Y PIC 9(2) VALUE 2.
           05 WS-W PIC X(5) VALUE "WORLD".
       PROCEDURE DIVISION.
           MOVE CORRESPONDING WS-A TO WS-B.
           DISPLAY WS-B.
           
           ADD CORRESPONDING WS-A TO WS-B.
           DISPLAY WS-B.
           
           SUBTRACT CORRESPONDING WS-A FROM WS-B.
           DISPLAY WS-B.
           GOBACK.
