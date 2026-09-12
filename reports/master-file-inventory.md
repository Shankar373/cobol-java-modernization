# SystemaOps Master File Inventory — Forensic Audit

- Branch: `environment-discovery` @ `d2311c5`  
- Generated: 2026-09-11 (read-only audit; no production code modified)
- Total tracked files: **2045**; untracked paths: **69**

Classification legend: `source/config`, `test`, `test-output-artifact`, `documentation`, `generated-artifact` (stale candidate), `generated-build-artifact` (committed bytecode), `tracked-binary`, `preprocessed-fixture`, `data`.

> Every tracked file is listed below within its component group. The decision-relevant files carry hand-audited annotations in the companion `project-gap-analysis.md` and `master-capability-matrix.md`. Committed bytecode and generated fixtures are stale candidates flagged per AGENTS.md hygiene rules but preserved (no deletions during audit).

**Stale-candidate count: 242 tracked files** (committed `*.class`/`*.pyc` bytecode, `generated*/` trees inside test repos, `*.exe`/`*.so` binaries).

## root (18 files)

| Path | Type | Bytes | Lifecycle |
|---|---|---|---|
| `.dockerignore` | (none) | 493 | source/config |
| `.gitignore` | (none) | 757 | source/config |
| `COMPLETE_SYSTEM_DOCUMENTATION.md` | documentation | 11552 | documentation |
| `Dockerfile` | (none) | 3960 | source/config |
| `Dockerfile.gnucobol-ocesql` | docker | 5113 | source/config |
| `PROJECT_OVERVIEW.md` | documentation | 18539 | documentation |
| `README.md` | documentation | 6948 | documentation |
| `audit_engine.py` | python-source | 30292 | source/config |
| `cobol_migrate.py` | python-source | 374418 | source/config |
| `conftest.py` | python-source | 1289 | source/config |
| `docker-compose.yml` | config | 2551 | source/config |
| `migration_config.json` | config/data | 1984 | source/config |
| `pyproject.toml` | build-config | 678 | source/config |
| `requirements-dev.txt` | data/text | 1219 | source/config |
| `requirements.txt` | data/text | 632 | source/config |
| `slicer.py` | python-source | 12027 | source/config |
| `ui.html` | ui | 76614 | source/config |
| `ui.py` | python-source | 43204 | source/config |

## modernize-V1 (43 files)

| Path | Type | Bytes | Lifecycle |
|---|---|---|---|
| `modernize/__init__.py` | python-source | 917 | source/config |
| `modernize/bms_parser.py` | python-source | 5728 | source/config |
| `modernize/capability_matrix.py` | python-source | 37064 | source/config |
| `modernize/control_flow.py` | python-source | 14364 | source/config |
| `modernize/coverage.py` | python-source | 1394 | source/config |
| `modernize/data_flow.py` | python-source | 16253 | source/config |
| `modernize/dependencies.py` | python-source | 12502 | source/config |
| `modernize/enterprise_generator.py` | python-source | 49714 | source/config |
| `modernize/java_helpers/CobolFormatHelper.java` | java-source | 15695 | source/config |
| `modernize/java_helpers/CobolRef.java` | java-source | 476 | source/config |
| `modernize/java_helpers/Db2Verify.java` | java-source | 5178 | source/config |
| `modernize/java_helpers/Idcams.java` | java-source | 4527 | source/config |
| `modernize/java_helpers/Iebgener.java` | java-source | 1698 | source/config |
| `modernize/java_helpers/Sort.java` | java-source | 4893 | source/config |
| `modernize/java_helpers/src/main/java/com/systema/modernized/CicsTransactionContext.java` | java-source | 3560 | source/config |
| `modernize/java_helpers/src/main/java/com/systema/modernized/KsdSDbService.java` | java-source | 7114 | source/config |
| `modernize/java_helpers/src/main/java/com/systema/modernized/MockSqlService.java` | java-source | 2623 | source/config |
| `modernize/java_helpers/src/main/java/com/systema/modernized/runtime/AssignResult.java` | java-source | 330 | source/config |
| `modernize/java_helpers/src/main/java/com/systema/modernized/runtime/CobolArithmetic.java` | java-source | 4263 | source/config |
| `modernize/java_helpers/src/main/java/com/systema/modernized/runtime/CobolNumeric.java` | java-source | 12851 | source/config |
| `modernize/java_helpers/src/main/java/com/systema/modernized/runtime/CobolNumericSpec.java` | java-source | 898 | source/config |
| `modernize/java_helpers/src/main/java/com/systema/modernized/runtime/CobolRoundingMode.java` | java-source | 1966 | source/config |
| `modernize/java_helpers/src/main/java/com/systema/modernized/runtime/CobolSignPosition.java` | java-source | 97 | source/config |
| `modernize/java_helpers/src/main/java/com/systema/modernized/runtime/CobolUsage.java` | java-source | 102 | source/config |
| `modernize/java_helpers/src/main/java/com/systema/modernized/runtime/ProhibitedRoundingException.java` | java-source | 201 | source/config |
| `modernize/java_helpers/src/main/java/com/systema/modernized/runtime/SizeErrorPolicy.java` | java-source | 96 | source/config |
| `modernize/java_helpers/src/main/java/com/systema/modernized/runtime/UnsupportedPrecisionException.java` | java-source | 202 | source/config |
| `modernize/java_helpers/src/main/java/com/systema/modernized/runtime/VsamIndexedStore.java` | java-source | 5178 | source/config |
| `modernize/jcl_generator.py` | python-source | 11509 | source/config |
| `modernize/jcl_parser.py` | python-source | 27694 | source/config |
| `modernize/lexer.py` | python-source | 21993 | source/config |
| `modernize/mock_cics_service.py` | python-source | 1901 | source/config |
| `modernize/mock_sql_service.py` | python-source | 5967 | source/config |
| `modernize/native_generator.py` | python-source | 349750 | source/config |
| `modernize/native_pipeline.py` | python-source | 81401 | source/config |
| `modernize/parser.py` | python-source | 138459 | source/config |
| `modernize/proleap_adapter/__init__.py` | python-source | 74 | source/config |
| `modernize/proleap_adapter/comparison.py` | python-source | 4151 | source/config |
| `modernize/proleap_adapter/diagnostics.py` | python-source | 411 | source/config |
| `modernize/proleap_adapter/ir_mapper.py` | python-source | 7245 | source/config |
| `modernize/proleap_adapter/parser_adapter.py` | python-source | 10749 | source/config |
| `modernize/semantic_ir.py` | python-source | 2647 | source/config |
| `modernize/traceability.py` | python-source | 1687 | source/config |

## modernize-V2 (28 files)

| Path | Type | Bytes | Lifecycle |
|---|---|---|---|
| `modernize_v2/__init__.py` | python-source | 1374 | source/config |
| `modernize_v2/analysis/__init__.py` | python-source | 1164 | source/config |
| `modernize_v2/analysis/scope_graph.py` | python-source | 14612 | source/config |
| `modernize_v2/analysis/scope_types.py` | python-source | 7115 | source/config |
| `modernize_v2/capabilities/__init__.py` | python-source | 1017 | source/config |
| `modernize_v2/capabilities/gate.py` | python-source | 8967 | source/config |
| `modernize_v2/capabilities/registry.py` | python-source | 9002 | source/config |
| `modernize_v2/ir/__init__.py` | python-source | 649 | source/config |
| `modernize_v2/ir/canonical.py` | python-source | 1636 | source/config |
| `modernize_v2/ir/diagnostic.py` | python-source | 12164 | source/config |
| `modernize_v2/ir/ids.py` | python-source | 11429 | source/config |
| `modernize_v2/ir/kinds.py` | python-source | 10233 | source/config |
| `modernize_v2/lexer/__init__.py` | python-source | 839 | source/config |
| `modernize_v2/lexer/keywords.py` | python-source | 7527 | source/config |
| `modernize_v2/lexer/lexer.py` | python-source | 21483 | source/config |
| `modernize_v2/lexer/tokens.py` | python-source | 3933 | source/config |
| `modernize_v2/parser/__init__.py` | python-source | 1943 | source/config |
| `modernize_v2/parser/grammar.py` | python-source | 4164 | source/config |
| `modernize_v2/parser/nodes.py` | python-source | 28577 | source/config |
| `modernize_v2/parser/parser.py` | python-source | 86938 | source/config |
| `modernize_v2/parser/recovery.py` | python-source | 2373 | source/config |
| `modernize_v2/source/__init__.py` | python-source | 1378 | source/config |
| `modernize_v2/source/source_map.py` | python-source | 12148 | source/config |
| `modernize_v2/source/workspace.py` | python-source | 21880 | source/config |
| `modernize_v2/verification/__init__.py` | python-source | 1615 | source/config |
| `modernize_v2/verification/contract.py` | python-source | 11495 | source/config |
| `modernize_v2/verification/observation.py` | python-source | 16205 | source/config |
| `modernize_v2/verification/verdict.py` | python-source | 8917 | source/config |

## execution (13 files)

| Path | Type | Bytes | Lifecycle |
|---|---|---|---|
| `execution/__init__.py` | python-source | 2154 | source/config |
| `execution/artifacts.py` | python-source | 2520 | source/config |
| `execution/contracts.py` | python-source | 2991 | source/config |
| `execution/equivalence.py` | python-source | 19647 | source/config |
| `execution/interactive_detector.py` | python-source | 6264 | source/config |
| `execution/models.py` | python-source | 4406 | source/config |
| `execution/normalization.py` | python-source | 1786 | source/config |
| `execution/observations.py` | python-source | 3511 | source/config |
| `execution/results.py` | python-source | 1994 | source/config |
| `execution/scenario_discovery.py` | python-source | 11557 | source/config |
| `execution/scenario_parser.py` | python-source | 6586 | source/config |
| `execution/scenario_runner.py` | python-source | 16149 | source/config |
| `execution/topology.py` | python-source | 2375 | source/config |

## audit (5 files)

| Path | Type | Bytes | Lifecycle |
|---|---|---|---|
| `audit/__init__.py` | python-source | 418 | source/config |
| `audit/certify.py` | python-source | 6527 | source/config |
| `audit/evidence.py` | python-source | 5300 | source/config |
| `audit/manifest.py` | python-source | 3520 | source/config |
| `audit/phase8/performance_results.json` | config/data | 203 | source/config |

## tools (18 files)

| Path | Type | Bytes | Lifecycle |
|---|---|---|---|
| `tools/acceptance_e2e.py` | python-source | 20153 | source/config |
| `tools/cobol_java_differential_verifier.py` | python-source | 32247 | source/config |
| `tools/modernize_and_verify.py` | python-source | 7460 | source/config |
| `tools/reference_runtimes/__init__.py` | python-source | 1402 | source/config |
| `tools/reference_runtimes/base.py` | python-source | 2784 | source/config |
| `tools/reference_runtimes/capability_detector.py` | python-source | 4705 | source/config |
| `tools/reference_runtimes/certification_policy.py` | python-source | 4346 | source/config |
| `tools/reference_runtimes/cics_runtime.py` | python-source | 7066 | source/config |
| `tools/reference_runtimes/database.py` | python-source | 8227 | source/config |
| `tools/reference_runtimes/differential_verifier.py` | python-source | 8796 | source/config |
| `tools/reference_runtimes/ebcdic/__init__.py` | python-source | 240 | source/config |
| `tools/reference_runtimes/ebcdic/charset.py` | python-source | 4966 | source/config |
| `tools/reference_runtimes/ebcdic/collation.py` | python-source | 2364 | source/config |
| `tools/reference_runtimes/gnu_cobol.py` | python-source | 7754 | source/config |
| `tools/reference_runtimes/hercules/__init__.py` | python-source | 131 | source/config |
| `tools/reference_runtimes/hercules/runner.py` | python-source | 3250 | source/config |
| `tools/reference_runtimes/z390/__init__.py` | python-source | 119 | source/config |
| `tools/reference_runtimes/z390/runner.py` | python-source | 7473 | source/config |

## src-cjp (2 files)

| Path | Type | Bytes | Lifecycle |
|---|---|---|---|
| `src/cjp/__init__.py` | python-source | 75 | source/config |
| `src/cjp/cli.py` | python-source | 2656 | source/config |

## legacy-fixture (25 files)

| Path | Type | Bytes | Lifecycle |
|---|---|---|---|
| `legacy/bin/claims_core.exe` | binary-executable | 47672 | tracked-binary (stale candidate) |
| `legacy/copybooks/CC-CLAIM.cpy` | cobol-copybook | 485 | source/config |
| `legacy/copybooks/CC-CONSTANTS.cpy` | cobol-copybook | 180 | source/config |
| `legacy/copybooks/CC-CUSTOMER.cpy` | cobol-copybook | 350 | source/config |
| `legacy/copybooks/CC-POLICY.cpy` | cobol-copybook | 505 | source/config |
| `legacy/data/in/claims.dat` | data/binary | 1071 | source/config |
| `legacy/data/out/.gitkeep` | (none) | 0 | source/config |
| `legacy/data/out/claim-audit.dat` | data/binary | 884 | source/config |
| `legacy/data/out/claim-exceptions.dat` | data/binary | 663 | source/config |
| `legacy/data/out/eod-claims-report.txt` | data/text | 344 | source/config |
| `legacy/data/work/.gitkeep` | (none) | 0 | source/config |
| `legacy/data/work/customer.dat` | data/binary | 8192 | source/config |
| `legacy/data/work/policy.dat` | data/binary | 8192 | source/config |
| `legacy/jcl/CLAIMSCORE.jcl` | jcl-source | 537 | source/config |
| `legacy/scripts/build.bat` | script | 155 | source/config |
| `legacy/scripts/build.sh` | script | 190 | source/config |
| `legacy/scripts/run.bat` | script | 449 | source/config |
| `legacy/scripts/run.sh` | script | 216 | source/config |
| `legacy/sql/CCCLAIM.sqc` | sql-source | 507 | source/config |
| `legacy/sql/DDL.sql` | sql-data | 778 | source/config |
| `legacy/src/CCLEGACYX.cob` | cobol-source | 945 | source/config |
| `legacy/src/CCLOAD01.cob` | cobol-source | 3188 | source/config |
| `legacy/src/CCMAIN01.cob` | cobol-source | 690 | source/config |
| `legacy/src/CCPROC01.cob` | cobol-source | 5254 | source/config |
| `legacy/src/CCREPT01.cob` | cobol-source | 2600 | source/config |

## docker (3 files)

| Path | Type | Bytes | Lifecycle |
|---|---|---|---|
| `docker/ci-seed.sql` | sql-data | 3303 | source/config |
| `docker/maven-proleap-seed-pom.xml` | build-config | 3061 | source/config |
| `docker/maven-seed-pom.xml` | build-config | 3256 | source/config |

## ci (1 files)

| Path | Type | Bytes | Lifecycle |
|---|---|---|---|
| `.github/workflows/ci.yml` | config | 21273 | source/config |

## third-party (6 files)

| Path | Type | Bytes | Lifecycle |
|---|---|---|---|
| `third_party/proleap/COMMIT` | (none) | 41 | source/config |
| `third_party/proleap/LICENSE` | (none) | 1078 | source/config |
| `third_party/proleap/README.md` | documentation | 572 | documentation |
| `third_party/proleap/VERSION` | (none) | 6 | source/config |
| `third_party/proleap/artifact/proleap-cobol-parser-4.0.0.jar` | java-archive | 2524628 | source/config |
| `third_party/proleap/artifact/proleap-poc-1.0.0.jar` | java-archive | 6665 | source/config |

## skills (7 files)

| Path | Type | Bytes | Lifecycle |
|---|---|---|---|
| `skills/certification-evidence/SKILL.md` | documentation | 943 | documentation |
| `skills/cobol-analysis/SKILL.md` | documentation | 1341 | documentation |
| `skills/copybook-expansion/SKILL.md` | documentation | 738 | documentation |
| `skills/differential-verifier/SKILL.md` | documentation | 1041 | documentation |
| `skills/ir-ast-pipeline/SKILL.md` | documentation | 828 | documentation |
| `skills/native-java-generator/SKILL.md` | documentation | 828 | documentation |
| `skills/system-architecture/SKILL.md` | documentation | 974 | documentation |

## docs (278 files)

| Path | Type | Bytes | Lifecycle |
|---|---|---|---|
| `docs/AGENTS.md` | documentation | 17542 | documentation |
| `docs/ARCHITECTURE.md` | documentation | 2564 | documentation |
| `docs/CERTIFICATION_MODEL.md` | documentation | 2724 | documentation |
| `docs/DEVELOPMENT.md` | documentation | 1107 | documentation |
| `docs/DOCUMENTATION_INDEX.md` | documentation | 9396 | documentation |
| `docs/FAIL_CLOSED_MATRIX.md` | documentation | 3746 | documentation |
| `docs/KNOWN_LIMITATIONS.md` | documentation | 8648 | documentation |
| `docs/MENTOR_VERIFIER.md` | documentation | 1929 | documentation |
| `docs/OPEN_SOURCE_INVENTORY.md` | documentation | 3280 | documentation |
| `docs/PARITY_EVIDENCE_MODEL.md` | documentation | 1703 | documentation |
| `docs/PHASE_2A_IMPLEMENTATION_REPORT.md` | documentation | 13493 | documentation |
| `docs/PHASE_2B_T2B01_IMPLEMENTATION_REPORT.md` | documentation | 9729 | documentation |
| `docs/PHASE_2B_T2B02_IMPLEMENTATION_REPORT.md` | documentation | 14752 | documentation |
| `docs/PHASE_2B_T3_HARDENING_AUDIT.md` | documentation | 14188 | documentation |
| `docs/PHASE_2B_T3_IMPLEMENTATION_REPORT.md` | documentation | 12780 | documentation |
| `docs/PHASE_2B_T4R4_IMPLEMENTATION_REPORT.md` | documentation | 8095 | documentation |
| `docs/PHASE_2B_T4R_ARCHITECTURE_REPORT.md` | documentation | 28593 | documentation |
| `docs/PHASE_2_ARCHITECTURE_V2.md` | documentation | 74964 | documentation |
| `docs/PHASE_2_DECISION_REGISTER.md` | documentation | 19798 | documentation |
| `docs/PHASE_2_TYPE_VOCABULARY.md` | documentation | 9045 | documentation |
| `docs/PHASE_2_WORK_BREAKDOWN.md` | documentation | 25090 | documentation |
| `docs/PIPELINE.md` | documentation | 2093 | documentation |
| `docs/SBOM.md` | documentation | 2296 | documentation |
| `docs/SECURITY.md` | documentation | 1409 | documentation |
| `docs/SUPPORTED_FEATURES.md` | documentation | 2279 | documentation |
| `docs/TESTING.md` | documentation | 1063 | documentation |
| `docs/UNIVERSAL_COBOL_MODERNIZATION_FINAL_REPORT.md` | documentation | 8669 | documentation |
| `docs/archive/historical/audits/AUDIT_BASELINE_BEFORE_FIXES.md` | documentation | 4847 | documentation |
| `docs/archive/historical/audits/DEEP_PROJECT_AUDIT_REPORT.md` | documentation | 20664 | documentation |
| `docs/archive/historical/audits/DEEP_PROJECT_AUDIT_REPORT_AFTER_FIXES.md` | documentation | 6324 | documentation |
| `docs/archive/historical/audits/DEEP_PROJECT_AUDIT_REPORT_FINAL.md` | documentation | 5496 | documentation |
| `docs/archive/historical/audits/FINAL_INDEPENDENT_ACCEPTANCE_AUDIT.md` | documentation | 8640 | documentation |
| `docs/archive/historical/audits/FIX_ANALYSIS_test_sql_baseline_differential.md` | documentation | 9270 | documentation |
| `docs/archive/historical/audits/SUPPORTED_COBOL_FEATURE_MATRIX.md` | documentation | 5504 | documentation |
| `docs/archive/historical/audits/TEST_REORGANIZATION_SUMMARY.md` | documentation | 8276 | documentation |
| `docs/archive/historical/audits/UNIVERSAL_TRANSFORMATION_ACCEPTANCE.md` | documentation | 2434 | documentation |
| `docs/archive/historical/audits/baseline.md` | documentation | 12208 | documentation |
| `docs/archive/historical/audits/final_audit_report.md` | documentation | 4552 | documentation |
| `docs/archive/historical/audits/gate2_capability_matrix.md` | documentation | 5210 | documentation |
| `docs/archive/historical/audits/gate2_executive_summary.md` | documentation | 6200 | documentation |
| `docs/archive/historical/audits/gate2_final_fix_summary.md` | documentation | 4831 | documentation |
| `docs/archive/historical/audits/gate2_fix_report.md` | documentation | 4425 | documentation |
| `docs/archive/historical/audits/gate2_full_audit_report.md` | documentation | 10641 | documentation |
| `docs/archive/historical/audits/gate2_gap_matrix.md` | documentation | 5029 | documentation |
| `docs/archive/historical/audits/golden_repo_gate2_root_cause.md` | documentation | 7177 | documentation |
| `docs/archive/historical/audits/implementation_plan.md` | documentation | 4836 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/API_AUDIT.md` | documentation | 612 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/ARCHITECTURAL_GAPS.md` | documentation | 759 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/ARCHITECTURE.md` | documentation | 2110 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/BENCHMARK_AUDIT.md` | documentation | 954 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/BUGS_AND_LOOPS.md` | documentation | 738 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/BUSINESS_LOGIC_AUDIT.md` | documentation | 668 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/CLAIMS_VS_REALITY.md` | documentation | 869 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/COBOL_ANALYSIS.md` | documentation | 943 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/CODE_AUDIT.md` | documentation | 1497 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/COMPLETE_WORKFLOW.md` | documentation | 1159 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/EQUIVALENCE_AUDIT.md` | documentation | 720 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/EXECUTIVE_SUMMARY.md` | documentation | 1787 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/FILE_INVENTORY.md` | documentation | 1718 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/FRONTEND_AUDIT.md` | documentation | 678 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/INTERACTIVE_EXECUTION.md` | documentation | 773 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/JAVA_ANALYSIS.md` | documentation | 841 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/MASTER_AUDIT_REPORT.md` | documentation | 879 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/PERFORMANCE_AUDIT.md` | documentation | 545 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/PIPELINE_AUDIT.md` | documentation | 1570 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/RECOMMENDATIONS.md` | documentation | 749 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/REQUIREMENTS_TRACEABILITY.md` | documentation | 755 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/RISKS.md` | documentation | 594 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/SECURITY_AUDIT.md` | documentation | 620 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/TECHNOLOGY_STACK.md` | documentation | 1362 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/TEST_AUDIT.md` | documentation | 622 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/current_state_00_MASTER_AUDIT.md` | documentation | 7644 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/current_state_01_EXECUTIVE_SUMMARY.md` | documentation | 2188 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/current_state_02_REPOSITORY_INVENTORY.md` | documentation | 3057 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/current_state_03_README_CLAIMS_VS_REALITY.md` | documentation | 2259 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/current_state_04_PIPELINE_AUDIT.md` | documentation | 2271 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/current_state_05_TEST_RESULTS.md` | documentation | 2401 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/current_state_06_LEXER_AUDIT.md` | documentation | 1417 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/current_state_07_PARSER_IR_AUDIT.md` | documentation | 1634 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/current_state_08_CONTROL_FLOW_AUDIT.md` | documentation | 1192 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/current_state_09_DATA_FLOW_AUDIT.md` | documentation | 1158 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/current_state_10_DEPENDENCY_AUDIT.md` | documentation | 1486 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/current_state_11_EQUIVALENCE_AUDIT.md` | documentation | 1447 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/current_state_12_NATIVE_JAVA_AUDIT.md` | documentation | 1668 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/current_state_13_SPRING_ENTERPRISE_AUDIT.md` | documentation | 1609 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/current_state_14_GENERICITY_AUDIT.md` | documentation | 1606 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/current_state_15_SECURITY_AUDIT.md` | documentation | 1503 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/current_state_16_ARCHITECTURE_AUDIT.md` | documentation | 1545 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/current_state_17_TEST_QUALITY_AUDIT.md` | documentation | 1345 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/current_state_18_BUG_REGISTER.md` | documentation | 1347 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/current_state_19_GAP_REGISTER.md` | documentation | 1952 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/current_state_20_FINAL_VERDICT.md` | documentation | 5627 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/current_state_SYSTEMAOPS_UNIVERSALITY_AUDIT.md` | documentation | 2011 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/final_CLEAN_INSTALL_VALIDATION.md` | documentation | 2070 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/final_FINAL_CLIENT_DEMO_READINESS.md` | documentation | 5933 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/final_FINAL_DEMO_EXECUTION.md` | documentation | 5063 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/final_FINAL_DEPLOYMENT_ACCEPTANCE.md` | documentation | 2983 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/final_FINAL_EQUIVALENCE_AUDIT.md` | documentation | 3885 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/final_FINAL_INSTALLATION_VALIDATION.md` | documentation | 2301 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/final_FINAL_PRODUCTION_STATUS.md` | documentation | 2514 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/final_FINAL_PRODUCT_ACCEPTANCE_AUDIT.md` | documentation | 7494 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/final_FINAL_RELEASE_CERTIFICATION.md` | documentation | 8124 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/final_FINAL_RELEASE_CHECKLIST.md` | documentation | 2698 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/final_FINAL_RELEASE_FREEZE.md` | documentation | 2491 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/final_FINAL_RELEASE_INVENTORY.md` | documentation | 2818 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/final_FINAL_RELEASE_MANIFEST.md` | documentation | 1768 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/final_FINAL_REPOSITORY_VERIFICATION.md` | documentation | 10036 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/final_FINAL_RUNTIME_STATE_VALIDATION.md` | documentation | 3570 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/final_FINAL_VERDICT_MATRIX.md` | documentation | 6071 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase10_PHASE10_FINAL_ACCEPTANCE.md` | documentation | 3690 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase10_PHASE10_PRODUCTION_GATE_REPORT.md` | documentation | 3057 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase10_PHASE10_RELEASE_CLOSURE_REPORT.md` | documentation | 4410 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase11_PHASE11A_UI_ACCEPTANCE.md` | documentation | 5718 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase11_PHASE11A_UI_API_CONTRACT.md` | documentation | 6774 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase11_PHASE11A_UI_INTEGRATION_GAP.md` | documentation | 13604 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase11_PHASE11B_E2E_ACCEPTANCE.md` | documentation | 3278 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase11_PHASE11B_RELEASE_STATUS.md` | documentation | 3789 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase11_PHASE11B_SECURITY_VALIDATION.md` | documentation | 3060 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase11_PHASE11B_UX_VALIDATION.md` | documentation | 2944 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase1_01_environment.md` | documentation | 1133 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase1_02_build.md` | documentation | 1055 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase1_03_tests.md` | documentation | 957 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase1_04_pipeline_execution.md` | documentation | 1282 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase1_05_interactive_execution.md` | documentation | 1093 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase1_06_bankcore_regression.md` | documentation | 948 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase1_07_equivalence_audit.md` | documentation | 1590 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase1_08_java_reality.md` | documentation | 1063 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase1_09_business_logic_baseline.md` | documentation | 803 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase1_10_coverage.md` | documentation | 768 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase1_11_frontend_smoke_test.md` | documentation | 762 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase1_12_bug_classification.md` | documentation | 990 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase1_13_static_vs_runtime.md` | documentation | 845 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase1_14_first_success_assessment.md` | documentation | 978 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase1_PHASE1_MASTER_REPORT.md` | documentation | 3471 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase2_00_architecture_review.md` | documentation | 2005 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase2_01_execution_observation.md` | documentation | 1000 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase2_01_genericity_review.md` | documentation | 1487 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase2_02_equivalence_contract.md` | documentation | 2542 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase2_02_equivalence_design.md` | documentation | 1333 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase2_02_execution_contract.md` | documentation | 915 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase2_03_equivalence_engine.md` | documentation | 863 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase2_03_native_java_design.md` | documentation | 1147 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase2_03_semantic_model.md` | documentation | 1408 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase2_04_business_rule_coverage_design.md` | documentation | 1153 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase2_04_comparison_result.md` | documentation | 1116 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase2_04_traceability_model.md` | documentation | 1530 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase2_05_dependency_coverage.md` | documentation | 1113 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase2_05_dependency_coverage_design.md` | documentation | 1012 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase2_05_normalization.md` | documentation | 669 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase2_06_native_java_architecture.md` | documentation | 995 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase2_06_security_review.md` | documentation | 1025 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase2_06_semantic_ir.md` | documentation | 1393 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase2_07_business_rule_coverage.md` | documentation | 881 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase2_07_control_flow.md` | documentation | 537 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase2_07_data_flow_control_flow.md` | documentation | 827 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase2_07_enterprise_scalability_review.md` | documentation | 862 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase2_08_data_flow.md` | documentation | 612 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase2_08_revised_implementation_plan.md` | documentation | 966 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase2_08_security_and_reliability.md` | documentation | 1007 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase2_08_traceability.md` | documentation | 1063 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase2_09_call_dependency.md` | documentation | 1113 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase2_09_dependency_coverage.md` | documentation | 1113 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase2_09_multi_repository_validation.md` | documentation | 967 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase2_10_business_rule_coverage.md` | documentation | 881 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase2_10_revised_phase2_scope.md` | documentation | 1027 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase2_10_traceability.md` | documentation | 1063 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase2_11_business_rule_coverage.md` | documentation | 881 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase2_11_native_java_architecture.md` | documentation | 995 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase2_12_multi_repository_validation.md` | documentation | 1035 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase2_12_native_java_architecture.md` | documentation | 995 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase2_13_multi_repository_validation.md` | documentation | 1035 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase2_13_security_reliability.md` | documentation | 1008 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase2_14_phase2_scope.md` | documentation | 1027 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase2_14_security_reliability.md` | documentation | 1008 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase2_15_phase2_scope.md` | documentation | 1027 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase2_PHASE2_REVIEW.md` | documentation | 5997 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase3_BASELINE.md` | documentation | 3232 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase3_CONTROL_FLOW_REPORT.md` | documentation | 3991 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase3_DATA_FLOW_REPORT.md` | documentation | 3772 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase3_DEPENDENCY_REPORT.md` | documentation | 3578 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase3_IR_REPORT.md` | documentation | 2977 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase3_LEXER_REPORT.md` | documentation | 3617 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase3_PARSER_ARCHITECTURE.md` | documentation | 3860 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase3_PARSER_REPORT.md` | documentation | 2887 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase4_PHASE4_FINAL_UNIVERSALITY_AUDIT.md` | documentation | 4891 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase4_PRODUCTION_HARDCODING_AUDIT.md` | documentation | 758546 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase5_NATIVE_HARDCODING_AUDIT.md` | documentation | 3234 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase5_NATIVE_JAVA_TRANSLATION_REPORT.md` | documentation | 676 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase5_PHASE5_VALIDATION_REPORT.md` | documentation | 583 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase6_PHASE6_COVERAGE_REPORT.md` | documentation | 4696 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase6_PHASE6_VALIDATION_REPORT.md` | documentation | 4408 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase8_PHASE8E_STRING_ARITHMETIC_REPORT.md` | documentation | 2769 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase8_PHASE8F_ENTERPRISE_UNIVERSALITY_REPORT.md` | documentation | 2455 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase8_PHASE8G_PRODUCTION_READINESS_REPORT.md` | documentation | 2352 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase8_PHASE8_FINAL_COVERAGE_REPORT.md` | documentation | 2472 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase8_PHASE8_FINAL_VALIDATION_REPORT.md` | documentation | 2381 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase9_PHASE9_FAILURE_MATRIX.md` | documentation | 3312 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase9_PHASE9_PRODUCTION_ACCEPTANCE_REPORT.md` | documentation | 5329 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase9_PHASE9_RELEASE_READINESS.md` | documentation | 4356 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase9_PHASE9_REPOSITORY_VALIDATION.md` | documentation | 4752 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/phase9_PHASE9_SECURITY_REVIEW.md` | documentation | 3074 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/post_audit_01_P0_BENCHMARK_COUPLING.md` | documentation | 2996 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/post_audit_02_P1_LIBCOBJ_DEPENDENCY.md` | documentation | 1791 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/post_audit_03_P1_WINDOWS_CLI.md` | documentation | 1388 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/post_audit_04_SECURITY_VERIFICATION.md` | documentation | 1742 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/post_audit_05_AUDIT_FINDINGS_REVALIDATION.md` | documentation | 1525 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/post_audit_06_NATIVE_JAVA_ACCEPTANCE_GATE.md` | documentation | 1752 | documentation |
| `docs/archive/historical/audits/legacy_audit_reports/post_audit_07_POST_AUDIT_MASTER_REPORT.md` | documentation | 742 | documentation |
| `docs/archive/historical/audits/pre_audit_snapshot.md` | documentation | 2643 | documentation |
| `docs/archive/historical/audits/pre_fix_snapshot.md` | documentation | 2491 | documentation |
| `docs/archive/historical/audits/walkthrough.md` | documentation | 4223 | documentation |
| `docs/archive/historical/integration/FINAL_REPOSITORY_STRUCTURE.md` | documentation | 9452 | documentation |
| `docs/archive/historical/integration/OPEN_SOURCE_REFERENCE_BASELINE.md` | documentation | 4658 | documentation |
| `docs/archive/historical/integration/REPOSITORY_STRUCTURE_AUDIT.md` | documentation | 4719 | documentation |
| `docs/archive/historical/integration/ROOT_CLEANUP_MANIFEST.md` | documentation | 4584 | documentation |
| `docs/archive/historical/integration/STRUCTURE_CLEANUP_FINAL_REPORT.md` | documentation | 6669 | documentation |
| `docs/archive/historical/integration/backport_log.md` | documentation | 7907 | documentation |
| `docs/archive/historical/integration/capability_merge_matrix.json` | config/data | 18010 | source/config |
| `docs/archive/historical/integration/capability_merge_matrix.md` | documentation | 10669 | documentation |
| `docs/archive/historical/integration/ci_verification.md` | documentation | 1936 | documentation |
| `docs/archive/historical/integration/common_test_baseline.md` | documentation | 3711 | documentation |
| `docs/archive/historical/integration/final_certification.md` | documentation | 3728 | documentation |
| `docs/archive/historical/integration/mentor_verification.md` | documentation | 2220 | documentation |
| `docs/archive/historical/integration/original_baseline_snapshot.md` | documentation | 1445 | documentation |
| `docs/archive/historical/integration/original_pre_integration_snapshot.md` | documentation | 3007 | documentation |
| `docs/archive/historical/integration/regression_analysis.md` | documentation | 3534 | documentation |
| `docs/archive/historical/integration/structure_cleanup_baseline.md` | documentation | 2779 | documentation |
| `docs/archive/historical/integration/successor_baseline_snapshot.md` | documentation | 1687 | documentation |
| `docs/archive/historical/integration/successor_reference_snapshot.md` | documentation | 3571 | documentation |
| `docs/archive/historical/integration/ui_verification.md` | documentation | 1983 | documentation |
| `docs/archive/historical/phases/CHANGES_FROM_UPLOADED_2026-08-31.md` | documentation | 4059 | documentation |
| `docs/archive/historical/phases/DB2_ARCHITECTURE_REPORT.md` | documentation | 8181 | documentation |
| `docs/archive/historical/phases/DB2_IMPLEMENTATION_VERIFICATION.md` | documentation | 6496 | documentation |
| `docs/archive/historical/phases/DB2_PRE_IMPLEMENTATION_BASELINE.md` | documentation | 2747 | documentation |
| `docs/archive/historical/phases/FINAL_REPOSITORY_AUDIT.md` | documentation | 7858 | documentation |
| `docs/archive/historical/phases/IMPLEMENTATION_STATUS_2026-08-31.md` | documentation | 2125 | documentation |
| `docs/archive/historical/phases/MASTER_PROJECT_AUDIT_REPORT.md` | documentation | 15902 | documentation |
| `docs/archive/historical/phases/PROJECT_HANDOFF.md` | documentation | 9538 | documentation |
| `docs/archive/historical/phases/REAL_DB2_FINAL_VERIFICATION.md` | documentation | 7589 | documentation |
| `docs/archive/historical/phases/UNIVERSAL_CAPABILITY_AUDIT.md` | documentation | 8710 | documentation |
| `docs/archive/historical/phases/UNSEEN_REPOSITORY_VALIDATION.md` | documentation | 2227 | documentation |
| `docs/archive/historical/phases/audit_phase1.md` | documentation | 4167 | documentation |
| `docs/archive/historical/phases/baseline-test-results.md` | documentation | 5465 | documentation |
| `docs/archive/historical/phases/baseline_frontend_checklist.md` | documentation | 4598 | documentation |
| `docs/archive/historical/phases/baseline_limits.md` | documentation | 7705 | documentation |
| `docs/archive/historical/phases/ci_and_business_logic_audit.md` | documentation | 22922 | documentation |
| `docs/archive/historical/phases/cobc-info.sha256` | checksum | 66 | source/config |
| `docs/archive/historical/phases/cobc-info.txt` | data/text | 1919 | source/config |
| `docs/archive/historical/phases/deep_audit_no_assumptions.md` | documentation | 105868 | documentation |
| `docs/archive/historical/phases/development-environment.md` | documentation | 4248 | documentation |
| `docs/archive/historical/phases/differential_tests_added.md` | documentation | 12906 | documentation |
| `docs/archive/historical/phases/limitations_and_gaps.md` | documentation | 21069 | documentation |
| `docs/archive/historical/phases/mock_middleware_architecture.md` | documentation | 13513 | documentation |
| `docs/archive/historical/phases/original_repository_baseline_audit.md` | documentation | 19672 | documentation |
| `docs/archive/historical/phases/phase01_summary.md` | documentation | 4942 | documentation |
| `docs/archive/historical/phases/phase2_summary.md` | documentation | 3896 | documentation |
| `docs/archive/historical/phases/phase3_summary.md` | documentation | 3572 | documentation |
| `docs/archive/historical/phases/pipeline_execution_limits.md` | documentation | 9253 | documentation |
| `docs/archive/historical/phases/test_charter_and_needs_analysis.md` | documentation | 17105 | documentation |
| `docs/archive/historical/phases/transformation-coverage.json` | config/data | 42088 | source/config |
| `docs/archive/historical/phases/transformation-coverage.md` | documentation | 9108 | documentation |
| `docs/archive/historical/phases/universal_roadmap.md` | documentation | 18539 | documentation |
| `docs/archive/historical/remediation/BASELINE.md` | documentation | 1912 | documentation |
| `docs/archive/historical/remediation/REMEDIATION_SUMMARY.md` | documentation | 7678 | documentation |
| `docs/audit/BUG_REGISTER.md` | documentation | 8153 | documentation |
| `docs/audit/CAPABILITY_MATRIX.md` | documentation | 7382 | documentation |
| `docs/audit/EVIDENCE_MAP.md` | documentation | 4368 | documentation |
| `docs/audit/FALSE_PASS_RISKS.md` | documentation | 4787 | documentation |
| `docs/audit/FINAL_FORENSIC_AUDIT.md` | documentation | 14393 | documentation |
| `docs/audit/LIMITATIONS_REGISTER.md` | documentation | 6665 | documentation |
| `docs/certification/FINAL_CERTIFICATION_REPORT.md` | documentation | 10001 | documentation |
| `docs/certification/MENTOR_ACCEPTANCE_SCOPE.md` | documentation | 6481 | documentation |
| `docs/integration/DOCUMENTATION_CLEANUP_BASELINE.md` | documentation | 2967 | documentation |
| `docs/integration/DOCUMENTATION_CLEANUP_FINAL_REPORT.md` | documentation | 9261 | documentation |
| `docs/integration/OPEN_SOURCE_EVALUATION.md` | documentation | 8486 | documentation |
| `docs/integration/OPEN_SOURCE_LICENSE_MATRIX.md` | documentation | 2381 | documentation |
| `docs/integration/OPEN_SOURCE_REFERENCE_BASELINE.md` | documentation | 2007 | documentation |
| `docs/integration/OPEN_SOURCE_REFERENCE_INTEGRATION_REPORT.md` | documentation | 10273 | documentation |

## reports (25 files)

| Path | Type | Bytes | Lifecycle |
|---|---|---|---|
| `reports/ACCTPROG/CERTIFICATION_REPORT.md` | documentation | 905 | documentation |
| `reports/ACCTPROG/certification_scorecard.json` | config/data | 5321 | source/config |
| `reports/ACCTPROG/differential_validation_report.json` | config/data | 3426 | source/config |
| `reports/ACCTPROG/differential_validation_report.md` | documentation | 1867 | documentation |
| `reports/CICSREST01/CERTIFICATION_REPORT.md` | documentation | 907 | documentation |
| `reports/CICSREST01/certification_scorecard.json` | config/data | 4969 | source/config |
| `reports/CICSREST01/differential_validation_report.json` | config/data | 3063 | source/config |
| `reports/CICSREST01/differential_validation_report.md` | documentation | 1860 | documentation |
| `reports/DB2SELECT01/CERTIFICATION_REPORT.md` | documentation | 908 | documentation |
| `reports/DB2SELECT01/certification_scorecard.json` | config/data | 5151 | source/config |
| `reports/DB2SELECT01/differential_validation_report.json` | config/data | 3208 | source/config |
| `reports/DB2SELECT01/differential_validation_report.md` | documentation | 1792 | documentation |
| `reports/JCLBATCH01/CERTIFICATION_REPORT.md` | documentation | 907 | documentation |
| `reports/JCLBATCH01/certification_scorecard.json` | config/data | 5092 | source/config |
| `reports/JCLBATCH01/differential_validation_report.json` | config/data | 3179 | source/config |
| `reports/JCLBATCH01/differential_validation_report.md` | documentation | 1907 | documentation |
| `reports/MENTOR_DEMO_SUMMARY.md` | documentation | 1023 | documentation |
| `reports/MULTIFILE01/CERTIFICATION_REPORT.md` | documentation | 908 | documentation |
| `reports/MULTIFILE01/certification_scorecard.json` | config/data | 5724 | source/config |
| `reports/MULTIFILE01/differential_validation_report.json` | config/data | 3748 | source/config |
| `reports/MULTIFILE01/differential_validation_report.md` | documentation | 2027 | documentation |
| `reports/SIMPLEBASELINE01/CERTIFICATION_REPORT.md` | documentation | 913 | documentation |
| `reports/SIMPLEBASELINE01/certification_scorecard.json` | config/data | 5168 | source/config |
| `reports/SIMPLEBASELINE01/differential_validation_report.json` | config/data | 3313 | source/config |
| `reports/SIMPLEBASELINE01/differential_validation_report.md` | documentation | 1956 | documentation |

## tests (873 files)

| Path | Type | Bytes | Lifecycle |
|---|---|---|---|
| `tests/acceptance/__init__.py` | python-source | 31 | test |
| `tests/acceptance/test_unseen_repositories.py` | python-source | 10105 | test |
| `tests/component/cics/__init__.py` | python-source | 26 | test |
| `tests/component/cics/test_bms_mapping.py` | python-source | 3583 | test |
| `tests/component/cics/test_cics_map_semantics.py` | python-source | 2084 | test |
| `tests/component/cics/test_cics_modernization.py` | python-source | 6941 | test |
| `tests/component/db/__init__.py` | python-source | 26 | test |
| `tests/component/db/test_db2_configuration.py` | python-source | 8647 | test |
| `tests/component/db/test_db2_error_mapper.py` | python-source | 4859 | test |
| `tests/component/db/test_db2_jcc_driver.py` | python-source | 2018 | test |
| `tests/component/db/test_db2_modernization.py` | python-source | 5762 | test |
| `tests/component/db/test_sql_advanced.py` | python-source | 3673 | test |
| `tests/component/db/test_sql_baseline.py` | python-source | 4765 | test |
| `tests/component/db/test_sql_literals_translation.py` | python-source | 1637 | test |
| `tests/component/db/test_sqlcode_loop_regression.py` | python-source | 9147 | test |
| `tests/component/jcl/__init__.py` | python-source | 26 | test |
| `tests/component/jcl/test_jcl_modernization.py` | python-source | 6633 | test |
| `tests/component/jcl/test_jcl_symbols_complete.py` | python-source | 3658 | test |
| `tests/component/jcl/test_jcl_utilities.py` | python-source | 7096 | test |
| `tests/component/vsam/__init__.py` | python-source | 26 | test |
| `tests/component/vsam/test_ksds_baseline.py` | python-source | 2975 | test |
| `tests/component/vsam/test_vsam_ksds_stage2.py` | python-source | 2903 | test |
| `tests/component/vsam/test_vsam_rrds.py` | python-source | 3143 | test |
| `tests/differential/__init__.py` | python-source | 55 | test |
| `tests/differential/test_mutation.py` | python-source | 4400 | test |
| `tests/differential/test_negative_gates.py` | python-source | 9159 | test |
| `tests/e2e/__init__.py` | python-source | 0 | test |
| `tests/e2e/differential/cics/__init__.py` | python-source | 65 | test |
| `tests/e2e/differential/control_flow/__init__.py` | python-source | 57 | test |
| `tests/e2e/differential/files/__init__.py` | python-source | 71 | test |
| `tests/e2e/differential/files/test_filestat01.py` | python-source | 3302 | test |
| `tests/e2e/differential/jcl/__init__.py` | python-source | 50 | test |
| `tests/e2e/differential/numeric/test_sizeerr01.py` | python-source | 2354 | test |
| `tests/e2e/differential/sql/__init__.py` | python-source | 94 | test |
| `tests/e2e/differential/sql/test_db2curnull01.py` | python-source | 4181 | test |
| `tests/e2e/differential/storage/__init__.py` | python-source | 46 | test |
| `tests/e2e/differential/storage/test_occurs01.py` | python-source | 2831 | test |
| `tests/e2e/differential/storage/test_redefines01.py` | python-source | 2597 | test |
| `tests/e2e/differential/storage/test_redefines_occurs.py` | python-source | 49 | test |
| `tests/e2e/fixtures/goldenpay-fresh.zip` | archive | 1007 | test |
| `tests/e2e/fixtures/inventory01-fresh.zip` | archive | 1430 | test |
| `tests/e2e/fixtures/invmgr-fresh.zip` | archive | 893 | test |
| `tests/e2e/fixtures/salesprog-fresh.zip` | archive | 2097 | test |
| `tests/e2e/test_e2e_modernization.py` | python-source | 42680 | test |
| `tests/e2e/test_e2e_multi_workload.py` | python-source | 49464 | test |
| `tests/fixtures/archives/A-PAYONLY.zip` | archive | 8978 | test |
| `tests/fixtures/archives/F-PAYFAIL.zip` | archive | 7657 | test |
| `tests/fixtures/archives/INVMGR.zip` | archive | 30146 | test |
| `tests/fixtures/unpacked/cics-genapp-main/meta.json` | config/data | 58 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/.gitattributes` | (none) | 497 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/.gitignore` | (none) | 36 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/Changes.md` | documentation | 2332 | documentation |
| `tests/fixtures/unpacked/cics-genapp-main/repo/LICENSE` | (none) | 14476 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/MAINTAINERS.md` | documentation | 162 | documentation |
| `tests/fixtures/unpacked/cics-genapp-main/repo/README.md` | documentation | 2254 | documentation |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/LGACDB01.CBL` | cobol-source | 13679 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/LGACDB02.CBL` | cobol-source | 10139 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/LGACUS01.CBL` | cobol-source | 8146 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/LGACVS01.CBL` | cobol-source | 5656 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/LGAPDB01.CBL` | cobol-source | 23118 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/LGAPOL01.CBL` | cobol-source | 7808 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/LGAPVS01.CBL` | cobol-source | 8576 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/LGASTAT1.CBL` | cobol-source | 5820 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/LGCMAREA.CPY` | cobol-copybook | 5561 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/LGDPDB01.CBL` | cobol-source | 11262 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/LGDPOL01.CBL` | cobol-source | 8477 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/LGDPVS01.CBL` | cobol-source | 6199 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/LGICDB01.CBL` | cobol-source | 10582 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/LGICUS01.CBL` | cobol-source | 7473 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/LGICVS01.CBL` | cobol-source | 9146 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/LGIPDB01.CBL` | cobol-source | 39617 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/LGIPOL01.CBL` | cobol-source | 6264 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/LGIPVS01.CBL` | cobol-source | 5913 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/LGPOLICY.CPY` | cobol-copybook | 5399 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/LGSETUP.CBL` | cobol-source | 22301 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/LGSTSQ.CBL` | cobol-source | 4696 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/LGTESTC1.CBL` | cobol-source | 12930 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/LGTESTP1.CBL` | cobol-source | 12407 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/LGTESTP2.CBL` | cobol-source | 11694 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/LGTESTP3.CBL` | cobol-source | 11528 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/LGTESTP4.CBL` | cobol-source | 12866 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/LGUCDB01.CBL` | cobol-source | 9368 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/LGUCUS01.CBL` | cobol-source | 7599 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/LGUCVS01.CBL` | cobol-source | 6397 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/LGUPDB01.CBL` | cobol-source | 22972 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/LGUPOL01.CBL` | cobol-source | 9110 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/LGUPVS01.CBL` | cobol-source | 9530 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/LGWEBST5.CBL` | cobol-source | 35695 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/LINKPARM.TXT` | data/text | 24 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/POLLOO2.CPY` | cobol-copybook | 609 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/POLLOOK.CPY` | cobol-copybook | 528 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/README.MD` | documentation | 3915 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/SOAIC01.CPY` | cobol-copybook | 1171 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/SOAIPB1.CPY` | cobol-copybook | 1760 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/SOAIPE1.CPY` | cobol-copybook | 1407 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/SOAIPH1.CPY` | cobol-copybook | 1364 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/SOAIPM1.CPY` | cobol-copybook | 1515 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/SOAVCII.CPY` | cobol-copybook | 494 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/SOAVCIO.CPY` | cobol-copybook | 541 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/SOAVPII.CPY` | cobol-copybook | 1040 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/SOAVPIO.CPY` | cobol-copybook | 1180 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/SQLCA.CPY` | cobol-copybook | 107 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/SSMAP.BMS` | bms-source | 33568 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/_preprocessed/base/src/SSMAP.CPY` | cobol-copybook | 107 | preprocessed-fixture |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/Architecture.md` | documentation | 7382 | documentation |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/Building.md` | documentation | 3725 | documentation |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/Installation.md` | documentation | 6312 | documentation |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/README.md` | documentation | 2833 | documentation |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/Reference.md` | documentation | 6552 | documentation |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/Testing.md` | documentation | 1969 | documentation |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/bin/install.sh` | script | 1639 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/cntl/README.md` | documentation | 3140 | documentation |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/cntl/adef121.jcl` | jcl-source | 1975 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/cntl/asmmap.jcl` | jcl-source | 2818 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/cntl/cdef121.jcl` | jcl-source | 6645 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/cntl/cdef122.jcl` | jcl-source | 10359 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/cntl/cdef123.jcl` | jcl-source | 12067 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/cntl/cdef124.jcl` | jcl-source | 956 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/cntl/cdef125.jcl` | jcl-source | 1012 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/cntl/cobol.jcl` | jcl-source | 4536 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/cntl/cpsmde2.jcl` | jcl-source | 5298 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/cntl/db2bind.jcl` | jcl-source | 7294 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/cntl/db2cre.jcl` | jcl-source | 50356 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/cntl/db2del.jcl` | jcl-source | 1522 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/cntl/defdrep.jcl` | jcl-source | 1850 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/cntl/defwrep.jcl` | jcl-source | 1638 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/cntl/itpentr.jcl` | jcl-source | 463 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/cntl/itpll.jcl` | jcl-source | 349 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/cntl/itpstl.jcl` | jcl-source | 1182 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/cntl/sampcma.jcl` | jcl-source | 2399 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/cntl/sampncs.jcl` | jcl-source | 307 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/cntl/samptsq.jcl` | jcl-source | 362 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/cntl/sampwui.jcl` | jcl-source | 3159 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/cntl/wsaac01.jcl` | jcl-source | 886 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/cntl/wsaap01.jcl` | jcl-source | 2473 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/cntl/wsaic01.jcl` | jcl-source | 886 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/cntl/wsaip01.jcl` | jcl-source | 3025 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/cntl/wsauc01.jcl` | jcl-source | 885 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/cntl/wsaup01.jcl` | jcl-source | 2476 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/cntl/wsavc01.jcl` | jcl-source | 899 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/cntl/wsavp01.jcl` | jcl-source | 897 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/data/README.md` | documentation | 2847 | documentation |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/data/ksdscust.txt` | data/text | 2268 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/data/ksdspoly.txt` | data/text | 660 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/event-bindings/README.md` | documentation | 164 | documentation |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/event-bindings/Transaction_Counters.evbind` | config | 3441 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/exec/README.md` | documentation | 2470 | documentation |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/exec/cust1.rexx` | script | 4594 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/exec/mac1.rexx` | script | 2876 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/images/initial_topology.jpg` | image | 53585 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/README.md` | documentation | 3893 | documentation |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/lgacdb01.cbl` | cobol-source | 14002 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/lgacdb02.cbl` | cobol-source | 9927 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/lgacus01.cbl` | cobol-source | 7874 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/lgacvs01.cbl` | cobol-source | 5329 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/lgapdb01.cbl` | cobol-source | 24354 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/lgapol01.cbl` | cobol-source | 7480 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/lgapvs01.cbl` | cobol-source | 8304 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/lgastat1.cbl` | cobol-source | 5645 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/lgcmarea.cpy` | cobol-copybook | 5561 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/lgdpdb01.cbl` | cobol-source | 11031 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/lgdpol01.cbl` | cobol-source | 8144 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/lgdpvs01.cbl` | cobol-source | 5899 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/lgicdb01.cbl` | cobol-source | 10581 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/lgicus01.cbl` | cobol-source | 7180 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/lgicvs01.cbl` | cobol-source | 8955 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/lgipdb01.cbl` | cobol-source | 42079 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/lgipol01.cbl` | cobol-source | 6017 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/lgipvs01.cbl` | cobol-source | 5744 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/lgpolicy.cpy` | cobol-copybook | 5399 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/lgsetup.cbl` | cobol-source | 22008 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/lgstsq.cbl` | cobol-source | 4510 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/lgtestc1.cbl` | cobol-source | 12572 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/lgtestp1.cbl` | cobol-source | 11937 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/lgtestp2.cbl` | cobol-source | 11228 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/lgtestp3.cbl` | cobol-source | 11064 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/lgtestp4.cbl` | cobol-source | 12441 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/lgucdb01.cbl` | cobol-source | 9370 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/lgucus01.cbl` | cobol-source | 7370 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/lgucvs01.cbl` | cobol-source | 5979 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/lgupdb01.cbl` | cobol-source | 22944 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/lgupol01.cbl` | cobol-source | 8720 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/lgupvs01.cbl` | cobol-source | 9112 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/lgwebst5.cbl` | cobol-source | 35721 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/linkparm.txt` | data/text | 24 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/polloo2.cpy` | cobol-copybook | 609 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/pollook.cpy` | cobol-copybook | 528 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/soaic01.cpy` | cobol-copybook | 1171 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/soaipb1.cpy` | cobol-copybook | 1760 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/soaipe1.cpy` | cobol-copybook | 1407 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/soaiph1.cpy` | cobol-copybook | 1364 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/soaipm1.cpy` | cobol-copybook | 1515 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/soavcii.cpy` | cobol-copybook | 494 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/soavcio.cpy` | cobol-copybook | 541 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/soavpii.cpy` | cobol-copybook | 1040 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/soavpio.cpy` | cobol-copybook | 1180 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/src/ssmap.bms` | bms-source | 32812 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/wsim/#ssvars.txt` | data/text | 5708 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/wsim/README.md` | documentation | 3391 | documentation |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/wsim/ccolor.txt` | data/text | 489 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/wsim/cmake.txt` | data/text | 425 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/wsim/cmodel.txt` | data/text | 439 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/wsim/ctype.txt` | data/text | 314 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/wsim/fname.txt` | data/text | 9691 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/wsim/genapp.txt` | data/text | 1503 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/wsim/htype.txt` | data/text | 347 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/wsim/oncics.txt` | data/text | 624 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/wsim/pcode.txt` | data/text | 677643 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/wsim/ptype.txt` | data/text | 363 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/wsim/rtype.txt` | data/text | 175 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/wsim/sname.txt` | data/text | 31979 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/wsim/ssc1a1.txt` | data/text | 1934 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/wsim/ssc1a2.txt` | data/text | 786 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/wsim/ssc1i1.txt` | data/text | 1126 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/wsim/ssp1a1.txt` | data/text | 2559 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/wsim/ssp1a2.txt` | data/text | 1165 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/wsim/ssp1d1.txt` | data/text | 1683 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/wsim/ssp1i1.txt` | data/text | 1517 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/wsim/ssp1u1.txt` | data/text | 3153 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/wsim/ssp2a1.txt` | data/text | 2121 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/wsim/ssp2a2.txt` | data/text | 1045 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/wsim/ssp2d1.txt` | data/text | 1683 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/wsim/ssp2i1.txt` | data/text | 1516 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/wsim/ssp2u1.txt` | data/text | 3050 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/wsim/ssp3a1.txt` | data/text | 2177 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/wsim/ssp3a2.txt` | data/text | 1074 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/wsim/ssp3d1.txt` | data/text | 1685 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/wsim/ssp3i1.txt` | data/text | 1517 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/wsim/ssp3u1.txt` | data/text | 3136 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/wsim/ssp4a1.txt` | data/text | 3164 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/wsim/ssp4d1.txt` | data/text | 1694 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/wsim/ssp4i1.txt` | data/text | 1517 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/wsim/stop.txt` | data/text | 455 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/wsim/waserror.txt` | data/text | 918 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/wsim/wsc1a1.txt` | data/text | 3987 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/wsim/wsc1i1.txt` | data/text | 4114 | test |
| `tests/fixtures/unpacked/cics-genapp-main/repo/base/wsim/wslgcf.txt` | data/text | 3594 | test |
| `tests/fixtures/unpacked/legacy-insurance/meta.json` | config/data | 81 | test |
| `tests/fixtures/unpacked/legacy-insurance/repo/.gitignore` | (none) | 58 | test |
| `tests/fixtures/unpacked/legacy-insurance/repo/LICENSE` | (none) | 338 | test |
| `tests/fixtures/unpacked/legacy-insurance/repo/README.md` | documentation | 1879 | documentation |
| `tests/fixtures/unpacked/legacy-insurance/repo/REPOSITORY_STATUS.md` | documentation | 483 | documentation |
| `tests/fixtures/unpacked/legacy-insurance/repo/_preprocessed/cics/maps/CLAIMMP.CPY` | cobol-copybook | 125 | preprocessed-fixture |
| `tests/fixtures/unpacked/legacy-insurance/repo/_preprocessed/cics/maps/POLICYMP.CPY` | cobol-copybook | 98 | preprocessed-fixture |
| `tests/fixtures/unpacked/legacy-insurance/repo/_preprocessed/cics/programs/CLMTRANS.cbl` | cobol-source | 529 | preprocessed-fixture |
| `tests/fixtures/unpacked/legacy-insurance/repo/_preprocessed/cics/programs/POLTRANS.cbl` | cobol-source | 425 | preprocessed-fixture |
| `tests/fixtures/unpacked/legacy-insurance/repo/_preprocessed/cobol/batch/BACKUP.cbl` | cobol-source | 149 | preprocessed-fixture |
| `tests/fixtures/unpacked/legacy-insurance/repo/_preprocessed/cobol/batch/BATCHCLM.cbl` | cobol-source | 881 | preprocessed-fixture |
| `tests/fixtures/unpacked/legacy-insurance/repo/_preprocessed/cobol/batch/DAILYREP.cbl` | cobol-source | 416 | preprocessed-fixture |
| `tests/fixtures/unpacked/legacy-insurance/repo/_preprocessed/cobol/batch/PAYBATCH.cbl` | cobol-source | 187 | preprocessed-fixture |
| `tests/fixtures/unpacked/legacy-insurance/repo/_preprocessed/cobol/batch/POLICYLOAD.cbl` | cobol-source | 247 | preprocessed-fixture |
| `tests/fixtures/unpacked/legacy-insurance/repo/_preprocessed/cobol/common/COMMONCALL.cbl` | cobol-source | 254 | preprocessed-fixture |
| `tests/fixtures/unpacked/legacy-insurance/repo/_preprocessed/cobol/copybooks/CLAIM.CPY` | cobol-copybook | 201 | preprocessed-fixture |
| `tests/fixtures/unpacked/legacy-insurance/repo/_preprocessed/cobol/copybooks/COMMON.CPY` | cobol-copybook | 93 | preprocessed-fixture |
| `tests/fixtures/unpacked/legacy-insurance/repo/_preprocessed/cobol/copybooks/CUSTOMER.CPY` | cobol-copybook | 162 | preprocessed-fixture |
| `tests/fixtures/unpacked/legacy-insurance/repo/_preprocessed/cobol/copybooks/PAYMENT.CPY` | cobol-copybook | 164 | preprocessed-fixture |
| `tests/fixtures/unpacked/legacy-insurance/repo/_preprocessed/cobol/copybooks/POLICY.CPY` | cobol-copybook | 202 | preprocessed-fixture |
| `tests/fixtures/unpacked/legacy-insurance/repo/_preprocessed/cobol/online/AUDIT01.cbl` | cobol-source | 484 | preprocessed-fixture |
| `tests/fixtures/unpacked/legacy-insurance/repo/_preprocessed/cobol/online/CLAIM01.cbl` | cobol-source | 606 | preprocessed-fixture |
| `tests/fixtures/unpacked/legacy-insurance/repo/_preprocessed/cobol/online/CLAIM02.cbl` | cobol-source | 654 | preprocessed-fixture |
| `tests/fixtures/unpacked/legacy-insurance/repo/_preprocessed/cobol/online/CLAIM03.cbl` | cobol-source | 298 | preprocessed-fixture |
| `tests/fixtures/unpacked/legacy-insurance/repo/_preprocessed/cobol/online/CUSTOMER01.cbl` | cobol-source | 482 | preprocessed-fixture |
| `tests/fixtures/unpacked/legacy-insurance/repo/_preprocessed/cobol/online/PAYMENT01.cbl` | cobol-source | 673 | preprocessed-fixture |
| `tests/fixtures/unpacked/legacy-insurance/repo/_preprocessed/cobol/online/POLICY01.cbl` | cobol-source | 804 | preprocessed-fixture |
| `tests/fixtures/unpacked/legacy-insurance/repo/bms/CLAIMMP.bms` | bms-source | 327 | test |
| `tests/fixtures/unpacked/legacy-insurance/repo/bms/POLICYMP.bms` | bms-source | 272 | test |
| `tests/fixtures/unpacked/legacy-insurance/repo/cics/maps/CLAIMMP.cpy` | cobol-copybook | 125 | test |
| `tests/fixtures/unpacked/legacy-insurance/repo/cics/maps/POLICYMP.cpy` | cobol-copybook | 98 | test |
| `tests/fixtures/unpacked/legacy-insurance/repo/cics/programs/CLMTRANS.cbl` | cobol-source | 253 | test |
| `tests/fixtures/unpacked/legacy-insurance/repo/cics/programs/POLTRANS.cbl` | cobol-source | 211 | test |
| `tests/fixtures/unpacked/legacy-insurance/repo/cobol/batch/BACKUP.cbl` | cobol-source | 114 | test |
| `tests/fixtures/unpacked/legacy-insurance/repo/cobol/batch/BATCHCLM.cbl` | cobol-source | 699 | test |
| `tests/fixtures/unpacked/legacy-insurance/repo/cobol/batch/DAILYREP.cbl` | cobol-source | 292 | test |
| `tests/fixtures/unpacked/legacy-insurance/repo/cobol/batch/PAYBATCH.cbl` | cobol-source | 145 | test |
| `tests/fixtures/unpacked/legacy-insurance/repo/cobol/batch/POLICYLOAD.cbl` | cobol-source | 150 | test |
| `tests/fixtures/unpacked/legacy-insurance/repo/cobol/common/COMMONCALL.cbl` | cobol-source | 198 | test |
| `tests/fixtures/unpacked/legacy-insurance/repo/cobol/copybooks/CLAIM.cpy` | cobol-copybook | 201 | test |
| `tests/fixtures/unpacked/legacy-insurance/repo/cobol/copybooks/COMMON.cpy` | cobol-copybook | 93 | test |
| `tests/fixtures/unpacked/legacy-insurance/repo/cobol/copybooks/CUSTOMER.cpy` | cobol-copybook | 162 | test |
| `tests/fixtures/unpacked/legacy-insurance/repo/cobol/copybooks/PAYMENT.cpy` | cobol-copybook | 164 | test |
| `tests/fixtures/unpacked/legacy-insurance/repo/cobol/copybooks/POLICY.cpy` | cobol-copybook | 202 | test |
| `tests/fixtures/unpacked/legacy-insurance/repo/cobol/online/AUDIT01.cbl` | cobol-source | 365 | test |
| `tests/fixtures/unpacked/legacy-insurance/repo/cobol/online/CLAIM01.cbl` | cobol-source | 347 | test |
| `tests/fixtures/unpacked/legacy-insurance/repo/cobol/online/CLAIM02.cbl` | cobol-source | 521 | test |
| `tests/fixtures/unpacked/legacy-insurance/repo/cobol/online/CLAIM03.cbl` | cobol-source | 186 | test |
| `tests/fixtures/unpacked/legacy-insurance/repo/cobol/online/CUSTOMER01.cbl` | cobol-source | 360 | test |
| `tests/fixtures/unpacked/legacy-insurance/repo/cobol/online/PAYMENT01.cbl` | cobol-source | 471 | test |
| `tests/fixtures/unpacked/legacy-insurance/repo/cobol/online/POLICY01.cbl` | cobol-source | 493 | test |
| `tests/fixtures/unpacked/legacy-insurance/repo/data/expected/claims.expected` | data/text | 134 | test |
| `tests/fixtures/unpacked/legacy-insurance/repo/data/input/claims.in` | data/text | 118 | test |
| `tests/fixtures/unpacked/legacy-insurance/repo/db2/schema.sql` | sql-data | 1657 | test |
| `tests/fixtures/unpacked/legacy-insurance/repo/db2/seed.sql` | sql-data | 382 | test |
| `tests/fixtures/unpacked/legacy-insurance/repo/db2/test-data.sql` | sql-data | 299 | test |
| `tests/fixtures/unpacked/legacy-insurance/repo/docs/ARCHITECTURE.md` | documentation | 984 | documentation |
| `tests/fixtures/unpacked/legacy-insurance/repo/docs/BUSINESS_RULES.md` | documentation | 506 | documentation |
| `tests/fixtures/unpacked/legacy-insurance/repo/docs/CICS.md` | documentation | 327 | documentation |
| `tests/fixtures/unpacked/legacy-insurance/repo/docs/DATABASE.md` | documentation | 313 | documentation |
| `tests/fixtures/unpacked/legacy-insurance/repo/docs/JCL.md` | documentation | 199 | documentation |
| `tests/fixtures/unpacked/legacy-insurance/repo/docs/TESTING.md` | documentation | 311 | documentation |
| `tests/fixtures/unpacked/legacy-insurance/repo/docs/VSAM.md` | documentation | 179 | documentation |
| `tests/fixtures/unpacked/legacy-insurance/repo/jcl/JOB001_POLICY_LOAD.jcl` | jcl-source | 166 | test |
| `tests/fixtures/unpacked/legacy-insurance/repo/jcl/JOB002_CLAIM_BATCH.jcl` | jcl-source | 169 | test |
| `tests/fixtures/unpacked/legacy-insurance/repo/jcl/JOB003_PAYMENT_BATCH.jcl` | jcl-source | 105 | test |
| `tests/fixtures/unpacked/legacy-insurance/repo/jcl/JOB004_DAILY_REPORT.jcl` | jcl-source | 117 | test |
| `tests/fixtures/unpacked/legacy-insurance/repo/jcl/JOB005_BACKUP.jcl` | jcl-source | 81 | test |
| `tests/fixtures/unpacked/legacy-insurance/repo/scripts/validate_structure.py` | python-source | 495 | test |
| `tests/fixtures/unpacked/legacy-insurance/repo/tests/test_golden_reference.py` | python-source | 916 | test |
| `tests/fixtures/unpacked/legacy-insurance/repo/vsam/policy.ksds` | data/binary | 141 | test |
| `tests/fixtures_spec.json` | config/data | 7759 | test |
| `tests/integration/ui/test_hardening_parity_and_ui.py` | python-source | 4730 | test |
| `tests/integration/ui/test_interactive_execution.py` | python-source | 16460 | test |
| `tests/integration/ui/test_phase11_ui_integration.py` | python-source | 10411 | test |
| `tests/integration/ui/test_phase11b_e2e.py` | python-source | 6129 | test |
| `tests/integration/ui/test_phase11b_failure_ux.py` | python-source | 9884 | test |
| `tests/logical_audit_test.py` | python-source | 8892 | test |
| `tests/reference_runtime/__init__.py` | python-source | 39 | test |
| `tests/reference_runtime/test_ebcdic_collation.py` | python-source | 1744 | test |
| `tests/reference_runtime/test_ebcdic_conversion.py` | python-source | 3119 | test |
| `tests/reference_runtime/test_reference_differential.py` | python-source | 4879 | test |
| `tests/reference_runtime/test_reference_negative.py` | python-source | 4565 | test |
| `tests/reference_runtime/test_reference_runtime_isolation.py` | python-source | 1595 | test |
| `tests/reference_runtime/test_z390_availability.py` | python-source | 1349 | test |
| `tests/reference_runtime/test_z390_batch.py` | python-source | 993 | test |
| `tests/reference_runtime/test_z390_cics.py` | python-source | 338 | test |
| `tests/reference_runtime/test_z390_vsam.py` | python-source | 743 | test |
| `tests/repos/A-PAYONLY/generated/PAYMAIN$1.class` | java-bytecode | 1123 | generated-artifact (stale candidate) |
| `tests/repos/A-PAYONLY/generated/PAYMAIN$2.class` | java-bytecode | 1123 | generated-artifact (stale candidate) |
| `tests/repos/A-PAYONLY/generated/PAYMAIN$3.class` | java-bytecode | 1123 | generated-artifact (stale candidate) |
| `tests/repos/A-PAYONLY/generated/PAYMAIN$4.class` | java-bytecode | 1942 | generated-artifact (stale candidate) |
| `tests/repos/A-PAYONLY/generated/PAYMAIN$5.class` | java-bytecode | 1614 | generated-artifact (stale candidate) |
| `tests/repos/A-PAYONLY/generated/PAYMAIN.class` | java-bytecode | 6227 | generated-artifact (stale candidate) |
| `tests/repos/A-PAYONLY/generated/PAYMAIN.java` | java-source | 8317 | generated-artifact (stale candidate) |
| `tests/repos/A-PAYONLY/src/PAYMAIN.cob` | cobol-source | 585 | test |
| `tests/repos/ACCTPROG/ACCTCALC.so` | binary-library | 17600 | tracked-binary (stale candidate) |
| `tests/repos/ACCTPROG/ACCTPROG.so` | binary-library | 18328 | tracked-binary (stale candidate) |
| `tests/repos/ACCTPROG/_preprocessed/copybooks/ACTLNK.CPY` | cobol-copybook | 198 | preprocessed-fixture |
| `tests/repos/ACCTPROG/_preprocessed/copybooks/ACTREC.CPY` | cobol-copybook | 191 | preprocessed-fixture |
| `tests/repos/ACCTPROG/_preprocessed/copybooks/ACTREP.CPY` | cobol-copybook | 149 | preprocessed-fixture |
| `tests/repos/ACCTPROG/_preprocessed/generated/ACCTCALC$1.class` | java-bytecode | 1128 | generated-artifact (stale candidate) |
| `tests/repos/ACCTPROG/_preprocessed/generated/ACCTCALC$2.class` | java-bytecode | 1128 | generated-artifact (stale candidate) |
| `tests/repos/ACCTPROG/_preprocessed/generated/ACCTCALC$3.class` | java-bytecode | 1128 | generated-artifact (stale candidate) |
| `tests/repos/ACCTPROG/_preprocessed/generated/ACCTCALC$4$1.class` | java-bytecode | 1166 | generated-artifact (stale candidate) |
| `tests/repos/ACCTPROG/_preprocessed/generated/ACCTCALC$4$2.class` | java-bytecode | 1003 | generated-artifact (stale candidate) |
| `tests/repos/ACCTPROG/_preprocessed/generated/ACCTCALC$4$3.class` | java-bytecode | 1168 | generated-artifact (stale candidate) |
| `tests/repos/ACCTPROG/_preprocessed/generated/ACCTCALC$4$4.class` | java-bytecode | 1003 | generated-artifact (stale candidate) |
| `tests/repos/ACCTPROG/_preprocessed/generated/ACCTCALC$4$5.class` | java-bytecode | 1166 | generated-artifact (stale candidate) |
| `tests/repos/ACCTPROG/_preprocessed/generated/ACCTCALC$4$6.class` | java-bytecode | 1168 | generated-artifact (stale candidate) |
| `tests/repos/ACCTPROG/_preprocessed/generated/ACCTCALC$4.class` | java-bytecode | 2492 | generated-artifact (stale candidate) |
| `tests/repos/ACCTPROG/_preprocessed/generated/ACCTCALC.class` | java-bytecode | 6376 | generated-artifact (stale candidate) |
| `tests/repos/ACCTPROG/_preprocessed/generated/ACCTCALC.java` | java-source | 9993 | generated-artifact (stale candidate) |
| `tests/repos/ACCTPROG/_preprocessed/generated/ACCTPROG$1.class` | java-bytecode | 1128 | generated-artifact (stale candidate) |
| `tests/repos/ACCTPROG/_preprocessed/generated/ACCTPROG$2.class` | java-bytecode | 1128 | generated-artifact (stale candidate) |
| `tests/repos/ACCTPROG/_preprocessed/generated/ACCTPROG$3.class` | java-bytecode | 1128 | generated-artifact (stale candidate) |
| `tests/repos/ACCTPROG/_preprocessed/generated/ACCTPROG$4.class` | java-bytecode | 2365 | generated-artifact (stale candidate) |
| `tests/repos/ACCTPROG/_preprocessed/generated/ACCTPROG$5.class` | java-bytecode | 3927 | generated-artifact (stale candidate) |
| `tests/repos/ACCTPROG/_preprocessed/generated/ACCTPROG$6.class` | java-bytecode | 1414 | generated-artifact (stale candidate) |
| `tests/repos/ACCTPROG/_preprocessed/generated/ACCTPROG.class` | java-bytecode | 8294 | generated-artifact (stale candidate) |
| `tests/repos/ACCTPROG/_preprocessed/generated/ACCTPROG.java` | java-source | 17169 | generated-artifact (stale candidate) |
| `tests/repos/ACCTPROG/_preprocessed/src/ACCTCALC.cob` | cobol-source | 428 | preprocessed-fixture |
| `tests/repos/ACCTPROG/_preprocessed/src/ACCTPROG.cob` | cobol-source | 1544 | preprocessed-fixture |
| `tests/repos/ACCTPROG/acctprog.exe` | binary-executable | 20272 | tracked-binary (stale candidate) |
| `tests/repos/ACCTPROG/copybooks/ACTLNK.cpy` | cobol-copybook | 198 | test |
| `tests/repos/ACCTPROG/copybooks/ACTREC.cpy` | cobol-copybook | 191 | test |
| `tests/repos/ACCTPROG/copybooks/ACTREP.cpy` | cobol-copybook | 149 | test |
| `tests/repos/ACCTPROG/data/final-result-report.txt` | data/text | 65 | test |
| `tests/repos/ACCTPROG/data/raw-source-data.bin` | data/binary | 76 | test |
| `tests/repos/ACCTPROG/generated/ACCTCALC$1.class` | java-bytecode | 1128 | generated-artifact (stale candidate) |
| `tests/repos/ACCTPROG/generated/ACCTCALC$2.class` | java-bytecode | 1128 | generated-artifact (stale candidate) |
| `tests/repos/ACCTPROG/generated/ACCTCALC$3.class` | java-bytecode | 1128 | generated-artifact (stale candidate) |
| `tests/repos/ACCTPROG/generated/ACCTCALC$4$1.class` | java-bytecode | 1166 | generated-artifact (stale candidate) |
| `tests/repos/ACCTPROG/generated/ACCTCALC$4$2.class` | java-bytecode | 1003 | generated-artifact (stale candidate) |
| `tests/repos/ACCTPROG/generated/ACCTCALC$4$3.class` | java-bytecode | 1168 | generated-artifact (stale candidate) |
| `tests/repos/ACCTPROG/generated/ACCTCALC$4$4.class` | java-bytecode | 1003 | generated-artifact (stale candidate) |
| `tests/repos/ACCTPROG/generated/ACCTCALC$4$5.class` | java-bytecode | 1166 | generated-artifact (stale candidate) |
| `tests/repos/ACCTPROG/generated/ACCTCALC$4$6.class` | java-bytecode | 1168 | generated-artifact (stale candidate) |
| `tests/repos/ACCTPROG/generated/ACCTCALC$4.class` | java-bytecode | 2492 | generated-artifact (stale candidate) |
| `tests/repos/ACCTPROG/generated/ACCTCALC.class` | java-bytecode | 6376 | generated-artifact (stale candidate) |
| `tests/repos/ACCTPROG/generated/ACCTCALC.java` | java-source | 10109 | generated-artifact (stale candidate) |
| `tests/repos/ACCTPROG/generated/ACCTPROG$1.class` | java-bytecode | 1128 | generated-artifact (stale candidate) |
| `tests/repos/ACCTPROG/generated/ACCTPROG$2.class` | java-bytecode | 1128 | generated-artifact (stale candidate) |
| `tests/repos/ACCTPROG/generated/ACCTPROG$3.class` | java-bytecode | 1128 | generated-artifact (stale candidate) |
| `tests/repos/ACCTPROG/generated/ACCTPROG$4.class` | java-bytecode | 2365 | generated-artifact (stale candidate) |
| `tests/repos/ACCTPROG/generated/ACCTPROG$5.class` | java-bytecode | 3927 | generated-artifact (stale candidate) |
| `tests/repos/ACCTPROG/generated/ACCTPROG$6.class` | java-bytecode | 1414 | generated-artifact (stale candidate) |
| `tests/repos/ACCTPROG/generated/ACCTPROG.class` | java-bytecode | 8294 | generated-artifact (stale candidate) |
| `tests/repos/ACCTPROG/generated/ACCTPROG.java` | java-source | 17169 | generated-artifact (stale candidate) |
| `tests/repos/ACCTPROG/migration_config.json` | config/data | 390 | test |
| `tests/repos/ACCTPROG/src/ACCTCALC.cob` | cobol-source | 428 | test |
| `tests/repos/ACCTPROG/src/ACCTPROG.cob` | cobol-source | 1544 | test |
| `tests/repos/ADVERSARIAL01/ADVERSARIAL01.cob` | cobol-source | 1276 | test |
| `tests/repos/ADVERSARIAL01/_preprocessed/ADVERSARIAL01.cob` | cobol-source | 1276 | preprocessed-fixture |
| `tests/repos/B-PAYCOPY/_preprocessed/copybooks/PAY-RECORD.CPY` | cobol-copybook | 189 | preprocessed-fixture |
| `tests/repos/B-PAYCOPY/_preprocessed/src/PAYMAIN.cob` | cobol-source | 543 | preprocessed-fixture |
| `tests/repos/B-PAYCOPY/copybooks/PAY-RECORD.cpy` | cobol-copybook | 189 | test |
| `tests/repos/B-PAYCOPY/generated/PAYMAIN$1.class` | java-bytecode | 1123 | generated-artifact (stale candidate) |
| `tests/repos/B-PAYCOPY/generated/PAYMAIN$2.class` | java-bytecode | 1123 | generated-artifact (stale candidate) |
| `tests/repos/B-PAYCOPY/generated/PAYMAIN$3.class` | java-bytecode | 1123 | generated-artifact (stale candidate) |
| `tests/repos/B-PAYCOPY/generated/PAYMAIN$4.class` | java-bytecode | 2723 | generated-artifact (stale candidate) |
| `tests/repos/B-PAYCOPY/generated/PAYMAIN.class` | java-bytecode | 6717 | generated-artifact (stale candidate) |
| `tests/repos/B-PAYCOPY/generated/PAYMAIN.java` | java-source | 9407 | generated-artifact (stale candidate) |
| `tests/repos/B-PAYCOPY/src/PAYMAIN.cob` | cobol-source | 543 | test |
| `tests/repos/C-PAYCHAIN/generated/PAYLOAD$1.class` | java-bytecode | 1123 | generated-artifact (stale candidate) |
| `tests/repos/C-PAYCHAIN/generated/PAYLOAD$2.class` | java-bytecode | 1123 | generated-artifact (stale candidate) |
| `tests/repos/C-PAYCHAIN/generated/PAYLOAD$3.class` | java-bytecode | 1123 | generated-artifact (stale candidate) |
| `tests/repos/C-PAYCHAIN/generated/PAYLOAD$4.class` | java-bytecode | 1805 | generated-artifact (stale candidate) |
| `tests/repos/C-PAYCHAIN/generated/PAYLOAD.class` | java-bytecode | 5602 | generated-artifact (stale candidate) |
| `tests/repos/C-PAYCHAIN/generated/PAYLOAD.java` | java-source | 6600 | generated-artifact (stale candidate) |
| `tests/repos/C-PAYCHAIN/generated/PAYMAIN$1.class` | java-bytecode | 1123 | generated-artifact (stale candidate) |
| `tests/repos/C-PAYCHAIN/generated/PAYMAIN$2.class` | java-bytecode | 1123 | generated-artifact (stale candidate) |
| `tests/repos/C-PAYCHAIN/generated/PAYMAIN$3.class` | java-bytecode | 1123 | generated-artifact (stale candidate) |
| `tests/repos/C-PAYCHAIN/generated/PAYMAIN$4.class` | java-bytecode | 3203 | generated-artifact (stale candidate) |
| `tests/repos/C-PAYCHAIN/generated/PAYMAIN.class` | java-bytecode | 5709 | generated-artifact (stale candidate) |
| `tests/repos/C-PAYCHAIN/generated/PAYMAIN.java` | java-source | 8956 | generated-artifact (stale candidate) |
| `tests/repos/C-PAYCHAIN/generated/PAYPROC$1.class` | java-bytecode | 1123 | generated-artifact (stale candidate) |
| `tests/repos/C-PAYCHAIN/generated/PAYPROC$2.class` | java-bytecode | 1123 | generated-artifact (stale candidate) |
| `tests/repos/C-PAYCHAIN/generated/PAYPROC$3.class` | java-bytecode | 1123 | generated-artifact (stale candidate) |
| `tests/repos/C-PAYCHAIN/generated/PAYPROC$4.class` | java-bytecode | 1814 | generated-artifact (stale candidate) |
| `tests/repos/C-PAYCHAIN/generated/PAYPROC.class` | java-bytecode | 5617 | generated-artifact (stale candidate) |
| `tests/repos/C-PAYCHAIN/generated/PAYPROC.java` | java-source | 6654 | generated-artifact (stale candidate) |
| `tests/repos/C-PAYCHAIN/generated/PAYREPT$1.class` | java-bytecode | 1123 | generated-artifact (stale candidate) |
| `tests/repos/C-PAYCHAIN/generated/PAYREPT$2.class` | java-bytecode | 1123 | generated-artifact (stale candidate) |
| `tests/repos/C-PAYCHAIN/generated/PAYREPT$3.class` | java-bytecode | 1123 | generated-artifact (stale candidate) |
| `tests/repos/C-PAYCHAIN/generated/PAYREPT$4.class` | java-bytecode | 2017 | generated-artifact (stale candidate) |
| `tests/repos/C-PAYCHAIN/generated/PAYREPT.class` | java-bytecode | 5413 | generated-artifact (stale candidate) |
| `tests/repos/C-PAYCHAIN/generated/PAYREPT.java` | java-source | 6235 | generated-artifact (stale candidate) |
| `tests/repos/C-PAYCHAIN/src/PAYLOAD.cob` | cobol-source | 347 | test |
| `tests/repos/C-PAYCHAIN/src/PAYMAIN.cob` | cobol-source | 663 | test |
| `tests/repos/C-PAYCHAIN/src/PAYPROC.cob` | cobol-source | 359 | test |
| `tests/repos/C-PAYCHAIN/src/PAYREPT.cob` | cobol-source | 407 | test |
| `tests/repos/CALLCHAIN01/CALLCHAIN01.cob` | cobol-source | 1701 | test |
| `tests/repos/CALLCHAIN01/SUBPROG1.cob` | cobol-source | 314 | test |
| `tests/repos/CALLCHAIN01/SUBPROG1.so` | binary-library | 17440 | tracked-binary (stale candidate) |
| `tests/repos/CALLCHAIN01/SUBPROG2.cob` | cobol-source | 319 | test |
| `tests/repos/CALLCHAIN01/SUBPROG2.so` | binary-library | 17440 | tracked-binary (stale candidate) |
| `tests/repos/CALLCHAIN01/_preprocessed/CALLCHAIN01.cob` | cobol-source | 1766 | preprocessed-fixture |
| `tests/repos/CALLCHAIN01/_preprocessed/SUBPROG1.cob` | cobol-source | 314 | preprocessed-fixture |
| `tests/repos/CALLCHAIN01/_preprocessed/SUBPROG2.cob` | cobol-source | 319 | preprocessed-fixture |
| `tests/repos/CALLCHAIN01/_preprocessed/copybooks/CHNDATA.CPY` | cobol-copybook | 249 | preprocessed-fixture |
| `tests/repos/CALLCHAIN01/_preprocessed/generated/CALLCHAIN01$1.class` | java-bytecode | 1143 | generated-artifact (stale candidate) |
| `tests/repos/CALLCHAIN01/_preprocessed/generated/CALLCHAIN01$2.class` | java-bytecode | 1143 | generated-artifact (stale candidate) |
| `tests/repos/CALLCHAIN01/_preprocessed/generated/CALLCHAIN01$3.class` | java-bytecode | 1143 | generated-artifact (stale candidate) |
| `tests/repos/CALLCHAIN01/_preprocessed/generated/CALLCHAIN01$4.class` | java-bytecode | 4890 | generated-artifact (stale candidate) |
| `tests/repos/CALLCHAIN01/_preprocessed/generated/CALLCHAIN01$5.class` | java-bytecode | 1429 | generated-artifact (stale candidate) |
| `tests/repos/CALLCHAIN01/_preprocessed/generated/CALLCHAIN01.class` | java-bytecode | 8349 | generated-artifact (stale candidate) |
| `tests/repos/CALLCHAIN01/_preprocessed/generated/CALLCHAIN01.java` | java-source | 15892 | generated-artifact (stale candidate) |
| `tests/repos/CALLCHAIN01/_preprocessed/generated/SUBPROG1$1.class` | java-bytecode | 1128 | generated-artifact (stale candidate) |
| `tests/repos/CALLCHAIN01/_preprocessed/generated/SUBPROG1$2.class` | java-bytecode | 1128 | generated-artifact (stale candidate) |
| `tests/repos/CALLCHAIN01/_preprocessed/generated/SUBPROG1$3.class` | java-bytecode | 1128 | generated-artifact (stale candidate) |
| `tests/repos/CALLCHAIN01/_preprocessed/generated/SUBPROG1$4$1.class` | java-bytecode | 1156 | generated-artifact (stale candidate) |
| `tests/repos/CALLCHAIN01/_preprocessed/generated/SUBPROG1$4.class` | java-bytecode | 2065 | generated-artifact (stale candidate) |
| `tests/repos/CALLCHAIN01/_preprocessed/generated/SUBPROG1.class` | java-bytecode | 6177 | generated-artifact (stale candidate) |
| `tests/repos/CALLCHAIN01/_preprocessed/generated/SUBPROG1.java` | java-source | 7342 | generated-artifact (stale candidate) |
| `tests/repos/CALLCHAIN01/_preprocessed/generated/SUBPROG2$1.class` | java-bytecode | 1128 | generated-artifact (stale candidate) |
| `tests/repos/CALLCHAIN01/_preprocessed/generated/SUBPROG2$2.class` | java-bytecode | 1128 | generated-artifact (stale candidate) |
| `tests/repos/CALLCHAIN01/_preprocessed/generated/SUBPROG2$3.class` | java-bytecode | 1128 | generated-artifact (stale candidate) |
| `tests/repos/CALLCHAIN01/_preprocessed/generated/SUBPROG2$4$1.class` | java-bytecode | 1156 | generated-artifact (stale candidate) |
| `tests/repos/CALLCHAIN01/_preprocessed/generated/SUBPROG2$4.class` | java-bytecode | 2065 | generated-artifact (stale candidate) |
| `tests/repos/CALLCHAIN01/_preprocessed/generated/SUBPROG2.class` | java-bytecode | 6177 | generated-artifact (stale candidate) |
| `tests/repos/CALLCHAIN01/_preprocessed/generated/SUBPROG2.java` | java-source | 7347 | generated-artifact (stale candidate) |
| `tests/repos/CALLCHAIN01/callchain01.exe` | binary-executable | 20992 | tracked-binary (stale candidate) |
| `tests/repos/CALLCHAIN01/copybooks/CHNDATA.cpy` | cobol-copybook | 249 | test |
| `tests/repos/CALLCHAIN01/data/out/chain-report.dat` | data/binary | 93 | test |
| `tests/repos/CALLCHAIN01/generated/CALLCHAIN01$1.class` | java-bytecode | 1143 | generated-artifact (stale candidate) |
| `tests/repos/CALLCHAIN01/generated/CALLCHAIN01$2.class` | java-bytecode | 1143 | generated-artifact (stale candidate) |
| `tests/repos/CALLCHAIN01/generated/CALLCHAIN01$3.class` | java-bytecode | 1143 | generated-artifact (stale candidate) |
| `tests/repos/CALLCHAIN01/generated/CALLCHAIN01$4.class` | java-bytecode | 4890 | generated-artifact (stale candidate) |
| `tests/repos/CALLCHAIN01/generated/CALLCHAIN01$5.class` | java-bytecode | 1429 | generated-artifact (stale candidate) |
| `tests/repos/CALLCHAIN01/generated/CALLCHAIN01.class` | java-bytecode | 8349 | generated-artifact (stale candidate) |
| `tests/repos/CALLCHAIN01/generated/CALLCHAIN01.java` | java-source | 15892 | generated-artifact (stale candidate) |
| `tests/repos/CALLCHAIN01/generated/SUBPROG1$1.class` | java-bytecode | 1128 | generated-artifact (stale candidate) |
| `tests/repos/CALLCHAIN01/generated/SUBPROG1$2.class` | java-bytecode | 1128 | generated-artifact (stale candidate) |
| `tests/repos/CALLCHAIN01/generated/SUBPROG1$3.class` | java-bytecode | 1128 | generated-artifact (stale candidate) |
| `tests/repos/CALLCHAIN01/generated/SUBPROG1$4$1.class` | java-bytecode | 1156 | generated-artifact (stale candidate) |
| `tests/repos/CALLCHAIN01/generated/SUBPROG1$4.class` | java-bytecode | 2065 | generated-artifact (stale candidate) |
| `tests/repos/CALLCHAIN01/generated/SUBPROG1.class` | java-bytecode | 6177 | generated-artifact (stale candidate) |
| `tests/repos/CALLCHAIN01/generated/SUBPROG1.java` | java-source | 7452 | generated-artifact (stale candidate) |
| `tests/repos/CALLCHAIN01/generated/SUBPROG2$1.class` | java-bytecode | 1128 | generated-artifact (stale candidate) |
| `tests/repos/CALLCHAIN01/generated/SUBPROG2$2.class` | java-bytecode | 1128 | generated-artifact (stale candidate) |
| `tests/repos/CALLCHAIN01/generated/SUBPROG2$3.class` | java-bytecode | 1128 | generated-artifact (stale candidate) |
| `tests/repos/CALLCHAIN01/generated/SUBPROG2$4$1.class` | java-bytecode | 1156 | generated-artifact (stale candidate) |
| `tests/repos/CALLCHAIN01/generated/SUBPROG2$4.class` | java-bytecode | 2065 | generated-artifact (stale candidate) |
| `tests/repos/CALLCHAIN01/generated/SUBPROG2.class` | java-bytecode | 6177 | generated-artifact (stale candidate) |
| `tests/repos/CALLCHAIN01/generated/SUBPROG2.java` | java-source | 7457 | generated-artifact (stale candidate) |
| `tests/repos/CICSREST01/migration_config.json` | config/data | 169 | test |
| `tests/repos/CICSREST01/src/CICSREST01.cob` | cobol-source | 1249 | test |
| `tests/repos/CICSREST01/src/LINKPROG.cob` | cobol-source | 285 | test |
| `tests/repos/D-PAYFIXED/generated/PAYMAIN$1.class` | java-bytecode | 1123 | generated-artifact (stale candidate) |
| `tests/repos/D-PAYFIXED/generated/PAYMAIN$2.class` | java-bytecode | 1123 | generated-artifact (stale candidate) |
| `tests/repos/D-PAYFIXED/generated/PAYMAIN$3.class` | java-bytecode | 1123 | generated-artifact (stale candidate) |
| `tests/repos/D-PAYFIXED/generated/PAYMAIN$4.class` | java-bytecode | 1930 | generated-artifact (stale candidate) |
| `tests/repos/D-PAYFIXED/generated/PAYMAIN.class` | java-bytecode | 5805 | generated-artifact (stale candidate) |
| `tests/repos/D-PAYFIXED/generated/PAYMAIN.java` | java-source | 7268 | generated-artifact (stale candidate) |
| `tests/repos/D-PAYFIXED/src/PAYMAIN.cob` | cobol-source | 447 | test |
| `tests/repos/DB2AGGREGATE01/data/customer.sql` | sql-data | 533 | test |
| `tests/repos/DB2AGGREGATE01/migration_config.json` | config/data | 120 | test |
| `tests/repos/DB2AGGREGATE01/src/DB2AGG01.cob` | cobol-source | 654 | test |
| `tests/repos/DB2CURNULL01/DB2CURNULL01.cob` | cobol-source | 2507 | test |
| `tests/repos/DB2CURNULL01/mock_db.yaml` | config | 64 | test |
| `tests/repos/DB2CURSOR01/data/customer.sql` | sql-data | 145 | test |
| `tests/repos/DB2CURSOR01/migration_config.json` | config/data | 118 | test |
| `tests/repos/DB2CURSOR01/mock_db.yaml` | config | 246 | test |
| `tests/repos/DB2CURSOR01/src/DB2CURSOR01.cob` | cobol-source | 1558 | test |
| `tests/repos/DB2DELETE01/data/customer.sql` | sql-data | 73 | test |
| `tests/repos/DB2DELETE01/migration_config.json` | config/data | 118 | test |
| `tests/repos/DB2DELETE01/mock_db.yaml` | config | 208 | test |
| `tests/repos/DB2DELETE01/src/DB2DELETE01.cob` | cobol-source | 545 | test |
| `tests/repos/DB2E2E01/data/db2_test_e2e.sql` | sql-data | 76 | test |
| `tests/repos/DB2E2E01/migration_config.json` | config/data | 113 | test |
| `tests/repos/DB2E2E01/src/DB2E2E01.cob` | cobol-source | 1646 | test |
| `tests/repos/DB2ERRCONSTRAINT/data/customer.sql` | sql-data | 121 | test |
| `tests/repos/DB2ERRCONSTRAINT/migration_config.json` | config/data | 121 | test |
| `tests/repos/DB2ERRCONSTRAINT/src/DB2ERRC.cob` | cobol-source | 665 | test |
| `tests/repos/DB2ERRNOTFOUND/data/customer.sql` | sql-data | 121 | test |
| `tests/repos/DB2ERRNOTFOUND/migration_config.json` | config/data | 120 | test |
| `tests/repos/DB2ERRNOTFOUND/src/DB2ERRNF.cob` | cobol-source | 479 | test |
| `tests/repos/DB2GROUPBY01/data/customer.sql` | sql-data | 498 | test |
| `tests/repos/DB2GROUPBY01/migration_config.json` | config/data | 118 | test |
| `tests/repos/DB2GROUPBY01/src/DB2GRP01.cob` | cobol-source | 1602 | test |
| `tests/repos/DB2INSERT01/data/customer.sql` | sql-data | 22 | test |
| `tests/repos/DB2INSERT01/migration_config.json` | config/data | 118 | test |
| `tests/repos/DB2INSERT01/mock_db.yaml` | config | 173 | test |
| `tests/repos/DB2INSERT01/src/DB2INSERT01.cob` | cobol-source | 630 | test |
| `tests/repos/DB2INVALID01/migration_config.json` | config/data | 120 | test |
| `tests/repos/DB2INVALID01/src/DB2INVALID01.cob` | cobol-source | 413 | test |
| `tests/repos/DB2JOIN01/_preprocessed/src/DB2JN01.cob` | cobol-source | 875 | preprocessed-fixture |
| `tests/repos/DB2JOIN01/data/customer.sql` | sql-data | 252 | test |
| `tests/repos/DB2JOIN01/data/orders.sql` | sql-data | 274 | test |
| `tests/repos/DB2JOIN01/migration_config.json` | config/data | 114 | test |
| `tests/repos/DB2JOIN01/src/DB2JN01.cob` | cobol-source | 854 | test |
| `tests/repos/DB2LEFTJOIN01/data/customer.sql` | sql-data | 337 | test |
| `tests/repos/DB2LEFTJOIN01/data/dept.sql` | sql-data | 320 | test |
| `tests/repos/DB2LEFTJOIN01/migration_config.json` | config/data | 118 | test |
| `tests/repos/DB2LEFTJOIN01/src/DB2LJ01.cob` | cobol-source | 1023 | test |
| `tests/repos/DB2NESTED01/data/customer.sql` | sql-data | 73 | test |
| `tests/repos/DB2NESTED01/migration_config.json` | config/data | 118 | test |
| `tests/repos/DB2NESTED01/mock_db.yaml` | config | 208 | test |
| `tests/repos/DB2NESTED01/src/DB2NESTED01.cob` | cobol-source | 693 | test |
| `tests/repos/DB2NULL01/data/customer.sql` | sql-data | 149 | test |
| `tests/repos/DB2NULL01/migration_config.json` | config/data | 115 | test |
| `tests/repos/DB2NULL01/src/DB2NULL01.cob` | cobol-source | 811 | test |
| `tests/repos/DB2SELECT01/data/customer.sql` | sql-data | 73 | test |
| `tests/repos/DB2SELECT01/migration_config.json` | config/data | 118 | test |
| `tests/repos/DB2SELECT01/mock_db.yaml` | config | 208 | test |
| `tests/repos/DB2SELECT01/src/DB2SELECT01.cob` | cobol-source | 702 | test |
| `tests/repos/DB2SELECT01/src/DB2SELECT01_precompiled.cob` | cobol-source | 1550 | test |
| `tests/repos/DB2SUBQUERY01/data/customer.sql` | sql-data | 446 | test |
| `tests/repos/DB2SUBQUERY01/data/orders.sql` | sql-data | 367 | test |
| `tests/repos/DB2SUBQUERY01/migration_config.json` | config/data | 119 | test |
| `tests/repos/DB2SUBQUERY01/src/DB2SUB01.cob` | cobol-source | 770 | test |
| `tests/repos/DB2TRANSACTION01/data/customer.sql` | sql-data | 73 | test |
| `tests/repos/DB2TRANSACTION01/migration_config.json` | config/data | 128 | test |
| `tests/repos/DB2TRANSACTION01/mock_db.yaml` | config | 115 | test |
| `tests/repos/DB2TRANSACTION01/src/DB2TRANSACTION01.cob` | cobol-source | 436 | test |
| `tests/repos/DB2TXVISIBILITY01/data/customer.sql` | sql-data | 521 | test |
| `tests/repos/DB2TXVISIBILITY01/migration_config.json` | config/data | 123 | test |
| `tests/repos/DB2TXVISIBILITY01/src/DB2TVS01.cob` | cobol-source | 1822 | test |
| `tests/repos/DB2UPDATE01/data/customer.sql` | sql-data | 73 | test |
| `tests/repos/DB2UPDATE01/migration_config.json` | config/data | 118 | test |
| `tests/repos/DB2UPDATE01/mock_db.yaml` | config | 208 | test |
| `tests/repos/DB2UPDATE01/src/DB2UPDATE01.cob` | cobol-source | 645 | test |
| `tests/repos/E-PAYCOMP3/generated/PAYMAIN$1.class` | java-bytecode | 1123 | generated-artifact (stale candidate) |
| `tests/repos/E-PAYCOMP3/generated/PAYMAIN$2.class` | java-bytecode | 1123 | generated-artifact (stale candidate) |
| `tests/repos/E-PAYCOMP3/generated/PAYMAIN$3.class` | java-bytecode | 1123 | generated-artifact (stale candidate) |
| `tests/repos/E-PAYCOMP3/generated/PAYMAIN$4.class` | java-bytecode | 2776 | generated-artifact (stale candidate) |
| `tests/repos/E-PAYCOMP3/generated/PAYMAIN.class` | java-bytecode | 7490 | generated-artifact (stale candidate) |
| `tests/repos/E-PAYCOMP3/generated/PAYMAIN.java` | java-source | 12081 | generated-artifact (stale candidate) |
| `tests/repos/E-PAYCOMP3/src/PAYMAIN.cob` | cobol-source | 965 | test |
| `tests/repos/F-PAYFAIL/generated/PAYMAIN$1.class` | java-bytecode | 1123 | generated-artifact (stale candidate) |
| `tests/repos/F-PAYFAIL/generated/PAYMAIN$2.class` | java-bytecode | 1123 | generated-artifact (stale candidate) |
| `tests/repos/F-PAYFAIL/generated/PAYMAIN$3.class` | java-bytecode | 1123 | generated-artifact (stale candidate) |
| `tests/repos/F-PAYFAIL/generated/PAYMAIN$4.class` | java-bytecode | 1783 | generated-artifact (stale candidate) |
| `tests/repos/F-PAYFAIL/generated/PAYMAIN.class` | java-bytecode | 5448 | generated-artifact (stale candidate) |
| `tests/repos/F-PAYFAIL/generated/PAYMAIN.java` | java-source | 6121 | generated-artifact (stale candidate) |
| `tests/repos/F-PAYFAIL/src/PAYBAD.cob` | cobol-source | 322 | test |
| `tests/repos/F-PAYFAIL/src/PAYMAIN.cob` | cobol-source | 348 | test |
| `tests/repos/FILESTAT01/FILESTAT01.cob` | cobol-source | 1948 | test |
| `tests/repos/FILESTAT01/mock_db.yaml` | config | 4 | test |
| `tests/repos/G-PAYMISSCP/src/PAYMAIN.cob` | cobol-source | 351 | test |
| `tests/repos/INVMGR/_preprocessed/src/INVMGR.cob` | cobol-source | 1187 | preprocessed-fixture |
| `tests/repos/INVMGR/migration_config.json` | config/data | 255 | test |
| `tests/repos/INVMGR/src/INVMGR.cob` | cobol-source | 1187 | test |
| `tests/repos/INVOICE01/_preprocessed/copybooks/INVREC.CPY` | cobol-copybook | 175 | preprocessed-fixture |
| `tests/repos/INVOICE01/_preprocessed/generated/INVOICE01$1.class` | java-bytecode | 1133 | generated-artifact (stale candidate) |
| `tests/repos/INVOICE01/_preprocessed/generated/INVOICE01$2.class` | java-bytecode | 1133 | generated-artifact (stale candidate) |
| `tests/repos/INVOICE01/_preprocessed/generated/INVOICE01$3.class` | java-bytecode | 1133 | generated-artifact (stale candidate) |
| `tests/repos/INVOICE01/_preprocessed/generated/INVOICE01$4.class` | java-bytecode | 2820 | generated-artifact (stale candidate) |
| `tests/repos/INVOICE01/_preprocessed/generated/INVOICE01$5.class` | java-bytecode | 3394 | generated-artifact (stale candidate) |
| `tests/repos/INVOICE01/_preprocessed/generated/INVOICE01$6.class` | java-bytecode | 1419 | generated-artifact (stale candidate) |
| `tests/repos/INVOICE01/_preprocessed/generated/INVOICE01.class` | java-bytecode | 9465 | generated-artifact (stale candidate) |
| `tests/repos/INVOICE01/_preprocessed/generated/INVOICE01.java` | java-source | 19770 | generated-artifact (stale candidate) |
| `tests/repos/INVOICE01/_preprocessed/src/INVOICE01.cob` | cobol-source | 2061 | preprocessed-fixture |
| `tests/repos/INVOICE01/bin/claims_core.exe` | binary-executable | 20776 | tracked-binary (stale candidate) |
| `tests/repos/INVOICE01/copybooks/INVREC.cpy` | cobol-copybook | 175 | test |
| `tests/repos/INVOICE01/data/in/invoice-input.dat` | data/binary | 195 | test |
| `tests/repos/INVOICE01/data/out/invoice-output.dat` | data/binary | 283 | test |
| `tests/repos/INVOICE01/generated/INVOICE01$1.class` | java-bytecode | 1133 | generated-artifact (stale candidate) |
| `tests/repos/INVOICE01/generated/INVOICE01$2.class` | java-bytecode | 1133 | generated-artifact (stale candidate) |
| `tests/repos/INVOICE01/generated/INVOICE01$3.class` | java-bytecode | 1133 | generated-artifact (stale candidate) |
| `tests/repos/INVOICE01/generated/INVOICE01$4.class` | java-bytecode | 2820 | generated-artifact (stale candidate) |
| `tests/repos/INVOICE01/generated/INVOICE01$5.class` | java-bytecode | 3394 | generated-artifact (stale candidate) |
| `tests/repos/INVOICE01/generated/INVOICE01$6.class` | java-bytecode | 1419 | generated-artifact (stale candidate) |
| `tests/repos/INVOICE01/generated/INVOICE01.class` | java-bytecode | 9465 | generated-artifact (stale candidate) |
| `tests/repos/INVOICE01/generated/INVOICE01.java` | java-source | 19770 | generated-artifact (stale candidate) |
| `tests/repos/INVOICE01/invoice01.exe` | binary-executable | 20776 | tracked-binary (stale candidate) |
| `tests/repos/INVOICE01/migration_config.json` | config/data | 393 | test |
| `tests/repos/INVOICE01/src/INVOICE01.cob` | cobol-source | 2061 | test |
| `tests/repos/JCLBATCH01/migration_config.json` | config/data | 199 | test |
| `tests/repos/JCLBATCH01/src/COBPROG1.cob` | cobol-source | 1285 | test |
| `tests/repos/JCLBATCH01/src/COBPROG2.cob` | cobol-source | 818 | test |
| `tests/repos/JCLBATCH01/src/COBPROG3.cob` | cobol-source | 817 | test |
| `tests/repos/JCLBATCH01/src/JCLBATCH01.jcl` | jcl-source | 851 | test |
| `tests/repos/JCLINVALID01/migration_config.json` | config/data | 67 | test |
| `tests/repos/JCLINVALID01/src/JCLINVALID01.jcl` | jcl-source | 432 | test |
| `tests/repos/JCLSYMBOL01/migration_config.json` | config/data | 134 | test |
| `tests/repos/JCLSYMBOL01/src/COBPROG1.cob` | cobol-source | 754 | test |
| `tests/repos/JCLSYMBOL01/src/JCLSYMBOL01.jcl` | jcl-source | 468 | test |
| `tests/repos/LAYOUT01/LAYOUT01.cob` | cobol-source | 912 | test |
| `tests/repos/LAYOUT01/_preprocessed/LAYOUT01.cob` | cobol-source | 912 | preprocessed-fixture |
| `tests/repos/MULTIFILE01/MULTIFILE01.cob` | cobol-source | 2108 | test |
| `tests/repos/MULTIFILE01/_preprocessed/MULTIFILE01.cob` | cobol-source | 2108 | preprocessed-fixture |
| `tests/repos/MULTIFILE01/_preprocessed/generated/MULTIFILE01$1.class` | java-bytecode | 1143 | generated-artifact (stale candidate) |
| `tests/repos/MULTIFILE01/_preprocessed/generated/MULTIFILE01$2.class` | java-bytecode | 1143 | generated-artifact (stale candidate) |
| `tests/repos/MULTIFILE01/_preprocessed/generated/MULTIFILE01$3.class` | java-bytecode | 1143 | generated-artifact (stale candidate) |
| `tests/repos/MULTIFILE01/_preprocessed/generated/MULTIFILE01$4.class` | java-bytecode | 3719 | generated-artifact (stale candidate) |
| `tests/repos/MULTIFILE01/_preprocessed/generated/MULTIFILE01$5.class` | java-bytecode | 1429 | generated-artifact (stale candidate) |
| `tests/repos/MULTIFILE01/_preprocessed/generated/MULTIFILE01.class` | java-bytecode | 8253 | generated-artifact (stale candidate) |
| `tests/repos/MULTIFILE01/_preprocessed/generated/MULTIFILE01.java` | java-source | 19740 | generated-artifact (stale candidate) |
| `tests/repos/MULTIFILE01/data/reports/report-a.dat` | data/binary | 30 | test |
| `tests/repos/MULTIFILE01/data/reports/report-b.dat` | data/binary | 42 | test |
| `tests/repos/MULTIFILE01/data/source/input-a.dat` | data/binary | 34 | test |
| `tests/repos/MULTIFILE01/data/source/input-b.dat` | data/binary | 44 | test |
| `tests/repos/MULTIFILE01/generated/MULTIFILE01$1.class` | java-bytecode | 1143 | generated-artifact (stale candidate) |
| `tests/repos/MULTIFILE01/generated/MULTIFILE01$2.class` | java-bytecode | 1143 | generated-artifact (stale candidate) |
| `tests/repos/MULTIFILE01/generated/MULTIFILE01$3.class` | java-bytecode | 1143 | generated-artifact (stale candidate) |
| `tests/repos/MULTIFILE01/generated/MULTIFILE01$4.class` | java-bytecode | 3719 | generated-artifact (stale candidate) |
| `tests/repos/MULTIFILE01/generated/MULTIFILE01$5.class` | java-bytecode | 1429 | generated-artifact (stale candidate) |
| `tests/repos/MULTIFILE01/generated/MULTIFILE01.class` | java-bytecode | 8253 | generated-artifact (stale candidate) |
| `tests/repos/MULTIFILE01/generated/MULTIFILE01.java` | java-source | 19740 | generated-artifact (stale candidate) |
| `tests/repos/MULTIFILE01/multifile01.exe` | binary-executable | 24504 | tracked-binary (stale candidate) |
| `tests/repos/NESTEDPROG01/migration_config.json` | config/data | 79 | test |
| `tests/repos/NESTEDPROG01/src/NESTEDPROG01.cob` | cobol-source | 1291 | test |
| `tests/repos/OCCURS01/OCCURS01.cob` | cobol-source | 1478 | test |
| `tests/repos/PICTUREEDIT01/migration_config.json` | config/data | 123 | test |
| `tests/repos/PICTUREEDIT01/src/PICTUREEDIT01.cob` | cobol-source | 2719 | test |
| `tests/repos/POINTERS01/src/POINTERS01.cob` | cobol-source | 546 | test |
| `tests/repos/REDEFINES01/REDEFINES01.cob` | cobol-source | 1304 | test |
| `tests/repos/REDEFINES01/mock_db.yaml` | config | 4 | test |
| `tests/repos/REPORTWRITER01/output.txt` | data/text | 450 | test |
| `tests/repos/REPORTWRITER01/src/REPORTWRITER01.cob` | cobol-source | 1317 | test |
| `tests/repos/SALESPROG/SALESCALC.so` | binary-library | 17840 | tracked-binary (stale candidate) |
| `tests/repos/SALESPROG/SALESPROG.so` | binary-library | 18472 | tracked-binary (stale candidate) |
| `tests/repos/SALESPROG/_preprocessed/copybooks/CALCLNK.CPY` | cobol-copybook | 216 | preprocessed-fixture |
| `tests/repos/SALESPROG/_preprocessed/copybooks/SLSREC.CPY` | cobol-copybook | 210 | preprocessed-fixture |
| `tests/repos/SALESPROG/_preprocessed/generated/SALESCALC$1.class` | java-bytecode | 1133 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/_preprocessed/generated/SALESCALC$2.class` | java-bytecode | 1133 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/_preprocessed/generated/SALESCALC$3.class` | java-bytecode | 1133 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/_preprocessed/generated/SALESCALC$4$1.class` | java-bytecode | 1170 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/_preprocessed/generated/SALESCALC$4$2.class` | java-bytecode | 1169 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/_preprocessed/generated/SALESCALC$4$3.class` | java-bytecode | 1166 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/_preprocessed/generated/SALESCALC$4$4.class` | java-bytecode | 1166 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/_preprocessed/generated/SALESCALC$4$5.class` | java-bytecode | 1166 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/_preprocessed/generated/SALESCALC$4$6.class` | java-bytecode | 1166 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/_preprocessed/generated/SALESCALC$4.class` | java-bytecode | 2840 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/_preprocessed/generated/SALESCALC.class` | java-bytecode | 6861 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/_preprocessed/generated/SALESCALC.java` | java-source | 11099 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/_preprocessed/generated/SALESPROG$1.class` | java-bytecode | 1133 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/_preprocessed/generated/SALESPROG$2.class` | java-bytecode | 1133 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/_preprocessed/generated/SALESPROG$3.class` | java-bytecode | 1133 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/_preprocessed/generated/SALESPROG$4.class` | java-bytecode | 2814 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/_preprocessed/generated/SALESPROG$5.class` | java-bytecode | 3905 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/_preprocessed/generated/SALESPROG$6.class` | java-bytecode | 1419 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/_preprocessed/generated/SALESPROG.class` | java-bytecode | 8878 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/_preprocessed/generated/SALESPROG.java` | java-source | 18225 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/_preprocessed/src/SALESCALC.cob` | cobol-source | 670 | preprocessed-fixture |
| `tests/repos/SALESPROG/_preprocessed/src/SALESPROG.cob` | cobol-source | 1992 | preprocessed-fixture |
| `tests/repos/SALESPROG/bin/salesprog.exe` | binary-executable | 20416 | tracked-binary (stale candidate) |
| `tests/repos/SALESPROG/copybooks/CALCLNK.cpy` | cobol-copybook | 216 | test |
| `tests/repos/SALESPROG/copybooks/SLSREC.cpy` | cobol-copybook | 210 | test |
| `tests/repos/SALESPROG/data/in/sales-input.dat` | data/binary | 200 | test |
| `tests/repos/SALESPROG/data/out/sales-report.dat` | data/binary | 192 | test |
| `tests/repos/SALESPROG/generated/SALESCALC$1.class` | java-bytecode | 1133 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/generated/SALESCALC$2.class` | java-bytecode | 1133 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/generated/SALESCALC$3.class` | java-bytecode | 1133 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/generated/SALESCALC$4$1.class` | java-bytecode | 1170 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/generated/SALESCALC$4$2.class` | java-bytecode | 1169 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/generated/SALESCALC$4$3.class` | java-bytecode | 1166 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/generated/SALESCALC$4$4.class` | java-bytecode | 1166 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/generated/SALESCALC$4$5.class` | java-bytecode | 1166 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/generated/SALESCALC$4$6.class` | java-bytecode | 1166 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/generated/SALESCALC$4.class` | java-bytecode | 2840 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/generated/SALESCALC.class` | java-bytecode | 6861 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/generated/SALESCALC.java` | java-source | 11213 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/generated/SALESPROG$1.class` | java-bytecode | 1133 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/generated/SALESPROG$2.class` | java-bytecode | 1133 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/generated/SALESPROG$3.class` | java-bytecode | 1133 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/generated/SALESPROG$4.class` | java-bytecode | 2814 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/generated/SALESPROG$5.class` | java-bytecode | 3905 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/generated/SALESPROG$6.class` | java-bytecode | 1419 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/generated/SALESPROG.class` | java-bytecode | 8878 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/generated/SALESPROG.java` | java-source | 18225 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/generated_debug/SALESCALC$1.class` | java-bytecode | 1133 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/generated_debug/SALESCALC$2.class` | java-bytecode | 1133 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/generated_debug/SALESCALC$3.class` | java-bytecode | 1133 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/generated_debug/SALESCALC$4$1.class` | java-bytecode | 1170 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/generated_debug/SALESCALC$4$2.class` | java-bytecode | 1169 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/generated_debug/SALESCALC$4$3.class` | java-bytecode | 1166 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/generated_debug/SALESCALC$4$4.class` | java-bytecode | 1166 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/generated_debug/SALESCALC$4$5.class` | java-bytecode | 1166 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/generated_debug/SALESCALC$4$6.class` | java-bytecode | 1166 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/generated_debug/SALESCALC$4.class` | java-bytecode | 2840 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/generated_debug/SALESCALC.class` | java-bytecode | 6861 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/generated_debug/SALESCALC.java` | java-source | 11099 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/generated_debug/SALESPROG$1.class` | java-bytecode | 1133 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/generated_debug/SALESPROG$2.class` | java-bytecode | 1133 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/generated_debug/SALESPROG$3.class` | java-bytecode | 1133 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/generated_debug/SALESPROG$4.class` | java-bytecode | 2895 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/generated_debug/SALESPROG$5.class` | java-bytecode | 3905 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/generated_debug/SALESPROG$6.class` | java-bytecode | 1419 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/generated_debug/SALESPROG.class` | java-bytecode | 9087 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/generated_debug/SALESPROG.java` | java-source | 18838 | generated-artifact (stale candidate) |
| `tests/repos/SALESPROG/migration_config.json` | config/data | 383 | test |
| `tests/repos/SALESPROG/salesprog.exe` | binary-executable | 20416 | tracked-binary (stale candidate) |
| `tests/repos/SALESPROG/salesprog_debug.exe` | binary-executable | 20512 | tracked-binary (stale candidate) |
| `tests/repos/SALESPROG/src/SALESCALC.cob` | cobol-source | 670 | test |
| `tests/repos/SALESPROG/src/SALESPROG.cob` | cobol-source | 1992 | test |
| `tests/repos/SIMPLEBASELINE01/_preprocessed/src/SIMPLEBASELINE01.cob` | cobol-source | 1125 | preprocessed-fixture |
| `tests/repos/SIMPLEBASELINE01/migration_config.json` | config/data | 283 | test |
| `tests/repos/SIMPLEBASELINE01/src/SIMPLEBASELINE01.cob` | cobol-source | 1125 | test |
| `tests/repos/SIZEERR01/SIZEERR01.cob` | cobol-source | 1117 | test |
| `tests/repos/SIZEERR01/mock_db.yaml` | config | 4 | test |
| `tests/repos/SORTMERGE01/output.txt` | data/text | 0 | test |
| `tests/repos/SORTMERGE01/src/SORTMERGE01.cob` | cobol-source | 951 | test |
| `tests/repos/VSAMKSDS01/VSAMKSDS01.cob` | cobol-source | 2990 | test |
| `tests/repos/VSAMKSDS01/data/work/ksds.dat.1` | 1 | 8192 | test |
| `tests/repos/VSAMKSDS01/data/work/ksds.dat.2` | 2 | 8192 | test |
| `tests/repos/ksds_baseline_01/CUSTOMER` | (none) | 8192 | test |
| `tests/repos/ksds_baseline_01/migration_config.json` | config/data | 130 | test |
| `tests/repos/ksds_baseline_01/src/ksds_baseline_01.cob` | cobol-source | 2170 | test |
| `tests/repos/sql_baseline_01/migration_config.json` | config/data | 127 | test |
| `tests/repos/sql_baseline_01/mock_db.yaml` | config | 208 | test |
| `tests/repos/sql_baseline_01/src/sql_baseline_01.cob` | cobol-source | 2401 | test |
| `tests/robustness/adversarial/test_java_source_mutation.py` | python-source | 10024 | test |
| `tests/robustness/adversarial/test_native_adversarial.py` | python-source | 3039 | test |
| `tests/robustness/unseen/test_phase8_unseen_repo.py` | python-source | 8528 | test |
| `tests/robustness/unseen/test_unseen_repositories_suite.py` | python-source | 21326 | test |
| `tests/test_adversarial_verification.py` | python-source | 7273 | test |
| `tests/test_certification_hardening.py` | python-source | 3839 | test |
| `tests/test_cics_ts_boundary.py` | python-source | 4134 | test |
| `tests/test_cobol_string_semantics.py` | python-source | 2542 | test |
| `tests/test_concurrency_isolation.py` | python-source | 5024 | test |
| `tests/test_control_flow.py` | python-source | 4200 | test |
| `tests/test_data_flow.py` | python-source | 4606 | test |
| `tests/test_db2_acceptance.py` | python-source | 13938 | test |
| `tests/test_db2_dialect_null_indicators.py` | python-source | 3488 | test |
| `tests/test_db2_real_vs_emulated.py` | python-source | 3415 | test |
| `tests/test_db2_stage1.py` | python-source | 6914 | test |
| `tests/test_db2_zos_boundary.py` | python-source | 4297 | test |
| `tests/test_dependencies.py` | python-source | 4674 | test |
| `tests/test_docker_isolation.py` | python-source | 2939 | test |
| `tests/test_eof_sequential_reader_parity.py` | python-source | 9672 | test |
| `tests/test_equivalence.py` | python-source | 5143 | test |
| `tests/test_equivalence_correctness_audit.py` | python-source | 7240 | test |
| `tests/test_equivalence_negative_gates.py` | python-source | 12501 | test |
| `tests/test_equivalence_topology_detection.py` | python-source | 1508 | test |
| `tests/test_final_equivalence_contract.py` | python-source | 4283 | test |
| `tests/test_forensic_fixes_round1.py` | python-source | 6781 | test |
| `tests/test_generic_refactoring.py` | python-source | 5433 | test |
| `tests/test_jcl_generator_fail_closed.py` | python-source | 564 | test |
| `tests/test_logical_comparison_fixes.py` | python-source | 5103 | test |
| `tests/test_modernize_models.py` | python-source | 2334 | test |
| `tests/test_native_artifact_isolation.py` | python-source | 4133 | test |
| `tests/test_native_call_translation.py` | python-source | 2551 | test |
| `tests/test_native_cli.py` | python-source | 2400 | test |
| `tests/test_native_compute_truncation.py` | python-source | 6858 | test |
| `tests/test_native_dependency_gate.py` | python-source | 2125 | test |
| `tests/test_native_equivalence.py` | python-source | 2589 | test |
| `tests/test_native_evaluate.py` | python-source | 2655 | test |
| `tests/test_native_file_io.py` | python-source | 2512 | test |
| `tests/test_native_level88.py` | python-source | 1908 | test |
| `tests/test_native_move_multi.py` | python-source | 789 | test |
| `tests/test_native_negative_equivalence.py` | python-source | 1238 | test |
| `tests/test_native_no_benchmark_coupling.py` | python-source | 773 | test |
| `tests/test_native_occurs.py` | python-source | 3082 | test |
| `tests/test_native_paragraph_control.py` | python-source | 2463 | test |
| `tests/test_native_perform_varying.py` | python-source | 1379 | test |
| `tests/test_native_period_scoping.py` | python-source | 4901 | test |
| `tests/test_native_ref_mod.py` | python-source | 2864 | test |
| `tests/test_native_statement_translation.py` | python-source | 7891 | test |
| `tests/test_native_traceability.py` | python-source | 2259 | test |
| `tests/test_native_type_mapping.py` | python-source | 1032 | test |
| `tests/test_negative_equivalence_contract.py` | python-source | 8005 | test |
| `tests/test_no_false_production_ready.py` | python-source | 3288 | test |
| `tests/test_no_hardcoding.py` | python-source | 2683 | test |
| `tests/test_normalization_safety.py` | python-source | 1858 | test |
| `tests/test_p0_unary_and_injection.py` | python-source | 6940 | test |
| `tests/test_parity_fixtures.py` | python-source | 42294 | test |
| `tests/test_partially_proven_constructs.py` | python-source | 6845 | test |
| `tests/test_phase10_gates.py` | python-source | 12816 | test |
| `tests/test_phase11b_security.py` | python-source | 5279 | test |
| `tests/test_phase11b_workspace_isolation.py` | python-source | 4048 | test |
| `tests/test_phase1_differential_proofs.py` | python-source | 29048 | test |
| `tests/test_phase8_arithmetic_errors.py` | python-source | 2822 | test |
| `tests/test_phase8_control_flow.py` | python-source | 7848 | test |
| `tests/test_phase8_dependency_audit.py` | python-source | 5366 | test |
| `tests/test_phase8_diagnostics.py` | python-source | 9622 | test |
| `tests/test_phase8_enterprise_topology.py` | python-source | 5557 | test |
| `tests/test_phase8_failure_recovery.py` | python-source | 2658 | test |
| `tests/test_phase8_file_semantics.py` | python-source | 11914 | test |
| `tests/test_phase8_layout_integration.py` | python-source | 4056 | test |
| `tests/test_phase8_nested_programs.py` | python-source | 2785 | test |
| `tests/test_phase8_next_sentence.py` | python-source | 3526 | test |
| `tests/test_phase8_perform_times.py` | python-source | 3305 | test |
| `tests/test_phase8_performance.py` | python-source | 2639 | test |
| `tests/test_phase8_pic_formatting.py` | python-source | 2589 | test |
| `tests/test_phase8_pointers.py` | python-source | 2367 | test |
| `tests/test_phase8_redefines.py` | python-source | 9713 | test |
| `tests/test_phase8_report_writer.py` | python-source | 3675 | test |
| `tests/test_phase8_security_audit.py` | python-source | 4290 | test |
| `tests/test_phase8_sort_merge.py` | python-source | 6968 | test |
| `tests/test_phase8_string_operations.py` | python-source | 6110 | test |
| `tests/test_phase8_traceability_extended.py` | python-source | 8586 | test |
| `tests/test_phase9_api_contract.py` | python-source | 3895 | test |
| `tests/test_phase9_failure_matrix.py` | python-source | 3832 | test |
| `tests/test_phase9_lifecycle.py` | python-source | 4101 | test |
| `tests/test_phase9_manifest.py` | python-source | 17505 | test |
| `tests/test_phase9_repeatability.py` | python-source | 3397 | test |
| `tests/test_phase9_repo_isolation.py` | python-source | 3697 | test |
| `tests/test_phase9_verdict.py` | python-source | 8652 | test |
| `tests/test_pic_v_string_semantics.py` | python-source | 3279 | test |
| `tests/test_pipeline_remediation.py` | python-source | 5369 | test |
| `tests/test_postgres_e2e.py` | python-source | 2171 | test |
| `tests/test_proleap_copybooks.py` | python-source | 3996 | test |
| `tests/test_proleap_security.py` | python-source | 886 | test |
| `tests/test_realistic_modernization.py` | python-source | 9395 | test |
| `tests/test_security_hardening.py` | python-source | 8700 | test |
| `tests/test_slicer.py` | python-source | 3451 | test |
| `tests/test_sql_db_ksds_modernization.py` | python-source | 4729 | test |
| `tests/test_strict_equivalence_guards.py` | python-source | 1760 | test |
| `tests/test_validation_nobypass.py` | python-source | 4208 | test |
| `tests/test_vsam_rrds_compatibility.py` | python-source | 8174 | test |
| `tests/unit/generator/__init__.py` | python-source | 21 | test |
| `tests/unit/ir/__init__.py` | python-source | 21 | test |
| `tests/unit/ir/test_semantic_ir.py` | python-source | 1242 | test |
| `tests/unit/lexer/__init__.py` | python-source | 21 | test |
| `tests/unit/lexer/test_lexer.py` | python-source | 2926 | test |
| `tests/unit/parser/__init__.py` | python-source | 21 | test |
| `tests/unit/parser/test_parser.py` | python-source | 8798 | test |
| `tests/utils/check_fingerprint.py` | python-source | 2152 | test |
| `tests/utils/cobol_runner.py` | python-source | 11347 | test |
| `tests/utils/gnucobol_fingerprint.txt` | data/text | 1874 | test |
| `tests/utils/parity_harness.py` | python-source | 44115 | test |
| `tests/v2/__init__.py` | python-source | 0 | test |
| `tests/v2/test_architecture_invariants.py` | python-source | 8456 | test |
| `tests/v2/test_capabilities.py` | python-source | 8014 | test |
| `tests/v2/test_diagnostic.py` | python-source | 6967 | test |
| `tests/v2/test_hardening_audit.py` | python-source | 20808 | test |
| `tests/v2/test_hardening_edge_cases.py` | python-source | 10997 | test |
| `tests/v2/test_ids.py` | python-source | 6612 | test |
| `tests/v2/test_kinds.py` | python-source | 5248 | test |
| `tests/v2/test_lexer.py` | python-source | 9945 | test |
| `tests/v2/test_lexer_tokens.py` | python-source | 8326 | test |
| `tests/v2/test_parser.py` | python-source | 9381 | test |
| `tests/v2/test_parser_determinism.py` | python-source | 5144 | test |
| `tests/v2/test_parser_grammar.py` | python-source | 6209 | test |
| `tests/v2/test_parser_r1_subsection_headers.py` | python-source | 20702 | test |
| `tests/v2/test_parser_r2_data_item_declarations.py` | python-source | 20157 | test |
| `tests/v2/test_parser_r3_clauses.py` | python-source | 34960 | test |
| `tests/v2/test_parser_r4_occurs_odo_level88.py` | python-source | 30011 | test |
| `tests/v2/test_parser_recovery.py` | python-source | 4644 | test |
| `tests/v2/test_parser_spans.py` | python-source | 4625 | test |
| `tests/v2/test_scope_graph.py` | python-source | 25535 | test |
| `tests/v2/test_source_workspace.py` | python-source | 13080 | test |
| `tests/v2/test_verification.py` | python-source | 12543 | test |

## artifacts (700 files)

| Path | Type | Bytes | Lifecycle |
|---|---|---|---|
| `artifacts/parity-failures/FILESTAT01/cobol-run/FILESTAT01.cob` | cobol-source | 2031 | test-output-artifact |
| `artifacts/parity-failures/FILESTAT01/cobol-run/outfile.txt` | data/text | 90 | test-output-artifact |
| `artifacts/parity-failures/FILESTAT01/cobol-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/FILESTAT01/java-run/com/systema/modernized/CicsProgramRegistry.java` | java-source | 266 | test-output-artifact |
| `artifacts/parity-failures/FILESTAT01/java-run/com/systema/modernized/CobolFormatHelper.java` | java-source | 12602 | test-output-artifact |
| `artifacts/parity-failures/FILESTAT01/java-run/com/systema/modernized/JclExecutionContext.java` | java-source | 1493 | test-output-artifact |
| `artifacts/parity-failures/FILESTAT01/java-run/com/systema/modernized/MockSqlService.java` | java-source | 2686 | test-output-artifact |
| `artifacts/parity-failures/FILESTAT01/java-run/com/systema/modernized/SpringContextHelper.java` | java-source | 553 | test-output-artifact |
| `artifacts/parity-failures/FILESTAT01/java-run/com/systema/modernized/native_gen/Filestat01.java` | java-source | 15258 | test-output-artifact |
| `artifacts/parity-failures/FILESTAT01/java-run/com/systema/modernized/runtime/AssignResult.java` | java-source | 343 | test-output-artifact |
| `artifacts/parity-failures/FILESTAT01/java-run/com/systema/modernized/runtime/CobolArithmetic.java` | java-source | 4385 | test-output-artifact |
| `artifacts/parity-failures/FILESTAT01/java-run/com/systema/modernized/runtime/CobolNumeric.java` | java-source | 13361 | test-output-artifact |
| `artifacts/parity-failures/FILESTAT01/java-run/com/systema/modernized/runtime/CobolNumericSpec.java` | java-source | 921 | test-output-artifact |
| `artifacts/parity-failures/FILESTAT01/java-run/com/systema/modernized/runtime/CobolRoundingMode.java` | java-source | 2012 | test-output-artifact |
| `artifacts/parity-failures/FILESTAT01/java-run/com/systema/modernized/runtime/CobolSignPosition.java` | java-source | 102 | test-output-artifact |
| `artifacts/parity-failures/FILESTAT01/java-run/com/systema/modernized/runtime/CobolUsage.java` | java-source | 107 | test-output-artifact |
| `artifacts/parity-failures/FILESTAT01/java-run/com/systema/modernized/runtime/ProhibitedRoundingException.java` | java-source | 208 | test-output-artifact |
| `artifacts/parity-failures/FILESTAT01/java-run/com/systema/modernized/runtime/SizeErrorPolicy.java` | java-source | 101 | test-output-artifact |
| `artifacts/parity-failures/FILESTAT01/java-run/com/systema/modernized/runtime/UnsupportedPrecisionException.java` | java-source | 209 | test-output-artifact |
| `artifacts/parity-failures/FILESTAT01/java-run/mock_data.sql` | sql-data | 0 | test-output-artifact |
| `artifacts/parity-failures/FILESTAT01/java-run/mock_schema.sql` | sql-data | 0 | test-output-artifact |
| `artifacts/parity-failures/FILESTAT01/java-run/outfile.txt` | data/text | 90 | test-output-artifact |
| `artifacts/parity-failures/FILESTAT01/java-run/src/main/java/com/systema/modernized/MockSqlService.java` | java-source | 2686 | test-output-artifact |
| `artifacts/parity-failures/FILESTAT01/java-run/src/main/resources/mock_data.sql` | sql-data | 0 | test-output-artifact |
| `artifacts/parity-failures/FILESTAT01/java-run/src/main/resources/mock_schema.sql` | sql-data | 0 | test-output-artifact |
| `artifacts/parity-failures/FILESTAT01/java-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/REDEFINES01/cobol-run/REDEFINES01.cob` | cobol-source | 1088 | test-output-artifact |
| `artifacts/parity-failures/REDEFINES01/cobol-run/WS-FILE-OUT` | (none) | 10 | test-output-artifact |
| `artifacts/parity-failures/REDEFINES01/cobol-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/REDEFINES01/java-run/WS-FILE-OUT` | (none) | 10 | test-output-artifact |
| `artifacts/parity-failures/REDEFINES01/java-run/com/systema/modernized/CicsProgramRegistry.java` | java-source | 266 | test-output-artifact |
| `artifacts/parity-failures/REDEFINES01/java-run/com/systema/modernized/CobolFormatHelper.java` | java-source | 12602 | test-output-artifact |
| `artifacts/parity-failures/REDEFINES01/java-run/com/systema/modernized/JclExecutionContext.java` | java-source | 1493 | test-output-artifact |
| `artifacts/parity-failures/REDEFINES01/java-run/com/systema/modernized/MockSqlService.java` | java-source | 2686 | test-output-artifact |
| `artifacts/parity-failures/REDEFINES01/java-run/com/systema/modernized/SpringContextHelper.java` | java-source | 553 | test-output-artifact |
| `artifacts/parity-failures/REDEFINES01/java-run/com/systema/modernized/native_gen/Redefines01.java` | java-source | 14601 | test-output-artifact |
| `artifacts/parity-failures/REDEFINES01/java-run/com/systema/modernized/runtime/AssignResult.java` | java-source | 343 | test-output-artifact |
| `artifacts/parity-failures/REDEFINES01/java-run/com/systema/modernized/runtime/CobolArithmetic.java` | java-source | 4385 | test-output-artifact |
| `artifacts/parity-failures/REDEFINES01/java-run/com/systema/modernized/runtime/CobolNumeric.java` | java-source | 13361 | test-output-artifact |
| `artifacts/parity-failures/REDEFINES01/java-run/com/systema/modernized/runtime/CobolNumericSpec.java` | java-source | 921 | test-output-artifact |
| `artifacts/parity-failures/REDEFINES01/java-run/com/systema/modernized/runtime/CobolRoundingMode.java` | java-source | 2012 | test-output-artifact |
| `artifacts/parity-failures/REDEFINES01/java-run/com/systema/modernized/runtime/CobolSignPosition.java` | java-source | 102 | test-output-artifact |
| `artifacts/parity-failures/REDEFINES01/java-run/com/systema/modernized/runtime/CobolUsage.java` | java-source | 107 | test-output-artifact |
| `artifacts/parity-failures/REDEFINES01/java-run/com/systema/modernized/runtime/ProhibitedRoundingException.java` | java-source | 208 | test-output-artifact |
| `artifacts/parity-failures/REDEFINES01/java-run/com/systema/modernized/runtime/SizeErrorPolicy.java` | java-source | 101 | test-output-artifact |
| `artifacts/parity-failures/REDEFINES01/java-run/com/systema/modernized/runtime/UnsupportedPrecisionException.java` | java-source | 209 | test-output-artifact |
| `artifacts/parity-failures/REDEFINES01/java-run/mock_data.sql` | sql-data | 0 | test-output-artifact |
| `artifacts/parity-failures/REDEFINES01/java-run/mock_schema.sql` | sql-data | 0 | test-output-artifact |
| `artifacts/parity-failures/REDEFINES01/java-run/src/main/java/com/systema/modernized/MockSqlService.java` | java-source | 2686 | test-output-artifact |
| `artifacts/parity-failures/REDEFINES01/java-run/src/main/resources/mock_data.sql` | sql-data | 0 | test-output-artifact |
| `artifacts/parity-failures/REDEFINES01/java-run/src/main/resources/mock_schema.sql` | sql-data | 0 | test-output-artifact |
| `artifacts/parity-failures/REDEFINES01/java-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_basic_move/cobol-run/MOVEPROG.cob` | cobol-source | 444 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_basic_move/cobol-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_basic_move/java-run/com/systema/modernized/CicsProgramRegistry.java` | java-source | 266 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_basic_move/java-run/com/systema/modernized/CobolFormatHelper.java` | java-source | 12684 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_basic_move/java-run/com/systema/modernized/JclExecutionContext.java` | java-source | 1493 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_basic_move/java-run/com/systema/modernized/SpringContextHelper.java` | java-source | 553 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_basic_move/java-run/com/systema/modernized/native_gen/Moveprog.java` | java-source | 7490 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_basic_move/java-run/com/systema/modernized/runtime/AssignResult.java` | java-source | 343 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_basic_move/java-run/com/systema/modernized/runtime/CobolArithmetic.java` | java-source | 4144 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_basic_move/java-run/com/systema/modernized/runtime/CobolNumeric.java` | java-source | 12659 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_basic_move/java-run/com/systema/modernized/runtime/CobolNumericSpec.java` | java-source | 921 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_basic_move/java-run/com/systema/modernized/runtime/CobolRoundingMode.java` | java-source | 2012 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_basic_move/java-run/com/systema/modernized/runtime/CobolSignPosition.java` | java-source | 102 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_basic_move/java-run/com/systema/modernized/runtime/CobolUsage.java` | java-source | 107 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_basic_move/java-run/com/systema/modernized/runtime/ProhibitedRoundingException.java` | java-source | 208 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_basic_move/java-run/com/systema/modernized/runtime/SizeErrorPolicy.java` | java-source | 101 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_basic_move/java-run/com/systema/modernized/runtime/UnsupportedPrecisionException.java` | java-source | 209 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_basic_move/java-run/com/systema/modernized/runtime/VsamIndexedStore.java` | java-source | 5335 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_integer_compute_add/cobol-run/ARITHPROG.cob` | cobol-source | 450 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_integer_compute_add/cobol-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_integer_compute_add/java-run/com/systema/modernized/CicsProgramRegistry.java` | java-source | 266 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_integer_compute_add/java-run/com/systema/modernized/CobolFormatHelper.java` | java-source | 12684 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_integer_compute_add/java-run/com/systema/modernized/JclExecutionContext.java` | java-source | 1493 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_integer_compute_add/java-run/com/systema/modernized/SpringContextHelper.java` | java-source | 553 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_integer_compute_add/java-run/com/systema/modernized/native_gen/Arithprog.java` | java-source | 7928 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_integer_compute_add/java-run/com/systema/modernized/runtime/AssignResult.java` | java-source | 343 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_integer_compute_add/java-run/com/systema/modernized/runtime/CobolArithmetic.java` | java-source | 4144 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_integer_compute_add/java-run/com/systema/modernized/runtime/CobolNumeric.java` | java-source | 12659 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_integer_compute_add/java-run/com/systema/modernized/runtime/CobolNumericSpec.java` | java-source | 921 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_integer_compute_add/java-run/com/systema/modernized/runtime/CobolRoundingMode.java` | java-source | 2012 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_integer_compute_add/java-run/com/systema/modernized/runtime/CobolSignPosition.java` | java-source | 102 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_integer_compute_add/java-run/com/systema/modernized/runtime/CobolUsage.java` | java-source | 107 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_integer_compute_add/java-run/com/systema/modernized/runtime/ProhibitedRoundingException.java` | java-source | 208 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_integer_compute_add/java-run/com/systema/modernized/runtime/SizeErrorPolicy.java` | java-source | 101 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_integer_compute_add/java-run/com/systema/modernized/runtime/UnsupportedPrecisionException.java` | java-source | 209 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_integer_compute_add/java-run/com/systema/modernized/runtime/VsamIndexedStore.java` | java-source | 5335 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_line_sequential_file/cobol-run/OUTFILE.TXT` | data/text | 30 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_line_sequential_file/cobol-run/SEQFILEPROG.cob` | cobol-source | 624 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_line_sequential_file/cobol-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_line_sequential_file/java-run/OUTFILE.TXT` | data/text | 44 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_line_sequential_file/java-run/com/systema/modernized/CicsProgramRegistry.java` | java-source | 266 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_line_sequential_file/java-run/com/systema/modernized/CobolFormatHelper.java` | java-source | 13421 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_line_sequential_file/java-run/com/systema/modernized/JclExecutionContext.java` | java-source | 1493 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_line_sequential_file/java-run/com/systema/modernized/SpringContextHelper.java` | java-source | 553 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_line_sequential_file/java-run/com/systema/modernized/native_gen/Seqfileprog.java` | java-source | 10236 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_line_sequential_file/java-run/com/systema/modernized/runtime/AssignResult.java` | java-source | 343 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_line_sequential_file/java-run/com/systema/modernized/runtime/CobolArithmetic.java` | java-source | 4385 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_line_sequential_file/java-run/com/systema/modernized/runtime/CobolNumeric.java` | java-source | 13361 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_line_sequential_file/java-run/com/systema/modernized/runtime/CobolNumericSpec.java` | java-source | 921 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_line_sequential_file/java-run/com/systema/modernized/runtime/CobolRoundingMode.java` | java-source | 2012 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_line_sequential_file/java-run/com/systema/modernized/runtime/CobolSignPosition.java` | java-source | 102 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_line_sequential_file/java-run/com/systema/modernized/runtime/CobolUsage.java` | java-source | 107 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_line_sequential_file/java-run/com/systema/modernized/runtime/ProhibitedRoundingException.java` | java-source | 208 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_line_sequential_file/java-run/com/systema/modernized/runtime/SizeErrorPolicy.java` | java-source | 101 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_line_sequential_file/java-run/com/systema/modernized/runtime/UnsupportedPrecisionException.java` | java-source | 209 | test-output-artifact |
| `artifacts/parity-failures/milestone_a_line_sequential_file/java-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_comp3_roundtrip/cobol-run/COMP3RT.cob` | cobol-source | 425 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_comp3_roundtrip/cobol-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_comp3_roundtrip/java-run/com/systema/modernized/CicsProgramRegistry.java` | java-source | 266 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_comp3_roundtrip/java-run/com/systema/modernized/CobolFormatHelper.java` | java-source | 12684 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_comp3_roundtrip/java-run/com/systema/modernized/JclExecutionContext.java` | java-source | 1493 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_comp3_roundtrip/java-run/com/systema/modernized/SpringContextHelper.java` | java-source | 553 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_comp3_roundtrip/java-run/com/systema/modernized/native_gen/Comp3rt.java` | java-source | 9376 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_comp3_roundtrip/java-run/com/systema/modernized/runtime/AssignResult.java` | java-source | 343 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_comp3_roundtrip/java-run/com/systema/modernized/runtime/CobolArithmetic.java` | java-source | 4144 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_comp3_roundtrip/java-run/com/systema/modernized/runtime/CobolNumeric.java` | java-source | 12659 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_comp3_roundtrip/java-run/com/systema/modernized/runtime/CobolNumericSpec.java` | java-source | 921 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_comp3_roundtrip/java-run/com/systema/modernized/runtime/CobolRoundingMode.java` | java-source | 2012 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_comp3_roundtrip/java-run/com/systema/modernized/runtime/CobolSignPosition.java` | java-source | 102 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_comp3_roundtrip/java-run/com/systema/modernized/runtime/CobolUsage.java` | java-source | 107 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_comp3_roundtrip/java-run/com/systema/modernized/runtime/ProhibitedRoundingException.java` | java-source | 208 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_comp3_roundtrip/java-run/com/systema/modernized/runtime/SizeErrorPolicy.java` | java-source | 101 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_comp3_roundtrip/java-run/com/systema/modernized/runtime/UnsupportedPrecisionException.java` | java-source | 209 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_comp3_roundtrip/java-run/com/systema/modernized/runtime/VsamIndexedStore.java` | java-source | 5335 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_compute_mixed/cobol-run/COMPMIX.cob` | cobol-source | 528 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_compute_mixed/cobol-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_compute_mixed/java-run/com/systema/modernized/CicsProgramRegistry.java` | java-source | 266 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_compute_mixed/java-run/com/systema/modernized/CobolFormatHelper.java` | java-source | 12684 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_compute_mixed/java-run/com/systema/modernized/JclExecutionContext.java` | java-source | 1493 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_compute_mixed/java-run/com/systema/modernized/SpringContextHelper.java` | java-source | 553 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_compute_mixed/java-run/com/systema/modernized/native_gen/Compmix.java` | java-source | 11200 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_compute_mixed/java-run/com/systema/modernized/runtime/AssignResult.java` | java-source | 343 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_compute_mixed/java-run/com/systema/modernized/runtime/CobolArithmetic.java` | java-source | 4144 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_compute_mixed/java-run/com/systema/modernized/runtime/CobolNumeric.java` | java-source | 12659 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_compute_mixed/java-run/com/systema/modernized/runtime/CobolNumericSpec.java` | java-source | 921 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_compute_mixed/java-run/com/systema/modernized/runtime/CobolRoundingMode.java` | java-source | 2012 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_compute_mixed/java-run/com/systema/modernized/runtime/CobolSignPosition.java` | java-source | 102 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_compute_mixed/java-run/com/systema/modernized/runtime/CobolUsage.java` | java-source | 107 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_compute_mixed/java-run/com/systema/modernized/runtime/ProhibitedRoundingException.java` | java-source | 208 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_compute_mixed/java-run/com/systema/modernized/runtime/SizeErrorPolicy.java` | java-source | 101 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_compute_mixed/java-run/com/systema/modernized/runtime/UnsupportedPrecisionException.java` | java-source | 209 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_compute_mixed/java-run/com/systema/modernized/runtime/VsamIndexedStore.java` | java-source | 5335 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_by_zero_with_size_error/cobol-run/DIVZEROW.cob` | cobol-source | 546 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_by_zero_with_size_error/cobol-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_by_zero_with_size_error/java-run/com/systema/modernized/CicsProgramRegistry.java` | java-source | 266 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_by_zero_with_size_error/java-run/com/systema/modernized/CobolFormatHelper.java` | java-source | 12684 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_by_zero_with_size_error/java-run/com/systema/modernized/JclExecutionContext.java` | java-source | 1493 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_by_zero_with_size_error/java-run/com/systema/modernized/SpringContextHelper.java` | java-source | 553 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_by_zero_with_size_error/java-run/com/systema/modernized/native_gen/Divzerow.java` | java-source | 9713 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_by_zero_with_size_error/java-run/com/systema/modernized/runtime/AssignResult.java` | java-source | 343 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_by_zero_with_size_error/java-run/com/systema/modernized/runtime/CobolArithmetic.java` | java-source | 4144 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_by_zero_with_size_error/java-run/com/systema/modernized/runtime/CobolNumeric.java` | java-source | 12659 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_by_zero_with_size_error/java-run/com/systema/modernized/runtime/CobolNumericSpec.java` | java-source | 921 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_by_zero_with_size_error/java-run/com/systema/modernized/runtime/CobolRoundingMode.java` | java-source | 2012 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_by_zero_with_size_error/java-run/com/systema/modernized/runtime/CobolSignPosition.java` | java-source | 102 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_by_zero_with_size_error/java-run/com/systema/modernized/runtime/CobolUsage.java` | java-source | 107 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_by_zero_with_size_error/java-run/com/systema/modernized/runtime/ProhibitedRoundingException.java` | java-source | 208 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_by_zero_with_size_error/java-run/com/systema/modernized/runtime/SizeErrorPolicy.java` | java-source | 101 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_by_zero_with_size_error/java-run/com/systema/modernized/runtime/UnsupportedPrecisionException.java` | java-source | 209 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_by_zero_with_size_error/java-run/com/systema/modernized/runtime/VsamIndexedStore.java` | java-source | 5335 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_by_zero_without_size_error/cobol-run/DIVZEROWO.cob` | cobol-source | 513 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_by_zero_without_size_error/cobol-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_by_zero_without_size_error/java-run/com/systema/modernized/CicsProgramRegistry.java` | java-source | 266 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_by_zero_without_size_error/java-run/com/systema/modernized/CobolFormatHelper.java` | java-source | 12684 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_by_zero_without_size_error/java-run/com/systema/modernized/JclExecutionContext.java` | java-source | 1493 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_by_zero_without_size_error/java-run/com/systema/modernized/SpringContextHelper.java` | java-source | 553 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_by_zero_without_size_error/java-run/com/systema/modernized/native_gen/Divzerowo.java` | java-source | 9476 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_by_zero_without_size_error/java-run/com/systema/modernized/runtime/AssignResult.java` | java-source | 343 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_by_zero_without_size_error/java-run/com/systema/modernized/runtime/CobolArithmetic.java` | java-source | 4144 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_by_zero_without_size_error/java-run/com/systema/modernized/runtime/CobolNumeric.java` | java-source | 12659 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_by_zero_without_size_error/java-run/com/systema/modernized/runtime/CobolNumericSpec.java` | java-source | 921 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_by_zero_without_size_error/java-run/com/systema/modernized/runtime/CobolRoundingMode.java` | java-source | 2012 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_by_zero_without_size_error/java-run/com/systema/modernized/runtime/CobolSignPosition.java` | java-source | 102 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_by_zero_without_size_error/java-run/com/systema/modernized/runtime/CobolUsage.java` | java-source | 107 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_by_zero_without_size_error/java-run/com/systema/modernized/runtime/ProhibitedRoundingException.java` | java-source | 208 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_by_zero_without_size_error/java-run/com/systema/modernized/runtime/SizeErrorPolicy.java` | java-source | 101 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_by_zero_without_size_error/java-run/com/systema/modernized/runtime/UnsupportedPrecisionException.java` | java-source | 209 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_by_zero_without_size_error/java-run/com/systema/modernized/runtime/VsamIndexedStore.java` | java-source | 5335 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_remainder/cobol-run/DIVREM.cob` | cobol-source | 613 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_remainder/cobol-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_remainder/java-run/com/systema/modernized/CicsProgramRegistry.java` | java-source | 266 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_remainder/java-run/com/systema/modernized/CobolFormatHelper.java` | java-source | 12684 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_remainder/java-run/com/systema/modernized/JclExecutionContext.java` | java-source | 1493 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_remainder/java-run/com/systema/modernized/SpringContextHelper.java` | java-source | 553 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_remainder/java-run/com/systema/modernized/native_gen/Divrem.java` | java-source | 10566 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_remainder/java-run/com/systema/modernized/runtime/AssignResult.java` | java-source | 343 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_remainder/java-run/com/systema/modernized/runtime/CobolArithmetic.java` | java-source | 4144 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_remainder/java-run/com/systema/modernized/runtime/CobolNumeric.java` | java-source | 12659 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_remainder/java-run/com/systema/modernized/runtime/CobolNumericSpec.java` | java-source | 921 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_remainder/java-run/com/systema/modernized/runtime/CobolRoundingMode.java` | java-source | 2012 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_remainder/java-run/com/systema/modernized/runtime/CobolSignPosition.java` | java-source | 102 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_remainder/java-run/com/systema/modernized/runtime/CobolUsage.java` | java-source | 107 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_remainder/java-run/com/systema/modernized/runtime/ProhibitedRoundingException.java` | java-source | 208 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_remainder/java-run/com/systema/modernized/runtime/SizeErrorPolicy.java` | java-source | 101 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_remainder/java-run/com/systema/modernized/runtime/UnsupportedPrecisionException.java` | java-source | 209 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_divide_remainder/java-run/com/systema/modernized/runtime/VsamIndexedStore.java` | java-source | 5335 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_division_scale_normalization/cobol-run/DIVSCALE.cob` | cobol-source | 527 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_division_scale_normalization/cobol-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_division_scale_normalization/java-run/com/systema/modernized/CicsProgramRegistry.java` | java-source | 266 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_division_scale_normalization/java-run/com/systema/modernized/CobolFormatHelper.java` | java-source | 12684 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_division_scale_normalization/java-run/com/systema/modernized/JclExecutionContext.java` | java-source | 1493 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_division_scale_normalization/java-run/com/systema/modernized/SpringContextHelper.java` | java-source | 553 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_division_scale_normalization/java-run/com/systema/modernized/native_gen/Divscale.java` | java-source | 11292 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_division_scale_normalization/java-run/com/systema/modernized/runtime/AssignResult.java` | java-source | 343 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_division_scale_normalization/java-run/com/systema/modernized/runtime/CobolArithmetic.java` | java-source | 4144 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_division_scale_normalization/java-run/com/systema/modernized/runtime/CobolNumeric.java` | java-source | 12659 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_division_scale_normalization/java-run/com/systema/modernized/runtime/CobolNumericSpec.java` | java-source | 921 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_division_scale_normalization/java-run/com/systema/modernized/runtime/CobolRoundingMode.java` | java-source | 2012 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_division_scale_normalization/java-run/com/systema/modernized/runtime/CobolSignPosition.java` | java-source | 102 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_division_scale_normalization/java-run/com/systema/modernized/runtime/CobolUsage.java` | java-source | 107 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_division_scale_normalization/java-run/com/systema/modernized/runtime/ProhibitedRoundingException.java` | java-source | 208 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_division_scale_normalization/java-run/com/systema/modernized/runtime/SizeErrorPolicy.java` | java-source | 101 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_division_scale_normalization/java-run/com/systema/modernized/runtime/UnsupportedPrecisionException.java` | java-source | 209 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_division_scale_normalization/java-run/com/systema/modernized/runtime/VsamIndexedStore.java` | java-source | 5335 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_division_terminating/cobol-run/DIVTERM.cob` | cobol-source | 470 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_division_terminating/cobol-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_division_terminating/java-run/com/systema/modernized/CicsProgramRegistry.java` | java-source | 266 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_division_terminating/java-run/com/systema/modernized/CobolFormatHelper.java` | java-source | 12684 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_division_terminating/java-run/com/systema/modernized/JclExecutionContext.java` | java-source | 1493 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_division_terminating/java-run/com/systema/modernized/SpringContextHelper.java` | java-source | 553 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_division_terminating/java-run/com/systema/modernized/native_gen/Divterm.java` | java-source | 10388 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_division_terminating/java-run/com/systema/modernized/runtime/AssignResult.java` | java-source | 343 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_division_terminating/java-run/com/systema/modernized/runtime/CobolArithmetic.java` | java-source | 4144 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_division_terminating/java-run/com/systema/modernized/runtime/CobolNumeric.java` | java-source | 12659 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_division_terminating/java-run/com/systema/modernized/runtime/CobolNumericSpec.java` | java-source | 921 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_division_terminating/java-run/com/systema/modernized/runtime/CobolRoundingMode.java` | java-source | 2012 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_division_terminating/java-run/com/systema/modernized/runtime/CobolSignPosition.java` | java-source | 102 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_division_terminating/java-run/com/systema/modernized/runtime/CobolUsage.java` | java-source | 107 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_division_terminating/java-run/com/systema/modernized/runtime/ProhibitedRoundingException.java` | java-source | 208 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_division_terminating/java-run/com/systema/modernized/runtime/SizeErrorPolicy.java` | java-source | 101 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_division_terminating/java-run/com/systema/modernized/runtime/UnsupportedPrecisionException.java` | java-source | 209 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_division_terminating/java-run/com/systema/modernized/runtime/VsamIndexedStore.java` | java-source | 5335 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_fixed_binary_file_io/cobol-run/BINIO.cob` | cobol-source | 1099 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_fixed_binary_file_io/cobol-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_fixed_binary_file_io/java-run/com/systema/modernized/CicsProgramRegistry.java` | java-source | 266 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_fixed_binary_file_io/java-run/com/systema/modernized/CobolFormatHelper.java` | java-source | 12684 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_fixed_binary_file_io/java-run/com/systema/modernized/JclExecutionContext.java` | java-source | 1493 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_fixed_binary_file_io/java-run/com/systema/modernized/SpringContextHelper.java` | java-source | 553 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_fixed_binary_file_io/java-run/com/systema/modernized/native_gen/Binio.java` | java-source | 15602 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_fixed_binary_file_io/java-run/com/systema/modernized/runtime/AssignResult.java` | java-source | 343 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_fixed_binary_file_io/java-run/com/systema/modernized/runtime/CobolArithmetic.java` | java-source | 4144 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_fixed_binary_file_io/java-run/com/systema/modernized/runtime/CobolNumeric.java` | java-source | 12659 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_fixed_binary_file_io/java-run/com/systema/modernized/runtime/CobolNumericSpec.java` | java-source | 921 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_fixed_binary_file_io/java-run/com/systema/modernized/runtime/CobolRoundingMode.java` | java-source | 2012 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_fixed_binary_file_io/java-run/com/systema/modernized/runtime/CobolSignPosition.java` | java-source | 102 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_fixed_binary_file_io/java-run/com/systema/modernized/runtime/CobolUsage.java` | java-source | 107 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_fixed_binary_file_io/java-run/com/systema/modernized/runtime/ProhibitedRoundingException.java` | java-source | 208 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_fixed_binary_file_io/java-run/com/systema/modernized/runtime/SizeErrorPolicy.java` | java-source | 101 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_fixed_binary_file_io/java-run/com/systema/modernized/runtime/UnsupportedPrecisionException.java` | java-source | 209 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_fixed_binary_file_io/java-run/com/systema/modernized/runtime/VsamIndexedStore.java` | java-source | 5335 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_high_scale_divide/cobol-run/HISCALE.cob` | cobol-source | 334 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_high_scale_divide/cobol-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_high_scale_divide/java-run/com/systema/modernized/CicsProgramRegistry.java` | java-source | 266 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_high_scale_divide/java-run/com/systema/modernized/CobolFormatHelper.java` | java-source | 12684 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_high_scale_divide/java-run/com/systema/modernized/JclExecutionContext.java` | java-source | 1493 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_high_scale_divide/java-run/com/systema/modernized/SpringContextHelper.java` | java-source | 553 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_high_scale_divide/java-run/com/systema/modernized/native_gen/Hiscale.java` | java-source | 8531 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_high_scale_divide/java-run/com/systema/modernized/runtime/AssignResult.java` | java-source | 343 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_high_scale_divide/java-run/com/systema/modernized/runtime/CobolArithmetic.java` | java-source | 4144 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_high_scale_divide/java-run/com/systema/modernized/runtime/CobolNumeric.java` | java-source | 12659 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_high_scale_divide/java-run/com/systema/modernized/runtime/CobolNumericSpec.java` | java-source | 921 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_high_scale_divide/java-run/com/systema/modernized/runtime/CobolRoundingMode.java` | java-source | 2012 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_high_scale_divide/java-run/com/systema/modernized/runtime/CobolSignPosition.java` | java-source | 102 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_high_scale_divide/java-run/com/systema/modernized/runtime/CobolUsage.java` | java-source | 107 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_high_scale_divide/java-run/com/systema/modernized/runtime/ProhibitedRoundingException.java` | java-source | 208 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_high_scale_divide/java-run/com/systema/modernized/runtime/SizeErrorPolicy.java` | java-source | 101 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_high_scale_divide/java-run/com/systema/modernized/runtime/UnsupportedPrecisionException.java` | java-source | 209 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_high_scale_divide/java-run/com/systema/modernized/runtime/VsamIndexedStore.java` | java-source | 5335 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_integer_fast_path_audit/cobol-run/FPFAST.cob` | cobol-source | 582 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_integer_fast_path_audit/cobol-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_integer_fast_path_audit/java-run/com/systema/modernized/CicsProgramRegistry.java` | java-source | 266 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_integer_fast_path_audit/java-run/com/systema/modernized/CobolFormatHelper.java` | java-source | 12684 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_integer_fast_path_audit/java-run/com/systema/modernized/JclExecutionContext.java` | java-source | 1493 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_integer_fast_path_audit/java-run/com/systema/modernized/SpringContextHelper.java` | java-source | 553 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_integer_fast_path_audit/java-run/com/systema/modernized/native_gen/Fpfast.java` | java-source | 10362 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_integer_fast_path_audit/java-run/com/systema/modernized/runtime/AssignResult.java` | java-source | 343 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_integer_fast_path_audit/java-run/com/systema/modernized/runtime/CobolArithmetic.java` | java-source | 4144 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_integer_fast_path_audit/java-run/com/systema/modernized/runtime/CobolNumeric.java` | java-source | 13361 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_integer_fast_path_audit/java-run/com/systema/modernized/runtime/CobolNumericSpec.java` | java-source | 921 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_integer_fast_path_audit/java-run/com/systema/modernized/runtime/CobolRoundingMode.java` | java-source | 2012 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_integer_fast_path_audit/java-run/com/systema/modernized/runtime/CobolSignPosition.java` | java-source | 102 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_integer_fast_path_audit/java-run/com/systema/modernized/runtime/CobolUsage.java` | java-source | 107 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_integer_fast_path_audit/java-run/com/systema/modernized/runtime/ProhibitedRoundingException.java` | java-source | 208 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_integer_fast_path_audit/java-run/com/systema/modernized/runtime/SizeErrorPolicy.java` | java-source | 101 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_integer_fast_path_audit/java-run/com/systema/modernized/runtime/UnsupportedPrecisionException.java` | java-source | 209 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_integer_fast_path_audit/java-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_multi_receiver/cobol-run/MULTIRCV.cob` | cobol-source | 513 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_multi_receiver/cobol-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_multi_receiver/java-run/com/systema/modernized/CicsProgramRegistry.java` | java-source | 266 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_multi_receiver/java-run/com/systema/modernized/CobolFormatHelper.java` | java-source | 12684 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_multi_receiver/java-run/com/systema/modernized/JclExecutionContext.java` | java-source | 1493 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_multi_receiver/java-run/com/systema/modernized/SpringContextHelper.java` | java-source | 553 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_multi_receiver/java-run/com/systema/modernized/native_gen/Multircv.java` | java-source | 11370 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_multi_receiver/java-run/com/systema/modernized/runtime/AssignResult.java` | java-source | 343 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_multi_receiver/java-run/com/systema/modernized/runtime/CobolArithmetic.java` | java-source | 4144 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_multi_receiver/java-run/com/systema/modernized/runtime/CobolNumeric.java` | java-source | 12659 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_multi_receiver/java-run/com/systema/modernized/runtime/CobolNumericSpec.java` | java-source | 921 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_multi_receiver/java-run/com/systema/modernized/runtime/CobolRoundingMode.java` | java-source | 2012 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_multi_receiver/java-run/com/systema/modernized/runtime/CobolSignPosition.java` | java-source | 102 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_multi_receiver/java-run/com/systema/modernized/runtime/CobolUsage.java` | java-source | 107 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_multi_receiver/java-run/com/systema/modernized/runtime/ProhibitedRoundingException.java` | java-source | 208 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_multi_receiver/java-run/com/systema/modernized/runtime/SizeErrorPolicy.java` | java-source | 101 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_multi_receiver/java-run/com/systema/modernized/runtime/UnsupportedPrecisionException.java` | java-source | 209 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_multi_receiver/java-run/com/systema/modernized/runtime/VsamIndexedStore.java` | java-source | 5335 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_halfway/cobol-run/NEGHALF.cob` | cobol-source | 469 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_halfway/cobol-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_halfway/java-run/com/systema/modernized/CicsProgramRegistry.java` | java-source | 266 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_halfway/java-run/com/systema/modernized/CobolFormatHelper.java` | java-source | 12684 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_halfway/java-run/com/systema/modernized/JclExecutionContext.java` | java-source | 1493 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_halfway/java-run/com/systema/modernized/SpringContextHelper.java` | java-source | 553 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_halfway/java-run/com/systema/modernized/native_gen/Neghalf.java` | java-source | 9552 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_halfway/java-run/com/systema/modernized/runtime/AssignResult.java` | java-source | 343 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_halfway/java-run/com/systema/modernized/runtime/CobolArithmetic.java` | java-source | 4144 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_halfway/java-run/com/systema/modernized/runtime/CobolNumeric.java` | java-source | 12659 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_halfway/java-run/com/systema/modernized/runtime/CobolNumericSpec.java` | java-source | 921 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_halfway/java-run/com/systema/modernized/runtime/CobolRoundingMode.java` | java-source | 2012 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_halfway/java-run/com/systema/modernized/runtime/CobolSignPosition.java` | java-source | 102 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_halfway/java-run/com/systema/modernized/runtime/CobolUsage.java` | java-source | 107 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_halfway/java-run/com/systema/modernized/runtime/ProhibitedRoundingException.java` | java-source | 208 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_halfway/java-run/com/systema/modernized/runtime/SizeErrorPolicy.java` | java-source | 101 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_halfway/java-run/com/systema/modernized/runtime/UnsupportedPrecisionException.java` | java-source | 209 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_halfway/java-run/com/systema/modernized/runtime/VsamIndexedStore.java` | java-source | 5335 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_subtract/cobol-run/NEGSUB.cob` | cobol-source | 584 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_subtract/cobol-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_subtract/java-run/com/systema/modernized/CicsProgramRegistry.java` | java-source | 266 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_subtract/java-run/com/systema/modernized/CobolFormatHelper.java` | java-source | 12684 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_subtract/java-run/com/systema/modernized/JclExecutionContext.java` | java-source | 1493 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_subtract/java-run/com/systema/modernized/SpringContextHelper.java` | java-source | 553 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_subtract/java-run/com/systema/modernized/native_gen/Negsub.java` | java-source | 9189 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_subtract/java-run/com/systema/modernized/runtime/AssignResult.java` | java-source | 343 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_subtract/java-run/com/systema/modernized/runtime/CobolArithmetic.java` | java-source | 4144 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_subtract/java-run/com/systema/modernized/runtime/CobolNumeric.java` | java-source | 12659 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_subtract/java-run/com/systema/modernized/runtime/CobolNumericSpec.java` | java-source | 921 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_subtract/java-run/com/systema/modernized/runtime/CobolRoundingMode.java` | java-source | 2012 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_subtract/java-run/com/systema/modernized/runtime/CobolSignPosition.java` | java-source | 102 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_subtract/java-run/com/systema/modernized/runtime/CobolUsage.java` | java-source | 107 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_subtract/java-run/com/systema/modernized/runtime/ProhibitedRoundingException.java` | java-source | 208 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_subtract/java-run/com/systema/modernized/runtime/SizeErrorPolicy.java` | java-source | 101 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_subtract/java-run/com/systema/modernized/runtime/UnsupportedPrecisionException.java` | java-source | 209 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_subtract/java-run/com/systema/modernized/runtime/VsamIndexedStore.java` | java-source | 5335 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_target_field_overflow/cobol-run/NEGOVER.cob` | cobol-source | 499 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_target_field_overflow/cobol-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_target_field_overflow/java-run/com/systema/modernized/CicsProgramRegistry.java` | java-source | 266 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_target_field_overflow/java-run/com/systema/modernized/CobolFormatHelper.java` | java-source | 12684 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_target_field_overflow/java-run/com/systema/modernized/JclExecutionContext.java` | java-source | 1493 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_target_field_overflow/java-run/com/systema/modernized/SpringContextHelper.java` | java-source | 553 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_target_field_overflow/java-run/com/systema/modernized/native_gen/Negover.java` | java-source | 8701 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_target_field_overflow/java-run/com/systema/modernized/runtime/AssignResult.java` | java-source | 343 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_target_field_overflow/java-run/com/systema/modernized/runtime/CobolArithmetic.java` | java-source | 4144 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_target_field_overflow/java-run/com/systema/modernized/runtime/CobolNumeric.java` | java-source | 12659 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_target_field_overflow/java-run/com/systema/modernized/runtime/CobolNumericSpec.java` | java-source | 921 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_target_field_overflow/java-run/com/systema/modernized/runtime/CobolRoundingMode.java` | java-source | 2012 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_target_field_overflow/java-run/com/systema/modernized/runtime/CobolSignPosition.java` | java-source | 102 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_target_field_overflow/java-run/com/systema/modernized/runtime/CobolUsage.java` | java-source | 107 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_target_field_overflow/java-run/com/systema/modernized/runtime/ProhibitedRoundingException.java` | java-source | 208 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_target_field_overflow/java-run/com/systema/modernized/runtime/SizeErrorPolicy.java` | java-source | 101 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_target_field_overflow/java-run/com/systema/modernized/runtime/UnsupportedPrecisionException.java` | java-source | 209 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_negative_target_field_overflow/java-run/com/systema/modernized/runtime/VsamIndexedStore.java` | java-source | 5335 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_non_rounded_truncation_arithmetic/cobol-run/TRUNCAR.cob` | cobol-source | 421 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_non_rounded_truncation_arithmetic/cobol-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_non_rounded_truncation_arithmetic/java-run/com/systema/modernized/CicsProgramRegistry.java` | java-source | 266 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_non_rounded_truncation_arithmetic/java-run/com/systema/modernized/CobolFormatHelper.java` | java-source | 12684 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_non_rounded_truncation_arithmetic/java-run/com/systema/modernized/JclExecutionContext.java` | java-source | 1493 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_non_rounded_truncation_arithmetic/java-run/com/systema/modernized/SpringContextHelper.java` | java-source | 553 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_non_rounded_truncation_arithmetic/java-run/com/systema/modernized/native_gen/Truncar.java` | java-source | 9643 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_non_rounded_truncation_arithmetic/java-run/com/systema/modernized/runtime/AssignResult.java` | java-source | 343 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_non_rounded_truncation_arithmetic/java-run/com/systema/modernized/runtime/CobolArithmetic.java` | java-source | 4144 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_non_rounded_truncation_arithmetic/java-run/com/systema/modernized/runtime/CobolNumeric.java` | java-source | 12659 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_non_rounded_truncation_arithmetic/java-run/com/systema/modernized/runtime/CobolNumericSpec.java` | java-source | 921 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_non_rounded_truncation_arithmetic/java-run/com/systema/modernized/runtime/CobolRoundingMode.java` | java-source | 2012 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_non_rounded_truncation_arithmetic/java-run/com/systema/modernized/runtime/CobolSignPosition.java` | java-source | 102 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_non_rounded_truncation_arithmetic/java-run/com/systema/modernized/runtime/CobolUsage.java` | java-source | 107 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_non_rounded_truncation_arithmetic/java-run/com/systema/modernized/runtime/ProhibitedRoundingException.java` | java-source | 208 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_non_rounded_truncation_arithmetic/java-run/com/systema/modernized/runtime/SizeErrorPolicy.java` | java-source | 101 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_non_rounded_truncation_arithmetic/java-run/com/systema/modernized/runtime/UnsupportedPrecisionException.java` | java-source | 209 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_non_rounded_truncation_arithmetic/java-run/com/systema/modernized/runtime/VsamIndexedStore.java` | java-source | 5335 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pic9_integer_arithmetic_baseline/cobol-run/PIC9BASE.cob` | cobol-source | 648 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pic9_integer_arithmetic_baseline/cobol-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pic9_integer_arithmetic_baseline/java-run/com/systema/modernized/CicsProgramRegistry.java` | java-source | 266 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pic9_integer_arithmetic_baseline/java-run/com/systema/modernized/CobolFormatHelper.java` | java-source | 12684 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pic9_integer_arithmetic_baseline/java-run/com/systema/modernized/JclExecutionContext.java` | java-source | 1493 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pic9_integer_arithmetic_baseline/java-run/com/systema/modernized/SpringContextHelper.java` | java-source | 553 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pic9_integer_arithmetic_baseline/java-run/com/systema/modernized/native_gen/Pic9base.java` | java-source | 9885 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pic9_integer_arithmetic_baseline/java-run/com/systema/modernized/runtime/AssignResult.java` | java-source | 343 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pic9_integer_arithmetic_baseline/java-run/com/systema/modernized/runtime/CobolArithmetic.java` | java-source | 4144 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pic9_integer_arithmetic_baseline/java-run/com/systema/modernized/runtime/CobolNumeric.java` | java-source | 12659 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pic9_integer_arithmetic_baseline/java-run/com/systema/modernized/runtime/CobolNumericSpec.java` | java-source | 921 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pic9_integer_arithmetic_baseline/java-run/com/systema/modernized/runtime/CobolRoundingMode.java` | java-source | 2012 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pic9_integer_arithmetic_baseline/java-run/com/systema/modernized/runtime/CobolSignPosition.java` | java-source | 102 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pic9_integer_arithmetic_baseline/java-run/com/systema/modernized/runtime/CobolUsage.java` | java-source | 107 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pic9_integer_arithmetic_baseline/java-run/com/systema/modernized/runtime/ProhibitedRoundingException.java` | java-source | 208 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pic9_integer_arithmetic_baseline/java-run/com/systema/modernized/runtime/SizeErrorPolicy.java` | java-source | 101 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pic9_integer_arithmetic_baseline/java-run/com/systema/modernized/runtime/UnsupportedPrecisionException.java` | java-source | 209 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pic9_integer_arithmetic_baseline/java-run/com/systema/modernized/runtime/VsamIndexedStore.java` | java-source | 5335 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pic9v99_implied_decimal_assignment/cobol-run/IMPDEC.cob` | cobol-source | 421 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pic9v99_implied_decimal_assignment/cobol-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pic9v99_implied_decimal_assignment/java-run/com/systema/modernized/CicsProgramRegistry.java` | java-source | 266 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pic9v99_implied_decimal_assignment/java-run/com/systema/modernized/CobolFormatHelper.java` | java-source | 12684 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pic9v99_implied_decimal_assignment/java-run/com/systema/modernized/JclExecutionContext.java` | java-source | 1493 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pic9v99_implied_decimal_assignment/java-run/com/systema/modernized/SpringContextHelper.java` | java-source | 553 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pic9v99_implied_decimal_assignment/java-run/com/systema/modernized/native_gen/Impdec.java` | java-source | 9652 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pic9v99_implied_decimal_assignment/java-run/com/systema/modernized/runtime/AssignResult.java` | java-source | 343 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pic9v99_implied_decimal_assignment/java-run/com/systema/modernized/runtime/CobolArithmetic.java` | java-source | 4144 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pic9v99_implied_decimal_assignment/java-run/com/systema/modernized/runtime/CobolNumeric.java` | java-source | 12659 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pic9v99_implied_decimal_assignment/java-run/com/systema/modernized/runtime/CobolNumericSpec.java` | java-source | 921 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pic9v99_implied_decimal_assignment/java-run/com/systema/modernized/runtime/CobolRoundingMode.java` | java-source | 2012 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pic9v99_implied_decimal_assignment/java-run/com/systema/modernized/runtime/CobolSignPosition.java` | java-source | 102 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pic9v99_implied_decimal_assignment/java-run/com/systema/modernized/runtime/CobolUsage.java` | java-source | 107 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pic9v99_implied_decimal_assignment/java-run/com/systema/modernized/runtime/ProhibitedRoundingException.java` | java-source | 208 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pic9v99_implied_decimal_assignment/java-run/com/systema/modernized/runtime/SizeErrorPolicy.java` | java-source | 101 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pic9v99_implied_decimal_assignment/java-run/com/systema/modernized/runtime/UnsupportedPrecisionException.java` | java-source | 209 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pic9v99_implied_decimal_assignment/java-run/com/systema/modernized/runtime/VsamIndexedStore.java` | java-source | 5335 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pics9_signed_arithmetic/cobol-run/SIGNEDAR.cob` | cobol-source | 706 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pics9_signed_arithmetic/cobol-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pics9_signed_arithmetic/java-run/com/systema/modernized/CicsProgramRegistry.java` | java-source | 266 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pics9_signed_arithmetic/java-run/com/systema/modernized/CobolFormatHelper.java` | java-source | 12684 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pics9_signed_arithmetic/java-run/com/systema/modernized/JclExecutionContext.java` | java-source | 1493 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pics9_signed_arithmetic/java-run/com/systema/modernized/SpringContextHelper.java` | java-source | 553 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pics9_signed_arithmetic/java-run/com/systema/modernized/native_gen/Signedar.java` | java-source | 9838 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pics9_signed_arithmetic/java-run/com/systema/modernized/runtime/AssignResult.java` | java-source | 343 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pics9_signed_arithmetic/java-run/com/systema/modernized/runtime/CobolArithmetic.java` | java-source | 4144 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pics9_signed_arithmetic/java-run/com/systema/modernized/runtime/CobolNumeric.java` | java-source | 12659 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pics9_signed_arithmetic/java-run/com/systema/modernized/runtime/CobolNumericSpec.java` | java-source | 921 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pics9_signed_arithmetic/java-run/com/systema/modernized/runtime/CobolRoundingMode.java` | java-source | 2012 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pics9_signed_arithmetic/java-run/com/systema/modernized/runtime/CobolSignPosition.java` | java-source | 102 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pics9_signed_arithmetic/java-run/com/systema/modernized/runtime/CobolUsage.java` | java-source | 107 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pics9_signed_arithmetic/java-run/com/systema/modernized/runtime/ProhibitedRoundingException.java` | java-source | 208 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pics9_signed_arithmetic/java-run/com/systema/modernized/runtime/SizeErrorPolicy.java` | java-source | 101 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pics9_signed_arithmetic/java-run/com/systema/modernized/runtime/UnsupportedPrecisionException.java` | java-source | 209 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_pics9_signed_arithmetic/java-run/com/systema/modernized/runtime/VsamIndexedStore.java` | java-source | 5335 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_positive_target_field_overflow/cobol-run/POSOVER.cob` | cobol-source | 451 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_positive_target_field_overflow/cobol-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_positive_target_field_overflow/java-run/com/systema/modernized/CicsProgramRegistry.java` | java-source | 266 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_positive_target_field_overflow/java-run/com/systema/modernized/CobolFormatHelper.java` | java-source | 12684 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_positive_target_field_overflow/java-run/com/systema/modernized/JclExecutionContext.java` | java-source | 1493 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_positive_target_field_overflow/java-run/com/systema/modernized/SpringContextHelper.java` | java-source | 553 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_positive_target_field_overflow/java-run/com/systema/modernized/native_gen/Posover.java` | java-source | 8731 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_positive_target_field_overflow/java-run/com/systema/modernized/runtime/AssignResult.java` | java-source | 343 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_positive_target_field_overflow/java-run/com/systema/modernized/runtime/CobolArithmetic.java` | java-source | 4144 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_positive_target_field_overflow/java-run/com/systema/modernized/runtime/CobolNumeric.java` | java-source | 12659 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_positive_target_field_overflow/java-run/com/systema/modernized/runtime/CobolNumericSpec.java` | java-source | 921 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_positive_target_field_overflow/java-run/com/systema/modernized/runtime/CobolRoundingMode.java` | java-source | 2012 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_positive_target_field_overflow/java-run/com/systema/modernized/runtime/CobolSignPosition.java` | java-source | 102 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_positive_target_field_overflow/java-run/com/systema/modernized/runtime/CobolUsage.java` | java-source | 107 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_positive_target_field_overflow/java-run/com/systema/modernized/runtime/ProhibitedRoundingException.java` | java-source | 208 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_positive_target_field_overflow/java-run/com/systema/modernized/runtime/SizeErrorPolicy.java` | java-source | 101 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_positive_target_field_overflow/java-run/com/systema/modernized/runtime/UnsupportedPrecisionException.java` | java-source | 209 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_positive_target_field_overflow/java-run/com/systema/modernized/runtime/VsamIndexedStore.java` | java-source | 5335 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_redefines_comp3_byte_view/cobol-run/REDEFCP3.cob` | cobol-source | 353 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_redefines_comp3_byte_view/cobol-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_redefines_comp3_byte_view/java-run/com/systema/modernized/CicsProgramRegistry.java` | java-source | 266 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_redefines_comp3_byte_view/java-run/com/systema/modernized/CobolFormatHelper.java` | java-source | 12684 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_redefines_comp3_byte_view/java-run/com/systema/modernized/JclExecutionContext.java` | java-source | 1493 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_redefines_comp3_byte_view/java-run/com/systema/modernized/SpringContextHelper.java` | java-source | 553 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_redefines_comp3_byte_view/java-run/com/systema/modernized/native_gen/Redefcp3.java` | java-source | 9128 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_redefines_comp3_byte_view/java-run/com/systema/modernized/runtime/AssignResult.java` | java-source | 343 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_redefines_comp3_byte_view/java-run/com/systema/modernized/runtime/CobolArithmetic.java` | java-source | 4144 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_redefines_comp3_byte_view/java-run/com/systema/modernized/runtime/CobolNumeric.java` | java-source | 12659 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_redefines_comp3_byte_view/java-run/com/systema/modernized/runtime/CobolNumericSpec.java` | java-source | 921 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_redefines_comp3_byte_view/java-run/com/systema/modernized/runtime/CobolRoundingMode.java` | java-source | 2012 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_redefines_comp3_byte_view/java-run/com/systema/modernized/runtime/CobolSignPosition.java` | java-source | 102 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_redefines_comp3_byte_view/java-run/com/systema/modernized/runtime/CobolUsage.java` | java-source | 107 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_redefines_comp3_byte_view/java-run/com/systema/modernized/runtime/ProhibitedRoundingException.java` | java-source | 208 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_redefines_comp3_byte_view/java-run/com/systema/modernized/runtime/SizeErrorPolicy.java` | java-source | 101 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_redefines_comp3_byte_view/java-run/com/systema/modernized/runtime/UnsupportedPrecisionException.java` | java-source | 209 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_redefines_comp3_byte_view/java-run/com/systema/modernized/runtime/VsamIndexedStore.java` | java-source | 5335 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_redefines_scalar_view/cobol-run/REDEFSC.cob` | cobol-source | 393 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_redefines_scalar_view/cobol-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_redefines_scalar_view/java-run/com/systema/modernized/CicsProgramRegistry.java` | java-source | 266 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_redefines_scalar_view/java-run/com/systema/modernized/CobolFormatHelper.java` | java-source | 12684 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_redefines_scalar_view/java-run/com/systema/modernized/JclExecutionContext.java` | java-source | 1493 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_redefines_scalar_view/java-run/com/systema/modernized/SpringContextHelper.java` | java-source | 553 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_redefines_scalar_view/java-run/com/systema/modernized/native_gen/Redefsc.java` | java-source | 9446 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_redefines_scalar_view/java-run/com/systema/modernized/runtime/AssignResult.java` | java-source | 343 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_redefines_scalar_view/java-run/com/systema/modernized/runtime/CobolArithmetic.java` | java-source | 4144 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_redefines_scalar_view/java-run/com/systema/modernized/runtime/CobolNumeric.java` | java-source | 12659 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_redefines_scalar_view/java-run/com/systema/modernized/runtime/CobolNumericSpec.java` | java-source | 921 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_redefines_scalar_view/java-run/com/systema/modernized/runtime/CobolRoundingMode.java` | java-source | 2012 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_redefines_scalar_view/java-run/com/systema/modernized/runtime/CobolSignPosition.java` | java-source | 102 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_redefines_scalar_view/java-run/com/systema/modernized/runtime/CobolUsage.java` | java-source | 107 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_redefines_scalar_view/java-run/com/systema/modernized/runtime/ProhibitedRoundingException.java` | java-source | 208 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_redefines_scalar_view/java-run/com/systema/modernized/runtime/SizeErrorPolicy.java` | java-source | 101 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_redefines_scalar_view/java-run/com/systema/modernized/runtime/UnsupportedPrecisionException.java` | java-source | 209 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_redefines_scalar_view/java-run/com/systema/modernized/runtime/VsamIndexedStore.java` | java-source | 5335 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_rounded_arithmetic/cobol-run/ROUNDEDAR.cob` | cobol-source | 431 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_rounded_arithmetic/cobol-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_rounded_arithmetic/java-run/com/systema/modernized/CicsProgramRegistry.java` | java-source | 266 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_rounded_arithmetic/java-run/com/systema/modernized/CobolFormatHelper.java` | java-source | 12684 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_rounded_arithmetic/java-run/com/systema/modernized/JclExecutionContext.java` | java-source | 1493 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_rounded_arithmetic/java-run/com/systema/modernized/SpringContextHelper.java` | java-source | 553 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_rounded_arithmetic/java-run/com/systema/modernized/native_gen/Roundedar.java` | java-source | 9659 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_rounded_arithmetic/java-run/com/systema/modernized/runtime/AssignResult.java` | java-source | 343 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_rounded_arithmetic/java-run/com/systema/modernized/runtime/CobolArithmetic.java` | java-source | 4144 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_rounded_arithmetic/java-run/com/systema/modernized/runtime/CobolNumeric.java` | java-source | 12659 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_rounded_arithmetic/java-run/com/systema/modernized/runtime/CobolNumericSpec.java` | java-source | 921 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_rounded_arithmetic/java-run/com/systema/modernized/runtime/CobolRoundingMode.java` | java-source | 2012 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_rounded_arithmetic/java-run/com/systema/modernized/runtime/CobolSignPosition.java` | java-source | 102 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_rounded_arithmetic/java-run/com/systema/modernized/runtime/CobolUsage.java` | java-source | 107 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_rounded_arithmetic/java-run/com/systema/modernized/runtime/ProhibitedRoundingException.java` | java-source | 208 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_rounded_arithmetic/java-run/com/systema/modernized/runtime/SizeErrorPolicy.java` | java-source | 101 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_rounded_arithmetic/java-run/com/systema/modernized/runtime/UnsupportedPrecisionException.java` | java-source | 209 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_rounded_arithmetic/java-run/com/systema/modernized/runtime/VsamIndexedStore.java` | java-source | 5335 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_two_operand_display/cobol-run/TWODISP.cob` | cobol-source | 384 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_two_operand_display/cobol-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_two_operand_display/java-run/com/systema/modernized/CicsProgramRegistry.java` | java-source | 266 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_two_operand_display/java-run/com/systema/modernized/CobolFormatHelper.java` | java-source | 12684 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_two_operand_display/java-run/com/systema/modernized/JclExecutionContext.java` | java-source | 1493 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_two_operand_display/java-run/com/systema/modernized/SpringContextHelper.java` | java-source | 553 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_two_operand_display/java-run/com/systema/modernized/native_gen/Twodisp.java` | java-source | 9133 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_two_operand_display/java-run/com/systema/modernized/runtime/AssignResult.java` | java-source | 343 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_two_operand_display/java-run/com/systema/modernized/runtime/CobolArithmetic.java` | java-source | 4144 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_two_operand_display/java-run/com/systema/modernized/runtime/CobolNumeric.java` | java-source | 12659 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_two_operand_display/java-run/com/systema/modernized/runtime/CobolNumericSpec.java` | java-source | 921 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_two_operand_display/java-run/com/systema/modernized/runtime/CobolRoundingMode.java` | java-source | 2012 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_two_operand_display/java-run/com/systema/modernized/runtime/CobolSignPosition.java` | java-source | 102 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_two_operand_display/java-run/com/systema/modernized/runtime/CobolUsage.java` | java-source | 107 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_two_operand_display/java-run/com/systema/modernized/runtime/ProhibitedRoundingException.java` | java-source | 208 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_two_operand_display/java-run/com/systema/modernized/runtime/SizeErrorPolicy.java` | java-source | 101 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_two_operand_display/java-run/com/systema/modernized/runtime/UnsupportedPrecisionException.java` | java-source | 209 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_two_operand_display/java-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_unsigned_drops_sign/cobol-run/DROPSIGN.cob` | cobol-source | 319 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_unsigned_drops_sign/cobol-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_unsigned_drops_sign/java-run/com/systema/modernized/CicsProgramRegistry.java` | java-source | 266 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_unsigned_drops_sign/java-run/com/systema/modernized/CobolFormatHelper.java` | java-source | 12684 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_unsigned_drops_sign/java-run/com/systema/modernized/JclExecutionContext.java` | java-source | 1493 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_unsigned_drops_sign/java-run/com/systema/modernized/SpringContextHelper.java` | java-source | 553 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_unsigned_drops_sign/java-run/com/systema/modernized/native_gen/Dropsign.java` | java-source | 7609 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_unsigned_drops_sign/java-run/com/systema/modernized/runtime/AssignResult.java` | java-source | 343 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_unsigned_drops_sign/java-run/com/systema/modernized/runtime/CobolArithmetic.java` | java-source | 4144 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_unsigned_drops_sign/java-run/com/systema/modernized/runtime/CobolNumeric.java` | java-source | 12659 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_unsigned_drops_sign/java-run/com/systema/modernized/runtime/CobolNumericSpec.java` | java-source | 921 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_unsigned_drops_sign/java-run/com/systema/modernized/runtime/CobolRoundingMode.java` | java-source | 2012 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_unsigned_drops_sign/java-run/com/systema/modernized/runtime/CobolSignPosition.java` | java-source | 102 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_unsigned_drops_sign/java-run/com/systema/modernized/runtime/CobolUsage.java` | java-source | 107 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_unsigned_drops_sign/java-run/com/systema/modernized/runtime/ProhibitedRoundingException.java` | java-source | 208 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_unsigned_drops_sign/java-run/com/systema/modernized/runtime/SizeErrorPolicy.java` | java-source | 101 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_unsigned_drops_sign/java-run/com/systema/modernized/runtime/UnsupportedPrecisionException.java` | java-source | 209 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_unsigned_drops_sign/java-run/com/systema/modernized/runtime/VsamIndexedStore.java` | java-source | 5335 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_zero_fill_formatting/cobol-run/ZEROFILL.cob` | cobol-source | 294 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_zero_fill_formatting/cobol-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_zero_fill_formatting/java-run/com/systema/modernized/CicsProgramRegistry.java` | java-source | 266 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_zero_fill_formatting/java-run/com/systema/modernized/CobolFormatHelper.java` | java-source | 12684 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_zero_fill_formatting/java-run/com/systema/modernized/JclExecutionContext.java` | java-source | 1493 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_zero_fill_formatting/java-run/com/systema/modernized/SpringContextHelper.java` | java-source | 553 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_zero_fill_formatting/java-run/com/systema/modernized/native_gen/Zerofill.java` | java-source | 7527 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_zero_fill_formatting/java-run/com/systema/modernized/runtime/AssignResult.java` | java-source | 343 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_zero_fill_formatting/java-run/com/systema/modernized/runtime/CobolArithmetic.java` | java-source | 4144 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_zero_fill_formatting/java-run/com/systema/modernized/runtime/CobolNumeric.java` | java-source | 12659 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_zero_fill_formatting/java-run/com/systema/modernized/runtime/CobolNumericSpec.java` | java-source | 921 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_zero_fill_formatting/java-run/com/systema/modernized/runtime/CobolRoundingMode.java` | java-source | 2012 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_zero_fill_formatting/java-run/com/systema/modernized/runtime/CobolSignPosition.java` | java-source | 102 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_zero_fill_formatting/java-run/com/systema/modernized/runtime/CobolUsage.java` | java-source | 107 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_zero_fill_formatting/java-run/com/systema/modernized/runtime/ProhibitedRoundingException.java` | java-source | 208 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_zero_fill_formatting/java-run/com/systema/modernized/runtime/SizeErrorPolicy.java` | java-source | 101 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_zero_fill_formatting/java-run/com/systema/modernized/runtime/UnsupportedPrecisionException.java` | java-source | 209 | test-output-artifact |
| `artifacts/parity-failures/milestone_b_zero_fill_formatting/java-run/com/systema/modernized/runtime/VsamIndexedStore.java` | java-source | 5335 | test-output-artifact |
| `artifacts/parity-failures/parity_call_by_content/cobol-run/CALLCONT.cob` | cobol-source | 593 | test-output-artifact |
| `artifacts/parity-failures/parity_call_by_content/cobol-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/parity_call_by_content/java-run/com/systema/modernized/CicsProgramRegistry.java` | java-source | 266 | test-output-artifact |
| `artifacts/parity-failures/parity_call_by_content/java-run/com/systema/modernized/CobolFormatHelper.java` | java-source | 12602 | test-output-artifact |
| `artifacts/parity-failures/parity_call_by_content/java-run/com/systema/modernized/JclExecutionContext.java` | java-source | 1493 | test-output-artifact |
| `artifacts/parity-failures/parity_call_by_content/java-run/com/systema/modernized/SpringContextHelper.java` | java-source | 553 | test-output-artifact |
| `artifacts/parity-failures/parity_call_by_content/java-run/com/systema/modernized/native_gen/Callcont.java` | java-source | 10597 | test-output-artifact |
| `artifacts/parity-failures/parity_call_by_content/java-run/com/systema/modernized/runtime/AssignResult.java` | java-source | 343 | test-output-artifact |
| `artifacts/parity-failures/parity_call_by_content/java-run/com/systema/modernized/runtime/CobolArithmetic.java` | java-source | 4385 | test-output-artifact |
| `artifacts/parity-failures/parity_call_by_content/java-run/com/systema/modernized/runtime/CobolNumeric.java` | java-source | 13361 | test-output-artifact |
| `artifacts/parity-failures/parity_call_by_content/java-run/com/systema/modernized/runtime/CobolNumericSpec.java` | java-source | 921 | test-output-artifact |
| `artifacts/parity-failures/parity_call_by_content/java-run/com/systema/modernized/runtime/CobolRoundingMode.java` | java-source | 2012 | test-output-artifact |
| `artifacts/parity-failures/parity_call_by_content/java-run/com/systema/modernized/runtime/CobolSignPosition.java` | java-source | 102 | test-output-artifact |
| `artifacts/parity-failures/parity_call_by_content/java-run/com/systema/modernized/runtime/CobolUsage.java` | java-source | 107 | test-output-artifact |
| `artifacts/parity-failures/parity_call_by_content/java-run/com/systema/modernized/runtime/ProhibitedRoundingException.java` | java-source | 208 | test-output-artifact |
| `artifacts/parity-failures/parity_call_by_content/java-run/com/systema/modernized/runtime/SizeErrorPolicy.java` | java-source | 101 | test-output-artifact |
| `artifacts/parity-failures/parity_call_by_content/java-run/com/systema/modernized/runtime/UnsupportedPrecisionException.java` | java-source | 209 | test-output-artifact |
| `artifacts/parity-failures/parity_call_by_content/java-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/parity_call_by_content_bigdecimal/cobol-run/CALLCONTB.cob` | cobol-source | 612 | test-output-artifact |
| `artifacts/parity-failures/parity_call_by_content_bigdecimal/cobol-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/parity_call_by_content_bigdecimal/java-run/com/systema/modernized/CicsProgramRegistry.java` | java-source | 266 | test-output-artifact |
| `artifacts/parity-failures/parity_call_by_content_bigdecimal/java-run/com/systema/modernized/CobolFormatHelper.java` | java-source | 12602 | test-output-artifact |
| `artifacts/parity-failures/parity_call_by_content_bigdecimal/java-run/com/systema/modernized/JclExecutionContext.java` | java-source | 1493 | test-output-artifact |
| `artifacts/parity-failures/parity_call_by_content_bigdecimal/java-run/com/systema/modernized/SpringContextHelper.java` | java-source | 553 | test-output-artifact |
| `artifacts/parity-failures/parity_call_by_content_bigdecimal/java-run/com/systema/modernized/native_gen/Callcontb.java` | java-source | 11369 | test-output-artifact |
| `artifacts/parity-failures/parity_call_by_content_bigdecimal/java-run/com/systema/modernized/runtime/AssignResult.java` | java-source | 343 | test-output-artifact |
| `artifacts/parity-failures/parity_call_by_content_bigdecimal/java-run/com/systema/modernized/runtime/CobolArithmetic.java` | java-source | 4385 | test-output-artifact |
| `artifacts/parity-failures/parity_call_by_content_bigdecimal/java-run/com/systema/modernized/runtime/CobolNumeric.java` | java-source | 13361 | test-output-artifact |
| `artifacts/parity-failures/parity_call_by_content_bigdecimal/java-run/com/systema/modernized/runtime/CobolNumericSpec.java` | java-source | 921 | test-output-artifact |
| `artifacts/parity-failures/parity_call_by_content_bigdecimal/java-run/com/systema/modernized/runtime/CobolRoundingMode.java` | java-source | 2012 | test-output-artifact |
| `artifacts/parity-failures/parity_call_by_content_bigdecimal/java-run/com/systema/modernized/runtime/CobolSignPosition.java` | java-source | 102 | test-output-artifact |
| `artifacts/parity-failures/parity_call_by_content_bigdecimal/java-run/com/systema/modernized/runtime/CobolUsage.java` | java-source | 107 | test-output-artifact |
| `artifacts/parity-failures/parity_call_by_content_bigdecimal/java-run/com/systema/modernized/runtime/ProhibitedRoundingException.java` | java-source | 208 | test-output-artifact |
| `artifacts/parity-failures/parity_call_by_content_bigdecimal/java-run/com/systema/modernized/runtime/SizeErrorPolicy.java` | java-source | 101 | test-output-artifact |
| `artifacts/parity-failures/parity_call_by_content_bigdecimal/java-run/com/systema/modernized/runtime/UnsupportedPrecisionException.java` | java-source | 209 | test-output-artifact |
| `artifacts/parity-failures/parity_corresponding/cobol-run/PCORR.cob` | cobol-source | 684 | test-output-artifact |
| `artifacts/parity-failures/parity_corresponding/cobol-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/parity_corresponding/java-run/com/systema/modernized/CicsProgramRegistry.java` | java-source | 266 | test-output-artifact |
| `artifacts/parity-failures/parity_corresponding/java-run/com/systema/modernized/CobolFormatHelper.java` | java-source | 12602 | test-output-artifact |
| `artifacts/parity-failures/parity_corresponding/java-run/com/systema/modernized/JclExecutionContext.java` | java-source | 1493 | test-output-artifact |
| `artifacts/parity-failures/parity_corresponding/java-run/com/systema/modernized/SpringContextHelper.java` | java-source | 553 | test-output-artifact |
| `artifacts/parity-failures/parity_corresponding/java-run/com/systema/modernized/native_gen/Pcorr.java` | java-source | 10493 | test-output-artifact |
| `artifacts/parity-failures/parity_corresponding/java-run/com/systema/modernized/runtime/AssignResult.java` | java-source | 343 | test-output-artifact |
| `artifacts/parity-failures/parity_corresponding/java-run/com/systema/modernized/runtime/CobolArithmetic.java` | java-source | 4385 | test-output-artifact |
| `artifacts/parity-failures/parity_corresponding/java-run/com/systema/modernized/runtime/CobolNumeric.java` | java-source | 13361 | test-output-artifact |
| `artifacts/parity-failures/parity_corresponding/java-run/com/systema/modernized/runtime/CobolNumericSpec.java` | java-source | 921 | test-output-artifact |
| `artifacts/parity-failures/parity_corresponding/java-run/com/systema/modernized/runtime/CobolRoundingMode.java` | java-source | 2012 | test-output-artifact |
| `artifacts/parity-failures/parity_corresponding/java-run/com/systema/modernized/runtime/CobolSignPosition.java` | java-source | 102 | test-output-artifact |
| `artifacts/parity-failures/parity_corresponding/java-run/com/systema/modernized/runtime/CobolUsage.java` | java-source | 107 | test-output-artifact |
| `artifacts/parity-failures/parity_corresponding/java-run/com/systema/modernized/runtime/ProhibitedRoundingException.java` | java-source | 208 | test-output-artifact |
| `artifacts/parity-failures/parity_corresponding/java-run/com/systema/modernized/runtime/SizeErrorPolicy.java` | java-source | 101 | test-output-artifact |
| `artifacts/parity-failures/parity_corresponding/java-run/com/systema/modernized/runtime/UnsupportedPrecisionException.java` | java-source | 209 | test-output-artifact |
| `artifacts/parity-failures/parity_corresponding/java-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/parity_indexed_file_missing_key/cobol-run/IDXMISS.cob` | cobol-source | 915 | test-output-artifact |
| `artifacts/parity-failures/parity_indexed_file_missing_key/cobol-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/parity_indexed_file_missing_key/java-run/com/systema/modernized/CicsProgramRegistry.java` | java-source | 266 | test-output-artifact |
| `artifacts/parity-failures/parity_indexed_file_missing_key/java-run/com/systema/modernized/CobolFormatHelper.java` | java-source | 12602 | test-output-artifact |
| `artifacts/parity-failures/parity_indexed_file_missing_key/java-run/com/systema/modernized/JclExecutionContext.java` | java-source | 1493 | test-output-artifact |
| `artifacts/parity-failures/parity_indexed_file_missing_key/java-run/com/systema/modernized/SpringContextHelper.java` | java-source | 553 | test-output-artifact |
| `artifacts/parity-failures/parity_indexed_file_missing_key/java-run/com/systema/modernized/native_gen/Idxmiss.java` | java-source | 27560 | test-output-artifact |
| `artifacts/parity-failures/parity_indexed_file_missing_key/java-run/com/systema/modernized/runtime/AssignResult.java` | java-source | 343 | test-output-artifact |
| `artifacts/parity-failures/parity_indexed_file_missing_key/java-run/com/systema/modernized/runtime/CobolArithmetic.java` | java-source | 4385 | test-output-artifact |
| `artifacts/parity-failures/parity_indexed_file_missing_key/java-run/com/systema/modernized/runtime/CobolNumeric.java` | java-source | 13361 | test-output-artifact |
| `artifacts/parity-failures/parity_indexed_file_missing_key/java-run/com/systema/modernized/runtime/CobolNumericSpec.java` | java-source | 921 | test-output-artifact |
| `artifacts/parity-failures/parity_indexed_file_missing_key/java-run/com/systema/modernized/runtime/CobolRoundingMode.java` | java-source | 2012 | test-output-artifact |
| `artifacts/parity-failures/parity_indexed_file_missing_key/java-run/com/systema/modernized/runtime/CobolSignPosition.java` | java-source | 102 | test-output-artifact |
| `artifacts/parity-failures/parity_indexed_file_missing_key/java-run/com/systema/modernized/runtime/CobolUsage.java` | java-source | 107 | test-output-artifact |
| `artifacts/parity-failures/parity_indexed_file_missing_key/java-run/com/systema/modernized/runtime/ProhibitedRoundingException.java` | java-source | 208 | test-output-artifact |
| `artifacts/parity-failures/parity_indexed_file_missing_key/java-run/com/systema/modernized/runtime/SizeErrorPolicy.java` | java-source | 101 | test-output-artifact |
| `artifacts/parity-failures/parity_indexed_file_missing_key/java-run/com/systema/modernized/runtime/UnsupportedPrecisionException.java` | java-source | 209 | test-output-artifact |
| `artifacts/parity-failures/parity_on_size_error_explicit/cobol-run/SIZEERR.cob` | cobol-source | 333 | test-output-artifact |
| `artifacts/parity-failures/parity_on_size_error_explicit/cobol-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/parity_on_size_error_explicit/java-run/com/systema/modernized/CicsProgramRegistry.java` | java-source | 266 | test-output-artifact |
| `artifacts/parity-failures/parity_on_size_error_explicit/java-run/com/systema/modernized/CobolFormatHelper.java` | java-source | 12602 | test-output-artifact |
| `artifacts/parity-failures/parity_on_size_error_explicit/java-run/com/systema/modernized/JclExecutionContext.java` | java-source | 1493 | test-output-artifact |
| `artifacts/parity-failures/parity_on_size_error_explicit/java-run/com/systema/modernized/SpringContextHelper.java` | java-source | 553 | test-output-artifact |
| `artifacts/parity-failures/parity_on_size_error_explicit/java-run/com/systema/modernized/native_gen/Sizeerr.java` | java-source | 8075 | test-output-artifact |
| `artifacts/parity-failures/parity_on_size_error_explicit/java-run/com/systema/modernized/runtime/AssignResult.java` | java-source | 343 | test-output-artifact |
| `artifacts/parity-failures/parity_on_size_error_explicit/java-run/com/systema/modernized/runtime/CobolArithmetic.java` | java-source | 4385 | test-output-artifact |
| `artifacts/parity-failures/parity_on_size_error_explicit/java-run/com/systema/modernized/runtime/CobolNumeric.java` | java-source | 13361 | test-output-artifact |
| `artifacts/parity-failures/parity_on_size_error_explicit/java-run/com/systema/modernized/runtime/CobolNumericSpec.java` | java-source | 921 | test-output-artifact |
| `artifacts/parity-failures/parity_on_size_error_explicit/java-run/com/systema/modernized/runtime/CobolRoundingMode.java` | java-source | 2012 | test-output-artifact |
| `artifacts/parity-failures/parity_on_size_error_explicit/java-run/com/systema/modernized/runtime/CobolSignPosition.java` | java-source | 102 | test-output-artifact |
| `artifacts/parity-failures/parity_on_size_error_explicit/java-run/com/systema/modernized/runtime/CobolUsage.java` | java-source | 107 | test-output-artifact |
| `artifacts/parity-failures/parity_on_size_error_explicit/java-run/com/systema/modernized/runtime/ProhibitedRoundingException.java` | java-source | 208 | test-output-artifact |
| `artifacts/parity-failures/parity_on_size_error_explicit/java-run/com/systema/modernized/runtime/SizeErrorPolicy.java` | java-source | 101 | test-output-artifact |
| `artifacts/parity-failures/parity_on_size_error_explicit/java-run/com/systema/modernized/runtime/UnsupportedPrecisionException.java` | java-source | 209 | test-output-artifact |
| `artifacts/parity-failures/parity_perform_varying/cobol-run/PVARY.cob` | cobol-source | 400 | test-output-artifact |
| `artifacts/parity-failures/parity_perform_varying/cobol-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/parity_perform_varying/java-run/com/systema/modernized/CicsProgramRegistry.java` | java-source | 266 | test-output-artifact |
| `artifacts/parity-failures/parity_perform_varying/java-run/com/systema/modernized/CobolFormatHelper.java` | java-source | 12602 | test-output-artifact |
| `artifacts/parity-failures/parity_perform_varying/java-run/com/systema/modernized/JclExecutionContext.java` | java-source | 1493 | test-output-artifact |
| `artifacts/parity-failures/parity_perform_varying/java-run/com/systema/modernized/SpringContextHelper.java` | java-source | 553 | test-output-artifact |
| `artifacts/parity-failures/parity_perform_varying/java-run/com/systema/modernized/native_gen/Pvary.java` | java-source | 7716 | test-output-artifact |
| `artifacts/parity-failures/parity_perform_varying/java-run/com/systema/modernized/runtime/AssignResult.java` | java-source | 343 | test-output-artifact |
| `artifacts/parity-failures/parity_perform_varying/java-run/com/systema/modernized/runtime/CobolArithmetic.java` | java-source | 4385 | test-output-artifact |
| `artifacts/parity-failures/parity_perform_varying/java-run/com/systema/modernized/runtime/CobolNumeric.java` | java-source | 13361 | test-output-artifact |
| `artifacts/parity-failures/parity_perform_varying/java-run/com/systema/modernized/runtime/CobolNumericSpec.java` | java-source | 921 | test-output-artifact |
| `artifacts/parity-failures/parity_perform_varying/java-run/com/systema/modernized/runtime/CobolRoundingMode.java` | java-source | 2012 | test-output-artifact |
| `artifacts/parity-failures/parity_perform_varying/java-run/com/systema/modernized/runtime/CobolSignPosition.java` | java-source | 102 | test-output-artifact |
| `artifacts/parity-failures/parity_perform_varying/java-run/com/systema/modernized/runtime/CobolUsage.java` | java-source | 107 | test-output-artifact |
| `artifacts/parity-failures/parity_perform_varying/java-run/com/systema/modernized/runtime/ProhibitedRoundingException.java` | java-source | 208 | test-output-artifact |
| `artifacts/parity-failures/parity_perform_varying/java-run/com/systema/modernized/runtime/SizeErrorPolicy.java` | java-source | 101 | test-output-artifact |
| `artifacts/parity-failures/parity_perform_varying/java-run/com/systema/modernized/runtime/UnsupportedPrecisionException.java` | java-source | 209 | test-output-artifact |
| `artifacts/parity-failures/parity_perform_varying/java-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/parity_redefines_group_view/cobol-run/REFGRP.cob` | cobol-source | 511 | test-output-artifact |
| `artifacts/parity-failures/parity_redefines_group_view/cobol-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/parity_redefines_group_view/java-run/com/systema/modernized/CicsProgramRegistry.java` | java-source | 266 | test-output-artifact |
| `artifacts/parity-failures/parity_redefines_group_view/java-run/com/systema/modernized/CobolFormatHelper.java` | java-source | 12602 | test-output-artifact |
| `artifacts/parity-failures/parity_redefines_group_view/java-run/com/systema/modernized/JclExecutionContext.java` | java-source | 1493 | test-output-artifact |
| `artifacts/parity-failures/parity_redefines_group_view/java-run/com/systema/modernized/SpringContextHelper.java` | java-source | 553 | test-output-artifact |
| `artifacts/parity-failures/parity_redefines_group_view/java-run/com/systema/modernized/native_gen/Refgrp.java` | java-source | 13016 | test-output-artifact |
| `artifacts/parity-failures/parity_redefines_group_view/java-run/com/systema/modernized/runtime/AssignResult.java` | java-source | 343 | test-output-artifact |
| `artifacts/parity-failures/parity_redefines_group_view/java-run/com/systema/modernized/runtime/CobolArithmetic.java` | java-source | 4385 | test-output-artifact |
| `artifacts/parity-failures/parity_redefines_group_view/java-run/com/systema/modernized/runtime/CobolNumeric.java` | java-source | 13361 | test-output-artifact |
| `artifacts/parity-failures/parity_redefines_group_view/java-run/com/systema/modernized/runtime/CobolNumericSpec.java` | java-source | 921 | test-output-artifact |
| `artifacts/parity-failures/parity_redefines_group_view/java-run/com/systema/modernized/runtime/CobolRoundingMode.java` | java-source | 2012 | test-output-artifact |
| `artifacts/parity-failures/parity_redefines_group_view/java-run/com/systema/modernized/runtime/CobolSignPosition.java` | java-source | 102 | test-output-artifact |
| `artifacts/parity-failures/parity_redefines_group_view/java-run/com/systema/modernized/runtime/CobolUsage.java` | java-source | 107 | test-output-artifact |
| `artifacts/parity-failures/parity_redefines_group_view/java-run/com/systema/modernized/runtime/ProhibitedRoundingException.java` | java-source | 208 | test-output-artifact |
| `artifacts/parity-failures/parity_redefines_group_view/java-run/com/systema/modernized/runtime/SizeErrorPolicy.java` | java-source | 101 | test-output-artifact |
| `artifacts/parity-failures/parity_redefines_group_view/java-run/com/systema/modernized/runtime/UnsupportedPrecisionException.java` | java-source | 209 | test-output-artifact |
| `artifacts/parity-failures/parity_relative_file_random_access/cobol-run/RELFILE.cob` | cobol-source | 1112 | test-output-artifact |
| `artifacts/parity-failures/parity_relative_file_random_access/cobol-run/stdin.txt` | data/text | 0 | test-output-artifact |
| `artifacts/parity-failures/parity_relative_file_random_access/java-run/com/systema/modernized/CicsProgramRegistry.java` | java-source | 266 | test-output-artifact |
| `artifacts/parity-failures/parity_relative_file_random_access/java-run/com/systema/modernized/CobolFormatHelper.java` | java-source | 12602 | test-output-artifact |
| `artifacts/parity-failures/parity_relative_file_random_access/java-run/com/systema/modernized/JclExecutionContext.java` | java-source | 1493 | test-output-artifact |
| `artifacts/parity-failures/parity_relative_file_random_access/java-run/com/systema/modernized/SpringContextHelper.java` | java-source | 553 | test-output-artifact |
| `artifacts/parity-failures/parity_relative_file_random_access/java-run/com/systema/modernized/native_gen/Relfile.java` | java-source | 26168 | test-output-artifact |
| `artifacts/parity-failures/parity_relative_file_random_access/java-run/com/systema/modernized/runtime/AssignResult.java` | java-source | 343 | test-output-artifact |
| `artifacts/parity-failures/parity_relative_file_random_access/java-run/com/systema/modernized/runtime/CobolArithmetic.java` | java-source | 4385 | test-output-artifact |
| `artifacts/parity-failures/parity_relative_file_random_access/java-run/com/systema/modernized/runtime/CobolNumeric.java` | java-source | 13361 | test-output-artifact |
| `artifacts/parity-failures/parity_relative_file_random_access/java-run/com/systema/modernized/runtime/CobolNumericSpec.java` | java-source | 921 | test-output-artifact |
| `artifacts/parity-failures/parity_relative_file_random_access/java-run/com/systema/modernized/runtime/CobolRoundingMode.java` | java-source | 2012 | test-output-artifact |
| `artifacts/parity-failures/parity_relative_file_random_access/java-run/com/systema/modernized/runtime/CobolSignPosition.java` | java-source | 102 | test-output-artifact |
| `artifacts/parity-failures/parity_relative_file_random_access/java-run/com/systema/modernized/runtime/CobolUsage.java` | java-source | 107 | test-output-artifact |
| `artifacts/parity-failures/parity_relative_file_random_access/java-run/com/systema/modernized/runtime/ProhibitedRoundingException.java` | java-source | 208 | test-output-artifact |
| `artifacts/parity-failures/parity_relative_file_random_access/java-run/com/systema/modernized/runtime/SizeErrorPolicy.java` | java-source | 101 | test-output-artifact |
| `artifacts/parity-failures/parity_relative_file_random_access/java-run/com/systema/modernized/runtime/UnsupportedPrecisionException.java` | java-source | 209 | test-output-artifact |
| `artifacts/releases/systemaops-release.zip` | archive | 614474 | test-output-artifact |
| `artifacts/releases/systemaops-release.zip.sha256` | checksum | 64 | test-output-artifact |
| `artifacts/verification/final_verification.json` | config/data | 354 | test-output-artifact |

## Untracked working-tree paths (WIP / artifacts — NOT in git)

- `artifacts/parity-failures/DB2CURNULL01/`
- `artifacts/parity-failures/add3/`
- `artifacts/parity-failures/be02_comp_arithmetic/`
- `artifacts/parity-failures/be02_mut/`
- `artifacts/parity-failures/be02_orig/`
- `artifacts/parity-failures/be03_mut/`
- `artifacts/parity-failures/be06_mut/`
- `artifacts/parity-failures/be06_orig/`
- `artifacts/parity-failures/be06_record_sequential/`
- `artifacts/parity-failures/be07_mut/`
- `artifacts/parity-failures/be07_orig/`
- `artifacts/parity-failures/be07_size_error/`
- `artifacts/parity-failures/be11_mut/`
- `artifacts/parity-failures/be11_orig/`
- `artifacts/parity-failures/be11_string_pointer/`
- `artifacts/parity-failures/be12_edited_numeric/`
- `artifacts/parity-failures/be12_mut/`
- `artifacts/parity-failures/be12_orig/`
- `artifacts/parity-failures/call_by_reference_mutant/`
- `artifacts/parity-failures/call_by_reference_mutation/`
- `artifacts/parity-failures/comp5_arithmetic/`
- `artifacts/parity-failures/comp5_mutant/`
- `artifacts/parity-failures/comp_binary_arithmetic/`
- `artifacts/parity-failures/comp_binary_mutant/`
- `artifacts/parity-failures/evaluate_mutant/`
- `artifacts/parity-failures/evaluate_when_other/`
- `artifacts/parity-failures/file_sequential_fixed/`
- `artifacts/parity-failures/file_sequential_fixed_mutant/`
- `artifacts/parity-failures/group_move/`
- `artifacts/parity-failures/group_move_mutant/`
- `artifacts/parity-failures/idxmiss_test/`
- `artifacts/parity-failures/occurs_fixed_and_odo/`
- `artifacts/parity-failures/occurs_odo_mutant/`
- `artifacts/parity-failures/occurs_odo_original/`
- `artifacts/parity-failures/parity_evaluate_when_other/`
- `artifacts/parity-failures/parity_indexed_file_missing_key/java-run/org/`
- `artifacts/parity-failures/parity_indexed_file_missing_key/java-run/stdin.txt`
- `artifacts/parity-failures/parity_occurs_depending_on/`
- `artifacts/parity-failures/parity_redefines_occurs_group/`
- `artifacts/parity-failures/parity_relative_file_random_access/java-run/org/`
- `artifacts/parity-failures/parity_relative_file_random_access/java-run/stdin.txt`
- `artifacts/parity-failures/perform_thru/`
- `artifacts/parity-failures/perform_thru_mutant/`
- `artifacts/parity-failures/pic_edited_numeric/`
- `artifacts/parity-failures/pic_edited_numeric_mutant/`
- `artifacts/parity-failures/relfile_test/`
- `artifacts/parity-failures/sections_fallthrough/`
- `artifacts/parity-failures/sections_mutant/`
- `artifacts/parity-failures/sort_input_procedure/`
- `artifacts/parity-failures/sort_input_procedure_mutant/`
- `artifacts/parity-failures/string_mutant/`
- `artifacts/parity-failures/string_with_pointer/`
- `docs/PARSER_IR_FORENSIC_AUDIT.md`
- `modernize_v2/analysis/resolver.py`
- `opencode.json`
- `reports/e2e-neg-goldenpay/`
- `reports/fresh-e2e-transformable/`
- `reports/verified-capability-matrix.md`
- `reports/verified-file-inventory.md`
- `reports/verified-jdk-compatibility.md`
- `reports/verified-project-gap-analysis.md`
- `sql_log_new.txt`
- `test_callchain.py`
- `tests/e2e/screenshots/`
- `tests/test_behavioral_equivalence.py`
- `tests/test_validate_startup.py`
- `tests/utils/behavioral_equivalence.py`
- `tests/v2/test_parser_r5_clause_fidelity.py`
- `tests/v2/test_t2b05_reference_resolution.py`

### Untracked source-code WIP (requires decision)

| Path | Nature | Status | Risk |
|---|---|---|---|
| `tests/test_behavioral_equivalence.py` | New differential battery (T-BE-01..09) | UNTRACKED-WIP, additive, collects | Lost work if not committed; not in CI |
| `tests/utils/behavioral_equivalence.py` | Engine for above (evidence.json, VALIDATION_REPORT.md) | UNTRACKED-WIP | Same |
| `tests/test_validate_startup.py` | Stage-11 validate startup regression tests | UNTRACKED-WIP | Same |
| `modernize_v2/analysis/resolver.py` | T-2B-05 reference resolution | UNTRACKED-WIP | Blocking 2 v2 tests |
| `tests/v2/test_parser_r5_clause_fidelity.py` | V2 parser R.5 tests | UNTRACKED — **currently ERRORS locally** (imports `RenamesClause`/`SignClause` not in committed parser) | Breaks local `pytest tests/v2/` (2 collection errors) |
| `tests/v2/test_t2b05_reference_resolution.py` | V2 resolver tests | UNTRACKED — **currently ERRORS locally** (imports `AmbiguousReferenceError` not exported) | Same |
| `test_callchain.py` (root) | Ad-hoc debug script, no test functions, executes docker at import | UNTRACKED scratch | Side-effectful; move to scratch/ or delete |
| `docs/PARSER_IR_FORENSIC_AUDIT.md`, `opencode.json`, `sql_failed_log.txt`, `sql_job_log.txt`, `reports/e2e-neg-goldenpay/`, `reports/fresh-e2e-transformable/`, `tests/e2e/screenshots/`, `artifacts/parity-failures/*` | Docs/logs/outputs | Artifacts | Exclude from commits (add .gitignore entries) |
