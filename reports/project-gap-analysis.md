# SystemaOps — Documentation-vs-Code Contradiction Matrix & Claim Register

Branch: `environment-discovery` @ `d2311c5` — hostile re-audit, 2026-09-11/12. All verdicts independently re-verified against code/tests/live runs this audit; prior reports treated as untrusted input.

## 1. FABRICATED claims (functionality/paths/results that DO NOT EXIST)

| # | Claim (source) | Reality (evidence) |
|---|---|---|
| F1 | `README.md:101,104` — runnable commands `--repo tests/repos/GOLDENPAY` and `python -m src.cjp.cli run` | `tests/repos/GOLDENPAY` does not exist; cjp CLI crashes 3 ways live-reproduced: `ModuleNotFoundError` as script, `TypeError: config_path` (cli.py:49 vs Pipeline(repo,out,cfg) cobol_migrate.py:2955), missing `run_until` (cli.py:56-62; only `run` exists :3096) |
| F2 | `MENTOR_ACCEPTANCE_SCOPE.md:40-50` — 11 workloads "Gate 1 PASS 100% byte match… MVP_CERTIFIED" incl. **BANKTXN01, UNSEEN01-03** | BANKTXN01/UNSEEN02/UNSEEN03: **zero occurrences repo-wide**; tracked `reports/*/certification_scorecard.json` (same era) all `UNPROVEN 20/100`, CICSREST01/DB2SELECT01/JCLBATCH01 tier_4 FAIL; `MENTOR_DEMO_SUMMARY.md` itself shows 5/6 Java-runtime FAILs |
| F3 | `docs/audit/CAPABILITY_MATRIX.md` — "Reference Runtime: GnuCOBOL/z390… Reference Proven: YES" (~35 rows), "JCL… Hercules/z390… PROVEN" | z390 never installed/executed (all tests use fake homes, assert UNAVAILABLE); Hercules `execute()` returns hardcoded standby SKIPPED (hercules/runner.py:88-94) |
| F4 | `EVIDENCE_MAP.md` / `FALSE_PASS_RISKS.md` — cite 9 evidence files: `test_mutation_verification.py`, `test_transpiler.py`, `test_native_generator.py`, `test_cics_rest.py`, `test_ksds.py`, `test_db2_pipeline.py`, `modernize/runtime/CobolRef.java`, `scratch/run_unseen_…py` | **None exist** (CobolRef lives at `modernize/java_helpers/CobolRef.java`; real mutation suite is `tests/differential/test_mutation.py`) |
| F5 | `tools/cobol_java_differential_verifier.py:648-649` + `reports/MENTOR_DEMO_SUMMARY.md` — "False Business-Equivalence PASS: 0", "Mutation Detection: 7/7 (100%)" | **Literal hardcoded strings** in `generate_mentor_demo_summary()` — never computed from any run |
| F6 | `COMPLETE_SYSTEM_DOCUMENTATION.md:90` + SBOM — "VSAM emulated via **SQLite** indexed tables"; "SQLite JDBC Driver 3.42.x Runtime" | No SQLite anywhere in the Java path; KSDS uses Spring JdbcTemplate over H2/PostgreSQL (KsdSDbService.java); pom has h2+postgresql only (maven-seed-pom.xml:41-63) |
| F7 | `pyproject.toml:15-21` — requires pydantic/fastapi/uvicorn/jinja2 | **Zero imports** of any of them; requirements.txt:1 "Standard Library only"; ui.py is stdlib http.server |
| F8 | `skills/system-architecture` + `native-java-generator` — cite `CobolDecimal.java`, "Flask", "line sequential mapped to VsamIndexedStore" | CobolDecimal.java does not exist; no Flask; line-sequential uses BufferedReader/Writer (native_generator.py:4340+) |
| F9 | `skills/copybook-expansion` — "expands COPY REPLACING" | Not supported anywhere: lexer COPY regex rejects REPLACING lines silently (lexer.py:74, audit); matrix :65 UNSUPPORTED |
| F10 | `FINAL_CERTIFICATION_REPORT.md:101` — "Remaining Bugs: None identified" vs `FINAL_FORENSIC_AUDIT.md:177` BUG-02 ACTIVE | Internally contradictory; this audit found 6 CRITICAL + ~14 HIGH live-verifiable bugs (bug register) |
| F11 | `modernize/capability_matrix.py` — cites ~40 fictional function names (`_parse_move_stmt`, `_emit_move`, `CobolParser._parse_call_stmt`…) as provenance | Real dispatchers: `_parse_statement_internal` (parser.py:997), `_translate_statement_inner` (native_generator.py:896) — none of the cited names exist |
| F12 | `enterprise_generator.py:370-373` — REST controller `@GetMapping("/api/status")` returns hardcoded `"Claim processing system is running"` | Hardcoded stub response presented as generated REST service |

## 2. EXAGGERATED / OVERSTATED

| # | Claim | Reality |
|---|---|---|
| E1 | `README.md:3` "production-grade" platform | Own gap-analysis rates LEVEL 3; tracked scorecards UNPROVEN; 6 CRITICAL bugs incl. silent wrong arithmetic (DIVIDE INTO) and dead DDL path (MockSqlService ordering) |
| E2 | "z390 / Hercules reference oracles integrated" (README:61) | Adapters exist; oracles NEVER executed; differential_verifier labels disagreement MATCH_WITH_REFERENCE_DISAGREEMENT but keeps MATCH verdict (differential_verifier.py:169-171) |
| E3 | "726 automated tests" (README:110) / "384 passed" (COMPLETE_SYSTEM_DOCUMENTATION) | Live collect = **1,483**; counts wildly outdated |
| E4 | CAPABILITY_MATRIX EBCDIC "ICU4J … PROVEN_FOR_TESTED_SCOPE" | ICU4J never imported (one string literal in capability_detector.py:79); real impl = Python codecs (charset.py), CP037 spot-values verified correct; **no program-level EBCDIC differential exists** |
| E5 | KNOWN_LIMITATIONS absent: harness false-PASS vectors | Substring-containment match (parity_harness.py:940-945), normalize_display space-collapse (:102-120), mock-SQL asymmetry (:563-579,608-709), seeded-baseline circularity — documented only in audit docs, not KNOWN_LIMITATIONS |
| E6 | `certify.py` "5-Tier … 100/FULL_PARITY" | Tier 5 never collected (evidence.py:73-142 tiers 1-4 only) → ceiling 80; UNPROVEN tier scores 5 → 4×PASS+UNPROVEN = 85 = "CERTIFIED_COMPATIBILITY" PASS verdict (certify.py:47-76) |

## 3. OUTDATED / CONTRADICTORY (docs disagree with each other or current code)

| # | Claim | Reality |
|---|---|---|
| O1 | PROJECT_OVERVIEW "Python 3.8+" vs README "3.10+" | pyproject requires-python >=3.10 |
| O2 | PROJECT_OVERVIEW:302 image `hurriedreformist/gnucobol:3.1-builder` vs current `gnucobol-ocesql:latest` (parity_harness.py:14, cobol_migrate.py:22) | Base image of gnucobol-ocesql IS hurriedreformist (Dockerfile.gnucobol-ocesql:21) but docs cite the old direct name |
| O3 | PROJECT_OVERVIEW §7.4 "divide-by-zero → Java silently skips, exit 0" vs KNOWN_LIMITATIONS §2.5 "terminates exit 1 / logs stderr" | Docs contradict each other on the same divergence; KNOWN_LIMITATIONS version matches implementation (CobolArithmetic checks + StopRunException paths) |
| O4 | FINAL_FORENSIC_AUDIT:161 "UI port **8788**" | ui.py:932 default 8787 |
| O5 | FINAL_FORENSIC_AUDIT:116,121 "Gate 1/2 passed 100% across all golden repos" | reports/MULTIFILE01 "Java Runtime FAIL", CICSREST01 "Business Equivalence FAIL" in the same commit |
| O6 | FINAL_FORENSIC_AUDIT BUG-02 EOF duplication "ACTIVE" | Now guarded by test_eof_10_no_duplicate_last_record (test_eof_sequential_reader_parity.py:227); its named regression file does not exist |
| O7 | KNOWN_LIMITATIONS missing 12 new limitations found this audit | DIVIDE INTO inversion, STRING ON OVERFLOW drop, CALL BY VALUE=REFERENCE, 88-multi-value, INDEXED BY/JUSTIFIED/BLANK drops, baseline_verified force (native_pipeline.py:208), MockSqlService DDL dead-path, COMP-3 indexed offsets, SORT BigDecimal CCE, cjp broken, tests/v2 local collection broken, DB2CURNULL01 e2e FAIL (live) |

## 4. VERIFIED claims (spot-checked TRUE)

- 13-stage pipeline (README) — STAGES list cobol_migrate.py:47-61, 13 entries. **VERIFIED**
- Security controls list (COMPLETE_SYSTEM_DOCUMENTATION:115-124) — MAX_UPLOAD 30MB ui.py:46, secure_resolve_path ui.py:77, UI_AUTH_CREDENTIALS ui.py:439, no shell=True in cobol_migrate (grep=0). **VERIFIED**
- FAIL_CLOSED architecture (docs) — engine ladders verified fail-closed in code (equivalence.py:402-412, verdict ladder cobol_migrate.py:6624+; run() RuntimeError on stage fail :3153-3155). **VERIFIED**
- "33/33 reference_runtime tests" — verified collecting/passing. **VERIFIED (as units, not as real z390 execution)**
- GnuCOBOL+OCESQL image purpose and paths (Dockerfile.gnucobol-ocesql) — matches cobol_migrate.py usage. **VERIFIED**
- reports/ tracked scorecards honestly say UNPROVEN — the raw generated evidence contradicts the certification NARRATIVES around it. **VERIFIED (evidence honest; narrative fabrications listed above)**

## 5. False-PASS vector register (verification infrastructure)

| # | Vector | Location | Severity |
|---|---|---|---|
| P1 | ISAM subset-containment: missing Java records PASS; order/dupes unchecked | native_pipeline.py:1427-1444 | CRITICAL |
| P2 | `baseline_verified=True` forced unconditionally → stale-baseline PASS | native_pipeline.py:208 | CRITICAL |
| P3 | Missing native stdout EXCUSED when baseline has any data file | native_pipeline.py:1402-1405 | HIGH |
| P4 | Parity-harness substring-containment file match (applies to ALL declared outputs) | parity_harness.py:940-945 | HIGH |
| P5 | normalize_display strips/collapses trailing spaces → unfalsifiable trailing-space parity | parity_harness.py:102-120 vs test_parity_trailing_spaces | HIGH |
| P6 | Mock-SQL/CICS/JCL-COND asymmetry: Java side runs no-op stubs vs real COBOL+PG | parity_harness.py:563-579,596-597,601-616 | HIGH |
| P7 | Seeded-baseline circularity (test authors its own oracle) | test_db2_modernization.py:90-110, test_db2_stage1.py, jcl/cics e2e (gates also stubbed to PASS) | HIGH |
| P8 | 12 vacuous negative-mutation asserts + nonexistent-attribute read | test_phase1_differential_proofs.py:193…:850, :130-131 | HIGH |
| P9 | e2e/differential inverted skip (off by default) + tolerant `status in (PASS,SKIP)` | e2e/differential/**: inverted skipif | HIGH |
| P10 | Binary outputs compared only via first ~1000 bytes hex | cobol_migrate.py:4227-4229,4258-4260 | MEDIUM |
| P11 | Non-interactive stdout compared as 1500/2000-char tails only | cobol_migrate.py:4035,4092,4126 | MEDIUM |
| P12 | Empty-vs-empty vacuous PASS modes (EXPECTED_NO_OUTPUT, empty stdouts, empty DB) | equivalence.py:121-123,281-282,400 | MEDIUM |
| P13 | File modes absent from contract → dimension NOT_APPLICABLE (invisible) | equivalence.py:44-53 + cobol_migrate.py:4329-4336 | MEDIUM |
| P14 | Negative gate comparator stricter than production gate (overstates sensitivity) | native_pipeline.py:1519-1530 vs 1355-1485 | MEDIUM |
| P15 | mutation "caught" if compile merely fails; mutates alphabetical java_files[0] | cobol_migrate.py:5234,5294-5295,5351-5353 | MEDIUM |
| P16 | H2-mode acceptance asserts accept every non-crash verdict | test_db2_acceptance.py:85-86+ | MEDIUM |
| P17 | z390/Hercules disagreement never affects match verdict | differential_verifier.py:169-171 | MEDIUM |
| P18 | `EXIT`-as-program-exit in CFG analysis; CALL/PERFORM self-loops | control_flow.py:315-325 | LOW |

## 6. Test-quality distribution (1,549 cases, live-collected)

| Strength | Count | Share | Definition |
|---|---|---|---|
| STRONG (oracle differential) | ~200 | 13% | run_parity / PG-probe / mutation-execution / e2e full-system |
| MED (executes Java, no COBOL oracle; or real engine-logic) | ~420 | 27% | cobol_runner suites, verdict-engine gates, real-server security tests |
| WEAK (source-text/IR asserts) | ~870 | 56% | literal Java substring pins, presence checks, greps |
| VACUOUS | 17 (+12 near) | ~2% | tautologies, fabricated attributes, hard-coded 6/6 |

CI coverage: Gates 1-5 execute ~2,100 of ~6,100 production LOC-relevant test cases; **never executed in CI: full nightly only on schedule**; e2e/differential OFF by default (verified live: 4 SKIP in 0.15s; 4 PASS in 71s when enabled). Nightly runs `python -m pytest` whole-suite with UI server; 2 auth tests fail there by env contract mismatch (ui.py:464-465 auth-optional on loopback; ci.yml sets no UI_AUTH_CREDENTIALS).

## 7. JDK / Maven / Spring matrix (VERIFIED vs NOT TESTED)

| Item | Value | Evidence |
|---|---|---|
| Build JDK (host) | **25.0.3 Temurin** | live `java -version` |
| Maven | 3.9.16 | live `mvn -version` |
| Spring Boot parent | 3.2.5 (native pom uses spring-jdbc/tx 6.1.3, h2 2.2.224, postgresql 42.7.1) | maven-seed-pom.xml:24,49-63 |
| CI JDK | 17 (setup-java) | ci.yml:43-47,141-145,214-218,422-427 |
| Docker runtime | eclipse-temurin:17-jdk-noble | Dockerfile:6 |
| Parity Java container | eclipse-temurin:17-jdk-noble | ci.yml:357; parity_harness |
| Generated-Java `--release 17` on JDK25 | **VERIFIED PASS** (compile+run, stdout identical) | live probe, jdk-probe-results.json |
| Generated-Java `--release 21` on JDK25 | **VERIFIED PASS** | live probe |
| Generated-Java `--release 25` on JDK25 | **VERIFIED PASS** | live probe |
| Native JDK 17 toolchain | **NOT TESTED — JDK not installed on host** | find_jdks() = {} |
| Native JDK 21 toolchain | **NOT TESTED — JDK not installed** | same |
| Spring Boot 3.2.5 app under JDK 25 | **NOT TESTED** (validate Gate-2 build not run this audit; SB 3.2.5 officially supports 17-23 → JDK25 runtime unverified for the Spring track) | inference flagged |
| java.* API risk in helpers | LOW — java.math/java.util/java.io only; no sun.*, no Nashorn, no SecurityManager, no removed APIs | helpers read in full |

**Minimum supported (verified): JDK 17 bytecode target via --release. Recommended: 17 (CI parity). Maximum tested: 25.0.3. The only true JDK risk is the Spring Boot 3.2.5 runtime on JDK 25 — untested, NOT claimed.**

## 8. Bug & vulnerability register (top entries; full detail in gap-analysis)

| # | Location | Sev | Bug | Consequence |
|---|---|---|---|---|
| B1 | native_generator.py:1070 (+parser.py:1108-1112 never stores INTO/BY) | **CRITICAL** | `DIVIDE a INTO b GIVING c` emits c=a/b | Silent wrong business arithmetic; live-reproduced emission |
| B2 | native_generator.py:1090-1095 | **CRITICAL** | REMAINDER dividend/divisor swapped for INTO | Wrong remainders |
| B3 | native_generator.py:6287-6288 + :6144 | **CRITICAL** | MockSqlService.initialize() in main() pre-sets jdbcTemplate → per-repo DDL+seed block dead in all standalone H2 runs | SQLCODE -1 / empty results silently; seed data never loaded |
| B4 | native_pipeline.py:208 | **CRITICAL** | baseline_verified=True unconditional | Comparisons legitimized against stale/prior-run baselines |
| B5 | native_generator.py:3425,3432-3433 | HIGH | COMP-3 length halving only for binary-sequential; INDEXED/RELATIVE get digit-count offsets | Wrong key bytes for indexed files w/ COMP-3 |
| B6 | native_generator.py:1314,1359-1360,1421-1423 | HIGH | SORT/MERGE decimal-key (BigDecimal) casts on CobolNumeric | CCE at runtime / compile errors |
| B7 | native_generator.py:456-459 | HIGH | Expression-translation failure → silent BigDecimal.ZERO | Whole expressions become 0, no diagnostic |
| B8 | native_generator.py:2298-2314 | HIGH | Dynamic CALL if/else chain, no else | Unregistered target = silent no-op CALL |
| B9 | native_generator.py:4344-4351 | HIGH | OPEN EXTEND/I-O on sequential → status "00", writes dropped | Silent data loss |
| B10 | jcl_generator.py:214-215 | HIGH | ClassNotFound on step PGM → rc 0 | Job "succeeds" though program never ran |
| B11 | native_generator.py:3366 | HIGH | CALL BY VALUE writeback (≠CONTENT ⇒ REFERENCE) | Callee mutations visible to caller — wrong semantics |
| B12 | parser.py:1146,1167 | HIGH | `self.error()` undefined; legal `ADD A GIVING B` triggers AttributeError | Whole-file parse crash escaping fail-closed recovery |
| B13 | parser.py:1526-1533 | HIGH | STRING ON/NOT ON OVERFLOW bodies leak into enclosing scope | Mis-scoped unconditional execution |
| B14 | parser.py:1042 | HIGH | COMPUTE expression collection breaks on ANY keyword-named operand / FUNCTION | Silently truncated arithmetic expressions |
| B15 | slicer.py:104-108 | HIGH | Fabricated `77 var PIC X(50).` fallbacks, no warning | Silent semantic change in sliced programs |
| B16 | Idcams.java:30-87 | HIGH | Unhandled IDCAMS commands → rc=0 | Jobs that should fail report success |
| B17 | Iebgener.java:38-44 / Sort.java | HIGH | Line-mode I/O strips/adds EOLs | Record boundary/byte-length corruption |
| B18 | parity_harness.py:367,337 | MED | PARITY_RUNTIME=local branch NameError; fixture.repo nonexistent attr | Local mode dead code |
| B19 | lexer.py:128-129 | MED | COPY recursion without cycle detection | Self-including copybook → RecursionError crash |
| B20 | check_fingerprint.py:4-5 vs parity_harness.py:14 | MED | Fingerprint pins different image than harness runs | Integrity check verifies the wrong oracle image |
| B21 | native_generator.py:3610,3776-3817 | MED | Per-row INSERT swallow; read_key catch-all → status 23 | Partial loads / DB outage misread as key-not-found |
| B22 | KsdSDbService.java:109-116 | MED | COUNT-then-INSERT TOCTOU, non-atomic | Duplicate-key race window |
| B23 | conftest.py:28-32 | LOW | stubbed_pipeline marks 12/13 stages (package missing) | Any gate test inspecting package stage sees false state |

Security register: no hardcoded secrets (compose demo creds only); zip-ingest path traversal guarded (ui.py secure_resolve_path verified by payload tests); docker exec hardened (memory/cpu/pids/cap-drop, scenario_runner.py:224-227); **Windows orphan-container gap** on watchdog timeout (scenario_runner.py:169-192, no taskkill /T); gnu_cobol.py:41-53 treats docker-CLI-presence as availability (weak); regex ReDoS exposure in normalization rules (no timeout); MockSqlService naive `;` split breaks literals containing semicolons.

## 9. Dead / stale / duplicate register (summary)

- **242 stale-candidate tracked files**: 198 `*.class`, 207 `generated/`+`_preprocessed/` fixture trees (A-G PAYMAIN family, ACCTPROG, SALESPROG, INVOICE01, MULTIFILE01, CALLCHAIN01), 9 `*.exe`, 6 `*.so`, `generated_debug/`, SORTMERGE01/output.txt (empty), 3 orphan `tests/fixtures/archives/*.zip`, ~646 tracked `artifacts/parity-failures/` snapshots (churned by every failing run), stale `audit/phase8/performance_results.json`.
- **Dead modules**: `tools/modernize_and_verify.py` (0 callers), `mock_cics_service.py` (0 callers, targets APIs the runtime lacks), `coverage.py`/`traceability.py` scaffolds unwired, `KsdSDbService.java` copied but never referenced by generated code, `VsamIndexedStore.java` excluded from all copies (1 test only), `CicsTransactionContext.java` disk variant never copied (3 divergent variants exist), `src/cjp/` (broken), enterprise_generator `to_java_var` returns None, `// Unsupported statement:` filter (native_generator.py:6265) matches nothing, 3rd SQLCODE regex unreachable (native_pipeline.py:1392), V2 `NUMERIC_LITERAL/STRING_LITERAL` enum values never emitted, V2 `_scan_operator_at/_eof_token/IdContext` dead, gate.py min() dead.
- **Orphan fixtures (no test references)**: A-PAYONLY…G-PAYMISSCP (7), DB2INVALID01, CALLCHAIN01 (only untracked scratch), tests/fixtures/archives/*, tests/fixtures/unpacked/cics-genapp-main + legacy-insurance (~676 tracked files).
- **Duplicated logic**: 4 COBOL keyword tables (lexer, parser, slicer, interactive_detector); MockSqlService 2 sources (disk + embedded overwrite); CicsTransactionContext 3 variants; Db2ErrorMapper 2 variants (native + enterprise); traceability 2 implementations (modernize/traceability.py vs cobol_migrate.extract_business_rules_traceability); COPY expansion 2 passes (pipeline + lexer, then lexer again = triple in tokenize).

## 10. Architecture (as reconstructed from code, not docs)

```
ui.py (stdlib http.server, SSE, one-run LOCK, workspace/<run_id>/state.json checkpointing)
  └─ POST /api/run → cobol_migrate.Pipeline.run() — 13 stages (ingest…package)
       ├─ discover/analyze: regex+heuristic; call-graph entry pick; file-assigns/file-ops extraction
       ├─ baseline: GnuCOBOL compile+run (host cobc preferred; docker gnucobol-ocesql + PG via ocesql; CICS/DLI/ReportWriter → blocked/bypassed)
       ├─ transpile: opensourcecobol4j (cobj) docker container — SEPARATE Java track (libcobj.jar)
       ├─ collect/generate: modernize/ V1 lexer→parser→SemanticIR→NativeProgramGenerator (hand-rolled Java, no cobj)
       │    └─ executed by execution/scenario_runner (docker temurin or host javac)
       ├─ compare: execution/equivalence.EquivalenceEngine (contract/observation model, 12 modes)
       ├─ refactor: copybook→JPA models + enterprise_generator Spring Boot/Batch app (validate Gate-2 track)
       ├─ validate: mvn package + Spring Boot jar run (Gate 2) + real mutation testing (Gate 8)
       └─ report/package: manifest.json, certification gates, ZIP release
modernize/native_pipeline.py — PARALLEL verdict engine (NATIVE_JAVA_VERIFIED) used by tests/tools
modernize_v2/ — isolated Phase-2 parser/scope/capability foundation; NOT wired to any pipeline (0 importers)
tools/cobol_java_differential_verifier.py — standalone 4-step verifier + ui /api/verify-differential
tools/reference_runtimes/ — z390/Hercules/GnuCOBOL adapters (oracles never executed except GnuCOBOL)
```

## 11. Production-readiness verdict & priority list

**SAFE TO SAY**: A genuinely fail-closed differential harness exists and proves byte/display parity for a tested core-COBOL subset (MOVE/arith/IF/EVALUATE/PERFORM incl THRU/VARYING/sections/GO TO in-range, STRING/UNSTRING/INSPECT-subset, COMP/COMP-3/COMP-5 numerics, REDEFINES/OCCURS/ODO, sequential/line-sequential/relative/indexed-vs-PG files, static+dynamic CALL ref/content, SORT/MERGE in-memory, SQL CRUD vs PostgreSQL, VALUE-clause truncation) — evidenced by 56 parity fixtures + 13 phase-1 differentials + 4/4 e2e differentials + logical-audit + mutation-execution suites, live-green this audit.

**UNSAFE TO SAY**: "production-grade"; any z390/Hercules/DB2-z/OS/CICS-TS/real-VSAM equivalence (no oracle ever executed); "7/7 mentor workloads certified" (fabricated); JCL COND routing correctness (stubbed in parity, source-text elsewhere); trailing-space DISPLAY parity (masked by normalizer); anything relying on seeded-baseline e2e (self-authored oracles).

**PROVABLY FALSE**: cjp CLI works; GOLDENPAY repo path exists; BANKTXN01/UNSEEN02/03 results; "no remaining bugs"; "SQLite VSAM emulation"; "ICU4J EBCDIC proven"; "COPY REPLACING supported"; "reference proven z390/Hercules"; "100% mentor Gate-1 byte match".

### P0 (must fix before ANY production claim)
1. B1/B2 DIVIDE INTO+GIVING/REMAINDER inversion (store INTO/BY in parser props; swap operands; add differential fixture — the form is currently untested anywhere).
2. B3 MockSqlService.initialize ordering (move after execute() DataSource selection or guard).
3. B4 remove unconditional baseline_verified=True; wire actual bypass status through.
4. P1/P3/P4/P5 comparator containment+normalizer fixes; P7 seeded-baseline tests must derive oracles from real GnuCOBOL runs.
5. P8 vacuous mutation tests → assert mutant≠original output; delete fabricated attribute reads.
6. B12 parser self.error crash; B14 COMPUTE keyword-truncation.

### P1
B5 COMP-3 indexed offsets; B6 SORT BigDecimal keys; B7 ZERO-fallback diagnostics; B8 dynamic-CALL else-diagnostic; B9 EXTEND/I-O sequential; B10 JCL ClassNotFound rc; B11 BY VALUE; B13 STRING overflow scoping; B15 slicer fabrication (warn or fail); lexer COPY cycle-detection; check_fingerprint image mismatch; auth contract (set UI_AUTH_CREDENTIALS in ci nightly or re-anchor tests).

### P2
Remove 242 stale tracked artifacts (bytecode/generated trees/.exe/.so/orphan archives/unpacked fixtures) after consumer-grep safety; commit or delete untracked WIP (behavioral_equivalence suite, resolver.py, v2 WIP tests breaking local collection); fix conftest 12/13 stages; dedupe keyword tables/MockSqlService/CicsTransactionContext/Db2ErrorMapper; wire modernize_v2 or freeze it; fix pyproject deps+console-script.

### P3
Docs overhaul: delete fabricated certification narratives or regenerate from live runs; update KNOWN_LIMITATIONS with the 12 missing entries; correct README commands/counts/ports; add CI lane for e2e/differential ON-by-default (already enforced in Gate 4 — extend to the 5 env-gated e2e files).

---

**Completion ledger (final)**: All 2,045 tracked files accounted in reports/master-file-inventory.md (2,044 tracked + .gitignore cross-checks). Fully line-read this audit: entire modernize/ (lexer 464, parser 3044, native_generator 6398, native_pipeline 1678, enterprise_generator 1019, jcl_parser 699, jcl_generator 233, bms_parser 165, capability_matrix 761, control_flow 355, data_flow 426, dependencies 257, coverage 39, traceability 56, mock_* 200, semantic_ir 80), all 22 java_helpers files, entire modernize_v2/ (29 files, 10,969 incl. untracked resolver), entire execution/ (13), audit/ (4), tools/ (18 incl. reference_runtimes 15), src/ (2), slicer 270, audit_engine 683, conftest 45, ui.py+ui.html endpoints/auth/SSE (agents), ~110 test files classified with proof-paths, all root docs + ~30 key docs/ + reports/ claim-verified, fixtures_spec.json + 51 test-repos + legacy + 4 zips inventoried. Partial (documented): 233 docs/archive/historical files (classified stale-historical, spot-checked); parser/generator line-coverage complete via two agents with per-file attestations. Live evidence: 9/9 unit, 56/56 parity, 46/46 phase1+mutation+gates, 24/24 adversarial+negative-gates, 4/4 e2e-differential (when enabled), 43/43 unseen, 13/13 security, JDK 17/21/25 cross-compile probe, cjp/v2-collection/resolver breakages reproduced, DIVIDE bug reproduced from emitted source.