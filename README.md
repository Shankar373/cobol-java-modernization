# COBOL-to-Java Modernization Pipeline & Audit Portal

Repository-agnostic, automated COBOL to Java modernization pipeline and validation suite, including a standalone audit verification engine, an interactive portal dashboard, and a native Java Enterprise refactoring layer (Spring Boot + Spring Batch + REST APIs).

---

## Production Architecture & Stages

The pipeline (`cobol_migrate.py`) automates the full modernization lifecycle through **11 distinct execution stages**:

1. **Ingest**: Fingerprint source repositories, calculating a SHA-256 baseline for source immutability verification.
2. **Discover**: Walk directories to discover arbitrary COBOL programs (`.cob`/`.cbl`) and copybooks (`.cpy`). Build call graphs and physical-logical file assignment maps.
3. **Transpile**: Invoke opensource COBOL 4J (`cobj`) inside Docker to convert COBOL to Java classes.
4. **Collect**: Gather generated Java sources and class files, performing stub detection checks.
5. **Preserve**: Vendor runtime jar dependencies (`libcobj.jar`).
6. **Generate**: Assemble the complete target project, complete with a provenance manifest.
7. **Baseline**: Run the original legacy COBOL code under GnuCOBOL to capture golden execution fixtures.
8. **Execute**: Run the transpiled Java batch programs.
9. **Compare**: Perform physical, logical (SQLite table parsing for indexed files), and semantic comparisons between legacy GnuCOBOL and transpiled Java outputs.
10. **Report**: Emit a comprehensive markdown audit report.
11. **Refactor**: Scaffold a decoupled native Spring Boot enterprise application from copybook definitions, incorporating a JPA database layer, Spring Batch chunk loader, REST APIs, and verify compilation using Maven.

---

## Toolchain & Requirements

- **Python 3.8+** (Standard Library only)
- **Docker** (Required on the host for transpilation and container execution)
- **Maven** (Optional on host, used for compilation verification checks)

---

## Quick Start Guide

### 1. Run the Portal Dashboard (Interactive UI)
Exposes an interactive dashboard to select repositories, execute pipelines, inspect files, and explore modernized Java code:
```bash
python ui.py
```
Open `http://localhost:8787` in your browser.

### 2. Run the Pipeline from the CLI
Run the entire 11-stage automated modernization pipeline against the local repository:
```bash
python cobol_migrate.py --repo legacy --out target --restart-from 0
```

### 3. Run the Standalone Audit Engine
Validate all 7 synthetic verification shape repositories (`A-PAYONLY` through `G-PAYMISSCP`) to prove correctness:
```bash
python audit_engine.py --run-synthetic
```

---

## Dockerizing & Running the Modernized App

The modernized Spring Boot batch application (generated inside `target/modernized/`) runs in a JRE container and mounts legacy files for processing:

### 1. Build the Docker Image
```bash
docker build -t modernized-app target/modernized/
```

### 2. Run the Container
Mount the legacy directory (where the `.dat` transaction files are located) and map port `8080`:
```bash
docker run -d -p 8080:8080 -v c:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test\legacy:/legacy --name modernized-container modernized-app
```

### 3. Query the REST Endpoints
Once the batch job completes (`Job: [FlowJob: [name=processClaimsJob]] completed ... status: [COMPLETED]`), query the H2 database results:
- **Query Processed Claims**:
  ```bash
  curl http://localhost:8080/api/process/claims
  ```
- **Query Processing Exceptions**:
  ```bash
  curl http://localhost:8080/api/process/exceptions
  ```
