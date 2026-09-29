# Fail-Closed Mainframe Construct Matrix

This document defines the strict fail-closed policy for unsupported or partially supported mainframe constructs. When encountering an unsupported construct, the modernization pipeline must fail closed with an actionable diagnostic message rather than silently emitting incomplete Java code or faking compilation passes.

> **Evidence note:** tiers below are reconciled with `modernize/capability_matrix.py`
> (authoritative). The executable transformation is deterministic with no LLM;
> OpenSource COBOL 4J (`cobj`/`libcobj.jar`) is the Track-A/Gate-1 oracle only;
> `z390`/`Hercules`/`ICU4J` are test-only reference oracles; `PHASE_2_*`
> target-design items remain planned unless a landed `modernize_v2/` module is named.

| Construct Category | Specific Mainframe Feature | Status | Pipeline Behavior | Remediation / Action Required |
|---|---|---|---|---|
| **Database** | **IMS DB/DC (`EXEC DLI`, `CBLTDLI`)** | **`UNSUPPORTED`** | **FAIL_CLOSED** (Emits `BlockedVerdict` with line number) | Modernize hierarchical IMS databases to relational PostgreSQL/DB2 tables before transpilation. |
| **Messaging** | **IBM MQSeries (`MQCONN`, `MQPUT`, `MQGET`)** | **`UNSUPPORTED`** | **FAIL_CLOSED** | Refactor native MQ calls to JMS / Spring JMS / Spring Cloud Stream interfaces. |
| **Online CICS** | **Unsupported CICS API verbs (e.g. `EXEC CICS SPOOL`)** | **`UNSUPPORTED`** | **FAIL_CLOSED** | Map batch spooling to standard filesystem or object storage API. |
| **Online CICS** | **`EXEC CICS LINK`, `XCTL`, `SEND MAP`, `RECEIVE MAP`** | **`PARSED_ONLY (stub)`** | Parsed to IR; generated Java emits stubs/diagnostics via `CicsTransactionContext` & Spring MVC scaffolding — not behavior-preserving | Validate COMMAREA sizes and field alignments in REST DTOs; do not treat stub output as proven parity. |
| **Data Types** | **`COMP-X` / `COMP-N` (Non-standard vendor extensions)** | **`UNSUPPORTED`** | **FAIL_CLOSED** | Convert non-standard binary storage layouts to standard `COMP` / `COMP-5`. |
| **Data Types** | **`COMP` / `COMP-3` / `COMP-5` (IBM Packed Decimal & Binary)** | **`MIXED: DIFFERENTIALLY_VERIFIED (COMP/COMP-3) / GENERATED_ONLY (COMP-5)`** | `COMP`/`COMP-3` via `CobolNumeric` & `CobolDecimal`; `COMP-5` generates without a differential fixture | Byte-level mathematical equivalence verified against IBM mainframe rules for `COMP`/`COMP-3` only; `COMP-5` native-endian binary remains unverified. |
| **Storage** | **`REDEFINES` & `OCCURS DEPENDING ON` (ODO)** | **`MIXED: DIFFERENTIALLY_VERIFIED (flat REDEFINES) / GENERATED_ONLY (ODO)`** | Flat scalar/group/COMP-3 views via array backing overlays; ODO generates without a differential fixture | Verified differential byte overlay checks across tested scalar and group fields; ODO bounds behavior not differentially verified. |
| **Storage** | **VSAM RRDS (`ORGANIZATION RELATIVE`)** | **`COMPATIBILITY_PROVEN`** | Supported via relational emulation (`key_col = RRN`) | RRN 1-based relative keys and status codes (00, 22, 23, 24) verified. Physical VSAM DASD remains UNPROVEN. |
| **Storage** | **Physical VSAM Internals (CI/CA splits, buffer pools)** | **`UNPROVEN`** | **FAIL_CLOSED** | Physical DASD control intervals and buffer pools are not reproduced on cloud JVM. |
| **SQL / DB2** | **Live IBM DB2 z/OS Connection** | **`UNPROVEN`** | **FAIL_CLOSED** (via `RealDb2ZosAdapter`) | Without verified IBM z/OS host connection (`DB2_ZOS_HOST`), execution fails closed as `UNAVAILABLE`. |
| **Online CICS**| **Live IBM CICS TS Region (EXCI / IPIC)** | **`UNPROVEN`** | **FAIL_CLOSED** (via `RealCicsTsReferenceAdapter`)| Without verified live CICS TS region (`CICS_TS_HOST`), execution fails closed as `UNAVAILABLE`. |
| **Charset** | **EBCDIC Code Page Transcoding (CP037, CP1047, CP500, etc.)** | **`UNIT_TESTED_ONLY (tools) / UNSUPPORTED_IN_JAVA`** | Python reference adapters (`CobolCharsetAdapter` & `ICU4J` strategy) unit-tested; generated Java uses ASCII/Unicode and the file I/O path has no EBCDIC codec | Byte transcoding and RuleBasedCollator ordering verified in tools only; native hardware DASD storage and in-Java collation unproven. |
| **Batch JCL** | **JCL Job Steps, `COND=(0,NE)`, `SET` symbols, DD files** | **`COMPATIBILITY_PROVEN`** | Supported via `JclExecutionContext` & Spring Batch | Generates Spring Batch configuration (Real JES2/JES3 unproven). |
| **Batch JCL** | **Unsupported JES Control Cards (e.g. `/*JOBPARM PROCLIB=...`)** | **`UNSUPPORTED`** | **FAIL_CLOSED** | Provide standard JCL procedure expansion before batch migration. |
| **SQL / DB2** | **DB2 DML (SELECT, INSERT, UPDATE, DELETE, JOIN, CURSOR)** | **`UNIT_TESTED (emulated)`** | Parsed and generated via PostgreSQL translation & direct JDBC (`SQL.*`); emulated locally, not differentially verified vs GnuCOBOL | Tested with real PostgreSQL container; Mock SQL rejected for business parity; GnuCOBOL-baseline differential remains unverified. |
