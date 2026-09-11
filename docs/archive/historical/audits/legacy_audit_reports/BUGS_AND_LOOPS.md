> [!NOTE]
> **HISTORICAL ARCHIVE — NOT CURRENT SOURCE OF TRUTH**  
> This document is preserved for historical provenance and audit trail purposes only. Refer to [`DOCUMENTATION_INDEX.md`](../../../../DOCUMENTATION_INDEX.md) for the authoritative active documentation set.

---

# Phase 22: Bugs, Hangs, and Code Smells

- **Stale Lock Files**: Force-killing processes leaves `backend.lock` and `launcher.lock` files on disk, preventing Docker Desktop from launching until deleted.
- **Orphaned Docker Containers**: Terminated runs do not actively stop background Docker containers, causing resource locking.
- **Level 78 Constant Limitations**: OpenSourceCOBOL4J does not support Level 78 variables, throwing syntax errors.
