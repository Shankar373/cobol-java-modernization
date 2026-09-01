# Root Directory Cleanup Manifest

**Repository:** `c:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test`  
**Branch:** `feature/repository-structure-hardening`  
**Date:** September 2, 2026  

---

## 1. Candidate Decision Matrix

| Root Item | Type | Disposition | Destination / Action | Justification |
|---|---|---|---|---|
| `AUDIT_BASELINE_BEFORE_FIXES.md` | Historical Doc | **ARCHIVE** | `docs/archive/historical_audits/` | Historical audit before fixes; keep for provenance. |
| `DEEP_PROJECT_AUDIT_REPORT.md` | Historical Doc | **ARCHIVE** | `docs/archive/historical_audits/` | Deep audit snapshot; preserve history. |
| `DEEP_PROJECT_AUDIT_REPORT_AFTER_FIXES.md`| Historical Doc | **ARCHIVE** | `docs/archive/historical_audits/` | Post-fix audit snapshot. |
| `DEEP_PROJECT_AUDIT_REPORT_FINAL.md` | Historical Doc | **ARCHIVE** | `docs/archive/historical_audits/` | Final deep project audit snapshot. |
| `FINAL_INDEPENDENT_ACCEPTANCE_AUDIT.md` | Historical Doc | **ARCHIVE** | `docs/archive/historical_audits/` | Historical acceptance audit. |
| `FIX_ANALYSIS_test_sql_baseline_differential.md`| Historical Doc | **ARCHIVE** | `docs/archive/historical_audits/` | SQL fix analysis memo. |
| `SUPPORTED_COBOL_FEATURE_MATRIX.md` | Historical Doc | **ARCHIVE** | `docs/archive/historical_audits/` | Superseded by authoritative `docs/audit/CAPABILITY_MATRIX.md`. |
| `TEST_REORGANIZATION_SUMMARY.md` | Historical Doc | **ARCHIVE** | `docs/archive/historical_audits/` | Historical test reorg notes. |
| `UNIVERSAL_TRANSFORMATION_ACCEPTANCE.md` | Historical Doc | **ARCHIVE** | `docs/archive/historical_audits/` | Historical acceptance criteria. |
| `baseline.md` | Historical Doc | **ARCHIVE** | `docs/archive/historical_audits/` | Superseded by `docs/remediation/BASELINE.md`. |
| `final_audit_report.md` | Historical Doc | **ARCHIVE** | `docs/archive/historical_audits/` | Historical audit report. |
| `implementation_plan.md` | Transient Plan | **ARCHIVE** | `docs/archive/historical_audits/` | Agent planning scratch artifact. |
| `walkthrough.md` | Transient Walk | **ARCHIVE** | `docs/archive/historical_audits/` | Agent walkthrough scratch artifact. |
| `run_20.log` ... `run_25_failed.log` | Run Logs | **MOVE** | `artifacts/runs/historical_logs/` | Preserve debugging logs in artifacts hierarchy. |
| `ui-server.log`, `ui-server.err.log` | Server Logs | **MOVE** | `artifacts/logs/` | UI server logs; add pattern to `.gitignore`. |
| `temp_testdisp`, `temp_testdisp.cob` | Temp Files | **DELETE** | Removed & ignored | Scratch test files from manual debugging. |
| `out.dat`, `idx.dat` | Temp Data | **DELETE** | Removed & ignored | Scratch data outputs. |
| `A-PAYONLY.zip`, `F-PAYFAIL.zip`, `INVMGR.zip` | Test Archives | **MOVE** | `tests/fixtures/archives/` | Test package fixture zips. |
| `systemaops-release.zip*` | Release Artifact | **MOVE** | `artifacts/releases/` | Release packaging verification artifact. |
| `final_verification.json` | Verification | **MOVE** | `artifacts/verification/` | JSON verification output. |
| `cics-genapp-main.zip` (dir) | Fixture Repo | **MOVE** | `tests/fixtures/unpacked/cics-genapp/` | Unpacked external CICS fixture. |
| `legacy-insurance-...` (dir) | Fixture Repo | **MOVE** | `tests/fixtures/unpacked/legacy-insurance/` | Unpacked external Insurance fixture. |
| `cobol_migrate.py` | Canonical Core | **KEEP** | Root | Primary 13-stage CLI and orchestrator. |
| `ui.py`, `ui.html` | Interactive UI | **KEEP** | Root | Canonical FastAPI web server & UI. |
| `audit_engine.py` | Audit Engine | **KEEP** | Root | Canonical forensic auditing engine. |
| `slicer.py` | Flow Slicer | **KEEP** | Root | Paragraph slicing utility. |
| `conftest.py` | Pytest Fixtures | **KEEP** | Root | Canonical root pytest configuration. |
| `migration_config.json` | Default Config | **KEEP** | Root | Default pipeline configuration. |
| `requirements.txt`, `requirements-dev.txt` | Dependencies | **KEEP** | Root | Python dependencies. |
| `Dockerfile*`, `docker-compose.yml` | Container Spec | **KEEP** | Root | Containerized build and execution recipes. |
| `README.md`, `PROJECT_OVERVIEW.md`, `COMPLETE_SYSTEM_DOCUMENTATION.md` | Core Docs | **KEEP** | Root | Primary architectural and system documentation. |
