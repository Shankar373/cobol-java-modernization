"""Diagnostic model for the V2 architecture.

A diagnostic is an immutable record of a problem, a warning, or
informational finding produced during IR construction, analysis,
generation, or verification.

Diagnostics are append-safe: once created, a Diagnostic instance
is frozen and cannot be mutated. Collections of diagnostics grow
by append; they are never edited in place.

The architecture (§20 of docs/PHASE_2_ARCHITECTURE_V2.md) requires
that:

    * Unsupported features surface as ERROR diagnostics.
    * Diagnostics must not silently disappear.
    * Diagnostic serialization must be deterministic so that the
      evidence store in Phase 2K can re-verify them.

Severity, kind, and span are first-class. Workload identity is
preserved so a diagnostic produced during workload W can be
traced back to W even after several runs.

The module is pure: no IO, no env, no clock. ``observed_at`` is
intentionally *not* a wall-clock timestamp; it is a logical
observation epoch that the calling pipeline sets. For tests the
caller can pass a fixed value.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Final, Mapping


# ------------------------------------------------------------------
# Severity
# ------------------------------------------------------------------


class DiagnosticSeverity(str, Enum):
    """Diagnostic severity.

    ERROR blocks the migration from being reported as a success.
    WARNING does not block but is surfaced in the report and the
    evidence file.
    INFO is informational; it is preserved but does not change
    the verdict.
    """

    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"

    @property
    def is_blocking(self) -> bool:
        return self is DiagnosticSeverity.ERROR


# ------------------------------------------------------------------
# Kind
# ------------------------------------------------------------------


class DiagnosticKind(str, Enum):
    """Diagnostic kind.

    The kinds are the V2 vocabulary for the categories a diagnostic
    can fall into. Adding a new kind is a non-breaking change;
    renaming or removing a kind is a breaking change.
    """

    UNSUPPORTED_FEATURE = "UNSUPPORTED_FEATURE"
    UNRESOLVED_SYMBOL = "UNRESOLVED_SYMBOL"
    TYPE_MISMATCH = "TYPE_MISMATCH"
    REDEFINES_OVERLAP = "REDEFINES_OVERLAP"
    ODO_OUT_OF_BOUNDS = "ODO_OUT_OF_BOUNDS"
    PARSER_RECOVERY = "PARSER_RECOVERY"
    INVALID_SOURCE = "INVALID_SOURCE"
    INVALID_CONFIGURATION = "INVALID_CONFIGURATION"
    ENVIRONMENT_BLOCKED = "ENVIRONMENT_BLOCKED"
    CAPABILITY_MISMATCH = "CAPABILITY_MISMATCH"

    @property
    def is_capability_error(self) -> bool:
        """Whether the kind represents a capability-class error.

        Capability-class errors block the verdict from becoming
        ``PASS``/``VERIFIED``. UNSUPPORTED_FEATURE and
        CAPABILITY_MISMATCH are always capability errors.
        """
        return self in _CAPABILITY_ERROR_KINDS


_CAPABILITY_ERROR_KINDS: Final[frozenset[DiagnosticKind]] = frozenset({
    DiagnosticKind.UNSUPPORTED_FEATURE,
    DiagnosticKind.CAPABILITY_MISMATCH,
})


# ------------------------------------------------------------------
# Source span
# ------------------------------------------------------------------


@dataclass(frozen=True)
class SourcePosition:
    """A single source position (line, column, byte offset)."""

    line: int
    column: int
    byte_offset: int

    def __post_init__(self) -> None:
        if self.line < 1:
            raise ValueError(f"line must be >= 1, got {self.line}")
        if self.column < 0:
            raise ValueError(f"column must be >= 0, got {self.column}")
        if self.byte_offset < 0:
            raise ValueError(
                f"byte_offset must be >= 0, got {self.byte_offset}"
            )


@dataclass(frozen=True)
class SourceSpan:
    """A range in a source file.

    The span is anchored on a canonical source path (relative,
    normalized, lowercased). The start position is inclusive; the
    end position is exclusive. An empty span has start == end.
    """

    canonical_path: str
    start: SourcePosition
    end: SourcePosition

    def __post_init__(self) -> None:
        if not isinstance(self.canonical_path, str):
            raise TypeError("canonical_path must be a string")
        if not self.canonical_path:
            raise ValueError("canonical_path must be non-empty")
        if (
            self.end.line < self.start.line
            or (
                self.end.line == self.start.line
                and self.end.column < self.start.column
            )
        ):
            raise ValueError(
                f"span end {self.end} precedes start {self.start}"
            )


# ------------------------------------------------------------------
# Diagnostic
# ------------------------------------------------------------------


_DIAGNOSTIC_ID_NAMESPACE: Final[str] = "D"


def _diagnostic_id(
    severity: DiagnosticSeverity,
    kind: DiagnosticKind,
    span: SourceSpan | None,
    workload_id: str | None,
    message: str,
    related_ids: tuple[str, ...],
) -> str:
    """Compute a deterministic 26-char diagnostic id.

    The id is Crockford base32 of the SHA-256 prefix of the
    canonical JSON of the diagnostic's identity-defining fields.
    External format is identical to node ids but the namespace
    is "D" (Diagnostic) instead of "N" (Node).
    """
    payload = {
        "ns": _DIAGNOSTIC_ID_NAMESPACE,
        "severity": severity.value,
        "kind": kind.value,
        "span": (
            None
            if span is None
            else {
                "path": span.canonical_path,
                "start_line": span.start.line,
                "start_col": span.start.column,
                "start_byte": span.start.byte_offset,
                "end_line": span.end.line,
                "end_col": span.end.column,
                "end_byte": span.end.byte_offset,
            }
        ),
        "workload_id": workload_id,
        "message": message,
        "related": list(related_ids),
    }
    text = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    value = int.from_bytes(digest[:16], "big")
    # 26 chars * 5 bits/char = 130 bits total. The namespace
    # prefix uses 5 bits, leaving 125 bits for the body.
    body_chars = 25
    body_bits = body_chars * 5
    mask = (1 << body_bits) - 1
    encoded = value & mask
    alphabet = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
    body_chars_list = ["0"] * body_chars
    for i in range(body_chars - 1, -1, -1):
        body_chars_list[i] = alphabet[encoded & 0x1F]
        encoded >>= 5
    return _DIAGNOSTIC_ID_NAMESPACE + "".join(body_chars_list)


@dataclass(frozen=True)
class Diagnostic:
    """An immutable diagnostic record.

    Diagnostics are produced by every V2 phase (lexer, parser,
    analyzer, generator, comparator) and are accumulated in
    append-only collections.

    An ``UNSUPPORTED_FEATURE`` diagnostic with ``ERROR`` severity
    prevents the migration verdict from becoming ``PASS``. There
    is no path in V2 that downgrades an ``ERROR`` to a warning
    or a comment.
    """

    severity: DiagnosticSeverity
    kind: DiagnosticKind
    message: str
    span: SourceSpan | None = None
    workload_id: str | None = None
    related_ids: tuple[str, ...] = field(default_factory=tuple)
    diagnostic_id: str = field(init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.message, str) or not self.message:
            raise ValueError("diagnostic message must be a non-empty string")
        # We must compute the id *after* dataclass __init__ has
        # set the other fields. field(init=False) plus __post_init__
        # is the standard idiom for that.
        object.__setattr__(
            self,
            "diagnostic_id",
            _diagnostic_id(
                self.severity,
                self.kind,
                self.span,
                self.workload_id,
                self.message,
                self.related_ids,
            ),
        )
        if len(self.diagnostic_id) != 26:
            raise AssertionError(
                f"diagnostic id must be 26 chars, got {self.diagnostic_id!r}"
            )

    @property
    def is_blocking(self) -> bool:
        return self.severity.is_blocking

    @property
    def is_capability_error(self) -> bool:
        return self.kind.is_capability_error

    def to_dict(self) -> dict[str, Any]:
        """Return a deterministic JSON-serializable dict."""
        return {
            "diagnostic_id": self.diagnostic_id,
            "severity": self.severity.value,
            "kind": self.kind.value,
            "message": self.message,
            "span": (
                None
                if self.span is None
                else {
                    "canonical_path": self.span.canonical_path,
                    "start": {
                        "line": self.span.start.line,
                        "column": self.span.start.column,
                        "byte_offset": self.span.start.byte_offset,
                    },
                    "end": {
                        "line": self.span.end.line,
                        "column": self.span.end.column,
                        "byte_offset": self.span.end.byte_offset,
                    },
                }
            ),
            "workload_id": self.workload_id,
            "related_ids": list(self.related_ids),
        }

    def to_canonical_json(self) -> str:
        """Deterministic JSON serialization for evidence storage."""
        return json.dumps(
            self.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Diagnostic":
        """Reconstruct a Diagnostic from a dict.

        The reconstruction is the inverse of ``to_dict`` and is
        used by the evidence re-verifier (Phase 2K). It is a
        best-effort round-trip: it does not check that the
        computed ``diagnostic_id`` matches ``data["diagnostic_id"]``
        because the field is computed on construction.
        """
        sev = DiagnosticSeverity(data["severity"])
        kind = DiagnosticKind(data["kind"])
        span_data = data.get("span")
        if span_data is None:
            span = None
        else:
            span = SourceSpan(
                canonical_path=span_data["canonical_path"],
                start=SourcePosition(
                    line=span_data["start"]["line"],
                    column=span_data["start"]["column"],
                    byte_offset=span_data["start"]["byte_offset"],
                ),
                end=SourcePosition(
                    line=span_data["end"]["line"],
                    column=span_data["end"]["column"],
                    byte_offset=span_data["end"]["byte_offset"],
                ),
            )
        return cls(
            severity=sev,
            kind=kind,
            message=data["message"],
            span=span,
            workload_id=data.get("workload_id"),
            related_ids=tuple(data.get("related_ids", ())),
        )


def diagnostics_to_canonical_json(
    diagnostics: tuple[Diagnostic, ...] | list[Diagnostic],
) -> str:
    """Serialize a collection of diagnostics deterministically.

    The list is sorted by ``diagnostic_id`` before serialization
    so that the same set of diagnostics produces the same JSON
    regardless of the order they were appended in.
    """
    items = sorted(diagnostics, key=lambda d: d.diagnostic_id)
    return json.dumps(
        [d.to_dict() for d in items],
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


__all__ = [
    "DiagnosticSeverity",
    "DiagnosticKind",
    "SourcePosition",
    "SourceSpan",
    "Diagnostic",
    "diagnostics_to_canonical_json",
]
