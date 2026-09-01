# Repository Structure Cleanup Baseline

**Canonical Repository:** `c:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test`  
**Base Branch:** `integration/successor-verified-improvements`  
**Cleanup Branch:** `feature/repository-structure-hardening`  
**Base Commit SHA:** `13e90e42dbff1440ee3d1d643ad8d801d71eef24`  
**Git Working Tree State:** Clean  
**Date:** September 2, 2026  

---

## 1. Environment & Tooling Baseline

- **Python Version:** 3.14.3
- **Java Compiler / Runtime:** OpenJDK / Temurin 25.0.3.9-hotspot (Java 25)
- **Maven Version:** Apache Maven 3.9.16
- **Docker Version:** Docker Engine 29.6.2 (build dfc4efb)
- **Pytest Version:** 9.1.1
- **Total Collected Tests:** 726 automated test cases

---

## 2. Core Gate & Certification Baseline

- **Platform Certification Verdict:** `VERIFIED_FOR_DEFINED_SCOPE`
- **Mentor Validation Status:** `VERIFIED_FOR_TESTED_SCOPE`
- **Gate 1 (Transpiled Parity):** `PASS` (100% exact differential match)
- **Gate 2 (Modernized Spring Boot Parity):** `PASS` (100% record/database match)
- **Mutation Testing:** 6/6 injected AST mutants caught fail-closed
- **Packaging:** Deterministic ZIP bundle generation verified

---

## 3. Workload Fixture Status

| Workload | Gate 1 | Gate 2 | Mutation Sensitivity | Final Verdict |
|---|---|---|---|---|
| **GOLDENPAY** | **PASS** | **PASS** | 6/6 caught | `MVP_CERTIFIED` |
| **INVENTORY01** | **PASS** | **PASS** | 6/6 caught | `MVP_CERTIFIED` |
| **BANKTXN01** | **PASS** | **PASS** | 6/6 caught | `MVP_CERTIFIED` |
| **ACCTPROG** | **PASS** | **PASS** | 6/6 caught | `MVP_CERTIFIED` |
| **MULTIFILE01** | **PASS** | **PASS** | 6/6 caught | `MVP_CERTIFIED` |
| **DB2SELECT01** | **PASS** | **PASS** | Row mutants caught | `MVP_CERTIFIED` |
| **JCLBATCH01** | **PASS** | **PASS** | Step mutants caught | `MVP_CERTIFIED` |
| **CICSREST01** | **PASS** | **PASS** | REST mutants caught | `MVP_CERTIFIED` |
| **UNSEEN01** | **PASS** | **PASS** | 6/6 caught | `MVP_CERTIFIED` |
| **UNSEEN02** | **PASS** | **PASS** | 6/6 caught | `MVP_CERTIFIED` |
| **UNSEEN03** | **PASS** | **PASS** | 6/6 caught | `MVP_CERTIFIED` |

---

## 4. Safety Invariants for Cleanup

1. No moving of files without prior dependency mapping.
2. No modification of parser, generator, or verification semantics.
3. No deletion of unknown files or historical evidence.
4. Continuous verification with automated test suites after each incremental structural adjustment.
