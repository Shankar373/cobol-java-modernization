# Supported COBOL Features

This document provides a matrix of COBOL grammar and batch statements supported by the compiler engine.

> **Scope note (deterministic architecture):** The executable transformation is fully
> deterministic — `modernize/lexer.py` → `modernize/parser.py` →
> `modernize/semantic_ir.py` → `modernize/native_generator.py` — with no LLM
> anywhere in the pipeline. OpenSource COBOL 4J (`cobj` + `libcobj.jar`,
> `jp.osscons`) is used only for the Track-A verification gate in
> `cobol_migrate.py` (`stage_transpile`/`stage_collect`), never in generated
> Track-B applications. `z390`/`Hercules`/`ICU4J` are test-only reference
> oracles (see `docs/integration/`). Authoritative per-construct evidence
> levels live in `modernize/capability_matrix.py`; where this table is less
> precise, that module governs. `PHASE_2_*` documents remain
> proposed/future design unless an implementation report names a landed module.

---

## Feature Matrix

| Feature / Statement | Support Tier | Description |
|---|---|---|
| **EVALUATE** | `UNIT_TESTED` | Translated to standard Java `switch` or `if-else` blocks; multi-subject (`ALSO`/`THRU`) differential parity not yet proven (`PROC.EVALUATE` in `modernize/capability_matrix.py`). |
| **PERFORM VARYING** | `VERIFIED` | Emitted as standard Java loops with break-guard indices. |
| **REDEFINES** | `VERIFIED_FOR_TESTED_SCOPE` | Flat scalar/group and COMP-3 byte views are differentially verified; nested REDEFINES over OCCURS remains `PARSED_ONLY` (`REDEFINES.NESTED_COMPLEX`). |
| **OCCURS / OCCURS DEPENDING** | `UNIT_TESTED` / `GENERATED_ONLY` | Fixed `OCCURS` is unit-tested (`OCCURS.FIXED`); `OCCURS DEPENDING ON` generates code but has no differential fixture (`OCCURS.DEPENDING_ON`). |
| **CALL ... USING** | `UNIT_TESTED` | `BY REFERENCE`/`BY CONTENT`/`BY VALUE` parse and generate (`PROC.CALL_STATIC`, `PROC.CALL_BY_REFERENCE`); only `BY CONTENT` has a differential fixture (`PROC.CALL_BY_CONTENT`). |
| **CALL identifier (Dynamic)**| `GENERATED_ONLY` | Dispatched against registered modernized program classes; unknown targets emit diagnostics — no differential fixture (`PROC.CALL_DYNAMIC`). |
| **PERFORM THRU / THROUGH** | `UNIT_TESTED` | Sequential execution of contiguous paragraph ranges; `EXIT PARAGRAPH` inside range and non-contiguous ranges not differentially verified (`PROC.PERFORM_THRU`). |
| **GO TO** | `UNIT_TESTED` | Structured forward branches and paragraph exits; `GO TO DEPENDING ON` unsupported and in-range jumps not differentially verified (`PROC.GO_TO`). |
| **UNSTRING** | `UNIT_TESTED` | Delimiter splitting, pointer offset updates, and tallying; no differential fixture (`STRING.UNSTRING_STMT`). |
| **INSPECT** | `UNIT_TESTED` | TALLYING ALL/LEADING, REPLACING, and CONVERTING; no differential fixture (`STRING.INSPECT`). |
| **SORT / MERGE** | `UNIT_TESTED` | `USING`/`GIVING` file sort only; `INPUT`/`OUTPUT PROCEDURE` not differentially verified (`SORT_MERGE`). |
| **RECORD SEQUENTIAL** | `UNIT_TESTED` | Fixed-length binary record stream I/O; record-boundary enforcement not differentially verified (`FILE.SEQUENTIAL_FIXED`). |
| **VSAM Files (Indexed - KSDS)**| `EMULATED` | Simulated locally using persistent relational tables (PostgreSQL/H2); unit-tested only (`FILE.INDEXED_KSDS`). |
| **VSAM Files (Relative - RRDS)**| `EMULATED` | Simulated locally using relational tables (`key_col = RRN`) and memory stores; unit-tested only (`FILE.RELATIVE`). |
| **EBCDIC Charset & Collation** | `UNIT_TESTED_ONLY` (tools) / `UNSUPPORTED_IN_JAVA` | Python reference adapters (`CobolCharsetAdapter`, `CobolCollationStrategy`) are unit-tested; generated Java uses ASCII/Unicode collation and the file I/O path has no EBCDIC codec (`FILE.SEQUENTIAL_EBCDIC`). |
| **Report Writer** | `PARTIAL` | Translates page formats but complex control breaks are bypassed. |
| **Embedded DB2 SQL** | `UNIT_TESTED` (emulated) | Parsed and executed via JDBC / JPA bindings against a local emulated database; not differentially verified against a GnuCOBOL baseline (`SQL.*`). |
| **CICS / BMS Maps** | `PARSED_ONLY` (stub) | Parsed into IR; generated Java emits stubs/diagnostics only (`CICS.*`), modernized at most to Spring REST/JSON DTO emulation. |
| **POINTER / ADDRESS OF** | `UNIT_TESTED` (partial) | Parsed and generated with `SET ADDRESS OF` limits; not differentially verified (`POINTER_FIELDS`). |
