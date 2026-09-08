# Phase 2A — Public Type Vocabulary

Status: **STABLE FOR PHASE 2A**
Source: `modernize_v2/`
Reference: `docs/PHASE_2_ARCHITECTURE_V2.md`, `docs/PHASE_2_WORK_BREAKDOWN.md`

This document is the public contract for the Phase 2A types. It
is the reference for downstream code (parser, generator, comparator,
evidence store).

---

## 1. Stability

Phase 2A is the *foundation* layer. Renaming a public symbol or
changing its external format (the 26-character Crockford base32
id, the JSON serialization, the capability status vocabulary) is
a **breaking change** for Phase 2B..2L and must be discussed in
`docs/PHASE_2_DECISION_REGISTER.md`.

Adding new enum members, new dataclass fields with defaults, or
new helper functions is a **non-breaking** change provided the
invariants in §3 are preserved.

---

## 2. Public Symbols

### 2.1 `modernize_v2`

```
modernize_v2.__version__        # "2.0.0-alpha.0"
modernize_v2.__phase__          # "2A"
```

### 2.2 `modernize_v2.ir`

```
DeterministicId                 # immutable 26-char Crockford base32 id
id_for_node(kind, path, line, column, byte_offset, ordinal=0)
ID_LENGTH                       # 26
ID_CHARSET                      # Crockford base32 alphabet
IRID_NAMESPACE                  # "N"
KIND_NAMESPACE                  # "NK"

IRKind                          # enum of canonical node kinds
is_statement_kind(kind)
is_expression_kind(kind)
is_sql_kind(kind)
is_cics_kind(kind)
is_jcl_kind(kind)
is_data_item_kind(kind)
iter_categories()

Diagnostic                      # immutable diagnostic record
DiagnosticSeverity              # ERROR | WARNING | INFO
DiagnosticKind                  # UNSUPPORTED_FEATURE | UNRESOLVED_SYMBOL
                                 # TYPE_MISMATCH | REDEFINES_OVERLAP
                                 # ODO_OUT_OF_BOUNDS | PARSER_RECOVERY
                                 # INVALID_SOURCE | INVALID_CONFIGURATION
                                 # ENVIRONMENT_BLOCKED | CAPABILITY_MISMATCH
SourcePosition                  # line, column, byte_offset
SourceSpan                      # canonical_path + start..end
diagnostics_to_canonical_json(diagnostics)
```

### 2.3 `modernize_v2.capabilities`

```
Capability                      # named feature key
CapabilityState                 # SUPPORTED_AND_VERIFIED |
                                 # SUPPORTED_UNVERIFIED |
                                 # PARTIAL | SIMULATED |
                                 # UNSUPPORTED
STATE_ORDER                     # tuple, strongest -> weakest
CapabilityRecord                # capability + state + workload + evidence
CapabilityRegistry              # append-only registry
iter_capabilities(registry)

GateOutcome                     # ALLOW | ALLOW_BUT_NOT_VERIFIED |
                                 # ALLOW_BUT_EMULATED | BLOCK
CapabilityDecision              # outcome + records + diagnostics
CapabilityGate(allow_partial, allow_simulated)
```

### 2.4 `modernize_v2.verification`

```
DIM_*                           # dimension keys
ALL_DIMENSIONS                  # tuple of all dimension keys
OutputFileMode                  # TEXT | BYTES
OutputFileObservation
DatabaseStateObservation
SqlOperationObservation         # sqlcode, sqlstate
NullIndicatorObservation        # call_site, host_var, indicator
TransactionObservation
FileStatusObservation
CicsStateObservation
BatchStateObservation
Encoding                        # source_codepage, java_charset, ...
Observation                     # complete observation tuple
                                # exit_code, stdout, stderr,
                                # output_files, db_state, sqlcode_seq,
                                # sqlstate_seq, null_indicator_seq,
                                # transaction_state, file_status_seq,
                                # cics_state, batch_state,
                                # observed_at, encoding, content_hash

ComparisonStatus                # PASS | FAILED | UNVERIFIED |
                                 # PARTIAL | ENVIRONMENT_BLOCKED |
                                 # SKIPPED
DimensionStatus                 # PASS | FAILED | UNVERIFIED | SKIPPED
DimensionResult
ComparisonResult
Verdict
compute_overall_status(...)
RESERVED_STATUSES

ComparisonMode                  # PHYSICAL | KEY_SORTED | SET
DEFAULT_COMPARISON_MODES
RequiredDimensions              # required dims + per-dim modes
SeedDeclaration                 # explicit seed data
ArtifactExpectation             # expected file/table/step/channel
ContractValidationError         # raised on invalid contract
VerificationContract            # immutable contract
default_contract(workload_id, ...)
```

---

## 3. Invariants

Every public type in Phase 2A upholds:

1. **Immutability.** All public dataclasses are `frozen=True`.
   Updates produce new instances; there is no mutating API.

2. **Determinism.** Every public type has a deterministic JSON
   serialization (`to_canonical_json`) and a deterministic hash
   (`content_hash` or `diagnostic_id`). Two instances with the
   same field values produce the same hash and the same JSON.

3. **No IO at import.** V2 modules do not read the filesystem
   or environment variables at import time. This is enforced
   by `tests/v2/test_architecture_invariants.py`.

4. **No V1 dependencies.** V2 does not import the V1 `modernize`
   package. This is enforced by the same test.

5. **No legacy runtime.** V2 does not import `libcobj`,
   `jp.osscons`, or `OpenSourceCOBOL4J`. This is enforced by
   the same test.

6. **No `Dict[str, Any]` in public contracts.** Field types are
   `tuple[...]`, `frozenset[...]`, dataclasses, or primitive
   types. This is enforced by the same test.

7. **No wall clock or random.** V2 has no `time`, `datetime`,
   `random`, or `uuid` imports. This is enforced by the same
   test.

8. **Fail-closed.** The CapabilityGate blocks on `UNSUPPORTED`.
   The Verdict becomes `UNVERIFIED` for missing required
   observations. The Contract raises `ContractValidationError`
   for missing required dimensions.

---

## 4. Dependency Direction

```
modernize_v2.ir
   ↑ (imports)
   ├── modernize_v2.capabilities
   └── modernize_v2.verification
```

Subpackages may import from `modernize_v2.ir` and from each
other in the direction shown. There is no circular import.

`modernize_v2` does not import from `modernize` (V1).

---

## 5. Serialization Rules

| Type                       | Hash function         | JSON canonicalization                  |
|----------------------------|-----------------------|----------------------------------------|
| `DeterministicId`          | external format       | text only                              |
| `Diagnostic`               | `diagnostic_id`       | `to_canonical_json` (sorted keys)      |
| `Observation`              | `content_hash` (SHA-256) | `to_canonical_json` (sorted, content_hash popped) |
| `ComparisonResult`         | text only             | `to_canonical_json`                    |
| `Verdict`                  | `content_hash` (SHA-256) | `to_canonical_json`                 |
| `VerificationContract`     | `content_hash` (SHA-256) | `to_canonical_json`                 |
| `CapabilityRecord`         | external format       | not directly serialized by V2          |

JSON output is UTF-8, `ensure_ascii=False`, `sort_keys=True`,
`separators=(",", ":")`. JSON input accepts the same form
or any non-canonical form (the comparator normalizes).

---

## 6. Status Vocabulary

The platform's verdict vocabulary is the closed set in
`RESERVED_STATUSES`:

```
PASS                     # all required dims match
FAILED                   # at least one required dim mismatched
UNVERIFIED               # at least one required dim is missing
PARTIAL                  # some dims matched, others skipped
                         # (out of scope for default comparator)
ENVIRONMENT_BLOCKED      # comparison could not run
                         # (e.g., real DB2 unavailable)
SKIPPED                  # comparison explicitly skipped
                         # (operator opt-in, documented reason)
```

The capability vocabulary is the closed set in `CapabilityState`:

```
SUPPORTED_AND_VERIFIED
SUPPORTED_UNVERIFIED
PARTIAL
SIMULATED
UNSUPPORTED
```

The diagnostic vocabulary is the closed set in `DiagnosticKind`.
Adding a kind is non-breaking; renaming is breaking.

---

## 7. Forbidden Patterns

The following patterns are forbidden in V2 code and will cause
the invariant tests to fail:

- `import modernize` or `from modernize import …` (V1 coupling)
- `import libcobj` or `import jp.osscons.*`
- `import random` or `import uuid` (non-determinism)
- `import time` or `import datetime` (wall clock at import)
- Top-level `open(...)` or `read_text()` (filesystem at import)
- Field type `Dict[str, Any]` in public dataclasses
- `shell=True` (forbidden by Phase 2K, enforced proactively)

These invariants are exercised by
`tests/v2/test_architecture_invariants.py` and are a regression
gate for Phase 2B..2L.
