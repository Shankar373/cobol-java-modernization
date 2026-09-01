# Authoritative Repository Structure Audit

**Repository:** `c:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test`  
**Branch:** `feature/repository-structure-hardening`  
**Date:** September 2, 2026  

---

## 1. Executive Summary & Inventory Summary

An exhaustive filesystem scan was performed across all directories and files.

| Category | File Count | Description | Action Required |
|---|---|---|---|
| **SOURCE** | 562 | Primary Python pipelines, modernizers, parsers, execution engines, UI, tools. | Retain and modularize under clean architecture boundaries. |
| **TEST** | 189 | Pytest test suites across unit, component, integration, security, eof, differential. | Retain; maintain 100% test passing rate. |
| **FIXTURE** | 1,850+ | COBOL programs, copybooks, data files, JCL cards, BMS maps (`tests/repos/`, `cics-genapp`, `legacy-insurance`). | Retain; organize into structured fixture directories. |
| **GENERATED** | 1,918+ | Target builds, compiled `.class` files, Spring Boot JARs, temporary outputs (`target/`, `generated/`, `test_out/`). | Exclude from version control via `.gitignore`. |
| **EVIDENCE** | 1,003 | Historical test logs, scorecards, differential reports, audit manifests (`reports/`, `artifacts/`). | Retain persistent verification runs; organize cleanly. |
| **DOCUMENTATION** | 370 | Architecture specifications, audit registers, certification reports, user guides. | Consolidate and preserve audit history with timestamps. |
| **TEMPORARY** | 17 | Root-level transient run logs (`run_*.log`), server err logs, temporary data files. | Archive/delete transient root noise safely. |
| **ARCHIVE** | 14 | Package ZIPs, golden snapshots (`A-PAYONLY.zip`, `systemaops-release.zip`). | Retain in designated archive/fixture locations. |

---

## 2. Primary Production Core & Entry Points

Through import and execution tracing, the authoritative production components are:

1. **Primary Pipeline Orchestrator & CLI:**
   - [`cobol_migrate.py`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/cobol_migrate.py): The 13-stage canonical pipeline orchestrator handling ingest, discover, analyze, baseline, transpile, generate, compile, execute, compare (Gate 1), test, validate (Gate 2), report, and package.
2. **Modernization Engine & Lexer/Parser/IR:**
   - [`modernize/parser.py`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/modernize/parser.py): Recursive descent AST parser.
   - [`modernize/semantic_ir.py`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/modernize/semantic_ir.py): Semantic Intermediate Representation model.
   - [`modernize/native_generator.py`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/modernize/native_generator.py): Native Java, Spring Boot, Spring Batch, and JPA code generator.
   - [`modernize/native_pipeline.py`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/modernize/native_pipeline.py): Native transformation orchestrator.
3. **Execution Layer:**
   - [`execution/`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/execution/): Independent execution and observation boundary (`execution/runner.py`, `execution/models.py`, `execution/interactive.py`).
4. **Verification & Audit Core:**
   - [`audit_engine.py`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/audit_engine.py): Forensic audit and capability inspection engine.
   - [`tools/cobol_java_differential_verifier.py`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/tools/cobol_java_differential_verifier.py): Standalone differential verification engine.
5. **Interactive UI Entry Point:**
   - [`ui.py`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/ui.py) & [`ui.html`](file:///c:/Users/bandi/Desktop/SystemaOps/Cobol-to-java-test/ui.html): FastAPI-based web UI interface.

---

## 3. Overlapping & Compatibility Components Analysis

- `cobol_migrate.py` is the CANONICAL orchestrator referenced across all CI and integration scripts.
- `modernize/native_pipeline.py` is the DOMAIN orchestrator for native code generation stages.
- `tools/modernize_and_verify.py` is a convenience wrapper for end-to-end local runs.
- `tools/cobol_java_differential_verifier.py` is an independent verification tool.
- `tools/acceptance_e2e.py` is an acceptance test harness.

All of these serve specific defined roles and must NOT be deleted.
