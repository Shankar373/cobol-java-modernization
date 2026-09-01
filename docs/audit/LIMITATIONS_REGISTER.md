# Master Limitations Register

**Repository:** `c:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test`  
**Branch:** `integration/successor-verified-improvements`  
**Certification Standard:** Ponytail Global AI Software Engineering Constitution  
**Platform Verdict:** `VERIFIED_FOR_DEFINED_SCOPE`  
**Mentor Validation Status:** `VERIFIED_FOR_TESTED_SCOPE`  

---

## 1. PROVEN (Production-Grade & Fully Verified for Tested Scope)
- **Core Procedural COBOL:** Full support for `IDENTIFICATION`, `ENVIRONMENT`, `DATA`, and `PROCEDURE` divisions.
- **Elementary Data Types:** `PIC X(N)`, `PIC 9(N)`, `PIC S9(N)` display representations.
- **Implied Decimals:** `PIC 9(N)V99` storage images, scaled conversions, and intermediate truncation in arithmetic.
- **Packed Decimal:** `COMP-3` / `COMPUTATIONAL-3` high-precision arithmetic via `BigDecimal` and `CobolNumeric`.
- **Binary Data:** `COMP` / `COMP-4` / `COMP-5` 2-, 4-, and 8-byte integers with boundary and size error checking.
- **Relational Conditions:** Space-padded alphanumeric comparison via `CobolFormatHelper.cobolEquals`.
- **Level-88 Condition Names:** Generated type-safe boolean helper methods.
- **Shared Storage (`REDEFINES`):** Byte-level backing arrays with synchronized getter/setter slices.
- **Group Operations:** `MOVE` on group records with synchronized byte arrays via `System.arraycopy`.
- **Reference Modification:** `VAR (offset:length)` 1-based substring slicing and assignments.
- **Line Sequential File I/O:** `ORGANIZATION LINE SEQUENTIAL` read and write with cross-platform CRLF/LF normalization and trailing whitespace handling.
- **Linkage Conventions:** `CALL ... USING BY REFERENCE` (bidirectional writeback via `CobolRef<T>`) and `BY CONTENT` (snapshot local copying).
- **Embedded SQL Translation:** Static host variable replacement (`:VAR`), JPA entity mapping, and basic CRUD operations.
- **Gate 1 Differential Verification:** Transpiled Java byte-level differential verification against GnuCOBOL Docker baseline.
- **Gate 2 Live Validation:** Native Spring Boot application packaging and runtime verification against baseline outputs.
- **AST Mutation Sensitivity:** Injected AST mutation suite fail-closed enforcement.

---

## 2. PARTIALLY_PROVEN (Partially Implemented / Scope Restricted)
- **Out-of-Line PERFORM THRU:** `PERFORM PARA-A THRU PARA-B` works for contiguous sequential paragraphs; complex non-sequential overlapping ranges are flattened into simple method calls without full call-stack modeling.
- **Unconditional `GO TO` Branching:** Forward `GO TO` within paragraphs is converted to structured control flow; arbitrary spaghetti `GO TO` jumping between unrelated sections is unsupported.
- **Dynamic Array Sizing (`OCCURS DEPENDING ON`):** Array allocation uses the maximum bound; dynamic resizing and length truncation on runtime change is only partially bounded.
- **Complex `UNSTRING` with Multiple Delimiters:** Basic single-character delimiters are supported; `COUNT IN`, `DELIMITER IN`, and multiple `OR` delimiters have incomplete pointer updates.
- **`INSPECT` with Complex Tallying:** `INSPECT REPLACING ALL` is supported; complex `TALLYING FOR LEADING` or `BEFORE/AFTER INITIAL` is partially implemented.
- **Fixed-Width Binary/Record Sequential Files:** Raw binary sequential records without newlines are supported when exact record length is known; variable-length binary records (`RECORDING MODE V`) are partial.

---

## 3. SIMULATED (Emulated via Modern Cloud Frameworks)
- **VSAM Indexed Storage (KSDS):** VSAM KSDS indexed operations (`START`, `READ NEXT`, `KEY IS >=`) are emulated via relational database queries in `KsdSDbService.java` using PostgreSQL/H2 tables rather than physical ISAM files. Control intervals, CI/CA splits, and physical locking are not reproduced.
- **CICS Transaction Subsystem:** `EXEC CICS LINK`, `XCTL`, and `RETURN` are simulated via Spring REST controllers and `CicsProgramRegistry` in-memory COMMAREA dispatchers rather than IBM CICS TS (`simulation: true`, `real_ibm_cics_tested: false`).
- **CICS BMS Screen Maps:** 3270 data stream mapping (`SEND MAP`, `RECEIVE MAP`) is simulated via `BmsMap.java` JSON attribute models.
- **Mainframe Batch Utilities:** JCL utilities like `IDCAMS`, `IEBGENER`, and `SORT` are emulated in Java via `CobolFormatHelper.java` file operations.

---

## 4. UNSUPPORTED (Explicitly Not Implemented)
- **Native EBCDIC Character Set:** Collating sequence (where lowercase letters precede uppercase and numbers follow letters) is not native; the JVM operates in ASCII/UTF-8. Emits `UNSUPPORTED_EBCDIC_DEPENDENCY` on detection.
- **Altered `GO TO` (`ALTER PARA-A TO PROCEED TO PARA-B`):** Deprecated self-modifying COBOL flow control is not supported.
- **`CORRESPONDING` Phrase on Group Moves:** `MOVE CORRESPONDING GROUP-A TO GROUP-B` is not automatically expanded by the parser.
- **Report Writer Division:** `REPORT SECTION` and `GENERATE` statements are not parsed into Spring Batch reports.
- **Debugging Lines (`D` in Column 7):** Debug lines are stripped during ingestion.

---

## 5. UNPROVEN (Requires Physical Mainframe Hardware / External Infrastructure)
- **Live IBM DB2 z/OS Subsystem:** Real DB2 commit/rollback, two-phase commit, table lock escalations, and DB2-specific catalog tables require an active IBM mainframe or remote DB2 LUW connection (`REAL_DB2_MODE=1`). Standard pipeline runs utilize H2/PostgreSQL/Docker DB2 emulation and are marked `UNPROVEN` on live mainframe DB2.
- **Physical VSAM Characteristics:** Physical control intervals, VSAM dataset locking, and low-level dataset behavior are not reproduced on cloud JVM runtimes.
- **Real IBM CICS TS Region:** Execution within a real IBM CICS Transaction Server region is unproven unless connected to external mainframe infrastructure.
- **High-Concurrency Mainframe Workloads:** High-throughput simultaneous execution (thousands of TPS) across distributed Spring Batch instances is unproven locally.
