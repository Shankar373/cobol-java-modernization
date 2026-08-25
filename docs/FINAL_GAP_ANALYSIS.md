# FINAL GAP ANALYSIS — Baseline Forensic Audit (Before Fixes)

**Audit date:** 2026-08-25
**Repository:** https://github.com/Shankar373/cobol-java-modernization @ `85bafe3` (master)
**Method:** Direct source inspection of every production module, full test-suite execution, runtime probes.
No previous audit reports were trusted; every finding below was re-verified against actual code.

---

## 0. Baseline test run (ground truth)

Command: `python -m pytest --tb=no -q`
Environment: Python 3.14.3 / OpenJDK 25.0.3 / Docker 29.6.2 / Maven 3.9.16 (all available)

| Result | Count |
|---|---|
| passed | 390 |
| failed | **1** (`tests/logical_audit_test.py::test_logical_comparator_verification`) |
| skipped | 1 |
| warnings | 79 |
| duration | 45m49s |

The single failure is caused by a **stale-artifact dependency**: the test asserts files exist under
gitignored `target/baseline/legacy/` left over from an earlier pipeline run. On any fresh clone the
test fails identically — it does not generate its own fixtures.

---

## 1. CRITICAL findings (false-PASS / fabricated evidence)

### C-1. `--skip-legacy` fabricates a complete VERIFIED chain
- `cobol_migrate.py:3817-3819` — `stage_compare` writes `{"status": "PASS", "checks": [], "rows": []}` when `skip_legacy=True`, without comparing anything.
- `cobol_migrate.py:3269-3283` — `stage_transpile` fabricates `all_at_once_rc=0` and perfect per-file success counts under skip mode.
- `cobol_migrate.py:3715-3724` — `stage_execute` fabricates `"rc": 0`.
- `cobol_migrate.py:5600-5601` — `_compute_verdict`: `if legacy.get("skipped"): return "VERIFIED"`.
- Net effect: zero executions + zero comparisons ⇒ terminal verdict `VERIFIED` and exit code 0.
- Note: even when real baseline data IS pre-seeded (as `test_realistic_modernization.py` does), the compare stage short-circuits and never compares.

### C-2. Console negative-equivalence is a hardcoded PASS stub
- `cobol_migrate.py:4293-4301` (`_run_neg_equiv_console`): when a stdin scenario exists, writes
  `"status": "PASS", mutations_tested: 1, mutations_caught: 1` — **no mutation is created and nothing is executed or compared**.
- This fabricated PASS feeds the PRODUCTION_READY gate (`neg_equiv_ok`, cobol_migrate.py:5724-5727).

### C-3. Fabricated "Final Acceptance Report V2" emitted on every run
- `cobol_migrate.py:5272-5341` (and duplicated at 5343-5440): hardcodes narrative claims —
  "Gate 1: PASS", "100/100 randomized claims PASS", "FULL PASS (100% verified)", image digest,
  boundary-test results — **regardless of the repository being migrated or any evidence**.
  Also duplicates the traceability JSON/MD emission twice in the same stage.

### C-4. UI `/api/reset` arbitrary directory deletion (pre-auth path traversal)
- `ui.py:644-650`: `run_id` from POST body is used unvalidated in `os.path.join(WORKSPACE, run_id)`
  then `shutil.rmtree(ws, ignore_errors=True)`. `run_id=".."` deletes ancestors; absolute paths
  replace the base entirely. Combined with F-01 (no auth by default) this is remotely exploitable.

### C-5. Authentication disabled by default while Dockerfile binds 0.0.0.0:8787
- `ui.py:343-346` — `check_auth()` returns True when `UI_AUTH_CREDENTIALS` unset.
- `Dockerfile:44` binds all interfaces; `docker-compose.yml` publishes 8787 and sets no credentials.
- Default deployment = unauthenticated remote control (upload zip, clone repos, run builds, delete dirs).

---

## 2. HIGH findings

### H-1. stderr is never compared anywhere
- `execution/equivalence.py:42` seeds `checks["stderr"] = "PASS"`; no code path ever reads or writes it again.
- No `EXPECTED_STDERR` contract mode exists (`execution/contracts.py:19`). Stderr divergence can never FAIL.

### H-2. Gate 2 "exact parity PASS" reachable with no baseline
- `cobol_migrate.py:4847-4880` — missing baseline `claim-audit.dat` falls back to count-only; empty
  `parity_issues` + non-empty output ⇒ "exact parity with GnuCOBOL baseline" claimed with nothing compared.

### H-3. `enterprise_dep_ok` gate is self-satisfying
- `cobol_migrate.py:5702-5706`: `... or spring_generated  # spring generated implies enterprise project exists`.
  Generating the Spring project satisfies the enterprise dependency-audit gate regardless of audit result.

### H-4. Diagnostics corruption silently elevates verdict
- `cobol_migrate.py:5588-5595`: unreadable/corrupt `native_translation_diagnostics.json` is swallowed;
  `UNSUPPORTED` entries are never seen.

### H-5. audit_engine ignores file-set mismatches
- `audit_engine.py:270-274` only inspects rows with `verdict == "differ"`. `baseline-only` /
  `java-only` rows (an entire dropped output file) create no issue ⇒ GREEN "AUTOMATED AND VERIFIED".

### H-6. Unvalidated git URL schemes + credential persistence
- `ui.py:303-319`: `file://`, `ssh://`, `git://` accepted (only `-` prefix blocked) ⇒ local-file
  exfiltration via clone + SSRF surface.
- `ui.py:330-337`: URLs with embedded credentials stored verbatim in `meta.json`, echoed by
  `/api/state` and rendered in the sidebar; never redacted.

### H-7. Shell-string interpolation inside containers
- `execution/scenario_runner.py:280,357-361`: repo-derived program names/args interpolated unquoted
  into `sh -c` inside Docker ⇒ container-level command injection from COBOL PROGRAM-ID content.

### H-8. Stored XSS in artifact explorer
- `ui.html:1141-1144` uses `escapeJs()` inside an HTML attribute context (`ui.html:896-898`);
  backslash-escapes do not stop HTML attribute termination ⇒ uploaded-zip filenames execute JS in operator browser.

---

## 3. MEDIUM findings

| # | Finding | Location |
|---|---|---|
| M-1 | Missing execution evidence defaults exit codes to 0 on both sides | cobol_migrate.py:3879, 3908 |
| M-2 | `stdout_equiv_ok` inconsistent defaults (False at :5626 vs True at :5637) | cobol_migrate.py |
| M-3 | Compare stage marks FAIL-with-content-diffs as ok=True; FAIL with empty diff list also ok | cobol_migrate.py:4103-4108 |
| M-4 | Transpile success = stale `.java` existence; repo `generated/` not cleaned pre-copy; `|| true` fallback chains | cobol_migrate.py:1961-2015 |
| M-5 | javac recompile failure swallowed → stale `.class` executed vs recorded hashes | cobol_migrate.py:3419-3421 |
| M-6 | Native generator emits `BigDecimal.ZERO` on arithmetic parse failure (silent wrong-code) | modernize/native_generator.py:394-397 |
| M-7 | DB-state equivalence compares only db_type + affected_tables; row_counts/before_after/transaction_status captured but never diffed | execution/equivalence.py:264-292 |
| M-8 | DB2/CICS status is TCP-connect-only theater ("REAL_DB2_VERIFIED" on socket open; no SQL executed) | cobol_migrate.py:5081-5114 |
| M-9 | Zip extraction has no decompression-size cap (30MB upload can expand unbounded); limit text says 20MB, enforces 30MB | ui.py:617-618, 221-265 |
| M-10 | Global `RUNS` dict iterated without lock; reset-during-run breaks single-run invariant; ingest TOCTOU on workspace names | ui.py:41-42,135-143,272-279,674,646 |
| M-11 | `.dockerignore` excludes `execution/` but pipeline imports it at runtime ⇒ ModuleNotFoundError mid-pipeline in container | .dockerignore:23, cobol_migrate.py:3632+ |
| M-12 | Hardcoded benchmark coupling in production paths: claims.dat/rundate.txt heuristics (:2095), decode_audit_baseline claim-audit layout (:2171), ClaimsCore/BankCore JPA map (:2215), hardcoded rulebook (:2323-2499), golden policy-id generator (:2543), copybook-name classification Transaction→bank / Claim→claims (:4548-4577), filename-keyed comparators claim-audit.dat/eod-claims-report.txt (:4720-4733), REST endpoint assumptions (:4783-4789) | cobol_migrate.py |
| M-13 | Hardcoded `final_verdict = "PARTIAL"` blocks with BankCore deferral narrative | cobol_migrate.py:5273, 5374 |
| M-14 | Traceability manifest hardcodes "validation_evidence": "Spring Boot Compile check: PASS" | cobol_migrate.py:5218, 5230 |
| M-15 | audit_engine nonsense gate `(not n_ok or n_ok>0)` always true; dead `normalized_matches` metric | audit_engine.py:546-548, 222 |
| M-16 | SSE streams unbounded threads; no socket timeouts (slowloris); events grow unbounded into every /api/state payload | ui.py:407-420, 117-131, 711 |
| M-17 | Process-tree kill gaps: direct-child-only kill on timeout (Windows); orphaned JVM/Maven children | cobol_migrate.py:105-108, scenario_runner.py:169-175 |
| M-18 | Uploaded repo's own migration_config.json silently drives execution directives (interactive_scenario script path) | ui.py:171-173, cobol_migrate.py:6167-6170 |
| M-19 | File-set check compares Java outputs against contract, not against what COBOL actually produced; missing-file content failures leave differences list empty | equivalence.py:131-133,162-164 |
| M-20 | Baseline-side abnormal termination recorded in evidence but never gated (crashed baseline still proceeds to comparison) | equivalence.py:30-32 |

---

## 4. LOW findings (selected)

- Non-constant-time Basic-auth comparison (ui.py:356); no TLS anywhere; no rate limiting; CSRF-replayable state-changing endpoints; no security headers.
- Raw internal error text returned to clients (ui.py:325,490,542).
- Request logging suppressed — no server-side audit trail (ui.py:666-667).
- `restore_workspaces()` trusts any directory under workspace/.
- `modernize_and_verify.py` docker_run has no timeout; float list equality for COMP-3 amounts.
- audit_engine.py:565 hardcodes CCPROC01 manual-modification narrative for every audited repo.
- Dead spec values `input_exhausted` documented but never produced (scenario_runner).
- `tests/test_slicer.py:41-44` soft-skips Docker compile checks by printing "[SKIP]" and returning success — masks skip as pass.
- Undeclared test dependencies: playwright + requests imported by phase11b tests but absent from requirements.txt; JDK required by ~15 test files unmentioned.
- No CI workflows exist (.github contains only IDE hook scripts).
- `systemaops-release.zip` (614KB binary) committed at repo root.
- Stale committed pipeline state for ~30 fixture repos under tests/out/*/state.json; __pycache__ directories committed.
- idx.dat/out.dat/ui-server.log/someout/ stray artifacts at repo root.

## 5. Verdict-state inventory (baseline)

States that exist: UNVERIFIED, PARTIAL, EQUIVALENCE_UNVERIFIED, FAILED, BASELINE_UNPRODUCIBLE,
VERIFIED_WITH_LIMITATIONS, VERIFIED, NATIVE_JAVA_VERIFIED, NATIVE_SPRING_UNIFIED,
PRODUCTION_CANDIDATE, PRODUCTION_READY, UNSUPPORTED, plus comparison-level PASS/FAIL/UNVERIFIED.
**NOT implemented anywhere:** NOT_APPLICABLE (only prose), ENVIRONMENT_BLOCKED (does not exist).

---

## 6. Fix plan derived from this baseline

P0 equivalence: eliminate C-1/C-2/C-3 fabrication paths, add stderr comparison (H-1),
fail-closed defaults (M-1/M-2), deep DB state compare (M-7), audit_engine mismatch handling (H-5),
ENVIRONMENT_BLOCKED/NOT_APPLICABLE states, negative tests proving each bypass is caught.
Security: C-4, C-5, H-6, H-7, H-8, M-9..M-11, M-16..M-18 + regression tests.
Generalization: move fixture-specific logic out of generic paths (M-12/M-13), evidence-driven acceptance report.
Tests: fix logical_audit_test self-containment; consolidate conftest helpers; declare test deps.
Cleanup: remove committed binaries/stale artifacts, fix .dockerignore packaging.
