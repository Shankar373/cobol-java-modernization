# Open-Source Mainframe Reference Stack Evaluation

**Repository:** `c:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test`  
**Branch:** `feature/open-source-mainframe-reference-stack`  
**Standard:** Ponytail Global AI Software Engineering Constitution  
**Date:** September 2, 2026  

---

## 1. Executive Summary

To strengthen verification without introducing proprietary mainframe emulators into the generated production Java application, this evaluation assesses candidate open-source mainframe technologies for use as **isolated reference oracles**, **differential verification sources**, and **charset/collation engines**.

The production modernization target remains 100% cloud-native Spring Boot, Spring Batch, and JPA/JDBC. External mainframe technologies operate exclusively within testing and verification harnesses.

---

## 2. Comprehensive Candidate Evaluation

### A. z390 (Portable Mainframe Assembler & Emulator)
* **Project / URL:** [z390development/z390](https://github.com/z390development/z390) / [z390.org](http://www.z390.org)
* **License:** Automated Software Tools Corporation Open Source License / GPLv2 compatible
* **Maintenance:** Active community maintenance on GitHub (z390development)
* **Build / Runtime:** Java-based core (`z390.jar`) with JVM execution across Windows, Linux, and macOS
* **Docker Availability:** Cleanly containerizable on lightweight OpenJDK base images (`eclipse-temurin:17-jre`)
* **Supported Mainframe Features:**
  - System/390 & z/Architecture instruction simulation
  - **zCOBOL:** Compiles COBOL source to HLASM assembler, then to System/390 bytecode for JVM execution
  - **zVSAM:** KSDS, ESDS, and RRDS indexed file emulation
  - **zCICS:** Simulated CICS execution with COMMAREA and basic BMS screen mapping
  - **QSAM / EBCDIC:** Native support for EBCDIC encoding and fixed-block dataset structures
* **Automation & Interface:** Headless CLI commands (`z390.jar`, `as390`, `exec390`, `mac.bat/sh`)
* **Testability:** High — deterministic return codes, standard stdout/stderr logging, isolated temporary work directories
* **Limitations:** Not a full operating system; zCOBOL implements a defined subset of Enterprise COBOL syntax; does not support modern 64-bit Java interoperability
* **Security & Isolation:** Sandboxable within non-root Docker containers or isolated process wrappers with strict directory bounds and execution timeouts
* **Recommendation:** **SELECTED as Primary Lightweight Reference Oracle** for z/Architecture instruction simulation, zCOBOL differential testing, and EBCDIC/zVSAM validation.

---

### B. ICU4J (Unicode Consortium International Components for Unicode)
* **Project / URL:** [Unicode Consortium ICU4J](https://github.com/unicode-org/icu) / [icu.unicode.org](https://icu.unicode.org)
* **License:** Unicode-DFS-2016 / ICU License (Permissive, BSD/MIT-style)
* **Maintenance:** Actively maintained by Unicode Consortium, IBM, Google, and Apple
* **Build / Runtime:** Standard Maven / Gradle library (`com.ibm.icu:icu4j`)
* **Docker Availability:** Fully portable pure-Java dependency
* **Supported Features:**
  - Exact EBCDIC code-page conversion (`CP037`, `CP1047`, `CP500`, `CP273`, `CP280`, etc.)
  - Byte-for-byte round-trip EBCDIC ↔ Unicode transcoding
  - Tailored Rule-Based EBCDIC Collator (`RuleBasedCollator` supporting EBCDIC character ordering where digits `0-9` sort after letters `A-Z`)
* **Testability:** Exceptionally high — pure deterministic unit and property-based testability
* **Limitations:** Charset and collation library only; does not execute COBOL or simulate mainframe I/O
* **Recommendation:** **SELECTED as Canonical EBCDIC Charset & Collation Engine** for `CobolCharsetAdapter` and `CobolCollationStrategy`.

---

### C. Hercules / MVS 3.8j (TK4- / Hyperion)
* **Project / URL:** [SDL Hercules Hyperion](https://github.com/sdl-hercules-390/hyperion) / [MVS TK4-](http://wotho.ethz.ch/tk4-/)
* **License:** QPL (Q Public License)
* **Maintenance:** Maintained by SoftDevLabs and Hercules community
* **Build / Runtime:** C/C++ native executable; pre-built Docker containers available (`rattydave/docker-tk4`)
* **Supported Mainframe Features:**
  - Full hardware emulation of System/370, ESA/390, and z/Architecture hardware
  - Boots public domain OS (MVS 3.8j) with JES2 spooling, real catalog structures, and QSAM/VSAM datasets
  - Executes JCL job cards (`//JOB`, `//EXEC`, `//DD`, condition codes)
* **Automation & Interface:** Automated job submission via TCP socket reader (`port 3505`) and spool extraction via `herclient`
* **Testability:** Medium — requires running an emulated virtual machine and polling JES2 spool output
* **Limitations:** Heavyweight startup time (~15–30s); MVS 3.8j only includes 1970s OS/VS COBOL; modern Enterprise COBOL features require licensed IBM z/OS
* **Security:** Must be isolated in dedicated non-root Docker container with restricted network and ephemeral shadow disk volumes
* **Recommendation:** **SELECTED as Optional Heavyweight Reference Environment** for JCL job streams and physical dataset sequencing. Marked as an optional reference runner (`hercules_available=false` by default in fast CI).

---

### D. GnuCOBOL (Canonical Primary Baseline)
* **Project / URL:** [GnuCOBOL](https://savannah.gnu.org/projects/gnucobol)
* **License:** GPLv3 / LGPLv3
* **Maintenance:** Actively maintained
* **Recommendation:** **RETAINED as Canonical Primary Baseline Oracle** for Gate 1 and Gate 2 validation.

---

### E. PostgreSQL / Docker DB2 / H2 (Relational Database Layer)
* **License:** PostgreSQL License / IBM Community Edition / MPL 2.0
* **Recommendation:** **RETAINED for Local & Containerized Relational Testing** and VSAM relational table emulation. Real IBM DB2 z/OS remains explicitly classified as `UNPROVEN` until executed on live mainframe infrastructure.

---

## 3. Technology Selection Matrix

| Candidate Technology | Role in Architecture | Selection Status | Primary Justification |
|---|---|---|---|
| **z390** | Reference Oracle / Multi-Oracle Diff | **SELECTED** | Lightweight JVM-based execution of zCOBOL, zVSAM, and EBCDIC byte sequences without full OS overhead. |
| **ICU4J** | EBCDIC Encoding & Collation | **SELECTED** | Enterprise-grade, permissive license, exact code-page conversion (CP037, CP1047) and EBCDIC collation support. |
| **Hercules / MVS 3.8j** | JCL / Dataset Reference Oracle | **OPTIONAL REFERENCE** | Full hardware/OS emulation for JES2 JCL streams; disabled in fast CI, available for deep reference testing. |
| **GnuCOBOL** | Primary Baseline Oracle | **RETAINED** | Fast, deterministic, industry-standard ANSI/ISO COBOL compilation and execution. |
| **PostgreSQL / Docker DB2** | Relational Database Testing | **RETAINED** | Verified SQL translation and relational persistence. |

---

## 4. Architectural Separation of Concerns

```
                      COBOL SOURCE
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
     GnuCOBOL Baseline            z390 Reference
        (Canonical)                 (Secondary)
             │                           │
             └─────────────┬─────────────┘
                           ▼
                 MODERNIZATION PLATFORM
                           │
                           ▼
                  PARSER & SEMANTIC IR
                           │
                           ▼
                 NATIVE JAVA GENERATOR
                           │
                           ▼
              SPRING BOOT / SPRING BATCH
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
        Native Java            Compatibility Layers
             │                 (VSAM, CICS, EBCDIC)
             │                           │
             └─────────────┬─────────────┘
                           ▼
                  DIFFERENTIAL ENGINE
            (Gate 1, Gate 2, Multi-Oracle)
                           │
                           ▼
                     CERTIFICATION
```
