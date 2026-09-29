# Master Limitations Register

**Repository:** `c:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test`  
**Branch:** `integration/successor-verified-improvements`  
**Certification Standard:** Ponytail Global AI Software Engineering Constitution  
**Platform Verdict:** `VERIFIED_FOR_DEFINED_SCOPE`  
**Mentor Validation Status:** `VERIFIED_FOR_TESTED_SCOPE`  

> **Scope note:** the executable transformation is deterministic
> (`modernize/lexer.py` → `modernize/parser.py` → `modernize/semantic_ir.py` →
> `modernize/native_generator.py`) with no LLM anywhere. OpenSource COBOL 4J
> (`cobj` + `libcobj.jar`) is implemented only as the Track-A/Gate-1
> verification oracle; `z390`/`Hercules`/`ICU4J` are test-only reference
> oracles. `modernize/capability_matrix.py` governs per-construct evidence;
> `PHASE_2_*` target-design items remain planned unless an implementation
> report names a landed `modernize_v2/` module.

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
- **Out-of-Line PERFORM THRU / THROUGH:** Contiguous paragraph ranges generate sequential execution; `EXIT PARAGRAPH` inside the range and non-contiguous ranges are not differentially verified (`PROC.PERFORM_THRU` = `UNIT_TESTED`).
- **Unconditional GO TO:** Forward jumps parse and generate; `GO TO DEPENDING ON` is unsupported and in-range jumps are not differentially verified (`PROC.GO_TO` = `UNIT_TESTED`).
- **Dynamic Subprogram CALL identifier:** Dispatched against registered program classes with diagnostics for unknown targets; no differential fixture (`PROC.CALL_DYNAMIC` = `GENERATED_ONLY`).
- **Dynamic Array Sizing (`OCCURS DEPENDING ON`):** Generated with bounds helpers but no differential fixture (`OCCURS.DEPENDING_ON` = `GENERATED_ONLY`).
- **String Splitting (`UNSTRING`):** Multi-character delimiters, pointer tracking, and tallying counters generate; no differential fixture (`STRING.UNSTRING_STMT` = `UNIT_TESTED`).
- **String Inspection (`INSPECT`):** `REPLACING ALL/LEADING`, `TALLYING`, and `CONVERTING` generate; no differential fixture (`STRING.INSPECT` = `UNIT_TESTED`).
- **EBCDIC Charset & Collation (tools only):** CP037, CP1047, CP500, CP273, and CP1140 byte transcoding and collation strategy are unit-tested in `tools/reference_runtimes/ebcdic/`; generated Java uses ASCII/Unicode collation and the file I/O path has no EBCDIC codec (`FILE.SEQUENTIAL_EBCDIC` = `UNSUPPORTED`).
- **Linkage Conventions:** `CALL ... USING BY REFERENCE` (bidirectional writeback via `CobolRef<T>`) and `BY CONTENT` (snapshot local copying) parse and generate (`UNIT_TESTED`); only `BY CONTENT` has a differential fixture.
- **Embedded SQL Translation:** Static host variable replacement (`:VAR`), JPA entity mapping, and basic CRUD operations parse and generate (`SQL.*` = `UNIT_TESTED`, emulated); not differentially verified against a GnuCOBOL baseline.
- **Gate 1 Differential Verification:** Transpiled Java byte-level differential verification against GnuCOBOL Docker baseline.
- **Gate 2 Live Validation:** Native Spring Boot application packaging and runtime verification against baseline outputs.
- **AST Mutation Sensitivity:** Injected AST mutation suite fail-closed enforcement.

---

## 2. PARTIALLY_PROVEN (Partially Implemented / Scope Restricted)
- **Arbitrary Spaghetti GO TO:** Unstructured non-local jumps across deeply nested sections require restructuring into clean control flow.
- **Variable-Length Binary Records (`RECORDING MODE V`):** Variable-length record descriptor words (RDW) are partially supported.
- **Fixed-Length Record Sequential (`ORGANIZATION RECORD SEQUENTIAL`):** Generates but record-boundary enforcement is not differentially verified (`FILE.SEQUENTIAL_FIXED` = `UNIT_TESTED`).
- **Group `MOVE`:** Treated as byte copy; byte-exact differential parity not verified (`MOVE.GROUP_TO_GROUP` = `UNIT_TESTED`).

---

## 3. SIMULATED (Emulated via Modern Cloud Frameworks)
- **VSAM Indexed Storage (KSDS):** VSAM KSDS indexed operations (`START`, `READ NEXT`, `KEY IS >=`) are emulated via relational database queries in `KsdSDbService.java` using PostgreSQL/H2 tables rather than physical ISAM files. Control intervals, CI/CA splits, and physical locking are not reproduced.
- **VSAM Relative Storage (RRDS):** VSAM RRDS relative record operations (1-based relative record number, random slot access, delete, rewrite, status codes 00, 22, 23, 24) are simulated via relational tables (`key_col = RRN`) and memory stores. Physical RRDS slots on DASD are not reproduced.
- **CICS Transaction Subsystem:** `EXEC CICS LINK`, `XCTL`, and `RETURN` parse into IR but generate stubs/diagnostics only (`CICS.*` = `PARSED_ONLY`); modernization direction is Spring REST controllers and `CicsProgramRegistry` in-memory COMMAREA dispatchers rather than IBM CICS TS (`simulation: true`, `real_ibm_cics_tested: false`).
- **CICS BMS Screen Maps:** 3270 data stream mapping (`SEND MAP`, `RECEIVE MAP`) parses into IR but generates stubs only (`CICS.SEND_MAP`/`CICS.RECEIVE_MAP` = `PARSED_ONLY`); modernization direction is `BmsMap.java` JSON attribute models.
- **Mainframe Batch Utilities:** JCL utilities like `IDCAMS`, `IEBGENER`, and `SORT` are emulated in Java via `CobolFormatHelper.java` file operations.

---

## 4. UNSUPPORTED (Explicitly Not Implemented)
- **Altered `GO TO` (`ALTER PARA-A TO PROCEED TO PARA-B`):** Deprecated self-modifying COBOL flow control is not supported.
- **`CORRESPONDING` Phrase on Group Moves:** `MOVE CORRESPONDING GROUP-A TO GROUP-B` is not automatically expanded by the parser.
- **Report Writer Division:** `REPORT SECTION` and `GENERATE` statements are not parsed into Spring Batch reports.
- **Debugging Lines (`D` in Column 7):** Debug lines are stripped during ingestion.

---

## 5. UNPROVEN (Requires Physical Mainframe Hardware / External Infrastructure)
- **Live IBM DB2 z/OS Subsystem:** Real DB2 commit/rollback, two-phase commit, table lock escalations, and DB2-specific catalog tables require an active IBM mainframe or remote DB2 LUW connection (`REAL_DB2_MODE=1`). Standard pipeline runs utilize H2/PostgreSQL/Docker DB2 emulation and are marked `UNPROVEN` on live mainframe DB2. Fail-closed status is maintained via `RealDb2ZosAdapter`.
- **Live IBM CICS Transaction Server Region:** Physical CICS TS execution via IBM EXCI or IPIC connection requires live IBM mainframe hardware. Standard runs utilize in-memory simulation and are marked `UNPROVEN`. Fail-closed status is maintained via `RealCicsTsReferenceAdapter`.
- **Physical VSAM Characteristics:** Physical control intervals, CI/CA splits, buffer pools, dataset locking, and low-level DASD layouts are not reproduced on cloud JVM runtimes.
- **Native Mainframe EBCDIC Hardware Semantics:** Byte-level native DASD binary representation and hardware instruction collation remain unproven on standard ASCII/UTF-8 JVM runtimes.
- **Real IBM CICS TS Region:** Execution within a real IBM CICS Transaction Server region is unproven unless connected to external mainframe infrastructure.
- **High-Concurrency Mainframe Workloads:** High-throughput simultaneous execution (thousands of TPS) across distributed Spring Batch instances is unproven locally.
