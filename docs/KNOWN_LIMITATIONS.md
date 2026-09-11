# Known Limitations

This document lists the architectural constraints and emulation limits of the current platform version.

---

## 1. Mainframe Interface Emulations

1.  **CICS Terminal Emulator**:
    *   *Limit*: Screen maps (`BMS` screens) are emulated in text format over standard console streams. The platform does not support real 3270 block-mode terminal drivers.
2.  **DB2 Host Environment**:
    *   *Limit*: SQL commands run against local JPA/Hibernate in-memory (H2) databases. Mainframe-specific features (such as DB2 plan bindings, transaction monitors, or explicit host variable isolation types) are emulated via standard JDBC.
3.  **JCL z/OS Parameter Mappings**:
    *   *Limit*: JCL step controls (e.g. `SPACE`, `UNIT`, and catalog flags) are ignored. Dataset dependencies are emulated via local directory paths.

---

## 2. Compiler Limits

1.  **Pointers & Direct Address Access**:
    *   COBOL constructs involving memory address updates (`SET ADDRESS OF var TO ptr`) are not supported and must be bypassed or rewritten.
2.  **Report Writer Breaks**:
    *   Complex control break headers and detail loops in `REPORT SECTION` are only partially parsed and require manual Spring Batch report generator stubs.
3.  **Dynamic CALL Resolution**:
    *   Program calls resolved at runtime (`CALL ws-program-name`) produce warnings and require explicit mapping dictionaries inside `migration_config.json`.
4.  **Integer/Long Fast-Path Limitations**:
    *   Variables without implied decimal points (`V`) or `COMP-3` usage are mapped to native Java `int` or `long` primitives. Size error checking (`ON SIZE ERROR`) relies on inlined absolute limits rather than precise zoned-decimal overflows. Direct binary serialization of these fields requires temporary conversions to avoid signed overpunch formatting discrepancies.
5.  **Divide-by-Zero Process Behavior Divergence**:
    *   Division by zero in GnuCOBOL crashes the program (triggering operating system signals like `SIGFPE` with exit code 136 and outputting platform-dependent crash messages). Modernized Java programs handle division by zero via inline checks or standard arithmetic exceptions, terminating with exit code 1 or logging to stderr, leading to minor process exit-code and stderr formatting divergence.

---

## 3. Subsystem & Oracle Boundaries

1.  **VSAM Emulation (KSDS & RRDS)**:
    *   *Limit*: VSAM KSDS and RRDS are emulated via relational persistence (`key_col = RRN` or record key) and in-memory structures. Physical VSAM control intervals (CI/CA splits), buffer pools, and DASD sector layouts are not reproduced and remain strictly unproven on cloud JVM runtimes.
2.  **EBCDIC Charset vs Hardware Semantics**:
    *   *Limit*: EBCDIC character transcoding (CP037, CP1047, CP500, CP273, CP1140) and RuleBasedCollator ordering are fully verified for tested scope. However, native hardware EBCDIC memory storage and CPU instruction execution remain unproven on standard ASCII/UTF-8 JVM runtimes.
3.  **Live IBM DB2 z/OS & CICS TS Subsystems**:
    *   *Limit*: Without active connections to real IBM z/OS hardware, DB2 and CICS operate via modernized Spring Boot equivalents (`JdbcTemplate`, JPA, REST controllers, `CicsProgramRegistry`). Live mainframe connections remain classified as `UNPROVEN` with fail-closed adapters (`RealDb2ZosAdapter`, `RealCicsTsReferenceAdapter`).


---

## 4. Generator Defects Found and Resolved

### 4.1 Multi-Program Entry-Point Selection (pick_entry)

- **Symptom:** When a multi-program repository's entry program sorts alphabetically after
  a subprogram, stage_discover selected the wrong entry. stage_baseline then ran
  cobc -x on a PROCEDURE DIVISION USING subprogram, causing:
  error: executable program requested but PROCEDURE/ENTRY has USING clause
- **Root cause:** pick_entry() returned program_ids[0] (first in discovery order) when no
  MAIN-named program existed. The call graph correctly identified the root but was built
  AFTER pick_entry had already set entry.
- **Fix:** After building the call graph, if exactly one unambiguous root exists and no
  explicit config entry is provided, the call-graph root overrides pick_entry.
- **Status:** RESOLVED in cobol_migrate.py stage_discover (2026-09-04).
- **Verification:** SALESPROG+SALESCALC CALL chain: baseline=done execute=done
  compare=PASS EXACT_BINARY SHA-256: 5776fd92150df00330250f044150cd8d155cc67958368ec0f19af459f51a70ca

### 4.2 GnuCOBOL CALL Chain Capability Confirmed

GnuCOBOL 3.1.2.0 fully supports multi-program static CALL chains via shared objects.
No open-source toolchain limitation exists for this pattern.
The prior baseline failure was solely due to the pipeline entry-point selection defect.

---

## 5. Audit Findings (2026-09-04 Post-Hardening Session)

### 5.1 Ambiguous Multi-Entry Repositories

- **Symptom:** When the call graph has multiple independent roots (two programs that do not
  call each other), stage_discover silently fell through to pick_entry heuristic with no
  log warning. Operators had no visibility that an ambiguous topology was encountered.
- **Root cause:** The `if not cfg_entry:` block only handled `len(roots)==1` (correct
  override) and `len(roots)==0` (no graph data). `len(roots)>1` fell through silently.
- **Fix:** Added explicit `elif len(call_roots) > 1:` branch that emits
  `[WARN] AMBIGUOUS_ENTRY_POINT` with machine-readable label, the root list, and
  instruction to provide `entry` in `migration_config.json`.
- **Status:** RESOLVED in cobol_migrate.py stage_discover (2026-09-04).
- **Remaining risk:** Entry selection remains heuristic for ambiguous topologies.
  Pipeline does not fail-closed; set `entry` in migration_config.json to disambiguate.

### 5.2 skip_legacy Seeded Baseline: No Freshness Verification

- **Symptom:** `--skip-legacy` reused files from `baseline/legacy/` with no SHA-256
  manifest and no WARN log tag. CI had no way to detect stale baseline artifacts
  automatically or verify the oracle files were valid GnuCOBOL outputs.
- **Fix:** Added SHA-256 manifest (`seeded_baseline_sha256: {file: sha256_hex}`) to
  `legacy` state data. Replaced silent log with `[WARN] STALE_BASELINE_RISK:` message.
- **Status:** RESOLVED in cobol_migrate.py stage_baseline (2026-09-04).
- **CI guidance:** Grep pipeline logs for `STALE_BASELINE_RISK` to detect seeded
  baselines. The SHA-256 manifest in `target/state.json` can be compared across runs.

### 5.3 Parser Error Recovery: Unsupported Statements Vanished from IR

- **Symptom:** When a COBOL statement failed to parse (ParserDiagnostic), the error
  recovery loop skipped forward until it found `PERIOD`, `MOVE`, `IF`, or `PERFORM`.
  This silently discarded all sibling statements after the unsupported one within the
  same sentence, dropping them from the IR entirely.
- **Root cause:** The recovery keywords (MOVE/IF/PERFORM) were arbitrary — if an INSERT
  or DROP statement appeared after an unsupported verb, valid statements were skipped.
- **Fix:** Recovery now adds the malformed statement to the IR as `status="UNSUPPORTED"`,
  making it visible to downstream stages and the generated Java. The skip loop stops at
  the next statement boundary (using `is_tok_statement_start`) rather than arbitrary
  keyword matches.
- **Status:** RESOLVED in modernize/parser.py (2026-09-04).

### 5.4 Stdout Comparison Truncation (Documented Operational Limit)

- **Limit:** Stdout comparison is capped at min(1500, 2000) = 1500 bytes tail.
  Programs producing more than 1500 bytes of stdout: only the tail is compared.
- **Detection:** Pipeline emits `[WARN] stdout comparison used truncated tail`
  when either side approaches the cap.
- **Mitigation:** Use file output (`WRITE` to sequential file) for large volumes.
  Increasing `STDOUT_TRUNCATE_LIMIT_LEGACY` requires re-testing all stdout workloads.

### 5.5 Empty Output Files Not Captured by snapshot()

- **Limit:** `snapshot()` skips files with `os.path.getsize(p) == 0`.
  Programs that intentionally produce empty output files are not captured.
- **Risk:** If Java produces an empty output where COBOL produced a non-empty one, the
  difference may not surface if the baseline also produced empty (due to skip).
  If COBOL produced non-empty but Java produced empty, the non-empty baseline IS captured
  and the PRESENT_EMPTY Java status would trigger `nonempty_status_mismatch` FAIL.
- **Classification:** PARTIALLY_MITIGATED — non-empty vs empty is detected; empty vs
  empty is not captured (both sides skip). Add files to `expected_empty_files` in
  `migration_config.json` to make empty-output contracts explicit.
