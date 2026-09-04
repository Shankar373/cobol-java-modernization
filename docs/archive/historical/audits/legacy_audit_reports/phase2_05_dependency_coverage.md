> [!NOTE]
> **HISTORICAL ARCHIVE — NOT CURRENT SOURCE OF TRUTH**  
> This document is preserved for historical provenance and audit trail purposes only. Refer to [`DOCUMENTATION_INDEX.md`](../../../../DOCUMENTATION_INDEX.md) for the authoritative active documentation set.

---

# Phase 2: Subprogram CALL & Dependency Resolution Tracking

Every subprogram call is explicitly mapped and reported:

## 1. CALL Target Classifications
- `RESOLVED_STATIC`: Static target parsed and generated.
- `RESOLVED_DYNAMIC`: Variable target resolved dynamically.
- `UNRESOLVED_DYNAMIC`: Variable target cannot be mapped statically.
- `UNSUPPORTED`: Mainframe calls (e.g. SORT) lacking target emulation.
- `EXTERNAL_SYSTEM`: Calls to external libraries or APIs.
- `MISSING_SOURCE`: Reference source file is not in repository.

## 2. CALL Lifecycle Statuses
Each call records its reachability and modernization status:
- **Reachability**: `REACHABLE` / `NOT_REACHABLE`.
- **Execution**: `EXECUTED` / `NOT_EXECUTED`.
- **Modernization**: `MIGRATED` / `PARTIAL` / `UNMIGRATED` / `UNSUPPORTED` / `BLOCKED`.
