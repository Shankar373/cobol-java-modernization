# Parity Evidence & Mathematical Precision Model

This document specifies the evidence criteria and mathematical rules governing IBM mainframe to Java semantic equivalence.

---

## 1. Numeric Precision & Packed Decimal Rules

IBM Enterprise COBOL numeric variables adhere to strict integer scaling and packed decimal representation (`COMP-3`):

1. **COMP-3 Packed Decimal Encoding**:
   - Each decimal digit is stored in a 4-bit BCD nibble.
   - The low-order nibble stores the sign: `C` (hex 12) or `F` (hex 15) for positive, `D` (hex 13) for negative.
   - Example: `+1234` stored in `S9(5) COMP-3` occupying 3 bytes: `01 23 4C`.
   - The runtime helper `CobolNumeric.java` guarantees bit-level BCD packing/unpacking parity.

2. **Truncation vs. Rounding**:
   - Default COBOL assignment truncates high-order digits exceeding receiver PICTURE integer scale and drops low-order fractional digits exceeding decimal scale without rounding.
   - `ROUNDED` clause applies half-up rounding (or bank's rounding if configured).
   - Division by zero or overflow without `ON SIZE ERROR` produces IBM standard defined behavior; with `ON SIZE ERROR`, receiver retains original value and branch is executed.

---

## 2. Cryptographic Evidence Chain

Verification evidence is cryptographically anchored:

```
[Input Sources] ────(SHA-256)───┐
[Generated Java] ───(SHA-256)───┼──> [manifest.json] ──(SHA-256)──> [scorecard.json]
[Baseline Outputs] ─(SHA-256)───┤
[Java Outputs] ─────(SHA-256)───┘
```

- Any modification to source inputs, generated classes, or output files alters the manifest digest, invalidating cached verification results.
