# Production Readiness Guidelines

This document details the checklist and requirements for deploying this platform to production migration pipelines.

---

## 1. Host Infrastructure Requirements

1.  **JDK and Maven**:
    *   The host executing the pipeline must have Java SDK 17+ and Maven 3.8+ installed locally.
2.  **GnuCOBOL Environment**:
    *   Docker must be active on the host if GnuCOBOL is used to compile golden baseline execution outputs. If Docker is not available, validations will run in emulated mode.
3.  **Permissions**:
    *   The execution process requires read/write access to the workspaces directory.

---

## 2. Production Checklist

| Category | Status | Details |
|---|---|---|
| **Security Auth** | `PARTIAL` | Can be enabled by configuring the `UI_AUTH_CREDENTIALS` env variable. |
| **Workspace Cleanup** | `PARTIAL` | Old runs are preserved on disk. A periodic system cron task is recommended to purge directories older than 7 days. |
| **Mainframe Connectors** | `MISSING` | Requires configuring real staging connections to DB2 and BMS screen drivers. |
| **SBOM Scan** | `READY` | Checked-in dependencies list documented inside `docs/SBOM.md`. |
| **Subprocess Timeouts** | `READY` | Timeout limits (120 seconds) enforced on all command executions. |
