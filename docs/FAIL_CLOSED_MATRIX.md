# Fail-Closed Mainframe Construct Matrix

This document defines the strict fail-closed policy for unsupported or partially supported mainframe constructs. When encountering an unsupported construct, the modernization pipeline must fail closed with an actionable diagnostic message rather than silently emitting incomplete Java code or faking compilation passes.

| Construct Category | Specific Mainframe Feature | Status | Pipeline Behavior | Remediation / Action Required |
|---|---|---|---|---|
| **Database** | **IMS DB/DC (`EXEC DLI`, `CBLTDLI`)** | **`UNSUPPORTED`** | **FAIL_CLOSED** (Emits `BlockedVerdict` with line number) | Modernize hierarchical IMS databases to relational PostgreSQL/DB2 tables before transpilation. |
| **Messaging** | **IBM MQSeries (`MQCONN`, `MQPUT`, `MQGET`)** | **`UNSUPPORTED`** | **FAIL_CLOSED** | Refactor native MQ calls to JMS / Spring JMS / Spring Cloud Stream interfaces. |
| **Online CICS** | **Unsupported CICS API verbs (e.g. `EXEC CICS SPOOL`)** | **`UNSUPPORTED`** | **FAIL_CLOSED** | Map batch spooling to standard filesystem or object storage API. |
| **Online CICS** | **`EXEC CICS LINK`, `XCTL`, `SEND MAP`, `RECEIVE MAP`** | **`COMPATIBILITY_PROVEN`** | Supported via `CicsTransactionContext` & Spring MVC | Validate COMMAREA sizes and field alignments in REST DTOs. |
| **Data Types** | **`COMP-X` / `COMP-N` (Non-standard vendor extensions)** | **`UNSUPPORTED`** | **FAIL_CLOSED** | Convert non-standard binary storage layouts to standard `COMP` / `COMP-5`. |
| **Data Types** | **`COMP` / `COMP-3` / `COMP-5` (IBM Packed Decimal & Binary)** | **`E2E_PROVEN`** | Supported via `CobolNumeric` & `CobolDecimal` | Byte-level mathematical equivalence verified against IBM mainframe rules. |
| **Storage** | **`REDEFINES` & `OCCURS DEPENDING ON` (ODO)** | **`E2E_PROVEN`** | Supported via array backing overlays | Verified differential byte overlay checks across scalar and group fields. |
| **Batch JCL** | **JCL Job Steps, `COND=(0,NE)`, `SET` symbols, DD files** | **`COMPATIBILITY_PROVEN`** | Supported via `JclExecutionContext` & Spring Batch | Generates Spring Batch configuration (Real JES2/JES3 unproven). |
| **Batch JCL** | **Unsupported JES Control Cards (e.g. `/*JOBPARM PROCLIB=...`)** | **`UNSUPPORTED`** | **FAIL_CLOSED** | Provide standard JCL procedure expansion before batch migration. |
| **SQL / DB2** | **DB2 DML (SELECT, INSERT, UPDATE, DELETE, JOIN, CURSOR)** | **`E2E_PROVEN`** | Supported via PostgreSQL translation & direct JDBC | Tested with real PostgreSQL container; Mock SQL rejected for business parity. |
