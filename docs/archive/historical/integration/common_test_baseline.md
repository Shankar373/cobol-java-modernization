> [!NOTE]
> **HISTORICAL ARCHIVE — NOT CURRENT SOURCE OF TRUTH**  
> This document is preserved for historical provenance and audit trail purposes only. Refer to [`DOCUMENTATION_INDEX.md`](../../../DOCUMENTATION_INDEX.md) for the authoritative active documentation set.

---

# Common Test Baseline (Phase 2)

**Integration Target:** `c:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test` (Original)  
**Reference Successor:** `C:\Users\bandi\Desktop\ai-workspace\cobol-java-platform`  
**Timestamp:** 2026-09-01T20:37:00Z  

## Common Test Execution & Evidence Comparison

| Capability Area | Original Test Result | Successor Test Result | Common Test Suite | Infrastructure Used | Evidence Difference |
|---|---|---|---|---|---|
| **COBOL Lexing & Parsing** | 22/22 PASSED | 15/15 PASSED | `tests/unit/lexer/`, `tests/unit/parser/` | Python AST & Lexer token stream | Original tests broader COBOL-85 dialect & inline EXEC statements. |
| **Control & Data Flow** | 19/19 PASSED | 12/12 PASSED | `tests/unit/test_control_flow.py`, `test_data_flow.py` | AST Graph Analyzer | Both verify CFG/DFG extraction and dead code analysis. |
| **Numeric Arithmetic (COMP-3)** | 23/23 PASSED | 18/18 PASSED | `tests/parity/test_milestone_b_arithmetic_parity.py` | Java `CobolNumeric` & GnuCOBOL | Byte-level mathematical equivalence verified on both. |
| **REDEFINES & OCCURS** | 2/2 PASSED (5 local Docker skip) | 2/2 PASSED | `tests/e2e/differential/storage/test_redefines01.py` | GnuCOBOL binary + JDK 17 Java | Both execute differential byte overlay checks. |
| **SQL / DB2 Operations** | 39/39 PASSED | 6/6 PASSED | `tests/component/sql/`, `tests/e2e/test_db2_enterprise_e2e.py` | PostgreSQL 16 Alpine container | Original tests full cursor lifecycle, null indicators, joins, and aggregates. |
| **VSAM & File I/O** | 17/17 PASSED | 8/8 PASSED | `tests/component/vsam/`, `test_filestat01.py` | Java File I/O + IDCAMS emulator | Original includes IEBGENER, SORT, and KSDS alternate keys. |
| **JCL Batch Processing** | 23/23 PASSED | 6/6 PASSED | `tests/component/jcl/`, `test_jcl_comprehensive.py` | Spring Batch runtime emulator | Original validates symbol substitution, COND evaluation, and Step generation. |
| **CICS & BMS Maps** | 28/28 PASSED | 8/8 PASSED | `tests/component/cics/`, `test_bms_parser.py` | Spring MVC DTO mapper | Original maps BMS attributes to Java model and REST controller endpoints. |
| **Differential Verifier (Mentor)** | N/A (unintegrated) | 6/6 VERIFIED | `tools/cobol_java_differential_verifier.py` | 4-step execution harness | Successor provides unified CLI verifier across 6 benchmark workloads. |
| **Negative & Mutation Gates** | 9/9 PASSED | 35/35 PASSED | `tests/differential/test_negative_gates.py`, `test_mutation.py` | Dynamic mutation harness | Successor guarantees 0% false VERIFIED and 100% mutation catch rate. |
| **Skills Architecture** | N/A (unintegrated) | 7/7 PASSED | `tests/test_skills_architecture.py` | YAML frontmatter & markdown validator | Successor provides complete AI agent cheatsheets and routing. |
| **Security Controls** | 15/15 PASSED | 8/8 PASSED | `tests/test_security_hardening.py` | Path traversal & HMAC validator | Original provides hardened fail-closed non-loopback authentication. |

---

## Baseline Summary

- **Original Platform Total Passing Tests:** 642 / 648 (6 skipped due to local Docker/ProLeap preconditions).
- **Successor Platform Total Passing Tests:** 158 / 158 (focused modular tests).
- **Core Principle:** Original verified functionality has broader enterprise dialect coverage. Successor brings superior certification, differential verifier, negative mutation gates, and skill workflows.
