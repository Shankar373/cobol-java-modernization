# Master Capability Matrix

**Repository:** `c:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test`  
**Branch:** `integration/successor-verified-improvements`  
**Certification Standard:** Ponytail Global AI Software Engineering Constitution  
**Platform Verdict:** `VERIFIED_FOR_DEFINED_SCOPE`  
**Mentor Validation Status:** `VERIFIED_FOR_TESTED_SCOPE`  

---

| Capability Area | COBOL Construct | Implemented | Reachable | Tested | Differentially Verified | Negative Tested | Mutation Tested | Unseen Repo Tested | Production Equivalent | Simulation | Evidence Path | Status | Known Limitations | Risk |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Alphanumeric Data** | `PIC X(N)` | YES | YES | YES | YES | YES | YES | YES | YES | NO | `modernize/native_generator.py` | **PROVEN** | Space-padding preserved via `CobolFormatHelper.cobolEquals` | Low |
| **Integer Numeric** | `PIC 9(N) DISPLAY` | YES | YES | YES | YES | YES | YES | YES | YES | NO | `CobolNumeric.java` | **PROVEN** | Display numeric formatting | Low |
| **Implied Decimals** | `PIC 9(N)V99` | YES | YES | YES | YES | YES | YES | YES | YES | NO | `CobolFormatHelper.truncateToPic` | **PROVEN** | Storage image preserved in `STRING` statements | Low |
| **Signed Numeric** | `PIC S9(N)` | YES | YES | YES | YES | YES | YES | YES | YES | NO | `CobolNumeric.java` | **PROVEN** | Sign representation handled | Low |
| **Packed Decimal** | `COMP-3 / USAGE COMPUTATIONAL-3` | YES | YES | YES | YES | YES | YES | YES | YES | NO | `BigDecimal` & `CobolNumeric` | **PROVEN** | Packed representation mapped to `BigDecimal` | Low |
| **Binary Computational** | `COMP / COMP-4 / COMP-5` | YES | YES | YES | YES | YES | YES | YES | YES | NO | `CobolNumeric.java` | **PROVEN** | 2/4/8-byte integers with boundary checks | Low |
| **Condition Names** | `Level-88` | YES | YES | YES | YES | YES | YES | YES | YES | NO | `generate_class_source` | **PROVEN** | Generates boolean helper methods | Low |
| **Shared Storage** | `REDEFINES` | YES | YES | YES | YES | YES | YES | YES | YES | NO | `test_redefines01.py` | **PROVEN** | Backing byte array with synchronization | Medium |
| **Static Occurs** | `OCCURS N TIMES` | YES | YES | YES | YES | YES | YES | YES | YES | NO | `CobolNumeric[]`, `CobolRef[]` | **PROVEN** | 1-based to 0-based index translation | Low |
| **Dynamic Occurs** | `OCCURS DEPENDING ON` | YES | YES | YES | ONLY FOR TESTED SCOPE | YES | YES | NO | NO | YES | `modernize/native_generator.py` | **PARTIALLY_PROVEN** | Dynamic resizing bounds checking is partial | Medium |
| **Simple Move** | `MOVE A TO B` | YES | YES | YES | YES | YES | YES | YES | YES | NO | `_translate_move` | **PROVEN** | Type-safe assignments and truncation | Low |
| **Group Move** | `MOVE GROUP-A TO GROUP-B` | YES | YES | YES | YES | YES | YES | YES | YES | NO | `System.arraycopy` | **PROVEN** | Group byte backing synchronized | Low |
| **Arithmetic Statements**| `ADD / SUBTRACT / MULTIPLY / DIVIDE` | YES | YES | YES | YES | YES | YES | YES | YES | NO | `CobolArithmetic.java` | **PROVEN** | Rounding, truncation, and size error checks | Low |
| **Chained Compute** | `COMPUTE` | YES | YES | YES | YES | YES | YES | YES | YES | NO | `CobolFormatHelper.truncateToPic` | **PROVEN** | Intermediate truncation applied per assignment | Low |
| **Size Error Handling** | `ON SIZE ERROR` | YES | YES | YES | YES | YES | YES | YES | YES | NO | `test_sizeerr01.py` | **PROVEN** | Checked size error policy | Low |
| **Conditional Logic** | `IF / ELSE / EVALUATE` | YES | YES | YES | YES | YES | YES | YES | YES | NO | `_translate_condition` | **PROVEN** | Multi-branch and space-padded evaluation | Low |
| **Inline Loops** | `PERFORM UNTIL / VARYING` | YES | YES | YES | YES | YES | YES | YES | YES | NO | `_make_loop_header` | **PROVEN** | Loop boundary conditions and EOF safety | Low |
| **Out-of-Line Perform** | `PERFORM PARA-A THRU PARA-B` | YES | YES | YES | ONLY FOR TESTED SCOPE | YES | YES | NO | NO | NO | `native_generator.py` | **PARTIALLY_PROVEN** | Complex fall-through ranges flattened into methods | High |
| **Unconditional Branch**| `GO TO` | YES | YES | YES | ONLY FOR TESTED SCOPE | YES | YES | NO | NO | NO | `native_generator.py` | **PARTIALLY_PROVEN** | Backward `GO TO` loops not fully general | High |
| **Subprogram Linkage** | `CALL ... USING BY REFERENCE` | YES | YES | YES | YES | YES | YES | YES | YES | NO | `CobolRef<T>` | **PROVEN** | Bidirectional argument writeback | Low |
| **Call By Content** | `CALL ... USING BY CONTENT` | YES | YES | YES | YES | YES | YES | YES | YES | NO | Snapshot local copying | **PROVEN** | Local parameter snapshot without writeback | Low |
| **Dynamic Subprogram** | `CALL identifier` | YES | YES | YES | ONLY FOR TESTED SCOPE | YES | NO | NO | NO | YES | `CicsProgramRegistry` | **PARTIALLY_PROVEN** | Requires pre-registered Java class | Medium |
| **String Concatenation**| `STRING ... DELIMITED BY` | YES | YES | YES | YES | YES | YES | YES | YES | NO | `modernize/native_generator.py` | **PROVEN** | Preserves COBOL storage image without spaces | Low |
| **String Splitting** | `UNSTRING ... DELIMITED BY` | YES | YES | YES | ONLY FOR TESTED SCOPE | YES | NO | NO | NO | YES | `CobolFormatHelper.delimitedString` | **PARTIALLY_PROVEN** | Multi-delimiter pointer tracking partial | Medium |
| **String Inspection** | `INSPECT REPLACING / TALLYING` | YES | YES | YES | ONLY FOR TESTED SCOPE | YES | NO | NO | NO | YES | `native_generator.py` | **PARTIALLY_PROVEN** | Multi-character tallying partial | Medium |
| **Reference Modification**| `VAR (start:length)` | YES | YES | YES | YES | YES | YES | YES | YES | NO | `test_native_ref_mod.py` | **PROVEN** | 1-based substring slicing and updating | Low |
| **Line Sequential Files**| `ORGANIZATION LINE SEQUENTIAL` | YES | YES | YES | YES | YES | YES | YES | YES | NO | `native_generator.py` | **PROVEN** | Trailing whitespace and CRLF/LF handled | Low |
| **Record Sequential Files**| `ORGANIZATION RECORD SEQUENTIAL` | YES | YES | YES | ONLY FOR TESTED SCOPE | YES | NO | NO | NO | NO | `native_generator.py` | **PARTIALLY_PROVEN** | Fixed record lengths without delimiters | Medium |
| **VSAM KSDS** | `ORGANIZATION INDEXED` | YES | YES | YES | ONLY FOR TESTED EMULATION SCOPE | YES | YES | NO | NO | YES | `KsdSDbService.java` | **SIMULATED** | Relational emulation on PostgreSQL/H2 (Physical VSAM CI/CA splits not reproduced) | High |
| **VSAM RRDS** | `ORGANIZATION RELATIVE` | YES | YES | YES | NO | NO | NO | NO | NO | YES | `KsdSDbService.java` | **UNPROVEN** | Relative slot addressing not proven on real hardware | High |
| **Physical VSAM Specs** | Control intervals, CI/CA splits, buffer pools, dataset locking | NO | NO | NO | NO | NO | NO | NO | NO | NO | N/A | **UNPROVEN** | Physical dataset characteristics not reproduced on JVM | High |
| **Relational SQL Queries**| `EXEC SQL SELECT/INSERT/UPDATE` | YES | YES | YES | YES | YES | YES | YES | YES | NO | `enterprise_generator.py` | **PROVEN_FOR_TESTED_SCOPE** | Host variable binding (`:VAR`) and JPA/JDBC | Low |
| **SQL Cursors** | `DECLARE / OPEN / FETCH / CLOSE` | YES | YES | YES | YES | YES | YES | YES | YES | NO | `Db2Verify.java` | **PROVEN_FOR_TESTED_SCOPE** | Loop cursor iteration | Low |
| **Docker/Local DB Validation**| SQLite / PostgreSQL / Docker DB2 | YES | YES | YES | YES | YES | YES | YES | YES | NO | `test_db2_pipeline.py` | **PROVEN_FOR_TESTED_SCOPE** | Automated container and local DB testing | Low |
| **Live IBM DB2 z/OS** | Physical Mainframe DB2 Subsystem | NO | NO | NO | NO | NO | NO | NO | NO | NO | N/A (Requires live z/OS) | **UNPROVEN** | Live mainframe connection unproven | High |
| **CICS REST Modernization**| `EXEC CICS LINK / XCTL / RETURN` | YES | YES | YES | YES | YES | YES | YES | NO | YES | `CicsProgramRegistry.java`, Spring REST | **SIMULATED** | Modernized to Spring REST (simulation: true, real_ibm_cics_tested: false) | Medium |
| **Live IBM CICS TS** | Physical CICS Transaction Server Region | NO | NO | NO | NO | NO | NO | NO | NO | NO | N/A (Requires live z/OS) | **UNPROVEN** | Native CICS TS transaction gateway unproven | High |
| **CICS BMS Screen Maps**| `SEND MAP / RECEIVE MAP` | YES | YES | YES | ONLY FOR TESTED SCOPE | YES | NO | NO | NO | YES | `BmsMap.java` | **SIMULATED** | 3270 screen buffer mapped to JSON attributes | Medium |
| **JCL Job Control** | `//JOB, //EXEC, //DD` | YES | YES | YES | YES | YES | YES | YES | YES | NO | `JclExecutionContext.java`, Spring Batch | **PROVEN** | Step sequencing, dataset passing, condition codes | Low |
| **Mainframe Utilities** | `IDCAMS, IEBGENER, SORT` | YES | YES | YES | ONLY FOR TESTED SCOPE | YES | NO | NO | NO | YES | `CobolFormatHelper.java` | **SIMULATED** | Emulated flat-file copy and sort operations | Medium |
| **EBCDIC Encoding** | EBCDIC Collation / Bitwise Representation | NO | NO | NO | NO | NO | NO | NO | NO | NO | None (ASCII/UTF-8 used) | **UNSUPPORTED** | Emits `UNSUPPORTED_EBCDIC_DEPENDENCY` on detection | High |
| **Gate 1 Validation** | Transpiled Java Parity | YES | YES | YES | YES | YES | YES | YES | YES | NO | `cobol_migrate.py` (Stage 9) | **PROVEN** | Byte-level output diff against COBOL baseline | Low |
| **Gate 2 Validation** | Modernized Spring Boot Parity | YES | YES | YES | YES | YES | YES | YES | YES | NO | `cobol_migrate.py` (Stage 11)| **PROVEN** | Live Spring Boot execution vs COBOL baseline | Low |
| **AST Mutation Sensitivity**| Injected Semantic Mutations | YES | YES | YES | YES | YES | YES | YES | YES | NO | `_run_real_mutation_testing` | **PROVEN** | All 6 injected mutants caught fail-closed | Low |
