# AGENTS.md COMPLIANCE AUDIT — POST-FIX VERIFICATION

**Date:** 2026-08-25 · **Tree:** post `1b70ef6` + this fix phase · **Spec:** `docs/AGENTS.md`
**Method:** every ✅ below is backed by an executed command in this session; ❌/⚠️ items carry file:line evidence.
Supersedes the pre-fix gap report; see §5 for what was changed and §6 for honest remaining gaps.

---

## 1. EXECUTION EVIDENCE (this session)

| Check | Command | Result |
|---|---|---|
| Full clean regression | `python -m pytest -q` (pycache cleared) | **466 passed / 0 failed / 0 skipped**, 18m38s |
| Tracked-tree hygiene during full run | `git status --porcelain audit/` | **empty** (was dirtied by every run pre-fix) |
| Offline Maven resolution | `mvn -B -o -f docker/maven-proleap-seed-pom.xml dependency:resolve` (+ seed pom) | **BUILD SUCCESS ×2**, zero network |
| Artifact inventory vs pinned list | local `.m2` existence check, same list as Dockerfile verify step | **8/8 present** |
| Concurrent-run isolation | `tests/test_native_artifact_isolation.py` | 3/3 pass; global paths untouched |
| Fixture-purge safety | legacy preprocess smoke + realistic E2E (`test_realistic_modernization`) | pass; cobj transpile unaffected |

---

## 2. SECTION MATRIX (post-fix)

| § | Area | Pre-fix | Post-fix | Evidence |
|---|---|---|---|---|
| 2 | Repository agnosticism | PARTIAL | **COMPLIANT** | 446 fixture-only lines removed from `_norm_file`; zero fixture names remain in module [grep]; `test_no_hardcoding` + unseen suites green |
| 2 | Native Track-B independence | ✅ | ✅ | dependency-gate suites green [T] |
| 2 | Business equivalence fail-closed | ✅ | ✅ | negative-gate suite green [T] |
| 3 | Parser/IR diagnostics | ✅ | ✅ | ALTER/SORT/SQL diagnostics tests [T] |
| 4 | JCL | ⚠️ | ⚠️ unchanged | symbol/util suites green [T]; nested-PROC depth still not individually re-verified |
| 5 | DB2 classification | PARTIAL | **COMPLIANT (capability gap documented)** | `classify_db2_status()` extracted; tautology replaced with 6 exact-state assertions incl. deterministic offline socket cases [T] |
| 6 | CICS honesty | ✅ | ✅ | emulation-only assertions [T] |
| 7 | VSAM/file semantics | PARTIAL | PARTIAL (documented) | single limitation: multi-mode reopen emits `NATIVE_TRANSLATION_LIMITED` [T: test_08b] |
| 8 | Codegen quality | ✅ | ✅ | WRITE-FROM literal fix held through full run [T] |
| 9 | Fail-closed gates | ❌ slicer | **COMPLIANT** | `self.skipTest("ENVIRONMENT_BLOCKED: Docker unavailable…")` replaces print+return [T] |
| 10 | Maven determinism | PARTIAL | **COMPLIANT on host; container step authored-not-executed** | seed poms pin plugin 3.6.1; Dockerfile hard-fails resolution and verifies 8 artifacts; list proven 8/8 locally; `mvn -o` SUCCESS |
| 11 | ProLeap integration | PARTIAL | **COMPLIANT** | `required_proleap_jars()` single source of truth; guard imports it; `os.pathsep` classpath; vendored jars tracked w/ SHA-256+MIT [T] |
| 12 | Security | ✅ | ✅ + XSS regression pinned | `escapeJs`=encodeURIComponent contract test [T] |
| 13 | Concurrency/isolation | ❌ globals | **COMPLIANT** | 9 writers scoped; regression test proves disjoint evidence dirs + untouched globals; perf-test writer moved to tmp_path; `audit/phase8` residue fixed |
| 14 | UI rules | ✅ | ✅ (cosmetic deferral noted) | live-verdict polling verified by 11b suites [T] |
| 15 | Testing breadth | ⚠️ | **COMPLIANT** | +10 tests this phase (isolation×3, parity×4, XSS×3); unseen-repo E2E inside full run |
| 16 | Test integrity | ⚠️ | **COMPLIANT** | tautological DB2 test now exercises production logic; no assertion weakened anywhere (diff-reviewed) |
| 17 | Docs sync | ❌ | **COMPLIANT** | requirements.txt corrected; requirements-dev.txt pins requests/playwright; JDK/Maven/Docker prerequisites documented |
| 18 | Production readiness | ❌ CI | ⚠️ **CI authored, execution UNVERIFIED** | `.github/workflows/ci.yml` fast+nightly lanes; cannot run GitHub runner locally — first push will exercise it |
| 19–22 | Workflow/report/DoD | ✅ | ✅ | this document satisfies §20 format |

---

## 3. CHANGES BY FILE (fix phase)

Production:
- `cobol_migrate.py` — removed 446 lines of fixture-keyed preprocessing (UTLMON00/UTLVAL00/error-handling/CB_01_MAP/HISTREC/CKPRST/ENTRY-POINT-INIT/ERRHND/INQCOM/BCHCTL/AUDITLOG/POSREC-stems/PORTFLIO/RTNANA00/TSTGEN00/INQPORT/PORTTEST/DB2STAT-specials); kept all generic cobj/CICS/DB2 compat steps; extracted `classify_db2_status()`; removed stale global-diagnostics fallback in `_compute_verdict`.
- `modernize/native_pipeline.py` — all 9 artifact writes + 2 report writes now run-scoped (`_artifact_file`/`_report_file` under `self.out`).
- `modernize/proleap_adapter/parser_adapter.py` — `required_proleap_jars()` SSOT; `os.pathsep` classpath; resolver extension superset (`.copy/.COPY` drift fixed).
- `Dockerfile` / `docker/maven-seed-pom.xml` — deterministic resolve (fail-loud), pinned plugin, per-artifact verification RUN (8 checks).
- `tests/test_phase8_performance.py`, `tests/test_slicer.py` — run-scoped results; genuine ENVIRONMENT_BLOCKED skip.

Tests added/strengthened: `test_native_artifact_isolation.py` (new), `test_hardening_parity_and_ui.py` (new), `test_db2_real_vs_emulated.py` (tautology→real), proleap guard parity.

Repo hygiene: `legacy/_preprocessed/**` untracked (104 files) + gitignored; `modernize_and_verify.py` → `tools/`.

Infra/docs: `.github/workflows/ci.yml`; `requirements-dev.txt`; `requirements.txt` corrections.

---

## 4. DEPENDENCY / OFFLINE STATUS

- Runtime deps of platform: stdlib-only [requirements.txt].
- Test deps: pinned in `requirements-dev.txt` (requests 2.x, playwright 1.x).
- Parser-side JARs: 7-path SSOT; vendored ProLeap jars git-tracked (SHA-256 recorded in FINAL_FORENSIC doc).
- Offline: both seed POMs resolve with `-o` (BUILD SUCCESS). Full OS-network-disable test NOT performed (documented limitation).

## 5. REMAINING LIMITATIONS (evidence-backed, accepted)

1. Multi-mode COBOL file reopen generates one IO family + explicit WARNING diagnostic (semantic gap, honestly surfaced).
2. Real DB2 / CICS execution capability does not exist; statuses are honest labels only.
3. CI workflow syntax/logic UNVERIFIED until first runner execution.
4. Dockerfile verification step not executed end-to-end (image build heavy); the checked path list itself proven 8/8 against a real `.m2`.
5. UI stage-detail pane can show stale content post-terminal until rerender (cosmetic; deferred — blind 76KB HTML edit risk > benefit).
6. Web residuals: Basic-auth over plain HTTP, CSRF-replayable POSTs, no rate limiting — acceptable for localhost tooling; must close before any network-exposed deployment.

## 6. FINAL STATUS

**PRODUCTION CANDIDATE** (upgraded confidence from MVP+):
full regression 466/0/0, false-PASS paths closed with regression tests, concurrency isolation proven, dependencies reproducible offline, repository-agnostic preprocessing restored.
**Production Ready remains blocked** by items 3–6 above (CI execution proof + deployment-hardening choices), none of which are correctness gaps in the migration engine itself.
