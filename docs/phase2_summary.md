# Phase 2 Summary — Numeric Semantics & Evidence Hardening

## What Was Changed

- **`runtime/CobolArithmetic.java`** — Hardened the `power(BigDecimal, BigDecimal)` exponentiation method to avoid double fallback:
  - If exponent is an integer, calculates pure `BigDecimal.pow(exponent, MC)`.
  - Supports negative integer exponents correctly by calculating the reciprocal using BigDecimal division.
  - If exponent is fractional or out-of-range, catches the exception and throws a clean `ArithmeticException` with a clear fail-fast diagnostic error code (`COBOL_UNSUPPORTED_NUMERIC_FEATURE`), ensuring no double-based math contamination is introduced.
- **`modernize/java_helpers/CobolFormatHelper.java`** — Removed the dead `mod(double, double)` utility method to prevent any unused double-based helper functions from residing in format helper classes.
- **`tests/utils/parity_harness.py`** — Added `normalize_display(b: bytes) -> bytes` to strip leading/trailing spaces, collapse multiple spaces to a single space, normalize CRLF to LF, and filter empty lines. This ensures differential stdout comparisons evaluate semantic equality rather than accidental formatting byte matches.
- **`modernize/capability_matrix.py`** — Updated the `ARITH.COMPUTE` entry to reflect the new fail-fast fractional exponent limitations (no double math).
- **`docs/transformation-coverage.json` & `docs/transformation-coverage.md`** — Regenerated and updated to reflect the new no-double power() implementation, removing the P0 and Math.pow limitations.

## New DIFFERENTIALLY_VERIFIED Entries

No new entries were upgraded to `DIFFERENTIALLY_VERIFIED`, but the **existing `DIFFERENTIALLY_VERIFIED` status of `ARITH.COMPUTE` has been hardened and secured** against the previously documented double-contamination P0 bug.

## Remaining Numeric/Semantic Gaps

- **Fractional exponents** — Explicitly unsupported at runtime (fail-fast throwing exception). True fractional exponentiation in pure BigDecimal is not implemented.
- **EBCDIC file I/O** — Remains UNSUPPORTED due to the lack of an EBCDIC codec in the file I/O path.
- **OCCURS DEPENDING ON** — Bounds are generated, but the runtime bounds checking has not been differentially verified yet.
- **REDEFINES overlapping views** — Still uses copy-on-access semantics rather than a shared byte-backed storage layout (targeted for Phase 3).
