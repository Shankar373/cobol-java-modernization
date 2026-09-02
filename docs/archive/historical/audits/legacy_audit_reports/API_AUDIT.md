> [!NOTE]
> **HISTORICAL ARCHIVE — NOT CURRENT SOURCE OF TRUTH**  
> This document is preserved for historical provenance and audit trail purposes only. Refer to [`DOCUMENTATION_INDEX.md`](../../../../DOCUMENTATION_INDEX.md) for the authoritative active documentation set.

---

# Phase 18: API Routing Endpoint Audit

- `GET /api/state`: Returns workspace list.
- `POST /api/run`: Launches migration run inside background worker thread.
- `GET /api/log-stream`: SSE stream.
- `GET /api/artifacts`: Lists target folder artifacts.
- `GET /api/artifact-content`: Path-traversal guarded file reader.
