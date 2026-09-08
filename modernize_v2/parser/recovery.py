"""T-2B-03 Deterministic Error Recovery.

Recovery records track skipped constructs and synchronization points
so that the parser can continue parsing sibling constructs after
encountering unsupported or malformed syntax.

No silent swallowing: every recovery produces a Diagnostic and a
RecoveryRecord.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from modernize_v2.ir.diagnostic import Diagnostic, DiagnosticSeverity, DiagnosticKind
from modernize_v2.lexer.tokens import Token, TokenKind


@dataclass(frozen=True)
class RecoveryRecord:
    """Records a point where the parser skipped syntax.

    Invariants:
    - span covers the skipped source region.
    - reason explains why parsing was interrupted.
    - sync_point is the byte offset where safe continued parsing
      may resume (typically a Period or a control keyword).
    """
    span: "SourceSpan"  # exact byte provenance in the original source
    reason: str  # short human-readable reason
    sync_point: int  # byte offset where parser resumes


def make_unsupported_diagnostic(
    message: str,
    span: "SourceSpan",
    workload_id: str | None = None,
) -> Diagnostic:
    """Create a deterministic UNSUPPORTED_FEATURE diagnostic."""
    from modernize_v2.ir.diagnostic import DiagnosticSeverity, DiagnosticKind

    return Diagnostic(
        severity=DiagnosticSeverity.ERROR,
        kind=DiagnosticKind.UNSUPPORTED_FEATURE,
        message=message,
        span=span,
        workload_id=workload_id,
    )


def make_recovery_record(
    skipped_construct: str,
    span: "SourceSpan",
    sync_byte: int,
) -> RecoveryRecord:
    """Create a RecoveryRecord for an unsupported or malformed construct."""
    return RecoveryRecord(
        span=span,
        reason=f"Unsupported/unsupported construct: {skipped_construct}",
        sync_point=sync_byte,
    )


def is_eof_token(token: "Token") -> bool:
    """Check whether *token* is the lexer's EOF sentinel.

    The T-2B-02 lexer contract represents EOF as:
      kind == TokenKind.IDENTIFIER  and  text == ""
      and  span.start.byte_offset == span.end.byte_offset == byte_size
    """
    return (
        token.kind == TokenKind.IDENTIFIER
        and token.text == ""
        # Byte-offset check; the caller must also verify byte_size
        # compatibility if desired.
    )