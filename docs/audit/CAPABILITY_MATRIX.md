# Master Capability & Multi-Oracle Reference Matrix

**Repository:** `c:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test`  
**Branch:** `feature/open-source-mainframe-reference-stack`  
**Certification Standard:** Ponytail Global AI Software Engineering Constitution  
**Platform Verdict:** `VERIFIED_FOR_DEFINED_SCOPE`  
**Mentor Validation Status:** `VERIFIED_FOR_TESTED_SCOPE`  

---

| Capability Area | COBOL Construct | Reference Runtime | Reference Proven? | Native Java Proven? | Production Equivalent? | Simulation? | Unproven? | Required Environment | Status | Risk |
|---|---|---|---|---|---|---|---|---|---|---|
| **Alphanumeric Data** | `PIC X(N)` | GnuCOBOL / z390 | YES | YES | YES | NO | NO | Standard Java / JVM | **PROVEN** | Low |
| **Integer Numeric** | `PIC 9(N) DISPLAY` | GnuCOBOL / z390 | YES | YES | YES | NO | NO | Standard Java / JVM | **PROVEN** | Low |
| **Implied Decimals** | `PIC 9(N)V99` | GnuCOBOL / z390 | YES | YES | YES | NO | NO | Standard Java / JVM | **PROVEN** | Low |
| **Signed Numeric** | `PIC S9(N)` | GnuCOBOL / z390 | YES | YES | YES | NO | NO | Standard Java / JVM | **PROVEN** | Low |
| **Packed Decimal** | `COMP-3 / USAGE COMPUTATIONAL-3` | GnuCOBOL / z390 | YES | YES | YES | NO | NO | Standard Java / JVM | **PROVEN** | Low |
| **Binary Computational** | `COMP / COMP-4 / COMP-5` | GnuCOBOL / z390 | YES | YES | YES | NO | NO | Standard Java / JVM | **PROVEN** | Low |
| **Condition Names** | `Level-88` | GnuCOBOL / z390 | YES | YES | YES | NO | NO | Standard Java / JVM | **PROVEN** | Low |
| **Shared Storage** | `REDEFINES` | GnuCOBOL / z390 | YES | YES | YES | NO | NO | Standard Java / JVM | **PROVEN** | Medium |
| **Static Occurs** | `OCCURS N TIMES` | GnuCOBOL / z390 | YES | YES | YES | NO | NO | Standard Java / JVM | **PROVEN** | Low |
| **Dynamic Occurs** | `OCCURS DEPENDING ON` | GnuCOBOL / z390 | YES | YES | YES | NO | NO | Standard Java / JVM | **PROVEN_FOR_TESTED_SCOPE** | Low |
| **Simple Move** | `MOVE A TO B` | GnuCOBOL / z390 | YES | YES | YES | NO | NO | Standard Java / JVM | **PROVEN** | Low |
| **Group Move** | `MOVE GROUP-A TO GROUP-B` | GnuCOBOL / z390 | YES | YES | YES | NO | NO | Standard Java / JVM | **PROVEN** | Low |
| **Arithmetic Statements**| `ADD / SUBTRACT / MULTIPLY / DIVIDE`| GnuCOBOL / z390 | YES | YES | YES | NO | NO | Standard Java / JVM | **PROVEN** | Low |
| **Chained Compute** | `COMPUTE` | GnuCOBOL / z390 | YES | YES | YES | NO | NO | Standard Java / JVM | **PROVEN** | Low |
| **Size Error Handling** | `ON SIZE ERROR` | GnuCOBOL / z390 | YES | YES | YES | NO | NO | Standard Java / JVM | **PROVEN** | Low |
| **Conditional Logic** | `IF / ELSE / EVALUATE` | GnuCOBOL / z390 | YES | YES | YES | NO | NO | Standard Java / JVM | **PROVEN** | Low |
| **Inline Loops** | `PERFORM UNTIL / VARYING` | GnuCOBOL / z390 | YES | YES | YES | NO | NO | Standard Java / JVM | **PROVEN** | Low |
| **Out-of-Line Perform** | `PERFORM PARA-A THRU/THROUGH PARA-B`| GnuCOBOL / z390 | YES | YES | YES | NO | NO | Standard Java / JVM | **PROVEN_FOR_TESTED_SCOPE** | Low |
| **Unconditional Branch**| `GO TO` | GnuCOBOL / z390 | YES | YES | YES | NO | NO | Standard Java / JVM | **PROVEN_FOR_TESTED_SCOPE** | Low |
| **Subprogram Linkage** | `CALL ... USING BY REFERENCE` | GnuCOBOL / z390 | YES | YES | YES | NO | NO | Standard Java / JVM | **PROVEN** | Low |
| **Call By Content** | `CALL ... USING BY CONTENT` | GnuCOBOL / z390 | YES | YES | YES | NO | NO | Standard Java / JVM | **PROVEN** | Low |
| **Dynamic Subprogram** | `CALL identifier` | GnuCOBOL / z390 | YES | YES | YES | NO | NO | Standard Java / JVM | **PROVEN_FOR_TESTED_SCOPE** | Low |
| **String Concatenation**| `STRING ... DELIMITED BY` | GnuCOBOL / z390 | YES | YES | YES | NO | NO | Standard Java / JVM | **PROVEN** | Low |
| **String Splitting** | `UNSTRING ... DELIMITED BY` | GnuCOBOL / z390 | YES | YES | YES | NO | NO | Standard Java / JVM | **PROVEN_FOR_TESTED_SCOPE** | Low |
| **String Inspection** | `INSPECT REPLACING / TALLYING` | GnuCOBOL / z390 | YES | YES | YES | NO | NO | Standard Java / JVM | **PROVEN_FOR_TESTED_SCOPE** | Low |
| **Reference Modification**| `VAR (start:length)` | GnuCOBOL / z390 | YES | YES | YES | NO | NO | Standard Java / JVM | **PROVEN** | Low |
| **Line Sequential Files**| `ORGANIZATION LINE SEQUENTIAL` | GnuCOBOL / z390 | YES | YES | YES | NO | NO | Standard Java / JVM | **PROVEN** | Low |
| **Record Sequential Files**| `ORGANIZATION RECORD SEQUENTIAL` | GnuCOBOL / z390 | YES | YES | YES | NO | NO | Standard Java / JVM | **PROVEN_FOR_TESTED_SCOPE** | Low |
| **VSAM KSDS** | `ORGANIZATION INDEXED` | zVSAM (z390) | ONLY EMULATION | ONLY RELATIONAL | NO | YES | NO | Relational DB (PostgreSQL/H2) | **SIMULATED** | Medium |
| **VSAM RRDS** | `ORGANIZATION RELATIVE` | zVSAM (z390) | ONLY EMULATION | ONLY RELATIONAL | NO | YES | NO | Relational DB (PostgreSQL/H2) | **SIMULATED** | Medium |
| **Physical VSAM Specs** | Control intervals, CI/CA splits, buffer pools, dataset locking | Hercules / Real MVS | NO | NO | NO | NO | YES | Physical Mainframe OS | **UNPROVEN** | High |
| **Relational SQL Queries**| `EXEC SQL SELECT/INSERT/UPDATE` | Local/Docker DB2 | YES | YES | YES | NO | NO | PostgreSQL / Docker DB2 | **PROVEN_FOR_TESTED_SCOPE** | Low |
| **SQL Cursors** | `DECLARE / OPEN / FETCH / CLOSE` | Local/Docker DB2 | YES | YES | YES | NO | NO | PostgreSQL / Docker DB2 | **PROVEN_FOR_TESTED_SCOPE** | Low |
| **Live IBM DB2 z/OS** | Physical Mainframe DB2 Subsystem | Real DB2 z/OS | NO | NO | NO | NO | YES | Live z/OS Hardware | **UNPROVEN** | High |
| **CICS REST Modernization**| `EXEC CICS LINK / XCTL / RETURN` | zCICS (z390) | ONLY TESTED SCOPE | YES | NO | YES | NO | Spring Boot REST Controller | **SIMULATED** | Medium |
| **Live IBM CICS TS** | Physical CICS Transaction Server Region | Real CICS TS Region | NO | NO | NO | NO | YES | Live z/OS Hardware | **UNPROVEN** | High |
| **CICS BMS Screen Maps**| `SEND MAP / RECEIVE MAP` | zCICS (z390) | ONLY TESTED SCOPE | PARTIAL | NO | YES | NO | Spring Boot JSON DTO | **SIMULATED** | Medium |
| **JCL Job Control** | `//JOB, //EXEC, //DD` | Hercules / z390 | YES | YES | YES | NO | NO | Spring Batch Job Runner | **PROVEN** | Low |
| **Mainframe Utilities** | `IDCAMS, IEBGENER, SORT` | z390 Utilities | ONLY TESTED SCOPE | PARTIAL | NO | YES | NO | Java Flat-file Helpers | **SIMULATED** | Medium |
| **EBCDIC Charset Conversion**| `CP037, CP1047, CP500, CP273, CP1140`| ICU4J / Pure-Java | YES | YES | YES | NO | NO | `CobolCharsetAdapter` | **PROVEN_FOR_TESTED_SCOPE** | Low |
| **EBCDIC Collation Strategy**| `RuleBasedCollator / Byte-order` | ICU4J / Strategy | YES | YES | YES | NO | NO | `CobolCollationStrategy` | **PROVEN_FOR_TESTED_SCOPE** | Low |
| **Native Mainframe EBCDIC** | Native EBCDIC DASD / Byte storage | Live Mainframe OS | NO | NO | NO | NO | YES | Physical Mainframe OS | **UNPROVEN** | High |
| **Gate 1 Validation** | Transpiled Java Parity | GnuCOBOL | YES | YES | YES | NO | NO | Docker Container | **PROVEN** | Low |
| **Gate 2 Validation** | Modernized Spring Boot Parity | GnuCOBOL | YES | YES | YES | NO | NO | Spring Boot Local Runtime | **PROVEN** | Low |
| **AST Mutation Sensitivity**| Injected Semantic Mutations | Differential Engine | YES | YES | YES | NO | NO | Python Mutation Runner | **PROVEN** | Low |
