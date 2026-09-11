# PHASE 2 — DECISION REGISTER

Status: **OPEN — AWAITING APPROVAL**

Companion docs:
- `docs/PHASE_2_ARCHITECTURE_V2.md`
- `docs/PHASE_2_WORK_BREAKDOWN.md`

This register records every significant architectural decision
proposed in Phase 2, the alternatives considered, the chosen
approach, the rationale, the consequences, and the unresolved
questions.

Each decision has a unique `D-ID`. Status fields are
`PROPOSED / APPROVED / REJECTED / DEFERRED / SUPERSEDED`.

Approval is **explicit and human** — agents do not approve their
own architectural decisions.

---

## D-01 — Canonical typed IR replaces property-bag IR

- **Decision**: Replace `modernize/semantic_ir.py` (property
  bags) with `modernize_v2/ir/canonical.py` (typed AST, stable
  IDs, source spans, attribute keys, provenance hashes).
- **Alternatives**:
  - (a) Incrementally type the existing property bag.
  - (b) Adopt an existing IR (e.g., ProLeap's IR) as the canonical
    one.
  - (c) Build a hybrid IR with optional type information.
- **Chosen**: (b)-style, but a **new** canonical IR we own.
- **Reason**:
  - (a) does not produce a clean foundation; the property bag
    is the structural defect, not a missing annotation.
  - (b)-adopt-existing creates a licensing and coupling risk;
    ProLeap is treated as a parser-time input only.
  - (c) reintroduces the same dual-track confusion Phase 1
    identified.
  - Owning the IR is the only way to enforce the
    fail-closed capability gate.
- **Consequences**:
  - Phase 2B is the largest single body of work in Phase 2.
  - V1 corpus becomes a regression fixture.
- **Unresolved**:
  - Do we want to publish the IR schema as a public contract
    (e.g., a JSON schema) for downstream tools? **DEFERRED**.

## D-02 — Typed expression AST replaces string expressions

- **Decision**: Build `modernize_v2/ir/expr.py` with a typed
  expression model.
- **Alternatives**:
  - (a) Continue with string expressions, add a separate type
    system on the side.
  - (b) Use a third-party expression library.
- **Chosen**: (a)-rejected, (b)-evaluated and rejected for
  the same reason as D-01: the expression model is the
  foundation for type checking, NULL handling, and SQL host
  variable flow. We own it.
- **Consequences**:
  - Phase 2C is large.
  - Many existing parser tests need rewriting; this is
    expected.
- **Unresolved**:
  - How much of the GnuCOBOL intrinsic function set is in scope
    for V2? **DEFERRED** to capability registry D-10.

## D-03 — Generator consumes CFG, not IR order

- **Decision**: Codegen walks a real CFG (`BasicBlock`,
  `Terminator`). Walking the IR in source order is no longer
  permitted.
- **Alternatives**:
  - (a) Keep IR-order codegen and add a CFG for analysis only.
  - (b) Build a complete SSA IR.
- **Chosen**: (a)-rejected; (b)-rejected for V2 (overkill).
- **Reason**: The paragraph-dispatch interpreter in V1 is the
  single largest source of false-PASS paths and is the reason
  "unsupported → comment" is a real risk.
- **Consequences**:
  - Phase 2D and 2G are tightly coupled.
  - Codegen unit tests must assert CFG-consumption.
- **Unresolved**:
  - How to handle GOTO chains that span paragraphs in a single
    method (V1 emits this as method calls; V2 may inline or
    not). **DEFERRED** to a Phase 2G design sub-decision.

## D-04 — Track-B does not depend on legacy emulator runtime

- **Decision**: `libcobj.jar`, `jp.osscons.*`, and
  OpenSourceCOBOL4J are not dependencies of generated
  Track-B applications. The legacy emulator helpers
  (`CobolNumeric`, `CobolString`, `MockSqlService`,
  `CicsTransactionContext`, `JclExecutionContext`,
  `SpringContextHelper`) are **not** packaged in the Track-B
  output.
- **Alternatives**:
  - (a) Keep the legacy helpers as a fallback.
  - (b) Keep them as a Track-A-only path.
- **Chosen**: V2 Track-B is native Java. Track-A is a separate
  output track (legacy emulator) and is **not** the default.
  Track-A is retained under `legacy_modernize/` for backward
  compatibility only.
- **Reason**: This is a direct consequence of the Phase 1
  finding that runtime independence is `NO`. The only way to
  make Track-B native is to remove the runtime.
- **Consequences**:
  - Track-A workloads re-classify as `EMULATED` in V2 reports.
  - Custom helpers (`CobolNumeric`, `RecordCodec`) are replaced
    by Java-only domain helpers in `modernize_v2/runtime/`.
- **Unresolved**:
  - Whether Track-A is supported at all in V2.0, or only V1.x
    (deprecation). **DEFERRED** to D-08.

## D-05 — `Class.forName` is removed from generated code

- **Decision**: `Class.forName` is not used in generated
  Track-B code. Program dispatch uses a Spring-managed
  `Map<String, Supplier<Program>>`.
- **Alternatives**:
  - (a) Keep `Class.forName` with a sanitized prefix.
  - (b) Replace with explicit polymorphism.
- **Chosen**: Spring-managed registry.
- **Reason**: `Class.forName` is a security smell and a
  false-PASS vector (the program name is COBOL-controlled and
  could be made to look like a Java class).
- **Consequences**:
  - `CicsProgramRegistry` is rewritten in V2.
  - All reflective dispatch is replaced with explicit
    polymorphism.
- **Unresolved**: None.

## D-06 — Comparator compares full observations, not last 500 chars

- **Decision**: stdout is compared in full. Missing expected
  observations produce `UNVERIFIED`.
- **Alternatives**:
  - (a) Keep 500-char limit for "long output" workloads.
  - (b) Truncate with a configurable window.
- **Chosen**: Full comparison. The comparator normalizes
  whitespace and line endings; it does not truncate.
- **Reason**: Truncation is the structural reason `1E-03`
  exists.
- **Consequences**:
  - Storage requirements for observations increase. Mitigated
    by content-addressed storage and compression.
- **Unresolved**:
  - Whether the comparator accepts a `TAIL_ONLY` mode for
    "unbounded log streams" workloads. **DEFERRED** — if added,
    it must be a contract-declared mode, never an implicit
    default.

## D-07 — Baseline is bound to content hash

- **Decision**: A baseline is reusable only if its
  `baseline_unit_hash` matches the current `unit_hash`. A
  baseline whose compile/exec failed is `INVALID` and
  cannot be reused.
- **Alternatives**:
  - (a) Keep the `os.path.exists(stdout.txt)` freshness check.
  - (b) Add a manual approval for stale baselines.
- **Chosen**: Hash binding.
- **Reason**: Stale baseline is the largest single
  false-PASS vector.
- **Consequences**:
  - The first run on a new code revision requires a new
    baseline. This is the correct behavior.
  - CI must run baselines on a clean checkout, not on stale
    artifacts.
- **Unresolved**: None.

## D-08 — Track-A and Track-B as separate output tracks

- **Decision**: V2 produces two output tracks:
  - Track-B (default): native Java / Spring Boot / Spring
    Batch. No legacy runtime dependency.
  - Track-A (legacy compatibility): the legacy emulator
    path, retained for backward compatibility.
- **Alternatives**:
  - (a) Keep only Track-B.
  - (b) Keep only Track-A.
  - (c) Drop both; require all migrations to start fresh.
- **Chosen**: Both, with Track-B default.
- **Reason**: A clean break would invalidate the existing
  corpus. The existing corpus is the V2 regression fixture.
- **Consequences**:
  - Track-A is a `legacy_modernize/` package in V2.
  - Track-A workloads are reported as `EMULATED`.
- **Unresolved**:
  - When (if ever) to deprecate Track-A. **DEFERRED** until
    Track-B is `VERIFIED` for the existing corpus.

## D-09 — `data/*.sql` is no longer auto-executed

- **Decision**: `data/*.sql` files are not auto-executed by
  the platform. Seed data is declared in the workload
  contract; the executor is allow-listed to `INSERT`/`MERGE`
  against declared tables.
- **Alternatives**:
  - (a) Continue auto-execution with sanitization.
  - (b) Move auto-execution to a feature flag.
- **Chosen**: Allow-listed contract-driven seed executor.
- **Reason**: `data/*.sql` is a code-execution sink. The
  security boundary of the platform is a "real" repository;
  arbitrary SQL is a supply-chain risk.
- **Consequences**:
  - Existing test workloads that rely on auto-execution need
    explicit seed declarations.
  - The seed executor is a new module
    (`modernize_v2/sql/seed.py`).
- **Unresolved**: None.

## D-10 — Capability registry and unsupported-feature gate

- **Decision**: A central capability registry classifies every
  feature. `UNSUPPORTED` features are hard blockers; they
  raise `Diagnostic { severity: ERROR, kind:
  UNSUPPORTED_FEATURE }`.
- **Alternatives**:
  - (a) Continue with comments for unsupported features.
  - (b) Compile with a warning, not an error.
- **Chosen**: Hard error.
- **Reason**: Comments are the Phase 1 false-PASS vector.
- **Consequences**:
  - The migration verdict for a workload with an unsupported
    feature cannot be `PASS`. It is `PARTIAL` or
    `ENVIRONMENT_BLOCKED`.
  - The capability registry is the single source of truth
    for `docs/SUPPORTED_FEATURES.md`.
- **Unresolved**:
  - The exact list of features in V2.0
    (per the §15 / §14 / §17 capability matrices). **DEFERRED**
    to a follow-up ADR.

## D-11 — `EMULATED` workloads are explicitly labeled, not `VERIFIED`

- **Decision**: Workloads that depend on simulated/emulated
  facilities (in-memory CICS, JDBC-as-VSAM, etc.) are
  reported as `EMULATED` and cannot be classified `VERIFIED`.
- **Alternatives**:
  - (a) Allow `EMULATED` to count as `VERIFIED` for "internal"
    workloads.
  - (b) Hide the distinction.
- **Chosen**: Hard distinction.
- **Reason**: Honesty about the platform's actual
  capabilities is a prerequisite for production readiness.
  The vocabulary in `AGENTS.md §17` is the contract.
- **Consequences**:
  - Migration reports must surface the `EMULATED` vs
    `VERIFIED` distinction.
  - The UI must show it.
- **Unresolved**:
  - Whether `EMULATED` workloads can be allowed in CI
    fast lane. **DEFERRED** — proposed default is no, only
    nightly.

## D-12 — No `shell=True` in subprocess invocations

- **Decision**: All subprocess invocations use argument
  arrays. No `shell=True`. All invocations have a hard
  timeout.
- **Alternatives**:
  - (a) Continue with `shell=True` and add sanitization.
  - (b) Use a shell wrapper with controlled variables.
- **Chosen**: Argument arrays.
- **Reason**: Eliminates a class of command-injection
  vulnerabilities.
- **Consequences**:
  - Existing callsites that use `shell=True` must be
    rewritten.
- **Unresolved**: None.

## D-13 — Per-run workspace isolation

- **Decision**: Each run has a `run_id` and a per-run
  workspace. No static state is shared between runs.
- **Alternatives**:
  - (a) Continue with `MockSqlService` static state.
  - (b) Use thread-local state.
- **Chosen**: Per-run DI scope.
- **Reason**: `MockSqlService` static state is a known
  concurrency defect.
- **Consequences**:
  - All static Spring beans are reviewed; per-run beans are
    introduced where needed.
- **Unresolved**: None.

## D-14 — Java source is emitted from a typed Java AST

- **Decision**: Java source is generated by serializing a
  typed Java AST (`JExpr` / `JStmt` / `JDecl`). No
  string-concatenation emission of executable Java code.
- **Alternatives**:
  - (a) Continue with string templates.
  - (b) Adopt a Java code generation library.
- **Chosen**: Own typed AST.
- **Reason**: String concatenation is the structural reason
  the `DISPLAY` literal injection is a real risk.
- **Consequences**:
  - Codegen unit tests assert on the AST, not on the
    emitted text, where possible.
- **Unresolved**: None.

## D-15 — Evidence is content-hashed and append-only

- **Decision**: `evidence.jsonl` records every artifact with
  `sha256` hashes, with a per-line HMAC forming a hash
  chain. A `verify_evidence` command re-derives the verdict
  from the evidence file.
- **Alternatives**:
  - (a) JSON file with a single signature.
  - (b) External blockchain.
- **Chosen**: Append-only JSONL + HMAC chain.
- **Reason**: External dependencies are operational risk;
  HMAC chain is sufficient and reproducible.
- **Consequences**:
  - A new `modernize_v2/evidence/` module.
  - The signer is a process-internal key, regenerated per
    run, with the key hash itself part of the evidence.
- **Unresolved**:
  - Long-term key custody (HSM? Vault?).
    **DEFERRED** — V2 uses a per-run key for simplicity.

## D-16 — JCL lowers to real Spring Batch

- **Decision**: A JCL `JOB` becomes a Spring Batch `Job`;
  each `EXEC PGM=...` step becomes a `Step`. Multi-step
  JCL produces a real multi-step `Job`.
- **Alternatives**:
  - (a) Single-tasklet wrapper, like V1.
  - (b) Direct main-method invocation.
- **Chosen**: Real `Job`/`Step` mapping.
- **Reason**: Single-tasklet wrapper is the structural
  reason "JCL is converted to Spring Batch" is misleading.
- **Consequences**:
  - `JclToSpringBatch` is a new module.
  - Restartable jobs are first-class.
- **Unresolved**:
  - GDG and PROC handling. **DEFERRED** to capability
    matrix updates.

## D-17 — Comparator mode is contract-declared, never implicit

- **Decision**: File comparison mode (`PHYSICAL` /
  `KEY_SORTED` / `SET`) is a contract field. The comparator
  does not pick a mode based on heuristics.
- **Alternatives**:
  - (a) Continue with `LOGICAL_MATCH` heuristic.
  - (b) Always physical.
- **Chosen**: Contract-declared, default `PHYSICAL`.
- **Reason**: Implicit mode selection is a false-PASS
  vector.
- **Consequences**:
  - Workload contracts must declare the mode.
  - The default `PHYSICAL` is stricter than V1.
- **Unresolved**:
  - Whether `SET` mode is allowed at all. **DEFERRED** — if
    allowed, it is a `NOT_VERIFIED` mode for output ordering
    and a `VERIFIED` mode for record set membership, but
    not a substitute for content equality.

## D-18 — Encoding is a first-class execution property

- **Decision**: `Encoding` is part of the workload contract.
  EBCDIC inputs are translated via a `Transcoder` injected
  by the file adapter. Encoding mismatches between baseline
  and Java are an environment error.
- **Alternatives**:
  - (a) Continue with ISO-8859-1 everywhere.
  - (b) Detect encoding heuristically.
- **Chosen**: Contract-declared.
- **Reason**: Encoding is the structural reason "EBCDIC
  support" is misleading in V1.
- **Consequences**:
  - New `modernize_v2/encoding/` module.
  - EBCDIC support is `SUPPORTED_UNVERIFIED` until proven
    against a real EBCDIC dataset.
- **Unresolved**:
  - Which codepages are in scope for V2.0? **DEFERRED** to
    capability matrix update.

## D-19 — Repository structure: `modernize_v2/` first, then promote

- **Decision**: V2 is built in `modernize_v2/`. Promotion
  to `modernize/` (and movement of V1 to `legacy_modernize/`)
  is a separate, explicitly approved decision (D-20).
- **Alternatives**:
  - (a) Replace V1 in place.
  - (b) Keep V1 as the default for the duration of V2.
- **Chosen**: (b) for development, (a) for promotion.
- **Reason**: A clean break risks destroying existing
  evidence.
- **Consequences**:
  - During V2 development, both packages exist.
  - The default pipeline path is decided at promotion time
    (D-20).
- **Unresolved**: See D-20.

## D-20 — Promotion of V2 to default and deprecation of V1

- **Decision (deferred)**: When V2 reaches equivalence
  with V1 on the existing corpus, V2 is promoted to
  `modernize/` and V1 is moved to `legacy_modernize/`.
- **Alternatives**:
  - (a) Hard cut-over.
  - (b) Sunset window.
- **Chosen (proposed)**: Hard cut-over at the next minor
  release after V2 reaches the acceptance criteria of §30.
- **Reason**: A long sunset window encourages parallelism
  and feature drift.
- **Consequences**:
  - All V1 callers must migrate to V2 interfaces.
- **Unresolved**:
  - Whether `legacy_modernize/` is removed at all, or kept
    for read-only historical access. **DEFERRED**.

## D-21 — Comparator is a pure function

- **Decision**: The comparator is a pure function:
  `compare(observed_cobol, observed_java, contract)`.
  It does not read the filesystem beyond the two
  observations, the environment, or the wall clock.
- **Alternatives**:
  - (a) Continue with file I/O in the comparator.
- **Chosen**: Pure function.
- **Reason**: Pure comparators are unit-testable and
  reproducible.
- **Consequences**:
  - Comparator tests are stable.
- **Unresolved**: None.

## D-22 — Reuse of V1 evidence is forbidden

- **Decision**: V1's existing evidence files are
  quarantined. They are not used as V2 evidence. The
  corpus itself (COBOL + expected outputs) is reused as
  a regression fixture, but the verdict is regenerated
  by V2.
- **Reason**: V1 evidence is not trustable.
- **Consequences**:
  - V1 evidence is moved to `legacy/evidence/`.
  - V2 evidence is built fresh.
- **Unresolved**: None.

## D-23 — Runtime version policy

- **Decision (deferred)**: Java 21, Spring Boot 3.x,
  Spring Batch 5.x. Maven plugin versions are pinned.
- **Alternatives**:
  - (a) Java 17 / Spring Boot 3.
  - (b) Java 25 / Spring Boot 4 (if available).
- **Chosen (proposed)**: Java 21 / Spring Boot 3.x.
- **Reason**: Java 21 is the current LTS; record patterns
  are valuable for the value class layer.
- **Consequences**:
  - Generated `pom.xml` declares Java 21.
  - CI runs on Java 21.
- **Unresolved**:
  - Long-term support policy. **DEFERRED**.

## D-24 — Comparator is parameterized by version, not by hard-coded heuristics

- **Decision**: The comparator's verifier_version is
  recorded in the evidence. Comparing observations from
  different verifier versions is permitted only with an
  explicit contract flag.
- **Alternatives**:
  - (a) Always compare.
  - (b) Refuse to compare across versions.
- **Chosen**: Compare, with the version recorded.
- **Reason**: Long-term reproducibility.
- **Consequences**:
  - Evidence is self-describing.
- **Unresolved**: None.

## D-25 — Track-A workloads are not part of the "PASS" pool

- **Decision**: A workload that runs on Track-A (the
  legacy emulator) is not eligible for a `VERIFIED` verdict.
- **Alternatives**:
  - (a) Allow Track-A to count as `VERIFIED`.
- **Chosen**: Refused. Track-A is `EMULATED`.
- **Reason**: Track-A is exactly the "interpreter
  wrapped in Java" pattern that Phase 1 identified.
- **Consequences**:
  - The Track-B corpus is the only source of `VERIFIED`
    workloads.
- **Unresolved**:
  - Whether to keep a Track-A CI lane at all. **DEFERRED**.

---

## Open Questions (require human input)

- Q1. Is the `EMULATED` / `VERIFIED` distinction acceptable
  in the migration report UI?
- Q2. Is the per-run workspace acceptable as a deployment
  model (vs. a single shared workspace)?
- Q3. Are the unseen-repository requirements of Phase 2L
  acceptable as a release gate?
- Q4. Is Java 21 + Spring Boot 3 the target, or do we need
  to support Java 17 for any reason?
- Q5. Is the legacy `libcobj.jar` path kept (Track-A) for
  any production customer, or is it safe to deprecate?
- Q6. What is the policy for unsupported features in
  production migrations: fail the migration, or deliver
  a `PARTIAL` report and let the customer decide?
- Q7. What is the policy for V1 evidence retention (raw
  bytes, or summary only)?
- Q8. What is the policy for ProLeap going forward:
  parser-time input, or deprecate?

These are not blockers for Phase 2A–2K; they are inputs to
Phase 2L and to the release plan.

---

## Approval

Each decision above requires an explicit human approval.
Agents do not approve their own architectural decisions.

Approval template:

```
D-XX: APPROVED / REJECTED / DEFERRED
By: <name>
Date: <date>
Notes: <optional rationale>
```
