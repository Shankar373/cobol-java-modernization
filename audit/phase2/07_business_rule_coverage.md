# Phase 2: Business Rule Coverage & Reporting

To ensure business logic is preserved, we design a coverage measurement engine:

## 1. Rule Extraction Criteria
The engine scans the Intermediate Representation (IR) to register logic rule candidates:
- **Validations**: Boundary and type validation conditionals.
- **Calculations**: Compute math blocks.
- **Transitions**: State status modifications.

## 2. Rule Status Values
- `DISCOVERED`: Logic rule is mapped in the COBOL IR.
- `MAPPED`: Translated to Java Target Model structure.
- `GENERATED`: Written to output source file.
- `TESTED`: Covered by automated test cases.
- `VERIFIED`: Parity validations pass under deterministic test scenarios.
