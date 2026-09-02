> [!NOTE]
> **HISTORICAL ARCHIVE — NOT CURRENT SOURCE OF TRUTH**  
> This document is preserved for historical provenance and audit trail purposes only. Refer to [`DOCUMENTATION_INDEX.md`](../../../../DOCUMENTATION_INDEX.md) for the authoritative active documentation set.

---

# Phase 31: Recommended Actions

1. **Decouple Emulation Layer**: Rewrite transpilation templates to produce native Java types (e.g. `String`, `BigDecimal`) instead of wrapping them in `libcobj` classes.
2. **Harden Subprocess Execution**: Use list-based arguments instead of string formatting with `shell=True` to eliminate shell injections.
3. **Database Mapping**: Parse and modernize SQL preprocessor statements into clean Spring Boot JPA repositories.
