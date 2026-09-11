---
name: ir-ast-pipeline
description: Constructs Semantic IR ASTs, control-flow graphs (CFGs), data-flow variable tracking, and program call-trees.
---

# Semantic IR & AST Pipeline Skill

## Key Components

1. **Semantic IR (`modernize/semantic_ir.py`)**:
   - Stores variable declarations (`DATA_ITEM`), picture clauses, USAGE clauses (`COMP`, `COMP-3`, `DISPLAY`).
   - Maps storage hierarchies (01 group records, elementary 05/10 fields, 88 condition names).

2. **Control Flow Graph (`modernize/control_flow.py`)**:
   - Builds paragraph-level directed graphs.
   - Detects dead code / unreachable paragraphs.
   - Normalizes fallthrough logic and `PERFORM ... THRU`.

3. **Data Flow Analyzer (`modernize/data_flow.py`)**:
   - Tracks variable definition/use chains.
   - Resolves `REDEFINES` memory overlay dependencies.
