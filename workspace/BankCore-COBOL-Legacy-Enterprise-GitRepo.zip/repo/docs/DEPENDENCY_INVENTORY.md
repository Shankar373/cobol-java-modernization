# Dependency Inventory

## Program dependencies

| Program | Calls / Uses | Files / Copybooks |
|---|---|---|
| BCMAIN01 | BCLOAD01, BCPROC01, BCREPT01 | Runtime orchestration |
| BCLOAD01 | — | BC-CUSTOMER.cpy, BC-ACCOUNT.cpy |
| BCPROC01 | — | BC-ACCOUNT.cpy, BC-TRANSACTION.cpy, BC-CONSTANTS.cpy |
| BCREPT01 | — | Audit/exception outputs |
| BCLEGACYX | — | Parser fixture |

## Data flow

`transactions.dat`
→ `BCPROC01`
→ `transaction-audit.dat` + `transaction-exceptions.dat`
→ `BCREPT01`
→ `end-of-day-report.txt`

## External/legacy artifacts

- JCL: `jcl/BANKCORE.jcl`
- DB2 precompiler fixture: `sql/BCACCOUNT.sqc`
- SQL schema: `sql/DDL.sql`
- Compiler: GnuCOBOL for local execution
