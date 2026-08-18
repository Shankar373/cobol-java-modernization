# BankCore — COBOL Legacy Enterprise Modernization Test Repository

> **Purpose:** A realistic, self-contained COBOL enterprise batch repository for testing Git-based legacy application discovery, analysis, dependency mapping, modernization, translation, validation, and regression workflows.

## Repository contract

This is intentionally a **multi-file Git repository**, not a single COBOL file. A modernization platform should ingest the repository root and discover:

- 5 COBOL programs
- 4 copybooks
- 1 JCL job
- 1 DB2 SQL precompiler fixture
- 1 SQL DDL schema
- sample transaction data
- build/run scripts
- CI workflow
- documentation and modernization acceptance criteria

## Suggested Git-based SystemaOps test

```text
Git Repository
      |
      v
Repository Discovery
      |
      +--> COBOL programs
      +--> Copybooks
      +--> JCL
      +--> SQL
      +--> Data files
      |
      v
Dependency / Call Graph
      |
      v
Business Rule Extraction
      |
      v
Modernization Plan
      |
      v
Target-language Translation
      |
      v
Build + Tests
      |
      v
Behavioral Validation
      |
      v
Migration Report
```

## Important

`src/BCLEGACYX.cob` is a **parser/modernization fixture** and is intentionally not included in the normal executable build. It contains additional legacy constructs such as `REDEFINES`, `OCCURS`, `PERFORM THRU`, and `EVALUATE`.

# COBOL Legacy Enterprise Test Application — BankCore

A self-contained, enterprise-style COBOL batch application designed specifically for testing a legacy-application modernization platform.

## What it simulates

- Customer master data
- Account master data
- Daily transaction processing
- Credit/debit/transfer transactions
- Balance validation
- Overdraft checks
- Transaction audit trail
- End-of-day reconciliation
- Exception/error file
- Operational report
- COBOL copybooks
- JCL-style batch job definitions
- DB2 SQL precompiler example
- Multi-program COBOL architecture
- Indexed VSAM-style files
- Packed-decimal (`COMP-3`) fields
- `REDEFINES`, `OCCURS`, `EVALUATE`, `PERFORM THRU`
- File status handling
- Sequential input/output files

## Application flow

1. `BCLOAD01` creates/rebuilds indexed customer and account master files.
2. `BCPROC01` processes `data/in/transactions.dat`.
3. `BCREPT01` reads the processed audit and exception files and produces an end-of-day report.
4. `BCMAIN01` orchestrates the full flow when running the complete application.

## Expected business behavior

The sample transaction file contains:
- valid credits
- valid debits
- valid transfers
- insufficient-funds transactions
- invalid account transactions
- invalid transaction types

The application should continue processing after individual transaction failures and write those failures to the exception file.

## Build

### Windows with GnuCOBOL

Install GnuCOBOL and make sure `cobc` is on PATH.

Run:

```bat
scripts\build.bat
```

Then:

```bat
scripts\run.bat
```

### Linux/macOS with GnuCOBOL

```bash
chmod +x scripts/build.sh scripts/run.sh
./scripts/build.sh
./scripts/run.sh
```

## Outputs

After execution:

- `data/out/transaction-audit.dat`
- `data/out/transaction-exceptions.dat`
- `data/out/end-of-day-report.txt`

The executable is:

- Windows: `bin\bankcore.exe`
- Linux/macOS: `bin/bankcore`

## Modernization test opportunities

This codebase intentionally contains patterns commonly encountered in enterprise COBOL:

- fixed-format COBOL
- copybooks
- numeric `COMP-3`
- indexed files
- sequential files
- file-status codes
- multiple programs
- shared data structures
- legacy naming conventions
- batch orchestration
- JCL
- SQL precompiler source
- business-rule-heavy procedural code
- error/reconciliation processing

The primary runtime does not require DB2, CICS, or a mainframe.
