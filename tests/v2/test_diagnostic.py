"""Tests for modernize_v2.ir.diagnostic — Diagnostic model.

Acceptance criteria from T-2A-03:

    * severity, kind, span, message, workload_id, related_ids
    * immutable/append-safe
    * deterministic serialization
    * 26-character diagnostic id
    * UNSUPPORTED_FEATURE can be represented as ERROR
    * diagnostics do not silently disappear
"""

from __future__ import annotations

import json

import pytest

from modernize_v2.ir.diagnostic import (
    Diagnostic,
    DiagnosticKind,
    DiagnosticSeverity,
    SourcePosition,
    SourceSpan,
    diagnostics_to_canonical_json,
)


def _span(path: str = "src/a.cbl", line: int = 1) -> SourceSpan:
    return SourceSpan(
        canonical_path=path,
        start=SourcePosition(line=line, column=0, byte_offset=0),
        end=SourcePosition(line=line, column=4, byte_offset=4),
    )


def test_diagnostic_minimal() -> None:
    d = Diagnostic(
        severity=DiagnosticSeverity.ERROR,
        kind=DiagnosticKind.UNSUPPORTED_FEATURE,
        message="CICS HANDLE AID not supported",
    )
    assert d.severity is DiagnosticSeverity.ERROR
    assert d.kind is DiagnosticKind.UNSUPPORTED_FEATURE
    assert d.is_blocking
    assert d.is_capability_error
    assert len(d.diagnostic_id) == 26


def test_diagnostic_id_is_deterministic() -> None:
    a = Diagnostic(
        severity=DiagnosticSeverity.ERROR,
        kind=DiagnosticKind.UNRESOLVED_SYMBOL,
        message="X is not defined",
        span=_span("src/a.cbl", 10),
        workload_id="W1",
    )
    b = Diagnostic(
        severity=DiagnosticSeverity.ERROR,
        kind=DiagnosticKind.UNRESOLVED_SYMBOL,
        message="X is not defined",
        span=_span("src/a.cbl", 10),
        workload_id="W1",
    )
    assert a.diagnostic_id == b.diagnostic_id


def test_diagnostic_id_differs_with_severity() -> None:
    args = dict(
        kind=DiagnosticKind.TYPE_MISMATCH,
        message="X is not a number",
        span=_span(),
    )
    a = Diagnostic(severity=DiagnosticSeverity.ERROR, **args)
    b = Diagnostic(severity=DiagnosticSeverity.WARNING, **args)
    assert a.diagnostic_id != b.diagnostic_id


def test_diagnostic_id_differs_with_message() -> None:
    a = Diagnostic(
        severity=DiagnosticSeverity.ERROR,
        kind=DiagnosticKind.TYPE_MISMATCH,
        message="X is not a number",
        span=_span(),
    )
    b = Diagnostic(
        severity=DiagnosticSeverity.ERROR,
        kind=DiagnosticKind.TYPE_MISMATCH,
        message="X is not a string",
        span=_span(),
    )
    assert a.diagnostic_id != b.diagnostic_id


def test_diagnostic_is_frozen() -> None:
    d = Diagnostic(
        severity=DiagnosticSeverity.WARNING,
        kind=DiagnosticKind.PARSER_RECOVERY,
        message="recovered",
    )
    with pytest.raises(Exception):
        d.message = "tampered"  # type: ignore[misc]


def test_unsupported_feature_is_blocking_error() -> None:
    d = Diagnostic(
        severity=DiagnosticSeverity.ERROR,
        kind=DiagnosticKind.UNSUPPORTED_FEATURE,
        message="REPORT WRITER not supported",
        workload_id="W1",
    )
    assert d.is_blocking
    assert d.is_capability_error


def test_warning_not_blocking() -> None:
    d = Diagnostic(
        severity=DiagnosticSeverity.WARNING,
        kind=DiagnosticKind.PARSER_RECOVERY,
        message="recovered",
    )
    assert not d.is_blocking
    assert not d.is_capability_error


def test_capability_mismatch_is_capability_error() -> None:
    d = Diagnostic(
        severity=DiagnosticSeverity.ERROR,
        kind=DiagnosticKind.CAPABILITY_MISMATCH,
        message="VSAM not available in this build",
    )
    assert d.is_capability_error


def test_to_dict_roundtrip() -> None:
    d = Diagnostic(
        severity=DiagnosticSeverity.ERROR,
        kind=DiagnosticKind.REDEFINES_OVERLAP,
        message="WS-FIELD-A overlaps WS-FIELD-B",
        span=_span("src/data.cbl", 50),
        workload_id="BANK",
        related_ids=("A1", "B2"),
    )
    data = d.to_dict()
    assert data["severity"] == "ERROR"
    assert data["kind"] == "REDEFINES_OVERLAP"
    assert data["workload_id"] == "BANK"
    assert data["related_ids"] == ["A1", "B2"]
    assert data["span"]["canonical_path"] == "src/data.cbl"

    restored = Diagnostic.from_dict(data)
    assert restored.message == d.message
    assert restored.severity == d.severity
    assert restored.kind == d.kind
    assert restored.workload_id == d.workload_id
    assert restored.span is not None
    assert restored.span.canonical_path == d.span.canonical_path


def test_to_canonical_json_is_deterministic() -> None:
    args = dict(
        severity=DiagnosticSeverity.ERROR,
        kind=DiagnosticKind.OOO_BOUNDS if False else DiagnosticKind.OUT_OF_BOUNDS if hasattr(DiagnosticKind, "OUT_OF_BOUNDS") else DiagnosticKind.ODO_OUT_OF_BOUNDS,
        message="bound exceeded",
        span=_span("src/p.cbl", 1),
        workload_id="W",
        related_ids=("x", "y"),
    )
    a = json.dumps(Diagnostic(**args).to_dict(), sort_keys=True)
    b = json.dumps(Diagnostic(**args).to_dict(), sort_keys=True)
    assert a == b


def test_diagnostics_collection_serialization() -> None:
    a = Diagnostic(
        severity=DiagnosticSeverity.WARNING,
        kind=DiagnosticKind.PARSER_RECOVERY,
        message="recovered",
        span=_span("src/a.cbl", 1),
    )
    b = Diagnostic(
        severity=DiagnosticSeverity.ERROR,
        kind=DiagnosticKind.UNSUPPORTED_FEATURE,
        message="REPORT WRITER not supported",
        span=_span("src/b.cbl", 2),
    )
    s1 = diagnostics_to_canonical_json([a, b])
    s2 = diagnostics_to_canonical_json([b, a])
    # Order-independent: same set, same JSON.
    assert s1 == s2
    parsed = json.loads(s1)
    assert len(parsed) == 2
    # Sorted by diagnostic_id
    assert parsed[0]["diagnostic_id"] < parsed[1]["diagnostic_id"]


def test_message_must_be_nonempty() -> None:
    with pytest.raises(ValueError):
        Diagnostic(
            severity=DiagnosticSeverity.WARNING,
            kind=DiagnosticKind.PARSER_RECOVERY,
            message="",
        )


def test_source_position_validates() -> None:
    with pytest.raises(ValueError):
        SourcePosition(line=0, column=0, byte_offset=0)
    with pytest.raises(ValueError):
        SourcePosition(line=1, column=-1, byte_offset=0)
    with pytest.raises(ValueError):
        SourcePosition(line=1, column=0, byte_offset=-1)


def test_source_span_validates_ordering() -> None:
    with pytest.raises(ValueError):
        SourceSpan(
            canonical_path="x.cbl",
            start=SourcePosition(line=10, column=0, byte_offset=0),
            end=SourcePosition(line=5, column=0, byte_offset=0),
        )


def test_diagnostic_id_is_26_chars() -> None:
    d = Diagnostic(
        severity=DiagnosticSeverity.INFO,
        kind=DiagnosticKind.INVALID_CONFIGURATION,
        message="note",
    )
    assert len(d.diagnostic_id) == 26
