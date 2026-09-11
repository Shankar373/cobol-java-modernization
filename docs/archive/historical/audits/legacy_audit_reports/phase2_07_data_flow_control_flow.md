> [!NOTE]
> **HISTORICAL ARCHIVE — NOT CURRENT SOURCE OF TRUTH**  
> This document is preserved for historical provenance and audit trail purposes only. Refer to [`DOCUMENTATION_INDEX.md`](../../../../DOCUMENTATION_INDEX.md) for the authoritative active documentation set.

---

# Phase 2: Data-Flow & Control-Flow Graph Design

We define the graph structure for flow and data tracking:

## 1. Control-Flow Graph (CFG)
The CFG tracks execution transitions:
`Program -> Paragraph -> Statement -> Control-flow edges`
This maps program branches, loops, perform loops, call graphs, and termination coordinates.

## 2. Data-Flow Tracking
Traces data dependencies:
`INPUT -> FIELD -> VARIABLE -> CALCULATION -> CONDITION -> STATE -> OUTPUT`
This enables mapping target variables back to source input operations.
