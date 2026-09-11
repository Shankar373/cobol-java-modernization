# COBOL-to-Native-Java Modernization Platform

A production-grade, repository-agnostic COBOL to Native Java modernization platform, verification suite, and forensic auditing engine.

```
PLATFORM_CERTIFICATION_VERDICT = VERIFIED_FOR_DEFINED_SCOPE
MENTOR_VALIDATION_STATUS = VERIFIED_FOR_TESTED_SCOPE
```

---

## 1. Documentation Quick Navigation

- 📖 **[Master Documentation Index](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/docs/DOCUMENTATION_INDEX.md)**: Full navigation index across all active specifications and audit registers.
- 🏛️ **[System Architecture](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/docs/ARCHITECTURE.md)**: AST Parser, Semantic IR, and Native Java Generator architecture.
- ⚙️ **[13-Stage Pipeline Specification](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/docs/PIPELINE.md)**: Comprehensive stage-by-stage pipeline workflow.
- 📋 **[Supported COBOL Features](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/docs/SUPPORTED_FEATURES.md)**: Supported COBOL divisions, verbs, data types, and file formats.
- 🔍 **[Capability Matrix](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/docs/audit/CAPABILITY_MATRIX.md)**: Construct-level capability, reference runtime, and status matrix.
- ⚠️ **[Limitations Register](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/docs/audit/LIMITATIONS_REGISTER.md)**: Categorical limitations (Proven, Simulated, Unsupported, Unproven).
- 📜 **[Final Certification Report](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/docs/certification/FINAL_CERTIFICATION_REPORT.md)**: Master platform certification report.
- 🎓 **[Mentor Acceptance Scope](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/docs/certification/MENTOR_ACCEPTANCE_SCOPE.md)**: 11-step mentor validation lifecycle and test repository matrix.
- 🛡️ **[Security Architecture](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/docs/SECURITY.md)**: Workspace sandboxing, input sanitization, and path validation.
- 🧪 **[Testing Strategy](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/docs/TESTING.md)**: Test suite architecture and execution instructions.

---

## 2. Production Architecture

The modernization platform generates clean, cloud-native Spring Boot, Spring Batch, and JPA/JDBC Java applications from legacy COBOL sources without proprietary runtime lock-in.

```
                         COBOL SOURCE
                              │
                              ▼
                       PARSER / SEMANTIC IR
                              │
                              ▼
                     NATIVE JAVA GENERATOR
                              │
                              ▼
                 SPRING BOOT / SPRING BATCH
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
               Native Java        Compatibility Layers
                    │                   │
                    │          ┌────────┼─────────┐
                    │          │        │         │
                    │        VSAM      CICS     EBCDIC
                    │       layer      layer      layer
                    │          │        │         │
                    └──────────┴────────┴─────────┘
                              │
                              ▼
                     DIFFERENTIAL ENGINE
                              ▲
                              │
             ┌────────────────┼────────────────┐
             │                │                │
         GnuCOBOL          z390            Hercules/MVS
         baseline       reference oracle    reference oracle
             │                │                │
             └────────────────┼────────────────┘
                              │
                              ▼
                         CERTIFICATION
```

---

## 3. The 13-Stage Modernization Pipeline

1. **Stage 0 - Ingest**: Upload repository, compute SHA-256 digests, and establish source immutability boundaries.
2. **Stage 1 - Discover**: Parse directory trees to discover COBOL programs, copybooks, and inventory files.
3. **Stage 2 - Analyze**: Extract call graphs, architecture mappings, copybook structures, and SQL queries.
4. **Stage 3 - Baseline**: Execute legacy COBOL under containerized GnuCOBOL to capture golden behavioral baselines.
5. **Stage 4 - Transpile**: Transpile COBOL source to Java classes using opensourcecobol4j toolchain (Gate 1 track).
6. **Stage 5 - Collect**: Gather transpiled Java sources, mapping schemas, and check for missing stubs.
7. **Stage 6 - Generate**: Assemble intermediate transpiled target project.
8. **Stage 7 - Execute**: Run transpiled Java programs against golden inputs to capture outputs and database state.
9. **Stage 8 - Compare**: Perform **Gate 1** differential validation (transpiled Java vs legacy golden baseline).
10. **Stage 9 - Refactor**: Generate clean, native Spring Boot REST controllers, Spring Batch jobs, and JPA schemas.
11. **Stage 10 - Validate**: Perform **Gate 2** validation (build modernized Spring Boot app, execute job, compare outputs vs baseline).
12. **Stage 11 - Report**: Generate cryptographic execution manifests, provenance graphs, and audit scorecards.
13. **Stage 12 - Package**: Build a distributable ZIP package containing modernized Spring Boot code, baselines, and reports.

---

## 4. Quick Start & Execution

### Running the Interactive UI Portal
```bash
python ui.py
```
Open `http://localhost:8787` in your browser.

### Running the Pipeline via CLI
```bash
# Run complete 13-stage modernization pipeline
python cobol_migrate.py --repo tests/repos/GOLDENPAY --out target/goldenpay

# Using the CJP CLI
python -m src.cjp.cli run --repo tests/repos/GOLDENPAY --out target/goldenpay
```

### Running Automated Test Suites
```bash
# Run all 726 automated test cases
python -m pytest

# Run specific core regression suites
python -m pytest tests/reference_runtime/ tests/test_eof_sequential_reader_parity.py tests/test_adversarial_verification.py -v
```

---

## 5. Toolchain Requirements

- **Python 3.10+** (Standard Library + FastAPI / Uvicorn for UI)
- **Java OpenJDK / Temurin 17+** (Java 25 supported)
- **Apache Maven 3.8+** (Used for Spring Boot compilation checks)
- **Docker** (Used for GnuCOBOL baseline execution and isolation)
