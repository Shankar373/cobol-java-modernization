# PHASE 2 — ARCHITECTURE V2

**True COBOL / JCL / CICS / VSAM / SQL → Native Java / Spring Modernization Compiler**

Status: **PROPOSED — DESIGN ONLY — NO IMPLEMENTATION YET**
Audience: Engineering leads, security, QA, modernization architects
Companion docs: `PHASE_2_DECISION_REGISTER.md`, `PHASE_2_WORK_BREAKDOWN.md`

---

## 1. Executive Summary

Phase 1A–1H concluded that the current platform is a **HYBRID leaning
INTERPRETER_STYLE** with **NO runtime independence** and a comparator
whose PASS verdict is **NOT_TRUSTWORTHY**. The principal structural
defects are:

- Property-bag Semantic IR with no typed AST, no symbol table, no type
  system.
- Expression nodes are stored as opaque strings and *re-parsed* at code
  generation time.
- Code generation operates by string concatenation from property bags
  and a paragraph-dispatch interpreter.
- Heavy reliance on a custom COBOL semantic runtime
  (`CobolNumeric`, `CobolString`, `MockSqlService`,
  `CicsTransactionContext`, etc.).
- CICS, VSAM, and Spring Batch are simulated, not implemented.
- Verification contract is contract-gated and truncated; baseline
  freshness is not enforced; evidence is not content-hashed.

This document defines the **target architecture** for a real compiler
that produces genuinely native Java/Spring applications, with a
fail-closed differential verification engine and a content-hashed
provenance chain.

The architecture follows the platform's documented engineering
principles in `docs/AGENTS.md`:

- Repository agnosticism (no benchmark-specific hardcoding).
- Native Java / Track-B as the primary target; no `libcobj.jar`,
  no `jp.osscons`, no OpenSourceCOBOL4J runtime in generated Track-B
  apps.
- Business equivalence first; PASS must be evidence-backed and
  fail-closed.
- Distinct, honest classification:
  `VERIFIED / EMULATED / PARTIAL / UNSUPPORTED / NOT_VERIFIED /
  ENVIRONMENT_BLOCKED`.
- Validation must be fail-closed:
  `PASS / FAILED / UNVERIFIED / PARTIAL / ENVIRONMENT_BLOCKED / SKIPPED`.

---

## 2. Phase 1 Findings Carried Forward

| ID    | Finding (summary)                                                  | Severity | Target subsumed by |
|-------|--------------------------------------------------------------------|----------|---------------------|
| 1C-01 | Property-bag SemanticIR; no typed AST                              | P0       | §6 Canonical IR    |
| 1C-02 | Expressions stored as raw strings                                  | P0       | §7 Expression AST  |
| 1C-03 | CFG/DataFlowModel not consumed by generator                        | P0       | §10 CFG, §11 DFA   |
| 1C-04 | Parser recovery swallows sibling statements                        | P0       | §9 Recovery policy |
| 1C-05 | SQL DDL failure swallowed                                          | P0       | §13 SQL            |
| 1C-06 | NULL literal misparsed as host variable                            | P0       | §7, §9             |
| 1D-01 | Interpreter-style paragraph dispatch                               | P0       | §18 Codegen        |
| 1D-02 | COBOL semantic runtime required to execute generated code          | P0       | §19 Runtime lib    |
| 1D-03 | CICS simulated (HashMap context)                                   | P0       | §15 CICS           |
| 1D-04 | VSAM KSDS mapped to JDBC table; ESDS/RRDS/alt-index missing        | P0       | §14 File/VSAM      |
| 1D-05 | Spring Batch = single Tasklet wrapper                              | P0       | §17 JCL/Batch      |
| 1D-06 | Unsupported statements emitted as comments                         | P0       | §20 Gate           |
| 1E-01 | Stale baseline reuse via `os.path.exists(stdout.txt)`              | P0       | §23 Baseline trust |
| 1E-02 | Baseline compile/exec failure swallowed                            | P0       | §23                |
| 1E-03 | stdout truncated to last 500 chars                                 | P0       | §24 Verifier       |
| 1E-04 | H2 in-memory fallback when PGHOST unset                            | P0       | §13 SQL            |
| 1E-05 | Java auto-seeds `data/*.sql`/`*.csv`                              | P0       | §13, §25           |
| 1E-06 | Logical-match override for indexed files                           | P0       | §24                |
| 1E-07 | SQLCODE/SQLSTATE not first-class                                   | P0       | §13                |
| 1E-08 | CICS/VSAM state not in observation                                 | P0       | §15, §14           |
| 1F-01 | EBCDIC unsupported (ISO-8859-1 everywhere)                         | P0       | §16 Encoding       |
| 1F-02 | DB2 DDL unsupported                                                | P0       | §13                |
| 1F-03 | BY VALUE unsupported                                               | P0       | §12 Linkage        |
| 1F-04 | JCL multi-step / restart / GDG unsupported                         | P0       | §17                |
| 1F-05 | SORT/MERGE/REPORT WRITER/Declaratives unsupported                  | P0       | §10, §18           |
| 1G-01 | No content hashing of any artifact                                 | P0       | §22 Provenance     |
| 1G-02 | CI bypass via `PARITY_ALLOW_SKIP`/Docker-not-required              | P0       | §26 CI             |
| 1G-03 | String injection from COBOL DISPLAY into generated Java            | P0       | §18, §25           |
| 1G-04 | Arbitrary SQL via `data/*.sql` auto-seed                           | P0       | §13, §25           |
| 1G-05 | `shell=True` with interpolation                                    | P0       | §25 Security       |
| 1G-06 | `Class.forName` reflection in CICS registry                        | P1       | §15                |
| 1G-07 | Concurrent runs share `MockSqlService` static state                | P1       | §21 Concurrency    |

**No Phase 1 finding is suppressed.** Each is either *closed by design*
by the relevant target section below or is recorded as an explicit,
unresolved limitation in §31.

---

## 3. Current Architecture (CURRENT)

```
COBOL
  → modernize/lexer.py (string tokens)
  → modernize/parser.py (regex + state machine; recovery swallows siblings)
  → modernize/semantic_ir.py (Dict[str, Any] property bags)
  → modernize/control_flow.py (CFG built but not consumed)
  → modernize/dependency_analysis.py (call graph built but not authoritative)
  → modernize/native_generator.py (string-template Java emitter)
  → modernize/enterprise_generator.py (Spring Boot/Batch scaffold)
  → runtime helpers under modernize/java_helpers/  (CobolNumeric, MockSqlService,
                                                      CicsTransactionContext, …)
  → modernize/native_pipeline.py (Docker-GnuCOBOL baseline; Maven build;
                                   Java run; observation capture)
  → execution/equivalence.py (truncated stdout, contract-gated)
  → report / UI
```

Properties:

- IR has no types, no scopes, no source provenance on nodes.
- Code generator is template-driven: `f"... {expr} ..."`.
- Generated Java requires `com.systema.modernized.runtime.*` to execute.
- Comparator compares only last 500 chars of stdout, optional files,
  optional DB. SQLCODE/SQLSTATE/CICS/VSAM not in observation.

## 4. Target Architecture (TARGET)

```
                                ┌──────────────────────────────┐
COBOL/JCL/COPYBOOK/SQL/CICS/BMS │   Preprocessor (COPY/REPLACE) │
                                └──────────────┬───────────────┘
                                               │  source map
                                ┌──────────────▼───────────────┐
                                │   Lexer (typed tokens)       │
                                └──────────────┬───────────────┘
                                               │
                                ┌──────────────▼───────────────┐
                                │   Parser (deterministic AST) │
                                └──────────────┬───────────────┘
                                               │  Concrete AST
                                ┌──────────────▼───────────────┐
                                │   Semantic analysis          │
                                │   (resolution, type check,   │
                                │    qualification, scope,     │
                                │    linkage)                  │
                                └──────────────┬───────────────┘
                                               │  Typed AST
                                ┌──────────────▼───────────────┐
                                │   Canonical Semantic IR      │
                                │   (immutable, addressed)     │
                                └──────────────┬───────────────┘
                                               │
                ┌──────────────────────────────┬─┴────────────────────────┐
                │                              │                          │
       ┌────────▼────────┐            ┌─────────▼────────┐        ┌────────▼────────┐
       │ CFG + Data-flow │            │   Call graph     │        │ Domain models   │
       │ (per program)   │            │  (linkage types) │        │ (records, FD)   │
       └────────┬────────┘            └─────────┬────────┘        └────────┬────────┘
                │                              │                          │
                └────────────────────┬─────────┴──────────────────────────┘
                                     │
                        ┌────────────▼─────────────┐
                        │ Workload classification  │
                        │ & capability gate        │
                        └────────────┬─────────────┘
                                     │  Plan
                        ┌────────────▼─────────────┐
                        │ Deterministic transformer│
                        │ (typed Java AST emitter) │
                        └────────────┬─────────────┘
                                     │  Java source (deterministic, AST-built)
                        ┌────────────▼─────────────┐
                        │ Spring generators        │
                        │ Boot  +  Batch           │
                        └────────────┬─────────────┘
                                     │  pom.xml, sources
                        ┌────────────▼─────────────┐
                        │ Build (Maven, pinned)    │
                        └────────────┬─────────────┘
                                     │  artifact
                        ┌────────────▼─────────────┐
                        │ Independent execution    │
                        │ (Java + real DB if needed)│
                        └────────────┬─────────────┘
                                     │  observation
                        ┌────────────▼─────────────┐
                        │ Differential verifier V2 │
                        │ (full observations)      │
                        └────────────┬─────────────┘
                                     │  verdict
                        ┌────────────▼─────────────┐
                        │ Provenance / Evidence     │
                        │ (content-hashed, signed) │
                        └────────────┬─────────────┘
                                     │
                        ┌────────────▼─────────────┐
                        │ Report / Package / UI    │
                        └──────────────────────────┘
```

---

## 5. Architectural Principles

1. **Canonical typed IR is the single source of truth.** No information
   is recovered from string templates at codegen time.
2. **Expressions are first-class AST nodes**, never strings at IR or
   codegen level.
3. **No COBOL interpreter in Java.** Generated Track-B code has no
   paragraph-dispatch loop, no global statement bag, no reflection
   dispatch on program name. The only reusable helpers permitted are
   libraries that solve Java-side problems (e.g., `CobolDecimal` for
   fixed-point arithmetic that does not have a clean Java primitive),
   and even these must be pure Java with no awareness of COBOL
   program structure.
4. **Fail-closed verification.** A migration that cannot be verified
   end-to-end is `UNVERIFIED` or `ENVIRONMENT_BLOCKED`, never `PASS`.
5. **Honest capability classification.** `SUPPORTED_AND_VERIFIED /
   SUPPORTED_UNVERIFIED / PARTIAL / SIMULATED / UNSUPPORTED` per
   feature, per workload.
6. **Deterministic transformation.** Same inputs ⇒ byte-identical
   generated source and byte-identical evidence.
7. **Provenance by content hash.** Every artifact is hashed at
   production and at consumption; mismatched hashes fail-closed.
8. **Repository agnosticism.** No benchmark-specific entities,
   tables, programs, copybooks, or sample data are hardcoded in
   production modernization logic.
9. **No legacy runtime in Track-B.** Generated Track-B applications
   must not depend on `libcobj.jar`, `jp.osscons.*`, or
   OpenSourceCOBOL4J. Custom runtime libraries are allowed only as
   Java-only domain helpers and must declare their scope.
10. **Security by construction.** No `shell=True`; no string-concat
    Java emission; allow-listed `data/*.sql`; structured SQL building;
    bounded subprocess timeouts; read-only Docker mounts for sources;
    workspace isolation by run ID.

---

## 6. Canonical Typed Semantic IR

### 6.1 Node identity

Every node has:

- `id`: stable ULID-style 26-char id (Crockford base32). Generated
  deterministically from source fingerprint + path + kind + index.
- `kind`: an enum value from `IRKind`.
- `source`: `SourceSpan { file_id, byte_start, byte_end, line, col }`.
- `parent_id`: optional.
- `children`: ordered list of child ids (or `[]`).
- `attrs`: typed attribute bag keyed by `AttrKey` (no `Dict[str, Any]`
  in the public surface).
- `diag`: list of attached diagnostics (never mutating the node).
- `provenance_hash`: `sha256(id || attrs_canonical)`.

### 6.2 Hierarchy (sketch)

```
CompilationUnit
  ├── CopybookMap                # expanded COPY map with source ids
  ├── RepositoryMap              # JCL / SQL / BMS / PROC files
  ├── Program[]
  │     ├── IdentificationDivision
  │     ├── EnvironmentDivision
  │     │     ├── FileSection (FD[])
  │     │     │     └── FileDescription { name, access, record_layout, organization }
  │     │     └── SelectClause[]
  │     ├── DataDivision
  │     │     ├── WorkingStorageSection
  │     │     ├── LocalStorageSection
  │     │     ├── LinkageSection
  │     │     └── ReportSection
  │     ├── DataItem[]            # tree of records / elementary / ODO / REDEFINES
  │     ├── ProcedureDivision
  │     │     ├── Paragraph[]     # or Section[]/Paragraph[]
  │     │     │     └── Statement[]
  │     │     └── Declaratives    # (gated: PARTIAL)
  │     ├── CallGraph (intra-program)
  │     ├── CFG
  │     └── DomainModel (records as Java value classes)
  └── SqlModule[]                # EXEC SQL blocks + DCLGEN
  └── CicsModule[]               # EXEC CICS, BMS maps
  └── JclJob[]                   # JOB / EXEC / DD / PROC
```

### 6.3 `DataItem` representation

```
DataItem
  id, name, level, parent, pic, usage, sign, value,
  occurs: OccursClause | None,
  odo: bool,
  redefines_target: id | None,
  renames_target: id | None,
  linkage: 'working' | 'local' | 'linkage' | 'file' | 'report' | 'screen',
  java_target: JavaTypeRef,
  layout: Layout { offset, length, byte_order, encoding },
  condition_items: Level88[],
```

`Layout` is computed once from PIC/USAGE/REDEFINES rules and frozen.
It is the only place where COBOL byte layout is preserved, and it is
expressed as offsets/lengths on the *value class*, not as a runtime
emulator.

### 6.4 Why these exist

- Stable IDs make diff-based tests and reproducibility possible.
- Source spans enable all diagnostics to point at exact source
  positions.
- `attrs` keyed by enum prevents drift between IR and codegen.
- `provenance_hash` is the unit of evidence (§22).

---

## 7. Expression AST

### 7.1 Why a real AST

In the current implementation expressions are strings. This makes
type-checking, constant-folding, REDEFINES overlap analysis, NULL
indicator tracking, and accurate Java emission impossible.

### 7.2 Node kinds (non-exhaustive)

- `Lit { kind: IntLit | StrLit | BoolLit | Figurative, value, pic_compat }`
- `Ref { target: id, qualification: [...], subscripts: [Expr],
        refmod: (offset, length) | None }`
- `BinOp { op, left, right, pic_promoted }`
- `Unary { op, operand }`
- `Cond { op: '='|'<'|'>'|'<='|'>='|'<>', left, right }`
- `Logical { op: AND|OR, operands }`
- `Func { name, args, intrinsic_def }`
- `InlineCall { target, args, linkage, returning }`
- `SqlExpr { kind, sql_ast_ref }`
- `CicsExpr { kind, cics_ast_ref }`
- `Cast { to: JavaTypeRef, from: JavaTypeRef, rounding, truncating }`

`pic_promoted` records the COBOL numeric promotion applied (e.g.,
`PIC S9(5)V9(2) + PIC 9(3)` ⇒ `PIC S9(8)V9(2)`). This is the unit of
correctness for arithmetic and is the reason we cannot use
Java-side `BigDecimal` only — many combinations collapse to `long`
arithmetic in COBOL and that distinction must be preserved.

### 7.4 Pipeline

```
COBOL source
   → Lexer tokens
   → Parser AST (with source spans)
   → Semantic analysis (resolution, type inference, qualification)
   → Typed AST (every Expr has `expr_type: CobolType`)
   → Normalized Expr (constant folded, BOOLEAN normalized,
                     parentheses minimized)
   → Java Expr emitter (typed; see §18)
```

### 7.5 Why not raw strings

- Cannot differentiate `NULL` literal from host variable `NULL`
  (Phase 1C-06).
- Cannot enforce SQLCODE/SQLSTATE flow analysis (1E-07).
- Cannot perform REDEFINES overlap analysis (1F).
- Cannot prove ODO bounds (1F).
- Cannot enforce reference modification range checks.
- Cannot distinguish display vs. numeric truncation rules.

---

## 8. Symbol Table + Type System

### 8.1 Symbol table

```
Scope (id, kind: Program|Paragraph|Block|File)
  parent: id | None
  symbols: Dict[SymbolKey, Symbol]

Symbol
  key: (name, qualification)              # canonical, case-folded
  decl: DataItem | Paragraph | File | Program | Const
  visibility: local | global | external
  linkage: by_ref | by_content | by_value | returning
  redefines: [id]
  rename_target: id | None
  used_by: [Statement id]
  defined_at: [Statement id]
  odo_range: (Expr, Expr) | None
```

Scopes are explicit so that nested programs and copy-expanded scopes
do not collide.

### 8.2 COBOL type system

- `CobolInt { signed, digits }`
- `CobolDec { signed, digits, scale }`
- `CobolFloat { kind: binary | long_float }`  # GnuCOBOL COMP-1/2
- `CobolPacked { digits, scale }`             # COMP-3
- `CobolBin { signed, bytes }`                # COMP (1,2,4,8)
- `CobolAlpha { length, charset }`            # PIC X / PIC A
- `CobolEdited { length, mask }`              # PIC Z, -, +, DB, CR, etc.
- `CobolBool` (level 88)
- `CobolPtr`                                  # POINTER / USAGE POINTER
- `CobolGroup { items: [id], layout: Layout }`
- `CobolArray { element: id, lower, upper, odo }`

### 8.3 Java target types (mapping rules)

| COBOL                | Java target                                    | Notes                         |
|----------------------|------------------------------------------------|-------------------------------|
| `PIC 9(n)` `n<=9`    | `long`                                         | fast path for counter-like    |
| `PIC 9(n)` `n<=18`   | `long` if unsigned, `BigInteger` if signed 18  | explicit bound                |
| `PIC S9(n)V9(s)`     | `BigDecimal` for s>0, else `long`              | exact decimal                 |
| `COMP-3`             | `BigDecimal` / `long` (lossless if 18 digits)  | explicit warning at IR level  |
| `COMP` 1/2/4/8       | `byte`/`short`/`int`/`long` (explicit endian)  | exact                         |
| `PIC X/A`            | `String` (fixed-length)                        | trimming explicit             |
| `PIC Z, -, +, $`     | `String` (edited) + formatting helper          | formatting is presentation    |
| level 88             | `boolean` field on record + constants          | enum where helpful            |
| ODO                  | `T[]` with size on the record                  | not global mutable            |
| POINTER              | `java.lang.ref.Reference` (typed handle)       | scope-limited                 |
| group                | value class (record)                           | layout frozen                 |

**Mapping is a typed function, not a heuristic.** Each mapping has
a unit test that asserts round-trip equivalence for a representative
set of PICs.

---

## 9. Storage Model

The storage model is **a layout, not an emulator.**

For a record in WORKING-STORAGE:

1. `LayoutComputer` walks the DataItem tree, applying COBOL
   alignment rules:
   - Elementary items are placed at the next byte aligned to their
     natural boundary for COMP/COMP-3/PTR.
   - Group items are laid out as the concatenation of their children.
   - REDEFINES repositions the cursor to the *start* of the redefined
     item; the second item is restricted to fit within the original
     length (validated, not assumed).
   - ODO items use the *current* bound to size; the bound is recorded
     so the layout is reproducible.
2. The layout is **frozen** at IR time and becomes part of the
   provenance hash.
3. Generated Java value classes are Java `record`s (or final classes
   with explicit fields) whose field order and `Layout` map match the
   COBOL record exactly.
4. Where layout matters for *binary I/O* (record files, VSAM), a
   single helper class `RecordCodec` knows how to encode/decode a
   record to/from bytes for the chosen encoding (§16). It does not
   know about paragraphs, programs, or CALL.

This approach keeps `CobolDecimal` / `RecordCodec` as **domain
helpers** (allowed by §5) rather than as a **runtime emulator**.

### 9.1 Linkage

- `BY REFERENCE` ⇒ parameter type is the value class (record) or
  the same element type for elementary items. Mutation in callee is
  visible in caller (Java reference semantics on the record).
- `BY CONTENT` ⇒ callee receives an immutable copy (record copy).
- `BY VALUE` ⇒ elementary value type; `BigDecimal`/`long`/`byte[]`
  per the Java target mapping.
- `RETURNING` ⇒ typed return value.

---

## 10. Control-Flow Model

### 10.1 Basic blocks

A `BasicBlock` has:

- `id`, `statements: [Statement id]`, `terminator: Terminator`.
- `preds: [Block id]`, `succs: [Block id]`.
- `dom: Block id | None`, `post_dom: Block id | None`.

`Terminator` kinds:
`FallThrough | If(cond) | Evaluate(arms) | PerformUntil(cond, body)
| PerformVarying(var, init, until, step) | PerformTimes(n, body)
| PerformProc(target) | Goto(target) | ExitPerform | ExitParagraph
| Goback | StopRun | NextSentence | Return(value) | Throw`

### 10.2 Construct lowering

| COBOL                            | IR / CFG                                              |
|----------------------------------|-------------------------------------------------------|
| `IF … ELSE … END-IF`             | If-terminator on condition expr; `merge` block       |
| `EVALUATE … WHEN … END-EVALUATE` | Evaluate with multiple arms; `merge` block            |
| `PERFORM para`                   | Call to `Block(id_of_para_entry)`                     |
| `PERFORM UNTIL cond`             | Loop with `Until(cond)`; back-edge                    |
| `PERFORM VARYING … UNTIL`        | Loop with init + step + until                         |
| `PERFORM n TIMES`                | Loop with counter                                     |
| `EXIT PERFORM` / `EXIT PARAGRAPH`| Terminator `ExitPerform` (closest loop) / `ExitParagraph` |
| `GO TO` (no dep.)                | Goto terminator                                       |
| `GO TO … DEPENDING ON`           | Switch terminator                                     |
| `NEXT SENTENCE`                  | terminator to next statement block                    |
| `GOBACK` / `STOP RUN`            | Goback / StopRun terminator                           |
| `SORT` / `MERGE`                 | Gated: PARTIAL; lowers to library call with semantic shim |
| `REPORT WRITER`                  | UNSUPPORTED in Track-B (gated FAIL)                   |
| `Declaratives`                   | PARTIAL via file-event hooks                          |

### 10.3 Generator consumption

The generator **must** walk the CFG. It is no longer permitted to
emit `f"PERFORM {target}"` from string concatenation. Codegen
emits Java source by:

1. Walking the entry block.
2. For each terminator, emitting structured Java:
   - `if` → Java `if` statement built from the typed condition.
   - `Evaluate` → Java `switch` (when keys are integral) or chained
     `if` (when not).
   - `PerformProc` → Java method call on the per-paragraph helper.
3. Paragraphs are emitted as **private methods** on the program
   class, not as entries in a global dispatch table. Method names
   derive from the paragraph identifier (slugified, stable).

This eliminates the paragraph-dispatch interpreter pattern.

---

## 11. Data-Flow Analysis

### 11.1 Analyses (mandatory at IR time)

- **Def-use chains** for every elementary `DataItem` and for
  every record field reachable through a `Ref`.
- **Reaching definitions** for REDEFINES validation.
- **Liveness** for register-like Java locals.
- **Mutation points** (statements that write a variable).
- **IODependencies** mapping I/O statements to file/screen
  resources.
- **Nullability** for SQL host variables.
- **Side-effect summary** per paragraph (for `EXIT PARAGRAPH`
  semantics, for `GOBACK` consistency).

### 11.2 Use in codegen

- Dead-statement elimination (with provenance retained).
- Constant folding at IR level (legal only for literals, never for
  values from I/O).
- SQL host variable nullability analysis feeding the
  `NullIndicator` wiring in generated SQL adapters.

### 11.3 Why this matters

Without DFA, Phase 1C-04 (parser recovery swallowing siblings) is
undetectable at codegen. With DFA, a missing statement produces
unreachable defs that **the verifier can flag as a diagnostic**
during IR validation, not at the comparator.

---

## 12. Call Graph + Linkage

### 12.1 Nodes

`CallNode { caller, callee, args, linkage, returning, dynamic,
            raised: [kind] }`.

Edges: `static_call`, `dynamic_call`, `sql_call`, `cics_link`,
`cics_xctl`.

### 12.2 Static CALL

- `CALL "literal"` ⇒ static; target resolvable at link time.
- Generated as a typed Java method call on the program's class or
  a service bean.
- `BY REFERENCE`/`BY CONTENT`/`BY VALUE` mapped per §9.1.
- `RETURNING` mapped to typed return.

### 12.3 Dynamic CALL

- `CALL variable` ⇒ dynamic; target resolved at runtime.
- Generated as a `ProgramRegistry` lookup, but the registry is a
  *Java* map of program-name → `Supplier<Program>`, populated by
  Spring DI; it is not a string-based `Class.forName` (this closes
  1G-06).
- Recursive CALL is supported via constructor-injected self
  reference; cycle detection is performed at IR level to surface
  infinite recursion explicitly.
- Programs without a known target are reported as diagnostics and
  *gated* (§20); they do not silently become comments.

### 12.4 CALL … ON EXCEPTION / ON OVERFLOW

- Translated to `try/catch` with explicit exception classes.

### 12.5 CALL … USING BY VALUE

- Per §9.1.

---

## 13. SQL / DB2 Architecture

### 13.1 Pipeline

```
COBOL EXEC SQL block
  → SqlLexer / SqlParser (typed SQL AST)
  → SqlAnalyzer (host var binding, type check, indicator binding)
  → SqlDialect plan (DB2 / PostgreSQL / H2)
  → SqlRuntime (parameterized execution, NULL indicator wiring)
```

### 13.2 SQL AST node kinds

- `Select { distinct, columns, from, where, group, having, order,
            fetch_first, into_host_vars, with_indicator }`
- `Insert { table, columns, values | select }`
- `Update { table, set, where }`
- `Delete { table, where }`
- `CursorDecl { name, scroll, sensitivity, sql }`
- `Open { name, using }`
- `Fetch { name, into, indicator }`
- `Close { name }`
- `Commit`, `Rollback`
- `Connect`, `SetConnection`

### 13.3 NULL indicators

- Every `host_var` carries a flag `nullable: bool` and an
  `indicator_var: Expr | None` from the parser.
- Generated SQL is **parameterized**. NULL is set by
  `setNull(...)` or `setObject(idx, value, Types.NUMERIC)`; never
  by string concatenation.
- `SQLCODE` / `SQLSTATE` are first-class return values of
  every SQL call site. The IR records the call site; the verifier
  compares the SQLCODE and SQLSTATE in the observation
  (§24.6). This closes 1E-07.

### 13.4 Dialect translation

- A dialect module translates the SQL AST to the target database
  dialect.
- The `default` dialect for verification is **PostgreSQL**, both for
  COBOL baseline and for Java, with the same host/port.
- `H2` is **not** an allowed target. It is permitted only behind a
  feature flag `allowH2ForUnitTests` and produces a `SIMULATED`
  classification. PASS is impossible with H2.

### 13.5 DB2 DDL

- `CREATE TABLE` / `CREATE INDEX` are parsed and emitted as
  DDL DTOs, not as opaque strings.
- Schema comparison is part of the observation: row counts, primary
  key uniqueness, index presence. Schema mismatch is a
  `FAILED` verdict, not a comparator warning.

### 13.6 Transactions

- `EXEC CICS` and `EXEC SQL` flows are bound to a single Spring
  `PlatformTransactionManager` per workload.
- `COMMIT` / `ROLLBACK` lower to explicit boundaries.
- Transaction state (committed vs. rolled-back) is part of the
  observation: verifier checks both expected state and observed
  state.

### 13.7 Honesty about DB2

PostgreSQL is **not** DB2. Until the platform is verified against a
real DB2 instance (Db2 for z/OS, Db2 LUW), DB2-related migrations
are classified as `SUPPORTED_UNVERIFIED`. This is documented in
`docs/SUPPORTED_FEATURES.md` and propagated to the report.

---

## 14. File / VSAM Architecture

### 14.1 Separation of concerns

- `FileSemantics` (COBOL concepts): organization, access mode,
  record format, alternate keys, status.
- `FileAdapter` (Java side): an interface chosen per organization.
- `FileRuntime` (concrete): implements the adapter using a chosen
  physical backend.

### 14.2 Adapters

| Organization     | Adapter                  | Backend                                 | Classification       |
|------------------|--------------------------|-----------------------------------------|----------------------|
| SEQUENTIAL       | `SequentialFile`         | plain `BufferedReader/Writer`           | SUPPORTED_AND_VERIFIED |
| LINE SEQUENTIAL  | `LineSeqFile`            | text records                            | SUPPORTED_AND_VERIFIED |
| INDEXED (KSDS)   | `IndexedFile`            | JPA entity + Spring repository          | SUPPORTED_UNVERIFIED |
| RELATIVE (RRDS)  | `RelativeFile`           | JPA entity with `int` key               | PARTIAL              |
| VSAM ESDS        | `EsdsFile`               | JPA entity with surrogate key + RBA     | PARTIAL              |
| VSAM KSDS        | `KsdsFile`               | JPA entity with primary key + alt-index | PARTIAL              |
| VSAM alt-index   | `AltIndex`               | secondary JPA indexes                   | UNSUPPORTED in V2.0  |

The phrase "VSAM" is reserved for adapters that have been verified
against an actual VSAM dataset. Otherwise the class is named
`IndexedFile`, not `VsamFile`. This closes the naming-overclaim
identified in 1D-04 / 1F.

### 14.3 Record-level semantics

- `OPEN`, `CLOSE`, `READ`, `READ NEXT`, `READ KEY`, `START`,
  `WRITE`, `REWRITE`, `DELETE` lower to typed Java method calls
  on the adapter.
- `FILE STATUS` is a first-class return value of every operation.
  The verifier compares file status between COBOL and Java.
- Record comparison for the verifier is **record-ordering-aware**
  (1E-06 / 1G logical-match): the physical byte representation and
  the record sequence are both compared unless the contract
  specifies a stable sort key, in which case both sides are sorted
  by that key before comparison.

### 14.4 No JDBC-as-VSAM

The current system uses a JDBC table as VSAM. V2 prohibits that
naming. If a JDBC table is used, the generated code's class name and
the documentation both say `IndexedFile`. The honesty is enforced
naming-wise, not just by comment.

---

## 15. CICS Architecture

### 15.1 Status classification (V2)

| Feature             | V2 status                  |
|---------------------|----------------------------|
| `LINK`              | SUPPORTED_AND_VERIFIED     |
| `XCTL`              | SUPPORTED_AND_VERIFIED     |
| `RETURN` (COMMAREA) | SUPPORTED_AND_VERIFIED     |
| `COMMAREA`          | SUPPORTED_AND_VERIFIED     |
| `EIB`               | SUPPORTED_UNVERIFIED       |
| `SYNCPOINT`         | SUPPORTED_UNVERIFIED       |
| `ROLLBACK`          | SUPPORTED_UNVERIFIED       |
| Channels/containers | PARTIAL                    |
| BMS SEND MAP        | PARTIAL                    |
| BMS RECEIVE MAP     | PARTIAL                    |
| TSQ / TDQ           | PARTIAL (in-memory)        |
| ENQUEUE / DEQUEUE   | PARTIAL (in-memory)        |
| Web / 3270 bridge   | UNSUPPORTED in V2.0        |

`PARTIAL` and `UNSUPPORTED` features raise a `CicsCapability`
diagnostic at IR time and surface in the report; they do not
silently degrade.

### 15.2 Implementation principle

- A `CicsRuntime` interface provides the operations.
- The default implementation is an in-process implementation for
  tests, behind a clear class name `InMemoryCicsRuntime`.
- A future adapter may target a real CICS region; today the
  in-memory implementation is honest about what it is.
- The word "CICS" in generated class names and Javadoc is reserved
  for the real semantic abstraction, not the in-memory store.

### 15.3 No `Class.forName`

The current `CicsProgramRegistry` uses `Class.forName`. V2 replaces
this with a typed `Map<String, Supplier<Program>>` populated by
Spring DI. This closes 1G-06.

---

## 16. Encoding Model

V2 introduces `Encoding` as a first-class execution property:

```
Encoding {
  source_codepage:  EBCDIC | ASCII | UTF-8 | cp037 | cp1140 | ...
  bytes_per_char:   1,
  record_encoding:  FixedBinary | LineTerminated | VLR | VLF,
  numeric_encoding: NativeEndian | BigEndian | LittleEndian,
  signed_encoding:  AsciiSign | EbcdicSign,
  java_charset:     Charset,
}
```

- Every file adapter declares its `Encoding`. Mismatched encodings
  between baseline and Java are an environment error, not a content
  mismatch.
- `EBCDIC ↔ ASCII` translation is a typed `Transcoder` class,
  injected by the adapter, **not** a runtime feature of generated
  business code.
- Numeric PICTURE → byte layout is driven by the same
  `LayoutComputer` (§9) and respects the encoding's
  `numeric_encoding`.

This closes 1F-01 (EBCDIC unsupported → at least explicitly modeled
and gated).

---

## 17. JCL / Spring Batch Architecture

### 17.1 JCL semantic IR

```
JclJob
  id, name, owner, class
  parameters: { symbolic -> expr }
  steps: [JclStep]
    ├── pgm | proc
    ├── args
    ├── cond: CondClause
    ├── dd: [DdStatement]
    │     ├── dsn: expr
    │     ├── disp: (status, normal, abnormal)
    │     ├── like: id
    │     ├── sysin: bool
    │     ├── recfm, lrecl, blksize
    │     └── gdg: GdgRef | None
    └── restart: RestartSpec
```

### 17.2 Mapping to Spring Batch

Each `JclStep` becomes a `Step` bean:

- PGM becomes a `Tasklet` or, where the PGM is a `READ-PROCESS-WRITE`
  pattern, a chunked `ItemReader` / `ItemProcessor` / `ItemWriter`.
- `JOB` becomes a `Job` bean with ordered `Step`s.
- `COND` becomes a `JobExecutionDecider`.
- `restart` becomes a `Restartable` Spring Batch job with
  `ExecutionContext` carry-over.
- `GDG` becomes a versioned `JobParameter`.
- `DISP=MOD,DELETE` translates to a JPA repository operation.
- Return code propagation is preserved via `StepExecution` exit
  status.

### 17.3 No main-in-Tasklet

V2 does not permit a single `Tasklet` whose body is "call
`Main.main()`". A `Tasklet` must model a meaningful unit of work
or be removed.

---

## 18. Native Java Generation

### 18.1 Principles

- Java is emitted from a **typed Java AST**, not by string
  concatenation.
- Every Java source line is constructable from a `JExpr` /
  `JStmt` / `JDecl` node.
- Generated class names, field names, method names, and package
  names are derived from the input COBOL program names using a
  deterministic slug. No class name collisions are allowed
  (detected at IR time).
- Imports are explicit and minimal. There is no
  `com.systema.modernized.*` blanket import.

### 18.2 Generated structure

```
com.example.modernized.<package>/
  Application.java                    # @SpringBootApplication
  domain/
    CustomerRecord.java               # value class (record) for 01-level
    OrderItem.java
  service/
    CustomerService.java
    BillingService.java
  persistence/
    CustomerRepository.java           # Spring Data
    OrderItemRepository.java
  batch/
    BillingJobConfig.java
    BillingStepTasklet.java           # only if the workload is a true tasklet
    BillingReader.java
    BillingProcessor.java
    BillingWriter.java
  runtime/
    DecimalArithmetic.java            # ONLY if a real Java-side need
                                       (e.g., packed-decimal exact arithmetic)
    RecordCodec.java                  # ONLY if binary record I/O is needed
```

### 18.3 What is *not* allowed

- `MainClass.executeParagraph(paragraphName, ...)`-style dispatcher.
- `static Map<String, Program> REGISTRY = new HashMap<>()`
  populated at init time.
- `Class.forName("com.systema..." + name)`.
- `g.drawCircle(…)` style emulation of COBOL statements.
- A single generated class with thousands of methods.
- Blanket `import com.systema.modernized.runtime.*;`.

### 18.4 Custom runtime libraries (allowed but constrained)

A custom Java helper may exist iff:

1. It solves a problem that the Java standard library does not solve
   (e.g., exact packed-decimal arithmetic).
2. It is unaware of paragraphs, programs, or CALL.
3. It is published under the platform's normal Java packaging, not
   packaged as a hidden emulator jar.
4. Its use is enumerated in the report (so reviewers can audit it).

The current `CobolNumeric`, `CobolString`, `MockSqlService`,
`CicsTransactionContext`, `JclExecutionContext`,
`SpringContextHelper` are **candidates for replacement** by V2.
Specifically, the platform **must not** ship
`jp.osscons.*` or `libcobj.jar` in the Track-B target (per
`AGENTS.md`).

---

## 19. Custom Runtime Library Policy

V2 distinguishes three categories of helpers, and each is treated
differently in the report:

| Category                    | Examples                       | Ship in Track-B? | Verifier impact          |
|-----------------------------|--------------------------------|------------------|--------------------------|
| Domain helper               | `DecimalArithmetic`, `RecordCodec` | YES, declared | Helper behavior verified |
| Adaptation helper           | `SpringConfig` glue, `Mappers`  | YES, declared   | Helper behavior verified |
| COBOL-emulator helper       | `CobolNumeric`, `CobolString`, `MockSqlService`, `CicsTransactionContext`, `JclExecutionContext`, `SpringContextHelper` | **NO** | N/A; replaced by V2 |

The "NO" line is the architectural commitment. Track-B is genuine
native Java; legacy emulator helpers either become domain helpers
in V2 form (if there is a real Java-side need) or are deleted.

---

## 20. Unsupported-Feature Gate

### 20.1 Classification

Every feature in the IR has a `Capability` flag:

```
SUPPORTED_AND_VERIFIED
SUPPORTED_UNVERIFIED
PARTIAL
SIMULATED
UNSUPPORTED
```

`SIMULATED` is reserved for things that look like the feature but
are an emulation (e.g., the in-memory CICS runtime, the
`IndexedFile` adapter used in place of VSAM). `SIMULATED` is never
acceptable as evidence for `VERIFIED`; it is reported as
`EMULATED` in the migration report.

### 20.2 Propagation

A feature flagged `UNSUPPORTED` is treated as a *hard* finding:

- IR validation produces a `Diagnostic { severity: ERROR, kind:
  UNSUPPORTED_FEATURE }`.
- The migration cannot reach `PASS`. The verdict is at best
  `PARTIAL` (with explicit list of unsupported features) or
  `ENVIRONMENT_BLOCKED` (if the feature is needed but the
  environment cannot host it).
- A build with `UNSUPPORTED_FEATURE` diagnostics cannot ship.

A `SIMULATED` feature is allowed to produce a passing build **only
if** the user opts in to `EMULATED` mode. The migration report
labels the build as `EMULATED`, not `VERIFIED`. This aligns with
the classification vocabulary in `AGENTS.md §17`.

### 20.3 What this prevents

- `unsupported → comment → compile → PASS` (1D-06): no comment is
  emitted; the diagnostic is loud.
- Missing SQLCODE flow (1E-07): SQLCODE is first-class, so its
  absence is a feature gap, not a comparator weakness.

---

## 21. Determinism

### 21.1 Stable ordering

- All maps and sets in the IR are traversed in insertion order.
  Insertion order is determined by source order, not by hashing.
- Identifiers are stable ULIDs derived from
  `(file_id, kind, source_index)`. They are deterministic across
  runs.

### 21.2 Stable IDs and hashes

- `provenance_hash` is `sha256(id || attrs_canonical)` with a
  canonical JSON serialization of attrs.
- The whole `CompilationUnit` has a `unit_hash` =
  `sha256(concat(sorted_provenance_hashes))`.

### 21.3 Reproducible output paths

- Generated files are written to
  `out/<unit_hash>/src/main/java/...`.
- The `out` root is configurable but the structure is fixed.
- A second run on identical inputs produces byte-identical files
  (modulo optional headers; we use a header that records the
  `unit_hash`, which is itself deterministic).

### 21.4 Tests

- **Reproducibility test**: re-run the pipeline on the same input
  in a fresh workspace, assert byte-identical generated files.
- **Hash test**: assert that the unit hash matches a known fixture.

---

## 22. Provenance / Evidence

### 22.1 Hash chain

The following are content-hashed (sha256) and recorded in an
append-only `evidence.jsonl`:

- Each source file (COBOL, COPYBOOK, JCL, BMS, PROC, SQL).
- Parser/transformer versions.
- Canonical IR (full serialization).
- Generated Java (per file).
- `pom.xml`.
- Resolved Maven dependencies (effective POM, plus a `tree` dump).
- Input fixtures (test data files).
- Baseline executable (sha256 of the compiled binary + image).
- Java executable (sha256 of the JAR).
- Stdout, stderr, output files, database observations.
- Comparison result (PASS/FAILED/UNVERIFIED/…).

### 22.2 Immutability

- `evidence.jsonl` is append-only. Each line is signed with an
  HMAC over the previous line's signature (hash chain).
- A run cannot overwrite a previous run's evidence.
- A compromise of the running process cannot forge PASS because the
  signature is computed by a separate, locked-down signer process
  (or, in V2.0, by an HMAC backed by a process-internal key in
  a `SecureRandom`-seeded per-run keystore, with the keystore
  itself hashed into the evidence file).

### 22.3 PASS is reproducible from evidence

A separate `verify_evidence` command can re-run verification from
the evidence file alone, asserting that the recorded observations
match the expected ones and that the chain is intact. This is the
final defense against 1E-01 / 1E-02.

---

## 23. Baseline Trust

A baseline is a *binding* to:

- A `baseline_unit_hash` (the hash of the COBOL input + tooling
  version at baseline time).
- A `baseline_run_id` (a unique id created at baseline time).
- A timestamp and a signer identity.

At verification time:

- If the current `unit_hash` does not match `baseline_unit_hash`,
  the baseline is **rejected** as stale (closes 1E-01).
- If the baseline executable is missing or its hash does not
  match `baseline_run_id`, the baseline is rejected.
- A baseline that failed to compile or execute cannot be reused.
  Its `baseline_run_id` is recorded as `INVALID`; a new baseline
  must be built before verification can proceed.
- If a baseline is not available, the verdict is
  `ENVIRONMENT_BLOCKED` (1E-02 closed). The migration is not
  considered `PASS`-eligible.

### 23.1 Why these rules

- Stale baseline is the single most important false-PASS vector.
  A hash-based binding makes it cryptographically detectable.
- Swallowed baseline failure is closed because the failure is now
  a hard blocker of the entire verification, not a warning.

---

## 24. Differential Verification V2

### 24.1 What is compared

For every workload, the comparison is over the **complete
observation tuple**:

- `exit_code` (must match).
- `stdout` (full content; §24.2).
- `stderr` (full content; the comparator does not require stderr
  to be empty, only to match).
- `output_files` (path, content, mtime range).
- `output_file_order` (sorted by path; if the contract specifies a
  sort key, sorted by that key).
- `database_state` (table-by-table row count, key uniqueness, and
  for each contract-declared row, full row equality).
- `sqlcode_sequence` (per SQL operation, ordered by call index).
- `sqlstate_sequence` (same).
- `null_indicator_sequence` (per host variable, per operation).
- `transaction_state` (committed / rolled-back per transaction
  boundary).
- `file_status_sequence` (per file operation).
- `cics_state` (channel, container, commarea snapshot at program
  boundary, when applicable).
- `batch_state` (Step exit status, ExecutionContext snapshot, when
  applicable).

### 24.2 stdout is no longer truncated

- The full stdout is compared, line by line, with normalizations
  applied (whitespace collapse, line-ending collapse).
- Timestamps are normalized to a configurable
  reference time, with the offset recorded in the observation.
- Locale is normalized: numeric formatting is locked to `en_US`
  by default; the comparator can be configured to compare raw
  bytes instead.

### 24.3 Missing expected observations

If a dimension is required by the contract and is absent from the
observation, the verdict is `UNVERIFIED`, not `PASS`. This closes
1E-03 / 1G-01.

### 24.4 Comparator

The comparator is a pure function:

```
compare(observed_cobol: Observation, observed_java: Observation,
        contract: VerificationContract) -> ComparisonResult
```

It is testable in isolation. The comparator is **not** allowed to
read environment variables, the current time, or the filesystem
beyond the observations it is given. This makes the comparator
unit-testable and removes a class of bypasses.

### 24.5 Result

```
ComparisonResult {
  status: PASS | FAILED | UNVERIFIED,
  dimension_results: Dict[str, DimensionResult],
  contract_id,
  observed_hash_cobol,
  observed_hash_java,
  verifier_version
}
```

### 24.6 SQLCODE / SQLSTATE / NULL

The observation captures the SQLCODE/SQLSTATE/indicator sequence
per call index. The comparator checks the sequence element-wise.
A mismatch in any element is `FAILED`, with the exact call index
and the two values reported.

### 24.7 Logical file match

The comparator supports three modes, *chosen by the contract*:

- `PHYSICAL` (default): record-by-record in path order.
- `KEY_SORTED`: both sides sorted by primary key.
- `SET` (last resort): sets of records compared, ignoring order.

The mode is recorded in the contract and in the evidence. The
verifier *never* chooses the mode implicitly; the mode is a
contract decision. This closes 1E-06.

---

## 25. Security Architecture

### 25.1 Generated Java injection (1G-03, NEW-01)

Java source is emitted from a **typed Java AST**, not from string
concatenation. The COBOL DISPLAY literal becomes a `JExpr.lit(s)`
node, which is serialized by escaping Java-significant characters
at the AST level. There is no path through which a COBOL source
character can break out of a Java string literal.

### 25.2 Arbitrary SQL via data files (1G-04, 1E-05)

- `data/*.sql` is *not* auto-executed. The platform has an
  explicit `seed` step that takes a list of named seed files
  declared in the workload contract.
- The seed executor is allow-listed: only `INSERT INTO <declared_table>`
  and `MERGE INTO <declared_table>` are accepted. Anything else
  produces a `Diagnostic { severity: ERROR }` and the run fails
  closed.
- The seed executor is parameterized: placeholders are bound by
  the workload configuration.

### 25.3 Path traversal (1G-08, NEW-01)

- All filesystem paths are normalized via
  `os.path.realpath` and bounded to the per-run workspace.
- COPY paths are validated against the workspace root.
- Generated file paths are checked for `..` segments before write.

### 25.4 Reflection (1G-06)

- `Class.forName` is removed from the generated code path.
- Program dispatch uses a typed registry populated by Spring DI.

### 25.5 Docker mounts

- Source directories are mounted **read-only**.
- The output directory is mounted **read-write**, into a path
  unique to the run.
- Containers are run with `--network=none` unless network access
  is required by the workload; if network is required, an
  explicit allow-list is configured.

### 25.6 subprocess / shell

- No `shell=True`. All subprocess invocations use argument arrays.
- All subprocess invocations have a hard timeout, measured from
  a single `Process` start.
- All subprocess invocations log the working directory and the
  resolved (sanitized) command.

### 25.7 Credentials and secrets

- Secrets are read from the process environment and never logged.
- Docker images are not built with `ARG PASSWORD=...`.
- Database credentials are injected at connection time, not via
  file.

### 25.8 Concurrent execution isolation (1G-07, NEW-02)

- Each run has a unique `run_id` and a per-run workspace
  (`workspaces/<run_id>/`).
- `MockSqlService` is replaced by a per-`run_id` Spring bean
  scope; no static state is shared across runs.
- Database connections are per-`run_id`.

### 25.9 Supply chain

- `pom.xml` plugin versions are pinned.
- Dependency hashes are recorded in the SBOM (§27.4).
- Vendored ProLeap (if used) is treated as an input to the
  parser, not as a runtime of the generated code.

---

## 26. Repository / Module Structure V2

### 26.1 Current (CURRENT)

```
modernize/
  lexer.py
  parser.py
  semantic_ir.py
  control_flow.py
  dependency_analysis.py
  native_generator.py
  enterprise_generator.py
  native_pipeline.py
  proleap/...
  java_helpers/  (CobolNumeric, MockSqlService, CicsTransactionContext, …)
execution/
  equivalence.py
  runner.py
tests/
parity/
fixtures/
.github/
```

### 26.2 Transition (PROPOSED — Phase 2A–2F)

```
modernize_v2/                              # new package, co-exists with modernize/
  __init__.py
  source/
    workspace.py                           # isolated workspace, source map
    preprocessor.py                        # COPY / REPLACE / format normalize
    lexer.py                               # typed token stream
    parser.py                              # deterministic AST
    recovery.py                            # explicit, gated, recorded
  ir/
    ids.py                                 # stable ids
    canonical.py                           # CanonicalIR + node kinds
    expr.py                                # Expression AST
    data_item.py                           # DataItem tree
    storage.py                             # LayoutComputer
    symbols.py                             # SymbolTable, Scope
    types.py                               # COBOL type system
  analysis/
    resolver.py                            # name resolution
    typecheck.py                           # type checking
    cfg.py                                 # CFG builder
    dataflow.py                            # def-use, liveness, nullability
    callgraph.py                           # call graph, linkage
  capabilities/
    registry.py                            # feature → capability mapping
    gate.py                                # UNSUPPORTED propagation
  codegen/
    java_ast.py                            # typed Java AST
    java_emitter.py                        # AST → text, deterministic
    spring_boot.py
    spring_batch.py
  sql/
    sql_ast.py
    sql_analyzer.py
    sql_dialect_postgres.py
    sql_runtime.py
  fileio/
    file_semantics.py
    adapters/
      sequential.py
      indexed.py
      relative.py
    record_codec.py
  cics/
    cics_ast.py
    cics_runtime.py
  jcl/
    jcl_ast.py
    jcl_to_spring_batch.py
  encoding/
    encoding.py
    transcoders/
  pipeline/
    pipeline.py
    build.py
    execute.py
    observe.py
  verification/
    contract.py
    observation.py
    comparator.py
    verdict.py
  evidence/
    provenance.py                          # hashing, signing
    evidence_store.py
  security/
    path_safety.py
    sql_seed_policy.py
    subprocess_policy.py
    workspace_isolation.py
modernize/                                 # legacy: kept, marked deprecated
  ...
```

### 26.3 Target (TARGET — post Phase 2)

```
modernize/                                 # V2 promoted to this package
  ... (all V2 modules, with legacy entry points removed)
legacy_modernize/                          # retained as a "pre-V2" compatibility shim
  ...
```

The exact promotion date is decided in `PHASE_2_DECISION_REGISTER.md`.

---

## 27. Migration Strategy

The platform must not destroy its existing verified workloads.
They become **regression fixtures** for V2.

### 27.1 Component classification

| Component                            | Class        | Notes |
|--------------------------------------|--------------|-------|
| `lexer.py` (legacy)                  | REFACTOR     | Token shape; port to typed tokens |
| `parser.py` (legacy)                 | REPLACE      | Replaced by `ir/parser.py` |
| `semantic_ir.py` (legacy)            | REPLACE      | Replaced by `ir/canonical.py` |
| `control_flow.py`                    | REFACTOR     | Becomes `analysis/cfg.py`, consumed |
| `dependency_analysis.py`             | REFACTOR     | Becomes `analysis/callgraph.py` |
| `native_generator.py`                | REPLACE      | Replaced by `codegen/java_emitter.py` |
| `enterprise_generator.py`            | REFACTOR     | Becomes `codegen/spring_boot.py` + `codegen/spring_batch.py` |
| `native_pipeline.py`                 | REFACTOR     | Becomes `pipeline/pipeline.py` |
| `equivalence.py`                     | REPLACE      | Replaced by `verification/comparator.py` |
| `MockSqlService`                     | REPLACE      | Replaced by `sql/sql_runtime.py` |
| `CobolNumeric`                       | REPLACE      | Replaced by `runtime/DecimalArithmetic` (scope-limited) |
| `CobolString`                        | REPLACE      | Java `String` with explicit helpers |
| `CicsTransactionContext`             | REPLACE      | `cics/cics_runtime.py` (`InMemoryCicsRuntime`) |
| `CicsProgramRegistry`                | REPLACE      | Spring-managed registry |
| `JclExecutionContext`                | REPLACE      | `jcl/jcl_to_spring_batch.py` |
| `SpringContextHelper`                | REMOVE       | Replaced by real DI |
| Existing verified workloads          | KEEP         | Becomes regression fixtures |
| Existing test corpus                 | KEEP         | Becomes regression corpus |
| Existing evidence                    | KEEP         | Quarantined; not used as V2 evidence |

### 27.2 Strategy

1. **Build V2 alongside V1.** V1 is the source of the existing
   evidence. V1's test suite continues to pass while V2 is built.
2. **V2 correctness is established against the same workloads.**
   V1 results become expected outputs only in a **regression**
   test, never in V2's primary differential verdict.
3. **Once V2 reaches equivalence with V1 on the existing corpus,
   promote V2 to be the default. V1 is moved to
   `legacy_modernize/` and marked deprecated.**
4. **The platform never deletes the existing V1 code without
   explicit approval.** Historical evidence must remain
   inspectable.

### 27.3 What "equivalent" means in the transition

V2 is considered equivalent to V1 if and only if:

- For each workload in the existing corpus, the V2 differential
  verdict (against the same COBOL source) matches the V1 verdict
  on the same dimensions *except* where V2 is stronger (e.g., it
  detects a missing statement that V1 missed).
- The V2 verdict is never *weaker* than V1's on any workload.

---

## 28. Test Strategy

The V2 test strategy is layered and adversarial. Each layer
**must** include negative tests designed to fail loudly.

| Layer                  | Test type      | Adversarial focus                                |
|------------------------|----------------|--------------------------------------------------|
| Lexer                  | UNIT           | malformed literals, continuations, free vs fixed |
| Parser                 | UNIT           | recovery, dangling END, ambiguity                |
| Expression AST         | UNIT           | NULL literal, host variable shadowing            |
| Type system            | UNIT           | overflow, signed/unsigned mismatch               |
| Symbol table           | UNIT           | qualification, REDEFINES, COPY scope            |
| CFG                    | UNIT           | GO TO DEPENDING ON, EXIT PERFORM                 |
| Data flow              | UNIT           | def-use across ODO, indicator variable flow      |
| Call graph             | UNIT           | dynamic CALL, recursive CALL, BY VALUE           |
| Preprocessor           | UNIT           | nested COPY, REPLACING, cycle, depth limit       |
| SQL semantic           | UNIT           | NULL indicator, SQLCODE flow, parameterization   |
| File/VSAM              | UNIT           | alternate key, START, file status, RBA           |
| CICS                   | UNIT           | COMMAREA mutation, EIB fields, syncpoint        |
| JCL                    | UNIT           | COND, restart, GDG, multi-step                   |
| Encoding               | UNIT           | EBCDIC ↔ ASCII, packed-decimal round-trip        |
| Codegen                | UNIT           | structural Java AST assertions                   |
| Compile                | INTEGRATION    | Maven build, no libcobj                          |
| Runtime                | INTEGRATION    | exits, exceptions, no reflection                 |
| Differential           | E2E            | every workload, full observations                |
| Mutation               | ADVERSARIAL    | per statement, per dimension                     |
| Security               | SECURITY       | injection, traversal, subprocess, isolation      |
| Reproducibility        | REGRESSION     | byte-identical output, hash stability            |
| Provenance             | REGRESSION     | evidence re-verification                         |
| Concurrency            | REGRESSION     | run isolation                                    |

### 28.1 Mutation tests

The mutation harness is mandatory. For each workload, a mutation
campaign applies the false-PASS attack matrix (Phase 1G) and
asserts that the **V2** comparator reports `FAILED`. The mutation
campaign itself is a regression test in CI.

### 28.2 Negative tests (FAIL-LOUD)

A negative test that *passes* is a defect. Every negative test
**must** be marked `xfail` with a clear reason and a link to the
diagnostic that it triggers. When the underlying defect is
addressed, the xfail is removed.

---

## 29. Phase-by-Phase Implementation Roadmap

| Phase | Objective | Dependencies | New interfaces | Tests required | Acceptance | Risks | Exit gate |
|-------|-----------|--------------|----------------|----------------|------------|-------|-----------|
| **2A** | Architecture & contracts | none | `IR` types, `Capability` enum, `Diagnostic`, `Observation`, `ComparisonResult` | unit tests for enums and dataclasses | all interfaces have unit tests; document linked | naming churn | `make arch-2A` passes |
| **2B** | Canonical IR | 2A | `CanonicalIR`, `CompilationUnit`, `DataItem`, `SourceSpan`, `provenance_hash` | IR unit tests; fixture round-trip | IR round-trips losslessly for at least the existing corpus | over-engineering | `ir_round_trip` test green |
| **2C** | Expression AST + symbol/type system | 2B | `Expr` hierarchy, `CobolType`, `JavaTypeRef`, `SymbolTable` | expression tests, type tests | `NULL` literal is recognized; host var shadowing is rejected | late-bound types | expression tests green |
| **2D** | CFG + data-flow + call graph | 2B, 2C | `BasicBlock`, `Terminator`, def-use, liveness, call graph | CFG/DFA unit tests | generator consumes CFG, not IR order | incomplete terminators | CFG consumer test green |
| **2E** | Preprocessor correctness | 2B | `CopybookMap`, `IncludeGraph`, cycle detection | COPY, REPLACING, REPLACE tests | nested COPY works; cycles fail-closed | path handling | preprocessor tests green |
| **2F** | Deterministic transformation framework | 2A, 2B | stable IDs, hash, JSON canonicalization, byte-identical output | reproducibility tests | same input ⇒ byte-identical output across two runs | hash collisions | `reproducibility` test green |
| **2G** | Native Java generation | 2B, 2C, 2D, 2F | `JExpr`/`JStmt`/`JDecl`, `java_emitter` | codegen unit tests, `javac` smoke | generated `javac` compiles, no paragraph dispatcher, no `Class.forName` | scope creep | codegen tests + `javac` green |
| **2H** | SQL/file/runtime semantic adapters | 2C, 2G | `sql_ast`, `sql_runtime`, `IndexedFile`, `RecordCodec`, `InMemoryCicsRuntime`, `JclToSpringBatch` | unit tests per adapter | SQL DDL emitted; VSAM/INDEXED adapter verified on at least one workload; CICS in-memory runtime passes contract | dialect gaps | adapter tests green |
| **2I** | Spring Boot / Spring Batch architecture | 2G, 2H | `SpringBootCodegen`, `SpringBatchCodegen` | integration tests | generated project is a normal Spring Boot app; no `Main.main()` wrapped in a Tasklet | DI mistakes | generated app boots |
| **2J** | Independent verification V2 | 2H, 2I | `Observation`, `Contract`, `Comparator`, `Verdict` | comparator unit tests, full-observation differential tests | stdout is full; SQLCODE/SQLSTATE first-class; missing expected obs ⇒ UNVERIFIED | comparator correctness | comparator tests green |
| **2K** | Provenance / security / CI hardening | 2J, 2F | `evidence.jsonl`, signer, `verify_evidence`, `path_safety`, `sql_seed_policy`, `subprocess_policy` | security tests, evidence re-verify | hash chain intact; replay returns same verdict; injection tests fail-closed | operational overhead | `verify_evidence` green on a real run |
| **2L** | Realistic enterprise workloads | 2K | (test-only) | unseen-repository regression suite | platform passes on at least three unseen repositories | scope | three-unseen-repo gate green |

### 29.1 Phase 2A — Architecture & contracts

- **Objective**: Stabilize the type vocabulary and the data classes
  that everything else depends on.
- **Files**: `modernize_v2/ir/ids.py`, `modernize_v2/ir/canonical.py`
  (skeletons), `modernize_v2/capabilities/registry.py`,
  `modernize_v2/verification/contract.py` (skeletons).
- **Acceptance**: All public dataclasses have round-trip unit tests.

### 29.2 Phase 2B — Canonical IR

- **Objective**: Property-bag IR is gone; typed IR is the single
  source of truth.
- **Files**: `modernize_v2/ir/canonical.py`, `modernize_v2/ir/data_item.py`,
  `modernize_v2/ir/storage.py`, `modernize_v2/ir/symbols.py`,
  `modernize_v2/ir/types.py`.
- **Acceptance**: IR round-trips losslessly for the existing
  corpus; old property-bag code paths are no longer reachable from
  the new pipeline.

### 29.3 Phase 2C — Expression AST + symbol/type system

- **Objective**: No more expression strings; full typed expression
  model.
- **Files**: `modernize_v2/ir/expr.py`, `modernize_v2/analysis/resolver.py`,
  `modernize_v2/analysis/typecheck.py`.
- **Acceptance**: `NULL` is a literal; host variables do not shadow
  it; type mismatches produce diagnostics; Java target types are
  decided at IR time.

### 29.4 Phase 2D — CFG + data-flow + call graph

- **Objective**: The generator consumes a real CFG.
- **Files**: `modernize_v2/analysis/cfg.py`, `dataflow.py`,
  `callgraph.py`.
- **Acceptance**: Generator is a CFG consumer; code paths that
  read IR order are not allowed in the new generator.

### 29.5 Phase 2E — Preprocessor correctness

- **Objective**: COPY/REPLACE/REPLACING are correct, deterministic,
  and cycle-safe.
- **Files**: `modernize_v2/source/preprocessor.py`.
- **Acceptance**: Nested COPY; cycle detection; depth limit;
  source map.

### 29.6 Phase 2F — Determinism

- **Objective**: Same input ⇒ byte-identical output.
- **Files**: `modernize_v2/ir/ids.py`, JSON canonicalization,
  `modernize_v2/codegen/java_emitter.py` (sorting invariants).
- **Acceptance**: Reproducibility test green.

### 29.7 Phase 2G — Native Java generation

- **Objective**: Generated Java is genuine native Java.
- **Files**: `modernize_v2/codegen/java_ast.py`,
  `java_emitter.py`.
- **Acceptance**: No `Class.forName`, no paragraph dispatcher,
  no `Main.main()` wrapped in a Tasklet. Generated code uses
  standard Java types and Spring DI.

### 29.8 Phase 2H — Semantic adapters

- **Objective**: SQL, file, CICS, JCL, and encoding models are
  real, not string-emulated.
- **Files**: `modernize_v2/sql/*`, `modernize_v2/fileio/*`,
  `modernize_v2/cics/*`, `modernize_v2/jcl/*`,
  `modernize_v2/encoding/*`.
- **Acceptance**: Each adapter is exercised end-to-end on at least
  one workload.

### 29.9 Phase 2I — Spring Boot / Batch

- **Objective**: Generated applications are real Spring Boot / Batch.
- **Files**: `modernize_v2/codegen/spring_boot.py`,
  `spring_batch.py`.
- **Acceptance**: Generated `pom.xml` produces a real Spring Boot
  JAR; multi-step JCL produces a real `Job` with multiple
  `Step`s.

### 29.10 Phase 2J — Differential verification V2

- **Objective**: Comparator compares complete observations; missing
  expected obs ⇒ `UNVERIFIED`.
- **Files**: `modernize_v2/verification/*`.
- **Acceptance**: Mutation campaign produces `FAILED` for all
  known false-PASS attacks.

### 29.11 Phase 2K — Provenance, security, CI hardening

- **Objective**: Hash chain; security controls; CI gates.
- **Files**: `modernize_v2/evidence/*`, `modernize_v2/security/*`,
  `.github/workflows/*`.
- **Acceptance**: `verify_evidence` command passes on a real run;
  injection tests fail-closed.

### 29.12 Phase 2L — Realistic enterprise workloads

- **Objective**: Platform is exercised on unseen repositories.
- **Files**: `tests/unseen_repos/`.
- **Acceptance**: Three unseen repositories pass the V2 pipeline
  with explicit evidence.

---

## 30. Acceptance Criteria for "True Native Java"

V2 code is "true native Java" iff **all** of the following are
demonstrable by automated tests:

1. The generated application compiles with `javac` *without* the
   COBOL source present.
2. The generated application runs with `java` *without* a
   `paragraph_dispatcher` or a `statement_bag` interpreter.
3. There is no `Class.forName("...cobol..." + name)` in the
   generated code.
4. There is no `import com.systema.modernized.runtime.*;` in the
   generated code.
5. There is no `libcobj.jar`, `jp.osscons.*`, or
   OpenSourceCOBOL4J dependency in the generated `pom.xml`.
6. Business logic exists as structured Java control flow
   (`if/else`, `switch`, `for`, `while`, `try/catch`).
7. Java types correspond to semantic types (mapping per §8.3).
8. Spring dependencies use normal DI; no `static` field holds a
   bean.
9. Transactions are explicit (`@Transactional` or
   `TransactionTemplate`).
10. Batch workloads use real Spring Batch architecture (real
    `ItemReader`/`ItemProcessor`/`ItemWriter`, real `Job`/`Step`
    composition, restartable).
11. Unsupported semantics cannot silently disappear: a missing
    construct produces a `Diagnostic` and prevents `PASS`.
12. Generated output is byte-identical across two consecutive runs
    on the same input.
13. Independent equivalence evidence exists: a `verify_evidence`
    command re-derives the verdict from the evidence file alone.
14. Migration report classifies each feature as one of
    `VERIFIED / EMULATED / PARTIAL / UNSUPPORTED /
    NOT_VERIFIED / ENVIRONMENT_BLOCKED`, matching implementation.

A workload that fails any of these cannot be classified
`VERIFIED`.

---

## 31. Risks and Trade-offs

| Risk                                            | Impact | Mitigation |
|-------------------------------------------------|--------|------------|
| IR rewrite breaks the existing corpus           | High   | V1 corpus becomes regression fixture; V2 must match or improve on V1 |
| V2 codegen scope creep                           | High   | Phase 2G has a strict no-interpreter rule; review gate |
| Determinism vs. performance                     | Medium | All collections ordered; canonical JSON |
| Migration of large enterprise workloads          | High   | Phase 2L exercises three unseen repos before sign-off |
| `EMULATED` vs `VERIFIED` semantics              | Medium | Classifier in `AGENTS.md §17` is the contract |
| Removal of V1 helpers breaks consumers          | Medium | V1 shim under `legacy_modernize/` retained |
| Comparator migration is a single big-bang risk  | High   | Phase 2J accepts `UNVERIFIED` until proven |
| ProLeap compatibility                            | Medium | V2 treats ProLeap as an input to the parser only |
| Maven / dependency drift                        | Medium | Pinned plugin versions; SBOM; offline mode |
| DB2 / VSAM / CICS gap remains                    | High   | Honest `SUPPORTED_UNVERIFIED` classification; no false claims |

---

## 32. Decisions Requiring Explicit Approval

These decisions are documented in
`docs/PHASE_2_DECISION_REGISTER.md`. Each requires an explicit
"approved / rejected / deferred" before implementation:

1. Promotion of `modernize_v2/` to `modernize/` and movement of
   the existing V1 to `legacy_modernize/`.
2. Deletion of the legacy V1 helpers (`CobolNumeric`,
   `CobolString`, `MockSqlService`, `CicsTransactionContext`,
   `SpringContextHelper`, `JclExecutionContext`).
3. Whether to keep ProLeap as a parser-time input or to deprecate
   it entirely.
4. Whether `EMULATED` workloads are allowed in the V2 corpus, and
   under what labelling.
5. Whether the comparator's `SET` (order-insensitive) mode is
   allowed in V2 contracts at all.
6. Whether to require real DB2 for `VERIFIED` DB2 classifications,
   and what the path to that is.
7. The runtime version policy (Java 17/21), Spring version
   policy, and Maven plugin version policy.
8. Whether Track-A (the legacy emulator) is retained in V2 or
   deprecated.

---

## 33. Final Recommendation

**Proceed with Phase 2A–2L as described.**

The current implementation is not a foundation for production
modernization; it is a property-bag interpreter wrapped in a
Java-emulator runtime, with a comparator whose PASS verdict is
not trustworthy. Continuing on the current code path will
accumulate more `PARTIAL` / `EMULATED` features without addressing
the structural defects.

The proposed V2 architecture:

- Replaces the property-bag IR with a canonical typed IR.
- Replaces string expressions with a typed expression AST.
- Replaces interpreter-style codegen with CFG-driven, Java-AST
  codegen.
- Replaces the COBOL emulator runtime with domain helpers (and
  removes what is not needed).
- Replaces the contract-gated, truncated comparator with a
  full-observation differential verifier.
- Replaces the artifact-less pipeline with a content-hashed,
  append-only evidence chain.

These changes are non-trivial but are individually scoped and
testable. The Phase 2A–2L roadmap makes the work decomposable.
The decision register and the work breakdown
(`PHASE_2_DECISION_REGISTER.md`, `PHASE_2_WORK_BREAKDOWN.md`)
are the operational artefacts that turn this architecture into
scheduled, reviewable work.

We **do not** lower the acceptance criteria to make the current
implementation qualify. Track-B is native Java; legacy emulation
helpers are not part of it.
