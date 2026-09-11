# Documentation Consolidation Baseline

**Repository:** `c:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test`  
**Base Commit SHA:** `14df99c7d484ab5116d7675282a879651b2ddab7`  
**Branch:** `feature/documentation-consolidation`  
**Date:** September 2, 2026  

---

## 1. Pre-Cleanup Document Inventory Summary

| Location | File Count | Classification / Nature | Target Disposition |
|---|---|---|---|
| **Root Documents** (`/`) | 3 | `README.md`, `PROJECT_OVERVIEW.md`, `COMPLETE_SYSTEM_DOCUMENTATION.md` | **KEEP** (Authoritative entry points) |
| **Docs Root** (`docs/`) | 14 | Architecture, Pipeline, Testing, Security, Agents, Standards | **KEEP** (Authoritative core docs) |
| **Current Audit** (`docs/audit/`) | 15 | Active bug register, capability matrix, evidence map + Gate 2 historical memos | **KEEP** 6 authoritative, **ARCHIVE** 9 historical |
| **Current Certification** (`docs/certification/`) | 2 | `FINAL_CERTIFICATION_REPORT.md`, `MENTOR_ACCEPTANCE_SCOPE.md` | **KEEP** (Authoritative certification) |
| **Current Integration** (`docs/integration/`) | 21 | OS evaluations, license matrix, backport snapshots, structure reports | **KEEP** 3 authoritative, **ARCHIVE** 18 historical snapshots |
| **Remediation** (`docs/remediation/`) | 2 | Historical remediation baselines | **ARCHIVE** to `docs/archive/historical/remediation/` |
| **Historical Archive** (`docs/archive/`) | 43 | Pre-fix audits, historical phase notes | **ORGANIZE** under `docs/archive/historical/` |
| **Audit Directory Markdown** (`audit/`) | 162 | Historical phase audit reports (Phase 1–11) | **ARCHIVE** to `docs/archive/historical/audits/legacy_phase_audits/` |

---

## 2. Active Authoritative Document Set (Inviolable Target)

### Core Architecture & Operating Standards (`docs/`)
- `docs/AGENTS.md`
- `docs/ARCHITECTURE.md`
- `docs/DEVELOPMENT.md`
- `docs/PIPELINE.md`
- `docs/TESTING.md`
- `docs/SECURITY.md`
- `docs/KNOWN_LIMITATIONS.md`
- `docs/SUPPORTED_FEATURES.md`
- `docs/CERTIFICATION_MODEL.md`
- `docs/FAIL_CLOSED_MATRIX.md`
- `docs/MENTOR_VERIFIER.md`
- `docs/PARITY_EVIDENCE_MODEL.md`
- `docs/OPEN_SOURCE_INVENTORY.md`
- `docs/SBOM.md`

### Current Audit Registers (`docs/audit/`)
- `docs/audit/BUG_REGISTER.md`
- `docs/audit/CAPABILITY_MATRIX.md`
- `docs/audit/EVIDENCE_MAP.md`
- `docs/audit/FALSE_PASS_RISKS.md`
- `docs/audit/LIMITATIONS_REGISTER.md`
- `docs/audit/FINAL_FORENSIC_AUDIT.md`

### Current Certification Standards (`docs/certification/`)
- `docs/certification/FINAL_CERTIFICATION_REPORT.md`
- `docs/certification/MENTOR_ACCEPTANCE_SCOPE.md`

### Current Integration & Compatibility (`docs/integration/`)
- `docs/integration/OPEN_SOURCE_EVALUATION.md`
- `docs/integration/OPEN_SOURCE_LICENSE_MATRIX.md`
- `docs/integration/OPEN_SOURCE_REFERENCE_INTEGRATION_REPORT.md`
- `docs/integration/DOCUMENTATION_CLEANUP_BASELINE.md`
- `docs/integration/DOCUMENTATION_CLEANUP_FINAL_REPORT.md`
