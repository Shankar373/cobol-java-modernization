# Architecture

```text
                    +------------------+
                    |   BCMAIN01       |
                    | Batch Controller |
                    +--------+---------+
                             |
                +------------+-------------+
                |            |             |
                v            v             v
          +-----------+ +-----------+ +-----------+
          | BCLOAD01  | | BCPROC01  | | BCREPT01  |
          | Master    | | Txn Rules | | EOD Report|
          | Load      | | & Posting | |           |
          +-----+-----+ +-----+-----+ +-----+-----+
                |             |             |
                v             v             v
          Customer/Account  Audit/Exc     EOD Report
          Indexed Files     Sequential     Sequential
```

The design intentionally resembles a small mainframe batch domain while remaining runnable on a normal workstation through GnuCOBOL.
