> [!NOTE]
> **HISTORICAL ARCHIVE — NOT CURRENT SOURCE OF TRUTH**  
> This document is preserved for historical provenance and audit trail purposes only. Refer to [`DOCUMENTATION_INDEX.md`](../../../DOCUMENTATION_INDEX.md) for the authoritative active documentation set.

---

# Gate 2 Executive Forensic Summary

## WHAT WORKS
- Automatic ingestion, AST parsing, and SemanticIR extraction from COBOL programs.
- GnuCOBOL baseline capture inside isolated Docker containers (`gnucobol-ocesql` and `opensourcecobol4j`).
- Stage-1 transpiled Java compilation and execution with `libcobj.jar`.
- Gate 1 byte-level equivalence validation (verified exact on Golden Repositories #1 and #2).
- Native Spring Boot project scaffolding and compilation via Maven (`mvn clean package -DskipTests`).
- Runtime dependency auditing ensuring 0 forbidden `libcobj`/`jp.osscons` references in generated native code.
- Dynamic port allocation starting from 8082 upward.
- Real AST mutation testing with 6 injected mutations enforcing fail-closed sensitivity.
- UI workbench on port 8788 streaming live migration logs and certification scores.
- Implied-decimal (PIC V) storage image translation in COBOL `STRING` statements.

## WHAT IS VERIFIED
- **Golden Repository #1 (`mentor_cobol_golden_repo.zip` - GOLDENPAY):**
  - COBOL Baseline == Stage-1 Java == Stage-2 Native Java (32 bytes, exact SHA-256 match `aa752eea4445308ea4ad065b337c1cfc285d3e1f8cdce2e2ebcc1cd90c3c08ad`).
  - Gate 1: **PASS**
  - Gate 2: **PASS**
  - Negative Equivalence: **PASS** (6/6 mutations caught).
- **Line-sequential LF line ending preservation (`\n`)** across platforms.

## WHAT IS PARTIALLY WORKING
- **Golden Repository #2 (`mentor_cobol_test_repo_02.zip` - INVENTORY01):**
  - Gate 1: **PASS** (88 bytes, exact SHA-256 match `4127a31798f6bae5c4785148cd4c1e447c0382ad60fd2b8955111760f986c251`).
  - Gate 2: **FAIL** due to fixed-length padded string comparison in `EVALUATE` statement (`STOCKED` vs `CHECK`).
- **Database state comparison:** Functional for SQLite/PostgreSQL/H2, but hardcodes `CUST_ID`/`CUST_NAME` for raw SQL script parsing.
- **Flat-file input staging:** Only copies `data/in/`, omitting custom directories like `data/source/` or `inputs/`.

## BUGS
1. **G2-BUG-01 (P0):** `modernize/native_generator.py` generates `Objects.equals(item_status, "ACTIVE")` for fixed-length padded alphanumeric fields (`PIC X(10)` value `"ACTIVE    "`), causing false comparison results in Java.
2. **G2-BUG-02 (P1):** `cobol_migrate.py` line 4839 hardcodes `CUST_ID` and `CUST_NAME` when parsing raw SQL tables in `_run_db_state_comparison`.
3. **G2-BUG-03 (P2):** `cobol_migrate.py` only discovers SQL files in `repo/data/*.sql`, failing to check `repo/sql/*.sql`.
4. **G2-BUG-04 (P2):** `cobol_migrate.py` lines 5851-5853 writes `traceability_manifest.json` to `os.path.dirname(self.out)/generated`, dirtying the workspace root.

## GAPS
1. **G2-GAP-01 (P1):** `stage_validate` only copies `repo/data/in/` to `mod_dir/data/in/`, missing other input directories (`data/source/`, `data/input/`, etc.).
2. **G2-GAP-02 (P1):** `extract_raw_layout` only parses `RAW-*` prefixed fields and hardcoded names, leaving generic COBOL 01 flat-file records unmapped.
3. **G2-GAP-03 (P2):** `_normalize_text` strips trailing whitespace, which can mask trailing column truncation in fixed-width `FB 80` sequential files.

## LIMITATIONS
1. **G2-LIM-01 (P2):** Generic batch completion detection relies on log sentinel scraping `and the following status: [COMPLETED]` with a 120-second timeout ceiling.
2. **G2-LIM-02 (P2):** Real IBM DB2 z/OS / LUW validation requires explicit environment activation (`REAL_DB2_MODE=1`) and live credentials, defaulting to H2 emulation otherwise.

## MOCKS
- `MockSqlService.java` is generated as a fallback when database connectivity is simulated. Any execution relying on `MockSqlService` must fail-closed from full production certification.

## UNPROVEN
- Live IBM DB2 z/OS mainframe connectivity and real DB2 transaction commit/rollback under high concurrency (requires external mainframe/z/OS hardware).

## P0 FIXES
- **Fix G2-BUG-01:** Implement COBOL-compliant string equality comparison (trimming or space-padding up to length) in `modernize/native_generator.py` so fixed-length alphanumeric `EVALUATE` and `IF` statements evaluate identically in Java.

## P1 FIXES
- **Fix G2-BUG-02:** Replace hardcoded `CUST_ID`/`CUST_NAME` extraction in `_run_db_state_comparison` with dynamic column extraction from SQL statements.
- **Fix G2-GAP-01:** Recursively mirror all non-output data directories (`data/in`, `data/source`, `data/input`, `inputs/`) to `modernized/data/`.
- **Fix G2-GAP-02:** Implement generic AST-driven flat-file layout extraction for Spring Batch readers.
- **Fix G2-CI-01:** Include Gate 2 non-bypass tests in the CI fast-lane pipeline.

## P2 FIXES
- **Fix G2-BUG-03:** Scan both `repo/data/` and `repo/sql/` for SQL schemas.
- **Fix G2-BUG-04:** Restrict `traceability_manifest.json` emission strictly within `self.out`.
- **Fix G2-GAP-03:** Support strict byte/record-length comparison for fixed-length line-sequential files.
- **Fix G2-DOC-01:** Align documentation claims with actual generic batch input resolution requirements.

---

## MENTOR TASK STATUS
**PARTIALLY VERIFIED**
- Golden Repository #1 is 100% verified end-to-end (COBOL == Stage-1 Java == Stage-2 Native Java, Gate 1 PASS, Gate 2 PASS).
- Golden Repository #2 reproduces a specific COBOL fixed-length string evaluation defect (`G2-BUG-01`), accurately diagnosed and documented.

---

## GATE 2 STATUS
**PARTIALLY WORKING**
- The Gate 2 validation pipeline correctly executes, compiles, launches, monitors, compares outputs, verifies databases, and detects mutations.
- Defect detection is actively functioning (demonstrating true fail-closed integrity by catching the `INVENTORY01` mismatch).

---

## PRODUCTION READINESS
**PARTIAL**
- Golden Repository #1 is production-grade.
- Full generic production readiness requires resolving P0 (String evaluation semantics) and P1 (SQL parsing & input directory discovery) items.
