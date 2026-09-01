"""Open-Source Mainframe Reference Runtimes & Oracle Package.

Provides isolated adapters, capability detection, EBCDIC charset/collation,
and multi-oracle differential verification for mainframe modernized workloads.
"""

from .base import (
    ReferenceRuntime,
    ReferenceExecutionResult,
    RuntimeCapability,
    RuntimeStatus,
)
from .gnu_cobol import GnuCobolReferenceRunner
from .z390.runner import Z390ReferenceRunner
from .hercules.runner import HerculesReferenceRunner
from .database import DatabaseReferenceRuntime, DatabaseValidationMode
from .ebcdic.charset import CobolCharsetAdapter
from .ebcdic.collation import CobolCollationStrategy, CollationMode
from .capability_detector import WorkloadCapabilityDetector
from .certification_policy import CertificationPolicy, WorkloadCertificationResult
from .differential_verifier import MultiOracleDifferentialVerifier

__all__ = [
    "ReferenceRuntime",
    "ReferenceExecutionResult",
    "RuntimeCapability",
    "RuntimeStatus",
    "GnuCobolReferenceRunner",
    "Z390ReferenceRunner",
    "HerculesReferenceRunner",
    "DatabaseReferenceRuntime",
    "DatabaseValidationMode",
    "CobolCharsetAdapter",
    "CobolCollationStrategy",
    "CollationMode",
    "WorkloadCapabilityDetector",
    "CertificationPolicy",
    "WorkloadCertificationResult",
    "MultiOracleDifferentialVerifier",
]
