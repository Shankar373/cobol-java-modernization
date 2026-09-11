"""modernize_v2.verification — V2 differential verification data model.

Phase 2A: Observation, Verdict, VerificationContract.

The actual comparator is implemented in Phase 2J. This module
establishes the data model that the comparator and the evidence
store (Phase 2K) will consume.
"""

from __future__ import annotations

from .observation import (
    Observation,
    OutputFileObservation,
    DatabaseStateObservation,
    SqlOperationObservation,
    NullIndicatorObservation,
    TransactionObservation,
    FileStatusObservation,
    CicsStateObservation,
    BatchStateObservation,
    Encoding,
)
from .verdict import (
    ComparisonStatus,
    DimensionResult,
    DimensionStatus,
    ComparisonResult,
    Verdict,
    compute_overall_status,
    RESERVED_STATUSES,
)
from .contract import (
    VerificationContract,
    ComparisonMode,
    RequiredDimensions,
    SeedDeclaration,
    ArtifactExpectation,
    ContractValidationError,
    default_contract,
)

__all__ = [
    "Observation",
    "OutputFileObservation",
    "DatabaseStateObservation",
    "SqlOperationObservation",
    "NullIndicatorObservation",
    "TransactionObservation",
    "FileStatusObservation",
    "CicsStateObservation",
    "BatchStateObservation",
    "Encoding",
    "ComparisonStatus",
    "DimensionStatus",
    "DimensionResult",
    "ComparisonResult",
    "Verdict",
    "compute_overall_status",
    "RESERVED_STATUSES",
    "VerificationContract",
    "ComparisonMode",
    "RequiredDimensions",
    "SeedDeclaration",
    "ArtifactExpectation",
    "ContractValidationError",
    "default_contract",
]
