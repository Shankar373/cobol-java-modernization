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
