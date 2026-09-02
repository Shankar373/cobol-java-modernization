> [!NOTE]
> **HISTORICAL ARCHIVE — NOT CURRENT SOURCE OF TRUTH**  
> This document is preserved for historical provenance and audit trail purposes only. Refer to [`DOCUMENTATION_INDEX.md`](../../../DOCUMENTATION_INDEX.md) for the authoritative active documentation set.

---

# Open-Source Mainframe Reference Stack Integration Baseline

**Repository:** `c:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test`  
**Base Branch:** `integration/successor-verified-improvements`  
**Integration Branch:** `feature/open-source-mainframe-reference-stack`  
**Base Commit SHA:** `13e90e42dbff1440ee3d1d643ad8d801d71eef24`  
**Working Tree State:** Clean  
**Date:** September 2, 2026  

---

## 1. Baseline Architectural Status

- **Primary Pipeline Architecture:**
  - COBOL Ingestion & Dynamic Discovery
  - Parser & Semantic IR (`modernize/parser.py`, `modernize/semantic_ir.py`)
  - Native Java Generator (`modernize/native_generator.py`)
  - Target Framework: Spring Boot, Spring Batch, JPA/JDBC
  - Gate 1: Transpiled Java differential verification vs GnuCOBOL Docker baseline (`stage_compare`)
  - Gate 2: Modernized Spring Boot live validation vs baseline outputs (`stage_validate`)
- **Primary Baseline Oracle:** GnuCOBOL 2.0 / 3.x (`opensourcecobol4j:2.0.0` / native `cobc`)
- **Platform Certification Verdict:** `VERIFIED_FOR_DEFINED_SCOPE`
- **Mentor Validation Status:** `VERIFIED_FOR_TESTED_SCOPE`

---

## 2. Baseline Test Suite Verification Results

| Suite / Area | Tests Run | Passed | Failed | Status |
|---|---|---|---|---|
| **EOF Sequential Reader Parity** (`tests/test_eof_sequential_reader_parity.py`) | 10 | 10 | 0 | **PASS** (100%) |
| **Adversarial Hardening** (`tests/test_adversarial_verification.py`) | 5 | 5 | 0 | **PASS** (100%) |
| **Unseen Repositories Suite** (`tests/acceptance/test_unseen_repositories.py`, `tests/robustness/unseen/test_unseen_repositories_suite.py`) | 32 | 32 | 0 | **PASS** (100%) |
| **Security & Anti-Bypass Suite** (`tests/test_phase11b_security.py`, `test_no_hardcoding.py`, `test_no_false_production_ready.py`, `test_validation_nobypass.py`) | 13 | 13 | 0 | **PASS** (100%) |
| **String & Decimal Semantics** (`tests/test_cobol_string_semantics.py`, `test_pic_v_string_semantics.py`) | 6 | 6 | 0 | **PASS** (100%) |
| **Manifest & Package Verification** (`tests/test_phase9_manifest.py`) | 9 | 9 | 0 | **PASS** (100%) |
| **Total Test Suite Collection** | 701 | 701 | 0 | **PASS** (100%) |

---

## 3. Baseline Mentor Fixtures Parity

| Workload Fixture | Gate 1 (Transpiled) | Gate 2 (Modernized Spring Boot) | AST Mutation Sensitivity | Verdict |
|---|---|---|---|---|
| **GOLDENPAY** | **PASS** (100% byte match) | **PASS** (100% record match) | 6/6 caught | `MVP_CERTIFIED` |
| **INVENTORY01** | **PASS** (100% byte match) | **PASS** (100% record match) | 6/6 caught | `MVP_CERTIFIED` |
| **BANKTXN01** | **PASS** (100% byte match) | **PASS** (100% record match) | 6/6 caught | `MVP_CERTIFIED` |
| **ACCTPROG** | **PASS** (100% byte match) | **PASS** (100% record match) | 6/6 caught | `MVP_CERTIFIED` |
| **MULTIFILE01** | **PASS** (100% byte match) | **PASS** (100% record match) | 6/6 caught | `MVP_CERTIFIED` |
| **DB2SELECT01** | **PASS** (100% row match) | **PASS** (100% row match) | Row mutations caught | `MVP_CERTIFIED` |
| **JCLBATCH01** | **PASS** (100% step match) | **PASS** (Spring Batch steps match) | Step mutations caught | `MVP_CERTIFIED` |
| **CICSREST01** | **PASS** (HTTP payload match) | **PASS** (Spring MVC REST match) | REST mutations caught | `MVP_CERTIFIED` |
| **UNSEEN01** | **PASS** (82 bytes matched) | **PASS** (82 bytes matched) | 6/6 caught | `MVP_CERTIFIED` |
| **UNSEEN02** | **PASS** (Exact match) | **PASS** (Exact match) | 6/6 caught | `MVP_CERTIFIED` |
| **UNSEEN03** | **PASS** (Exact match) | **PASS** (Exact match) | 6/6 caught | `MVP_CERTIFIED` |

---

## 4. Integration Objectives & Guardrails

1. Keep native Java generator, parser/IR, and Spring Boot modernization architecture canonical.
2. Introduce open-source mainframe technologies (`z390`, `ICU4J`, `Hercules/MVS 3.8j`, `DatabaseReferenceRuntime`) strictly as external reference runtimes / oracles.
3. Establish capability detection (`z390_available`, `hercules_available`, `ebcdic_required`, etc.) so that unavailable optional environments report `UNPROVEN_REFERENCE_ENVIRONMENT` / `SKIPPED` without breaking standard mentor runs.
4. Establish EBCDIC charset and collation abstraction (`CobolCharsetAdapter`, `CobolCollationStrategy`).
5. Ensure zero runtime dependency on mainframe emulators in generated production Java.
