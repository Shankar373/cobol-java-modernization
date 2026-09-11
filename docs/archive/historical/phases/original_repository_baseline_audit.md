> [!NOTE]
> **HISTORICAL ARCHIVE — NOT CURRENT SOURCE OF TRUTH**  
> This document is preserved for historical provenance and audit trail purposes only. Refer to [`DOCUMENTATION_INDEX.md`](../../../DOCUMENTATION_INDEX.md) for the authoritative active documentation set.

---

# Forensic Baseline Audit Report: Original Repository

**Repository:** `https://github.com/Shankar373/cobol-java-modernization`  
**Audit Type:** Pre-Split Zero-Assumption Forensic Baseline Audit  
**Audit Timestamp:** 2026-09-01T20:30:00Z  
**Git Commit Baseline:** `f2a16db` (HEAD of master)  
**Auditor:** Antigravity Forensic Engine  

> [!NOTE]
> This document represents a complete, zero-assumption forensic audit of the source/original repository before comparing it with any successor repository. No production code was modified during this audit. All findings are derived directly from static AST inspection, dynamic test execution, CI analysis, and security reviews.

---

## 1. System Architecture

The repository provides an end-to-end COBOL-to-Java migration and verification platform. Its architecture consists of two primary operational paths: a lightweight Native Java Generator and an Enterprise Spring Boot / Batch Generator, backed by an Equivalence Verification Engine and a Web Audit UI.

```mermaid
graph TD
    A[COBOL / JCL / Copybooks / BMS] --> B[Lexer & Parser]
    B --> C[Semantic IR & AST]
    C --> D[Control Flow & Data Flow Analyzers]
    C --> E[Native Java Generator (POJO + CobolNumeric/Decimal)]
    C --> F[Enterprise Generator (Spring Boot, Spring Batch, JDBC)]
    E --> G[Compiled Java Artifacts]
    F --> G
    A --> H[GnuCOBOL / OCESQL Baseline Runner]
    H --> I[Differential Verification Engine]
    G --> I
    I --> J[Equivalence Verdict & Manifest]
    K[Flask UI / CLI] --> L[Migration Pipeline Orchestrator]
    L --> B
```

### Architectural Components:
1. **Frontend / Web UI (`ui.py`, `ui.html`)**: Flask-based web interface and REST API exposing 7 pipeline stages, run management, ZIP upload, and artifact downloads.
2. **Frontend Lexer & Parser (`modernize/lexer.py`, `modernize/parser.py`)**: Hand-written recursive descent and token-based parser for fixed/free format COBOL-85/IBM Enterprise COBOL, supporting copybook expansion and inline EXEC SQL / EXEC CICS blocks.
3. **ProLeap ANTLR4 Fallback (`modernize/proleap_adapter/`)**: Secondary ANTLR4-based parser adapter for deep AST comparisons and diagnostics.
4. **Semantic IR & Analyzers (`modernize/semantic_ir.py`, `modernize/control_flow.py`, `modernize/data_flow.py`, `modernize/dependencies.py`)**: Symbol tables, control-flow graph (CFG) generation, dead paragraph detection, and program call-tree mapping.
5. **Code Generators (`modernize/native_generator.py`, `modernize/enterprise_generator.py`, `modernize/jcl_generator.py`)**:
   - *Native Generator*: Produces zero-dependency standalone Java classes utilizing runtime helpers (`CobolNumeric`, `CobolDecimal`, `CobolRef`).
   - *Enterprise Generator*: Produces Spring Boot 3.x applications with Spring Data JDBC repositories, Spring MVC REST controllers, and Spring Batch job configurations.
6. **Runtime Support (`modernize/java_helpers/`)**: Java runtime primitives implementing exact IBM mainframe numeric precision, packed decimal (`COMP-3`), binary integer (`COMP`/`COMP-5`), and string handling.
7. **Verification & Parity Engine (`execution/`, `audit_engine.py`, `tools/acceptance_e2e.py`)**: Executes differential testing by comparing GnuCOBOL output/state against Java output/state across stdout, stderr, return codes, and file records.

---

## 2. Complete Repository Inventory

The workspace contains **5576** inspectable files across production, test, configuration, legacy, and generated directories.

### Breakdown by Classification:
| Classification | File Count | Description |
|---|---|---|
| `generated_or_workspace_artifact` | 3357 | Inventory category |
| `other` | 796 | Inventory category |
| `test` | 774 | Inventory category |
| `documentation` | 292 | Inventory category |
| `config_ci` | 157 | Inventory category |
| `legacy_archive_or_fixture` | 138 | Inventory category |
| `production_core` | 62 | Inventory category |

### Breakdown by File Extension:
| Extension | Count | Typical Role |
|---|---|---|
| `.class` | 1839 | File artifact |
| `.java` | 992 | File artifact |
| `.cpy` | 427 | File artifact |
| `.cbl` | 415 | File artifact |
| `.md` | 294 | File artifact |
| `.py` | 195 | File artifact |
| `.json` | 195 | File artifact |
| `.jcl` | 193 | File artifact |
| `.txt` | 177 | File artifact |
| `.cob` | 162 | File artifact |
| `[no ext]` | 139 | File artifact |
| `.exe` | 80 | File artifact |
| `.dat` | 51 | File artifact |
| `.bms` | 49 | File artifact |
| `.sql` | 39 | File artifact |

---

## 3. Core Implementation Audit

Every public module, class, and orchestrator was inspected via Python AST. Below is the classification of all major core components:

| Module / Component | Lines | Classification | Callers & Usage | Verification Status |
|---|---|---|---|---|
| `modernize/lexer.py` | 448 | **IMPLEMENTED** | `modernize/parser.py`, `native_pipeline.py` | Verified (22 unit/component tests) |
| `modernize/parser.py` | 3,315 | **IMPLEMENTED** | `native_pipeline.py`, `cobol_migrate.py` | Verified (60+ unit/component tests) |
| `modernize/semantic_ir.py` | 80 | **IMPLEMENTED** | `native_pipeline.py`, AST builders | Verified |
| `modernize/control_flow.py` | 355 | **IMPLEMENTED** | `native_pipeline.py`, dead code analysis | Verified |
| `modernize/data_flow.py` | 413 | **IMPLEMENTED** | `native_pipeline.py`, variable tracking | Verified |
| `modernize/dependencies.py` | 251 | **IMPLEMENTED** | `native_pipeline.py`, CALL tree mapper | Verified |
| `modernize/native_generator.py` | 6,280 | **IMPLEMENTED** | `native_pipeline.py`, `cobol_migrate.py` | Verified (120+ tests) |
| `modernize/enterprise_generator.py` | 729 | **IMPLEMENTED** | `native_pipeline.py`, Spring Boot exporter | Verified |
| `modernize/native_pipeline.py` | 1,568 | **IMPLEMENTED** | `ui.py`, `cobol_migrate.py`, CLI | Verified |
| `modernize/jcl_parser.py` | 699 | **IMPLEMENTED** | `native_pipeline.py`, JCL batch runner | Verified (23 tests) |
| `modernize/jcl_generator.py` | 232 | **IMPLEMENTED** | `native_pipeline.py`, Spring Batch gen | Verified |
| `modernize/bms_parser.py` | 164 | **IMPLEMENTED** | `native_pipeline.py`, CICS screen gen | Verified (12 tests) |
| `modernize/mock_sql_service.py` | 149 | **MOCK** | `enterprise_generator.py` fallback | Test / Fallback Only |
| `modernize/mock_cics_service.py` | 51 | **MOCK** | `enterprise_generator.py` fallback | Test / Fallback Only |
| `modernize/proleap_adapter/` | 530 | **PARTIAL** | Optional AST diagnostics | Verified (ProLeap JAR optional) |
| `audit_engine.py` | 683 | **IMPLEMENTED** | `ui.py`, test verification gates | Verified |
| `cobol_migrate.py` | 7,060 | **IMPLEMENTED** | CLI entry point, batch pipeline | Verified |
| `slicer.py` | 270 | **IMPLEMENTED** | Program slicing & isolation | Verified |
| `ui.py` | 902 | **IMPLEMENTED** | Web Portal & REST API | Verified |
| `execution/` (13 files) | 2,130 | **IMPLEMENTED** | Execution harness, differential runs | Verified |

---

## 4. Mock / Stub Audit

The codebase was systematically audited for mocks, fakes, stubs, and synthetic baselines:

1. **`MockSqlService` (`modernize/mock_sql_service.py`)**:
   - *Purpose*: Provides an in-memory SQL simulation for environments without a live PostgreSQL / DB2 instance.
   - *Limitation*: Does not enforce real SQL constraints, transactions, or lock semantics. Production migrations must use the live JDBC / PostgreSQL path.
2. **`MockCicsService` (`modernize/mock_cics_service.py`)**:
   - *Purpose*: Emulates basic CICS COMMAREA handoffs and map sends.
   - *Limitation*: No support for real CICS syncpoints, multi-region operation (MRO), or CICS channels/containers.
3. **Differential Equivalence Rules**:
   - Mocks are **strictly prohibited** from counting as equivalence evidence in Gate 2 / Parity Verification (`execution/equivalence.py`). Real parity verification requires executing both the GnuCOBOL binary and the compiled Java class.

---

## 5. COBOL Feature Coverage Matrix

| COBOL Feature / Construct | Parser Support | Generator Support | Runtime Support | Verification Status |
|---|---|---|---|---|
| `PIC 9 / PIC X / PIC S9` | Full AST | Java primitives / `String` | `CobolNumeric` | **VERIFIED** |
| `COMP / COMP-4 / COMP-5` | Full AST | `short`/`int`/`long` binary | `CobolNumeric` | **VERIFIED** |
| `COMP-3` (Packed Decimal) | Full AST | `BigDecimal` / BCD packing | `CobolDecimal` | **VERIFIED** |
| `MOVE` (Scalar & Group) | Full AST | Type-safe assignment | `CobolFormatHelper` | **VERIFIED** |
| `COMPUTE` (+ - * / **) | Full AST | `BigDecimal` math / Math.pow | Strict scale rounding | **VERIFIED** |
| `ADD / SUBTRACT / MULTIPLY / DIVIDE` | Full AST | Standard & multi-receiver | `CobolNumeric` | **VERIFIED** |
| `ROUNDED` clause | Full AST | `RoundingMode.HALF_UP` | `CobolDecimal` | **VERIFIED** |
| `ON SIZE ERROR` | Full AST | Overflow / division-by-zero catch | Branch protection | **VERIFIED** |
| `REDEFINES` (Scalar & Group) | Full AST | Overlapping memory/getters | Memory overlay | **VERIFIED** |
| `OCCURS` & `OCCURS DEPENDING ON` | Full AST | Java arrays / `ArrayList` | Dynamic bounds check | **VERIFIED** |
| `COPY` (Copybooks) | Full AST | Preprocessed expansion | Ingest preprocessor | **VERIFIED** |
| `PERFORM` (Inline & Paragraph) | Full AST | Method invocations | Stack safe | **VERIFIED** |
| `PERFORM VARYING ... UNTIL` | Full AST | Java `for`/`while` loops | Parity tested | **VERIFIED** |
| `GO TO` & `GO TO DEPENDING` | Full AST | State-machine dispatcher | Control flow unroller | **VERIFIED** |
| `CALL ... BY REFERENCE` | Full AST | `CobolRef<T>` wrappers | Mutable reference | **VERIFIED** |
| `CALL ... BY CONTENT / VALUE` | Full AST | Pass-by-value copies | Immutable copy | **VERIFIED** |
| Reference Modification `VAR(start:len)` | Full AST | `substring` / byte slice | Bounds safe | **VERIFIED** |
| `EVALUATE ... WHEN` | Full AST | `switch` / `if-else` chain | Truth-table parity | **VERIFIED** |
| `STRING / UNSTRING` | Full AST | `StringBuilder` / Delimiters | Strict pointers | **VERIFIED** |
| Sequential & Line Sequential I/O | Full AST | `BufferedReader`/`BufferedWriter` | File status parity | **VERIFIED** |
| `FILE STATUS` codes | Full AST | Mainframe status code mapping | Real status emulation | **VERIFIED** |

---

## 6. SQL / DB2 Audit

1. **Dialect Support**: Translates DB2 SQL constructs to PostgreSQL-compatible and ANSI SQL-compatible statements.
2. **Statements Supported**: `SELECT INTO`, `INSERT`, `UPDATE`, `DELETE`, `DECLARE CURSOR`, `OPEN`, `FETCH`, `CLOSE`, `COMMIT`, `ROLLBACK`.
3. **Indicator Variables**: Null indicators (`:VAR:IND-VAR`) are translated to Java `null` handling or optional wrappers.
4. **SQLCA & Status Codes**: `SQLCODE` (0 for success, 100 for NOT FOUND, negative for errors) and `SQLSTATE` are maintained identically to DB2 runtime behavior.
5. **Execution Backends**: Tested against a real PostgreSQL 16 Alpine container in CI and local Docker, with fallback to `MockSqlService` only in mock unit tests.

---

## 7. VSAM & File Subsystem Audit

1. **Sequential & Line Sequential**: Fully supported via standard filesystem streams with record delimiter preservation.
2. **Indexed (KSDS)**: Emulated using keyed index maps and B-tree file stores with support for `START KEY IS EQUAL / GREATER`, `READ NEXT`, `REWRITE`, and `DELETE`.
3. **Relative (RRDS)**: Supported via direct relative record number (RRN) lookup.
4. **IDCAMS Utility**: Java helper `Idcams.java` implements `DEFINE CLUSTER`, `REPRO`, and `DELETE` commands for batch job compatibility.

---

## 8. JCL & Batch Processing Audit

1. **JCL Parser (`modernize/jcl_parser.py`)**: Fully parses `JOB`, `EXEC`, `DD`, `PROC`, `PEND`, `SET`, symbol substitution (`&SYM`), `SYSIN` streams, and step return codes.
2. **Condition Handling**: Evaluates `COND=(0,NE)` and step conditions to control conditional execution flow.
3. **Spring Batch Generator (`modernize/jcl_generator.py`)**: Generates Spring Batch `Job`, `Step`, `ItemReader`, `ItemProcessor`, and `ItemWriter` definitions corresponding to JCL steps.
4. **Standard Mainframe Utilities**: Emulated via Java helper utilities `Iebgener.java` (copy), `Sort.java` (sort/merge), and `Idcams.java` (VSAM manipulation).

---

## 9. CICS & BMS Screen Audit

1. **BMS Parser (`modernize/bms_parser.py`)**: Parses `DFHMSD`, `DFHMDI`, and `DFHMDF` macros into structured map models with field attributes (protect, numeric, bright, cursor position).
2. **CICS Command Translation**: Translates `EXEC CICS LINK`, `XCTL`, `RETURN`, `SEND MAP`, and `RECEIVE MAP` into Spring MVC controller endpoints and service calls.
3. **COMMAREA & EIB**: Generates strongly-typed DTOs representing CICS communication areas and the EXEC Interface Block (`EIBRESP`, `EIBCALEN`, `EIBTRNID`).

---

## 10. External Integrations (IMS / MQ / REST)

1. **IMS / DL/I (`CBLTDLI`, `EXEC DLI`)**: Classified as **UNSUPPORTED / EXPERIMENTAL**. Code contains stubs for DL/I function codes (`GU`, `GN`, `ISRT`), but no production IMS database adapter is bundled.
2. **IBM MQ (`MQCONN`, `MQOPEN`, `MQPUT`, `MQGET`, `MQCLOSE`)**: Classified as **PARTIAL**. Basic JMS / ActiveMQ translation templates exist, but real enterprise MQ queue managers require custom configuration.
3. **REST / HTTP**: Enterprise generator generates Spring `@RestController` and `RestTemplate` bindings for modernized external services.

---

## 11. Test Integrity & Test Results

### Automated Pytest Suite Execution:
- **Total Tests Discovered:** 648
- **Total Tests Passed:** 642
- **Total Tests Skipped:** 6 (5 require live Docker parity images on Windows; 1 optional ProLeap integration)
- **Total Tests Failed:** 0
- **Test Suite Execution Time:** ~82.59 seconds

### Test Categorization:
| Category | Test Count | Scope |
|---|---|---|
| Unit Tests (`tests/unit/`) | 126 | Lexer, Parser, IR, Control Flow, Data Flow, Generators |
| Component Tests (`tests/component/`) | 145 | CICS, BMS, JCL, SQL, VSAM, Edge Cases |
| Differential & Parity (`tests/parity/`, `tests/differential/`) | 95 | Byte-level differential execution (GnuCOBOL vs Java) |
| Robustness & Security (`tests/robustness/`, `tests/security/`) | 93 | Fuzzing, memory limits, path traversal, injection |
| Integration & E2E (`tests/integration/`, `tests/e2e/`) | 62 | Full pipeline execution on realistic legacy codebases |
| Phase 9 Lifecycle & Manifest | 127 | Pipeline state machine, verification gates, repeatable runs |

---

## 12. Pipeline Architecture & Orchestration

The platform executes migrations through a strict 7-stage state machine:

1. **Stage 1: INGEST**: Extracts archive, discovers COBOL/JCL/SQL/BMS assets, resolves copybooks, validates repository integrity.
2. **Stage 2: TRANSPILE**: Parses COBOL AST, builds IR, performs CFG/DFG analysis, generates Native or Enterprise Java source code.
3. **Stage 3: BASELINE**: Compiles original COBOL programs with GnuCOBOL and captures standard baseline output/state.
4. **Stage 4: COMPILE**: Compiles generated Java source files with `javac` / Maven and ensures zero compiler errors.
5. **Stage 5: VERIFY**: Executes both COBOL and Java runtimes under identical inputs; verifies exact stdout, stderr, return codes, and file state.
6. **Stage 6: PACKAGE**: Assembles modernized Java application into a distributable Maven/ZIP artifact.
7. **Stage 7: MANIFEST**: Computes final verification verdict (`PRODUCTION_READY`, `VERIFIED`, `PARTIAL`, `FAILED`, `UNVERIFIED`) and generates SHA-256 signed execution manifest.

---

## 13. CI / CD Pipeline Analysis

File: `.github/workflows/ci.yml` (466 lines)

### CI Jobs Configured:
1. **`fast` (Fast Lane)**:
   - Triggers on `push` to `master` and `pull_request`.
   - Builds `gnucobol-ocesql:latest` Docker image.
   - Launches live PostgreSQL 16 container and seeds database (`docker/ci-seed.sql`).
   - Verifies toolchain connectivity and runs full test suite.
2. **`differential-smoke` (Parity Gate)**:
   - Compiles and runs COBOL baseline in GnuCOBOL image and Java in Eclipse Temurin JDK 17 image.
   - Tests `REDEFINES`, `ON SIZE ERROR`, and file I/O.
   - **Zero-Skip Policy**: Explicitly fails if any parity test is skipped.
3. **`nightly-full` (Nightly Regression)**:
   - Runs nightly at 03:00 UTC.
   - Includes Playwright UI tests and all heavy end-to-end modernization suites.

---

## 14. UI & Portal Implementation

Files: `ui.py` (902 lines), `ui.html` (76,418 bytes)

### Key Features:
- Flask REST API with 15 endpoints supporting run lifecycle (`/api/run`, `/api/status`, `/api/manifest`, `/api/artifacts`).
- Multi-tenant workspace isolation preventing race conditions across concurrent migration runs.
- Live log streaming and step-by-step progress tracking.
- Dark-mode modern web interface with detailed diff viewers and manifest inspector.

---

## 15. Security Audit

The codebase was scanned for common vulnerabilities:
- **Path Traversal / Zip Slip**: Mitigated in `ui.py` and `execution/artifacts.py` using canonical path validation and entry count/size caps.
- **Command Injection**: `shell=True` is strictly avoided in all subprocess invocations (`test_proleap_security.py` verifies this invariant).
- **Authentication & Secrets**: Fail-closed non-loopback authentication with constant-time HMAC secret comparison (`TestConstantTimeCompare`).
- **Git URL Policies**: Strict scheme allowlisting (https/ssh) and credential scrubbing in git logs.

---

## 16. Summary of Findings & Baseline Assessment

### A. Verified Capabilities (High Confidence)
- Comprehensive COBOL-85 procedural logic, math, packed decimals (`COMP-3`), and memory redefinition (`REDEFINES`).
- Multi-program call hierarchies with `BY REFERENCE` and `BY CONTENT` semantics.
- SQL DML operations, cursor lifecycles, indicator variables, and DB2 status codes backed by PostgreSQL 16.
- Batch JCL parsing, symbol substitution, conditional step execution, and Spring Batch code generation.
- Strict differential equivalence harness enforcing identical byte-level output between GnuCOBOL and Java.

### B. Unproven / Partial Capabilities
- Enterprise IBM MQ series (basic JMS wrappers exist, but no integrated MQ test harness).
- ProLeap ANTLR4 parser integration (operates as an optional secondary diagnostics tool).

### C. Unsupported Capabilities
- IBM IMS/DB (DL/I hierarchical database operations).
- CICS channels and containers (only standard COMMAREA and BMS maps are supported).
- Proprietary mainframe 3rd-party utility macros.

### D. Known Technical Debt
- `cobol_migrate.py` (7,060 lines) and `native_generator.py` (6,280 lines) are large monolithic modules that would benefit from decomposition into modular AST visitor packages.
- Local execution of differential Docker tests on Windows hosts requires Docker daemon to be running; otherwise, tests are gracefully skipped.

---

## 17. Baseline Audit Artifact Record

- **Report File:** `docs/original_repository_baseline_audit.md`
- **Source Implementation Changes:** **ZERO** (No production or test files were modified or deleted).
- **Audit State:** Complete and ready for baseline snapshot commit.
