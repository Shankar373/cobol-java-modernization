# Supported COBOL Features

This document provides a matrix of COBOL grammar and batch statements supported by the compiler engine.

---

## Feature Matrix

| Feature / Statement | Support Tier | Description |
|---|---|---|
| **EVALUATE** | `VERIFIED` | Translated to standard Java `switch` or `if-else` blocks. |
| **PERFORM VARYING** | `VERIFIED` | Emitted as standard Java loops with break-guard indices. |
| **REDEFINES** | `VERIFIED` | Mapped to native Java getters/setters performing substring or ByteBuffer views over overlapping memory. |
| **OCCURS / OCCURS DEPENDING** | `VERIFIED` | Subscripted arrays backed by Java lists or arrays with dynamic checkBounds verification. |
| **CALL ... USING** | `VERIFIED` | Arguments passed by reference wrapping values inside custom `CobolRef` objects. |
| **CALL identifier (Dynamic)**| `VERIFIED` | Dispatched against registered modernized program classes. |
| **PERFORM THRU / THROUGH** | `VERIFIED` | Sequential execution of contiguous paragraph ranges. |
| **GO TO** | `VERIFIED` | Structured forward branches and paragraph exits. |
| **UNSTRING** | `VERIFIED` | Delimiter splitting, pointer offset updates, and tallying. |
| **INSPECT** | `VERIFIED` | TALLYING ALL/LEADING, REPLACING, and CONVERTING. |
| **SORT / MERGE** | `VERIFIED` | Executed using native JVM-based collection sorting utilities. |
| **RECORD SEQUENTIAL** | `VERIFIED` | Fixed-length binary record stream I/O with byte buffers. |
| **VSAM Files (Indexed - KSDS)**| `EMULATED` | Simulated locally using persistent relational tables (PostgreSQL/H2). |
| **VSAM Files (Relative - RRDS)**| `EMULATED` | Simulated locally using relational tables (`key_col = RRN`) and memory stores. |
| **EBCDIC Charset & Collation** | `VERIFIED_FOR_TESTED_SCOPE` | CP037, CP1047, CP500, CP273, CP1140 transcoding and EBCDIC collation strategy. |
| **Report Writer** | `PARTIAL` | Translates page formats but complex control breaks are bypassed. |
| **Embedded DB2 SQL** | `EMULATED` | Executed via JDBC / JPA bindings using an emulated local SQL database. |
| **CICS / BMS Maps** | `EMULATED` | Modernized to Spring REST endpoints, in-memory COMMAREA registry, and JSON DTOs. |
| **POINTER / ADDRESS OF** | `UNSUPPORTED` | Unsupported; memory pointers are bypassed/ignored. |
