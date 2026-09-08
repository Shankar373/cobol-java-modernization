# T-2B-02/T-2B-03 Hardening Audit Report

**Date**: Adversarial hardening audit conducted after T-2B-03 implementation.
**Status**: P0 defects identified, fixed, and verified.  See "Resolution" section.

## 1. Contract Findings

### Documented Contracts

**From T-2B-02 Implementation Report (`PHASE_2B_T2B02_IMPLEMENTATION_REPORT.md`):**
- Line 109: *"Numeric literals are conservatively emitted as IDENTIFIER tokens for T-2B-02 (parser/AST not implemented in this phase)."*
- Line 117: *"Never use line-wide spans or character indexes as byte offsets."*
- Line 36: *"Spans are byte-accurate: SourcePosition.column is byte-based, not character-based."*

**From T-2B-03 Implementation Report (`PHASE_2B_T3_IMPLEMENTATION_REPORT.md`):**
- Line 320: *"The T-2B-02 lexer does NOT emit tokens for purely numeric text (e.g., 123). The parser inherits this behavior."*
- Line 322: *"The T-2B-02 lexer does not produce fully byte-accurate spans for multibyte UTF-8 characters."*

### Original Actual Behavior (Pre-Hardening)

| Contract | Documented | Original Actual |
|---|---|---|
| Numeric literals as IDENTIFIER | Yes (line 109) | NO — silently dropped |
| UTF-8 byte-accurate spans | Yes (line 117) | NO — character-indexed |
| Column is byte-based | Yes (line 36) | NO — char-based for UTF-8 |

**Key finding**: The T-2B-02 implementation report and actual implementation were **contradictory** for numeric literals and UTF-8 byte spans.

## 2. Numeric Literal Findings (Pre-Hardening)

### Defect Proven: `test_defect_123_silently_lost`

```python
sf = make_source_file("t.cbl", b"123")
lexer = CobolLexer(sf, b"123", SourceFormat.FREE)
tokens = lexer.lex()
# tokens has ONLY 1 token: the EOF sentinel
# The number "123" is silently consumed.
```

**Root cause**: `modernize_v2/lexer/lexer.py:282-303`:
```python
if word_len > 0 and word_str and word_str[0].isalpha():
    # ... emit token
elif word_len == 1 and word_str == '-':
    # ... emit MINUS
# else: silently advance cursor, no token emitted
```

A bare numeric word (e.g., `123`, `0`, `999999`) never satisfies `word_str[0].isalpha()` and is therefore not emitted as a token.

### Impact on Real COBOL Constructs

| Construct | Expected Tokens | Actual Tokens | Defect |
|---|---|---|---|
| `MOVE 123 TO B.` | 6 (MOVE, 123, TO, B, ., EOF) | 5 (MOVE, TO, B, ., EOF) | `123` missing |
| `ADD 10 TO B.` | 6 | 5 | `10` missing |
| `COMPUTE X = A + 123.` | 8 | 7 | `123` missing |
| `MOVE 123.45 TO B.` | 6 | 6 (MOVE, ., TO, B, ., EOF) | Both `123` and `45` missing; `.` tokenized as PERIOD |

### Parser Impact

The parser's `_parse_primary()` at `parser.py:1153` checks `tok.text.isdigit()`:
```python
if tok.kind == TokenKind.IDENTIFIER and tok.text.isdigit():
    return self._consume_numeric_literal(tok)
```

But this code path is **dead** because the lexer never produces IDENTIFIER tokens with purely numeric text.

This means the parser **cannot** produce `LiteralExpression(INTEGER)` nodes for numeric literals in actual COBOL source. The `LiteralExpression` node class exists in the AST but is unreachable for numeric source.

## 3. UTF-8 Byte-Span Findings

### Defect Proven: `test_defect_e_acute_byte_span_wrong`

```python
source = b"MOVE \xc3\xa9 TO B."  # é is 2 bytes in UTF-8
lexer = CobolLexer(sf, source, SourceFormat.FREE)
# é is at bytes 5-7 in the source (0xc3 at 5, 0xa9 at 6, next byte at 7)
# The lexer reports span=[5, 6) — only 1 byte wide
# This is character-indexed, not byte-indexed
```

**Root cause**: `modernize_v2/lexer/lexer.py:231-316` operates on `self._text` (a Python `str`), not on `self._raw_bytes`. The word-collection loop:
```python
while word_len < len(remaining):  # len() on str is char count
    ch_byte = remaining[word_len:word_len + 1]
    if ch_byte.isalnum() or ch_byte == '-':
        word_len += 1
    else:
        break
```
advances `word_len` by character count, not byte count. Then `self._byte_cursor += word_len` advances the byte cursor by the same (wrong) count.

### Impact

| Source | Expected byte span | Actual byte span | Status |
|---|---|---|---|
| `MOVE é TO B.` (13 bytes) | é at [5,7), TO at [8,9) | é at [5,6), TO at [7,9) | DEFECT |
| `MOVE € TO B.` (14 bytes) | € at [5,8), TO at [9,11) | € at [5,6), TO at [7,9) | DEFECT |
| `ABC-中文` (10 bytes) | whole at [0,10) | whole at [0,9) | DEFECT |

This is a **silent byte-offset corruption** that affects:
- All UTF-8 source content
- Any tool that depends on byte-accurate spans (compilation, codegen, etc.)

## 4. EOF Findings

### EOF Contract: WORKING CORRECTLY

The EOF sentinel is correctly produced as:
- `TokenKind.IDENTIFIER`, `text=""`, `span.start.byte_offset == span.end.byte_offset == byte_size`

The parser correctly detects EOF via `is_eof_token()` and never produces `IdentifierExpression(identifier_text="")`.

Tests: `test_eof_sentinel_correct`, `test_eof_after_content`, `test_eof_with_crlf` all pass.

## 5. Parser Boundary Findings

### Parser is Syntax-Only: VERIFIED

The parser:
- Does NOT import or use `DataItemId`, `JavaTypeRef`, `Layout`, `CobolType`
- Does NOT perform symbol resolution
- Does NOT perform type checking
- Does NOT generate Java code
- Does NOT perform runtime emulation

Verified by:
- AST field analysis (no semantic fields in any node class)
- Import analysis (no V1 imports, no forbidden modules)

## 6. Unsupported Feature Findings

### Unsupported Construct Detection: WORKING CORRECTLY

The parser correctly diagnoses:
- READ, WRITE, REWRITE, DELETE, START → UNSUPPORTED_FEATURE
- SORT, MERGE → UNSUPPORTED_FEATURE
- PERFORM VARYING/UNTIL/TIMES → UNSUPPORTED_FEATURE
- EXEC SQL/CICS → UNSUPPORTED_FEATURE
- Unknown keywords → PARSER_RECOVERY diagnostic

The parser continues to parse sibling statements after encountering unsupported constructs. Recovery is deterministic.

## 7. Determinism Findings

### Determinism: VERIFIED

- Repeated `parse()` calls on same instance: identical
- Two separate parser instances on same tokens: identical
- Two separate lexer+parser chains on same source: identical
- Identical source produces identical node IDs
- No `random`, `uuid`, `time`, `datetime` at module level
- No filesystem I/O

## 8. Defects Proven

### DEFECT #1: Pure Numeric Literals Silently Consumed (P0)

**File**: `modernize_v2/lexer/lexer.py`
**Line**: 282-303
**Severity**: P0 (compiler correctness)

The lexer fails to emit IDENTIFIER tokens for words whose first character is a digit. This violates the documented T-2B-02 contract (line 109 of the implementation report).

**Proof tests** (all in `tests/v2/test_hardening_audit.py`):
- `test_defect_123_silently_lost`
- `test_defect_zero_silently_lost`
- `test_defect_999999_silently_lost`
- `test_defect_move_123_to_b_silently_loses_literal`
- `test_defect_123_45_decimal_silently_lost`
- `test_defect_add_10_silently_loses_literal`
- `test_defect_compute_with_numeric_loses_literal`
- `test_defect_parser_cannot_classify_numeric`

**Impact**:
- Parser cannot produce `LiteralExpression(INTEGER)` for any source number
- The `LiteralExpression` AST node is unreachable for numeric input
- Real COBOL constructs like `MOVE 123 TO X.` are broken at the parser level
- Any downstream code (type checker, codegen) cannot work without a fix

### DEFECT #2: UTF-8 Multibyte Characters Have Wrong Spans (P0)

**File**: `modernize_v2/lexer/lexer.py`
**Line**: 231-316
**Severity**: P0 (compiler correctness)

The lexer operates on `self._text` (decoded str) rather than `self._raw_bytes`. The word-collection loop advances by character count, not byte count, causing byte spans to be character-indexed for multibyte UTF-8 content.

**Proof tests**:
- `test_defect_e_acute_byte_span_wrong`
- `test_defect_lexer_byte_cursor_misaligned_after_e_acute`
- `test_defect_following_token_misaligned_after_e_acute`

**Impact**:
- All UTF-8 source content has corrupted byte spans
- A `é` (2 bytes) has a 1-byte span
- The following token's start position is off by 1 per multibyte char before it
- SourceMap and SourcePosition are designed for byte-accuracy; the lexer violates this

## 9. Files Modified

This audit only **adds** test files; no production code was modified.

| File | Change |
|---|---|
| `tests/v2/test_hardening_audit.py` | NEW (18 tests proving defects) |
| `docs/PHASE_2B_T3_HARDENING_AUDIT.md` | NEW (this report) |

## 10. Regression Tests Added

18 new tests in `tests/v2/test_hardening_audit.py`:
- 8 numeric literal defect tests
- 3 UTF-8 byte-span defect tests
- 3 EOF contract tests (passing)
- 4 syntax adversarial tests (passing)

**Total V2 tests**: 291 (273 existing + 18 new)
**All pass**: Yes

## 11. Test Results

### Full V2 Test Run
```
$ python -m pytest tests/v2 -q
........................................................................ [ 24%]
........................................................................ [ 49%]
........................................................................ [ 74%]
........................................................................ [ 98%]
...                                                                      [100%]
291 passed in 3.34s
```

### V1 Spot Checks
```
$ python -m pytest tests/test_modernize_models.py tests/test_dependencies.py tests/test_control_flow.py tests/test_data_flow.py tests/test_jcl_generator_fail_closed.py -q --timeout=30
7 passed in 0.45s
```

### Hardening Audit Tests
```
$ python -m pytest tests/v2/test_hardening_audit.py -v
18 passed in 0.38s
```

## 12. Final Freeze Decision

## **NOT SAFE TO FREEZE — HARDENING REQUIRED**

Two P0 defects have been proven:

1. **Numeric literals silently consumed by T-2B-02 lexer** — contradicts documented contract, breaks parser, breaks real COBOL
2. **UTF-8 byte spans are character-indexed, not byte-indexed** — corrupts all byte-offset tracking for multibyte content

These defects existed at the time T-2B-02 was reported as "SAFE TO FREEZE" and were carried forward into T-2B-03. The T-2B-03 implementation report acknowledged these as "known limitations" but T-2B-03 was still declared "SAFE TO FREEZE" — which is incorrect because the foundation (T-2B-02) has correctness defects.

### Required Hardening Gate

The HARDENING GATE must be enforced:

```
T-2B-02 correctness (numeric literals, UTF-8 spans)
        ↓
T-2B-03 correctness
        ↓
T-2B-04 (identifier resolution)
```

**Do NOT proceed to T-2B-04** until:
- Defect #1 is fixed: numeric literals are emitted as IDENTIFIER tokens
- Defect #2 is fixed: UTF-8 multibyte chars have correct byte spans

### Required Next Phase

**T-2B-02-HARDENING**: Fix the two proven defects in `modernize_v2/lexer/lexer.py`:
1. Emit IDENTIFIER tokens for purely-numeric words (change the `isalpha()` check)
2. Use byte-based cursor and span calculation (use `self._raw_bytes` indexing, not `self._text`)

After T-2B-02 hardening:
- Re-run all 291 V2 tests
- Verify the 18 hardening audit tests still pass (they prove the defects, so they must be updated to prove the FIXES)
- Update T-2B-02 implementation report to reflect corrected behavior
- THEN proceed to T-2B-04

## 13. Resolution

The two P0 defects identified in this audit have been **fixed** in
`modernize_v2/lexer/lexer.py`.  The original defect-proving tests in
`tests/v2/test_hardening_audit.py` were transformed into regression
tests that prove the **fixes**:

- `TestNumericLiteralFix`: proves that `123`, `0`, `999999`,
  `000123`, `MOVE 123 TO B.`, `ADD 10 TO B.`,
  `COMPUTE WS-TOTAL = WS-A + 123.`, `-123`, `+123`, and `123.45`
  all now produce the correct token stream.  All 11 tests pass.
- `TestUTF8ByteSpanFix`: proves that `é` (2 bytes), `€` (3 bytes),
  `中文` (6 bytes), and `ABC-中文` (10 bytes) all have correct
  byte-accurate spans.  The following token's start position is
  also correct.  All 7 tests pass.
- `TestEOFSentinelFix`, `TestCRLFPreservationFix`,
  `TestFixedFormatPreservationFix`, `TestDeterminismPreservationFix`:
  verify that the contract that was working correctly before
  hardening is preserved unchanged.  All 15 tests pass.

Additional edge-case tests are in
`tests/v2/test_hardening_edge_cases.py` (15 tests, all pass).

### After-Hardening Actual Behavior

| Contract | Documented | After-Hardening Actual |
|---|---|---|
| Numeric literals as IDENTIFIER | Yes | YES — emitted verbatim |
| UTF-8 byte-accurate spans | Yes | YES — raw-byte based |
| Column is byte-based | Yes | YES — byte-based for UTF-8 |
| EOF sentinel at byte_size | Yes | YES — unchanged |
| CRLF preserved | Yes | YES — unchanged |
| Fixed-format sequence area | Yes | YES — unchanged (skipped) |

### Resolution Required Next Phase

The T-2B-02 hardening gate is **now passed**:

```
T-2B-02 correctness (numeric literals, UTF-8 spans)  ← FIXED
        ↓
T-2B-03 correctness                                    ← UNCHANGED, STILL VALID
        ↓
T-2B-04 (identifier resolution)                       ← SAFE TO PROCEED
```

**Both P0 defects are fixed and verified.**  T-2B-03 parser
correctness is unchanged (its contract with T-2B-02 was satisfied;
the lexer was the broken piece).

### Test Results After Hardening

- 321 V2 tests pass (273 pre-hardening + 33 hardening regression
  + 15 hardening edge cases)
- 7 V1 spot-check tests pass (V1 unchanged)

## 14. Final Verdict (After Hardening)

**The two P0 defects identified in the original audit have been
fixed.  The lexer now correctly emits numeric literals as IDENTIFIER
tokens and produces byte-accurate spans for UTF-8 content.  T-2B-02
is hardened.  T-2B-03 is unchanged and remains correct given the
fixed lexer contract.**

**T-2B-02 + T-2B-03: SAFE TO FREEZE**

The compiler foundation is now trustworthy for real-world COBOL
sources.  Work may proceed to T-2B-04 (identifier resolution) on top
of the hardened T-2B-02 lexer.
