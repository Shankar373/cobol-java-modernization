# Mentor 4-Step Differential Validation Report: SIMPLEBASELINE01

- **Program:** `SIMPLEBASELINE01`
- **Source:** `C:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test\tests\repos\SIMPLEBASELINE01\src\SIMPLEBASELINE01.cob`
- **Generated Java:** `C:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test\target\verification\SIMPLEBASELINE01\native`
- **JDK Version:** `javac 25.0.3`
- **Maven Version:** `Apache Maven 3.9.16 (2bdd9fddda4b155ebf8000e807eb73fd829a51d5)`
- **Conversion:** `PASS`
- **Compilation:** `PASS`
- **COBOL Runtime:** `PASS` (Exit Code: `0`)
- **Java Runtime:** `PASS` (Exit Code: `0`)
- **Business Equivalence:** `PASS`
- **Execution UTC:** `2026-09-01T16:00:32.271335+00:00`
- **Cryptographic Manifest SHA-256:** `5b18ee90d8000b2b615a3c8bf69334caa09cedfae9cabd4b3c5912f0543fd31f`

---

## 1. Step-by-Step Execution Summary

| Step | Name | Status | Duration (ms) | Details |
|---|---|---|---|---|
| **Step 1** | Step 1: Conversion (COBOL -> Java) | `PASS` | `180.9` | OK |
| **Step 2** | Step 2: JDK 17+ Compilation | `PASS` | `14646.7` | OK |
| **Step 3** | Step 3: COBOL Baseline Execution | `PASS` | `3242.4` | REAL_GNUCOBOL_DOCKER |
| **Step 4** | Step 4: Differential Equivalence | `PASS` | `13658.5` | OK |

---

## 2. Stdout Comparison

### COBOL Baseline Stdout
```text
SIMPLEBASELINE01 START
ADD RESULT: 00075
COMPUTE RESULT: 01260
SIMPLEBASELINE01 END
```

### Java Modernized Stdout
```text
SIMPLEBASELINE01 START
ADD RESULT: 00075
COMPUTE RESULT: 01260
SIMPLEBASELINE01 END
```

**Stdout Match:** `MATCH`

---

## 3. File & Database State Comparison

| Filename | Legacy SHA-256 | Java SHA-256 | Match | Size (Bytes) |
|---|---|---|---|---|
| `out.dat` | `8bee67331dce...` | `de5f7f3f99df...` | `MATCH` | 22 |

- **Database State Comparison:** `NOT_APPLICABLE` - No SQL embedded in workload.

---

## 4. Warnings & Unsupported Constructs

- No warnings recorded.