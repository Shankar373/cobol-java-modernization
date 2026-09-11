"""GnuCOBOL Canonical Baseline Reference Runner."""

import os
import shutil
import subprocess
import time
from typing import Dict, List, Optional, Set, Tuple

from .base import (
    ReferenceExecutionResult,
    ReferenceRuntime,
    RuntimeCapability,
    RuntimeStatus,
)


class GnuCobolReferenceRunner(ReferenceRuntime):
    """Canonical GnuCOBOL baseline execution engine."""

    def __init__(self, docker_image: str = "opensourcecobol/opensourcecobol4j:2.0.0"):
        self.docker_image = docker_image

    @property
    def name(self) -> str:
        return "GnuCOBOL"

    def is_available(self) -> bool:
        # Check docker availability or local cobc
        if shutil.which("docker"):
            return True
        if shutil.which("cobc"):
            return True
        return False

    def supported_capabilities(self) -> Set[RuntimeCapability]:
        return {
            RuntimeCapability.BATCH_COBOL,
            RuntimeCapability.SQL_RELATIONAL,
        }

    def validate_environment(self) -> Tuple[bool, str]:
        if shutil.which("docker"):
            try:
                res = subprocess.run(
                    ["docker", "image", "inspect", self.docker_image],
                    capture_output=True,
                    timeout=5,
                )
                if res.returncode == 0:
                    return True, f"Docker image {self.docker_image} is available"
            except Exception:
                pass
            return True, "Docker is available on PATH"
        if shutil.which("cobc"):
            return True, "Native cobc compiler is available on PATH"
        return False, "Neither Docker nor local cobc found on host"

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

        # Execution using local or containerized cobc
        entry_file = os.path.join(src_dir, f"{entry_program}.cob")
        if not os.path.exists(entry_file):
            # Try to match any file with entry_program
            candidates = [f for f in os.listdir(src_dir) if entry_program.lower() in f.lower()]
            if candidates:
                entry_file = os.path.join(src_dir, candidates[0])

        exe_path = os.path.join(work_dir, "prog.exe")
        cobc_cmd = ["cobc", "-x", "-I", cpy_dir, "-o", exe_path, entry_file]

        if shutil.which("docker"):
            # Docker execution
            container_work = "/workspace"
            vol = f"{os.path.abspath(work_dir)}:{container_work}"
            docker_cmd = [
                "docker", "run", "--rm", "-v", vol, "-w", container_work,
                self.docker_image, "bash", "-c",
                f"cobc -x -I cpy -o prog.bin src/{os.path.basename(entry_file)} && ./prog.bin"
            ]
            try:
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
                    metadata={"container": self.docker_image},
                )
            except subprocess.TimeoutExpired:
                return ReferenceExecutionResult(
                    runtime_name=self.name,
                    status=RuntimeStatus.FAILED,
                    exit_code=-1,
                    error_message=f"GnuCOBOL execution timed out after {timeout_seconds}s",
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
        else:
            # Native cobc
            try:
                compile_proc = subprocess.run(cobc_cmd, capture_output=True, text=True, timeout=timeout_seconds)
                if compile_proc.returncode != 0:
                    return ReferenceExecutionResult(
                        runtime_name=self.name,
                        status=RuntimeStatus.FAILED,
                        exit_code=compile_proc.returncode,
                        stdout=compile_proc.stdout,
                        stderr=compile_proc.stderr,
                        error_message="GnuCOBOL compilation failed",
                        duration_seconds=round(time.time() - start_time, 3),
                    )
                run_proc = subprocess.run([exe_path], cwd=work_dir, capture_output=True, text=True, timeout=timeout_seconds)
                res = ReferenceExecutionResult(
                    runtime_name=self.name,
                    status=RuntimeStatus.EXECUTED if run_proc.returncode == 0 else RuntimeStatus.FAILED,
                    exit_code=run_proc.returncode,
                    stdout=run_proc.stdout,
                    stderr=run_proc.stderr,
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

        # Collect output files
        if os.path.exists(out_dir):
            for root, _, files in os.walk(out_dir):
                for fname in files:
                    full_p = os.path.join(root, fname)
                    rel_p = os.path.relpath(full_p, work_dir).replace("\\", "/")
                    with open(full_p, "rb") as fh:
                        res.output_files[rel_p] = fh.read()
        res.calculate_hashes()
        return res
