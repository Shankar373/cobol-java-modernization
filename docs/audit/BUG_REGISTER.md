# Master Bug Register

This register documents all defects, bugs, and behavioral inconsistencies identified during the comprehensive forensic audit of the modernization platform.

---

### BUG-01: Alphanumeric Fixed-Length Comparison in Java (RESOLVED IN GATE 2)
- **BUG-ID:** `BUG-01`
- **Severity:** `P0` (Catastrophic / Business Equivalence Failure)
- **Priority:** `P0` (Fixed)
- **Component:** Native Statement Translator / Native Generator
- **File:** `modernize/native_generator.py` (lines 3014, 3016, 3181, 5520) & `modernize/java_helpers/CobolFormatHelper.java`
- **Description:** Fixed-length `PIC X(N)` variables initialized with space padding (e.g. `"ACTIVE    "`) failed string equality checks in Java when compared against string literals (`"ACTIVE"`).
- **Trigger:** Any `EVALUATE <var> WHEN <literal>` or `IF <var> = <literal>` on fixed-length alphanumeric fields.
- **Expected Behavior:** Space-padded COBOL comparison semantics (shorter operand treated as if padded on right with spaces).
- **Actual Behavior:** Java `Objects.equals("ACTIVE    ", "ACTIVE")` evaluated to `false`, executing fallback `WHEN OTHER` branches.
- **Root Cause:** Direct emission of Java standard `Objects.equals` rather than COBOL-compliant space-padded comparison.
- **Evidence:** `INVENTORY01.cob`: Baseline output produced `STOCKED`, Java produced `CHECK`.
- **Affected Workloads:** Any COBOL program evaluating alphanumeric status codes or category flags.
- **Security Impact:** Low (Logic flow error).
- **Data Impact:** High (Wrong branch execution and corrupted report status).
- **Recommended Fix:** Implement `CobolFormatHelper.cobolEquals` and invoke across all condition generators.
- **Regression Test:** `tests/test_cobol_string_semantics.py`, Golden Repo #2.

---

### BUG-02: Spring Batch Sequential EOF Processing / Last Record Loop Duplication (ACTIVE)
- **BUG-ID:** `BUG-02`
- **Severity:** `P1` (Major Functional Defect on Generic File Loops)
- **Priority:** `P1` (High)
- **Component:** Enterprise Batch Generator / Spring Batch ItemReader-Processor Wiring
- **File:** `modernize/enterprise_generator.py` & generated batch processor classes
- **Description:** On unseen sequential flat-file processing (`PERFORM UNTIL WS-EOF = 'Y' READ IN-FILE NOT AT END ... WRITE OUT-REC`), the generated Spring Batch job processes the last record twice upon reaching EOF.
- **Trigger:** Reading sequential files where the COBOL loop relies on `READ ... AT END MOVE 'Y' TO WS-EOF` inside an inline `PERFORM UNTIL`.
- **Expected Behavior:** Exactly N records read and processed (1:1 with input).
- **Actual Behavior:** N+1 records processed with the final item repeated.
- **Root Cause:** In COBOL, `READ ... AT END` skips the `NOT AT END` block when EOF is reached. In Spring Batch, the reader returns `null` on EOF, but the item processor retains previous state or executes an un-guarded final cycle before job completion.
- **Evidence:** `UNSEEN01.cob` baseline produced 2 records (82 B), Gate 2 Spring Boot produced 3 records (84 B with record 1002 repeated).
- **Affected Workloads:** Batch programs with sequential flat-file inputs and inline `READ ... NOT AT END` processing.
- **Security Impact:** Low.
- **Data Impact:** High (Duplicate output record written to destination files).
- **Recommended Fix:** Explicitly synchronize the Spring Batch reader EOF condition with the generated processor's `WS-EOF` flag to skip processing on null input chunks.
- **Regression Test Needed:** `tests/acceptance/test_unseen_sequential_eof_parity.py`.

---

### BUG-03: Hardcoded SQL Table Column Extraction in Database State Comparison (RESOLVED IN GATE 2)
- **BUG-ID:** `BUG-03`
- **Severity:** `P1` (Database State Verification Inaccuracy)
- **Priority:** `P1` (Fixed)
- **Component:** Pipeline DB State Comparator
- **File:** `cobol_migrate.py` (`_run_db_state_comparison` line 4839)
- **Description:** Line 4839 hardcoded column names `{"CUST_ID": ..., "CUST_NAME": ...}` when parsing SQL seed files for baseline DB verification.
- **Trigger:** Any repository with non-customer tables (e.g., `INVENTORY`, `ORDERS`, `DEPT`, `TRANSACTIONS`).
- **Expected Behavior:** Dynamic column extraction from SQL schema and table metadata.
- **Actual Behavior:** Hardcoded column extraction failed for arbitrary database tables.
- **Root Cause:** Legacy fixture-specific assumption left in database verification logic.
- **Evidence:** Audit of `cobol_migrate.py` line 4839.
- **Affected Workloads:** Generic SQL-backed COBOL programs.
- **Security Impact:** Low.
- **Data Impact:** Medium (Database state validation false negatives or failures).
- **Recommended Fix:** Dynamically parse columns from `CREATE TABLE` and `INSERT INTO` statements.
- **Regression Test:** Generic SQL baseline differential test.

---

### BUG-04: Out-of-Workspace Traceability Manifest Emission (RESOLVED IN GATE 2)
- **BUG-ID:** `BUG-04`
- **Severity:** `P2` (Workspace Boundary Pollution)
- **Priority:** `P2` (Fixed)
- **Component:** Pipeline Report Generator
- **File:** `cobol_migrate.py` (`stage_report` lines 5851-5853)
- **Description:** Wrote `traceability_manifest.json` to `os.path.dirname(self.out)/generated`, which wrote to the workspace root when `self.out` was relative.
- **Trigger:** Executing pipeline with top-level or relative `--out target`.
- **Expected Behavior:** All generated output contained strictly within `self.out`.
- **Actual Behavior:** Leaked artifacts into parent directory.
- **Root Cause:** Double-writing path calculation using parent directory.
- **Evidence:** Inspection of `stage_report` lines 5851-5853.
- **Affected Workloads:** CI and multi-tenant test environments.
- **Security Impact:** Low (Directory hygiene).
- **Data Impact:** Low.
- **Recommended Fix:** Confine all manifest and generated writes strictly inside `self.out`.
- **Regression Test:** Path isolation tests.

---

### BUG-05: Missing SQL Files in `repo/sql/` Directory (RESOLVED IN GATE 2)
- **BUG-ID:** `BUG-05`
- **Severity:** `P2` (Schema Discovery Limitation)
- **Priority:** `P2` (Fixed)
- **Component:** Pipeline Ingest & DB Discovery
- **File:** `cobol_migrate.py` (`_run_db_state_comparison`)
- **Description:** Schema discovery only searched `repo/data/*.sql` and missed `repo/sql/*.sql` or `repo/database/*.sql`.
- **Trigger:** Repositories organizing DDL/DML scripts in `sql/` folder.
- **Expected Behavior:** Automatic discovery of all SQL files regardless of directory convention.
- **Actual Behavior:** Fell back to hardcoded table list when `data/` had no SQL files.
- **Root Cause:** Narrow path scanning assumption.
- **Evidence:** `mentor_cobol_golden_repo` placed SQL in `sql/` directory.
- **Affected Workloads:** Repositories using standard `sql/` directory structure.
- **Security Impact:** None.
- **Data Impact:** Low.
- **Recommended Fix:** Scan `data/`, `sql/`, and `database/` recursively.
- **Regression Test:** Multi-directory schema discovery test.

---

### BUG-06: Text Normalizer Trailing Whitespace Stripping (RESOLVED IN GATE 2)
- **BUG-ID:** `BUG-06`
- **Severity:** `P2` (Validation False-Positive Risk)
- **Priority:** `P2` (Fixed)
- **Component:** Pipeline Comparison Engine
- **File:** `cobol_migrate.py` (`_normalize_text` line 5261)
- **Description:** `line.rstrip(" \t\r\n\x00")` stripped intra-line trailing spaces on every record, masking record truncation in fixed-width sequential files.
- **Trigger:** Comparing fixed-width records where trailing spaces represent significant field padding.
- **Expected Behavior:** Normalize line endings (`\r\n` vs `\n`) while preserving field length alignment.
- **Actual Behavior:** Stripped trailing spaces, allowing truncated records to pass comparison.
- **Root Cause:** Over-aggressive whitespace stripping.
- **Evidence:** `_normalize_text` code inspection.
- **Affected Workloads:** Fixed-width sequential file outputs.
- **Security Impact:** None.
- **Data Impact:** Medium (Could mask data truncation).
- **Recommended Fix:** Only replace `\r` and normalize trailing empty lines, preserving per-record column spaces.
- **Regression Test:** `tests/test_pic_v_string_semantics.py`.
