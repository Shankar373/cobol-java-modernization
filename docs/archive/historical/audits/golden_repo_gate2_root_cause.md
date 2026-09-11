> [!NOTE]
> **HISTORICAL ARCHIVE — NOT CURRENT SOURCE OF TRUTH**  
> This document is preserved for historical provenance and audit trail purposes only. Refer to [`DOCUMENTATION_INDEX.md`](../../../DOCUMENTATION_INDEX.md) for the authoritative active documentation set.

---

# Root Cause Investigation: Golden Repo Gate 2 File Mismatch

- **Target Workload:** `mentor_cobol_golden_repo.zip` (`GOLDENPAY`)
- **Failing File:** `data/out/customer_report.txt`
- **Gate Status:** Gate 1 PASS, Gate 2 FAIL
- **Investigator:** Antigravity Senior Software Engineer
- **Date:** 2026-09-01
- **Status:** **INVESTIGATION COMPLETE — ROOT CAUSE IDENTIFIED (NO CODE MODIFICATIONS APPLIED)**

---

## 1. Artifact Inventory & Cryptographic Hashes

| Artifact Description | Path | Size | SHA-256 Hash | Line Ending |
|---|---|---|---|---|
| **COBOL Baseline Output** | `target/baseline/legacy/data/out/customer_report.txt` | 32 B | `aa752eea4445308ea4ad065b337c1cfc285d3e1f8cdce2e2ebcc1cd90c3c08ad` | LF (`0x0A`) |
| **Transpiled Java Output** | `target/results/java/data/out/customer_report.txt` | 32 B | `aa752eea4445308ea4ad065b337c1cfc285d3e1f8cdce2e2ebcc1cd90c3c08ad` | LF (`0x0A`) |
| **Refactored Native Output** | `target/modernized/data/out/customer_report.txt` | 34 B | `cbb06447172aeffcfc39793c773ff8fe9ac37b1e1f0be78557528f67589ec951` | CRLF (`0x0D 0x0A`) |

---

## 2. Byte-Level Comparison

### Raw Output Content

- **COBOL Baseline:**
  ```text
  100101 | ACTIVE     | 000010025\n
  ```
- **Transpiled Java:**
  ```text
  100101 | ACTIVE     | 000010025\n
  ```
- **Refactored Native Java:**
  ```text
  100101 | ACTIVE     | 0000100.25\r\n
  ```

### Hex Dump Comparison

```text
COBOL / Transpiled Java (32 bytes):
31 30 30 31 30 31 20 7C 20 41 43 54 49 56 45 20   100101 | ACTIVE 
20 20 20 20 20 7C 20 30 30 30 30 31 30 30 32 35      | 000010025
0A                                                .

Refactored Native Java (34 bytes):
31 30 30 31 30 31 20 7C 20 41 43 54 49 56 45 20   100101 | ACTIVE 
20 20 20 20 20 7C 20 30 30 30 30 31 30 30 2E 32      | 0000100.2
35 0D 0A                                          5..
```

- **First Differing Byte:** Byte 30 (0-indexed).
  - COBOL/Transpiled: Byte 30 is `0x32` (`'2'`).
  - Refactored Native: Byte 30 is `0x2E` (`'.'`).
- **End-of-Line Difference:**
  - COBOL/Transpiled: `0x0A` (LF).
  - Refactored Native: `0x0D 0x0A` (CRLF).

---

## 3. Text-Level Analysis

The mismatch stems from two distinct factors:
1. **Implied Decimal (`V`) in `STRING` Statement:**
   In COBOL, `CUSTOMER-BALANCE` is declared as `PIC 9(7)V99` (total 9 digits, 2 implied fractional decimals).
   Under COBOL standard semantics (ANSI/ISO COBOL), sending items in a `STRING` statement are treated as alphanumeric character data corresponding to their **raw storage representation**. In storage, `PIC 9(7)V99` holds **no decimal point character**; `100.25` is stored as the 9-character string `"000010025"`.
   The native generator translated `STRING ... CUSTOMER-BALANCE ...` using `String.valueOf(customer_balance)`, which called `CobolNumeric.toString() -> toDisplayString()`, inserting an explicit ASCII decimal point `.` (`"0000100.25"`).
2. **Platform Newline Emission:**
   `BufferedWriter.newLine()` on Windows emits `\r\n` (2 bytes), whereas GnuCOBOL line sequential file handler emits `\n` (1 byte).

---

## 4. Trace Back to COBOL

### `CUSTOMER-COPY.cpy`
```cobol
01 CUSTOMER-AREA.
   05 CUSTOMER-ID       PIC 9(6) VALUE 100101.
   05 CUSTOMER-NAME     PIC X(30) VALUE "ALICE".
   05 CUSTOMER-STATUS   PIC X(10) VALUE SPACES.
   05 CUSTOMER-BALANCE  PIC 9(7)V99 VALUE 0.
```

### `GOLDENPAY.cob`
```cobol
       OPEN OUTPUT REPORT-FILE.
       STRING CUSTOMER-ID DELIMITED BY SIZE
              " | " DELIMITED BY SIZE
              CUSTOMER-STATUS DELIMITED BY SIZE
              " | " DELIMITED BY SIZE
              CUSTOMER-BALANCE DELIMITED BY SIZE
              INTO WS-LINE
       END-STRING.
       WRITE REPORT-REC FROM WS-LINE.
       CLOSE REPORT-FILE.
```

---

## 5. Trace of Java Generation & Refactoring

### Stage 1: Transpiled Java (`target/generated/GOLDENPAY.java`)
- Transpiled with opensource COBOL 4J runtime (`libcobj`).
- `b_CUSTOMER_BALANCE__CUSTOMER_AREA.setBytes(str_2_000010025, 9);`
- `CobolString.stringAppend(f_CUSTOMER_BALANCE__CUSTOMER_AREA);`
- Appended raw 9 bytes `"000010025"`.
- **Result:** Output matched COBOL baseline byte-for-byte (**Gate 1: PASS**).

### Stage 2: Refactored Native Java (`target/modernized/.../Goldenpay.java`)
- `modernize/native_generator.py` generated line 271:
  ```java
  ws_line = padString(String.valueOf(String.valueOf(customer_id) + " | " + customer_status + " | " + String.valueOf(customer_balance)), 80);
  ```
- `String.valueOf(customer_balance)` invokes `CobolNumeric.toDisplayString()`, formatting the number as `"0000100.25"` (10 characters with decimal dot) instead of `"000010025"` (9 characters storage image).
- `write_report_file()` uses `BufferedWriter.newLine()`, emitting `\r\n`.
- **Result:** Content mismatch (**Gate 2: FAIL**).

---

## 6. Output Comparison Matrix

| Comparison | Result | Note |
|---|---|---|
| **COBOL == Transpiled Java** | **`MATCH`** | 100% byte-for-byte match (32 bytes, identical SHA-256) |
| **Transpiled Java == Refactored Native** | **`MISMATCH`** | Refactored introduced `.` and CRLF (34 bytes vs 32 bytes) |
| **COBOL == Refactored Native** | **`MISMATCH`** | Gate 2 failure detected |

---

## 7. Validation Logic Check

- **Validator Status:** **`CORRECT`**
- Gate 2 properly compared the actual output generated by the native application against the certified baseline.
- No workspace contamination, stale artifacts, or path redirection bugs exist.
- The failure was genuinely caused by a divergence in code generation semantics between Stage 1 and Stage 2.

---

## 8. Root Cause Classification

**`B. Java generator bug`**

Specifically:
`modernize/native_generator.py` handles operands in COBOL `STRING` statements by emitting `String.valueOf(var)`. For `CobolNumeric` fields with implied decimal positions (`V`), `String.valueOf()` yields the formatted decimal string with `.` (`toDisplayString()`) instead of the unscaled alphanumeric storage image (`getUnscaledAbsoluteString()`).

---

## 9. Recommended Technical Fix (For Future Implementation)

1. In `modernize/native_generator.py` (within `visit_StringStatement` / string operand translation):
   When a sending operand is a `CobolNumeric` or has PIC with `V`, generate:
   `customer_balance.getUnscaledAbsoluteString(spec.digits)` or `new String(customer_balance.toStorageImage(), StandardCharsets.ISO_8859_1)`
   rather than `String.valueOf(customer_balance)`.
2. Ensure sequential text file writers normalize line-ending behavior to match target platform file definitions (`\n` vs `\r\n`).

### Regression Risk
- **Very Low:** Affects only string concatenation of numeric fields with implied decimals (`V`) inside `STRING` statements, restoring strict ANSI/ISO COBOL standard behavior.
