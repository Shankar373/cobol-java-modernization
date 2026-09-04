# Master False-Pass Risk Register

**Repository:** `c:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test`  
**Branch:** `integration/successor-verified-improvements`  
**Certification Standard:** Ponytail Global AI Software Engineering Constitution  
**Platform Verdict:** `VERIFIED_FOR_DEFINED_SCOPE`  
**Mentor Validation Status:** `VERIFIED_FOR_TESTED_SCOPE`  

---

| Risk ID | Vulnerability / False-Pass Mechanism | Potential Impact | Current Protection Mechanism | Proving Test Case | Residual Risk | Status |
|---|---|---|---|---|---|---|
| **FP-01** | **Stale Output Reuse Across Runs** | Previous run's valid output files might be compared if new run fails to write output. | Pipeline clears `target/` and output directories with `.gitkeep` at stage start; file size and timestamp checked. | `test_adversarial_verification.py` | Low | **MITIGATED** |
| **FP-02** | **Self-Comparison (Comparing Output Against Itself)** | If baseline directory and target directory point to the same path, comparison will always match. | `stage_compare` (Gate 1) and `stage_validate` (Gate 2) assert `os.path.realpath(baseline_dir) != os.path.realpath(mod_dir)`. Aborts immediately with `Self-comparison vulnerability detected`. | `test_adv_01_self_comparison_rejection_gate1`, `test_adv_02_self_comparison_rejection_gate2` | None | **MITIGATED** |
| **FP-03** | **Zero-Byte / Empty File False Match** | If both COBOL and Java crash or exit without creating data, two 0-byte files could be compared as matching. | Comparison engine fails closed on 0-byte output unless `allow_empty_outputs: true` is explicitly declared in config. | `test_adv_04_zero_byte_mismatch_detection` | None | **MITIGATED** |
| **FP-04** | **Log Sentinel Spoofing (`[COMPLETED]`)** | If an application prints `[COMPLETED]` into log but later throws an unhandled exception or terminates with error, it could falsely report success. | `cobol_migrate.py` verifies `proc.poll() == 0` alongside log sentinel; Gate 2 differential output file check is mandatory regardless of log message. | `test_adv_05_sentinel_log_spoofing_with_process_failure` | None | **MITIGATED** |
| **FP-05** | **Whitespace Stripping Masking Truncation** | Normalizer stripping trailing whitespace could mask fixed-width record column truncation. | `_normalize_text` preserves record column spaces and only normalizes line endings (`\r\n` -> `\n`). | `test_pic_v_string_semantics.py` | Low | **MITIGATED** |
| **FP-06** | **Mock Database Service Certified as Live DB** | Generated code utilizing `MockSqlService` could pass in-memory tests without actual database connectivity. | Verdict engine in `_compute_verdict` checks for `MockSqlService` usage and forces verdict to `EQUIVALENCE_UNVERIFIED` / fail-closed from production certification. | `test_validation_nobypass.py` | Low | **MITIGATED** |
| **FP-07** | **Incomplete SQL Schema Row Count Matching** | Comparing rows only on matching columns while ignoring extra/missing table columns. | `_run_db_state_comparison` performs full column dictionary comparison on sorted row keys. | `test_db2_pipeline.py` | Low | **MITIGATED** |
| **FP-08** | **Unsupported Syntax Silently Skipped by Parser** | Parser emitting warning for unsupported statement and continuing execution without emitting corresponding Java logic. | Parser flags unhandled AST statements as `UNKNOWN_STATEMENT`; compiler check rejects missing identifiers; Gate 2 output comparison fails if logic is omitted. | `test_parser.py` | Medium | **PARTIALLY_MITIGATED** |
| **FP-09** | **Missing Required Batch Input Fallback** | If flat-file input is not found, batch reader falls back to default empty reader. | `stage_validate` aborts immediately with `Required batch input file missing or unresolvable` when required input cannot be resolved. | `test_adv_03_missing_required_input_fails_closed` | None | **MITIGATED** |
| **FP-10** | **Mutation Test False Negative** | Injected mutant that does not alter business logic (dead code mutant) passing verifier without proving sensitivity. | `_run_real_mutation_testing` uses 6 distinct real AST mutations affecting calculations, branching, and string formatting; all 6 must be detected. | `test_mutation_verification.py` | Low | **MITIGATED** |
| **FP-11** | **Output Topology Masking Extra Files** | A single matching expected output file could hide extra incorrect output files created by the Java application. | Gate 2 scans output directory tree and rejects unexpected extra files. | `stage_validate` output topology check | None | **MITIGATED** |
| **FP-12** | **Live Mainframe DB2 Divergence** | In-memory/Docker DB2 behaves differently from live IBM DB2 z/OS. | Marked `UNPROVEN` in capability matrix and certification report. | `REAL_DB2_MODE=1` validation | High | **UNPROVEN** |
