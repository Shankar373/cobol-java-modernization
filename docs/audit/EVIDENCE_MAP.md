# Master Evidence Map

This map traces every claim in the platform's certification reports, README, and documentation to exact source code locations, test suites, and reproducible execution artifacts.

---

| Claim / Capability | Evidence Type | Exact File | Exact Function / Module | Test Suite | Runtime Artifact | Confidence |
|---|---|---|---|---|---|---|
| **COBOL AST Parsing & Semantic IR** | Source & Test | `modernize/parser.py` | `parse_cobol_program()`, `SemanticIRNode` | `tests/test_parser.py` | `pipeline_execution_manifest.json` | **DIRECTLY_PROVEN** |
| **GnuCOBOL Docker Baseline Execution** | Runtime & Docker | `cobol_migrate.py` | `stage_baseline()`, `run_in_docker()` | `tests/test_parity_fixtures.py` | `target/baseline/legacy/data/out/*` | **DIRECTLY_PROVEN** |
| **Stage-1 Transpiled Java Execution** | Source & Runtime | `cobol_migrate.py` | `stage_transpile()`, `stage_execute()` | `tests/test_transpiler.py` | `target/results/java/data/out/*` | **DIRECTLY_PROVEN** |
| **Gate 1 Differential File Verification** | Differential | `cobol_migrate.py` | `stage_compare()`, `ComparisonResult` | `tests/e2e/differential/files/test_filestat01.py` | `differential_validation_report.json` | **DIRECTLY_PROVEN** |
| **Stage-2 Native Spring Boot Generation** | Source & Generator| `modernize/native_generator.py` | `NativeProgramGenerator.generate_class_source()` | `tests/test_native_generator.py` | `target/modernized/src/main/java/...` | **DIRECTLY_PROVEN** |
| **Alphanumeric Relational Parity** | Semantic / Parity | `modernize/java_helpers/CobolFormatHelper.java` | `CobolFormatHelper.cobolEquals()` | `tests/test_cobol_string_semantics.py` | `target/modernized/data/out/inventory_report.txt` | **DIRECTLY_PROVEN** |
| **Implied Decimal (PIC V) Parity** | Semantic / Parity | `modernize/java_helpers/CobolFormatHelper.java` | `CobolFormatHelper.truncateToPic()` | `tests/test_pic_v_string_semantics.py` | `target/modernized/data/out/customer_report.txt` | **DIRECTLY_PROVEN** |
| **REDEFINES Shared Memory Synchronization** | Differential | `modernize/runtime/CobolRef.java` | `get_<var>_bytes()`, `sync_redefines()` | `tests/e2e/differential/storage/test_redefines01.py` | `redefines_output.txt` (Exact hash) | **DIRECTLY_PROVEN** |
| **ON SIZE ERROR Checked Arithmetic** | Differential | `modernize/runtime/CobolArithmetic.java` | `CobolArithmetic.add()`, `SizeErrorPolicy` | `tests/e2e/differential/numeric/test_sizeerr01.py` | `sizeerr_output.txt` (Exact hash) | **DIRECTLY_PROVEN** |
| **AST Mutation Testing Sensitivity** | Mutation | `cobol_migrate.py` | `_run_real_mutation_testing()` | `tests/test_mutation_verification.py` | `pipeline_execution_manifest.json` (6/6 mutants caught) | **DIRECTLY_PROVEN** |
| **Gate 2 Live Spring Boot Validation** | E2E JVM Runtime | `cobol_migrate.py` | `stage_validate()` | `tests/test_validation_nobypass.py` | `target/modernized/data/out/*` | **DIRECTLY_PROVEN** |
| **PostgreSQL Database State Verification** | SQL / JDBC | `modernize/java_helpers/Db2Verify.java` | `Db2Verify.main()`, `_run_db_state_comparison` | `tests/test_sql_baseline_differential.py` | Database row comparison JSON | **DIRECTLY_PROVEN** |
| **Fail-Closed Gate 2 on Mismatch** | Negative Test | `cobol_migrate.py` | `stage_validate()` | `tests/test_validation_nobypass.py` | Exception trace / `Gate 2 FAIL` | **DIRECTLY_PROVEN** |
| **CICS REST Modernization** | Simulation | `modernize/java_helpers/CicsProgramRegistry.java`| `CicsProgramRegistry.execute()` | `tests/test_cics_rest.py` | `reports/CICSREST01/CERTIFICATION_REPORT.md` | **SUPPORTED_BY_TEST (SIMULATION)** |
| **VSAM KSDS Indexed Database Emulation** | Simulation | `modernize/java_helpers/KsdSDbService.java` | `KsdSDbService.readRecord()` | `tests/test_ksds.py` | Database table records | **SUPPORTED_BY_TEST (SIMULATION)** |
| **Live IBM DB2 z/OS Subsystem Parity** | Mainframe Subsystem| `modernize/java_helpers/Db2Verify.java` | `run_real_db2_validation()` | Manual mainframe runs (`REAL_DB2_MODE=1`) | None (Unexecuted locally) | **UNPROVEN** |
| **Native EBCDIC Character Collating** | Character Set | None | None | None | None | **UNSUPPORTED** |
| **Arbitrary Unseen Mainframe Generalization** | Generalization | `cobol_migrate.py` | Full Pipeline | `scratch/run_unseen_and_failure_injections.py` | Fail-closed diagnostic output | **PARTIALLY_PROVEN** |
