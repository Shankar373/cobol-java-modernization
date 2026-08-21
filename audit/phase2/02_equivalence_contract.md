# Phase 2: Repository-Agnostic Comparison Contract

This document details the contract-driven design for behavior comparison:

## 1. The Observables Model
Behavioral equivalence will match multiple target observables:
- **Stdout & Stderr**: Live console prints.
- **Exit Status**: Process return code parity (`run_rc == execute.rc`).
- **File Assets**: Output files generated in target directories.
- **Record Counts**: Records inside output tables.
- **Database Parity**: Record states inside SQLite tables.

## 2. Contract Schema Definition
The contract is defined via a configuration file `equivalence_contract.json`:
```json
{
  "observables": {
    "stdout": { "compare": true, "ignore_patterns": ["^TIMESTAMP:.*$"] },
    "exit_code": { "compare": true, "strict": true },
    "files": {
      "compare": true,
      "expect_empty": false,
      "list": ["data/out/audit.csv"],
      "nondeterministic_fields": {
        "data/out/audit.csv": { "field_index": 2, "pattern": "\d{8}" }
      }
    }
  }
}
```

## 3. Auditable Normalizations
Normalizations are never silent. All regex ignores or substitutions applied to files are explicitly recorded in the scenario verification metadata.
