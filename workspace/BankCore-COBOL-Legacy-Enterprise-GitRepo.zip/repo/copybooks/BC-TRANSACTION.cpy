       01  TRANSACTION-RECORD.
           05  TXN-ID              PIC X(12).
           05  TXN-DATE            PIC 9(8).
           05  TXN-TIME            PIC 9(6).
           05  TXN-TYPE            PIC X(01).
           05  TXN-SOURCE-ACCT     PIC X(10).
           05  TXN-TARGET-ACCT     PIC X(10).
           05  TXN-AMOUNT          PIC 9(9)V99.
           05  TXN-CURRENCY        PIC X(03).
           05  TXN-CHANNEL         PIC X(02).
           05  TXN-REFERENCE       PIC X(20).
           05  TXN-FLAGS           PIC X(10).
