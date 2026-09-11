> [!NOTE]
> **HISTORICAL ARCHIVE — NOT CURRENT SOURCE OF TRUTH**  
> This document is preserved for historical provenance and audit trail purposes only. Refer to [`DOCUMENTATION_INDEX.md`](../../../../DOCUMENTATION_INDEX.md) for the authoritative active documentation set.

---

# Phase 1: Business Logic Baseline Preservation

We verified how business rules translate from COBOL to Java:

## 1. Verification Table
- **Rule**: Validation evaluates (nested branches). Mapped to nested conditional or switch statements. **STATUS: VERIFIED**.
- **Rule**: COMP-3 decimal arithmetic. Mapped to `CobolDecimal` math operations. **STATUS: VERIFIED**.
- **Rule**: Dynamic calls. Dynamic subprogram CALLs are mapped to helper method calls. **STATUS: PARTIAL** (Requires manual target resolution).
