"""z390 Mainframe Reference Runtime & Oracle Adapter."""

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


class Z390ReferenceRunner(ReferenceRuntime):
    """Reference execution engine using the open-source z390 mainframe emulator."""

    def __init__(
        self,
        z390_home: Optional[str] = None,
        docker_image: Optional[str] = "z390development/z390:latest",
    ):
        self.z390_home = z390_home or os.environ.get("Z390_HOME")
        self.docker_image = docker_image

    @property
    def name(self) -> str:
        return "z390"

    def is_available(self) -> bool:
        """Check if local z390 installation or container exists."""
        if self.z390_home and os.path.isdir(self.z390_home):
            jar_path = os.path.join(self.z390_home, "z390.jar")
            if os.path.isfile(jar_path):
                return True
        if shutil.which("exec390") or shutil.which("z390"):
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
            RuntimeCapability.VSAM_KSDS,
            RuntimeCapability.VSAM_RRDS,
            RuntimeCapability.CICS_REST,
            RuntimeCapability.EBCDIC_NATIVE,
        }

    def validate_environment(self) -> Tuple[bool, str]:
        if self.is_available():
            if self.z390_home:
                return True, f"Local z390 installation found at {self.z390_home}"
            return True, f"z390 runtime available via {self.docker_image or 'PATH'}"
        return (
            False,
            "z390 reference environment unavailable (set Z390_HOME or pull z390 container)",
        )

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
        if not self.is_available():
            return ReferenceExecutionResult(
                runtime_name=self.name,
                status=RuntimeStatus.UNAVAILABLE,
                exit_code=-1,
                error_message="z390 reference environment is not available on this system",
            )

        start_time = time.time()
        os.makedirs(work_dir, exist_ok=True)
        src_dir = os.path.join(work_dir, "src")
        cpy_dir = os.path.join(work_dir, "cpy")
        in_dir = os.path.join(work_dir, "data", "in")
        out_dir = os.path.join(work_dir, "data", "out")
        os.makedirs(src_dir, exist_ok=True)
        os.makedirs(cpy_dir, exist_ok=True)
        os.makedirs(in_dir, exist_ok=True)
        os.makedirs(out_dir, exist_ok=True)

        for name, content in source_files.items():
            path = os.path.join(src_dir, os.path.basename(name))
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

        for name, content in copybooks.items():
            path = os.path.join(cpy_dir, os.path.basename(name))
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

        for name, data in input_files.items():
            path = os.path.join(in_dir, os.path.basename(name))
            with open(path, "wb") as f:
                f.write(data)

        entry_file = os.path.join(src_dir, f"{entry_program}.cob")
        if not os.path.exists(entry_file):
            candidates = [f for f in os.listdir(src_dir) if entry_program.lower() in f.lower()]
            if candidates:
                entry_file = os.path.join(src_dir, candidates[0])

        # Execution using local z390 JVM or Docker container
        try:
            if self.z390_home and os.path.isfile(os.path.join(self.z390_home, "z390.jar")):
                cmd = [
                    "java",
                    "-jar",
                    os.path.join(self.z390_home, "z390.jar"),
                    f"zcobol({os.path.basename(entry_file)})",
                    f"syslib({cpy_dir})",
                ]
                proc = subprocess.run(
                    cmd,
                    cwd=work_dir,
                    capture_output=True,
                    text=True,
                    timeout=timeout_seconds,
                )
            else:
                # Docker invocation
                container_work = "/workspace"
                vol = f"{os.path.abspath(work_dir)}:{container_work}"
                docker_cmd = [
                    "docker",
                    "run",
                    "--rm",
                    "-v",
                    vol,
                    "-w",
                    container_work,
                    self.docker_image,
                    "z390",
                    f"src/{os.path.basename(entry_file)}",
                ]
                proc = subprocess.run(
                    docker_cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout_seconds,
                )

            duration = time.time() - start_time
            res = ReferenceExecutionResult(
                runtime_name=self.name,
                status=RuntimeStatus.EXECUTED if proc.returncode == 0 else RuntimeStatus.FAILED,
                exit_code=proc.returncode,
                stdout=proc.stdout,
                stderr=proc.stderr,
                duration_seconds=round(duration, 3),
                metadata={"engine": "z390_zcobol", "entry": entry_program},
            )
        except subprocess.TimeoutExpired:
            return ReferenceExecutionResult(
                runtime_name=self.name,
                status=RuntimeStatus.FAILED,
                exit_code=-1,
                error_message=f"z390 execution timed out after {timeout_seconds}s",
                duration_seconds=round(time.time() - start_time, 3),
            )
        except Exception as e:
            return ReferenceExecutionResult(
                runtime_name=self.name,
                status=RuntimeStatus.FAILED,
                exit_code=-1,
                error_message=str(e),
                duration_seconds=round(time.time() - start_time, 3),
            )

        # Collect output datasets
        if os.path.exists(out_dir):
            for root, _, files in os.walk(out_dir):
                for fname in files:
                    full_p = os.path.join(root, fname)
                    rel_p = os.path.relpath(full_p, work_dir).replace("\\", "/")
                    with open(full_p, "rb") as fh:
                        res.output_files[rel_p] = fh.read()
        res.calculate_hashes()
        return res
