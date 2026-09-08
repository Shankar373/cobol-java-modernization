# PHASE 2 — WORK BREAKDOWN

Status: **PROPOSED — TICKETS READY FOR ASSIGNMENT**

Companion docs:
- `docs/PHASE_2_ARCHITECTURE_V2.md`
- `docs/PHASE_2_DECISION_REGISTER.md`

This document is the actionable implementation backlog for
Phase 2. Tickets are grouped by phase (2A–2L). Each ticket has:

- a unique `T-ID`
- a `Phase` label
- a `Priority` (`P0` critical path, `P1` high, `P2` medium)
- an `Owner` placeholder
- `Depends on` (T-IDs)
- an `Acceptance` criterion (objective)
- a `Verification` step
- a `Risk` note

`P0` tickets are on the critical path. The first 10 tickets to
start are at the bottom of this document.

---

## Phase 2A — Architecture & Contracts

### T-2A-01 — Define IR ID scheme
- **Phase**: 2A
- **Priority**: P0
- **Depends on**: —
- **Files**: `modernize_v2/ir/ids.py`
- **Acceptance**: A function `new_id(kind, source)` returns a
  deterministic 26-char Crockford base32 ULID. Two calls with
  the same inputs return the same id. The id space is
  partitioned by `kind`.
- **Verification**: Unit tests for determinism, length,
  character set, partition, and uniqueness across 1M
  generations.
- **Risk**: Hash collisions across kinds.

### T-2A-02 — Define `IRKind` enum
- **Phase**: 2A
- **Priority**: P0
- **Depends on**: —
- **Files**: `modernize_v2/ir/canonical.py`
- **Acceptance**: An `IRKind` enum with at least 80 values
  covering CompilationUnit, Program, IdentificationDivision,
  EnvironmentDivision, DataDivision, ProcedureDivision,
  FileSection, WorkingStorageSection, LocalStorageSection,
  LinkageSection, ReportSection, FD, SD, Paragraph, Section,
  Sentence, Statement (one per kind), Expr (one per kind),
  DataItem, GroupItem, ElementaryItem, OdoClause,
  OccursClause, RedefinesClause, RenamesClause, Level88Item,
  SqlStatement, CicsStatement, JclStep, DdStatement.
- **Verification**: `len(IRKind) >= 80` asserted in a unit test.

### T-2A-03 — Define `Diagnostic` model
- **Phase**: 2A
- **Priority**: P0
- **Depends on**: —
- **Files**: `modernize_v2/ir/diagnostic.py`
- **Acceptance**: `Diagnostic` has `severity` (ERROR, WARNING,
  INFO), `kind` (UNSUPPORTED_FEATURE, UNRESOLVED_SYMBOL,
  TYPE_MISMATCH, REDEFINES_OVERLAP, ODO_OUT_OF_BOUNDS, etc.),
  `span: SourceSpan`, `message`, `workload_id`. Diagnostic
  records are append-only.
- **Verification**: Unit tests for severity, kind, span
  formatting.

### T-2A-04 — Define `Capability` enum and gate
- **Phase**: 2A
- **Priority**: P0
- **Depends on**: T-2A-03
- **Files**: `modernize_v2/capabilities/registry.py`,
  `modernize_v2/capabilities/gate.py`
- **Acceptance**: `Capability` enum has
  `SUPPORTED_AND_VERIFIED, SUPPORTED_UNVERIFIED, PARTIAL,
  SIMULATED, UNSUPPORTED`. `CapabilityGate` raises a
  `Diagnostic(severity=ERROR, kind=UNSUPPORTED_FEATURE)` for
  `UNSUPPORTED` features and refuses to continue. A
  `SIMULATED` feature records a diagnostic with severity
  `WARNING` and labels the workload as `EMULATED`.
- **Verification**: Unit tests for each capability value.

### T-2A-05 — Define `Observation` and `ComparisonResult` types
- **Phase**: 2A
- **Priority**: P0
- **Depends on**: T-2A-01, T-2A-04
- **Files**: `modernize_v2/verification/observation.py`,
  `modernize_v2/verification/verdict.py`
- **Acceptance**: `Observation` has fields
  `run_id, workload_id, exit_code, stdout, stderr,
  output_files, db_state, sqlcode_seq, sqlstate_seq,
  null_indicator_seq, transaction_state, file_status_seq,
  cics_state, batch_state, observed_at, encoding,
  content_hash`. `ComparisonResult` has `status: PASS |
  FAILED | UNVERIFIED`, `dimension_results: dict[str,
  DimensionResult]`, `contract_id`, `observed_hash_cobol`,
  `observed_hash_java`, `verifier_version`.
- **Verification**: Unit tests for round-trip JSON.

### T-2A-06 — Define `VerificationContract` type
- **Phase**: 2A
- **Priority**: P0
- **Depends on**: T-2A-05
- **Files**: `modernize_v2/verification/contract.py`
- **Acceptance**: `VerificationContract` declares which
  dimensions are required, the comparison mode per
  dimension (`PHYSICAL`, `KEY_SORTED`, `SET`), the
  encoding, and the seed list. Missing a required
  dimension is a contract validation error.
- **Verification**: Unit tests.

### T-2A-07 — Document the public type vocabulary
- **Phase**: 2A
- **Priority**: P1
- **Depends on**: T-2A-01..06
- **Files**: `docs/PHASE_2_TYPE_VOCABULARY.md` (new)
- **Acceptance**: A short doc that names every public type,
  its purpose, and its invariants.
- **Verification**: Doc renders; cross-references match.

### T-2A-08 — Bootstrap modernize_v2 package
- **Phase**: 2A
- **Priority**: P0
- **Depends on**: —
- **Files**: `modernize_v2/__init__.py`,
  `pyproject.toml` (or equivalent) entry, CI import test
- **Acceptance**: `import modernize_v2` succeeds. The package
  has a top-level `__version__` and a public `__all__`.
- **Verification**: CI import test green.

---

## Phase 2B — Canonical IR

### T-2B-01 — Source map and workspace model
- **Phase**: 2B
- **Priority**: P0
- **Depends on**: T-2A-01, T-2A-08
- **Files**: `modernize_v2/source/workspace.py`,
  `modernize_v2/source/source_map.py`
- **Acceptance**: `Workspace` exposes files by stable id,
  with a `SourceMap` for byte-offset to `(file_id, line,
  col)` translation. Path traversal raises.
- **Verification**: Unit tests for traversal, offsets.

### T-2B-02 — Lexer for COBOL (fixed + free format)
- **Phase**: 2B
- **Priority**: P0
- **Depends on**: T-2B-01
- **Files**: `modernize_v2/source/lexer.py`
- **Acceptance**: Tokens carry `id, kind, span, lexeme`. The
  lexer recognizes both fixed and free format. Continuation
  lines are folded with span expansion. Comment lines are
  preserved in the source map (not in the token stream).
- **Verification**: Unit tests on canonical COBOL samples.

### T-2B-03 — Preprocessor (COPY / REPLACE / REPLACING)
- **Phase**: 2E (out of order, but the dependency is small)
- **Priority**: P0
- **Depends on**: T-2B-02
- **Files**: `modernize_v2/source/preprocessor.py`
- **Acceptance**: COPY/REPLACING/REPLACE work, with
  deterministic expansion, cycle detection, and a depth
  limit. The source map records the expansion path.
- **Verification**: Unit tests for nested COPY, REPLACING,
  cycle detection, depth limit.

### T-2B-04 — Parser for COBOL (skeleton)
- **Phase**: 2B
- **Priority**: P0
- **Depends on**: T-2B-02, T-2B-03
- **Files**: `modernize_v2/source/parser.py`
- **Acceptance**: Parser produces a typed AST. Recovery is
  explicit: a `RecoveryRecord` records the span that was
  skipped and the reason. Recovery cannot silently swallow
  siblings (a `RecoveryRecord` must be raised for any
  skipped sibling).
- **Verification**: Unit tests for recovery, including
  fixtures that previously caused sibling swallowing.

### T-2B-05 — Identifier resolution and qualification
- **Phase**: 2B
- **Priority**: P0
- **Depends on**: T-2B-04
- **Files**: `modernize_v2/analysis/resolver.py`
- **Acceptance**: Names resolve through the
  `Program → Section → Paragraph → Block` scope chain.
  Qualified names resolve unambiguously. Unresolved names
  produce a `Diagnostic(severity=ERROR,
  kind=UNRESOLVED_SYMBOL)`.
- **Verification**: Unit tests.

### T-2B-06 — DataItem tree
- **Phase**: 2B
- **Priority**: P0
- **Depends on**: T-2B-05
- **Files**: `modernize_v2/ir/data_item.py`
- **Acceptance**: `DataItem` tree is built with PIC, USAGE,
  SIGN, VALUE, OCCURS, ODO, REDEFINES, RENAMES, 66/77/78/88
  level support. REDEFINES overlap is validated.
- **Verification**: Unit tests.

### T-2B-07 — Layout computer
- **Phase**: 2B
- **Priority**: P0
- **Depends on**: T-2B-06
- **Files**: `modernize_v2/ir/storage.py`
- **Acceptance**: A `Layout` is computed deterministically
  for every record, with offsets, lengths, alignment, and
  REDEFINES handling. ODO bounds are recorded.
- **Verification**: Unit tests on representative PICs.

### T-2B-08 — COBOL type system
- **Phase**: 2B
- **Priority**: P0
- **Depends on**: T-2B-06
- **Files**: `modernize_v2/ir/types.py`
- **Acceptance**: All `CobolType` variants from §8.2 are
  implemented with `JavaTypeRef` mapping.
- **Verification**: Unit tests for type promotion and Java
  target mapping.

### T-2B-09 — `CompilationUnit` and IR serialization
- **Phase**: 2B
- **Priority**: P0
- **Depends on**: T-2B-04..08
- **Files**: `modernize_v2/ir/canonical.py`
- **Acceptance**: A `CompilationUnit` can be serialized to
  canonical JSON and back without loss. The
  `unit_hash` is reproducible.
- **Verification**: Round-trip test on existing corpus.

---

## Phase 2C — Expression AST + Symbol/Type System

### T-2C-01 — Expression AST
- **Phase**: 2C
- **Priority**: P0
- **Depends on**: T-2B-04
- **Files**: `modernize_v2/ir/expr.py`
- **Acceptance**: All `Expr` node kinds from §7.2 are
  implemented. Each carries a `CobolType`.
- **Verification**: Unit tests.

### T-2C-02 — Type checker
- **Phase**: 2C
- **Priority**: P0
- **Depends on**: T-2C-01, T-2B-08
- **Files**: `modernize_v2/analysis/typecheck.py`
- **Acceptance**: Type checker produces typed expressions
  and surfaces mismatches as diagnostics. NULL is a literal.
  Host variables do not shadow NULL.
- **Verification**: Unit tests including the Phase 1C-06
  fixture.

### T-2C-03 — Constant folder
- **Phase**: 2C
- **Priority**: P1
- **Depends on**: T-2C-02
- **Files**: `modernize_v2/analysis/constfold.py`
- **Acceptance**: Literal expressions are folded.
  Folded expressions carry a provenance note.
- **Verification**: Unit tests.

### T-2C-04 — Java target type mapping
- **Phase**: 2C
- **Priority**: P0
- **Depends on**: T-2B-08
- **Files**: `modernize_v2/ir/java_type_ref.py`
- **Acceptance**: Each `CobolType` maps to a `JavaTypeRef`
  per §8.3. The mapping is a typed function, not a heuristic.
- **Verification**: Unit tests for every mapping.

### T-2C-05 — SQL host variable flow
- **Phase**: 2C
- **Priority**: P0
- **Depends on**: T-2C-01
- **Files**: `modernize_v2/analysis/sql_flow.py`
- **Acceptance**: For every SQL statement, host variables
  are bound to expressions; indicator variables are
  tracked. NULL flow is recorded.
- **Verification**: Unit tests.

---

## Phase 2D — CFG / Data-Flow / Call Graph

### T-2D-01 — CFG builder
- **Phase**: 2D
- **Priority**: P0
- **Depends on**: T-2C-01
- **Files**: `modernize_v2/analysis/cfg.py`
- **Acceptance**: CFG builder produces `BasicBlock`s with
  `Terminator`s for all constructs in §10.2. Loops, switches,
  and `GO TO DEPENDING ON` are represented.
- **Verification**: Unit tests.

### T-2D-02 — Def-use / liveness
- **Phase**: 2D
- **Priority**: P0
- **Depends on**: T-2D-01
- **Files**: `modernize_v2/analysis/dataflow.py`
- **Acceptance**: Def-use chains, reaching definitions, and
  liveness are computed.
- **Verification**: Unit tests.

### T-2D-03 — Call graph
- **Phase**: 2D
- **Priority**: P0
- **Depends on**: T-2C-01
- **Files**: `modernize_v2/analysis/callgraph.py`
- **Acceptance**: Call graph is built with linkage
  semantics. Recursive cycles are flagged.
- **Verification**: Unit tests.

### T-2D-04 — Codegen consumes CFG (no IR order)
- **Phase**: 2D
- **Priority**: P0
- **Depends on**: T-2D-01
- **Files**: `modernize_v2/codegen/cfg_consumer.py`
- **Acceptance**: The codegen walks the CFG. A test
  fails if any codegen path walks IR source order.
- **Verification**: A static check (`grep` for known
  IR-order patterns in the codegen module) in CI.

---

## Phase 2E — Preprocessor

(see T-2B-03; Phase 2E is largely T-2B-03 plus
`IncludeGraph` and depth limits)

### T-2E-01 — `IncludeGraph` and cycle detection
- **Phase**: 2E
- **Priority**: P0
- **Depends on**: T-2B-03
- **Files**: `modernize_v2/source/include_graph.py`
- **Acceptance**: Cycles are detected and produce
  diagnostics. Depth is bounded.
- **Verification**: Unit tests for cycles, depth.

---

## Phase 2F — Determinism

### T-2F-01 — Stable ordering
- **Phase**: 2F
- **Priority**: P0
- **Depends on**: T-2B-09
- **Files**: `modernize_v2/ir/order.py`
- **Acceptance**: All collection types in the IR are
  traversed in insertion order. The IR is not allowed to
  use `set` for non-typed key collections.
- **Verification**: A lint rule (CI) checks for `set(` in
  IR-construction code.

### T-2F-02 — Canonical JSON
- **Phase**: 2F
- **Priority**: P0
- **Depends on**: T-2B-09
- **Files**: `modernize_v2/ir/canonical_json.py`
- **Acceptance**: A canonical JSON serializer is used for
  hashing. Two equal IRs produce the same hash.
- **Verification**: Unit tests.

### T-2F-03 — Reproducibility test
- **Phase**: 2F
- **Priority**: P0
- **Depends on**: T-2F-01, T-2F-02
- **Files**: `tests/reproducibility/`
- **Acceptance**: A regression test runs the pipeline on a
  fixture twice in a fresh workspace and asserts
  byte-identical generated source and identical
  `unit_hash`.
- **Verification**: Test green.

---

## Phase 2G — Native Java Generation

### T-2G-01 — Typed Java AST
- **Phase**: 2G
- **Priority**: P0
- **Depends on**: T-2A-01
- **Files**: `modernize_v2/codegen/java_ast.py`
- **Acceptance**: `JDecl`, `JStmt`, `JExpr` cover the
  minimum set needed for the existing corpus.
- **Verification**: Unit tests.

### T-2G-02 — Java emitter
- **Phase**: 2G
- **Priority**: P0
- **Depends on**: T-2G-01
- **Files**: `modernize_v2/codegen/java_emitter.py`
- **Acceptance**: Emitter is a pure function from
  `JDecl` to source text. It does not concatenate strings
  to produce executable Java; it serializes a typed AST.
- **Verification**: Unit tests asserting on AST.

### T-2G-03 — No `Class.forName` in generated code (rule)
- **Phase**: 2G
- **Priority**: P0
- **Depends on**: T-2G-01
- **Files**: CI grep check
- **Acceptance**: A CI check fails if `Class.forName` or
  `import com.systema.modernized.runtime.*` appears in
  generated code.
- **Verification**: CI test.

### T-2G-04 — No `libcobj.jar` in Track-B `pom.xml`
- **Phase**: 2G
- **Priority**: P0
- **Depends on**: T-2G-02
- **Files**: CI check
- **Acceptance**: A CI check fails if `libcobj`,
  `jp.osscons`, or `OpenSourceCOBOL4J` appears in
  generated `pom.xml`.
- **Verification**: CI test.

### T-2G-05 — Generated code compiles with `javac`
- **Phase**: 2G
- **Priority**: P0
- **Depends on**: T-2G-02
- **Files**: `tests/codegen/compile_smoke.py`
- **Acceptance**: For each corpus workload, generated
  Java compiles in a clean `javac` invocation.
- **Verification**: Test green.

---

## Phase 2H — Semantic Adapters (SQL, File, CICS, JCL, Encoding)

### T-2H-01 — SQL AST
- **Phase**: 2H
- **Priority**: P0
- **Depends on**: T-2C-01
- **Files**: `modernize_v2/sql/sql_ast.py`
- **Acceptance**: All SQL constructs in §13.2 are
  represented. The AST is dialect-agnostic.
- **Verification**: Unit tests.

### T-2H-02 — SQL analyzer
- **Phase**: 2H
- **Priority**: P0
- **Depends on**: T-2H-01
- **Files**: `modernize_v2/sql/sql_analyzer.py`
- **Acceptance**: Host variable binding, type check, and
  indicator binding work.
- **Verification**: Unit tests.

### T-2H-03 — SQL runtime (PostgreSQL)
- **Phase**: 2H
- **Priority**: P0
- **Depends on**: T-2H-01, T-2H-02
- **Files**: `modernize_v2/sql/sql_runtime.py`
- **Acceptance**: SQL execution is parameterized.
  SQLCODE/SQLSTATE are first-class return values.
- **Verification**: Integration test against PostgreSQL.

### T-2H-04 — File semantics
- **Phase**: 2H
- **Priority**: P0
- **Depends on**: T-2A-04
- **Files**: `modernize_v2/fileio/file_semantics.py`
- **Acceptance**: SEQUENTIAL, LINE SEQUENTIAL, INDEXED,
  RELATIVE semantics are represented. The class name is
  `IndexedFile`, not `VsamFile`, until V2 has a real VSAM
  adapter.
- **Verification**: Unit tests.

### T-2H-05 — File adapters
- **Phase**: 2H
- **Priority**: P0
- **Depends on**: T-2H-04
- **Files**:
  `modernize_v2/fileio/adapters/sequential.py`,
  `indexed.py`, `relative.py`
- **Acceptance**: Each adapter exposes typed Java methods
  for OPEN/CLOSE/READ/WRITE/REWRITE/DELETE/START.
- **Verification**: Unit tests.

### T-2H-06 — `RecordCodec`
- **Phase**: 2H
- **Priority**: P0
- **Depends on**: T-2B-07, T-2H-05
- **Files**: `modernize_v2/fileio/record_codec.py`
- **Acceptance**: A typed encoder/decoder for records
  using the layout from §9.
- **Verification**: Round-trip tests.

### T-2H-07 — `InMemoryCicsRuntime`
- **Phase**: 2H
- **Priority**: P0
- **Depends on**: T-2A-04
- **Files**: `modernize_v2/cics/cics_runtime.py`
- **Acceptance**: An in-memory CICS runtime supporting
  LINK/XCTL/RETURN/COMMAREA. Class name is
  `InMemoryCicsRuntime`. CICS state is part of the
  observation.
- **Verification**: Unit tests.

### T-2H-08 — CICS AST
- **Phase**: 2H
- **Priority**: P1
- **Depends on**: T-2H-07
- **Files**: `modernize_v2/cics/cics_ast.py`
- **Acceptance**: CICS statements are typed.
- **Verification**: Unit tests.

### T-2H-09 — JCL AST
- **Phase**: 2H
- **Priority**: P0
- **Depends on**: T-2A-04
- **Files**: `modernize_v2/jcl/jcl_ast.py`
- **Acceptance**: JOB/EXEC/DD/COND/IF/THEN/ELSE
  represented.
- **Verification**: Unit tests.

### T-2H-10 — `JclToSpringBatch`
- **Phase**: 2H
- **Priority**: P0
- **Depends on**: T-2H-09
- **Files**: `modernize_v2/jcl/jcl_to_spring_batch.py`
- **Acceptance**: A multi-step JCL becomes a real Spring
  Batch `Job` with multiple `Step`s. COND becomes a
  `JobExecutionDecider`.
- **Verification**: Generated app boots.

### T-2H-11 — Encoding model
- **Phase**: 2H
- **Priority**: P0
- **Depends on: T-2A-05
- **Files**: `modernize_v2/encoding/encoding.py`,
  `modernize_v2/encoding/transcoders/`
- **Acceptance**: EBCDIC ↔ ASCII `Transcoder` exists.
  Encoding is part of the workload contract.
- **Verification**: Round-trip tests on a representative
  EBCDIC dataset.

---

## Phase 2I — Spring Boot / Batch

### T-2I-01 — Spring Boot codegen
- **Phase**: 2I
- **Priority**: P0
- **Depends on**: T-2G-02
- **Files**: `modernize_v2/codegen/spring_boot.py`
- **Acceptance**: Generated project is a normal Spring
  Boot 3 application. `pom.xml` declares Java 21.
- **Verification**: Generated app boots and exposes the
  service beans.

### T-2I-02 — Spring Batch codegen
- **Phase**: 2I
- **Priority**: P0
- **Depends on**: T-2H-10, T-2I-01
- **Files**: `modernize_v2/codegen/spring_batch.py`
- **Acceptance**: Generated `Job` has multiple `Step`s
  for multi-step JCL. Each step is a real
  `Tasklet`/`ItemReader`/`ItemProcessor`/`ItemWriter`.
  No `Main.main()` wrapped in a single Tasklet.
- **Verification**: Generated app runs a multi-step job
  end-to-end.

### T-2I-03 — Per-run Spring context
- **Phase**: 2I
- **Priority**: P0
- **Depends on**: T-2I-01
- **Files**: `modernize_v2/pipeline/run_context.py`
- **Acceptance**: No static field holds a Spring bean.
  Each run has its own `ApplicationContext`.
- **Verification**: Unit tests + CI grep check.

---

## Phase 2J — Differential Verification V2

### T-2J-01 — Observation capture
- **Phase**: 2J
- **Priority**: P0
- **Depends on**: T-2A-05, T-2H-03, T-2H-05, T-2H-07
- **Files**:
  `modernize_v2/verification/observe_cobol.py`,
  `modernize_v2/verification/observe_java.py`
- **Acceptance**: All dimensions in §24.1 are captured for
  both COBOL and Java. Missing required dimensions
  produce `UNVERIFIED`.
- **Verification**: Unit tests + integration tests.

### T-2J-02 — Pure comparator
- **Phase**: 2J
- **Priority**: P0
- **Depends on**: T-2J-01, T-2A-05, T-2A-06
- **Files**: `modernize_v2/verification/comparator.py`
- **Acceptance**: Comparator is a pure function. It does
  not read the filesystem, environment, or wall clock.
- **Verification**: Unit tests.

### T-2J-03 — File comparison mode is contract-declared
- **Phase**: 2J
- **Priority**: P0
- **Depends on**: T-2A-06, T-2J-02
- **Files**: `modernize_v2/verification/contract.py`,
  `modernize_v2/verification/comparator.py`
- **Acceptance**: A test fails if the comparator uses a
  mode not declared in the contract.
- **Verification**: Unit tests.

### T-2J-04 — Mutation campaign
- **Phase**: 2J
- **Priority**: P0
- **Depends on**: T-2J-02
- **Files**: `tests/mutation/`
- **Acceptance**: For every entry in the Phase 1G
  false-PASS attack matrix, the V2 comparator reports
  `FAILED` for the corresponding mutation.
- **Verification**: Mutation campaign green.

### T-2J-05 — Comparator handles `UNVERIFIED` correctly
- **Phase**: 2J
- **Priority**: P0
- **Depends on**: T-2J-02
- **Files**: `modernize_v2/verification/comparator.py`
- **Acceptance**: A test asserts that a missing required
  observation produces `UNVERIFIED`, never `PASS`.
- **Verification**: Unit test.

---

## Phase 2K — Provenance, Security, CI Hardening

### T-2K-01 — Hash chain
- **Phase**: 2K
- **Priority**: P0
- **Depends on: T-2A-05
- **Files**: `modernize_v2/evidence/evidence_store.py`
- **Acceptance**: `evidence.jsonl` is append-only with
  HMAC chain. `verify_evidence` re-derives the verdict.
- **Verification**: Test green on a real run.

### T-2K-02 — Subprocess policy
- **Phase**: 2K
- **Priority**: P0
- **Depends on: —
- **Files**: `modernize_v2/security/subprocess_policy.py`
- **Acceptance**: All subprocess invocations use argument
  arrays. A test asserts no `shell=True` in the codebase.
- **Verification**: CI test.

### T-2K-03 — Path safety
- **Phase**: 2K
- **Priority**: P0
- **Depends on: T-2K-01
- **Files**: `modernize_v2/security/path_safety.py`
- **Acceptance**: All file paths are bounded to the
  per-run workspace. Path traversal raises.
- **Verification**: Unit tests.

### T-2K-04 — SQL seed policy
- **Phase**: 2K
- **Priority**: P0
- **Depends on: T-2H-03
- **Files**: `modernize_v2/sql/seed.py`
- **Acceptance**: Only `INSERT INTO <declared_table>` and
  `MERGE INTO <declared_table>` are accepted. Other
  statements produce a diagnostic.
- **Verification**: Unit tests.

### T-2K-05 — Hardening of CI gates
- **Phase**: 2K
- **Priority**: P0
- **Depends on: T-2K-01..04
- **Files**: `.github/workflows/*`
- **Acceptance**: Fast CI gates on V2 differential tests;
  nightly CI gates on mutation campaign. UNVERIFIED is
  never `PASS`. Docker availability is required for the
  differential lane.
- **Verification**: CI inspection.

### T-2K-06 — Remove `PARITY_ALLOW_SKIP` and equivalent
- **Phase**: 2K
- **Priority**: P0
- **Depends on: T-2K-05
- **Files**: removal of env-var bypasses
- **Acceptance**: A CI grep check fails if
  `PARITY_ALLOW_SKIP` or any equivalent skip flag is
  present in production code.
- **Verification**: CI test.

---

## Phase 2L — Realistic Enterprise Workloads

### T-2L-01 — Unseen-repository corpus
- **Phase**: 2L
- **Priority**: P0
- **Depends on: T-2K-05
- **Files**: `tests/unseen_repos/`
- **Acceptance**: At least three unseen repositories pass
  the V2 pipeline with explicit evidence.
- **Verification**: Three-unseen-repo gate green.

### T-2L-02 — Honest classification report
- **Phase**: 2L
- **Priority**: P1
- **Depends on: T-2L-01
- **Files**: `modernize_v2/reporting/`
- **Acceptance**: Each workload's report uses
  `VERIFIED / EMULATED / PARTIAL / UNSUPPORTED /
  NOT_VERIFIED / ENVIRONMENT_BLOCKED` per the contract.
- **Verification**: Visual inspection of reports.

### T-2L-03 — Update SUPPORTED_FEATURES, KNOWN_LIMITATIONS,
  and FINAL_FORENSIC_AUDIT for V2
- **Phase**: 2L
- **Priority**: P1
- **Depends on: T-2L-02
- **Files**: `docs/SUPPORTED_FEATURES.md`,
  `docs/KNOWN_LIMITATIONS.md`,
  `docs/audit/FINAL_FORENSIC_AUDIT.md`
- **Acceptance**: Documents reflect V2 architecture and
  classifications.
- **Verification**: Doc review.

---

## First 10 Tickets to Start

The first 10 tickets are the critical path for Phase 2A and
the bootstrap of Phase 2B. Starting them in parallel:

1. **T-2A-08** — Bootstrap `modernize_v2` package
2. **T-2A-01** — Define IR ID scheme
3. **T-2A-02** — Define `IRKind` enum
4. **T-2A-03** — Define `Diagnostic` model
5. **T-2A-04** — Define `Capability` enum and gate
6. **T-2A-05** — Define `Observation` and
   `ComparisonResult` types
7. **T-2A-06** — Define `VerificationContract` type
8. **T-2B-01** — Source map and workspace model
9. **T-2B-02** — Lexer for COBOL (fixed + free format)
10. **T-2F-01** — Stable ordering (because it informs IR
    design choices in T-2B-09)

The remaining tickets are sequenced by their `Depends on`
fields.

---

## Dependencies / Blockers

- The IR rewrite (T-2B-*) cannot start until T-2A-08, T-2A-01
  and T-2A-02 are stable.
- The codegen rewrite (T-2G-*) cannot start until T-2D-04
  (CFG consumer) is in place.
- The verification rewrite (T-2J-*) cannot start until at
  least one semantic adapter (T-2H-03, T-2H-05) is in
  place to produce observations.
- The promotion decision (D-20) blocks `legacy_modernize/`
  cleanup.

---

## Unresolved Decisions Requiring Human Approval

- D-04 / D-08: Track-A status
- D-20: Promotion of V2 to default
- D-23: Java / Spring / Maven version policy
- D-25: Track-A in CI

(See `docs/PHASE_2_DECISION_REGISTER.md` for the full list.)
