# Mentor 4-Step Differential Verifier Architecture

The Canonical Mentor 4-Step Differential Verifier (`tools/cobol_java_differential_verifier.py`) provides an automated, reproducible bridge between mainframe legacy execution and modern Java applications.

---

## 1. The 4 Verification Steps

```mermaid
sequenceDiagram
    participant User as CLI / REST API / CI
    participant Verifier as Differential Verifier
    participant Pipeline as Native Pipeline
    participant GnuCOBOL as GnuCOBOL / DB2 Baseline
    participant JVM as JDK 17+ JVM

    User->>Verifier: run_all(repo, out, workload)
    Verifier->>Pipeline: Step 1: Conversion (COBOL -> Java)
    Pipeline-->>Verifier: Java source files generated
    Verifier->>Pipeline: Step 2: JDK Compilation (javac / Maven)
    Pipeline-->>Verifier: .class files compiled
    Verifier->>GnuCOBOL: Step 3: Mainframe Baseline Execution
    GnuCOBOL-->>Verifier: Baseline stdout, stderr, exit code, files
    Verifier->>JVM: Step 4: Java Runtime Execution
    JVM-->>Verifier: Java stdout, stderr, exit code, files
    Verifier->>Verifier: Compare Channels & Evaluate Tier Scorecard
    Verifier-->>User: Structured Report (MD/JSON) + SHA-256 Manifest
```

---

## 2. CLI Usage

```bash
# Verify a single workload:
python tools/cobol_java_differential_verifier.py --repo tests/repos/SIMPLEBASELINE01 --workload SIMPLEBASELINE01 --json

# Run all canonical benchmark workloads:
python tools/cobol_java_differential_verifier.py --verify-all
```

---

## 3. Output Artifacts

For each workload `<WORKLOAD>`, the verifier writes:
1. `reports/<WORKLOAD>/differential_validation_report.md`: Markdown summary for humans.
2. `reports/<WORKLOAD>/differential_validation_report.json`: Machine-readable JSON summary.
3. `reports/<WORKLOAD>/certification_scorecard.json`: 5-Tier certification scores and evidence.
4. `reports/<WORKLOAD>/CERTIFICATION_REPORT.md`: Printable audit certificate.
