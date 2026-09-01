"""Base abstractions for Open-Source Mainframe Reference Runtimes."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import os
from typing import Any, Dict, List, Optional, Set, Tuple


class RuntimeCapability(str, Enum):
    BATCH_COBOL = "BATCH_COBOL"
    VSAM_KSDS = "VSAM_KSDS"
    VSAM_RRDS = "VSAM_RRDS"
    CICS_REST = "CICS_REST"
    EBCDIC_NATIVE = "EBCDIC_NATIVE"
    JCL_JOB = "JCL_JOB"
    SQL_RELATIONAL = "SQL_RELATIONAL"


class RuntimeStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    SKIPPED = "SKIPPED"
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"


@dataclass
class ReferenceExecutionResult:
    runtime_name: str
    status: RuntimeStatus
    exit_code: int = -1
    stdout: str = ""
    stderr: str = ""
    output_files: Dict[str, bytes] = field(default_factory=dict)
    output_hashes: Dict[str, str] = field(default_factory=dict)
    record_counts: Dict[str, int] = field(default_factory=dict)
    duration_seconds: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None

    def calculate_hashes(self) -> None:
        """Compute SHA-256 for all captured output files."""
        for rel_path, content in self.output_files.items():
            self.output_hashes[rel_path] = hashlib.sha256(content).hexdigest()
            self.record_counts[rel_path] = content.count(b"\n")


class ReferenceRuntime(ABC):
    """Abstract interface for all mainframe reference execution oracles."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the reference runtime engine (e.g. 'GnuCOBOL', 'z390', 'Hercules')."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check whether the reference runtime is installed, configured, or containerized."""
        pass

    @abstractmethod
    def supported_capabilities(self) -> Set[RuntimeCapability]:
        """Return the set of mainframe capabilities supported by this runtime."""
        pass

    @abstractmethod
    def validate_environment(self) -> Tuple[bool, str]:
        """Verify that runtime binaries, environment variables, and containers are healthy."""
        pass

    @abstractmethod
    def execute(
        self,
        source_files: Dict[str, str],
        copybooks: Dict[str, str],
        input_files: Dict[str, bytes],
        entry_program: str,
        work_dir: str,
        timeout_seconds: int = 60,
        extra_args: Optional[List[str]] = None,
    ) -> ReferenceExecutionResult:
        """Execute the COBOL/JCL workload in an isolated workspace and capture results."""
        pass
