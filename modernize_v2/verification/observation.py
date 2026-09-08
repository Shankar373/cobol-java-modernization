"""V2 Observation model.

The Observation captures the complete state of a single execution
(COBOL baseline or Java target). The differential comparator
(Phase 2J) compares two Observations and produces a ComparisonResult.

Observations are immutable. The content_hash is computed at
construction; it is a SHA-256 over the canonical JSON of the
observation minus the hash itself.

Per the architecture (§24.1 of docs/PHASE_2_ARCHITECTURE_V2.md),
an Observation captures:

    run_id
    workload_id
    exit_code
    stdout           (full, not truncated)
    stderr           (full)
    output_files
    db_state
    sqlcode_seq
    sqlstate_seq
    null_indicator_seq
    transaction_state
    file_status_seq
    cics_state
    batch_state
    observed_at      (logical observation epoch, not wall clock)
    encoding
    content_hash     (computed)

The model is *data model only*. The actual capture happens in
Phase 2J.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Final, Mapping


# Standard dimension identifiers. These are the keys used in
# ``ComparisonResult.dimension_results``. New dimensions are
# non-breaking; renaming a dimension is a breaking change.
DIM_EXIT_CODE: Final[str] = "exit_code"
DIM_STDOUT: Final[str] = "stdout"
DIM_STDERR: Final[str] = "stderr"
DIM_OUTPUT_FILES: Final[str] = "output_files"
DIM_DB_STATE: Final[str] = "db_state"
DIM_SQLCODE_SEQ: Final[str] = "sqlcode_seq"
DIM_SQLSTATE_SEQ: Final[str] = "sqlstate_seq"
DIM_NULL_INDICATOR_SEQ: Final[str] = "null_indicator_seq"
DIM_TRANSACTION_STATE: Final[str] = "transaction_state"
DIM_FILE_STATUS_SEQ: Final[str] = "file_status_seq"
DIM_CICS_STATE: Final[str] = "cics_state"
DIM_BATCH_STATE: Final[str] = "batch_state"

ALL_DIMENSIONS: Final[tuple[str, ...]] = (
    DIM_EXIT_CODE,
    DIM_STDOUT,
    DIM_STDERR,
    DIM_OUTPUT_FILES,
    DIM_DB_STATE,
    DIM_SQLCODE_SEQ,
    DIM_SQLSTATE_SEQ,
    DIM_NULL_INDICATOR_SEQ,
    DIM_TRANSACTION_STATE,
    DIM_FILE_STATUS_SEQ,
    DIM_CICS_STATE,
    DIM_BATCH_STATE,
)


class OutputFileMode(str, Enum):
    """How an output file's content is captured."""

    TEXT = "TEXT"
    BYTES = "BYTES"


@dataclass(frozen=True)
class OutputFileObservation:
    """A single output file produced by a run."""

    path: str
    mode: OutputFileMode
    content: str  # text or base64 of bytes, depending on mode
    size_bytes: int
    content_hash: str  # hex SHA-256 of the raw bytes

    def __post_init__(self) -> None:
        if not isinstance(self.path, str) or not self.path:
            raise ValueError("path must be a non-empty string")
        if not isinstance(self.size_bytes, int) or self.size_bytes < 0:
            raise ValueError("size_bytes must be a non-negative int")
        if not isinstance(self.content_hash, str):
            raise TypeError("content_hash must be a string")
        if not all(
            c in "0123456789abcdef" for c in self.content_hash.lower()
        ):
            raise ValueError("content_hash must be hex")
        if len(self.content_hash) != 64:
            raise ValueError("content_hash must be 64 hex chars (SHA-256)")


@dataclass(frozen=True)
class DatabaseStateObservation:
    """A snapshot of a database table for a run."""

    table: str
    row_count: int
    # Rows are a list of tuples in canonical (column-sorted) order.
    # Each tuple's elements are JSON-serializable values.
    rows: tuple[tuple[Any, ...], ...] = field(default_factory=tuple)
    columns: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not isinstance(self.table, str) or not self.table:
            raise ValueError("table must be a non-empty string")
        if not isinstance(self.row_count, int) or self.row_count < 0:
            raise ValueError("row_count must be a non-negative int")
        if self.columns is None:  # type: ignore[unreachable]
            object.__setattr__(self, "columns", ())
        if self.rows is None:  # type: ignore[unreachable]
            object.__setattr__(self, "rows", ())


@dataclass(frozen=True)
class SqlOperationObservation:
    """The result of a single SQL operation."""

    operation_index: int
    sqlcode: int
    sqlstate: str
    row_count: int | None = None
    operation: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.operation_index, int) or self.operation_index < 0:
            raise ValueError("operation_index must be a non-negative int")
        if not isinstance(self.sqlcode, int):
            raise TypeError("sqlcode must be an int")
        if not isinstance(self.sqlstate, str) or len(self.sqlstate) != 5:
            raise ValueError("sqlstate must be a 5-character string")


@dataclass(frozen=True)
class NullIndicatorObservation:
    """The null indicator state of a host variable at a given call site."""

    call_site: int
    host_var: str
    indicator: int  # -1 means null, 0 means non-null, >=0 means truncated

    def __post_init__(self) -> None:
        if not isinstance(self.call_site, int) or self.call_site < 0:
            raise ValueError("call_site must be a non-negative int")
        if not isinstance(self.host_var, str) or not self.host_var:
            raise ValueError("host_var must be a non-empty string")
        if not isinstance(self.indicator, int):
            raise TypeError("indicator must be an int")


@dataclass(frozen=True)
class TransactionObservation:
    """A transaction boundary."""

    boundary_index: int
    committed: bool
    isolation: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.boundary_index, int) or self.boundary_index < 0:
            raise ValueError("boundary_index must be a non-negative int")
        if not isinstance(self.committed, bool):
            raise TypeError("committed must be a bool")


@dataclass(frozen=True)
class FileStatusObservation:
    """A file operation's file status code."""

    operation_index: int
    path: str
    status: str  # COBOL FILE STATUS, 2 chars (or "00" for success)
    operation: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.operation_index, int) or self.operation_index < 0:
            raise ValueError("operation_index must be a non-negative int")
        if not isinstance(self.path, str) or not self.path:
            raise ValueError("path must be a non-empty string")
        if not isinstance(self.status, str):
            raise TypeError("status must be a string")


@dataclass(frozen=True)
class CicsStateObservation:
    """A CICS state snapshot at a program boundary."""

    boundary_index: int
    channel: str
    commarea_summary_hash: str  # hex SHA-256 of the canonical commarea
    resp: int = 0
    resp2: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.boundary_index, int) or self.boundary_index < 0:
            raise ValueError("boundary_index must be a non-negative int")
        if not isinstance(self.channel, str):
            raise TypeError("channel must be a string")
        if not isinstance(self.commarea_summary_hash, str):
            raise TypeError("commarea_summary_hash must be a string")
        if len(self.commarea_summary_hash) != 64:
            raise ValueError(
                "commarea_summary_hash must be 64 hex chars (SHA-256)"
            )


@dataclass(frozen=True)
class BatchStateObservation:
    """A Spring Batch Step snapshot at a step boundary."""

    step_index: int
    step_name: str
    exit_status: str
    read_count: int = 0
    write_count: int = 0
    skip_count: int = 0
    commit_count: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.step_index, int) or self.step_index < 0:
            raise ValueError("step_index must be a non-negative int")
        if not isinstance(self.step_name, str) or not self.step_name:
            raise ValueError("step_name must be a non-empty string")
        if not isinstance(self.exit_status, str):
            raise TypeError("exit_status must be a string")


@dataclass(frozen=True)
class Encoding:
    """An execution encoding declaration.

    The encoding is part of the workload contract (§16 of the
    architecture). Mismatched encodings between baseline and
    Java are an environment error.
    """

    source_codepage: str
    java_charset: str
    record_encoding: str = "FixedBinary"
    numeric_encoding: str = "NativeEndian"
    signed_encoding: str = "AsciiSign"

    def __post_init__(self) -> None:
        for f in (
            self.source_codepage,
            self.java_charset,
            self.record_encoding,
            self.numeric_encoding,
            self.signed_encoding,
        ):
            if not isinstance(f, str) or not f:
                raise ValueError("encoding fields must be non-empty strings")


@dataclass(frozen=True)
class Observation:
    """A complete observation of a single execution.

    Observations are immutable. They carry a content_hash that
    uniquely identifies the observation's contents.
    """

    run_id: str
    workload_id: str
    exit_code: int
    stdout: str
    stderr: str
    output_files: tuple[OutputFileObservation, ...] = field(
        default_factory=tuple
    )
    db_state: tuple[DatabaseStateObservation, ...] = field(
        default_factory=tuple
    )
    sqlcode_seq: tuple[SqlOperationObservation, ...] = field(
        default_factory=tuple
    )
    sqlstate_seq: tuple[SqlOperationObservation, ...] = field(
        default_factory=tuple
    )
    null_indicator_seq: tuple[NullIndicatorObservation, ...] = field(
        default_factory=tuple
    )
    transaction_state: tuple[TransactionObservation, ...] = field(
        default_factory=tuple
    )
    file_status_seq: tuple[FileStatusObservation, ...] = field(
        default_factory=tuple
    )
    cics_state: tuple[CicsStateObservation, ...] = field(
        default_factory=tuple
    )
    batch_state: tuple[BatchStateObservation, ...] = field(
        default_factory=tuple
    )
    observed_at: str = ""
    encoding: Encoding = field(default_factory=lambda: Encoding(
        source_codepage="UTF-8",
        java_charset="UTF-8",
    ))
    content_hash: str = field(init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.run_id, str) or not self.run_id:
            raise ValueError("run_id must be a non-empty string")
        if not isinstance(self.workload_id, str) or not self.workload_id:
            raise ValueError("workload_id must be a non-empty string")
        if not isinstance(self.exit_code, int):
            raise TypeError("exit_code must be an int")
        if not isinstance(self.stdout, str):
            raise TypeError("stdout must be a str (no truncation in V2)")
        if not isinstance(self.stderr, str):
            raise TypeError("stderr must be a str")
        object.__setattr__(
            self, "content_hash", self._compute_content_hash()
        )

    def _compute_content_hash(self) -> str:
        d = self.to_dict()
        d.pop("content_hash", None)
        text = json.dumps(
            d, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
            default=_json_default,
        )
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "workload_id": self.workload_id,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "output_files": [
                {
                    "path": o.path,
                    "mode": o.mode.value,
                    "content": o.content,
                    "size_bytes": o.size_bytes,
                    "content_hash": o.content_hash,
                }
                for o in self.output_files
            ],
            "db_state": [
                {
                    "table": d.table,
                    "row_count": d.row_count,
                    "rows": [list(r) for r in d.rows],
                    "columns": list(d.columns),
                }
                for d in self.db_state
            ],
            "sqlcode_seq": [
                {
                    "operation_index": s.operation_index,
                    "sqlcode": s.sqlcode,
                    "sqlstate": s.sqlstate,
                    "row_count": s.row_count,
                    "operation": s.operation,
                }
                for s in self.sqlcode_seq
            ],
            "sqlstate_seq": [
                {
                    "operation_index": s.operation_index,
                    "sqlcode": s.sqlcode,
                    "sqlstate": s.sqlstate,
                    "row_count": s.row_count,
                    "operation": s.operation,
                }
                for s in self.sqlstate_seq
            ],
            "null_indicator_seq": [
                {
                    "call_site": n.call_site,
                    "host_var": n.host_var,
                    "indicator": n.indicator,
                }
                for n in self.null_indicator_seq
            ],
            "transaction_state": [
                {
                    "boundary_index": t.boundary_index,
                    "committed": t.committed,
                    "isolation": t.isolation,
                }
                for t in self.transaction_state
            ],
            "file_status_seq": [
                {
                    "operation_index": f.operation_index,
                    "path": f.path,
                    "status": f.status,
                    "operation": f.operation,
                }
                for f in self.file_status_seq
            ],
            "cics_state": [
                {
                    "boundary_index": c.boundary_index,
                    "channel": c.channel,
                    "commarea_summary_hash": c.commarea_summary_hash,
                    "resp": c.resp,
                    "resp2": c.resp2,
                }
                for c in self.cics_state
            ],
            "batch_state": [
                {
                    "step_index": b.step_index,
                    "step_name": b.step_name,
                    "exit_status": b.exit_status,
                    "read_count": b.read_count,
                    "write_count": b.write_count,
                    "skip_count": b.skip_count,
                    "commit_count": b.commit_count,
                }
                for b in self.batch_state
            ],
            "observed_at": self.observed_at,
            "encoding": {
                "source_codepage": self.encoding.source_codepage,
                "java_charset": self.encoding.java_charset,
                "record_encoding": self.encoding.record_encoding,
                "numeric_encoding": self.encoding.numeric_encoding,
                "signed_encoding": self.encoding.signed_encoding,
            },
        }

    def to_canonical_json(self) -> str:
        d = self.to_dict()
        d["content_hash"] = self.content_hash
        return json.dumps(
            d,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            default=_json_default,
        )


def _json_default(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    raise TypeError(
        f"Object of type {type(value).__name__} is not JSON serializable"
    )


__all__ = [
    "DIM_EXIT_CODE",
    "DIM_STDOUT",
    "DIM_STDERR",
    "DIM_OUTPUT_FILES",
    "DIM_DB_STATE",
    "DIM_SQLCODE_SEQ",
    "DIM_SQLSTATE_SEQ",
    "DIM_NULL_INDICATOR_SEQ",
    "DIM_TRANSACTION_STATE",
    "DIM_FILE_STATUS_SEQ",
    "DIM_CICS_STATE",
    "DIM_BATCH_STATE",
    "ALL_DIMENSIONS",
    "OutputFileMode",
    "OutputFileObservation",
    "DatabaseStateObservation",
    "SqlOperationObservation",
    "NullIndicatorObservation",
    "TransactionObservation",
    "FileStatusObservation",
    "CicsStateObservation",
    "BatchStateObservation",
    "Encoding",
    "Observation",
]
