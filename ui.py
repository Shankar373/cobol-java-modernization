#!/usr/bin/env python3
"""Simple stdlib web UI for the COBOL -> Java migration pipeline.

Serves a single-page UI on http://127.0.0.1:8787 that drives cobol_migrate.py:

  * Step 0  - INPUT: accept a ZIP of the repository OR a git URL. Nothing on the
              host is changed at ingest time; the source is copied into an
              isolated workspace (<project>/workspace/<run_id>) before the
              pipeline runs.
  * Steps 1..11 - the migration workflow, each stage checkpointed
              (state.json) with resume / restart-from / reset controls.
  * Downloads - migration report and checkpoint archive.

No third-party dependencies. Run:  python ui.py [--port 8787]
"""

import argparse
import base64
import io
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib.parse
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cobol_migrate as engine

ROOT = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.join(ROOT, "workspace")
CFG = engine.load_json(os.path.join(ROOT, "migration_config.json"), {}) or {}
GIT = shutil.which("git")

POT = {"ip": "127.0.0.1"}
RUNS = {}               # run_id -> dict
LOCK = threading.Lock()  # guards starting runs (one active run at a time)

def secure_resolve_path(base_dir, relative_path):
    norm_rel = relative_path.replace("\\", "/").strip("/")
    if norm_rel.startswith("/") or (len(norm_rel) > 1 and norm_rel[1] == ":"):
        return None
    real_base = os.path.realpath(base_dir)
    joined_path = os.path.join(real_base, norm_rel)
    real_target = os.path.realpath(joined_path)
    if not real_target.startswith(real_base + os.sep) and real_target != real_base:
        return None
    if not os.path.exists(real_target) or os.path.isdir(real_target):
        return None
    return real_target


def get_run_verdict(run):
    try:
        p = engine.Pipeline(run["repo"], run["out"])
        return p._compute_verdict()
    except Exception:
        return "UNVERIFIED"


STEP_LABELS = [
    ("Ingest",      "Upload repository • fingerprint source • establish baseline"),
    ("Discover",    "Detect technologies • programs • copybooks • dependencies"),
    ("Analyze",     "Build architecture • call graph • data model • business rules"),
    ("Baseline",    "Execute legacy application • capture golden-master behavior"),
    ("Transpile",   "COBOL → Java using real cobj"),
    ("Collect",     "Gather generated Java • detect stubs and gaps"),
    ("Generate",    "Assemble executable transpiled Java target"),
    ("Execute",     "Run transpiled Java • capture outputs"),
    ("Compare",     "Legacy baseline vs transpiled Java • behavioral parity"),
    ("Refactor",    "Native Spring Boot • Spring Batch • JPA • REST"),
    ("Validate",    "Build • tests • native Java vs legacy validation"),
    ("Report",      "Migration results • traceability • risks • audit"),
    ("Package",     "Create final deployable modernized application"),
]


def run_id_of(ws):
    return os.path.basename(ws)


def restore_workspaces():
    os.makedirs(WORKSPACE, exist_ok=True)
    for name in sorted(os.listdir(WORKSPACE)):
        ws = os.path.join(WORKSPACE, name)
        if not os.path.isdir(ws):
            continue
        state = engine.load_json(os.path.join(ws, "target", "state.json"), {})
        st = state.get("stages", {})
        last = None
        for idx, (name2, _) in enumerate(STEP_LABELS):
            sname = engine.STAGES[idx]
            status = st.get(sname, {}).get("status")
            if status == "done":
                last = idx
        if last is None:
            continue
        status = "done" if st.get("package", {}).get("status") == "done" else "interrupted"
        # Restore name/source from persisted meta.json if available
        meta = engine.load_json(os.path.join(ws, "meta.json"), {})
        RUNS[name] = {
            "run_id": name, "status": status,
            "repo": os.path.join(ws, "repo"), "out": os.path.join(ws, "target"),
            "last_stage": last, "log": [],
            "source": meta.get("source"),
            "name": meta.get("name", name),
            "events": [],
            "seq": 0,
        }


def emit_run_event(run, event_type, message="", stage=None, status=None, **kwargs):
    run.setdefault("events", [])
    run.setdefault("seq", 0)
    run["seq"] += 1
    event = {
        "run_id": run["run_id"],
        "seq": run["seq"],
        "timestamp": engine.now_iso(),
        "type": event_type,
        "stage": stage,
        "message": message,
        "status": status,
        **kwargs
    }
    run["events"].append(event)


def start_run(run_id, restart_from):
    run = RUNS.get(run_id)
    if not run:
        return False, "unknown run"
    if run.get("status") == "running":
        return False, "run already in progress"

    if restart_from is not None and restart_from > 0:
        divider_msg = (
            f"\n=== RESTARTING FROM STAGE {restart_from} ({engine.STAGES[restart_from]}) ===\n"
            f"Timestamp: {engine.now_iso()}\n"
            f"Restart Stage: {engine.STAGES[restart_from]}\n"
            f"Reason: User requested rerun\n"
        )
        run["log"].append(divider_msg)
        emit_run_event(run, "log", message=divider_msg, restart_boundary=True)

    def sink(msg):
        run["log"].append(msg)
        run["log"] = run["log"][-400:]
        emit_run_event(run, "log", message=msg)

    def event_sink(event_type, **kwargs):
        emit_run_event(run, event_type, **kwargs)

    def worker():
        with LOCK:
            run["status"] = "running"
            run["started_at"] = engine.now_iso()
            engine.LOG_SINK = sink
            engine.EVENT_SINK = event_sink
            
            p = None
            try:
                run_cfg_path = os.path.join(run["repo"], "migration_config.json")
                if os.path.exists(run_cfg_path):
                    run_cfg = engine.load_json(run_cfg_path, {})
                else:
                    run_cfg = {
                        "execution": CFG.get("execution", {}),
                        "compare": {
                            "output_dirs": [],
                            "modes": {},
                            "checks": []
                        }
                    }
                p = engine.Pipeline(run["repo"], run["out"], cfg=run_cfg, pull=True)
                p.run_id = run_id
                run["pipeline"] = p
                
                p.run(restart_from=restart_from)
                
                state = engine.load_json(os.path.join(run["out"], "state.json"), {})
                run["last_stage"] = 12 if state.get("stages", {}).get("package", {}).get("status") == "done" else 11
                run["verdict"] = state.get("stages", {}).get("report", {}).get("detail", "done")
                run["status"] = "done"
            except BaseException as e:
                if (p and getattr(p, "cancelled", False)) or isinstance(e, KeyboardInterrupt):
                    run["status"] = "interrupted"
                    run["error"] = "Pipeline execution cancelled by user."
                else:
                    run["error"] = f"{type(e).__name__}: {e}"
                    run["status"] = "error"
            finally:
                run.pop("pipeline", None)
                engine.LOG_SINK = None
                engine.EVENT_SINK = None
                
                for idx, (lab, _) in enumerate(STEP_LABELS):
                    st = engine.load_json(os.path.join(run["out"], "state.json"), {}).get("stages", {})
                    if st.get(engine.STAGES[idx], {}).get("status") == "done":
                        run["last_stage"] = idx
                run["finished_at"] = engine.now_iso()

    t = threading.Thread(target=worker, daemon=True)
    t.start()
    return True, "started"


def re_abs(name):
    return len(name) > 1 and name[1] == ":"  # windows drive letter


def safe_extract_zip(data, dest):
    zf = zipfile.ZipFile(io.BytesIO(data))
    names = []
    for info in zf.infolist():
        name = info.filename.replace("\\", "/")
        parts = name.split("/")
        if not parts[-1] or info.is_dir():
            continue
        if any(p in ("..", ".") for p in parts) or name.startswith("/") or re_abs(name):
            continue
        names.append(info)

    # Detect common top-level directory prefix (if all files share it)
    common_prefix = None
    if names:
        first_parts = names[0].filename.replace("\\", "/").split("/")
        if len(first_parts) > 1:
            possible_prefix = first_parts[0]
            all_share = True
            for info in names:
                parts = info.filename.replace("\\", "/").split("/")
                if not parts or parts[0] != possible_prefix:
                    all_share = False
                    break
            if all_share:
                common_prefix = possible_prefix

    for info in names:
        name = info.filename.replace("\\", "/")
        strip = [p for p in name.split("/") if p not in ("", ".")]
        if common_prefix and strip and strip[0] == common_prefix:
            strip = strip[1:]
        target = os.path.join(dest, *strip)
        # Symlink guard: ensure resolved path stays within dest
        real_dest = os.path.realpath(dest)
        real_target = os.path.realpath(os.path.join(dest, *strip))
        if not real_target.startswith(real_dest + os.sep) and real_target != real_dest:
            continue  # silently skip path-traversal entries
        os.makedirs(os.path.dirname(target), exist_ok=True)
        if info.is_dir():
            os.makedirs(target, exist_ok=True)
        else:
            with zf.open(info) as src, open(target, "wb") as out:
                shutil.copyfileobj(src, out)
    return len(names)


def ingest(payload):
    source = payload.get("source")
    suffix = payload.get("name") or time.strftime("run-%Y%m%d-%H%M%S")
    run_id = re.sub(r"[^A-Za-z0-9._-]", "-", suffix)
    ws = os.path.join(WORKSPACE, run_id)
    if os.path.exists(ws):
        ini = 2
        while os.path.exists(os.path.join(WORKSPACE, f"{run_id}-{ini}")):
            ini += 1
        run_id = f"{run_id}-{ini}"
        ws = os.path.join(WORKSPACE, run_id)
    os.makedirs(ws, exist_ok=True)
    repo = os.path.join(ws, "repo")
    os.makedirs(repo, exist_ok=True)
    if source == "zip":
        try:
            data = base64.b64decode(payload.get("data", ""))
        except Exception as e:
            shutil.rmtree(ws, ignore_errors=True)
            return False, f"invalid base64 payload: {e}"
        if not data:
            shutil.rmtree(ws, ignore_errors=True)
            return False, "empty zip payload"
        try:
            n = safe_extract_zip(data, repo)
        except zipfile.BadZipFile:
            shutil.rmtree(ws, ignore_errors=True)
            return False, "not a valid zip file"
        if n == 0:
            shutil.rmtree(ws, ignore_errors=True)
            return False, "zip contained no files"
    elif source == "git":
        if not GIT:
            shutil.rmtree(ws, ignore_errors=True)
            return False, "git is not installed on this host"
        url = (payload.get("url") or "").strip()
        if not url:
            shutil.rmtree(ws, ignore_errors=True)
            return False, "missing git url"
        if url.startswith("-"):
            shutil.rmtree(ws, ignore_errors=True)
            return False, "invalid git url (cannot start with -)"
        cmd = [GIT, "clone", "--depth", "1"]
        branch = (payload.get("branch") or "").strip()
        if branch:
            if branch.startswith("-") or not re.match(r"^[a-zA-Z0-9/._\-]+$", branch):
                shutil.rmtree(ws, ignore_errors=True)
                return False, "invalid branch name"
            cmd += ["--branch", branch]
        cmd += [url, repo]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        except subprocess.TimeoutExpired:
            shutil.rmtree(ws, ignore_errors=True)
            return False, "git clone timed out after 30 seconds"
        if r.returncode != 0:
            shutil.rmtree(ws, ignore_errors=True)
            return False, "git clone failed: " + (r.stderr or r.stdout)[-300:]
    else:
        return False, "unknown source"
    RUNS[run_id] = {"run_id": run_id, "status": "ready",
                    "repo": repo, "out": os.path.join(ws, "target"),
                    "last_stage": -1, "log": [], "source": source,
                    "name": payload.get("name") or ("git: " + url if source == "git" else "zip-package"),
                    "events": [], "seq": 0}
    # Persist source + name so they survive server restarts
    engine.write_json(os.path.join(ws, "meta.json"), {
        "source": RUNS[run_id]["source"],
        "name": RUNS[run_id]["name"],
    })
    return True, run_id


# ---------------------------------------------------------------------------
class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json; charset=utf-8", binary=False):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, code=200):
        self._send(code, json.dumps(obj).encode("utf-8"))

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path in ("/", "/index.html"):
            with open(os.path.join(ROOT, "ui.html"), "rb") as fh:
                self._send(200, fh.read(), "text/html; charset=utf-8")
            return
        if u.path == "/api/state":
            self._json(build_state())
            return
        if u.path == "/api/log":
            q = urllib.parse.parse_qs(u.query)
            rid = q.get("run_id", [""])[0]
            run = RUNS.get(rid)
            self._json({"run_id": rid, "log": run["log"] if run else []})
            return
        if u.path == "/api/log-stream":
            q = urllib.parse.parse_qs(u.query)
            rid = q.get("run_id", [""])[0]
            run = RUNS.get(rid)
            if not run:
                self.send_error(404, "unknown run")
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            sent_idx = 0
            try:
                while True:
                    run_events = run.get("events", [])
                    events_len = len(run_events)
                    if sent_idx < events_len:
                        for i in range(sent_idx, events_len):
                            event = run_events[i]
                            self.wfile.write(f"data: {json.dumps(event)}\n\n".encode("utf-8"))
                        self.wfile.flush()
                        sent_idx = events_len
                    if run.get("status") in ("done", "error", "interrupted") and sent_idx >= len(run.get("events", [])):
                        self.wfile.write(b"event: end\ndata: {}\n\n")
                        self.wfile.flush()
                        break
                    time.sleep(0.2)
            except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
                pass
            return
        if u.path == "/api/artifacts":
            q = urllib.parse.parse_qs(u.query)
            rid = q.get("run_id", [""])[0]
            run = RUNS.get(rid)
            if not run:
                self._json({"ok": False, "error": "unknown run"}, 404)
                return
            
            out_dir = run["out"]
            files = []
            
            reports = [
                "migration-report.md", "migration-report.json",
                "business-rule-traceability.md", "business-rule-traceability.json",
                "transpilation-provenance.json", "pipeline_execution_manifest.json",
                "state.json", "hardcoded-value-scan.json"
            ]
            for rfile in reports:
                path = os.path.join(out_dir, rfile)
                if os.path.exists(path) and os.path.isfile(path):
                    files.append({"name": rfile, "path": rfile, "type": "report"})
                    
            gen_dir = os.path.join(out_dir, "generated")
            if os.path.exists(gen_dir) and os.path.isdir(gen_dir):
                for root, _, filenames in os.walk(gen_dir):
                    for f in filenames:
                        fullpath = os.path.join(root, f)
                        rel = os.path.relpath(fullpath, out_dir).replace("\\", "/")
                        files.append({"name": f, "path": rel, "type": "generated"})
                        
            exec_dir = os.path.join(out_dir, "execution")
            if os.path.exists(exec_dir) and os.path.isdir(exec_dir):
                for root, _, filenames in os.walk(exec_dir):
                    for f in filenames:
                        fullpath = os.path.join(root, f)
                        rel = os.path.relpath(fullpath, out_dir).replace("\\", "/")
                        files.append({"name": f, "path": rel, "type": "execution"})
                        
            mod_dir = os.path.join(out_dir, "modernized")
            if os.path.exists(mod_dir) and os.path.isdir(mod_dir):
                for root, _, filenames in os.walk(mod_dir):
                    for f in filenames:
                        if f.endswith(".class"):
                            continue
                        fullpath = os.path.join(root, f)
                        rel = os.path.relpath(fullpath, out_dir).replace("\\", "/")
                        files.append({"name": f, "path": rel, "type": "modernized"})

            self._json({"ok": True, "artifacts": files})
            return
        if u.path == "/api/artifact-content":
            q = urllib.parse.parse_qs(u.query)
            rid = q.get("run_id", [""])[0]
            name = q.get("name", [""])[0]
            run = RUNS.get(rid)
            if not run or not name:
                self._json({"ok": False, "error": "Artifact not available for this run."}, 400)
                return
            resolved = secure_resolve_path(run["out"], name)
            if not resolved:
                self._json({"ok": False, "error": "Artifact not available for this run."}, 400)
                return
            try:
                with open(resolved, "r", encoding="utf-8", errors="replace") as fh:
                    self._json({"ok": True, "content": fh.read()})
            except Exception as e:
                self._json({"ok": False, "error": f"Failed to read file: {e}"}, 500)
            return
        if u.path == "/report":
            q = urllib.parse.parse_qs(u.query)
            rid = q.get("run_id", [""])[0]
            run = RUNS.get(rid)
            if not run:
                self._send(404, b"run not found")
                return
            resolved = secure_resolve_path(run["out"], "migration-report.md")
            if not resolved:
                self._send(404, b"no report yet")
                return
            with open(resolved, "rb") as fh:
                self._send(200, fh.read(), "text/markdown; charset=utf-8")
            return
        if u.path == "/api/modernized":
            q = urllib.parse.parse_qs(u.query)
            rid = q.get("run_id", [""])[0]
            run = RUNS.get(rid)
            if not run:
                self._json({"ok": False, "error": "unknown run"})
                return
            mod_path = os.path.join(run["out"], "modernized")
            if not os.path.exists(mod_path):
                self._json({"ok": True, "files": []})
                return
            files = []
            for root, _, filenames in os.walk(mod_path):
                for f in filenames:
                    fullpath = os.path.join(root, f)
                    rel = os.path.relpath(fullpath, mod_path).replace("\\", "/")
                    if not f.endswith(".class"):
                        files.append({"name": f, "path": rel})
            self._json({"ok": True, "files": sorted(files, key=lambda x: x["path"])})
            return
        if u.path == "/api/modernized-file":
            q = urllib.parse.parse_qs(u.query)
            rid = q.get("run_id", [""])[0]
            rpath = q.get("path", [""])[0]
            run = RUNS.get(rid)
            if not run or not rpath:
                self._json({"ok": False, "error": "Artifact not available for this run."}, 400)
                return
            resolved = secure_resolve_path(os.path.join(run["out"], "modernized"), rpath)
            if not resolved:
                self._json({"ok": False, "error": "Artifact not available for this run."}, 400)
                return
            try:
                with open(resolved, "r", encoding="utf-8", errors="replace") as fh:
                    self._json({"ok": True, "content": fh.read()})
            except Exception as e:
                self._json({"ok": False, "error": f"Failed to read file: {e}"}, 500)
            return
        if u.path == "/package":
            q = urllib.parse.parse_qs(u.query)
            rid = q.get("run_id", [""])[0]
            run = RUNS.get(rid)
            if not run:
                self._send(404, b"run not found")
                return
            resolved = secure_resolve_path(run["out"], "modernized-package.zip")
            if not resolved:
                self._send(404, b"no package archive found")
                return
            with open(resolved, "rb") as fh:
                self.send_response(200)
                self.send_header("Content-Type", "application/zip")
                self.send_header("Content-Disposition", "attachment; filename=modernized-package.zip")
                self.send_header("Content-Length", str(os.path.getsize(resolved)))
                self.end_headers()
                self.wfile.write(fh.read())
            return
        if u.path == "/api/deps":
            q = urllib.parse.parse_qs(u.query)
            rid = q.get("run_id", [""])[0]
            run = RUNS.get(rid)
            if not run:
                self._json({"ok": False, "error": "unknown run"}, 404)
                return
            state = engine.load_json(os.path.join(run["out"], "state.json"), {})
            disc = state.get("data", {}).get("discover", {})
            imm  = state.get("data", {}).get("immutability", [])
            tr   = state.get("data", {}).get("transpile", {})
            manifest = engine.load_json(os.path.join(run["out"], "manifest.json"), {})
            self._json({
                "ok": True,
                "copy_deps": disc.get("copy_deps", {}),
                "copybook_coverage": disc.get("copybook_coverage", {}),
                "missing_copybooks": disc.get("missing_copybooks", []),
                "call_graph": disc.get("call_graph", {}),
                "file_assigns": disc.get("file_assigns", {}),
                "analyze": state.get("data", {}).get("analyze", {}),
                "immutability": imm,
                "transpile_status": tr.get("status", {}),
                "provenance": manifest.get("programs", []),
                "stub_flags": state.get("data", {}).get("collect", {}).get("stub_flags", {}),
                "verdict": state.get("data", {}).get("manifest", {}) and
                           state.get("stages", {}).get("report", {}).get("detail", ""),
                "validate": state.get("data", {}).get("validate", {}),
            })
            return
        if u.path == "/api/report-json":
            q = urllib.parse.parse_qs(u.query)
            rid = q.get("run_id", [""])[0]
            filename = q.get("file", ["migration-report.json"])[0]
            if filename not in ["migration-report.json", "pipeline_execution_manifest.json"]:
                self._send(400, b"invalid file name requested")
                return
            run = RUNS.get(rid)
            if not run:
                self._send(404, b"run not found")
                return
            resolved = secure_resolve_path(run["out"], filename)
            if not resolved:
                self._send(404, b"file not found")
                return
            with open(resolved, "rb") as fh:
                self._send(200, fh.read(), "application/json; charset=utf-8")
            return
        self._send(404, b"not found")

    def do_POST(self):
        u = urllib.parse.urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            payload = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._json({"ok": False, "error": "bad json"}, 400)
            return
        if u.path == "/api/ingest":
            ok, result = ingest(payload)
            self._json({"ok": ok, "run_id": result if ok else None, "error": None if ok else result}, 200 if ok else 400)
            return
        if u.path == "/api/run":
            run_id = payload.get("run_id")
            restart = payload.get("restart_from", 0)
            if not isinstance(restart, int) or isinstance(restart, bool) \
                    or restart < 0 or restart >= len(engine.STAGES):
                restart = 0
            with LOCK:
                active = [r for r in RUNS.values() if r.get("status") == "running"]
            if active:
                self._json({"ok": False, "error": "another run is in progress"})
                return
            ok, msg = start_run(run_id, restart)
            self._json({"ok": ok, "error": None if ok else msg})
            return
        if u.path == "/api/reset":
            run_id = payload.get("run_id")
            run = RUNS.pop(run_id, None)
            ws = os.path.join(WORKSPACE, run_id)
            shutil.rmtree(ws, ignore_errors=True)
            self._json({"ok": True})
            return
        if u.path == "/api/stop":
            run_id = payload.get("run_id")
            run = RUNS.get(run_id)
            if not run:
                self._json({"ok": False, "error": "unknown run"}, 404)
                return
            p = run.get("pipeline")
            if p and run.get("status") == "running":
                p.cancel()
                self._json({"ok": True, "message": "Cancellation request sent"})
            else:
                self._json({"ok": False, "error": "run is not actively executing"})
            return
        self._json({"ok": False, "error": "unknown route"}, 404)

    def log_message(self, *a):  # silence request logging
        pass


# ponytail: state.json read per-run per-poll; acceptable for single-user local tool.
# For multi-user scale, cache with mtime invalidation.
def build_state():
    runs = []
    for rid, run in RUNS.items():
        state_path = os.path.join(run["out"], "state.json")
        state = engine.load_json(state_path, {})
        stages = []
        for idx, (label, desc) in enumerate(STEP_LABELS):
            sname = engine.STAGES[idx]
            st = state.get("stages", {}).get(sname, {})
            stages.append({
                "index": idx,
                "label": label, "desc": desc,
                "status": st.get("status", "pending"),
                "at": st.get("at", ""),
                "detail": st.get("detail", ""),
                "started_at": st.get("started_at", ""),
                "completed_at": st.get("completed_at", ""),
                "duration_seconds": st.get("duration_seconds"),
                "warnings": st.get("warnings", []),
                "errors": st.get("errors", []),
            })
        runs.append({
            "run_id": rid,
            "status": run.get("status"),
            "source": run.get("source"),
            "name": run.get("name", rid),
            "last_stage": run.get("last_stage", -1),
            "error": run.get("error"),
            "verdict": get_run_verdict(run),
            "log": run["log"][-150:],
            "stages": stages,
            "compare_data": state.get("data", {}).get("compare", {}),
            "package_size": os.path.getsize(os.path.join(run["out"], "modernized-package.zip"))
            if os.path.exists(os.path.join(run["out"], "modernized-package.zip")) else None,
            "execution_scenario": state.get("data", {}).get("execution_scenario"),
            "legacy": state.get("data", {}).get("legacy"),
            "execute": state.get("data", {}).get("execute"),
            "manifest_exists": os.path.exists(os.path.join(run["out"], "pipeline_execution_manifest.json")),
            "data": state.get("data", {}),
            "events": run.get("events", []),
        })
    active = [r for r in RUNS.values() if r.get("status") == "running"]
    return {"runs": runs, "active": bool(active), "git_available": bool(GIT)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8787)
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args()
    print("COBOL -> Java migration UI")
    print("  UI        : http://%s:%d" % (args.host, args.port))
    print("  workspace : %s" % WORKSPACE)
    restore_workspaces()
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print("  (ctrl-c to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")


if __name__ == "__main__":
    main()