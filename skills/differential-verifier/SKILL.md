---
name: differential-verifier
description: Orchestrates the canonical 4-step differential verification between GnuCOBOL and JDK 17+ Java executions.
---

# Differential Verifier Skill

## The 4-Step Verification Lifecycle

1. **Step 1: Conversion**: Transpile COBOL to Java.
2. **Step 2: Compilation**: Compile Java with JDK 17+ javac and Maven.
3. **Step 3: Baseline Execution**: Execute COBOL under GnuCOBOL/OCESQL or recorded baseline fixtures.
4. **Step 4: Java Execution & Differential Comparison**:
   - Compare exit codes (`0` vs `0`).
   - Compare stdout byte-for-byte or normalized line endings.
   - Compare output files (`data/out/*`).
   - Compare database state mutations.

## Verdicts
- `PASS`: Exact equivalence across all observable channels.
- `WARNING`: Compatibility proven (e.g. JCL/CICS compatibility runners or mock database).
- `FAIL`: Any discrepancy in return code, stdout, or files.
- `UNPROVEN`: Baseline or runtime environment unavailable.
- `BLOCKED`: Blocked by unsupported construct or prerequisite failure.
