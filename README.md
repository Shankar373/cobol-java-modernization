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

---

## Interactive Legacy Application Execution

The pipeline automatically detects COBOL entry points that contain user-facing
`ACCEPT` statements and executes them deterministically using discovered test
scenarios or input fixtures.

### How it works

1. **Detection** — The pipeline analyses every COBOL source reachable from the
   configured entry point and classifies the application:
   - `NON_INTERACTIVE` — no stdin-consuming `ACCEPT` found; existing batch path is used unchanged.
   - `INTERACTIVE` — one or more bare `ACCEPT` (without `FROM DATE/TIME/DAY-OF-WEEK`) found; scenario discovery runs.
   - `UNKNOWN` — dynamic `CALL` targets prevent full analysis; treated as interactive.

   > `ACCEPT WS-DATE FROM DATE` and `ACCEPT WS-T FROM TIME` are **not** treated
   > as interactive — they read the system clock, not stdin.

2. **Scenario discovery** (in priority order):
   1. Shell smoke/test scripts (`test/*.sh`, `test/*.bash`) — heredoc, echo pipe, printf pipe
   2. Stdin fixture files (`test/*.stdin`, `data/in/*.stdin`, etc.)
   3. Explicit path in `migration_config.json` under `execution.interactive_scenario`
   4. Code blocks in `README.md`
   5. **Fail fast** — `INTERACTIVE_INPUT_REQUIRED` — if no safe scenario exists

   Static analysis is used only for diagnostics (identifying which `ACCEPT` statements
   were found). It **never automatically generates business transactions**.

3. **Deterministic execution** — The discovered scenario is persisted in `state.json`
   with a content-hash `scenario_id`. The exact same scenario (not a re-discovered one)
   is used for both the GnuCOBOL baseline and the Java execution, guaranteeing a
   meaningful equivalence comparison.

4. **Watchdog protection** — Every execution is guarded by:
   - Configurable timeout (`execution.timeout_seconds`, default **120 s**)
   - Configurable output-size cap (`execution.max_output_bytes`, default **5 MB**)
   - Full process-tree cleanup on violation
   - Clear error codes: `BASELINE_EXECUTION_TIMEOUT`, `JAVA_EXECUTION_TIMEOUT`,
     `EXECUTION_OUTPUT_LIMIT_EXCEEDED`

5. **Audit artifacts** — Written to `target/execution/<scenario_id>/`:
   - `scenario.json` — what was discovered and used
   - `interactive_input.txt` — exact bytes sent to the program
   - `stdout_baseline.txt` / `stdout_execute.txt`
   - `execution_metadata_baseline.json` / `execution_metadata_execute.json`

### Configuration

Add an `execution` block to `migration_config.json` to override defaults or pin a scenario:

```json
{
  "execution": {
    "timeout_seconds": 120,
    "max_output_bytes": 5242880,
    "interactive_scenario": "test/run_smoke_test.sh"
  }
}
```

### BankCore regression example

> **Note**: BankCore (`BANKMAIN.cob`) is used below purely as a *regression example*
> of a real interactive program. The pipeline has **zero BankCore-specific code**.
> It works because the existing `test/run_smoke_test.sh` in the BankCore repository
> contains a heredoc with the correct menu selections — the generic discovery system
> finds and uses it automatically.

```text
== Stage 3: baseline ==
  interactivity: INTERACTIVE
  scenario discovered: test/run_smoke_test.sh (4 stdin lines, id=a3f2...)
  [GnuCOBOL baseline terminates normally — no infinite loop]

== Stage 7: execute ==
  reusing scenario id=a3f2... (source: test/run_smoke_test.sh)
  [Java execution uses identical input — comparison is valid]
```

### Fail-fast example

When no scenario exists:
```text
INTERACTIVE_INPUT_REQUIRED

The selected COBOL entry point 'MYMENU' requires stdin input,
but no deterministic test scenario was discovered.

Provide:
  - An existing test/smoke script (test/*.sh) with a heredoc or pipe
  - A stdin fixture file (test/*.stdin)
  - An explicit scenario path in migration_config.json:
      {"execution": {"interactive_scenario": "test/my_script.sh"}}
```
