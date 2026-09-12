# SystemaOps Master Capability Matrix — Forensic Audit

Branch: `environment-discovery` @ `d2311c5` — audited live 2026-09-11.

**Method.** No capability is marked verified because code exists. `DIFFERENTIALLY_VERIFIED` requires an executed COBOL-vs-Java comparison (run_parity via GnuCOBOL/OCESQL docker oracle, or PG-probe component suites). Live evidence gathered this audit: `tests/unit` 9/9; e2e/differential 4/4 with `PARITY_ALLOW_SKIP=true` (and confirmed **SKIP-by-default** without it); phase1+mutation+negative-gates 46/46; parity fixtures 56/56; DIVIDE-INTO bug reproduced from generated source; cjp crash reproduced; tests/v2 local collection broken by untracked WIP.

Status vocabulary: `DIFFERENTIALLY_VERIFIED` (oracle-backed), `CONDITIONALLY_CERTIFIED` (oracle-limited/seeded), `UNIT_TESTED_ONLY`, `IMPLEMENTED_NOT_VERIFIED`, `PARTIAL`, `BROKEN`, `UNSUPPORTED`, `EXPERIMENTAL`, `VERIFIED` (engine-level fail-closed proofs).

| Capability | Code | Parser | IR | Generator | Compile | Runtime | COBOL Baseline | Differential/Negative | Status |
|---|---|---|---|---|---|---|---|---|---|
| PIC zoned DISPLAY numeric (S9/V) | Y | Y | Y | Y | Y | Y | CERT (56 parity fixtures + phase1) | GATE (java_source_mutation) | DIFFERENTIALLY_VERIFIED |
| PIC alphanumeric X / group bytes | Y | Y | Y | Y | Y | Y | CERT (fixtures, group_move) | GATE | DIFFERENTIALLY_VERIFIED |
| USAGE COMP (binary S9(n)) | Y | Y | BigDecimal | Y | Y | Y | CERT (comp_binary + 8-case VALUE truncation) | GATE | DIFFERENTIALLY_VERIFIED |
| USAGE COMP-3 (packed decimal) | Y | Y | BigDecimal+storage image | Y | Y | Y | CERT (fixed-binary fixture, decode_bcd comparators) | GATE | DIFFERENTIALLY_VERIFIED |
| USAGE COMP-5 | Y | Y | BigDecimal | Y | Y | Y | CERT (comp5_differential PASS) | GATE | DIFFERENTIALLY_VERIFIED |
| COMP-1 / COMP-2 (float/double) | PARTIAL (only via USAGE IS) | Y | Float/Double | NOT TESTED | NOT TESTED | NO | NONE — unreachable from bare usage tokens; no fixture | NONE | IMPLEMENTED_NOT_VERIFIED |
| Edited PIC (Z , . $ CR + -) | Y | Y | String.format/CobolNumeric | Y | Y | Y | CERT (pic_edited + be12 fixtures) | GATE | DIFFERENTIALLY_VERIFIED |
| 88-level conditions (single value) | Y | Y | isXxx() helpers | Y | Y | Y | CERT (level88 fixtures) | GATE | DIFFERENTIALLY_VERIFIED |
| 88-level multi-value / THRU VALUEs | BUG (parser keeps only first value :775-776) | Y | Partial (SET TO TRUE assigns values[0]) | ? | ? | ? | NONE | NONE | PARTIAL/BROKEN |
| REDEFINES scalar/group/COMP-3 views | Y | Y | backing byte[] + typed accessors; **no COMP binary sizes / SYNCHRONIZED alignment; 1-D occurs stepping only (:5121,:5042-5052)** | Y | Y | Y | CERT (redefines01 + redefines_occurs_group parity) | GATE | DIFFERENTIALLY_VERIFIED (subset; layout limits unlisted) |
| OCCURS fixed tables | Y | Y | Java arrays | Y | Y | Y | CERT (occurs01) | GATE | DIFFERENTIALLY_VERIFIED |
| OCCURS DEPENDING ON | Y | Y | checkBounds guard | Y | Y | Y | CERT (occurs_odo fixture) | GATE | DIFFERENTIALLY_VERIFIED |
| INDEXED BY | N (clause dropped silently) | N | N | - | - | - | NONE | NONE | UNSUPPORTED (silent drop) |
| JUSTIFIED / BLANK WHEN ZERO | N (silently dropped) | N | N | - | - | - | NONE | NONE | UNSUPPORTED (silent drop) |
| VALUE clause (incl. truncation) | Y | Y | two-step init + instance init block | Y | Y | Y | CERT (VALUE clause battery: normal/neg/boundary/oversized) | GATE | DIFFERENTIALLY_VERIFIED |
| DDL+seed of repo data/*.SQL in standalone H2 runs | - | - | **DEAD CODE: MockSqlService.initialize() in main() pre-sets jdbcTemplate so execute() DDL+seed block (if jdbcTemplate==null) unreachable (:6287-6288 vs :6144)** | compiles | SILENT SQLCODE -1 / empty results | - | NOT COVERED by any fixture | NONE | BROKEN (silent) |
| Dynamic CALL to UNREGISTERED target | Y | Y | **if/else-if chain has no trailing else -> silent no-op CALL (:2298-2314)** | compiles | SILENT NO-OP | - | NOT COVERED | NONE | BROKEN (silent) |
| OPEN EXTEND / OPEN I-O on SEQUENTIAL files | Y | Y | **no branch -> stream stays null, FILE STATUS set 00, writes dropped (:4344-4351)** | compiles | SILENT DATA LOSS | - | NOT COVERED | NONE | BROKEN (silent) |
| Indexed/RELATIVE files containing COMP-3 fields | Y | Y | **COMP-3 storage-length halving applied only for binary-sequential (:3425,:3432-3433) -> INDEXED/RELATIVE key/alt-key offsets WRONG** | compiles | WRONG KEY BYTES | - | NOT COVERED (no fixture mixes COMP-3 into indexed records) | NONE | BROKEN (silent) |

| MOVE (all forms incl. multi-target) | Y | Y | Y | Y | Y | Y | CERT (75-parametrized fixtures) | GATE | DIFFERENTIALLY_VERIFIED |
| MOVE CORRESPONDING | Y | Y | Y | Y | Y | Y | CERT (corresponding fixture) | GATE | DIFFERENTIALLY_VERIFIED |
| ADD / SUBTRACT / MULTIPLY | Y | Y | CobolArithmetic.* | Y | Y | Y | CERT | GATE | DIFFERENTIALLY_VERIFIED |
| ADD/SUBTRACT CORRESPONDING | Y | Y | Y | Y | Y | Y | CERT | GATE | DIFFERENTIALLY_VERIFIED |
| DIVIDE ... BY / INTO (non-GIVING) | Y | Y | CobolArithmetic.divide | Y | Y | Y | CERT (arithmetic errors fixtures) | GATE | DIFFERENTIALLY_VERIFIED |
| DIVIDE INTO ... GIVING | Y | Y | **BUG: emits A/B instead of B/A** (:1070); REMAINDER dividend/divisor also swapped for INTO form (:1090-1095) | compiles | RUNS WRONG | Y | **NO FIXTURE — untested form** | NONE | BROKEN (silent wrong result) |
| DIVIDE ... REMAINDER | Y | Y | CobolArithmetic.remainder | Y | Y | Y | CERT (remainder fixture) | GATE | DIFFERENTIALLY_VERIFIED (BY-form only; INTO+GIVING mis-ordered) |
| COMPUTE (+ ROUNDED) | Y | Y | infix expr translator + ** power | Y | Y | Y | CERT (compute fixtures) | GATE | DIFFERENTIALLY_VERIFIED |
| ON SIZE ERROR / NOT ON SIZE ERROR | Y | Y | CHECKED policy wrapper | Y | Y | Y | CERT (sizeerr01 differential) | GATE | DIFFERENTIALLY_VERIFIED |
| IF / ELSE / END-IF | Y | Y | Y | Y | Y | Y | CERT | GATE | DIFFERENTIALLY_VERIFIED |
| EVALUATE (+ WHEN OTHER) | Y | Y | if/else-if chain | Y | Y | Y | CERT (evaluate_when_other) | GATE | DIFFERENTIALLY_VERIFIED |
| EVALUATE ... THRU | Y | Y | **int-only emission (BigDecimal/String → javac error)** | PARTIAL | PARTIAL | PARTIAL | PASS only for int subjects (phase1 evaluate) | NONE | PARTIAL |
| EVALUATE ... ALSO (multi-subject) | Y | Y | && conjunction | Y | Y | Y | CERT | GATE | DIFFERENTIALLY_VERIFIED |
| PERFORM para / THRU | Y | Y | perform() range walker | Y | Y | Y | CERT (perform_thru) | GATE | DIFFERENTIALLY_VERIFIED |
| PERFORM TIMES / UNTIL (inline+out) | Y | Y | for/while loops | Y | Y | Y | CERT | GATE | DIFFERENTIALLY_VERIFIED |
| PERFORM VARYING (+ AFTER) | Y | Y | nested loop headers | Y | Y | Y | CERT (varying/AFTER fixtures) | GATE | DIFFERENTIALLY_VERIFIED |
| GO TO (incl. in performed range) | Y | Y | nextParagraphIndex jump | Y | Y | Y | CERT (goto-in-range fixture) | GATE | DIFFERENTIALLY_VERIFIED |
| GO TO ... DEPENDING ON | N | N | N | - | - | - | NONE | NONE | UNSUPPORTED |
| NEXT SENTENCE | Y | Y | skipToNextSentence | Y | Y | Y | CERT (next_sentence phase8) | GATE | DIFFERENTIALLY_VERIFIED |
| EXIT / EXIT PERFORM / PARAGRAPH / PROGRAM | Y | Y | break/return/section-jump | Y | Y | Y | CERT | GATE | DIFFERENTIALLY_VERIFIED |
| INITIALIZE | Y | Y | **uses VALUE-clause map (empty at :5883) -> String fields become empty, not PIC-width SPACES (:1845-1855, :581-598)** | Y | WRONG for alphanumeric fields | - | phase8 (does not exercise alnum case) | NONE | PARTIAL/BROKEN (alnum) |
| SET TO TRUE/FALSE, SET ADDRESS OF | Y | Y | 88-assign / CobolRef | Y | Y | Y | CERT (set_true fixtures; pointers phase8) | GATE | DIFFERENTIALLY_VERIFIED (ADDRESS OF = UNIT) |
| STOP RUN / GOBACK | Y | Y | StopRunException→exit(0) | Y | Y | Y | CERT (stop_run propagation) | GATE | DIFFERENTIALLY_VERIFIED |
| CONTINUE | Y | Y | ; | Y | Y | Y | CERT | GATE | DIFFERENTIALLY_VERIFIED |
| SEARCH / SEARCH ALL | Y (status=UNSUPPORTED node) | Y | **NONE — falls to // UNSUPPORTED diagnostic** | - | - | - | NONE | NONE | UNSUPPORTED (fail-closed diag) |
| Class conditions (NUMERIC/ALPHABETIC) | N (no lexer keyword) | N | N | - | - | - | NONE | NONE | UNSUPPORTED |
| DECLARATIVES sections | Y (keyword only → UNKNOWN nodes) | Y | NONE | - | - | - | NONE | NONE | UNSUPPORTED (degraded to diagnostics) |
| STRING (+ WITH POINTER) | Y | Y | delimitedString concat + pointer splice | Y | Y | Y | CERT (string_with_pointer parity) | GATE | DIFFERENTIALLY_VERIFIED |
| STRING ON/NOT ON OVERFLOW | **Parser drops bodies** (:1526-1532 only consumes keywords) | Y | **No emission — re-parsed as unconditional siblings** | runs | runs wrong | Y | NONE | NONE | BROKEN (silent semantic corruption) |
| UNSTRING (+ POINTER/TALLYING/OVERFLOW) | Y | Y | full inline scan loop | Y | Y | Y | CERT (unstring fixtures) | GATE | DIFFERENTIALLY_VERIFIED |
| INSPECT TALLYING/REPLACING/CONVERTING | Y (single tally var; no BEFORE/AFTER) | Y | loop emitters | Y | Y | Y | CERT (inspect tallying fixture) | GATE | DIFFERENTIALLY_VERIFIED (subset) |
| Reference modification X(a:b) | Y | Y | substring emitters | Y | Y | Y | CERT (ref_mod fixtures) | GATE | DIFFERENTIALLY_VERIFIED |
| CALL static (literal) | Y | Y | direct class invoke + writeback | Y | Y | Y | CERT (callchain static) | GATE | DIFFERENTIALLY_VERIFIED |
| CALL dynamic (WS variable) | Y | Y | if/else-if chain over known programs | Y | Y | Y | CERT (call_dynamic parity — **now PASS** post c000620) | GATE (dynamic_callers → CERTIFIED_WITH_REVIEW) | DIFFERENTIALLY_VERIFIED |
| CALL BY REFERENCE | Y | Y | writeback after call | Y | Y | Y | CERT (call_by_reference mutant) | GATE | DIFFERENTIALLY_VERIFIED |
| CALL BY CONTENT | Y | Y | snapshot, no writeback | Y | Y | Y | CERT (by_content fixture) | GATE | DIFFERENTIALLY_VERIFIED |
| CALL BY VALUE | Y (mode recorded) | Y | **treated as BY REFERENCE (spurious writeback)** (:3366) | runs wrong | ? | NO dedicated fixture | NONE | BROKEN semantics / UNVERIFIED |
| Nested programs | Y | Y | child generators + parent refs | Y | Y | Y | component (phase8 nested_programs) | NONE | UNIT_TESTED_ONLY |
| COPY / copybook expansion | Y (lexer pre-expansion, case-insens 2nd pass) | Y | Y | Y | Y | Y | CERT (B-PAYCOPY, ACCTPROG repos) | GATE | DIFFERENTIALLY_VERIFIED |
| COPY REPLACING | PARTIAL (expand handles plain COPY only) | - | - | - | - | - | NONE | NONE | UNSUPPORTED |
| Sections fallthrough | Y | Y | paragraph order | Y | Y | Y | CERT (sections_fallthrough) | GATE | DIFFERENTIALLY_VERIFIED |
| LINE SEQUENTIAL files | Y | Y | BufferedReader/Writer | Y | Y | Y | CERT (line_seq fixtures) | GATE | DIFFERENTIALLY_VERIFIED |
| SEQUENTIAL fixed/binary (+COMP-3 records) | Y | Y | byte streams, halved lengths | Y | Y | Y | CERT (file_sequential_fixed parity) | GATE | DIFFERENTIALLY_VERIFIED |
| RELATIVE files (random access) | Y | Y | JdbcTemplate <fd>_vsam + LinkedHashMap | Y | Y | Y | CERT (relative_file_random_access fixture) | GATE | DIFFERENTIALLY_VERIFIED |
| INDEXED/KSDS files | Y | Y | H2/PG table + in-memory + flat fallback | Y | Y | Y | CERT (indexed missing-key + ksds_baseline vs PG; logical_audit LOGICAL_MATCH) | GATE (logical_audit negative mutants) | DIFFERENTIALLY_VERIFIED (PG-backed, EMULATED vs real VSAM) |
| FILE STATUS handling | Y | Y | status var sets | Y | Y | Y | CERT (filestat01 differential) | GATE | DIFFERENTIALLY_VERIFIED |
| VSAM real (z/OS) | N | N | N | - | - | - | NONE | NONE | UNSUPPORTED (PG/H2 emulation only) |
| Variable-length records | N | N | N | - | - | - | NONE | NONE | UNSUPPORTED |
| EBCDIC datasets | N (charset tables exist as Python lib only) | - | - | - | - | - | PURE-PYTHON table tests only | NONE | IMPLEMENTED_NOT_VERIFIED (library only, no program-level differential) |
| EXEC SQL SELECT INTO | Y | Y | JdbcTemplate queryForRowSet | Y | Y (H2/PG) | Y (ocesql+PG) | CERT (sql_baseline, postgres_e2e vs live PG) | GATE (negative_gates mock-SQL cannot PASS) | DIFFERENTIALLY_VERIFIED (PG dialect, NOT real DB2) |
| EXEC SQL INSERT/UPDATE/DELETE | Y | Y | JdbcTemplate update | Y | Y | Y | CERT | GATE | DIFFERENTIALLY_VERIFIED (PG) |
| Cursors DECLARE/OPEN/FETCH/CLOSE | Y | Y | SqlRowSet fields | Y | Y | Y | CERT (cursor fixtures) | GATE | DIFFERENTIALLY_VERIFIED (PG) |
| NULL indicators | Y | Y | wasNull() | Y | Y | Y | CERT (db2curnull01 — Java side mock-limited) | GATE | CONDITIONALLY_CERTIFIED |
| COMMIT / ROLLBACK | Y | Y | DataSourceTransactionManager | Y | Y | Y | CERT (tx fixtures) | GATE | DIFFERENTIALLY_VERIFIED (PG) |
| SQLCODE/SQLSTATE mapping | Y | Y | type-aware assign (fixed b4afbc4) | Y | Y | Y | CERT (sqlcode_loop_regression) | GATE | DIFFERENTIALLY_VERIFIED (PG subset of codes) |
| DB2 real z/OS dialect | PARTIAL (dialect warnings WITH UR/FOR UPDATE/FETCH FIRST) | - | - | - | - | - | REAL_DB2_MODE gated — never run | NONE | UNPROVEN (honest fail-closed) |
| IMS DL/I, MQ | Y (blocked diagnostic) | Y | **NATIVE_TRANSLATION_BLOCKED** | - | - | - | NONE | GATE (negative_gates IMS fails closed) | UNSUPPORTED (fail-closed) |
| EXEC CICS SEND/RECEIVE | Y (allowlist) | Y | CicsTransactionContext (real emission, not stub) | Y (component CICSREST01) | Y | **NO COBOL oracle — baseline BYPASSED for CICS** | parity harness registry = no-op echo stub | NONE | IMPLEMENTED_NOT_VERIFIED (no oracle exists in-stack) |
| EXEC CICS LINK/XCTL/RETURN | Y | Y | CicsProgramRegistry.invoke | Y | Y | NO | NONE | NONE | IMPLEMENTED_NOT_VERIFIED |
| BMS mapsets | Y (bms_parser) | Y | map copybook generation | SRC | - | - | NONE | NONE | UNIT_TESTED_ONLY (parse-level) |
| CICS real TS region | N | - | - | - | - | - | NONE (cics_runtime.py = SIMULATED/UNAVAILABLE boundary) | NONE | UNSUPPORTED (no oracle) |
| JCL JOB/EXEC/DD parse+gen | Y | Y | Spring Batch job gen | Y | Y (JCLBATCH01 e2e) | **NO JES oracle** | JCL smoke via source-text only | NONE | CONDITIONALLY_CERTIFIED (roundtrip e2e, no oracle) |
| JCL COND/IF routing | Y | Y | checkAnyStepCond | compiles | SRC keyword-sniff only | - | NONE | NONE | UNIT_TESTED_ONLY (weak) |
| JCL symbols/PROC expansion | Y | Y | symbol substitution | Y | component | - | NONE | NONE | UNIT_TESTED_ONLY |
| GDG / STEPLIB / real JES | PARTIAL parse | - | - | - | - | - | NONE | NONE | UNSUPPORTED |
| INITIATE/GENERATE/TERMINATE + print_report_group | Y | Y | full emission (:1493-1580, :5512-5591) | Y | Y | **baseline BYPASSED for Report-Writer programs** | REPORTWRITER01 output.txt committed compare | GATE | CONDITIONALLY_CERTIFIED (vs committed expected file, not live oracle) |
| SORT/MERGE (USING/GIVING/KEY) | Y | Y | in-memory List<Map> sort; **decimal keys: (BigDecimal) cast on CobolNumeric map values -> CCE/compile error (:1313-1318,:1356-1360,:1419-1423)** | PARTIAL | CCE risk for decimal keys | Y | CERT for int/String keys (sort_input_procedure PASS); decimal-key fixtures ABSENT | GATE | PARTIAL/BROKEN for decimal keys |
| RELEASE/RETURN (sort procedures) | Y | Y | map add / indexed read | Y | Y | Y | CERT (via sort procedure fixture) | GATE | DIFFERENTIALLY_VERIFIED |
| 13-stage pipeline + checkpoints | Y | - | - | - | - | - | phase9 contract tests | GATE (negative gates) | VERIFIED engine (fail-closed) |
| Differential comparator engine | - | - | - | - | - | - | logical_audit + mutation tests | GATE | VERIFIED (with documented false-PASS vectors) |
| Spring Boot/Unified gen (enterprise_generator) | Y | - | SpringBatchConfig etc. | Y (validate stage) | Y | - | SRC/component | NONE | IMPLEMENTED_NOT_VERIFIED |
| UI (ui.py/ui.html) + SSE + run history | Y | - | - | - | - | - | 89 e2e tests (2 auth failures = real contract violations) | NONE | WORKING_WITH_LIMITATIONS (auth-optional on loopback; 6 dead endpoints) |
| Packaging (Stage 12 ZIP + manifests) | Y | - | - | - | - | - | phase9 manifest tests | NONE | UNIT_TESTED_ONLY |
| Docker runtime images | Y | - | - | - | - | - | CI 5 gates | NONE | VERIFIED for GnuCOBOL/OCESQL/PG/Temurin17 stack |
| z390 / Hercules mainframe oracles | Y (adapters) | - | - | - | - | **STUB: hercules execute()=standby; z390 never installed** | comparator units only (synthetic) | NONE | IMPLEMENTED_NOT_VERIFIED (adapters exist, never executed) |
| V2 parser stack (modernize_v2) | Y | Y | **NO generator — parser/IR/scope only** | - | - | - | 24 test files, 542 tests | NONE | EXPERIMENTAL (not wired to pipeline; explicit Phase-2 foundation) |
| cjp CLI (src/cjp) | Y | - | - | - | - | - | **CRASHES on every invocation** (import + config_path + run_until missing) | NONE | BROKEN / DEAD |

## Status tallies (of 92 capability rows)

- **DIFFERENTIALLY_VERIFIED**: 53
- **CONDITIONALLY_CERTIFIED**: 3
- **UNIT_TESTED_ONLY**: 6
- **IMPLEMENTED_NOT_VERIFIED**: 6
- **PARTIAL**: 2
- **BROKEN**: 4
- **UNSUPPORTED**: 12
- **EXPERIMENTAL**: 1

## False-PASS vectors in the verification stack (must-fix before production claims)

1. **Substring containment file-match** (`tests/utils/parity_harness.py:940-945`): on byte-mismatch, PASSES if every non-empty Java line is a substring of the whole COBOL file — ignores record count, order, duplicates. Reserved for indexed/relative but applied to any declared output.
2. **`normalize_display` space collapsing** (`parity_harness.py:102-120`): trims per-line trailing whitespace and collapses runs — trailing-space/column-alignment semantics of PIC X DISPLAY are structurally masked.
3. **Mock-SQL asymmetry** (`parity_harness.py:564-709`): Java side SQL runs against hand-written no-op stubs (JdbcTemplate returns 0/empty); COBOL side runs real PG via ocesql. SQL fixtures whose DISPLAY doesn't depend on rows PASS without DB behavior being verified. True DB parity exists only in component/db PG-probe suites (sql_baseline, ksds_baseline, postgres_e2e).
4. **Seeded-baseline circularity** (`tests/component/db/test_db2_modernization.py:90-95`, `test_db2_stage1.py`, `test_vsam_ksds_stage2.py`): the test writes its own expected stdout, then asserts the pipeline reproduces it — the oracle is authored by the test.
5. **Vacuous negative-mutation twins** (`test_phase1_differential_proofs.py` — 12× `assert result.status in ("PASS","FAIL","SKIP")`, plus `:130-135` reading a nonexistent `cobol_result` attribute): give an illusion of mutation-verified constructs.
6. **e2e/differential inverted skip** (`skipif` unless `PARITY_ALLOW_SKIP=true`): five core differentials silently SKIP by default — confirmed live (4 skipped in 0.15s; 4 pass when enabled).
7. **COBOL oracle is harness-rewritten** (`parity_harness.py:286-306`): COMP/COMP-5/BINARY stripped from host vars, CONNECT + sqlca injected — parity is proven against a modified program.
8. **Report-Writer / CICS / JCL baselines BYPASSED** (`native_pipeline.py:83-85,69-70`): equivalence for these families rests on committed expected files or component e2e, never a live COBOL oracle.

---

## Deep-audit addendum (2026-09-12): updated rows + verification-infrastructure false-PASS register

Row corrections this deep audit: **+4 BROKEN rows added** (DDL-dead-path, dynamic-CALL-no-op, OPEN-EXTEND-sequential, COMP-3-indexed-offsets); **SORT/MERGE downgraded to PARTIAL/BROKEN for decimal keys**; **INITIALIZE downgraded to PARTIAL/BROKEN (alnum)**; DIVIDE-INTO row extended (REMAINDER swap). Updated tallies: DIFFERENTIALLY_VERIFIED ~44 (subset caveats noted per row), PARTIAL ~8, BROKEN ~9, UNSUPPORTED ~12, UNIT_TESTED_ONLY ~8, IMPLEMENTED_NOT_VERIFIED ~6.

These are defects in the VERIFICATION machinery itself (not COBOL capabilities). Full detail in `reports/project-gap-analysis.md`.

| # | Vector | Location | Severity | Effect |
|---|---|---|---|---|
| P1 | ISAM logical containment: Java records ⊆ baseline binary only — missing Java records PASS; order/duplicates unchecked | native_pipeline.py:1427-1444 | CRITICAL | Indexed/relative equivalence overstates |
| P2 | `self.baseline_verified = True` set unconditionally in run() — defeats bypass conditions (:61-85) and pre-existing-stdout short-circuit (:74-76) | native_pipeline.py:208 | CRITICAL | PASS against stale prior-run baselines |
| P3 | Missing native stdout.txt EXCUSED whenever baseline has any data file | native_pipeline.py:1402-1405 | HIGH | Java printing nothing can PASS |
| P4 | Parity harness substring-containment file match applied to ALL declared outputs | parity_harness.py:940-945 | HIGH | Record loss/reorder masked |
| P5 | normalize_display strips per-line trailing spaces + collapses runs | parity_harness.py:102-120 | HIGH | Trailing-space parity unfalsifiable (test_parity_trailing_spaces cannot fail) |
| P6 | Java side runs no-op MockSqlService/JdbcTemplate/CICS/COND stubs vs real COBOL+PG | parity_harness.py:563-616 | HIGH | SQL/CICS/JCL parity is mock-level, labeled as parity |
| P7 | Seeded-baseline circularity — test authors its own oracle stdout; jcl/cics e2e gates stubbed to PASS (test_jcl_modernization.py:140-141, test_cics_modernization.py:132-133) | test_db2_modernization.py:90-110; test_db2_stage1.py; component jcl/cics | HIGH | Fabricated NATIVE_JAVA_VERIFIED |
| P8 | 12 vacuous negative-mutation asserts; nonexistent-attribute read cobol_result | test_phase1_differential_proofs.py:193…:850; :130-131 | HIGH | Mutation-sensitivity unproven for 12 constructs |
| P9 | e2e/differential suite off by default (inverted PARITY_ALLOW_SKIP gate) + tolerant assert | e2e/differential/** | HIGH | Live-verified: 4 SKIP in 0.15s default; 4 PASS when enabled |
| P10 | Binary outputs compared via first ~1000 bytes of hex string | cobol_migrate.py:4227-4229,4258-4260 | MEDIUM | Tail divergence invisible |
| P11 | Non-interactive stdout compared as 1500/2000-char tails | cobol_migrate.py:4035,4092,4126 | MEDIUM | Divergence outside tail PASSes (warn only) |
| P12 | Empty-vs-empty PASS modes (EXPECTED_NO_OUTPUT, empty stdouts, empty DB evidence) | execution/equivalence.py:121-123,281-282,348-400 | MEDIUM | Vacuous PASS reachable |
| P13 | Contract modes absent -> dimension NOT_APPLICABLE (invisible) | equivalence.py:44-53 + cobol_migrate.py:4329-4336 | MEDIUM | File divergence invisible when no baseline files |
| P14 | Negative gate comparator is strict byte-eq, stricter than production gate | native_pipeline.py:1519-1530 vs 1355-1485 | MEDIUM | Overstates production gate sensitivity |
| P15 | Mutation Gate-8 "caught" on compile failure alone; mutates alphabetical java_files[0] | cobol_migrate.py:5234,5294-5295,5351-5353 | MEDIUM | Mutation evidence weak |
| P16 | H2-mode acceptance asserts accept every non-crash verdict | test_db2_acceptance.py:85-86+ | MEDIUM | Acceptance proves nothing |
| P17 | z390/Hercules disagreement never affects match verdict | tools/reference_runtimes/differential_verifier.py:169-171 | MEDIUM | Multi-oracle claim overstated |
| P18 | Fingerprint test pins a DIFFERENT image than the harness executes | tests/utils/check_fingerprint.py:4-5 vs parity_harness.py:14 | MEDIUM | Oracle integrity check verifies wrong image |

**Headline conclusion (unchanged by depth): the *tested* differential core is genuinely green (56/56 + 46/46 + 4/4 live this audit), but the UNTESTED perimeter contains silent-wrong-result emission paths that would corrupt real workloads, and the verification stack itself carries 4 CRITICAL/HIGH false-PASS vectors (P1-P7) that must be fixed before any production parity claim.**
