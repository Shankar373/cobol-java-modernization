# Mentor 4-Step Differential Validation Report: DB2SELECT01

- **Program:** `DB2SELECT01`
- **Source:** `C:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test\tests\repos\DB2SELECT01\src\DB2SELECT01.cob`
- **Generated Java:** `C:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test\target\verification\DB2SELECT01\native`
- **JDK Version:** `javac 25.0.3`
- **Maven Version:** `Apache Maven 3.9.16 (2bdd9fddda4b155ebf8000e807eb73fd829a51d5)`
- **Conversion:** `PASS`
- **Compilation:** `PASS`
- **COBOL Runtime:** `UNPROVEN` (Exit Code: `-1`)
- **Java Runtime:** `FAIL` (Exit Code: `0`)
- **Business Equivalence:** `FAIL`
- **Execution UTC:** `2026-09-01T16:02:24.792796+00:00`
- **Cryptographic Manifest SHA-256:** `3c05b4c1f8c61c1d09ea39477f2cee7c83914e3cc5a7c9195b83500e751cc734`

---

## 1. Step-by-Step Execution Summary

| Step | Name | Status | Duration (ms) | Details |
|---|---|---|---|---|
| **Step 1** | Step 1: Conversion (COBOL -> Java) | `PASS` | `333.4` | OK |
| **Step 2** | Step 2: JDK 17+ Compilation | `PASS` | `15907.5` | OK |
| **Step 3** | Step 3: COBOL Baseline Execution | `UNPROVEN` | `2674.9` | No GnuCOBOL baseline available |
| **Step 4** | Step 4: Differential Equivalence | `FAIL` | `15167.1` | OK |

---

## 2. Stdout Comparison

### COBOL Baseline Stdout
```text
<EMPTY>
```

### Java Modernized Stdout
```text
SQLCODE: 000000000
SQLSTATE: 00000
CUST-NAME: TEST CUSTOMER
```

**Stdout Match:** `MISMATCH`

---

## 3. File & Database State Comparison

- No output files generated.

- **Database State Comparison:** `WARNING_H2` - Compatibility verified; real DB2 unproven.

---

## 4. Warnings & Unsupported Constructs

- ⚠️ SQL execution executed against local H2 compatibility store; real DB2 unproven.