# Phase 2: Source-to-Target Traceability Matrix

This document defines the traceability contract connecting COBOL code to Java targets:

## 1. Traceability Record Schema
Every generated business rule or calculation maps directly to its source elements:

```json
{
  "rule_id": "RULE-0017",
  "cobol_source": {
    "file": "PREMCALC.cob",
    "line": 120,
    "paragraph": "PROCESS-RECORD-PARA"
  },
  "intermediate_representation": {
    "node_id": "STMT_0017"
  },
  "java_target": {
    "class": "PremiumService",
    "method": "calculatePremium",
    "statement_index": 12
  },
  "verification": {
    "test_case": "PremiumServiceTest.testBoundaryConditions",
    "status": "VERIFIED"
  }
}
```

## 2. Integrity Verification
Traceability reports are generated under the `target/` directory to allow auditors to trace execution paths backwards from Java lines to original COBOL statements.
