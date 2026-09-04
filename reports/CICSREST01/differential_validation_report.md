# Mentor 4-Step Differential Validation Report: CICSREST01

- **Program:** `CICSREST01`
- **Source:** `C:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test\tests\repos\CICSREST01\src\CICSREST01.cob`
- **Generated Java:** `C:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test\target\verification\CICSREST01\native`
- **JDK Version:** `javac 25.0.3`
- **Maven Version:** `Apache Maven 3.9.16 (2bdd9fddda4b155ebf8000e807eb73fd829a51d5)`
- **Conversion:** `PASS`
- **Compilation:** `PASS`
- **COBOL Runtime:** `UNPROVEN` (Exit Code: `-1`)
- **Java Runtime:** `FAIL` (Exit Code: `0`)
- **Business Equivalence:** `FAIL`
- **Execution UTC:** `2026-09-01T16:03:31.317348+00:00`
- **Cryptographic Manifest SHA-256:** `5d365b4c5306ae0298068ec73767f352c689f6aff047697af5b94e1b91a1fcd2`

---

## 1. Step-by-Step Execution Summary

| Step | Name | Status | Duration (ms) | Details |
|---|---|---|---|---|
| **Step 1** | Step 1: Conversion (COBOL -> Java) | `PASS` | `169.1` | OK |
| **Step 2** | Step 2: JDK 17+ Compilation | `PASS` | `13943.8` | OK |
| **Step 3** | Step 3: COBOL Baseline Execution | `UNPROVEN` | `2000.6` | No GnuCOBOL baseline available |
| **Step 4** | Step 4: Differential Equivalence | `FAIL` | `11440.7` | OK |

---

## 2. Stdout Comparison

### COBOL Baseline Stdout
```text
<EMPTY>
```

### Java Modernized Stdout
```text
CICS RECEIVE MAP: INPUTMAP MAPSET: MSET OPTIONS: {}
RECEIVED INPUT:           
CICS SEND MAP: OUTMAP MAPSET: MSET DATA: INITIALVAL OPTIONS: {}
```

**Stdout Match:** `MISMATCH`

---

## 3. File & Database State Comparison

- No output files generated.

- **Database State Comparison:** `NOT_APPLICABLE` - No SQL embedded in workload.

---

## 4. Warnings & Unsupported Constructs

- ⚠️ CICS transaction executed under compatibility runtime (Real IBM CICS unproven).