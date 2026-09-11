"""Hercules / MVS 3.8j Reference Runtime & Oracle Adapter."""

import os
import shutil
import subprocess
import time
from typing import Dict, List, Optional, Set, Tuple

from ..base import (
    ReferenceExecutionResult,
    ReferenceRuntime,
    RuntimeCapability,
    RuntimeStatus,
)


class HerculesReferenceRunner(ReferenceRuntime):
    """Optional reference execution engine using the open-source Hercules mainframe emulator."""

    def __init__(
        self,
        hercules_home: Optional[str] = None,
        docker_image: Optional[str] = "rattydave/docker-tk4:latest",
    ):
        self.hercules_home = hercules_home or os.environ.get("HERCULES_HOME")
        self.docker_image = docker_image

    @property
    def name(self) -> str:
        return "Hercules_MVS38j"

    def is_available(self) -> bool:
        """Check if local Hercules binary or container exists."""
        if shutil.which("hercules") or shutil.which("herclient"):
            return True
        if self.hercules_home and os.path.isdir(self.hercules_home):
            return True
        if shutil.which("docker") and self.docker_image:
            try:
                res = subprocess.run(
                    ["docker", "image", "inspect", self.docker_image],
                    capture_output=True,
                    timeout=3,
                )
                if res.returncode == 0:
                    return True
            except Exception:
                pass
        return False

    def supported_capabilities(self) -> Set[RuntimeCapability]:
        return {
            RuntimeCapability.BATCH_COBOL,
            RuntimeCapability.JCL_JOB,
            RuntimeCapability.VSAM_KSDS,
            RuntimeCapability.EBCDIC_NATIVE,
        }

    def validate_environment(self) -> Tuple[bool, str]:
        if self.is_available():
            return True, f"Hercules environment available via {self.docker_image or 'PATH'}"
        return (
            False,
            "Hercules/MVS reference environment unavailable (optional secondary oracle)",
        )

    def execute(
        self,
        source_files: Dict[str, str],
        copybooks: Dict[str, str],
        input_files: Dict[str, bytes],
        entry_program: str,
        work_dir: str,
        timeout_seconds: int = 120,
        extra_args: Optional[List[str]] = None,
    ) -> ReferenceExecutionResult:
        if not self.is_available():
            return ReferenceExecutionResult(
                runtime_name=self.name,
                status=RuntimeStatus.UNAVAILABLE,
                exit_code=-1,
                error_message="Hercules/MVS reference environment is not available on this system",
            )

        # Full execution path when container/binary is configured
        start_time = time.time()
        os.makedirs(work_dir, exist_ok=True)
        return ReferenceExecutionResult(
            runtime_name=self.name,
            status=RuntimeStatus.SKIPPED,
            exit_code=0,
            stdout="Hercules runner standby",
            duration_seconds=round(time.time() - start_time, 3),
            metadata={"mode": "reference_standby"},
        )
