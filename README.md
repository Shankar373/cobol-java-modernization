# Cobol-to-java-test — ClaimsCore modernization proof with COBOL 4J

Standalone test project. Proves that the **ClaimsCore** COBOL insurance-claims batch
(the sample found in `SystemaOps\Cobol-to-java\temp_sessions`) can be transpiled to Java
with **opensource COBOL 4J** (`cobj`), executed, and produce the exact business outcomes
documented in the legacy project.

This project is a *sandbox*. Nothing here is wired into the original
`SystemaOps\Cobol-to-java` project. If the checks pass and you are happy with the result,
this Java output is the thing to integrate.

---

## Toolchain

| Component | Version | How obtained |
|---|---|---|
| opensource COBOL 4J (`cobj`) | 2.0.0 | Docker image `opensourcecobol/opensourcecobol4j:2.0.0` |
| Runtime library `libcobj.jar` | 2.0.0 | ships inside the image |
| JDK | any (image uses OpenJDK) | inside the image |
| Docker | local | required on the host |

The original project's `README.md` already names this engine ("opensource-cobol4j v2.0.0").
This test project makes it actually run.

---

## Structure

```
Cobol-to-java-test/
├── modernize_and_verify.py   # harness: transpile -> run -> verify (exit code = pass/fail)
├── legacy/                   # ClaimsCore sample (isolated copy)
│   ├── src/*.cob             #   CCMAIN01, CCLOAD01, CCPROC01, CCREPT01, CCLEGACYX
│   ├── copybooks/*.cpy       #   CC-POLICY, CC-CUSTOMER, CC-CLAIM, CC-CONSTANTS
│   ├── data/in/claims.dat    #   7 fixed-format claim records (golden fixture)
│   ├── data/work/            #   indexed policy/customer master files (auto-created)
│   ├── data/out/             #   audit / exceptions / report (generated)
│   ├── generated/            #   cobj output: CCMAIN01.java ... *.class  (generated)
│   ├── jcl/                  #   CLAIMSCORE.jcl (reference only)
│   └── sql/                  #   CCCLAIM.sqc, DDL.sql (reference only)
└── README.md
```

---

## How to run

```
docker pull opensourcecobol/opensourcecobol4j:2.0.0     # once
python modernize_and_verify.py                          # transpile + run + verify
```

The harness:
1. **transpile** — `cobj -free` converts all 5 COBOL programs to Java/class files.
2. **run** — `java CCMAIN01` executes the whole batch (CALL chain, indexed files,
   line-sequential files).
3. **verify** — asserts the 7 claim outcomes, exception codes, report counts, and the
   COMP-3 settlement amounts.

Expected console output ends with:

```
RESULT: ALL CHECKS PASSED (7/7 claims, report counts, COMP-3 amounts)
```

---

## What is verified (business outcomes)

Business rules come from `CCPROC01` (`VALIDATE-POLICY`, `CALCULATE-SETTLEMENT`):
policy must exist (P001), be active (P002), and cover the claim type (P003);
settlement = loss − deductible, floored at 0, capped at the cover limit,
and routed to manual review when above 200,000.

| # | Claim | Policy | Loss | Outcome | Amount | Rule exercised |
|---|---|---|---|---|---|---|
| 1 | CLM000000001 | PL00000001 (MV) | 120,000.00 | APPROVED | 95,000.00 | deduct 25,000 |
| 2 | CLM000000002 | PL00000002 (HE) | 45,000.00 | APPROVED | 35,000.00 | deduct 10,000 |
| 3 | CLM000000003 | PL00000001 (MV) | 320,000.00 | MANUAL_REVIEW | 295,000.00 | > 200,000 |
| 4 | CLM000000004 | PL00000003 (status E) | 60,000.00 | REJECTED P002 | — | inactive policy |
| 5 | CLM000000005 | PL99999999 (missing) | 25,000.00 | REJECTED P001 | — | unknown policy |
| 6 | CLM000000006 | PL00000002 (HE) | 50,000.00 | REJECTED P003 | — | type mismatch (MV claim) |
| 7 | CLM000000007 | PL00000002 (HE) | 350,000.00 | MANUAL_REVIEW | 300,000.00 | cap at 300,000 cover |

Report: `AUDIT RECORDS 4, EXCEPTIONS 3, MANUAL REVIEWS 2`.

---

## Findings and notes

1. **Legacy fixture defect (fixed in this copy only).** The original `CCPROC01.cob`
   reads each claim into `CLAIM-LINE` but `MAP-CLAIM` copies from `WS-RAW`, which is
   **never populated** (`MOVE CLAIM-LINE TO WS-RAW` is missing). As written, every claim
   has empty fields and is rejected P001 — both under GnuCOBOL and under COBOL 4J
   (the transpiler reproduced it faithfully). To make the documented 7-outcome behavior
   testable, this test copy adds the missing MOVE and widens `CLAIM-LINE` to X(152)
   (records are 152 bytes). The original `temp_sessions` file was **not** touched.

2. **Source is free-format.** 12 lines exceed column 72 (e.g. `CCLOAD01.cob:11`), so
   compilation requires `cobj -free` (the original GnuCOBOL build already used `cobc -free`).

3. **COMP-3 in STRING output.** In the generated Java, `STRING` of a COMP-3 field writes
   the **raw packed bytes** (not display digits) into the audit line. GnuCOBOL renders
   digits. Semantically the amount is correct (verified by decoding the packed decimal),
   but byte-for-byte output differs. Flag for a renderer shim if byte-parity is required.

4. **STRING does not clear the target.** The report lines keep leftover bytes
   (`AUDIT RECORDS : 0000004REPORT`). This is faithful COBOL STRING behavior, present
   under GnuCOBOL too.

5. **Indexed files auto-create.** `OPEN OUTPUT` + `WRITE` on `ORGANIZATION IS INDEXED`
   files creates `policy.dat`/`customer.dat` automatically (no `cobj-idx create` needed).

6. **COBOL 4J is a real transpiler here.** `legacy/generated/CCPROC01.java` contains the
   actual settlement logic (e.g. `d0.sub(d1)` = loss − deductible, cap vs cover limit,
   `> 200000 → result 'M'`), not a stub. This is the opposite of the original project's
   `modernization_pipeline.py`, which only emits `System.out.println` placeholders.

---

## Integration notes (later phase)

- Generated Java: `legacy/generated/*.java` (+ `libcobj.jar` at runtime).
- To integrate into `SystemaOps\Cobol-to-java`: replace the stub generation in
  `modernization_pipeline.convert_cobol_to_java()` with a call to `cobj`, vendor
  `libcobj.jar`, and route DSNs through `systemaops.json` (already exists).
- The `cobj` `-info-json-dir` option emits program metadata that the project's
  `cobj-api` can turn into Spring Boot controllers — a documented upgrade path for
  the batch/web/API story.
- Postgres path: `sql/CCCLAIM.sqc` + `DDL.sql` map to `INS_POLICY` / `INS_CLAIM_AUDIT`
  (`libcobj` has EXEC SQL support as of 2.0.0).
