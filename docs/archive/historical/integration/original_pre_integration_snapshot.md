> [!NOTE]
> **HISTORICAL ARCHIVE — NOT CURRENT SOURCE OF TRUTH**  
> This document is preserved for historical provenance and audit trail purposes only. Refer to [`DOCUMENTATION_INDEX.md`](../../../DOCUMENTATION_INDEX.md) for the authoritative active documentation set.

---

# Original Repository Pre-Integration Snapshot (Phase 0)

**Repository:** `C:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test`  
**GitHub Origin:** `https://github.com/Shankar373/cobol-java-modernization.git`  
**Integration Branch:** `integration/successor-verified-improvements`  
**Baseline Commit SHA:** `b351d6649fa064af104724d8683dd6dc0ab54e05`  
**Commit Message:** `audit: baseline original repository before successor comparison`  
**Timestamp:** `2026-09-01T20:47:00+05:30`  

---

## 1. System Environment Details

| Component | Version / Build | Path / Vendor |
|---|---|---|
| **Operating System** | Windows 11 (10.0, amd64) | Microsoft Windows |
| **Python** | 3.14.3 | CPython |
| **Java (JDK)** | OpenJDK 25.0.3+9-LTS | Eclipse Adoptium (Temurin-25.0.3+9) |
| **Maven** | Apache Maven 3.9.16 | `C:\Program Files\Apache\Maven\apache-maven-3.9.16` |
| **Docker** | 29.6.2 (build dfc4efb) | Docker Desktop / Daemon |

---

## 2. Working Tree State at Freeze

- Working tree is clean on baseline commit `b351d6649fa064af104724d8683dd6dc0ab54e05`.
- Active branch is `integration/successor-verified-improvements`.
- Baseline test suite passes 642 / 648 tests with 0 unexpected test failures.
- No production source files modified during this freeze step.

---

## 3. Original Core Capabilities to Preserve

1. **COBOL Lexer & Parser (`modernize/lexer.py`, `modernize/parser.py`)**: Full fixed/free format COBOL-85 parser supporting inline EXEC SQL, EXEC CICS, COPY REPLACING, and PICTURE clauses.
2. **Semantic IR & Analyzers (`modernize/semantic_ir.py`, `control_flow.py`, `data_flow.py`, `dependencies.py`)**: Paragraph CFGs, dead code detection, call tree mapping.
3. **Native Code Generator (`modernize/native_generator.py`)**: Generates standalone high-performance Java classes with byte-exact precision via `CobolNumeric`, `CobolDecimal`, `CobolRef`.
4. **Enterprise Generator (`modernize/enterprise_generator.py`)**: Transpiles to Spring Boot 3.x REST controllers, Spring Data JDBC repositories, and Spring Batch jobs.
5. **SQL / DB2 Engine (`modernize/native_generator.py`, PostgreSQL backend)**: Multi-table joins, cursors, indicator variables, SQLCODE/SQLSTATE emulation.
6. **VSAM / File I/O Engine (`modernize/java_helpers/`, `KsdSDbService.java`, `VsamIndexedStore.java`)**: KSDS, RRDS, ESDS, IDCAMS, IEBGENER, SORT utilities.
7. **JCL Engine (`modernize/jcl_parser.py`, `modernize/jcl_generator.py`)**: Batch orchestration, symbol substitution, return code conditions (`COND=(0,NE)`), Spring Batch conversion.
8. **CICS Engine (`modernize/bms_parser.py`, `CicsTransactionContext.java`)**: BMS map parsing, LINK/XCTL dispatching, COMMAREA state tracking.
