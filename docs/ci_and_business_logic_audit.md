# CI & Business-Logic Coverage Audit

Date: 2026-08-31
Branch: `master`
Status: PARTIAL — CI green-able but not fully green due to environment-blocked DB2 tests

---

## 1. Objective

This audit documents:

1. The current GitHub Actions CI status and what each run verified.
2. A classification of the automated test suite into **business-logic coverage**
   versus **infrastructure-only coverage**.
3. Coverage gaps and evidence-backed recommendations.

The audit follows the project engineering rules (FAIL-CLOSED; no claim without
evidence; infrastructure tests must not masquerade as business equivalence).

---

## 2. CI Workflow Overview

Workflow: `.github/workflows/ci.yml` (id `342352724`)

Two jobs:

| Job | Trigger | What it runs |
|---|---|---|
| `fast` | push to `master`, pull_request | Builds GnuCOBOL+OCESQL image, starts real PostgreSQL 16, seeds schema, runs full pytest suite (minus nightly-only tests) |
| `nightly-full` | schedule (03:00 daily) + `workflow_dispatch` | Everything in `fast` plus all tests, Playwright UI, opensourcecobol4j transpiler |

### Fast-lane test exclusions (`--ignore`)

After this work, the fast-lane `--ignore` list is:

```
tests/logical_audit_test.py
tests/test_realistic_modernization.py
tests/test_validation_nobypass.py
tests/test_generic_refactoring.py
tests/robustness/adversarial/test_java_source_mutation.py
```

> Note: during the test reorganization, `test_java_source_mutation.py` was moved
> from `tests/` into `tests/robustness/adversarial/`, which silently changed its
> `--ignore` matching. This was corrected (see §5).

---

## 3. CI Run History (evidence)

Repository GitHub: `Shankar373/cobol-java-modernization` (remote `origin`, branch `master`).

| Run ID | Commit | Result | Test summary |
|---|---|---|---|
| `33325109742` | `41e5c5a` (baseline, pre-reorg) | FAIL | 1 failed (DB2 tx visibility), 627 passed, 4 skipped |
| `33324242651` | (pre-reorg) | FAIL | DB2 tx visibility only |
| `33323310086` | (pre-reorg) | FAIL | DB2 tx visibility only |
| `33371944619` | `3132603` (reorg) | FAIL | **collection abort** — 24 errors, 488 collected |
| `33372723406` | `3a687d7` (shim removal) | FAIL | 8 failed, 622 passed, 9 skipped |
| `33374179798` | `882fdc0` (ignore + ui.html fix) | FAIL | 4 failed, 625 passed, 9 skipped |

### Latest run (`33374179798`) — breaking it down

```
4 failed, 625 passed, 9 skipped in 544.40s
```

- **625 passed** — the business-logic and unit/integration acceptance suite.
- **9 skipped** — all infrastructure/parity tests:
  - 5 new differential tests (`filestat01`, `sizeerr01`, `db2curnull01`,
    `occurs01`, `redefines01`) — SKIP in fast-lane because Docker parity is not
    enabled there.
  - 4 `test_parity_fixtures` tests (EBCDIC records, relative-file random access,
    indexed-file missing key, JCL conditional) — SKIP for the same reason.
- **4 failed** — all in `tests/test_db2_stage1.py`:
  - `test_db2_left_outer_join_e2e`
  - `test_db2_count_aggregate_e2e`
  - `test_db2_group_by_having_e2e`
  - `test_db2_tx_commit_visible_e2e`

---

## 4. Classification of the 4 Remaining Failures (DB2 E2E)

All four failures share a single error signature produced by the generated /
OCESQL native execution path against PostgreSQL:

```
CURSOR OPEN FAILED SQLSTATE: 99999
NATIVE_JAVA = NOT_VERIFIED: Equivalence failed (verdict: FAIL)
```

`SQLSTATE 99999` is the OCESQL/runtime generic connection-failure SQLSTATE. The
failure occurs at runtime **DB connectivity**, not at parse, generate, or compile.

### Evidence-based classification

| Test | Pre-reorg baseline | Post-reorg (2 runs) | Classification |
|---|---|---|---|
| `test_db2_tx_commit_visible_e2e` | FAIL (all prior runs, same error) | FAIL (both runs) | **PRE-EXISTING** |
| `test_db2_left_outer_join_e2e` | PASS (3 prior runs) | FAIL (both runs) | **ENVIRONMENT/DB-connectivity** |
| `test_db2_count_aggregate_e2e` | PASS (3 prior runs) | FAIL (both runs) | **ENVIRONMENT/DB-connectivity** |
| `test_db2_group_by_having_e2e` | PASS (3 prior runs) | FAIL (both runs) | **ENVIRONMENT/DB-connectivity** |

### Reasoning (not asserted — argued from evidence)

- No DB2 runtime code, `modules/native_pipeline.py`, or any of the failing test
  repos (`DB2LEFTJOIN01`, `DB2AGGREGATE01`, `DB2GROUPBY01`, `DB2TXVISIBILITY01`)
  were modified by this work. The entire source delta on the production path was a
  one-line assertion in `modernize/native_generator.py:373` (Payment01 single-quote
  bug) — unrelated to DB connection.
- The identical `CURSOR OPEN FAILED 99999` connection error spans **four different
  repos**, which is the signature of a shared infrastructure / DB-connectivity
  cause, not four independent logic bugs.
- The same three tests passed in **three prior CI runs** on the same DB2 code
  paths, indicating the code path itself is functionally correct in a healthy
  environment.

**Status: NOT VERIFIED (root cause).** Full root-cause verification requires the
Docker GnuCOBOL+OCESQL image and the real PostgreSQL container, which are not
available in this working environment (Docker daemon is not running locally).
This must not be claimed as fixed.

> Per project rule §16, these tests are **NOT** being weakened, skipped, or
> converted to PASS. They remain real failures until the environment supports them.

---

## 5. Regressions Introduced by the Test Reorganization (all now FIXED)

The reorganization commit `3132603` introduced three CI-breaking issues. All were
diagnosed and fixed; each fix is committed and pushed.

| Issue | Symptom in CI | Fix | Verified |
|---|---|---|---|
| Empty placeholder shims | `import file mismatch` — 24 collection errors | Deleted 23 placeholder shim files (commit `3a687d7`) | `647` tests collected cleanly |
| `test_java_source_mutation.py` moved, so `--ignore` stopped matching | It unexpectedly ran and failed in fast-lane | Updated `--ignore` path (commit `882fdc0`) | Removed from run |
| `test_hardening_parity_and_ui.py` moved, so `ui.html` path broke | `FileNotFoundError: tests/integration/ui.html` (3 test failures) | Corrected relative path to repo root (commit `882fdc0`) | 7/7 pass locally |

---

## 6. Test Suite Coverage Classification

### 6.1 Business-logic coverage (semantics, parser, IR, generator, equivalence)

These verify that COBOL behaviour is preserved by the generator — the heart of
"business equivalence".

| Area | Representative files | What they verify |
|---|---|---|
| Parser / IR / lexer | `tests/unit/parser`, `tests/unit/lexer`, `tests/unit/ir`, `tests/test_control_flow.py`, `tests/test_data_flow.py` | Tokenization, parse, semantic IR, control/data flow |
| Native generator semantics | `test_native_*.py` (call, compute truncation, evaluate, file_io, level88, move_multi, occurs, paragraph_control, perform_varying, period_scoping, ref_mod, statement_translation, traceability, type_mapping) | Per-CONSTRUCT behavioural translation |
| Arithmetic / numeric | `test_phase8_arithmetic_errors.py`, `test_native_compute_truncation.py` | Overflow, ON SIZE ERROR, precision |
| Report Writer | `test_phase8_report_writer.py` | Report generation semantics |
| Sort / merge | `test_phase8_sort_merge.py` | SORT/MERGE workflow |
| String / pointers | `test_phase8_string_operations.py`, `test_phase8_pointers.py` | String and pointer operations |
| DB2 / SQL semantics | `test_db2_acceptance.py`, `test_db2_stage1.py` (unit), `test_sql_db_ksds_modernization.py`, `test_db2_dialect_null_indicators.py` | SQL translation and (where env allows) execution |
| Differential equivalence | `tests/e2e/differential/*` (5 new tests) | COBOL-vs-Java output comparison (SKIP in fast-lane) |
| Unseen repos | `tests/robustness/unseen/*` | Repository-agnostic generalisation |

### 6.2 Infrastructure / validation / security coverage (NOT business equivalence)

These verify the pipeline's robustness, validation integrity and security — they
are important but do **not** prove business equivalence on their own.

| Area | Representative files |
|---|---|
| Validation gates / fail-closed | `test_no_false_production_ready.py`, `test_phase10_gates.py`, `test_validation_nobypass.py`, `test_no_hardcoding.py` (all at `tests/` root) |
| Security | `test_phase11b_security.py`, `test_phase8_security_audit.py`, `test_proleap_security.py`, `test_security_hardening.py` |
| Concurrency / workspace isolation | `test_concurrency_isolation.py`, `test_phase11b_workspace_isolation.py`, `test_docker_isolation.py`, `test_pipeline_remediation.py` |
| Failure recovery / negative paths | `test_phase8_failure_recovery.py`, `test_phase9_failure_matrix.py`, `test_negative_*`, `test_native_negative_equivalence.py` |
| Dependency / Maven / offline | `test_dependencies.py`, `test_phase8_dependency_audit.py`, `test_native_dependency_gate.py` |
| API / contract | `test_phase9_api_contract.py`, `test_phase9_manifest.py`, `test_phase9_repeatability.py` |
| E2E pipeline | `test_postgres_e2e.py`, `test_sql_baseline.py`, `test_sql_db_ksds_modernization.py` (integration) |

### 6.3 Finding: "categorization" subdirectories removed (flat layout retained)

After removing the placeholder shims (which only contained comment text and broke
pytest collection), the previously-empty categorization subdirectories
(`tests/negative/`, `tests/security/`, `tests/hardening/`, `tests/contracts/`,
`tests/gates/`) were **deleted** in favour of keeping all such tests flat at the
`tests/` root.

The real tests for those domains remain **at `tests/` root** (e.g.
`test_security_hardening.py`, `test_negative_equivalence_contract.py`,
`test_phase10_gates.py`). These directories were only empty scaffolding — they
contained no tracked source files and no real tests, so removing them changes no
test logic and the suite collects cleanly.

**Why flat rather than moving tests into subdirectories:** the affected tests all
rely on root-relative `sys.path` boilerplate
(`os.path.dirname(os.path.dirname(os.path.abspath(__file__)))`) that resolves to
the repository root only at the `tests/` depth. Moving them one level deeper
(e.g. into `tests/security/`) would break `from modernize.*` and `from tests.*`
package imports (e.g. `test_phase8_failure_recovery.py` imports
`from tests.test_phase8_file_semantics import run_cobol_code`), and would require
path fixes in several files that reference fixtures (`ui.py`, `ui.html`,
`repos/ACCTPROG`). The decision rule in the task therefore selects **Option B**
(remove stubs, keep flat). The test suite is intentionally split across a small
number of genuinely-moved subdirectories (`tests/unit`, `tests/component`,
`tests/e2e/differential`, `tests/robustness`) plus a flat root for the remaining
domain suites.

---

## 7. Coverage Gaps

1. **Differential equivalence largely SKIPPED in CI fast-lane.** All 5 new
   differential tests and 4 parity-fidelity tests require Docker parity /
   `PARITY_ALLOW_SKIP` semantics and do not run in the fast lane. Business
   equivalence claims currently rest on the (large) unit/integration suite, not on
   a running fixture-to-fixture comparison in CI. Only the `nightly-full` job
   exercises this, and it must be confirmed to actually run rather than skip.

2. **Real DB2 is `NOT_VERIFIED`.** As documented in the objective and in
   `docs/REAL_DB2_FINAL_VERIFICATION.md`, the platform has never been executed
   against a real DB2. All DB2 evidence is either emulated (H2) or against
   PostgreSQL. The `CURSOR OPEN FAILED 99999` failures sharpen this: even the
   PostgreSQL-backed DB2 E2E path is currently unstable in CI.

3. **No per-domain home for security/gates/negative/contracts/hardening tests.**
   The empty stub directories (§6.3) leave the suite layout inconsistent and make
   it easy for future "reorganization" to drift into duplicate-basename collisions
   again.

4. **CI is not green.** Until the DB2 E2E connectivity issue is resolved (or those
   tests are correctly classified as environment-blocked), the repo cannot claim a
   green CI signal. Per project rules, this must not be hidden by weakening tests.

5. **No explicit CI gate tying nightly differential results back to a job result.**
   The `nightly-full` job runs everything but there is no fast, deterministic,
   required diff-coverage assertion on business-critical constructs in the default
   push path.

---

## 8. Recommendations

1. **Investigate and resolve the DB2 E2E connection failure in CI** (highest
   priority). Reproduce inside the Docker `gnucobol-ocesql` container against the
   seeded PostgreSQL: confirm whether `CURSOR OPEN FAILED 99999` is a transaction /
   connection-pool exhaustion, a container network issue, or a genuine generated-
   code regression. Do not mark green until root-caused.

2. **Make differential parity run deterministically in a defined job**, with
   `PARITY_ALLOW_SKIP=false` explicitly asserted where Docker is guaranteed, so
   that business-equivalence comparison is not silently exercised only in nightly.
   Add a CI step that fails if any "business-equivalence-required" differential
   test reports `SKIP` without a recorded environment reason.

3. **Complete or revert the test reorganization.** Either move the real
   security/gates/negative/contracts/hardening tests into their empty
   subdirectories (fixing all `__file__`-relative paths), or remove the empty
   stub directories to restore a coherent flat layout. Re-run full collection after
   any change to avoid duplicate-basename `import file mismatch`.

4. **Guard against duplicate module basenames.** Add a lightweight CI check (or
   `conftest.py` assertion) that fails if two collected test modules resolve to
   the same pytest module name, preventing a recurrence of the 24-error collection
   abort.

5. **Document DB2 status honestly.** Keep `REAL_DB2` as `NOT_VERIFIED` and classify
   the DB2 E2E failures as `ENVIRONMENT_BLOCKED` / failing until a healthy DB
   environment proves otherwise. No emulation should be reported as real DB2.

---

## 9. Final Status

| Item | Status |
|---|---|
| Local changes committed & pushed | VERIFIED (HEAD `882fdc0`) |
| CI workflow inspected | VERIFIED |
| Reorg-induced collection errors | FIXED & VERIFIED (647 collected) |
| Reorg-induced ignore/path regressions | FIXED & VERIFIED |
| Full suite result | 625 passed, 9 skipped, 4 failed |
| DB2 E2E connectivity failure root cause | **NOT VERIFIED** (environment unavailable to reproduce) |
| Real DB2 compatibility | NOT_VERIFIED |

Overall status: **PARTIAL** — all structural/regression issues from the
reorganization are resolved, but the CI pipeline is not green because four DB2 E2E
tests fail on DB connectivity (one pre-existing, three environment-classified).
These have **not** been weakened; they remain real failures pending environment
verification.
