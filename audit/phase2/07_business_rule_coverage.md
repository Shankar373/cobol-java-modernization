# Phase 2: Business Rule Coverage Specification

This document details the tracking contract for logic rules mapping:

## 1. Business Verification Reporting Layout
The final report must list verification test coverage for all discovered business rules:

| Program | Rule ID | COBOL Location | Java Location | Test Case | Status | Evidence |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| `BCPROC01` | BR-01 | Line 159 (ACCT-STATUS NOT = 'A') | `BCPROC01.java:120` | `test_inactive_rejection` | **VERIFIED** | Reject logs match |
| `BCPROC01` | BR-02 | Line 179 (Balance < Overdraft) | `BCPROC01.java:145` | `test_insufficient_debit` | **VERIFIED** | Balance matches |

## 2. Rule Lifecycles
- `DISCOVERED`: Mapped in the COBOL IR.
- `MAPPED`: Mapped to Java Target Model structure.
- `GENERATED`: Written to output source file.
- `TESTED`: Covered by automated test cases.
- `VERIFIED`: Parity validations pass under deterministic test scenarios.
