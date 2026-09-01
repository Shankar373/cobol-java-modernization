# Mentor 4-Step Differential Validation Report: ACCTPROG

- **Program:** `ACCTPROG`
- **Source:** `C:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test\tests\repos\ACCTPROG\src\ACCTPROG.cob`
- **Generated Java:** `C:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test\target\verification\ACCTPROG\native`
- **JDK Version:** `javac 25.0.3`
- **Maven Version:** `Apache Maven 3.9.16 (2bdd9fddda4b155ebf8000e807eb73fd829a51d5)`
- **Conversion:** `PASS`
- **Compilation:** `PASS`
- **COBOL Runtime:** `PASS` (Exit Code: `0`)
- **Java Runtime:** `FAIL` (Exit Code: `0`)
- **Business Equivalence:** `UNPROVEN`
- **Execution UTC:** `2026-09-01T16:01:10.963829+00:00`
- **Cryptographic Manifest SHA-256:** `020666f8e489c8ab0c3ed77c69646811af3b94f259ddd88bbc6f62a28e9db13a`

---

## 1. Step-by-Step Execution Summary

| Step | Name | Status | Duration (ms) | Details |
|---|---|---|---|---|
| **Step 1** | Step 1: Conversion (COBOL -> Java) | `PASS` | `160.9` | OK |
| **Step 2** | Step 2: JDK 17+ Compilation | `PASS` | `15066.1` | OK |
| **Step 3** | Step 3: COBOL Baseline Execution | `PASS` | `3478.8` | REAL_GNUCOBOL_DOCKER |
| **Step 4** | Step 4: Differential Equivalence | `UNPROVEN` | `14434.3` | OK |

---

## 2. Stdout Comparison

### COBOL Baseline Stdout
```text
<EMPTY>
```

### Java Modernized Stdout
```text
<EMPTY>
```

**Stdout Match:** `MATCH`

---

## 3. File & Database State Comparison

| Filename | Legacy SHA-256 | Java SHA-256 | Match | Size (Bytes) |
|---|---|---|---|---|
| `final-result-report.txt` | `cb1aef1a3648...` | `4e3698b292bf...` | `MISMATCH` | 67 |
| `raw-source-data.bin` | `2498721d6842...` | `2498721d6842...` | `MATCH` | 76 |

- **Database State Comparison:** `NOT_APPLICABLE` - No SQL embedded in workload.

---

## 4. Warnings & Unsupported Constructs

- No warnings recorded.