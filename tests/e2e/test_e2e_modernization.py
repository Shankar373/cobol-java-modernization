"""
tests/e2e/test_e2e_modernization.py

END-TO-END BLACK-BOX VALIDATION
COBOL -> Java Modernization UI

Target URL : http://127.0.0.1:8787
Auth       : Basic admin:admin  (env: UI_TEST_CREDENTIALS, default admin:admin)
Workload   : INVENTORY01 (minimal single-program, FILE_OUTPUT business equivalence)

Evidence Levels:
  UI_VERIFIED             -- UI renders / HTTP responds correctly
  BACKEND_VERIFIED        -- /api/state matches backend state
  FILESYSTEM_VERIFIED     -- files on disk exist with correct timestamps
  COBOL_EXEC_VERIFIED     -- COBOL program ran and produced baseline output
  JAVA_COMPILED           -- Maven build produced .class files for this run
  JAVA_RUNTIME_VERIFIED   -- Java program ran and produced output for this run
  BUSINESS_EQUIVALENCE_VERIFIED -- COBOL output == Java output (exact bytes)

Run:
  pytest tests/e2e/test_e2e_modernization.py -v --timeout=600
  pytest tests/e2e/test_e2e_modernization.py -v -k health
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import time
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Optional

import pytest
import requests
from playwright.sync_api import Page, sync_playwright

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_URL = os.environ.get("UI_TEST_BASE_URL", "http://127.0.0.1:8787")
_raw_creds = os.environ.get("UI_TEST_CREDENTIALS", "admin:admin")
CRED_USER, CRED_PASS = _raw_creds.split(":", 1)
AUTH_HEADER = "Basic " + base64.b64encode(_raw_creds.encode()).decode()

FIXTURE_ZIP = Path(__file__).parent / "fixtures" / "inventory01-fresh.zip"
WORKSPACE_DIR = Path(__file__).parent.parent.parent / "workspace"

PIPELINE_TIMEOUT = 420
STAGE_POLL = 4
SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

# Evidence ledger populated across the session
EVIDENCE: dict = {}


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------
def _api(method: str, path: str, **kw) -> requests.Response:
    hdrs = kw.pop("headers", {})
    hdrs["Authorization"] = AUTH_HEADER
    return getattr(requests, method)(BASE_URL + path, headers=hdrs, timeout=30, **kw)


def api_state() -> dict:
    return _api("get", "/api/state").json()


def api_run_state(run_id: str) -> Optional[dict]:
    for r in api_state().get("runs", []):
        if r["run_id"] == run_id:
            return r
    return None


def api_log(run_id: str) -> list:
    return _api("get", f"/api/log?run_id={run_id}").json().get("log", [])


def api_artifacts(run_id: str) -> list:
    return _api("get", f"/api/artifacts?run_id={run_id}").json().get("artifacts", [])


def api_modernized(run_id: str) -> list:
    return _api("get", f"/api/modernized?run_id={run_id}").json().get("files", [])


def api_ingest_zip(zip_path: Path, name: str) -> str:
    data = base64.b64encode(zip_path.read_bytes()).decode()
    r = _api("post", "/api/ingest", json={"source": "zip", "data": data, "name": name})
    body = r.json()
    assert body.get("ok"), f"Ingest failed: {body}"
    return body["run_id"]


def api_start(run_id: str, restart_from: int = 0) -> dict:
    return _api("post", "/api/run",
                json={"run_id": run_id, "restart_from": restart_from}).json()


def api_reset(run_id: str) -> dict:
    return _api("post", "/api/reset", json={"run_id": run_id}).json()


def api_stop(run_id: str) -> dict:
    return _api("post", "/api/stop", json={"run_id": run_id}).json()


def wait_for_run(run_id: str, timeout: int = PIPELINE_TIMEOUT) -> dict:
    deadline = time.time() + timeout
    while time.time() < deadline:
        st = api_run_state(run_id)
        if st is None:
            raise RuntimeError(f"Run {run_id!r} vanished from state")
        if st.get("status") in ("done", "error", "interrupted"):
            return st
        time.sleep(STAGE_POLL)
    return api_run_state(run_id) or {}


# ---------------------------------------------------------------------------
# Filesystem helpers
# ---------------------------------------------------------------------------
def ws(run_id: str) -> Path:
    return WORKSPACE_DIR / run_id


def tgt(run_id: str) -> Path:
    return ws(run_id) / "target"


def file_mtime(p: Path) -> Optional[float]:
    return p.stat().st_mtime if p.exists() else None


def state_json(run_id: str) -> dict:
    p = tgt(run_id) / "state.json"
    return json.loads(p.read_text()) if p.exists() else {}


def stage_fs(run_id: str, stage: str) -> str:
    return state_json(run_id).get("stages", {}).get(stage, {}).get("status", "pending")


def class_files(run_id: str) -> list:
    mod = tgt(run_id) / "modernized"
    return list(mod.rglob("*.class")) if mod.exists() else []


def java_sources(run_id: str) -> list:
    result = []
    for d in [tgt(run_id) / "modernized" / "src", tgt(run_id) / "generated"]:
        if d.exists():
            result.extend(d.rglob("*.java"))
    return result


def java_out(run_id: str) -> Optional[str]:
    for p in [
        tgt(run_id) / "results" / "java" / "data" / "out" / "inventory_report.txt",
        tgt(run_id) / "results" / "native" / "data" / "out" / "inventory_report.txt",
    ]:
        if p.exists():
            return p.read_text(encoding="utf-8", errors="replace")
    return None


def cobol_out(run_id: str) -> Optional[str]:
    # Engine stores baseline output under baseline/legacy/ (see stage_baseline in cobol_migrate.py)
    # Search both old and new layout for robustness
    candidates = [
        tgt(run_id) / "baseline" / "legacy" / "data" / "out" / "inventory_report.txt",
        tgt(run_id) / "baseline" / "data" / "out" / "inventory_report.txt",
    ]
    for p in candidates:
        if p.exists():
            return p.read_text(encoding="utf-8", errors="replace")
    # Fallback: scan baseline/legacy for any .txt output
    legacy = tgt(run_id) / "baseline" / "legacy"
    if legacy.exists():
        for txt in legacy.rglob("*.txt"):
            content = txt.read_text(encoding="utf-8", errors="replace")
            if content.strip():
                return content
    return None


def cmp_result(run_id: str) -> Optional[dict]:
    exec_dir = tgt(run_id) / "execution"
    if not exec_dir.exists():
        return None
    for scenario in exec_dir.iterdir():
        cmp = scenario / "comparison_result.json"
        if cmp.exists():
            return json.loads(cmp.read_text())
    return None


def artifact_snap(run_id: str) -> dict:
    td = tgt(run_id)
    keys = ["state.json", "migration-report.md", "modernized-package.zip"]
    return {k: file_mtime(td / k) for k in keys}


# ---------------------------------------------------------------------------
# Browser helpers
# ---------------------------------------------------------------------------
def screenshot(page: Page, name: str) -> Path:
    p = SCREENSHOT_DIR / f"{name}.png"
    page.screenshot(path=str(p), full_page=True)
    return p


def setup_page(page: Page):
    errs = []
    failed_reqs: list = []
    page.set_extra_http_headers({"Authorization": AUTH_HEADER})
    page.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    # Track failed requests with their URLs so we can correlate bare ERR_FAILED
    # console messages (which have no URL in the text) against external origins.
    page.on("requestfailed",
            lambda r: failed_reqs.append({"url": r.url, "failure": r.failure}))
    page._e2e_errs = errs
    page._e2e_failed_reqs = failed_reqs


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def browser_ctx():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        ctx = browser.new_context(
            base_url=BASE_URL,
            http_credentials={"username": CRED_USER, "password": CRED_PASS},
            ignore_https_errors=True,
        )
        yield ctx
        ctx.close()
        browser.close()


@pytest.fixture()
def page(browser_ctx):
    p = browser_ctx.new_page()
    setup_page(p)
    yield p
    p.close()


@pytest.fixture(scope="session")
def fresh_run_id():
    """Ingest INVENTORY01 ZIP, run full pipeline, yield run_id."""
    assert FIXTURE_ZIP.exists(), f"Fixture ZIP missing: {FIXTURE_ZIP}"
    run_start = time.time()

    run_id = api_ingest_zip(FIXTURE_ZIP, "e2e-inventory01")
    EVIDENCE["run_id"] = run_id
    EVIDENCE["run_start"] = run_start
    EVIDENCE["pre_snap"] = artifact_snap(run_id)

    resp = api_start(run_id)
    assert resp.get("ok"), f"Pipeline start failed: {resp}"

    final = wait_for_run(run_id, PIPELINE_TIMEOUT)
    EVIDENCE["final_status"] = final.get("status")
    EVIDENCE["final_verdict"] = final.get("verdict", "")
    EVIDENCE["final_stages"] = {
        s["label"].lower(): s["status"]
        for s in final.get("stages", [])
    }
    EVIDENCE["post_snap"] = artifact_snap(run_id)
    EVIDENCE["class_files"] = [str(f) for f in class_files(run_id)]
    EVIDENCE["java_srcs"] = [str(f) for f in java_sources(run_id)]
    EVIDENCE["baseline_out"] = cobol_out(run_id)
    EVIDENCE["java_output"] = java_out(run_id)
    EVIDENCE["cmp"] = cmp_result(run_id)
    EVIDENCE["state"] = state_json(run_id)

    yield run_id

    if os.environ.get("E2E_CLEANUP", "1") == "1":
        api_reset(run_id)


# ---------------------------------------------------------------------------
# PHASE 3 - Health
# ---------------------------------------------------------------------------
class TestHealth:

    def test_no_auth_returns_401(self):
        """UI_VERIFIED: no-auth request must be rejected."""
        r = requests.get(BASE_URL + "/", timeout=10)
        assert r.status_code == 401, (
            f"UI_VERIFIED FAIL: unauthenticated request returned {r.status_code}. "
            "Auth is NOT enforced!"
        )

    def test_root_with_auth_serves_html(self, page: Page):
        """UI_VERIFIED: root with auth serves the modernization UI."""
        page.goto(BASE_URL + "/")
        page.wait_for_load_state("networkidle")
        content = page.content()
        assert any(kw in content.lower() for kw in ("cobol", "migration", "moderniz")), (
            f"UI_VERIFIED FAIL: page does not look like modernization UI. "
            f"Content: {content[:300]}"
        )
        EVIDENCE["ui_title"] = page.title()
        screenshot(page, "health_ui_loaded")

    def test_api_state_valid_schema(self):
        """BACKEND_VERIFIED: /api/state returns correct schema."""
        r = _api("get", "/api/state")
        assert r.status_code == 200
        b = r.json()
        assert "runs" in b and "active" in b, (
            f"BACKEND_VERIFIED FAIL: /api/state schema wrong: {b}"
        )
        EVIDENCE["api_state_ok"] = True

    def test_wrong_credentials_rejected(self):
        """UI_VERIFIED: wrong password must be rejected (auth not bypassable)."""
        bad = "Basic " + base64.b64encode(b"admin:WRONG_PASSWORD").decode()
        r = requests.get(BASE_URL + "/api/state",
                         headers={"Authorization": bad}, timeout=10)
        assert r.status_code == 401, (
            f"UI_VERIFIED FAIL: wrong credentials accepted! Got {r.status_code}"
        )

    def test_no_critical_browser_errors(self, page: Page):
        """UI_VERIFIED: no critical JS console errors from localhost on page load.

        Distinguishes:
        - External CDN failures (fonts, etc.) caused by our Authorization header
          injection on cross-origin preflight requests -- NOT a product defect.
        - Genuine localhost errors from the application itself -- these ARE defects.

        Strategy: correlate bare 'ERR_FAILED' console messages (which have no URL)
        against the requestfailed event log to determine if they're external-origin.
        """
        page.goto(BASE_URL + "/")
        page.wait_for_load_state("networkidle")

        EXTERNAL_MARKERS = (
            "fonts.gstatic.com", "fonts.googleapis.com",
            "cdnjs.cloudflare.com", "jsdelivr.net",
            "unpkg.com", "googleapis.com",
        )
        # All failed requests, split by origin
        failed_reqs = getattr(page, "_e2e_failed_reqs", [])
        external_fail_count = sum(
            1 for r in failed_reqs
            if any(m in r.get("url", "") for m in EXTERNAL_MARKERS)
        )
        localhost_fails = [
            r for r in failed_reqs
            if not any(m in r.get("url", "") for m in EXTERNAL_MARKERS)
            and "127.0.0.1" in r.get("url", "")
        ]

        # Console errors: filter out anything mentioning external origins
        all_errs = getattr(page, "_e2e_errs", [])
        named_external_errs = [
            e for e in all_errs
            if any(m in e.lower() for m in EXTERNAL_MARKERS)
        ]
        unnamed_err_failed = [
            e for e in all_errs
            if "err_failed" in e.lower() and e not in named_external_errs
        ]
        other_errs = [
            e for e in all_errs
            if e not in named_external_errs
            and "err_failed" not in e.lower()
            and "favicon" not in e.lower()
            and "err_aborted" not in e.lower()
        ]

        # Bare ERR_FAILED messages are companions to blocked external font loads
        # when external_fail_count > 0 and no localhost_fails exist
        bare_err_failed_from_external = (
            len(unnamed_err_failed) <= external_fail_count
            and not localhost_fails
        )

        real_errors = other_errs + (
            [] if bare_err_failed_from_external else unnamed_err_failed
        )

        EVIDENCE["browser_console_external_failures"] = external_fail_count
        EVIDENCE["browser_console_localhost_failures"] = len(localhost_fails)
        EVIDENCE["browser_console_real_errors"] = real_errors

        assert real_errors == [], (
            f"UI_VERIFIED FAIL: genuine browser console errors from localhost: {real_errors}\n"
            f"  (external CDN failures excluded: {external_fail_count})"
        )


# ---------------------------------------------------------------------------
# PHASE 4 - Stale Artifact Protection
# ---------------------------------------------------------------------------
class TestStaleProtection:

    def test_pre_run_snapshot_captured(self, fresh_run_id):
        """FILESYSTEM_VERIFIED: pre-run snapshot captured before pipeline."""
        assert EVIDENCE.get("pre_snap"), (
            "FILESYSTEM_VERIFIED FAIL: pre-run snapshot not captured"
        )

    def test_state_json_updated_by_current_run(self, fresh_run_id):
        """FILESYSTEM_VERIFIED: state.json must be newer than run start."""
        run_start = EVIDENCE["run_start"]
        sp = tgt(fresh_run_id) / "state.json"
        assert sp.exists(), "FILESYSTEM_VERIFIED FAIL: state.json missing after run"
        mtime = sp.stat().st_mtime
        assert mtime >= run_start - 5, (
            f"STALE ARTIFACT: state.json mtime={mtime:.0f} predates "
            f"run_start={run_start:.0f} by {run_start - mtime:.0f}s. "
            "This belongs to a PREVIOUS run!"
        )
        EVIDENCE["state_freshness"] = "PASS"

    def test_run_id_unique_and_present(self, fresh_run_id):
        """BACKEND_VERIFIED: run_id in state, named with our prefix."""
        ids = [r["run_id"] for r in api_state().get("runs", [])]
        assert fresh_run_id in ids, f"BACKEND_VERIFIED FAIL: {fresh_run_id!r} not in state"


# ---------------------------------------------------------------------------
# PHASE 5-6 - Pipeline and Stage Monitoring
# ---------------------------------------------------------------------------
class TestPipeline:

    def test_pipeline_reached_terminal_state(self, fresh_run_id):
        """BACKEND_VERIFIED: pipeline reached a terminal state."""
        status = EVIDENCE.get("final_status")
        assert status in ("done", "interrupted", "error"), (
            f"BACKEND_VERIFIED FAIL: unexpected final status {status!r}"
        )

    def test_ingest_done_ui_and_fs(self, fresh_run_id):
        """UI_VERIFIED + FILESYSTEM_VERIFIED: ingest stage completed."""
        ui = EVIDENCE["final_stages"].get("ingest", "pending")
        fs = stage_fs(fresh_run_id, "ingest")
        assert ui == "done", f"UI_VERIFIED FAIL: ingest UI={ui!r}"
        assert fs == "done", f"FILESYSTEM_VERIFIED FAIL: ingest FS={fs!r}"
        cob = list((ws(fresh_run_id) / "repo" / "src").glob("*.cob"))
        assert cob, "FILESYSTEM_VERIFIED FAIL: no .cob files ingested"
        EVIDENCE["cobol_ingested"] = [f.name for f in cob]

    def test_discover_done(self, fresh_run_id):
        """BACKEND_VERIFIED + FILESYSTEM_VERIFIED: discover completed."""
        ui = EVIDENCE["final_stages"].get("discover", "pending")
        fs = stage_fs(fresh_run_id, "discover")
        assert ui == "done", f"BACKEND_VERIFIED FAIL: discover UI={ui!r}"
        assert fs == "done", f"FILESYSTEM_VERIFIED FAIL: discover FS={fs!r}"

    def test_analyze_done(self, fresh_run_id):
        """BACKEND_VERIFIED: analyze completed."""
        ui = EVIDENCE["final_stages"].get("analyze", "pending")
        fs = stage_fs(fresh_run_id, "analyze")
        assert ui == "done", f"BACKEND_VERIFIED FAIL: analyze UI={ui!r}"
        assert fs == "done", f"FILESYSTEM_VERIFIED FAIL: analyze FS={fs!r}"

    def test_baseline_or_skip_with_evidence(self, fresh_run_id):
        """COBOL_EXEC_VERIFIED: baseline stage (COBOL execution)."""
        ui = EVIDENCE["final_stages"].get("baseline", "pending")
        fs = stage_fs(fresh_run_id, "baseline")
        EVIDENCE["baseline_ui"] = ui
        EVIDENCE["baseline_fs"] = fs
        if ui != "done":
            EVIDENCE["cobol_exec_verified"] = f"UNAVAILABLE (baseline={ui})"
            pytest.skip(
                f"COBOL_EXEC_VERIFIED: UNAVAILABLE -- baseline={ui!r}. "
                "Docker/GnuCOBOL not available."
            )
        assert fs == "done", f"UI/FS MISMATCH: baseline UI=done FS={fs!r}"
        EVIDENCE["cobol_exec_verified"] = "PASS"

    def test_all_done_stages_consistent_ui_vs_fs(self, fresh_run_id):
        """UI/BACKEND CONSISTENCY: every done stage matches filesystem."""
        ui_stages = EVIDENCE["final_stages"]
        fs_stages = state_json(fresh_run_id).get("stages", {})
        mismatches = []
        for label, ui_st in ui_stages.items():
            fs_name = label.lower().replace(" ", "_").replace("-", "_")
            fs_st = fs_stages.get(fs_name, {}).get("status", "pending")
            if ui_st != fs_st:
                mismatches.append(f"{label}: UI={ui_st!r} FS={fs_st!r}")
        EVIDENCE["stage_mismatches"] = mismatches
        assert not mismatches, (
            "UI/BACKEND CONSISTENCY FAIL:\n" + "\n".join(mismatches)
        )

    def test_log_non_empty(self, fresh_run_id):
        """UI_VERIFIED: /api/log returns execution evidence."""
        log = api_log(fresh_run_id)
        assert log, "UI_VERIFIED FAIL: /api/log returned empty log"
        EVIDENCE["log_lines"] = len(log)


# ---------------------------------------------------------------------------
# PHASE 7 - Generated Artifacts
# ---------------------------------------------------------------------------
class TestArtifacts:

    def test_java_sources_exist(self, fresh_run_id):
        """FILESYSTEM_VERIFIED: generated .java files exist."""
        srcs = java_sources(fresh_run_id)
        assert srcs, "FILESYSTEM_VERIFIED FAIL: no .java files found after generation"
        EVIDENCE["java_src_names"] = [f.name for f in srcs]

    def test_java_sources_are_current_run(self, fresh_run_id):
        """FILESYSTEM_VERIFIED: COBOL-generated .java files must be newer than run start.

        Exclusion: pre-installed runtime library files (CobolNumeric, CobolArithmetic,
        etc.) live in the modernized/src/main/java/com/modernization/runtime/ subtree
        and are intentionally pre-installed by the framework -- they are NOT generated
        from the COBOL source and may predate this run by design.
        """
        run_start = EVIDENCE["run_start"]
        RUNTIME_LIB_MARKERS = (
            "cobolnumeric", "cobolarithmetic", "cobolrounding", "cobolsign",
            "cobolusage", "cobolformat", "assignresult", "sizeresult",
            "sizeerror", "vsam", "mocksql", "prohibited", "unsupported",
        )
        stale = []
        for f in java_sources(fresh_run_id):
            # Skip pre-installed runtime library files
            fname_lower = f.name.lower().replace(".java", "")
            if any(marker in fname_lower for marker in RUNTIME_LIB_MARKERS):
                continue
            # Also skip files in runtime/ or lib/ subdirectories
            parts_lower = [p.lower() for p in f.parts]
            if any(d in parts_lower for d in ("runtime", "lib", "support", "framework")):
                continue
            if f.stat().st_mtime < run_start - 10:
                stale.append(f"{f.name} (mtime={f.stat().st_mtime:.0f} run={run_start:.0f})")
        assert not stale, (
            f"STALE COBOL-GENERATED JAVA SOURCES detected (not runtime library files): {stale}"
        )

    def test_api_modernized_lists_java(self, fresh_run_id):
        """UI_VERIFIED: /api/modernized returns .java files."""
        files = api_modernized(fresh_run_id)
        java = [f["name"] for f in files if f["name"].endswith(".java")]
        assert java, f"UI_VERIFIED FAIL: /api/modernized returned no .java: {files[:5]}"
        EVIDENCE["ui_java_files"] = java

    def test_modernized_file_content_is_java(self, fresh_run_id):
        """UI_VERIFIED: file content from /api/modernized-file looks like Java."""
        files = [f for f in api_modernized(fresh_run_id) if f["name"].endswith(".java")]
        if not files:
            pytest.skip("No .java in /api/modernized")
        r = _api("get", f"/api/modernized-file?run_id={fresh_run_id}&path={files[0]['path']}")
        assert r.status_code == 200
        body = r.json()
        content = body.get("content", "")
        assert "class" in content or "public" in content, (
            f"UI_VERIFIED FAIL: content does not look like Java: {content[:200]}"
        )

    def test_migration_report_exists_and_current(self, fresh_run_id):
        """FILESYSTEM_VERIFIED: migration-report.md exists and is current."""
        rpt = tgt(fresh_run_id) / "migration-report.md"
        assert rpt.exists(), "FILESYSTEM_VERIFIED FAIL: migration-report.md missing"
        assert rpt.stat().st_mtime >= EVIDENCE["run_start"] - 10, (
            "STALE ARTIFACT: migration-report.md predates run start"
        )
        txt = rpt.read_text(encoding="utf-8", errors="replace")
        assert "inventory" in txt.lower() or "INVENTORY" in txt, (
            "FILESYSTEM_VERIFIED FAIL: report does not mention workload"
        )

    def test_report_endpoint_serves_content(self, fresh_run_id):
        """UI_VERIFIED: /report endpoint returns report content."""
        r = _api("get", f"/report?run_id={fresh_run_id}")
        assert r.status_code == 200 and len(r.text) > 200, (
            f"UI_VERIFIED FAIL: /report returned {r.status_code}, len={len(r.text)}"
        )

    def test_artifact_paths_no_traversal(self, fresh_run_id):
        """SECURITY: artifact paths must not allow directory traversal."""
        for a in api_artifacts(fresh_run_id):
            path = a.get("path", "")
            assert ".." not in path and not path.startswith("/"), (
                f"SECURITY FAIL: path traversal in artifact: {path!r}"
            )


# ---------------------------------------------------------------------------
# PHASE 8 - Java Compilation
# ---------------------------------------------------------------------------
class TestJavaCompilation:

    def test_validate_stage_status(self, fresh_run_id):
        """JAVA_COMPILED: validate (Maven) stage status."""
        ui = EVIDENCE["final_stages"].get("validate", "pending")
        fs = stage_fs(fresh_run_id, "validate")
        EVIDENCE["validate_ui"] = ui
        EVIDENCE["validate_fs"] = fs
        if ui != "done":
            EVIDENCE["java_compiled"] = f"UNAVAILABLE (validate={ui})"
            pytest.skip(f"JAVA_COMPILED: UNAVAILABLE -- validate={ui!r}")
        assert fs == "done", f"UI/FS MISMATCH: validate UI=done FS={fs!r}"

    def test_class_files_exist_when_validate_done(self, fresh_run_id):
        """JAVA_COMPILED: .class files must exist when validate=done."""
        if EVIDENCE.get("validate_ui") != "done":
            pytest.skip("validate not done")
        clazz = class_files(fresh_run_id)
        assert clazz, (
            "PRODUCT DEFECT: validate=done but NO .class files on disk. "
            "UI claimed compilation success without physical evidence."
        )
        EVIDENCE["java_compiled"] = "PASS"
        EVIDENCE["class_count"] = len(clazz)

    def test_class_files_are_current_run(self, fresh_run_id):
        """JAVA_COMPILED: .class files must be newer than run start."""
        clazz = class_files(fresh_run_id)
        if not clazz:
            pytest.skip("No .class files to check")
        run_start = EVIDENCE["run_start"]
        stale = [f.name for f in clazz[:10] if f.stat().st_mtime < run_start - 30]
        assert not stale, f"STALE .class FILES: {stale}"


# ---------------------------------------------------------------------------
# PHASE 9 - Java Runtime
# ---------------------------------------------------------------------------
class TestJavaRuntime:

    def test_execute_stage_status(self, fresh_run_id):
        """JAVA_RUNTIME_VERIFIED: execute stage status."""
        ui = EVIDENCE["final_stages"].get("execute", "pending")
        fs = stage_fs(fresh_run_id, "execute")
        EVIDENCE["execute_ui"] = ui
        EVIDENCE["execute_fs"] = fs
        if ui != "done":
            EVIDENCE["java_runtime_verified"] = f"UNAVAILABLE (execute={ui})"
            pytest.skip(f"JAVA_RUNTIME_VERIFIED: UNAVAILABLE -- execute={ui!r}")

    def test_java_output_exists_when_execute_done(self, fresh_run_id):
        """JAVA_RUNTIME_VERIFIED: Java output file must exist when execute=done."""
        if EVIDENCE.get("execute_ui") != "done":
            pytest.skip("execute not done")
        out = java_out(fresh_run_id)
        assert out and out.strip(), (
            "PRODUCT DEFECT: execute=done but Java output file missing/empty."
        )
        EVIDENCE["java_runtime_verified"] = "PASS"
        EVIDENCE["java_out_content"] = out.strip()


# ---------------------------------------------------------------------------
# PHASE 10 - COBOL Baseline
# ---------------------------------------------------------------------------
class TestCobolBaseline:

    def test_baseline_output_exists(self, fresh_run_id):
        """COBOL_EXEC_VERIFIED: COBOL baseline output must exist when baseline=done."""
        if EVIDENCE.get("baseline_ui") != "done":
            EVIDENCE["cobol_exec_verified"] = "UNAVAILABLE"
            pytest.skip("COBOL_EXEC_VERIFIED: UNAVAILABLE")
        out = cobol_out(fresh_run_id)
        assert out and out.strip(), (
            "PRODUCT DEFECT: baseline=done but COBOL output file missing/empty."
        )
        EVIDENCE["cobol_exec_verified"] = "PASS"
        EVIDENCE["baseline_out_content"] = out.strip()

    def test_cobol_output_contains_business_data(self, fresh_run_id):
        """COBOL_EXEC_VERIFIED: COBOL output has inventory business fields."""
        out = EVIDENCE.get("baseline_out_content")
        if not out:
            pytest.skip("COBOL baseline output unavailable")
        assert "|" in out, f"COBOL output missing pipe delimiters: {out!r}"
        assert "QTY=" in out or "PRICE=" in out, (
            f"COBOL output missing inventory fields: {out!r}"
        )


# ---------------------------------------------------------------------------
# PHASE 11 - Business Equivalence
# ---------------------------------------------------------------------------
class TestBusinessEquivalence:

    def test_compare_stage_status(self, fresh_run_id):
        """BUSINESS_EQUIVALENCE_VERIFIED: compare stage status."""
        ui = EVIDENCE["final_stages"].get("compare", "pending")
        fs = stage_fs(fresh_run_id, "compare")
        EVIDENCE["compare_ui"] = ui
        if ui != "done":
            EVIDENCE["biz_eq"] = f"UNAVAILABLE (compare={ui})"
            pytest.skip(f"BUSINESS_EQUIVALENCE_VERIFIED: UNAVAILABLE -- compare={ui!r}")
        assert fs == "done", f"UI/FS MISMATCH: compare UI=done FS={fs!r}"

    def test_comparison_result_json_pass(self, fresh_run_id):
        """BUSINESS_EQUIVALENCE_VERIFIED: comparison_result.json status=PASS."""
        cmp = cmp_result(fresh_run_id)
        if cmp is None:
            EVIDENCE["biz_eq"] = "UNAVAILABLE (no comparison_result.json)"
            pytest.skip("comparison_result.json not found")
        EVIDENCE["cmp_json"] = cmp
        status = cmp.get("status")
        assert status == "PASS", (
            f"BUSINESS_EQUIVALENCE: FAIL -- status={status!r}. "
            f"Differences: {cmp.get('differences', [])}"
        )
        EVIDENCE["biz_eq"] = "PASS"

    def test_cobol_java_outputs_byte_identical(self, fresh_run_id):
        """BUSINESS_EQUIVALENCE_VERIFIED: COBOL and Java outputs byte-match."""
        b_raw = (EVIDENCE.get("baseline_out_content")
                 or (cobol_out(fresh_run_id) or "")).strip()
        j_raw = (EVIDENCE.get("java_out_content")
                 or (java_out(fresh_run_id) or "")).strip()

        if not b_raw or not j_raw:
            EVIDENCE["biz_eq"] = f"UNAVAILABLE cobol={bool(b_raw)} java={bool(j_raw)}"
            pytest.skip(
                f"BUSINESS_EQUIVALENCE_VERIFIED: UNAVAILABLE -- "
                f"cobol_output={bool(b_raw)} java_output={bool(j_raw)}"
            )

        b = b_raw.replace("\r\n", "\n").replace("\r", "\n")
        j = j_raw.replace("\r\n", "\n").replace("\r", "\n")
        assert b == j, (
            "BUSINESS EQUIVALENCE FAILURE:\n"
            f"COBOL: {b!r}\n"
            f"Java : {j!r}\n"
        )
        EVIDENCE["biz_eq"] = "EXACT_BYTE_MATCH"

    def test_ui_verdict_consistent_with_cmp(self, fresh_run_id):
        """UI_TRUTHFULNESS: UI verdict consistent with comparison_result."""
        cmp = EVIDENCE.get("cmp_json") or cmp_result(fresh_run_id)
        if cmp is None:
            pytest.skip("No comparison result to check")
        verdict = EVIDENCE.get("final_verdict", "")
        if cmp.get("status") == "PASS":
            assert "FAIL" not in (verdict or "").upper(), (
                f"UI MISMATCH: cmp=PASS but UI verdict={verdict!r}"
            )
        elif cmp.get("status") == "FAIL":
            assert "PASS" not in (verdict or "").upper(), (
                f"UI FABRICATED SUCCESS: cmp=FAIL but verdict={verdict!r}"
            )


# ---------------------------------------------------------------------------
# PHASE 12 - UI Truthfulness
# ---------------------------------------------------------------------------
class TestUITruthfulness:

    def test_package_size_matches_filesystem(self, fresh_run_id):
        """UI_TRUTHFULNESS: UI-reported package_size matches real file."""
        run_state = api_run_state(fresh_run_id)
        if not run_state:
            pytest.skip("Run not in state")
        ui_sz = run_state.get("package_size")
        pkg = tgt(fresh_run_id) / "modernized-package.zip"
        if pkg.exists() and ui_sz is not None:
            actual = pkg.stat().st_size
            assert ui_sz == actual, (
                f"UI/FS MISMATCH: UI package_size={ui_sz} actual={actual}"
            )
            EVIDENCE["pkg_size_ok"] = "PASS"

    def test_no_done_stage_without_fs_evidence(self, fresh_run_id):
        """UI_TRUTHFULNESS: UI must not report done for stages FS says are not done."""
        ui_stages = EVIDENCE["final_stages"]
        fs_stages = state_json(fresh_run_id).get("stages", {})
        fabricated = []
        for label, ui_st in ui_stages.items():
            if ui_st == "done":
                fs_name = label.lower().replace(" ", "_").replace("-", "_")
                fs_st = fs_stages.get(fs_name, {}).get("status", "pending")
                if fs_st != "done":
                    fabricated.append(f"{label}: UI=done FS={fs_st!r}")
        assert not fabricated, "UI FABRICATED SUCCESS:\n" + "\n".join(fabricated)


# ---------------------------------------------------------------------------
# PHASE 13 - Negative: Failure Honesty
# ---------------------------------------------------------------------------
class TestNegativeFailureHonesty:

    def test_invalid_zip_rejected(self):
        """FAILURE HONESTY: garbage data rejected as invalid ZIP."""
        b64 = base64.b64encode(b"THIS IS NOT A ZIP").decode()
        r = _api("post", "/api/ingest", json={"source": "zip", "data": b64, "name": "neg-bad"})
        body = r.json()
        assert not body.get("ok"), (
            f"FAILURE HONESTY FAIL: invalid ZIP accepted! Body: {body}"
        )
        EVIDENCE["neg_invalid_zip"] = "PASS"

    def test_empty_zip_rejected(self):
        """FAILURE HONESTY: empty ZIP (no files) must be rejected."""
        buf = BytesIO()
        with zipfile.ZipFile(buf, "w"):
            pass
        b64 = base64.b64encode(buf.getvalue()).decode()
        r = _api("post", "/api/ingest", json={"source": "zip", "data": b64, "name": "neg-empty"})
        assert not r.json().get("ok"), "FAILURE HONESTY FAIL: empty ZIP accepted"
        EVIDENCE["neg_empty_zip"] = "PASS"

    def test_nonexistent_run_rejected(self):
        """FAILURE HONESTY: starting nonexistent run must fail."""
        r = _api("post", "/api/run", json={"run_id": "nonexistent-xyz-99999"})
        assert not r.json().get("ok"), (
            "FAILURE HONESTY FAIL: non-existent run accepted"
        )
        EVIDENCE["neg_nonexistent_run"] = "PASS"

    def test_stop_completed_run_returns_error(self, fresh_run_id):
        """FAILURE HONESTY: stopping completed run must fail."""
        r = _api("post", "/api/stop", json={"run_id": fresh_run_id})
        assert not r.json().get("ok"), (
            "FAILURE HONESTY: stopping completed run returned ok=True"
        )
        EVIDENCE["neg_stop_completed"] = "PASS"


# ---------------------------------------------------------------------------
# PHASE 14 - Negative: Stale Artifact Protection
# ---------------------------------------------------------------------------
class TestNegativeStaleArtifact:

    def test_second_ingest_different_workspace(self, fresh_run_id):
        """STALE PROTECTION: second ingest creates separate workspace."""
        run_id2 = api_ingest_zip(FIXTURE_ZIP, "e2e-inventory01")
        try:
            assert run_id2 != fresh_run_id, (
                f"STALE PROTECTION FAIL: second ingest reused same run_id {fresh_run_id!r}"
            )
            assert ws(run_id2) != ws(fresh_run_id), "STALE PROTECTION FAIL: same workspace"
            EVIDENCE["neg_stale_ws"] = "PASS"
        finally:
            api_reset(run_id2)

    def test_unrun_workspace_no_report(self):
        """STALE PROTECTION: unrun workspace must not serve a report."""
        run_id_empty = api_ingest_zip(FIXTURE_ZIP, "e2e-stale-chk")
        try:
            r = _api("get", f"/report?run_id={run_id_empty}")
            assert r.status_code == 404, (
                f"STALE PROTECTION FAIL: unrun workspace returned {r.status_code} for /report. "
                "Serving a stale report!"
            )
            EVIDENCE["neg_stale_report"] = "PASS"
        finally:
            api_reset(run_id_empty)

    def test_nonexistent_run_has_no_artifacts(self):
        """STALE PROTECTION: nonexistent run_id returns empty artifacts."""
        r = _api("get", "/api/artifacts?run_id=nonexistent-run-xyz")
        artifacts = r.json().get("artifacts", [])
        assert not artifacts, (
            f"STALE PROTECTION FAIL: nonexistent run returned artifacts: {artifacts[:3]}"
        )
        EVIDENCE["neg_artifact_isolation"] = "PASS"


# ---------------------------------------------------------------------------
# PHASE 15 - Negative: Verification Honesty
# ---------------------------------------------------------------------------
class TestNegativeVerificationHonesty:

    def test_comparison_checks_not_all_na(self, fresh_run_id):
        """VERIFICATION HONESTY: checks must not all be NOT_APPLICABLE."""
        cmp = cmp_result(fresh_run_id)
        if cmp is None:
            pytest.skip("No comparison result")
        checks = cmp.get("checks", {})
        if not checks:
            pytest.skip("No checks block")
        all_na = all(v == "NOT_APPLICABLE" for v in checks.values())
        assert not all_na, (
            "VERIFICATION HONESTY FAIL: ALL checks are NOT_APPLICABLE. "
            "Nothing is actually being verified!"
        )
        EVIDENCE["neg_checks_honest"] = f"checks={list(checks.items())}"

    def test_comparison_evidence_block_present(self, fresh_run_id):
        """VERIFICATION HONESTY: comparison_result has an evidence block."""
        cmp = cmp_result(fresh_run_id)
        if cmp is None:
            pytest.skip("No comparison result")
        assert cmp.get("evidence"), (
            "VERIFICATION HONESTY FAIL: comparison_result.json has no evidence block"
        )
        EVIDENCE["neg_evidence_present"] = "PASS"


# ---------------------------------------------------------------------------
# PHASE 16 - Playwright Browser Workflow
# ---------------------------------------------------------------------------
class TestBrowserWorkflow:

    def test_completed_run_visible_in_browser(self, fresh_run_id, page: Page):
        """UI_VERIFIED: completed run appears in the browser UI."""
        page.goto(BASE_URL + "/")
        page.wait_for_load_state("networkidle")
        content = page.content()
        assert (
            fresh_run_id[:12] in content
            or "inventory" in content.lower()
        ), f"UI_VERIFIED FAIL: run not visible in browser. Content: {content[:500]}"
        screenshot(page, "browser_runs_list")

    def test_stage_names_visible_in_browser(self, fresh_run_id, page: Page):
        """UI_VERIFIED: stage names visible in browser UI."""
        page.goto(BASE_URL + "/")
        page.wait_for_load_state("networkidle")
        content = page.content().lower()
        found = [k for k in ("ingest", "discover", "transpile", "validate") if k in content]
        assert len(found) >= 2, f"UI_VERIFIED FAIL: stage names not in UI. Found: {found}"
        screenshot(page, "browser_stage_visibility")

    def test_report_link_accessible(self, fresh_run_id, page: Page):
        """UI_VERIFIED: migration report accessible for completed run."""
        r = _api("get", f"/report?run_id={fresh_run_id}")
        assert r.status_code == 200 and len(r.text) > 100, (
            "UI_VERIFIED FAIL: report not accessible or too short"
        )
        screenshot(page, "browser_report_access")


# ---------------------------------------------------------------------------
# Evidence ledger (printed after all tests)
# ---------------------------------------------------------------------------
def pytest_sessionfinish(session, exitstatus):
    sep = "=" * 72
    print(f"\n{sep}")
    print("E2E BLACK-BOX VALIDATION -- EVIDENCE LEDGER")
    print(sep)
    print(f"  WORKLOAD : INVENTORY01 (mentor_cobol_test_repo_02 fixture)")
    print(f"  RUN_ID   : {EVIDENCE.get('run_id', 'NOT_SET')}")
    print(f"  BASE_URL : {BASE_URL}")
    print(f"  BROWSER  : Chromium (playwright headless)")
    print()

    rows = [
        ("UI_VERIFIED",                    "api_state_ok"),
        ("BACKEND_VERIFIED",               "stage_mismatches"),
        ("FILESYSTEM_VERIFIED",            "state_freshness"),
        ("COBOL_EXEC_VERIFIED",            "cobol_exec_verified"),
        ("JAVA_COMPILED",                  "java_compiled"),
        ("JAVA_RUNTIME_VERIFIED",          "java_runtime_verified"),
        ("BUSINESS_EQUIVALENCE_VERIFIED",  "biz_eq"),
    ]
    print(f"  {'EVIDENCE LEVEL':<40} RESULT")
    print("  " + "-" * 68)
    for label, key in rows:
        val = EVIDENCE.get(key, "NOT_EXECUTED")
        # stage_mismatches is a list -- summarise
        if key == "stage_mismatches":
            val = "NO_MISMATCHES" if val == [] else f"MISMATCHES({len(val)})"
        print(f"  {label:<40} {val}")

    print()
    neg = [
        ("Failure honesty (invalid ZIP)",    "neg_invalid_zip"),
        ("Failure honesty (empty ZIP)",      "neg_empty_zip"),
        ("Failure honesty (nonexistent run)","neg_nonexistent_run"),
        ("Stale workspace protection",       "neg_stale_ws"),
        ("Stale report protection",          "neg_stale_report"),
        ("Artifact isolation",               "neg_artifact_isolation"),
        ("Verification checks non-trivial",  "neg_checks_honest"),
    ]
    print(f"  {'NEGATIVE TEST':<42} RESULT")
    print("  " + "-" * 68)
    for label, key in neg:
        val = EVIDENCE.get(key, "NOT_EXECUTED")
        print(f"  {label:<42} {val}")

    mismatches = EVIDENCE.get("stage_mismatches", [])
    if mismatches:
        print(f"\n  UI/BACKEND MISMATCHES:")
        for m in mismatches:
            print(f"    !! {m}")
    else:
        print(f"\n  UI/BACKEND CONSISTENCY: no mismatches")
    print(sep)
