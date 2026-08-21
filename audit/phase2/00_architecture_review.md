# Phase 2: Architecture Review

## 1. Architectural Review Mappings
Here is the structural review of the pipeline flow for SystemaOps:

```mermaid
graph TD
    Ingest[Ingest: SHA-256 fingerprinting] --> Discover[Discover: Entry point & copybook search]
    Discover --> Analyze[Analyze: Static call graph parsing]
    Analyze --> Baseline[Baseline: GnuCOBOL Docker golden execution]
    Baseline --> Transpile[Transpile: cobj Docker Java translation]
    Transpile --> Collect[Collect: Java file search & check stubs]
    Collect --> Generate[Generate: Assembly Maven layout]
    Generate --> Execute[Execute: Compile and run target Java]
    Execute --> Compare[Compare: Parity outputs check]
    Compare --> Refactor[Refactor: Placeholder]
    Refactor --> Validate[Validate: Placeholder]
    Validate --> Report[Report: Write pipeline report]
    Report --> Package[Package: Zip modernized artifacts]
```

## 2. Component Analysis
- **Ingestion & Discovery**: Ingestion calculates file hashes. Discovery scans file extensions (`.cob`/`.cbl`) to construct local repositories.
- **Static Analysis & Dependency Graph**: Scans files for static `CALL` statements to draw call-graphs. Unresolved dynamic paths are labeled.
- **Scenario Discovery**: Prioritizes test scripts containing heredoc markers to build transaction scenarios.
- **Execution & Equivalence**: Emulates running COBOL and Java using standard docker command line wrappers. Parity compares directory changes.
