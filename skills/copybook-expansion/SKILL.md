---
name: copybook-expansion
description: Resolves and expands COBOL COPY statements including COPY REPLACING directives.
---

# Copybook Expansion Skill

## Workflow

1. **Discovery**:
   - Search copybook directories (`cpy/`, `copy/`, `include/`, `src/`).
   - Match case-insensitively with `.cpy`, `.cbl`, `.copy` extensions.

2. **COPY REPLACING Processing**:
   - `COPY FOO REPLACING ==:PREFIX:== BY ==CUST==`: Perform exact token and string substitution before semantic parsing.
   - Prevent infinite recursion during nested `COPY` invocations.

3. **Validation**:
   - Confirm all referenced copybooks are resolved.
   - Unresolved copybooks must fail closed with an explicit diagnostic rather than generating partial Java models.
