# Mentor 4-Step Differential Validation Report: MULTIFILE01

- **Program:** `MULTIFILE01`
- **Source:** `C:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test\tests\repos\MULTIFILE01\MULTIFILE01.cob`
- **Generated Java:** `C:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test\target\verification\MULTIFILE01\native`
- **JDK Version:** `javac 25.0.3`
- **Maven Version:** `Apache Maven 3.9.16 (2bdd9fddda4b155ebf8000e807eb73fd829a51d5)`
- **Conversion:** `PASS`
- **Compilation:** `PASS`
- **COBOL Runtime:** `PASS` (Exit Code: `0`)
- **Java Runtime:** `FAIL` (Exit Code: `0`)
- **Business Equivalence:** `UNPROVEN`
- **Execution UTC:** `2026-09-01T16:01:46.393511+00:00`
- **Cryptographic Manifest SHA-256:** `1e11b4e924cbae600a94a5b2eae6ed4fc33f4c55a12d71765540eaf17956922f`

---

## 1. Step-by-Step Execution Summary

| Step | Name | Status | Duration (ms) | Details |
|---|---|---|---|---|
| **Step 1** | Step 1: Conversion (COBOL -> Java) | `PASS` | `100.5` | OK |
| **Step 2** | Step 2: JDK 17+ Compilation | `PASS` | `12850.3` | OK |
| **Step 3** | Step 3: COBOL Baseline Execution | `PASS` | `3011.0` | REAL_GNUCOBOL_DOCKER |
| **Step 4** | Step 4: Differential Equivalence | `UNPROVEN` | `14855.3` | OK |

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
| `source/input-b.dat` | `MISSING...` | `da2c2f5fb0f0...` | `MISMATCH` | 44 |
| `source/input-a.dat` | `MISSING...` | `c5cac2f5e9e9...` | `MISMATCH` | 34 |
| `reports/report-b.dat` | `MISSING...` | `d499037b69b7...` | `MISMATCH` | 44 |
| `reports/report-a.dat` | `MISSING...` | `21b359d4e47f...` | `MISMATCH` | 32 |

- **Database State Comparison:** `NOT_APPLICABLE` - No SQL embedded in workload.

---

## 4. Warnings & Unsupported Constructs

- No warnings recorded.