---
name: certification-evidence
description: Manages the 5-tier certification model, cryptographic SHA-256 manifests, and evidence scorecards.
---

# Certification & Evidence Skill

## 5-Tier Certification Model

- **Tier 1: Syntax & AST Parsing**: Program parses to Semantic IR with zero fatal lex/parse errors.
- **Tier 2: Compilation & Symbol Resolution**: Generated Java compiles cleanly with JDK 17+.
- **Tier 3: Structural & Symbol Equivalence**: Variables, methods, and CFG structures map 1:1.
- **Tier 4: Runtime Differential Equivalence**: Byte-level equivalence across stdout, files, exit codes, and SQL state.
- **Tier 5: Negative & Mutation Hardening**: Verified 0% false PASS on corrupted inputs and 100% mutation catch rate.

## Cryptographic Manifest
- Every run generates `manifest.json` computing SHA-256 hashes of all input source files, generated Java artifacts, compiled `.class` files, execution outputs, and scorecards.
