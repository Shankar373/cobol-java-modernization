# Legacy Insurance COBOL

A controlled, deterministic legacy-style Insurance Policy & Claims Management System used as a golden-reference application for COBOL → Native Java/Spring modernization testing.

## Scope

This repository intentionally contains multiple legacy technologies:

- COBOL batch and online-style programs
- COPYBOOKs
- DB2 EXEC SQL examples
- SQLCA handling
- CICS EXEC CICS examples
- BMS maps
- VSAM KSDS definitions
- Sequential files
- JCL
- Static and dynamic CALL examples
- Deterministic business rules and test data

## Important execution boundary

This is a **reference legacy application**, not a claim that a plain Windows/GnuCOBOL environment can execute every mainframe subsystem.

| Component | Local reference validation | Requires legacy runtime |
|---|---|---|
| COBOL business logic | Yes, where compiler-supported | No |
| Sequential files | Yes | No |
| DB2 SQL source analysis | Yes | Real DB2 for execution |
| CICS programs | Source validation only | CICS runtime |
| BMS maps | Source validation only | CICS/BMS runtime |
| VSAM definitions | Source validation only | VSAM/mainframe-compatible runtime |
| JCL | Structural review | JES/mainframe scheduler |

H2 must not be treated as proof of DB2 equivalence. REAL_DB2_VERIFIED requires actual DB2 execution.

## Business rules

1. Approved claim = min(requested amount, policy coverage limit).
2. Deductible is subtracted from the approved amount, never below zero.
3. Claims above 200000 require MANUAL_REVIEW.
4. Claims for inactive/expired/cancelled policies are rejected.
5. Duplicate claim IDs are rejected.
6. Every approval/rejection/payment event is auditable.

## Golden-reference objective

The expected outputs in `data/expected/` are deterministic and can be compared against a future native Java/Spring implementation.
