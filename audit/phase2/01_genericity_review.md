# Phase 2: Genericity & Benchmark-Specific Coupling Review

We audited the codebase to locate hardcoded repository dependencies:

## 1. Identified Coupling Gaps:
- **Hardcoded Claims Executable**: In `cobol_migrate.py` (Line 2860 & 2929), the binary output file is hardcoded to `bin/claims_core.exe` regardless of whether the input project is Accounting, BankCore, or another unseen repository.
- **Interactive Parsing Limitations**: `scenario_parser.py` extracts heredoc streams from shell scripts, but makes strong assumptions about test directory structures (`test/`, `tests/`) rather than scanning all directory leaves.
- **Hardcoded Subprocess Commands**: Launching Java execution in `cobol_migrate.py` (Line 3013) uses `java -cp /target/generated:/target/libcobj.jar {entry}` which couples executions to `libcobj.jar` emulation structures.

## 2. Generic Upgrades Design:
- **Dynamically Derived Binary Naming**: The GnuCOBOL binary name must be derived from the discovered entrypoint program name (e.g. `bin/{entry}.exe`).
- **Flexible Scenario Scanner**: Recursive scan directories to resolve any valid input scripts matching test keywords.
