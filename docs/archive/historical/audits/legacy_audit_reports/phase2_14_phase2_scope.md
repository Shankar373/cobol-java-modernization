> [!NOTE]
> **HISTORICAL ARCHIVE — NOT CURRENT SOURCE OF TRUTH**  
> This document is preserved for historical provenance and audit trail purposes only. Refer to [`DOCUMENTATION_INDEX.md`](../../../../DOCUMENTATION_INDEX.md) for the authoritative active documentation set.

---

# Phase 2: Revised Implementation Scope

We restrict Phase 2 implementation to:

## 1. Phase 2 Scope:
- **Goal A: Hardened Comparator**: Generic equivalence checks validating files, exit code parity, and record counts.
- **Goal B: Semantic IR Scaffolding**: AST node maps preserving variables, operations, and file/line locations.
- **Genericity Enhancements**: Removing nightly batch name couplings.
- **Call-graph Resolution reports**: Track and output resolved/unresolved dependency lists.

## 2. Deferred to Phase 3
- **Full AST Code Generation**: Complete automatic COBOL-to-Java native compilation.
- **Spring Scaffolding**: Maven Spring Boot Batch code setups.
- **DB2 SQL translations**: JPA repository modernization.
