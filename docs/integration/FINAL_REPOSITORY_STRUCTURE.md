# Final Repository Structure & Architecture Map

**Canonical Repository:** `c:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test`  
**Branch:** `feature/repository-structure-hardening`  
**Standard:** Ponytail Global AI Software Engineering Constitution  
**Platform Verdict:** `VERIFIED_FOR_DEFINED_SCOPE`  
**Mentor Status:** `VERIFIED_FOR_TESTED_SCOPE`  
**Date:** September 2, 2026  

---

## 1. Top-Level Directory Tree

```
Cobol-to-java-test/
├── src/
│   └── cjp/
│       ├── __init__.py
│       └── cli.py                          # Unified CJP CLI interface
│
├── modernize/                              # Production Modernization Engine
│   ├── lexer.py                            # COBOL Lexer
│   ├── parser.py                           # COBOL Recursive Descent AST Parser
│   ├── semantic_ir.py                      # Semantic IR Models
│   ├── native_generator.py                 # Native Java & Spring Boot Generator
│   ├── enterprise_generator.py             # JPA & Batch Orchestration Generator
│   └── native_pipeline.py                  # Domain Transformation Pipeline
│
├── execution/                              # Execution & Observation Layer
│   ├── runner.py                           # Process & Container Execution
│   ├── models.py                           # Execution Scenarios & Observations
│   ├── normalization.py                    # Output Normalization Engine
│   └── interactive.py                      # Terminal & Interactive Handler
│
├── audit/                                  # Cryptographic Audit Core
│   ├── certify.py                          # 5-Tier Certification Scorecard Evaluator
│   ├── evidence.py                         # Evidence Bundle & Tier Models
│   └── manifest.py                         # Cryptographic SHA-256 Manifest Builder
│
├── tools/                                  # Operational & Verification Tooling
│   ├── cobol_java_differential_verifier.py # Differential Verifier CLI
│   ├── acceptance_e2e.py                   # E2E Acceptance Test Harness
│   ├── modernize_and_verify.py             # Single-Command Modernizer Wrapper
│   └── reference_runtimes/                 # Isolated External Reference Adapters
│       ├── base.py                         # Base Adapter Interface
│       ├── gnu_cobol.py                    # Canonical GnuCOBOL Baseline Runner
│       ├── z390/                           # z390 Reference Oracle Adapter
│       ├── hercules/                       # Hercules Reference Oracle Adapter
│       ├── database.py                     # Database Validation Modes
│       ├── ebcdic/                         # EBCDIC Charset & Collation Strategy
│       ├── capability_detector.py          # Workload Capability Scanner
│       └── certification_policy.py         # Fail-Closed Certification Policy
│
├── tests/                                  # Automated Test Architecture (726 Tests)
│   ├── unit/                               # Lexer, Parser, IR Unit Tests
│   ├── component/                          # Subsystem Component Tests
│   ├── integration/                        # Pipeline & State Integration Tests
│   ├── differential/                       # Gate 1 & Gate 2 Differential Tests
│   ├── acceptance/                         # Unseen Repositories & Acceptance Tests
│   ├── robustness/                         # Mutation & Robustness Suites
│   ├── reference_runtime/                  # Reference Runtime & Oracle Tests
│   ├── fixtures/                           # Structured Test Fixtures
│   │   ├── archives/                       # Test Archive Zips (A-PAYONLY, etc.)
│   │   ├── unpacked/                       # External Benchmarks (cics-genapp, etc.)
│   │   └── repos/                          # Canonical Batch Fixtures (GOLDENPAY, etc.)
│   └── utils/                              # Test Utilities & Helpers
│
├── skills/                                 # Antigravity Skills
│   ├── certification-evidence/
│   ├── cobol-analysis/
│   ├── copybook-expansion/
│   ├── differential-verifier/
│   ├── ir-ast-pipeline/
│   ├── native-java-generator/
│   └── system-architecture/
│
├── docs/                                   # Documentation Hierarchy
│   ├── AGENTS.md                           # Developer Guidelines & Constitution
│   ├── ARCHITECTURE.md                     # System Architecture
│   ├── CERTIFICATION_MODEL.md              # 5-Tier Model Specification
│   ├── DEVELOPMENT.md                      # Development & Build Instructions
│   ├── FAIL_CLOSED_MATRIX.md               # Anti-Bypass Rules
│   ├── KNOWN_LIMITATIONS.md                # System Boundaries
│   ├── MENTOR_VERIFIER.md                  # Mentor Workflow Overview
│   ├── OPEN_SOURCE_INVENTORY.md            # Open Source Component Index
│   ├── PARITY_EVIDENCE_MODEL.md            # Parity Evidence Specification
│   ├── PIPELINE.md                         # 13-Stage Pipeline Guide
│   ├── SBOM.md                             # Software Bill of Materials
│   ├── SECURITY.md                         # Security Policies & Sandboxing
│   ├── SUPPORTED_FEATURES.md               # Supported COBOL Construct Matrix
│   ├── TESTING.md                          # Testing Strategy
│   ├── audit/                              # Current Authoritative Audit Documents
│   │   ├── BUG_REGISTER.md                 # Forensic Bug Register
│   │   ├── CAPABILITY_MATRIX.md            # Multi-Oracle Capability Matrix
│   │   ├── EVIDENCE_MAP.md                 # Evidence Artifact Mapping
│   │   ├── FALSE_PASS_RISKS.md             # False-Pass Risk Register
│   │   ├── FINAL_FORENSIC_AUDIT.md         # Forensic Audit Report
│   │   └── LIMITATIONS_REGISTER.md         # Authoritative Limitations Register
│   ├── certification/                      # Certification Specifications
│   │   ├── FINAL_CERTIFICATION_REPORT.md   # Final 20-Section Certification Report
│   │   └── MENTOR_ACCEPTANCE_SCOPE.md      # Formal Mentor Workflow Specification
│   ├── integration/                        # Integration Reports & Baselines
│   │   ├── structure_cleanup_baseline.md   # Structure Cleanup Baseline
│   │   ├── REPOSITORY_STRUCTURE_AUDIT.md   # Exhaustive Inventory Audit
│   │   ├── ROOT_CLEANUP_MANIFEST.md        # Root Cleanup Disposition Matrix
│   │   ├── FINAL_REPOSITORY_STRUCTURE.md   # Final Architecture Tree Map
│   │   └── STRUCTURE_CLEANUP_FINAL_REPORT.md# Final Cleanup Summary Report
│   ├── remediation/                        # Remediation Logs & Baselines
│   │   ├── BASELINE.md                     # Remediation Baseline
│   │   └── REMEDIATION_SUMMARY.md          # Remediation Summary
│   └── archive/                            # Historical Audit Snapshots & Phase Notes
│       ├── historical_audits/              # Historical Pre-Fix Audits
│       └── historical_phases/              # Past Phase Notes & Snapshots
│
├── artifacts/                              # Generated Evidence Artifacts (.gitignored)
│   ├── runs/                               # Run Outputs & Historical Logs
│   ├── logs/                               # Server & Runtime Logs
│   ├── releases/                           # Packaged Release Verification Zips
│   └── verification/                       # Final Verification Evidence Bundles
│
├── docker/                                 # Container Configurations
├── cobol_migrate.py                        # Canonical 13-Stage Pipeline Orchestrator & CLI
├── ui.py & ui.html                         # Interactive Web GUI Entry Point
├── audit_engine.py                         # Forensic Audit Engine
├── slicer.py                               # Flow Slicer Utility
├── conftest.py                             # Root Pytest Fixture Configuration
├── pyproject.toml                          # Standard Python Project Metadata
├── requirements.txt & requirements-dev.txt # Dependency Manifests
├── Dockerfile* & docker-compose.yml        # Docker Container Definitions
├── .gitignore & .dockerignore              # Clean Git & Docker Ignore Rules
├── README.md & PROJECT_OVERVIEW.md         # Repository Readme & Overview
└── COMPLETE_SYSTEM_DOCUMENTATION.md        # End-to-End System Documentation
```
