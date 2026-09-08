# PHASE 2B — T-2B-01 IMPLEMENTATION REPORT

**Source Map + Workspace Model**

Status: **COMPLETE**
Ticket: T-2B-01 (per `docs/PHASE_2_WORK_BREAKDOWN.md`, Phase 2B)

---

## 1. Implementation Summary

T-2B-01 provides the source-handling foundation for the V2
compiler pipeline:

- **`Workspace`** — an immutable, fail-closed collection of
  `SourceFile` records with deterministic ordering and a
  workspace-root safety boundary.
- **`SourceFile`** — an immutable, content-hashed source file
  whose `file_id` is derived from `modernize_v2.ir.ids`
  (`id_for_node`, kind `"SOURCE_FILE"`), and whose
  `content_hash` is the SHA-256 of the raw bytes.
- **`SourceMap`** — an immutable byte-offset → `(line, column)`
  index built from raw bytes, not decoded text.
- **Path security** — `normalize_canonical_path` rejects
  absolute paths, `..` traversal, drive-letter paths, and NUL /
  control characters, and produces canonical POSIX-style
  lowercased relative paths.

This is infrastructure only. No lexer, parser, COPYBOOK
expansion, or IR work was done; those are T-2B-02+.

---

## 2. Files Changed

### Created

| Path | Purpose |
|---|---|
| `modernize_v2/source/__init__.py` | Package surface exports |
| `modernize_v2/source/workspace.py` | `Workspace`, `SourceFile`, `FileKind`, `PathSecurityError`, `WorkspaceError`, `make_source_file`, `normalize_canonical_path`, `resolve_relative_path` |
| `modernize_v2/source/source_map.py` | `SourceMap`, `SourceMapError`, `byte_to_position`, `MAX_LINE_BYTES` |
| `tests/v2/test_source_workspace.py` | 48 T-2B-01 tests |

### Modified

None. No V1 file was modified. No Phase 2A file was modified.

### Untracked pre-existing noise (unchanged by this ticket)

`artifacts/`, `reports/`, `opencode.json`, `tests/e2e/screenshots/`,
`modernize/native_generator.py.bak`, `modernize/native_generator.py.new`,
`docs/PARSER_IR_FORENSIC_AUDIT.md`, and the Phase 2 documents from
earlier phases. `git diff --stat` is empty (all additions are
untracked files).

---

## 3. Public Interfaces

```python
from modernize_v2.source import (
    Workspace, SourceFile, SourceMap, FileKind,
    WorkspaceError, PathSecurityError, SourceMapError,
    make_source_file, normalize_canonical_path,
    resolve_relative_path, byte_to_position,
)
```

Key signatures:

- `Workspace.empty(workspace_id="default", root_canonical_path=".")`
- `Workspace.with_file(SourceFile) -> Workspace` (returns a new workspace)
- `Workspace.file_by_path(path)`, `Workspace.file_by_id(id)`, `Workspace.paths()`, `Workspace.ids()`
- `SourceFile.file_id`, `.file_kind`, `.canonical_path`, `.content_hash`, `.byte_size`, `.declared_encoding`
- `SourceMap.from_bytes(source_file, raw_bytes)` — validates `byte_size` **and** SHA-256 content hash against the `SourceFile`
- `SourceMap.position_at(byte_offset) -> SourcePosition`
- `SourceMap.position_at_line_column(line, column) -> SourcePosition`
- `SourceMap.line_count()`, `SourceMap.line_start_byte(line)`

---

## 4. Security / Path Behavior

Path safety is **fail-closed**; unsafe inputs raise
`PathSecurityError` and are never silently rewritten:

| Input | Result |
|---|---|
| `../secret`, `src/../../evil.cbl`, `..\\evil.cbl` | rejected (`..` segment) |
| `/etc/passwd`, `\\server\share\x.cbl` | rejected (absolute) |
| `C:/windows/x.cbl`, `C:\x.cbl` | rejected (drive-letter absolute) |
| Paths containing NUL or control chars (0x00–0x1F, 0x7F) | rejected |
| `src\\A.CBL`, `src//a.cbl`, `./src/a.cbl` | normalized to `src/a.cbl` |
| `""` (empty) | rejected |

`Workspace.with_file` additionally enforces that a file's
canonical path is under the workspace root when a non-default
root is configured; a file outside the root is rejected with
`PathSecurityError`.

The workspace performs **no filesystem I/O at import time** and
no file reading at any time — callers pass bytes in. This is
enforced by the existing Phase 2A invariants suite.

---

## 5. Determinism Behavior

- `SourceFile.file_id` is produced by `id_for_node` with
  `kind="SOURCE_FILE"` — fully deterministic from
  (canonical path, kind, fixed position).
- `content_hash` is SHA-256 over raw bytes.
- Workspace ordering is sorted by `canonical_path`; insertion
  order does not affect the resulting ordering or ids tuple.
- Cross-process reproducibility is tested by running the same
  workspace construction in a subprocess twice and comparing
  ids and hashes byte-for-byte, then comparing against the
  in-process result.

---

## 6. Immutability Guarantees

- `Workspace`, `SourceFile`, and `SourceMap` are
  `@dataclass(frozen=True)`.
- `Workspace.files` is a `tuple`, sorted at construction; an
  unsorted or duplicated tuple passed to the constructor is
  rejected.
- `SourceMap.line_starts` is `tuple[int, ...]` — the earlier
  design question ("frozen dataclass containing `list[int]`")
  does not apply: the index is an immutable tuple.
- Mutation attempts raise (verified by tests).

---

## 7. SourceMap Indexing Convention

- **Lines** are 1-based.
- **Columns** are 0-based **byte offsets from the start of the
  line** (not character positions).
- **Byte offsets** are 0-based from the start of the file.
- The newline byte `\n` belongs to the line it terminates.
  `\r` (CR) is ordinary content; on CRLF files the `\r` occupies
  a column on the preceding line.
- `position_at(byte_size)` is the EOF position (allowed).
  Offsets beyond `byte_size` and negative offsets raise
  `SourceMapError`.
- `position_at_line_column` on a non-final line rejects a column
  that would alias the first byte of the next line.

---

## 8. UTF-8 Behavior

Tested with `DISPLAY '€'` (euro sign = 3 UTF-8 bytes):

- Each of the 3 bytes of the euro sign has its own
  `SourcePosition`, with columns increasing by exactly 1 per
  byte.
- The closing quote is at column +3 relative to the euro sign
  start, confirming columns are **bytes, not characters**.
- No decoding occurs in the source map; the lexer (T-2B-02) will
  decode with the declared encoding.

---

## 9. Bugs Found and Fixed During This Ticket

While writing the acceptance tests, two defects in the initial
implementation were found and fixed **within T-2B-01 scope
only**:

1. **`SourceMap` line-start invariant rejected files without a
   trailing newline.** `__post_init__` required
   `line_starts[-1] == byte_size`, which only holds when the
   file ends with `\n`. Fixed: `line_starts` is now strictly a
   "line starts" index (no EOF sentinel); `byte_size` is the
   authoritative bound for offset checks.
2. **`Workspace.empty()` default root `"."` was rejected by
   `normalize_canonical_path`,** making the default workspace
   unusable. Fixed: `"."` is accepted as a canonical root
   designator; `with_file` treats `"."` as "no additional
   boundary" while still rejecting `..`/absolute paths at
   normalization time.

Both fixes are covered by regression tests.

---

## 10. Tests Executed and Results

### New T-2B-01 tests
`tests/v2/test_source_workspace.py` — **48 tests**, covering:
workspace creation, registration, stable IDs, distinct identity,
deterministic ordering, duplicate rejection (exact + case-fold),
immutability, FileKind classification, path traversal (10
parametrized inputs), control characters (7 parametrized inputs),
absolute paths (POSIX, UNC, drive-letter), normalization,
boundary enforcement, empty files, single-line files, LF, CRLF,
trailing newline, negative/beyond-EOF offsets, line/column
round-trip, UTF-8 multibyte byte offsets, SHA-256 verification,
forged-content rejection in `SourceMap.from_bytes`, and
cross-process reproducibility.

### Full V2 suite

```
$ python -m pytest tests/v2 -q
151 passed in 2.12s
```

(103 pre-existing Phase 2A tests + 48 new T-2B-01 tests.)

### V1 spot checks (unmodified)

```
$ python -m pytest tests/test_modernize_models.py tests/test_dependencies.py \
    tests/test_control_flow.py tests/test_data_flow.py \
    tests/test_jcl_generator_fail_closed.py -q --timeout=30
7 passed in 0.30s
```

No V1 file was modified; this is a representative spot check,
not a full V1 regression claim.

---

## 11. Known Limitations

- `SourceMap.position_at` uses a linear scan over line starts
  (documented); a binary search can be added later if profiling
  requires it. Not a correctness issue.
- Line splitting counts LF only. A CR-only (classic Mac) file is
  treated as one line. COBOL sources in this project are LF or
  CRLF; if CR-only sources ever appear, this policy must be
  revisited deliberately.
- `SourceMapError` / `PathSecurityError` are exception types,
  not `Diagnostic` records; integration with the V2 diagnostic
  funnel happens when the pipeline (later phase) consumes the
  workspace.
- The `MAX_SOURCE_BYTES` cap (64 MiB) rejects oversized sources
  with a hard error; no streaming reader exists yet.
- No COPYBOOK include-graph or expansion — that is T-2E-01.

---

## 12. Deviations From the Architecture Document

None. The implementation follows
`docs/PHASE_2_ARCHITECTURE_V2.md` §6 (canonical paths, stable
ids), §13 (source handling), and the Phase 2A invariants
(no V1 deps, no wall clock, no randomness, no `Dict[str, Any]`
public contracts, fail-closed).

---

## 13. Next Recommended Ticket

**T-2B-02 — Lexer for COBOL (fixed + free format)**,
per `docs/PHASE_2_WORK_BREAKDOWN.md` §"First 10 Tickets".

The lexer should consume `SourceFile` + `SourceMap` to produce
a typed token stream with `SourceSpan` provenance.
