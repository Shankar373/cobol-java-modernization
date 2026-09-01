# Gate 2 Remediation & Fix Report

## Overview
This document details the exact root causes, code changes, and test verification results for all issues resolved in Gate 2.

---

### 1. G2-BUG-01: Fixed-Length COBOL String Equality Semantics (P0)
- **Root Cause:** In COBOL, comparisons between alphanumeric fields (`PIC X(N)`) follow standard space-padding semantics: if operands are unequal in length, the shorter operand is padded on the right with spaces. In Java, `Objects.equals("ACTIVE    ", "ACTIVE")` evaluates to `false`, causing `EVALUATE` and `IF` statements in `INVENTORY01` to mistakenly execute fallback branches.
- **Affected Files:**
  - `modernize/java_helpers/CobolFormatHelper.java`: Added `public static boolean cobolEquals(String a, String b)`.
  - `modernize/native_generator.py`: Updated `_build_single_when_condition`, `_translate_condition`, and Level-88 method generator to invoke `CobolFormatHelper.cobolEquals`.
- **Verification:**
  - `tests/test_cobol_string_semantics.py` (all 3 unit tests passed).
  - Golden Repository #2 (`mentor_cobol_test_repo_02.zip` - `INVENTORY01`): Gate 2 changed from **FAIL** to **PASS** (exact 88-byte match `4127a31798f6bae5c4785148cd4c1e447c0382ad60fd2b8955111760f986c251`).

---

### 2. G2-GAP-01: Generic Input Directory Staging (P1)
- **Root Cause:** `stage_validate` in `cobol_migrate.py` previously only copied `repo/data/in/`, causing failures on repositories using `data/source/`, `data/input/`, `inputs/`, or `datasets/`.
- **Affected Files:** `cobol_migrate.py` (`stage_validate` lines 5088–5115).
- **Fix:** Recursively copies all input directories while explicitly skipping output/work/db directories (`data/out`, `data/work`, `.git`, `.db`).

---

### 3. G2-GAP-02: Generic COBOL Record Layout Extraction (P1)
- **Root Cause:** `extract_raw_layout` only parsed fields matching `RAW-*` against a hardcoded dictionary (`RAW_NAME_MAP`), causing 0 fields to be mapped for generic COBOL records.
- **Affected Files:** `cobol_migrate.py` (`extract_raw_layout` & `_calculate_pic_length`).
- **Fix:** Implemented AST-driven elementary item parser for arbitrary 01/05/10 levels, automatically computing field lengths from PICTURE clauses (e.g. `9(6)`, `X(20)`, `9(5)V99`).

---

### 4. G2-BUG-02 & G2-BUG-03: Dynamic DB State Comparison & SQL Discovery (P1/P2)
- **Root Cause:** Line 4839 hardcoded column names `{"CUST_ID": ..., "CUST_NAME": ...}` and only searched `repo/data/*.sql`.
- **Affected Files:** `cobol_migrate.py` (`_run_db_state_comparison`).
- **Fix:** Expanded search to `repo/data/`, `repo/sql/`, and `repo/database/`, dynamically deriving column names from `CREATE TABLE` / `INSERT INTO` statements.

---

### 5. G2-BUG-04: Traceability Manifest Output Containment (P2)
- **Root Cause:** Lines 5851–5853 wrote `traceability_manifest.json` to `os.path.dirname(self.out)/generated`, dirtying the workspace root.
- **Affected Files:** `cobol_migrate.py` (`stage_report`).
- **Fix:** Restricted all manifest output writes strictly inside `self.out`.

---

### 6. G2-GAP-03: Fixed-Width Record Line Normalization (P2)
- **Root Cause:** `_normalize_text` stripped trailing whitespace from every line, masking fixed-width record truncation.
- **Affected Files:** `cobol_migrate.py` (`_normalize_text`).
- **Fix:** Preserved trailing spaces on each record line while strictly normalizing line endings (`\r\n` -> `\n`).

---

## Direct Validation Evidence

| Test Suite / Target | Command | Result |
|---|---|---|
| **String Semantics Tests** | `pytest tests/test_cobol_string_semantics.py` | **3/3 PASSED** |
| **PIC V Semantics Tests** | `pytest tests/test_pic_v_string_semantics.py` | **3/3 PASSED** |
| **Fail-Closed Gate 2 Test** | `pytest tests/test_validation_nobypass.py` | **1/1 PASSED** (Fail-closed on mismatch) |
| **Golden Repo #1 (GOLDENPAY)** | `python cobol_migrate.py --repo ...golden_repo...` | **Gate 1: PASS, Gate 2: PASS** (32 bytes exact) |
| **Golden Repo #2 (INVENTORY01)**| `python cobol_migrate.py --repo ...test_repo_02...`| **Gate 1: PASS, Gate 2: PASS** (88 bytes exact) |
