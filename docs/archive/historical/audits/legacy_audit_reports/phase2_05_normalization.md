> [!NOTE]
> **HISTORICAL ARCHIVE — NOT CURRENT SOURCE OF TRUTH**  
> This document is preserved for historical provenance and audit trail purposes only. Refer to [`DOCUMENTATION_INDEX.md`](../../../../DOCUMENTATION_INDEX.md) for the authoritative active documentation set.

---

# Phase 2: Strict Normalization Rules

Every normalization rule must declare:
- **pattern**: Regex string.
- **artifact**: Filename.
- **field**: Field position/index.
- **reason**: Justification (e.g. `nondeterministic transaction timestamp`).
- **scope**: Mapped lines or fields.
- **original_value**: Value before translation.
- **normalized_value**: Translated value.
