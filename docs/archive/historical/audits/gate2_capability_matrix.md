> [!NOTE]
> **HISTORICAL ARCHIVE — NOT CURRENT SOURCE OF TRUTH**  
> This document is preserved for historical provenance and audit trail purposes only. Refer to [`DOCUMENTATION_INDEX.md`](../../../DOCUMENTATION_INDEX.md) for the authoritative active documentation set.

---

# Gate 2 Capability Matrix

This matrix establishes the verified capability status across all dimensions of the Gate 2 modernization and validation engine.

| Capability Domain | Sub-Capability | Status | Evidence / Forensic Notes |
|---|---|---|---|
| **Input Resolution** | Flat-file `data/in/` discovery | **VERIFIED** | Successfully resolves and mounts `data/in/input.txt` when present. |
| **Input Resolution** | Custom input paths (`data/source`, `inputs/`) | **PARTIAL** | Fails to copy non-`in` directories to `modernized/data/` in `stage_validate`. |
| **Input Resolution** | Model-driven batch layout mapping | **PARTIAL** | Works for `RAW-*` prefixed fields; defaults for non-matching records. |
| **State Isolation** | Run-scoped directory allocation (`self.out`) | **VERIFIED** | Unique targets prevent concurrent execution clobbering. |
| **State Isolation** | Workspace root isolation | **PARTIAL** | Traceability manifest currently writes to `os.path.dirname(self.out)/generated`. |
| **State Isolation** | Port collision avoidance | **VERIFIED** | `select_validation_port` probes free socket from 8082 upward. |
| **Baseline Capture** | GnuCOBOL Docker compilation & run | **VERIFIED** | Direct execution in `gnucobol-ocesql:latest` / `opensourcecobol4j:2.0.0`. |
| **Baseline Capture** | Line-sequential file capture | **VERIFIED** | Captures exact POSIX `\n` byte streams into `target/baseline/legacy/`. |
| **Baseline Capture** | Missing baseline detection | **VERIFIED** | Pipeline marks baseline `BASELINE_UNPRODUCIBLE` / `EQUIVALENCE_UNVERIFIED`. |
| **Stage-1 Parity (Gate 1)** | COBOL4J transpilation & execution | **VERIFIED** | Stage-1 compiles with `libcobj.jar` and passes differential comparison. |
| **Stage-1 Parity (Gate 1)** | Byte-level equivalence checking | **VERIFIED** | Detects SHA-256 and byte-length parity between legacy and Stage-1 Java. |
| **Stage-2 Generation** | Clean Native Java emission (no libcobj) | **VERIFIED** | Verified 0 forbidden runtime dependencies across 54 scanned files. |
| **Stage-2 Generation** | PIC V / Implied Decimal STRING output | **VERIFIED** | Emits `toStorageImage()` (`000010025`), matching COBOL storage semantics. |
| **Stage-2 Generation** | Alphanumeric Fixed-Width `EVALUATE`/`IF` | **BROKEN** | Uses `Objects.equals("ACTIVE    ", "ACTIVE")` which evaluates false in Java. |
| **Stage-2 Generation** | Line-sequential writer line endings | **VERIFIED** | Uses `.write("\n")` ensuring cross-platform LF byte fidelity. |
| **Spring Batch Integration** | Batch job lifecycle and configuration | **VERIFIED** | Spring Boot starts, completes `JobLauncherCommandLineRunner`, outputs status. |
| **Spring Batch Integration** | Parameter override (`--app.batch.input`) | **VERIFIED** | Passed dynamically via CLI arguments to Spring Boot runner. |
| **File Output & Comparison** | Exact content comparison | **VERIFIED** | Generic and benchmark modes discover and compare output files. |
| **File Output & Comparison** | Whitespace normalization | **PARTIAL** | Trailing whitespace normalization can hide fixed-width record truncation. |
| **Database Comparison** | Record-by-record table comparison | **PARTIAL** | Works for SQLite/PostgreSQL/H2; hardcodes `CUST_ID`/`CUST_NAME` for raw SQL. |
| **Database Comparison** | Live IBM DB2 z/OS / LUW validation | **UNPROVEN** | Defaults to `H2_EMULATED` / `NOT_VERIFIED` unless `REAL_DB2_MODE=1`. |
| **Mutation Testing** | Real AST / Java byte mutation injection | **VERIFIED** | Injects 6 structural mutations; verifies fail-closed build/execution/Gate 2. |
| **Traceability** | Business-rule extraction & matrix | **VERIFIED** | Extracts rule AST, maps to Java classes, outputs markdown & JSON manifests. |
| **Error & Timeout Handling** | JVM crash detection | **VERIFIED** | Polls `proc.poll()`, surfaces exit code and log tail on premature termination. |
| **Error & Timeout Handling** | Hanging process timeout | **VERIFIED** | Hard timeout ceiling (120s / 240 ticks) terminates runaway JVMs cleanly. |
| **CI Integration** | Push / PR fast lane & smoke lane | **VERIFIED** | Multi-lane GitHub Actions workflow with Docker image build & PostgreSQL. |
| **CI Integration** | Full regression lane coverage | **PARTIAL** | 5 suites ignored in fast-lane; nightly full lane runs on schedule only. |
| **UI Integration** | Web Application dashboard & logs | **VERIFIED** | Serves dashboard on port 8788, uploads zip, displays real Gate 1 & Gate 2 badges. |

### Summary Status Legend:
- **VERIFIED:** Fully implemented, exercised by tests, proven by execution evidence.
- **PARTIAL:** Functional in core paths, but has documented edge-case gaps or limitations.
- **BROKEN:** Demonstrates semantic regression or incorrect logic requiring a bug fix.
- **UNPROVEN:** Supported in design, but requires external hardware/credentials not active in standard environment.
