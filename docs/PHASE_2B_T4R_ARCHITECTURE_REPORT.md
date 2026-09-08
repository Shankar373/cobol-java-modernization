# T-2B-04R — Architectural Decision Report

**Date**: Architectural evaluation conducted after T-2B-05 was reported blocked.
**Status**: This is a design/decision report only. No code has been written.

---

## 1. Why T-2B-05 Is Blocked

The T-2B-05 ticket's acceptance criterion states:

> *"Names resolve through the `Program → Section → Paragraph → Block` scope chain. Qualified names resolve unambiguously. Unresolved names produce a `Diagnostic(severity=ERROR, kind=UNRESOLVED_SYMBOL)`."*

To produce a `UNRESOLVED_SYMBOL` diagnostic, the resolver must have a *known set* of declarations to compare against. There is no implementation of a declaration model anywhere in the V2 stack.

**Verified facts from the inspection:**

1. **No DataItem class exists.** The `IRKind` enum has `DATA_ITEM`, `GROUP_ITEM`, `ELEMENTARY_ITEM`, `LEVEL_88_ITEM` declared as vocabulary, but no concrete Python class implements these kinds. There is no `modernize_v2/ir/data_item.py` file.

2. **The T-2B-03 parser does not parse data-item declarations.** For source `01 WS-A PIC X(10).` the parser produces three "unknown token" diagnostics (`WORKING-STORAGE`, `01`, `01`). The data item is never represented in the AST.

3. **The T-2B-03 parser does not parse paragraph-definition headers.** The only paragraph names that exist in the AST are forward references in `PerformStatement.paragraph_name` and `GoToStatement.target`. There is no node that represents a paragraph label (e.g. `MAIN-PARA.` starting a paragraph).

4. **The T-2B-03 parser does not represent qualified names.** For source `MOVE A OF B TO C.` the parser raises an `ValueError: expected 'TO', got 'OF'`. The `OF` operator is not recognized.

5. **The T-2B-03 parser does not have access to raw source bytes.** Its `__init__` signature is `(tokens, canonical_path)`. It cannot re-scan the source for declarations.

6. **T-2C-0A does not provide declarations.** Its `ScopeGraph` has only `program, scopes, references, forward_referenced_paragraphs, paragraph_detection_available`. There is no `declarations` field.

7. **T-2C-0A made an architectural deviation.** It used `ScopeKind.SECTION` because the parser emits division-level headers, but the architecture §8.1 specifies `Scope (id, kind: Program|Paragraph|Block|File)` — **no `SECTION` kind**. This deviation is pre-existing and must be addressed by any parser extension that produces real paragraph scope.

---

## 2. Exact Parser Capabilities Currently Missing

The T-2B-03 implementation report explicitly documents what is *not* supported. From the "Known Limitations" section of `docs/PHASE_2B_T3_IMPLEMENTATION_REPORT.md`:

> *"3. Data Division parsing: Structural recognition only. No PIC/USAGE/OCCURS/REDEFINES parsing."*

The T-2B-03 ticket is **frozen** with this exact limitation. The parser explicitly produces:
- 4 division-header strings (`IDENTIFICATION DIVISION`, `ENVIRONMENT DIVISION`, `DATA DIVISION`, `PROCEDURE DIVISION`)
- 4 environment-division subsections (`WORKING-STORAGE SECTION`, etc.) as "unknown token" diagnostics
- Data-item declarations (level numbers, names, PIC/USAGE/VALUE clauses) as "unknown token" diagnostics
- No paragraph-definition headers
- No qualified-name AST representation
- No support for `OF`, `IN`, `REDEFINES`, `OCCURS`, `RENAMES`, `88`-level, or other Data Division clause syntax

In other words, the parser is *deliberately* a procedural-statement parser. It does not represent the structural information that T-2B-05 / T-2B-06 require.

---

## 3. Proposed Parser-Extension Architecture

### 3.1 The architectural principle being violated

The V2 architecture §6 states: *"Canonical typed IR is the single source of truth."* The principle is that all structural information about the program should be in one well-typed AST produced by the parser. Semantic phases (resolution, type-checking) consume the AST; they do not re-parse source.

The current parser violates this principle for any program with a Data Division: the Data Division's structural information is *not* in the AST. The only way to recover it would be to re-parse the source, which is forbidden by the architecture.

### 3.2 The only architecturally correct fix

The parser must be extended to represent, in its AST, the structural information required by later semantic phases:

1. **Data Division subsection headers** (`WORKING-STORAGE SECTION`, `LINKAGE SECTION`, `LOCAL-STORAGE SECTION`, `REPORT SECTION`, `FILE SECTION`) — these are currently "unknown token" diagnostics.
2. **Data-item declarations** (`01 NAME PIC X(10).`, `01 NAME REDEFINES OTHER PIC 9(5).`, etc.) — these are also "unknown token" diagnostics.
3. **Paragraph-definition headers** (a paragraph name followed by `.` at the start of a logical line) — these are not detected.
4. **Qualified-name references** (`A OF B`) — these cause a parser crash.
5. **Level-88 condition names** (`88 NAME VALUE THRU.`) — these are "unknown token" diagnostics.

The IRKind enum *already* has all the necessary kinds (`DATA_ITEM`, `GROUP_ITEM`, `ELEMENTARY_ITEM`, `LEVEL_88_ITEM`, `OCCURS_CLAUSE`, `ODO_CLAUSE`, `REDEFINES_CLAUSE`, `RENAMES_CLAUSE`, `WORKING_STORAGE_SECTION`, `LINKAGE_SECTION`, `LOCAL_STORAGE_SECTION`, `REPORT_SECTION`, `FILE_SECTION`, `SECTION`, `PARAGRAPH`).

### 3.3 Whether T-2B-03 must be formally reopened

**Yes.** There is no way to extend the parser's structural coverage without modifying `parser/nodes.py` and `parser/parser.py`. The alternative options (B and C in the user's question) are evaluated below.

---

## 4. Evaluation of the Three Options

### Option A: Formally revise/reopen T-2B-03

**What it means**: Treat T-2B-03 as the *first increment* of a multi-increment parser, explicitly authorize extension tickets (T-2B-04R being the first), and modify `parser/nodes.py` and `parser/parser.py` to add new structural nodes.

**Evaluation against the criteria:**

| Criterion | Assessment |
|---|---|
| Single source of structural truth | **Yes** — all structure in the parser AST |
| Deterministic behavior | **Yes** — new nodes follow the existing deterministic-id pattern |
| No duplicated parser logic | **Yes** — no re-scanning of source bytes |
| Source-span preservation | **Yes** — new nodes carry `SourceSpan` |
| Compatibility with T-2C-0A | **Must be verified** — T-2C-0A reads `ast.divisions` as a tuple of strings. If we change the type of `divisions`, T-2C-0A breaks. **Mitigation**: add a *new* field `division_nodes: tuple[DivisionNode, ...]` alongside the existing `divisions: tuple[str, ...]`. T-2C-0A continues to work; downstream phases consume the new field. |
| Compatibility with T-2B-06 | **Yes** — T-2B-06 then has the structural input it needs |
| Compatibility with T-2B-05 | **Yes** — T-2B-05 then has both references (from T-2C-0A) and declarations (from new parser nodes) |
| Backward compatibility of existing V2 tests | **Must be preserved** — existing 364 tests must continue to pass |
| Enterprise COBOL extensibility | **Yes** — this is the only way to extend the compiler to real COBOL programs |

**Verdict: Option A is the architecturally correct choice.** It preserves all architectural principles, maintains single source of truth, and enables the next-ticket pipeline. It requires human approval because it formally reopens a frozen ticket.

### Option B: Introduce a new parser structural layer after T-2B-03

**What it means**: Keep the current T-2B-03 parser exactly as-is. Add a *second parser* (or a pre-parser / preprocessor) that runs after T-2B-03 and adds the missing structural nodes. The final output is a merged AST.

**Evaluation against the criteria:**

| Criterion | Assessment |
|---|---|
| Single source of structural truth | **No** — there would be two parsers, each producing part of the AST. The merger logic becomes a new source of complexity. |
| Deterministic behavior | **Yes** — could be made deterministic |
| No duplicated parser logic | **No** — the second parser duplicates the T-2B-03 tokenization / parsing logic |
| Source-span preservation | **Yes** — could preserve spans |
| Compatibility with T-2C-0A | **Confusing** — T-2C-0A consumes the T-2B-03 output, not the second-parser output. Where does the second-parser output live? |
| Compatibility with T-2B-06 | **Confusing** — T-2B-06 would have to choose which parser's output to consume |
| Compatibility with T-2B-05 | **Confusing** — same problem |
| Backward compatibility of existing V2 tests | **Yes** — the T-2B-03 tests still pass |
| Enterprise COBOL extensibility | **Marginal** — we now have two parsers to maintain |

**Verdict: Option B creates two sources of truth.** It is rejected. The architecture §6 explicitly requires "single source of truth" and the decision D-01 rejects hybrid approaches.

### Option C: Another architecture already supported by the repository

**Inspection result**: There is no other architecture for parser-extension in the repository. The V2 architecture specifies the parser as the single source of structural truth. There is no pre-existing mechanism for post-parse structural augmentation.

**Verdict: Option C is not applicable.**

### Combined verdict

**Option A is the only architecturally correct choice**, but it requires formal reopening of T-2B-03. This is an architectural decision that needs human approval.

---

## 5. Proposed AST Additions

If Option A is approved, the following new nodes are proposed. They are *additions* to the existing AST — no existing node is removed or replaced.

### 5.1 New division / section nodes

```python
@dataclass(frozen=True)
class DivisionNode:
    """A division or subsection header in the COBOL source."""
    node_id: DeterministicId
    kind: IRKind  # DATA_DIVISION | ENVIRONMENT_DIVISION | IDENTIFICATION_DIVISION
                 # | PROCEDURE_DIVISION | WORKING_STORAGE_SECTION | LINKAGE_SECTION
                 # | LOCAL_STORAGE_SECTION | REPORT_SECTION | FILE_SECTION
    span: SourceSpan


@dataclass(frozen=True)
class DataItemDeclaration:
    """A single data-item declaration entry.

    Captures only the structural information available from the
    parser. PIC/USAGE/value-clause details are emitted as nested
    clause nodes where parseable; otherwise as raw text spans
    reserved for the DataItem constructor (T-2B-06) to refine.
    """
    node_id: DeterministicId
    kind: IRKind  # DATA_ITEM | GROUP_ITEM | ELEMENTARY_ITEM | LEVEL_88_ITEM
    span: SourceSpan
    level: int  # 01-49, 66, 77, 78, 88
    name: str  # the data-item name
    parent: Optional["DataItemDeclaration"] = None  # group/elementary relationship
    # Clausal substructure.  None means the parser did not (yet)
    # support this clause; the T-2B-06 DataItem builder may parse
    # the raw text within the span to recover it.
    pic_clause: Optional["PicClause"] = None
    usage_clause: Optional["UsageClause"] = None
    value_clause: Optional["ValueClause"] = None
    occurs_clause: Optional["OccursClause"] = None
    odo_clause: Optional["OdoClause"] = None
    redefines_target: Optional[str] = None
    renames_target: Optional[str] = None
    linkage: str = "working"  # working | local | linkage | file | report | screen


@dataclass(frozen=True)
class PicClause:
    node_id: DeterministicId
    kind: IRKind  # PICTURE_CLAUSE (or reuse STATEMENT?  -- add new IRKind)
    span: SourceSpan
    pic_string: str  # the raw PIC text, e.g. "X(10)", "9(5)V99", "S9(5)V9(2)"
```

### 5.2 New procedure-structure nodes

```python
@dataclass(frozen=True)
class Section:
    """A Procedure-Division section.

    A section is a named group of paragraphs.  In COBOL, sections
    are declared with ``SECTION.`` and may contain zero or more
    paragraphs.  A program may have paragraphs *outside* of any
    section (these are anonymous / in the "main section").
    """
    node_id: DeterministicId
    kind: IRKind  # SECTION
    span: SourceSpan
    name: str  # the section name; empty string for anonymous
    parent: "ProcedureDivision" = None


@dataclass(frozen=True)
class Paragraph:
    """A Procedure-Division paragraph.

    A paragraph is introduced by a paragraph-name followed by a
    period and contains zero or more sentences (statements).
    """
    node_id: DeterministicId
    kind: IRKind  # PARAGRAPH
    span: SourceSpan
    name: str
    parent_section: Optional[Section] = None
    statements: Tuple[Any, ...] = field(default_factory=tuple)
    # The container this paragraph belongs to: the Section if
    # inside one, otherwise the Procedure-Division itself.
    container: Any = None
```

### 5.3 New expression nodes

```python
@dataclass(frozen=True)
class QualifiedReference:
    """A qualified identifier reference, e.g. ``A OF B``.

    The architecture §8.1 specifies ``Symbol.key = (name, qualification)``.
    This node represents the syntactic structure from which the
    qualification is derived.
    """
    node_id: DeterministicId
    kind: IRKind  # EXPRESSION_REFERENCE (reuse)
    span: SourceSpan
    primary: IdentifierExpression  # the leftmost (innermost) identifier
    qualifications: Tuple[IdentifierExpression, ...]  # subsequent OF qualifiers


@dataclass(frozen=True)
class SubscriptedReference:
    """A subscripted identifier reference, e.g. ``A(I)`` or ``A(I, J)``."""
    node_id: DeterministicId
    kind: IRKind
    span: SourceSpan
    target: IdentifierExpression | QualifiedReference
    subscripts: Tuple[Any, ...]


@dataclass(frozen=True)
class RefModReference:
    """A reference-modification, e.g. ``A(I:L)``."""
    node_id: DeterministicId
    kind: IRKind
    span: SourceSpan
    target: IdentifierExpression | QualifiedReference
    offset: Any  # expression
    length: Any | None  # expression or None
```

### 5.4 Update to `CompilationUnit`

The `CompilationUnit` node already exists. We propose to *add* fields without removing or breaking existing fields:

```python
@dataclass(frozen=True)
class CompilationUnit:
    # ... existing fields unchanged ...
    divisions: Tuple[str, ...]  # UNCHANGED — preserves T-2C-0A compatibility
    statements: Tuple[Any, ...]  # UNCHANGED — preserves T-2C-0A compatibility
    diagnostics: Tuple[Diagnostic, ...]  # UNCHANGED
    recovery_records: Tuple[Any, ...]  # UNCHANGED

    # NEW (additive) — T-2C-0A and the existing tests ignore these.
    division_nodes: Tuple[DivisionNode, ...] = ()
    data_division: Optional["DataDivisionBlock"] = None
    procedure_division: Optional["ProcedureDivisionBlock"] = None
```

This *additive* design preserves backward compatibility: T-2C-0A reads only `divisions` and `statements`, both of which are unchanged. T-2B-06 reads the new fields. T-2B-05 reads both.

### 5.5 Backward compatibility strategy

The strategy is **additive-only**:
- New fields are appended to existing dataclasses (with default values).
- New node types are added in `nodes.py`; existing node types are unchanged.
- `parser/parser.py` is extended with new parsing methods; existing methods are not modified.
- Existing tests in `tests/v2/test_parser.py` and `tests/v2/test_parser_*.py` must continue to pass.

The risk: if any test asserts on the *exact* set of fields of an existing node, adding a field might break it. The fields are added with defaults so this should not happen, but it must be verified.

---

## 6. Proposed Ticket Breakdown

The single monolithic "T-2B-04R" ticket is too large. The following incremental breakdown is proposed:

### 6.1 T-2B-04R.1 — Data Division subsection headers (smallest slice)

**Scope**: Extend the parser to recognize `WORKING-STORAGE SECTION.`, `LINKAGE SECTION.`, `LOCAL-STORAGE SECTION.`, `REPORT SECTION.`, `FILE SECTION.` as new `DivisionNode` AST nodes *only* (no data-item declarations yet). Update `CompilationUnit` to add `division_nodes: tuple[DivisionNode, ...]`.

**Acceptance**: `IDENTIFICATION DIVISION.`, `DATA DIVISION.`, `WORKING-STORAGE SECTION.`, `PROCEDURE DIVISION.` all produce `DivisionNode` entries in `division_nodes`. Existing 364 tests still pass.

**Estimated complexity**: small. Extends existing division-detection code.

### 6.2 T-2B-04R.2 — Data-item declaration skeleton

**Scope**: Extend the parser to recognize `01 NAME.` and `01 NAME REDEFINES OTHER.` as `DataItemDeclaration` skeleton nodes. PIC/USAGE/VALUE clauses are recognized as *raw-text* spans (a string field on the node) but not yet parsed structurally.

**Acceptance**: A data-item declaration produces a `DataItemDeclaration` node with `level`, `name`, `span`, `redefines_target` (string or None). The PIC clause appears as a `pic_string` field on the node.

### 6.3 T-2B-04R.3 — PIC / USAGE / VALUE structural clauses

**Scope**: Replace the `pic_string` raw-text field with a structured `PicClause` node. Add `UsageClause` and `ValueClause` nodes. This is what T-2B-06's `DataItem` constructor needs.

### 6.4 T-2B-04R.4 — OCCURS / ODO / 88-level

**Scope**: Add `OccursClause`, `OdoClause`, and level-88 condition-name recognition. The `level` field on `DataItemDeclaration` already supports `88`.

### 6.5 T-2B-04R.5 — Paragraph definitions

**Scope**: Detect paragraph names that appear as labels (i.e. at the start of a logical line followed by `.`) and emit `Paragraph` nodes. The Procedure Division structure becomes `ProcedureDivision(paragraphs: tuple[Paragraph, ...])` and `Section(paragraphs: tuple[Paragraph, ...])`.

### 6.6 T-2B-04R.6 — Sections in Procedure Division

**Scope**: Detect `SECTION.` headers in the Procedure Division and emit `Section` nodes. Update `Paragraph.parent_section` to point to the enclosing `Section`.

### 6.7 T-2B-04R.7 — Qualified-name references

**Scope**: Add `QualifiedReference` node and extend expression parsing to handle `A OF B` syntax. This is the smallest change that unblocks T-2B-05's acceptance criterion.

### 6.8 T-2B-04R.8 — Subscripts and reference modification

**Scope**: Add `SubscriptedReference` and `RefModReference` nodes for `A(I)` and `A(I:L)`.

### 6.9 T-2B-04R.9 — RENAMES

**Scope**: 66-level `RENAMES` support.

### Dependency graph

```
T-2B-04R.1 ──────→ (additive only, no downstream)
T-2B-04R.2 ──────→ builds on R.1
T-2B-04R.3 ──────→ builds on R.2
T-2B-04R.4 ──────→ builds on R.3
T-2B-04R.5 ──────→ independent (procedure division)
T-2B-04R.6 ──────→ builds on R.5
T-2B-04R.7 ──────→ independent (expression parser)
T-2B-04R.8 ──────→ builds on R.7
T-2B-04R.9 ──────→ builds on R.2

T-2B-06 (DataItem tree)        depends on R.1-R.4
T-2B-05 (Identifier resolution) depends on R.1-R.7 + T-2B-06
```

---

## 7. Tests Required

For each T-2B-04R.* ticket:

1. **Empty Data Division** — no nodes, no diagnostics, no regression.
2. **Data Division with subsection** — `DivisionNode` emitted, no "unknown token" diagnostics.
3. **Single data-item declaration** — `DataItemDeclaration` emitted, no "unknown token" diagnostics.
4. **Multiple data-item declarations** — each gets its own node, source-order preserved.
5. **REDEFINES clause** — `redefines_target` is a non-None string; subsequent redefinition in the same record is allowed.
6. **88-level condition name** — `kind == LEVEL_88_ITEM`.
7. **OCCURS** — `occurs_clause` is a non-None `OccursClause`.
8. **ODO** — `odo_clause` is a non-None `OdoClause`.
9. **PIC clauses** — `X(n)`, `9(n)`, `S9(n)V9(s)`, `Z(n)`, etc., produce a `PicClause` with the correct `pic_string`.
10. **USAGE clause** — `USAGE IS BINARY`, `USAGE IS COMP-3`, etc.
11. **VALUE clause** — `VALUE 0`, `VALUE 'X'`.
12. **Paragraph definitions** — `MAIN-PARA.` followed by statements emits a `Paragraph`.
13. **Section definitions** — `MY-SECTION SECTION.` followed by paragraphs.
14. **Qualified references** — `A OF B` produces a `QualifiedReference` with `primary=A` and `qualifications=(B,)`.
15. **Nested qualifications** — `A OF B OF C` produces the correct nesting.
16. **Subscripts** — `A(I)` produces a `SubscriptedReference`.
17. **Reference modification** — `A(I:L)` produces a `RefModReference`.
18. **RENAMES** — 66-level renames.
19. **Existing tests still pass** — 364 V2 tests unchanged.
20. **T-2C-0A behavior unchanged** — scope graph builder still produces the same scopes.
21. **Determinism** — repeated parsing produces byte-identical AST.
22. **No Dict[str, Any] in public API** — frozen-dataclass invariant.
23. **No V1 imports** — frozen-contract invariant.
24. **No filesystem I/O** — frozen-contract invariant.
25. **No source re-scanning from semantic phases** — single-source-of-truth invariant.

---

## 8. Migration / Compatibility Strategy

### Backward compatibility

The proposed changes are **additive**:
- New AST node types are *added* to `nodes.py`; existing types are *unchanged*.
- New fields on existing nodes are *appended* with default values; existing field values are unchanged.
- `parser.py` is extended with new parse methods; existing parse methods are unchanged.
- New tests are added in a new file; existing tests are unchanged.

### T-2C-0A compatibility

T-2C-0A's `scope_graph.py` reads:
- `ast.span` (unchanged)
- `ast.divisions` (unchanged — still a tuple of strings)
- `ast.statements` (unchanged)

The new fields on `CompilationUnit` (`division_nodes`, `data_division`, `procedure_division`) are ignored by T-2C-0A. T-2C-0A tests continue to pass without modification.

### V1 compatibility

V1 is untouched. The V1 spot-check tests (7 tests) continue to pass.

### Test count

Before any T-2B-04R.* work: 364 V2 tests pass.
After each T-2B-04R.* increment: 364 + new tests, all pass.

---

## 9. Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Modifying `parser.py` breaks existing 364 tests | Medium | Add additive code paths only; run the full V2 suite after every change |
| New fields on `CompilationUnit` break T-2C-0A | Low | T-2C-0A reads only `divisions` and `statements`; new fields are ignored |
| New IRKind values conflict with existing usage | Low | The IRKind enum already has the necessary values; no new values needed |
| T-2B-04R.7 (qualified names) requires deep changes to the expression parser | Medium | Constrain to a small slice: only `A OF B` (no nested qualifications in the first increment) |
| T-2B-04R.5 (paragraph definitions) conflicts with T-2B-03's "unknown token" pattern | Medium | The new detection runs *before* the existing statement dispatch; a paragraph label does not match any statement keyword, so the new logic does not interfere |
| Reopening T-2B-03 breaks architectural boundary | Low | The T-2B-03 ticket is reopened *with* a new architectural commitment: the parser is a multi-increment project, with each increment adding specific structural coverage |
| New nodes introduce `Dict[str, Any]` | Low | All new nodes are frozen dataclasses with explicit fields; no attribute bags |
| Span drift in new clauses | Medium | Every new clause is constructed using the existing `_make_span` pattern with byte offsets |
| Identifier normalization (case folding) inconsistent with architecture §8.1 | Medium | T-2B-04R produces raw text; the resolver (T-2B-05) is responsible for case-folding per the architecture |

---

## 10. Recommended Smallest Implementation Slice

**T-2B-04R.1: Data Division subsection headers** is the recommended smallest slice.

**Why:**
- It is the *smallest* change that unblocks the next-ticket pipeline.
- It touches the *fewest* existing tests (only the parser tests).
- It is purely additive (new `DivisionNode` type; new optional field on `CompilationUnit`).
- It does not require any new expression-parser logic.
- It can be implemented and verified in a single small change.

After T-2B-04R.1 is implemented and verified:
- T-2B-04R.2 (data-item declarations) is the next smallest increment.
- After R.1 + R.2: T-2B-06 (DataItem tree) can be implemented (T-2B-06 was originally a separate ticket).
- After T-2B-06: T-2B-05 (Identifier resolution) can finally be implemented.
- T-2B-05 + remaining R.5/R.6/R.7 enables full identifier resolution with qualification.

**The full implementation is not done in this ticket; only the architectural recommendation and the smallest-slice plan.**

---

## 11. Whether Human Approval Is Required

**YES.**

Three architectural decisions require human approval:

1. **Reopening T-2B-03.** The T-2B-03 ticket was marked "SAFE TO FREEZE" in the implementation report. Reopening it is an architectural decision that changes the freeze contract. The user has explicitly proposed "T-2B-04R" as the new ticket name, which suggests the original T-2B-03 *stays* frozen and T-2B-04R is a separate ticket. But the implementation of T-2B-04R *must* modify `parser/parser.py` and `parser/nodes.py`, which are part of T-2B-03's freeze boundary. This is a contradiction that the user must resolve.

2. **T-2B-04R ticket ordering.** The proposed 9-increment breakdown (R.1 through R.9) is a plan, not an approved structure. The human must confirm the increment ordering and acceptance criteria.

3. **Naming and file-location convention for new nodes.** The new `DivisionNode`, `DataItemDeclaration`, `Section`, `Paragraph`, `QualifiedReference`, `SubscriptedReference`, `RefModReference`, `PicClause`, etc. need to be placed in either `modernize_v2/parser/nodes.py` (extending T-2B-03) or `modernize_v2/ir/` (in a new file). This affects the architecture's "parser AST vs. semantic IR" boundary. The architecture §6.2 lists the expected hierarchy in the *semantic* IR, not the parser AST, which suggests some of these nodes belong in the semantic IR rather than the parser AST. The human must confirm the split.

---

## 12. Final Architectural Recommendation

### What I recommend

**Approve the following, in this order:**

1. **Reopen T-2B-03** with a documented multi-increment extension plan.
2. **Approve Option A** (formally revise the parser, additively, preserving all existing contracts and tests).
3. **Approve the T-2B-04R.1..R.9 breakdown** as the extension plan.
4. **Start with T-2B-04R.1** (Data Division subsection headers) as the smallest implementation slice.
5. **After R.1 + R.2 + R.3 + R.4 are complete and verified**: proceed to T-2B-06 (DataItem tree).
6. **After T-2B-06 is complete and verified**: proceed to T-2B-05 (Identifier resolution).
7. **T-2B-05 + R.5 + R.6 + R.7**: full identifier resolution with paragraphs and qualification.

### What I do NOT recommend

- I do **not** recommend implementing T-2B-05 before the parser has the structural information.
- I do **not** recommend implementing a fake declaration model.
- I do **not** recommend re-scanning source bytes from the resolver.
- I do **not** recommend silently changing `parser.py` without formal reopening of T-2B-03.
- I do **not** recommend a hybrid parser (Option B).

### What I will NOT do now

- I will not write any code.
- I will not modify any frozen file.
- I will not implement any of the T-2B-04R.* tickets.
- I will not implement T-2B-05.
- I will not implement T-2B-06.

The architectural recommendation in this report is the deliverable. The actual implementation is the next ticket, **T-2B-04R.1**, pending human approval.

---

## 13. Git Status

```
$ git diff --name-only
(empty — no tracked files were modified)

$ git status --short | grep modern_v2
?? modernize_v2/
?? tests/v2/
```

No code was written. No tracked file was modified. The repository state is unchanged from the post-T-2C-0A / pre-T-2B-05-blocked freeze boundary.

**Test baseline**: 364 V2 tests pass, 7 V1 spot-check tests pass.

---

## 14. Stop Condition

I am stopping here, as instructed. The architectural decision report is the deliverable for this turn. No code has been written. The repository is in the same state as after the T-2C-0A freeze.

The next action requires **human approval** of the architectural decision (reopen T-2B-03, approve Option A, approve the T-2B-04R breakdown).
