# Open-Source Mainframe Reference Stack Baseline

**Repository:** `c:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test`  
**Base Commit SHA:** `243a340a35d9540c5d03e5c11b3629151c427671`  
**Branch:** `feature/open-source-mainframe-reference-stack`  
**Standard:** Ponytail Global AI Software Engineering Constitution  
**Date:** September 2, 2026  

---

## 1. Baseline Environment & State

- **Branch:** `feature/open-source-mainframe-reference-stack`
- **Commit SHA:** `243a340a35d9540c5d03e5c11b3629151c427671`
- **Working Tree:** Clean (`nothing to commit, working tree clean`)
- **Python Version:** 3.14.3
- **Java SDK:** Eclipse Temurin 25.0.3.9
- **Apache Maven:** 3.9.16
- **Docker Engine:** 29.6.2
- **Pytest:** 9.1.1
- **Total Automated Test Count:** 726 automated test cases (+25 reference tests)

---

## 2. Platform Certification Status Invariant

```
PLATFORM_CERTIFICATION_VERDICT = VERIFIED_FOR_DEFINED_SCOPE
MENTOR_VALIDATION_STATUS = VERIFIED_FOR_TESTED_SCOPE
```

---

## 3. Reference Architecture Principles

1. **Production Pipeline Preservation:**
   The production Java generation pipeline ($\text{COBOL} \rightarrow \text{Semantic IR} \rightarrow \text{Native Java} \rightarrow \text{Spring Boot / Spring Batch}$) remains strictly unmodified and decoupled from external mainframe emulators.
2. **External Tools as Reference Oracles Only:**
   External open-source mainframe technologies (z390, Hercules, ICU4J, GnuCOBOL) are introduced strictly as **Reference Execution Environments**, **Differential Oracles**, and **Compatibility Targets**.
3. **No False-Pass or Unverified Claims:**
   - CICS simulation $\neq$ IBM CICS TS.
   - Logical VSAM emulation $\neq$ Physical VSAM.
   - Local relational DB validation $\neq$ Real DB2 z/OS certification.
   - Charset translation $\neq$ Native mainframe EBCDIC semantic equivalence.
4. **Isolated Adapter Pattern:**
   All external reference runners reside under `tools/reference_runtimes/` with fail-closed timeout and error boundaries.
