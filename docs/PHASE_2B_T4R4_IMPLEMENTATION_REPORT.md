# T-2B-04R.4 — OCCURS / ODO / level-88 Parser Slice — Implementation Report

## 1. Objective

Extend the deterministic, syntax-only V2 parser (T-2B-04R.2/R.3
baseline) with three structural data-item clause features:

- **OCCURS** (fixed-count form `OCCURS n TIMES` and range form
  `OCCURS l TO u TIMES`, TIMES optional)
- **ODO** — `OCCURS ... DEPENDING ON <name>`
- **Level-88 condition names** (`88 <cond-name> VALUE <literal>.`)

R.4 is syntax-only, consistent with R.2/R.3.  It does NOT resolve
symbols, validate OCCURS bounds, bind the DEPENDING ON identifier to
an indexed object, compute array layout or storage sizes, interpret
condition VALUES, or build the semantic DataItem hierarchy.

R.4 adds NO new IR vocabulary: `OCCURS_CLAUSE`, `ODO_CLAUSE`, and
`LEVEL_88_ITEM` already exist as `IRKind` members and are classified
by `is_data_item_kind`.

## 2. Files Created

| File | Purpose |
|---|---|
| `tests/v2/test_parser_r4_occurs_odo_level88.py` | R.4 suite (48 tests) |
| `docs/PHASE_2B_T4R4_IMPLEMENTATION_REPORT.md` | This report |

## 3. Files Modified

| File | Change |
|---|---|
| `modernize_v2/parser/nodes.py` | New frozen `OccursClause`, `OdoClause`, `Level88Declaration` nodes; additive `occurs_clause` / `odo_clause` fields on `DataItemDeclaration`; `CompilationUnit.data_items` type widened to `Tuple[Union[DataItemDeclaration, Level88Declaration], ...]` |
| `modernize_v2/parser/parser.py` | `_match_data_item_declaration` now returns a 12-tuple (`+ occurs_clause, odo_clause, clause_diags`); new OCCURS branch in the clause loop; new `_parse_occurs_clause()`; level-88 handling at the call site; call-site diagnostics for malformed clauses |
| `modernize_v2/parser/__init__.py` | Export `Level88Declaration`, `OccursClause`, `OdoClause` |

## 4. Files Intentionally NOT Modified

**FROZEN T-2B-02 lexer (byte-identical):**
- `modernize_v2/lexer/lexer.py` , `tokens.py`, `keywords.py`, `__init__.py`
- `tests/v2/test_lexer.py`, `tests/v2/test_lexer_tokens.py`

**V1 production code (zero tracked changes, verified via `git diff --name-only -- modernize/`):**
- All files under `modernize/`

## 5. T-2B-02 Freeze Note

`TIMES` is NOT a keyword in the frozen lexer vocabulary and is
emitted as an `IDENTIFIER` token; the parser matches it textually
(case-insensitive).  Numeric literals are also emitted as
`IDENTIFIER` tokens, so the OCCURS count is validated by
digits-only text.  No lexer change was required or made.

## 6. IR Vocabulary Reuse

`IRKind.OCCURS_CLAUSE`, `IRKind.ODO_CLAUSE`, `IRKind.LEVEL_88_ITEM`
existed before R.4 (`modernize_v2/ir/kinds.py`).  R.4 builds nodes
from exactly these members (`node.kind is IRKind.X`).  A regression
test snapshots `DATA_ITEM_KINDS` to its baseline 11-member set.

## 7. Representational Decisions

- `OccursClause(node_id, kind, span, occurs, lower_bound, upper_bound)`:
  exactly one form populated — `occurs` (fixed) XOR
  `lower_bound`/`upper_bound` (range).  Missing `TIMES` is accepted.
- `OdoClause(node_id, kind, span, identifier)`: `identifier` is the
  verbatim source word; NO symbol resolution.
- `Level88Declaration(node_id, kind, span, level=88, name,
  value_clause)`: a dedicated node that REMAINS in the flat,
  source-ordered `data_items` tuple — this is required by the R.2
  contract (`test_r2_level_88_recognized`).  Hierarchy is NOT
  constructed (T-2B-05 concern).
- `OccursClause`/`OdoClause` are siblings on `DataItemDeclaration`
  additive fields (T4R §5.1 design).  The OCCURS span ends before
  the ODO text begins; each clause carries its own span.

## 8. Diagnostics (recovery, no silent swallowing)

All new diagnostics are `ERROR` severity / `PARSER_RECOVERY` kind:

| Condition | Message |
|---|---|
| OCCURS with no integer count | `OCCURS: missing integer count` |
| `OCCURS n TO` without upper count | `OCCURS: range requires an upper count after TO` (recovered as fixed count) |
| `DEPENDING` not followed by `ON` | `OCCURS: DEPENDING must be followed by ON` |
| `DEPENDING ON` at EOF / without identifier | `OCCURS: DEPENDING ON requires an identifier` |
| Level-88 without VALUE | `level-88: missing VALUE clause` |
| Level-88 with a non-VALUE clause | `level-88: only a VALUE clause is valid on a condition name` |

Valid declarations produce zero diagnostics
(`result.ast.diagnostics == ()`).

## 9. Verification

CLI: `python -m pytest tests/v2 -q`

| Suite | Result |
|---|---|
| Full V2 (`tests/v2`, incl. R.4) | **542 passed** (494 baseline + 48 new) |
| R.4 suite (new) | **48 passed** |
| R.3 slice + hardening + R.2/R.1 + invariants + spans + determinism + recovery + kinds | **228 passed** |

No V1 modules or tests were modified; the V1 tree has zero tracked
changes (`git diff --name-only -- modernize/` is empty).

Lint: `ruff` is not installed in this environment (`ruff: The term
'ruff' is not recognized`); linting was NOT executed.  NOT VERIFIED.

## 10. Architectural Audit

- No filesystem I/O in parser (`open(`, `Path(`, `os.open/read/write` absent from changed regions; guarded by test)
- No V1 imports in `nodes.py` / `parser.py` (guarded by test)
- No new `Dict[str, Any]` public contracts (guarded by test)
- Frozen dataclasses for all new nodes (guarded by test)
- Deterministic node IDs via existing infrastructure (guarded by tests)
- Syntax-only: no symbol resolution, no layout, no Java mapping (guarded by tests)
- No new IR kinds (guarded by snapshot test)

## 11. Known Limitations

1. **OCCURS bounds not validated**: `OCCURS 0`, `OCCURS 10 TO 1`, and
   non-integer counts beyond the digits check are not checked.  Bound
   validation is a semantic (T-2B-05/T-2B-06) concern.
2. **DEPENDING ON identifier is unresolved**: stored verbatim only;
   no check that the target data item exists (T-2B-04/T-2B-06).
3. **Level-88 VALUES are not interpreted**: `VALUE 20 THRU 99` range
   values surface as baseline R.3 value-clause text; the `THRU`
   token yields the pre-existing unknown-token diagnostic.  VALUE
   interpretation is out of R.4 scope.
4. **Repeat/duplicate clause detection**: a second OCCURS stops the
   clause loop and falls through to the normal dispatch, which
   reports the leftover tokens (same fall-through policy R.3 uses
   for duplicate PIC/USAGE/VALUE).

## 12. Deviations from Design

None.  The one design refinement versus the earlier R.4 plan is that
level-88 nodes stay in the flat `data_items` tuple (required by the
existing `test_r2_level_88_recognized` contract) instead of moving to
a separate collection.  This was verified during requirements
inspection (FACT, not a silent change).

## 13. Final Verdict

**R.4: PASS (uncommitted, ready for review)**

All 542 V2 tests pass, the frozen T-2B-02 lexer and the V1 tree are
untouched, and the extension is syntax-only as required.  Changes are
left unstaged for review; no commit was created.

Recommended next steps:
- T-2B-05: semantic DataItem tree / hierarchy + OCCURS layout semantics
- T-2B-06: layout computer
- T-2B-04 identifier resolution and qualification

### T-2B-04R.4 Result

| Item | Status |
|---|---|
| Fixed-count OCCURS (`n TIMES`, `TIMES` optional) | PASS |
| Range OCCURS (`l TO u TIMES`) | PASS |
| OCCURS DEPENDING ON (ODO), syntactic identifier | PASS |
| Level-88 condition-name nodes (dedicated, in `data_items`) | PASS |
| Clause coexistence / ordering (PIC, USAGE, VALUE, OCCURS) | PASS |
| Exact byte spans (OCCURS, ODO, item, level-88) | PASS |
| Determinism (IDs, repeated parse, two-parse equivalence) | PASS |
| Immutability (frozen nodes) | PASS |
| IR vocabulary reuse (no new kinds) | PASS |
| Malformed OCCURS / ODO / level-88 recovery diagnostics | PASS |
| Zero false-positive diagnostics on valid declarations | PASS |
| T-2B-02 lexer freeze preserved | PASS |
| V1 tree untouched (zero tracked changes) | PASS |
| Lint (ruff) | NOT VERIFIED (tool not installed) |
| Commit | NOT PERFORMED (left unstaged per rule) |

**Status: PASS**