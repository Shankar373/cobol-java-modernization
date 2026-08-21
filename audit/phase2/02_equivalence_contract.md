# Phase 2: Repository-Agnostic Comparison Contract & Observables Model

This document defines the generic model for behavior validation:

## 1. ExecutionObservation Model
The validator constructs an `ExecutionObservation` container for both legacy and modernized runs:

```json
{
  "scenario_id": "SC-1002",
  "execution_status": "normal",
  "exit_code": 0,
  "stdout": "Processing complete.",
  "stderr": "",
  "files": ["data/out/records.csv"],
  "file_contents": {
    "data/out/records.csv": "10001,ACTIVE,95000.00"
  },
  "record_counts": {
    "data/out/records.csv": 1
  },
  "database_state": {},
  "structured_outputs": {}
}
```

## 2. Validator State Machine
The equivalence engine resolves validation into one of six distinct states:
- **Expected no output / Actual no output** -> **PASS**
- **Expected output / Actual no output** -> **FAIL**
- **Expected no output / Actual output** -> **FAIL**
- **Expected output / Actual output / contents equal** -> **PASS**
- **Expected output / Actual output / contents differ** -> **FAIL**
- **Expected behavior cannot be determined** -> **UNVERIFIED** (UNKNOWN = UNVERIFIED; never defaults to pass or fail).

## 3. Exit Code Parity Contract
Default behavior: `EXIT_CODE_MISMATCH = FAIL`.
If different exit codes are equivalent (e.g. baseline returns 0, target Java returns 1 due to runtime wrappers), the equivalence contract must explicitly record the exception with an auditable justification.

## 4. Strict Normalization Rules
Every normalization rule must declare:
- **pattern**: Regex string.
- **affected artifact**: Filename.
- **reason**: Justification (e.g. `nondeterministic transaction timestamp`).
- **scope**: Mapped lines or fields.
- **before/after evidence**: Sample conversions.
