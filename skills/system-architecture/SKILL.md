---
name: system-architecture
description: Overview of the COBOL-to-Java modernization architecture, pipeline orchestrator, and runtime subsystems.
---

# System Architecture Skill

## Architectural Subsystems

1. **Parser & Semantic Frontend**: `modernize/lexer.py`, `modernize/parser.py`, `modernize/semantic_ir.py`.
2. **Generators**:
   - `modernize/native_generator.py`: Standalone Java.
   - `modernize/enterprise_generator.py`: Spring Boot 3.x REST/Batch.
   - `modernize/jcl_generator.py`: Spring Batch XML/Java steps.
3. **Runtime Support**:
   - `modernize/java_helpers/CobolNumeric.java`, `CobolDecimal.java`, `CobolArithmetic.java`.
   - `KsdSDbService.java`, `VsamIndexedStore.java`.
   - `CicsTransactionContext.java`, `JclExecutionContext.java`.
4. **Verification & Audit**:
   - `tools/cobol_java_differential_verifier.py`.
   - `audit/manifest.py`, `audit/evidence.py`, `audit/certify.py`.
5. **Web UI**:
   - `ui.py` (Flask/stdlib HTTP server), `ui.html`.
