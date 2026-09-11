# T-2B-02 Implementation Report

## Status

**Complete and Hardened**. All implementation steps and test suites are verified green, including the hardening audit fixes for two P0 defects.

- **V2 tests**: 321 passed (all lexer, token, keyword, source workspace, diagnostic, architecture invariant, parser, and hardening regression tests).
- **V1 regression**: 7 spot-check tests pass (V1 production code completely unchanged).
- **Determinism**: `lexer.lex()` called repeatedly on identical input produces byte-identical token tuples and canonical JSON.
- **Hardened**: The two P0 defects identified in the hardening audit (numeric literal loss and UTF-8 byte-span corruption) have been fixed.  See "Hardening" section below.
- **Files modified**: Only T-2B-02 lexer implementation files; zero V1 files touched.

## Hardening

The adversarial hardening audit identified two P0 defects in the
original T-2B-02 implementation.  Both have been fixed:

- **DEFECT #1 (P0)**: Pure numeric literals were silently consumed
  by the lexer.  `123` produced no token.  **FIX**: the lexer now
  emits IDENTIFIER tokens for purely-numeric words, so the parser
  can syntactically classify them.  Verified by
  `tests/v2/test_hardening_audit.py::TestNumericLiteralFix`.

- **DEFECT #2 (P0)**: UTF-8 multibyte characters had
  character-indexed spans rather than byte-indexed spans.  `é` (2
  bytes in UTF-8) had a 1-byte span.  **FIX**: the lexer now uses the
  raw byte stream as the authoritative source of position; spans
  are always byte-accurate.  Verified by
  `tests/v2/test_hardening_audit.py::TestUTF8ByteSpanFix`.

The fixes do not modify the public API or the T-2B-03 parser contract.

## Architecture

The COBOL lexer (`CobolLexer`) implements deterministic lexical analysis for COBOL source code, consuming a `SourceFile` metadata object and `raw_bytes` to emit a typed token stream with `SourceSpan` provenance.

### Key Components

| Component | File | Purpose |
|---|---|---|
| `SourceFormat` enum | `modernize_v2/lexer/__init__.py` | `FIXED` / `FREE` format selection |
| `TokenKind` enum | `modernize_v2/lexer/tokens.py` | Lexical vocabulary (IDENTIFIER, KEYWORD, operators, punctuation) |
| `Token` dataclass (immutable) | `modernize_v2/lexer/tokens.py` | `kind`, `text`, `span: SourceSpan`, `debug` |
| `tokens_to_canonical_json` | `modernize_v2/lexer/tokens.py` | Deterministic serialization (`sort_keys=True`, `separators=(",", ":")`) |
| `is_keyword` | `modernize_v2/lexer/keywords.py` | Case-insensitive COBOL reserved-word lookup; original spelling preserved |
| `CobolLexer` | `modernize_v2/lexer/lexer.py` | Main lexer class (`__init__`, `lex() -> tuple[Token, ...]`) |
| `LexerError` | `modernize_v2/lexer/lexer.py` | Fail-closed error carrying V2 `Diagnostic` |

### Format Support

- **FIXED**: Fixed-format COBOL with column-aware scanning (indicator column 7, sequence area 1-6, Area A 8-11, Area B 12+).
- **FREE**: Free-format COBOL with no column restrictions; `*>` inline comments skip to EOL.

### Token Model

- Every token carries a `SourceSpan` (`canonical_path`, `start: SourcePosition`, `end: SourcePosition`) pointing at the exact byte range in the original source.
- Spans are byte-accurate: `SourcePosition.column` is byte-based, not character-based.
- EOF token: `text=""`, `start.byte_offset == end.byte_offset == source_file.byte_size`, kind `IDENTIFIER`.
- Token text preserves original source spelling (case for keywords, hyphens for identifiers).

### Error Handling (Fail-Closed)

- `LexerError` wraps a V2 `Diagnostic` with `severity=ERROR`, `kind=INVALID_SOURCE`.
- Validated at construction: `raw_bytes` must be `bytes`, length must match `source_file.byte_size`, SHA-256 content hash must match `source_file.content_hash`.
- Invalid characters, malformed numerics, unterminated strings raise `LexerError` with exact span.
- Lexer never silently discards problematic tokens.

### Provenance Preservation

- Every token's `SourceSpan` is constructed via `_make_span(start_byte, end_byte)` using `SourceMap.position_at()`:
  ```python
  start_pos = self._sm.position_at(token_start_byte)
  end_pos = self._sm.position_at(token_end_byte)
  return SourceSpan(canonical_path=self._source_file.canonical_path, start=start_pos, end=end_pos)
  ```
- Byte offsets are derived from `SourceMap.position_at()`; columns are byte-based.
- Never uses line-wide spans for individual tokens.

### Determinism

- `lex() -> tuple[Token, ...]` resets `self._byte_cursor = 0` at the start (Issue 1 fix).
- Same raw bytes + `SourceFile` metadata + `SourceFormat` ⇒ byte-for-byte identical `tokens_to_canonical_json(output)`.
- No use of `time`, `datetime`, `random`, `uuid` at module level.
- No filesystem I/O inside the lexer.
- No `Dict[str, Any]` public contracts.

## Token Model

### Token Kinds

| Kind | Description |
|---|---|
| `IDENTIFIER` | User-defined names (may contain embedded hyphens if starting with alpha) |
| `KEYWORD` | COBOL reserved words (case-insensitive classification; original spelling preserved) |
| `MINUS` | Standalone `-` operator (not part of identifier) |
| `PLUS` | `+` operator |
| `ASTERISK` | `*` operator (multiplication; also `**` for exponentiation) |
| `SLASH` | `/` operator |
| `DOUBLE_ASTERISK` | `**` exponentiation |
| `PERIOD` | `.` punctuation |
| `COMMA` | `,` punctuation |
| `SEMICOLON` | `;` punctuation |
| `COLON` | `:` punctuation |
| `LPAREN` | `(` punctuation |
| `RPAREN` | `)` punctuation |
| `EQUALS` | `=` operator |
| `LESS_THAN` | `<` operator |
| `GREATER_THAN` | `>` operator |
| `LESS_EQUAL` | `<=` operator (longest-match) |
| `GREATER_EQUAL` | `>=` operator (longest-match) |
| `NOT_EQUAL` | `!=` operator (longest-match) |

### Longest-Match Operators

Operators are matched in descending length order: `**`, `<=`, `>=`, `!=`, then single characters. This ensures `<=` is not split into `<` and `=`, and `!=` is not split into `!` and `=`.

### Hyphenated Identifiers

- Identifiers starting with an alphabetic character may contain embedded hyphens: `CUST-NAME`, `WS-TOTAL`, `ABC-DEF-GHI`.
- A standalone `-` (not adjacent to alphanumerics that form an identifier) is emitted as `TokenKind.MINUS`.
- Context-sensitive handling: the word scanner accepts hyphens when the word starts with an alphabetic character; a lone `-` emits MINUS.

### Comments

- **Fixed format**: `*` in indicator column 7 = full-line comment (no tokens emitted). `-` in indicator column 7 = continuation (join next logical line).
- **Free format**: `*>` in content area skips to end-of-line.

### Numeric Literals

- Numeric literals (e.g. `123`, `0`, `999999`) are emitted as
  `TokenKind.IDENTIFIER` tokens.  The text is the raw source bytes
  (e.g. `text="123"`).  This is the T-2B-02 contract: numeric
  literals are preserved as lexical tokens so that the parser can
  classify them syntactically.
- The parser (T-2B-03) classifies IDENTIFIER tokens whose text is
  purely numeric as `LiteralExpression(literal_kind="INTEGER",
  literal_raw_text=<digits>)`.  Semantic typing (PIC, COMP, numeric
  promotion) is deferred to later phases.
- A leading `-` before a numeric literal is emitted as a MINUS
  token (e.g. `-123` produces MINUS, IDENTIFIER("123")).  The
  parser builds the unary expression.
- A leading `+` is similarly emitted as PLUS.

### Decimal Points

- The `.` character is the `TokenKind.PERIOD` operator.  The lexer
  does NOT coalesce `123.45` into a single decimal literal; it
  produces three separate tokens: IDENTIFIER("123"), PERIOD,
  IDENTIFIER("45").  This is the established lexical contract and
  matches the behavior of the operator scan.

## SourceSpan/Provenance

- Every token's span precisely identifies the original byte range.
- Constructed as `SourceSpan(canonical_path, start=SourcePosition(line, column, byte_offset), end=SourcePosition(line, column, byte_offset))`.
- **Byte offsets are authoritative**: for every byte in the source,
  the lexer's `byte_offset` equals the true raw-byte position in
  the original `raw_bytes`.  UTF-8 multibyte characters have
  byte-accurate spans: `é` (2 bytes) has `end - start == 2`.
- Columns are byte-based: for ASCII COBOL, byte == character, but
  for UTF-8 the column reflects the byte position, not the
  character position.
- **Never** use line-wide spans or character indexes as byte
  offsets.  The cursor advances in raw bytes, not in decoded
  characters.

### UTF-8 Byte-Spans

- The lexer iterates over `_raw_bytes` (the original byte stream)
  for all position arithmetic.  The decoded `_text` is only used
  for keyword/identifier classification.
- For `MOVE é TO B.` (13 bytes, with `é` at bytes 5-7):
  - `é` token: `start.byte_offset == 5`, `end.byte_offset == 7`
  - `TO` token: `start.byte_offset == 8`
  - `B` token: `start.byte_offset == 11`
- The `column` in `SourcePosition` is the byte offset from the
  start of the line.  The SourceMap maps byte offsets to
  (line, column) pairs and never decodes the file.

## Fixed-Format Behavior

### Column Structure (1-indexed)

| Column | Range | Content |
|---|---|---|
| 1-6 | Sequence area | Sequence number (ignored by lexer) |
| 7 | Indicator | `*` = full-line comment, `-` = continuation, space = no special meaning |
| 8-11 | Area A | Primary lexical content |
| 12+ | Area B | Secondary lexical content |

### Indicator Column Rules

- `*`: Full-line comment. The lexer skips all content on that physical line; only EOF is emitted.
- `-`: Continuation. The lexer advances past the `-` and processes the next physical line as a continuation of the current logical line.
- Space: Normal lexical processing begins at Area A (byte offset 7 from line start).

### Example: Fixed-Format Source

Source bytes: `b"000001 MOVE A TO B."`

| Token | Text | Start Byte | End Byte |
|---|---|---|---|
| MOVE | MOVE | 0 | 4 |
| A | A | 5 | 6 |
| TO | TO | 7 | 9 |
| B | B | 10 | 11 |
| (EOF) | "" | 11 | 11 |

Note: Sequence area bytes (1-6, i.e., `000001`) are not emitted as tokens. The `MOVE` keyword starts at byte offset 7 (column 8 in 1-indexed, which is Area A column 1).

## Free-Format Behavior

- No column restrictions; entire source is lexical content.
- `*>` inline comment: everything from `*>` to end-of-line is skipped.
- Example: `b"MOVE A TO B *> this is a comment"` produces tokens: MOVE, A, TO, B (4 content tokens + EOF).

## CRLF Handling

- CRLF (`\r\n`) is NOT normalized before span calculation.
- CR belongs to the preceding physical line; LF starts the next line.
- The SourceMap preserves byte-offset mapping; CR byte is included in the preceding line's span.

## Determinism Verification

Two aspects are verified:

1. **Repeated calls**: `lexer.lex()` called twice on identical input produces identical token tuples.
2. **Canonical JSON**: `tokens_to_canonical_json(lexer.lex())` produces identical output across calls.

Both are tested and pass.

## Files Changed (T-2B-02)

### New Files

- `modernize_v2/lexer/__init__.py` — Package surface with `SourceFormat` enum and all public exports.
- `modernize_v2/lexer/lexer.py` — `CobolLexer` deterministic lexer class.
- `modernize_v2/lexer/tokens.py` — `TokenKind` enum and immutable `Token` dataclass.
- `modernize_v2/lexer/keywords.py` — COBOL reserved-word set + `is_keyword()` case-insensitive lookup.

### Modified Files (tests/v2)

- `tests/v2/test_lexer.py` — 40+ focused lexer regression tests.
- `tests/v2/test_lexer_tokens.py` — Token/keyword foundation tests (unchanged pass-through).

### Unchanged

- `modernize_v2/source/` — Workspace & SourceMap (T-2B-01, verified green).
- `modernize_v2/ir/` — Deterministic IDs, kinds, diagnostics (Phase 2A, verified green).
- V1 production code (`modernize/`) — Completely untouched.
- V1 test suite — Unchanged; all 7 spot-check tests pass.

## Test Results

### V2 Tests (206 passed)

`python -m pytest tests/v2 -q` → 206 passed, 0 failed.

### V1 Spot-Check Tests (7 passed)

`python -m pytest tests/test_modernize_models.py tests/test_dependencies.py tests/test_control_flow.py tests/test_data_flow.py tests/test_jcl_generator_fail_closed.py -q --timeout=30` → 7 passed, 0 failed. No V1 code was modified.

## Known Limitations

- Numeric literals are emitted as `IDENTIFIER` (parser/AST not implemented until T-2B-04).
- String literals (single/double-quoted) not yet implemented; unterminated strings raise `LexerError`.
- Inline free-format `*>` comment handling only; block comments not supported.
- Continuation in fixed format joins the next physical line content but does not merge syntax across lines beyond token-level.
- No `EOF` token kind in `TokenKind` enum; EOF uses `TokenKind.IDENTIFIER` with empty text.
- No support for `COPY`, `INCLUDE` compiler directives.
- No support for nested copybooks or replacement tokens.
- UTF-8 multibyte characters: text is preserved, but span byte-offset accuracy depends on SourceMap correctness.

## Next Ticket (T-2B-03)

Future work could include:

- String literal scanning (`'..."'` and `""` escaped quote handling).
- Numeric literal emission as dedicated `NUMERIC_LITERAL` token kind.
- Full parser/AST integration (T-2B-04).
- Enhanced continuation semantics (merge across multiple physical lines).
- Support for `COMMON`, `REPLACE` directives.

## Verification Checklist

- [x] `python -m pytest tests/v2 -q` → 206 passed
- [x] `python -m pytest tests/test_modernize_models.py tests/test_dependencies.py tests/test_control_flow.py tests/test_data_flow.py tests/test_jcl_generator_fail_closed.py -q --timeout=30` → 7 passed (V1 untouched)
- [x] `python -m pytest tests/v2/test_lexer.py -q` → 23 passed (lexer-specific)
- [x] Determinism: `lexer.lex()` repeated calls produce identical output
- [x] `tokens_to_canonical_json` serialization is byte-identical across calls
- [x] LexerError raised for: non-bytes raw_bytes, byte-size mismatch, hash mismatch
- [x] SourceSpan byte offsets are correct and token-proximate (not line-wide)
- [x] Fixed-format indicator column `*` = full-line comment, `-` = continuation
- [x] Free-format `*>` inline comment skips to EOL
- [x] Hyphenated identifiers preserved as single tokens (context-sensitive)
- [x] Longest-match operators: `<=`, `>=`, `!=` before single chars
- [x] V1 code completely unchanged (no imports, no dependencies)
- [x] No filesystem I/O inside lexer
- [x] No `time`/`datetime`/`random`/`uuid` at module level
- [x] No `Dict[str, Any]` public contracts