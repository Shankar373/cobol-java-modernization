---
name: native-java-generator
description: Generates high-performance native Java classes using CobolNumeric, CobolDecimal, and CobolRef runtime helpers.
---

# Native Java Generator Skill

## Code Generation Guidelines

1. **Numeric Representation**:
   - `CobolNumeric` for zoned and packed decimal fields (`COMP-3`).
   - `CobolDecimal` / `BigDecimal` with exact IBM rounding (`ROUNDED`) and `ON SIZE ERROR` trapping.

2. **Storage Overlays (`REDEFINES`)**:
   - Use backing byte buffer overlays for overlapping fields to preserve byte-exact mutated state.

3. **Subroutine Calling (`CALL`)**:
   - Pass parameters wrapped in `CobolRef<T>` for `BY REFERENCE` semantics, allowing the callee to modify caller state.

4. **File I/O**:
   - Line sequential and VSAM KSDS files mapped to `VsamIndexedStore` and `KsdSDbService`.
