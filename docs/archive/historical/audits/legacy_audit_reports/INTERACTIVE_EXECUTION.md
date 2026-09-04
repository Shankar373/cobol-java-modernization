> [!NOTE]
> **HISTORICAL ARCHIVE — NOT CURRENT SOURCE OF TRUTH**  
> This document is preserved for historical provenance and audit trail purposes only. Refer to [`DOCUMENTATION_INDEX.md`](../../../../DOCUMENTATION_INDEX.md) for the authoritative active documentation set.

---

# Phase 9: Interactive Execution Layer Audit

- **Interactivity Detection**: `detect_interactivity()` scans the reachable call-graph for bare `ACCEPT` statements (excluding `FROM DATE/TIME/DAY` systems).
- **Heredoc Shell Parsing**: `scenario_parser.py` parses `cat <<EOF` and echo/printf pipes from shell scripts to generate deterministic input arrays.
- **Watchdog Protection**: Ensures running processes are killed if they exceed `timeout_seconds` or `max_output_bytes` limits.
