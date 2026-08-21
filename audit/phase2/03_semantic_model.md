# Phase 2: COBOL Semantic Model & Intermediate Representation (IR)

To enable genuine modernization, SystemaOps maps COBOL elements to an Intermediate Representation (IR).

## 1. COBOL Declaration Semantics
The model preserves the complete semantics of data definitions:
- **Field Characteristics**: PIC/PICTURE strings, USAGE modes (COMP, COMP-3, DISPLAY, PACKED-DECIMAL).
- **Implied Decimals**: Implied decimal position scale and precision values (e.g. `PIC 9(9)V99`).
- **Data Structures**: Levels, Group items, Elementary items, REDEFINES declarations, and OCCURS arrays.
- **Conditionals**: 88-level condition names.

## 2. Semantic IR Node Layout
Every parsed statement is structured as an IR node preserving source file locations for complete traceability:

```json
{
  "node_id": "STMT_0017",
  "operation": "COMPUTE",
  "target": {
    "name": "WS-TOTAL",
    "type": "PACKED-DECIMAL",
    "scale": 2,
    "precision": 11
  },
  "expression": {
    "op": "MULTIPLY",
    "left": "WS-QTY",
    "right": "WS-RATE"
  },
  "source_location": {
    "file": "PREMCALC.cob",
    "line": 120,
    "paragraph": "PROCESS-RECORD-PARA"
  }
}
```
