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
        }


def start_run(run_id, restart_from):
    run = RUNS.get(run_id)
    if not run:
        return False, "unknown run"
    if run.get("status") == "running":
        return False, "run already in progress"

    def sink(msg):
        run["log"].append(msg)
        run["log"] = run["log"][-400:]

    def worker():
        with LOCK:
            run["status"] = "running"
            run["started_at"] = engine.now_iso()
            engine.LOG_SINK = sink
            try:
                p = engine.Pipeline(run["repo"], run["out"], cfg=CFG, pull=True)
                p.run(restart_from=restart_from)
                state = engine.load_json(os.path.join(run["out"], "state.json"), {})
                run["last_stage"] = 12 if state.get("stages", {}).get("package", {}).get("status") == "done" else 11
                run["verdict"] = state.get("stages", {}).get("report", {}).get("detail", "done")
                run["status"] = "done"
            except Exception as e:  # noqa: BLE001
                run["error"] = f"{type(e).__name__}: {e}"
                run["status"] = "error"
            finally:
                engine.LOG_SINK = None
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
        data = base64.b64decode(payload.get("data", ""))
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
        cmd = [GIT, "clone", "--depth", "1"]
        branch = (payload.get("branch") or "").strip()
        if branch:
            cmd += ["--branch", branch]
        cmd += [url, repo]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            shutil.rmtree(ws, ignore_errors=True)
            return False, "git clone failed: " + (r.stderr or r.stdout)[-300:]
    else:
        return False, "unknown source"
    RUNS[run_id] = {"run_id": run_id, "status": "ready",
                    "repo": repo, "out": os.path.join(ws, "target"),
                    "last_stage": -1, "log": [], "source": source,
                    "name": payload.get("name") or ("git: " + url if source == "git" else "zip-package")}
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
        if u.path == "/report":
            q = urllib.parse.parse_qs(u.query)
            rid = q.get("run_id", [""])[0]
            run = RUNS.get(rid)
            path = os.path.join(run["out"], "migration-report.md") if run else ""
            if not path or not os.path.exists(path):
                self._send(404, b"no report yet")
                return
            with open(path, "rb") as fh:
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
                self._json({"ok": False, "error": "bad query"})
                return
            clean_path = rpath.replace("\\", "/").strip("/")
            fullpath = os.path.realpath(os.path.join(run["out"], "modernized", clean_path))
            base = os.path.realpath(os.path.join(run["out"], "modernized"))
            if not fullpath.startswith(base + os.sep):
                self._json({"ok": False, "error": "invalid path"})
                return
            if not os.path.exists(fullpath) or os.path.isdir(fullpath):
                self._json({"ok": False, "error": "file not found"})
                return
            with open(fullpath, "r", encoding="utf-8", errors="replace") as fh:
                self._json({"ok": True, "content": fh.read()})
            return
        if u.path == "/package":
            q = urllib.parse.parse_qs(u.query)
            rid = q.get("run_id", [""])[0]
            run = RUNS.get(rid)
            path = os.path.join(run["out"], "modernized-package.zip") if run else ""
            if not path or not os.path.exists(path):
                self._send(404, b"no package archive found")
                return
            with open(path, "rb") as fh:
                self.send_response(200)
                self.send_header("Content-Type", "application/zip")
                self.send_header("Content-Disposition", f"attachment; filename=modernized-package.zip")
                self.send_header("Content-Length", str(os.path.getsize(path)))
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
            run = RUNS.get(rid)
            path = os.path.join(run["out"], "migration-report.json") if run else ""
            if not path or not os.path.exists(path):
                self._send(404, b"no report yet")
                return
            with open(path, "rb") as fh:
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
            self._json({"ok": ok, "run_id": result if ok else None, "error": None if ok else result})
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
        self._json({"ok": False, "error": "unknown route"}, 404)

    def log_message(self, *a):  # silence request logging
        pass


def build_state():
    runs = []
    for rid, run in RUNS.items():
        state = engine.load_json(os.path.join(run["out"], "state.json"), {})
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
            })
        runs.append({
            "run_id": rid,
            "status": run.get("status"),
            "source": run.get("source"),
            "name": run.get("name", rid),
            "last_stage": run.get("last_stage", -1),
            "error": run.get("error"),
            "verdict": run.get("verdict"),
            "log": run["log"][-150:],
            "stages": stages,
            "compare_data": state.get("data", {}).get("compare", {}),
            "package_size": os.path.getsize(os.path.join(run["out"], "modernized-package.zip"))
            if os.path.exists(os.path.join(run["out"], "modernized-package.zip")) else None,
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