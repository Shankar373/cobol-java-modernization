# Modernization Test Matrix

| Area | Source | Expected test |
|---|---|---|
| COBOL program discovery | `src/*.cob` | Detect 4 programs |
| Copybook discovery | `copybooks/*.cpy` | Resolve shared record layouts |
| Indexed files | `BCLOAD01`, `BCPROC01` | Convert VSAM-style access |
| Packed decimals | `BC-CUSTOMER.cpy`, `BC-ACCOUNT.cpy` | Preserve numeric precision |
| Business rules | `BCPROC01` | Preserve credit/debit/transfer behavior |
| Error handling | `BCPROC01` | Preserve rejection paths |
| Batch orchestration | `BCMAIN01` | Preserve program call sequence |
| JCL | `jcl/BANKCORE.jcl` | Map job/step/DD semantics |
| SQL | `sql/BCACCOUNT.sqc` | Detect EXEC SQL blocks |
| DB schema | `sql/DDL.sql` | Map tables and DECIMAL fields |
| Sequential files | transaction/audit/exception | Preserve record flow |
| Reports | `BCREPT01` | Preserve aggregation/report output |
| Legacy constructs | EVALUATE/PERFORM/REDEFINES/COMP-3 | Parser and translator coverage |
