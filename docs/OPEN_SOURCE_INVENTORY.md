# Open-Source Software (OSS) Inventory & License Audit

**Audit Date:** 2026-09-01T20:55:00Z  
**Platform Target:** COBOL-to-Java Modernization Platform  
**Compliance Standard:** Open-Source License & Provenance Verification  

---

## 1. Inventory of Platform Dependencies

| Component | Version | License | Source / Repository | Scope | Provenance / Redistribution Obligations |
|---|---|---|---|---|---|
| **Python** | `3.14.x` / `3.11+` | Python Software Foundation License (PSFL) | `python.org` | Core CLI / Pipeline | Permissive; include copyright notice in binary redistribution. |
| **OpenJDK** | `17+` / `25-LTS` | GPL v2 with Classpath Exception (GPLv2+CE) | Eclipse Adoptium / Temurin | Build & Runtime | Standard JVM runtime; Classpath exception allows proprietary linking. |
| **Apache Maven** | `3.9.x` | Apache License 2.0 | `apache.org` | Build Tool | Permissive; include Apache NOTICE in distributed artifacts. |
| **GnuCOBOL** | `3.2` | GPL v3 (compiler) / LGPL v3 (runtime `libcob`) | `gnu.org/software/gnucobol` | Baseline Container | GPLv3 for compiler; LGPLv3 allows dynamic linking with runtime. |
| **OCESQL** | `2.0.x` | BSD 2-Clause License | OpenCobol / Tokyo System House | SQL Precompiler | Permissive; include BSD disclaimer in redistribution. |
| **PostgreSQL** | `16-alpine` | PostgreSQL License (MIT/BSD-like) | `postgresql.org` | Database Container | Permissive; retain copyright in source distributions. |
| **PostgreSQL JDBC Driver** | `42.7.x` | BSD 2-Clause License | Maven Central (`org.postgresql:postgresql`) | Runtime JDBC | Permissive; include BSD notice. |
| **Spring Boot** | `3.2.x` | Apache License 2.0 | Maven Central (`org.springframework.boot`) | Enterprise Generator | Permissive; include Apache 2.0 license headers. |
| **Spring Batch** | `5.1.x` | Apache License 2.0 | Maven Central (`org.springframework.batch`) | Batch Generator | Permissive; standard Spring framework license. |
| **H2 Database Engine** | `2.2.x` | MPL 2.0 / EPL 1.0 (Dual) | Maven Central (`com.h2database:h2`) | Test Mock Runtime | Permissive; source available on request for modifications. |
| **ProLeap COBOL Parser** | `4.0.0` | MIT License | `github.com/proleap/proleap-cobol-parser` | Optional AST Parser | Permissive; standard MIT attribution. |
| **ANTLR4 Runtime** | `4.13.x` | BSD 3-Clause License | Maven Central (`org.antlr:antlr4-runtime`) | Lexer / Parser Tool | Permissive; include BSD attribution. |
| **Pytest** | `8.x` / `9.x` | MIT License | PyPI (`pytest`) | Test Harness | Development / test only; no redistribution impact. |
| **Requests** | `2.31+` | Apache License 2.0 | PyPI (`requests`) | Test / UI Driver | Permissive; standard Apache license. |

---

## 2. License Compatibility & Compliance Findings

1. **No GPL Contamination in Generated Java Code**:
   - The generated Java code relies exclusively on Apache 2.0, MIT, and BSD licensed libraries (`modernize/java_helpers` and Spring Boot).
   - GnuCOBOL is utilized strictly within an isolated Docker baseline container as an external verification oracle.
2. **Third-Party Redistribution**:
   - All third-party Java runtime dependencies are standard open-source artifacts fetched directly from Maven Central.
   - All third-party Python dependencies are fetched from PyPI.
