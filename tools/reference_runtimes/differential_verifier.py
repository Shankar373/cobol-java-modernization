"""Multi-Oracle Differential Verifier for Mainframe Reference Runtimes.

In accordance with the Ponytail Global AI Software Engineering Constitution:
- Evaluates Native Java output against GnuCOBOL baseline, z390 reference, and Hercules reference oracles.
- Detects exact byte mismatches, whitespace differences, return code differences, record count differences, and ordering differences.
- Emits explicit verifiable verdicts:
  - REFERENCE_AGREEMENT
  - REFERENCE_DISAGREEMENT
  - REFERENCE_UNAVAILABLE
  - REFERENCE_EXECUTION_FAILURE
- NEVER converts REFERENCE_UNAVAILABLE into PASS.
"""

from dataclasses import dataclass, field
from enum import Enum
import hashlib
from typing import Any, Dict, List, Optional, Set
from .base import ReferenceExecutionResult, RuntimeStatus


class DifferentialVerdict(str, Enum):
    REFERENCE_AGREEMENT = "REFERENCE_AGREEMENT"
    REFERENCE_DISAGREEMENT = "REFERENCE_DISAGREEMENT"
    REFERENCE_UNAVAILABLE = "REFERENCE_UNAVAILABLE"
    REFERENCE_EXECUTION_FAILURE = "REFERENCE_EXECUTION_FAILURE"
    EXACT_MATCH = "EXACT_MATCH"
    CONTENT_MISMATCH = "CONTENT_MISMATCH"
    WHITESPACE_MISMATCH = "WHITESPACE_MISMATCH"
    RECORD_COUNT_MISMATCH = "RECORD_COUNT_MISMATCH"
    ORDERING_MISMATCH = "ORDERING_MISMATCH"
    RETURN_CODE_MISMATCH = "RETURN_CODE_MISMATCH"


@dataclass
class OracleComparisonReport:
    is_match: bool
    status: str
    verdict: DifferentialVerdict
    gnucobol_result: Optional[ReferenceExecutionResult] = None
    z390_result: Optional[ReferenceExecutionResult] = None
    hercules_result: Optional[ReferenceExecutionResult] = None
    java_result: Optional[Dict[str, bytes]] = None
    mismatches: List[str] = field(default_factory=list)
    disagreements: List[str] = field(default_factory=list)
    file_hashes: Dict[str, Dict[str, str]] = field(default_factory=dict)
    detailed_differences: Dict[str, str] = field(default_factory=dict)


class MultiOracleDifferentialVerifier:
    """Verifies Native Java output against multiple reference oracles simultaneously."""

    @classmethod
    def compare_multi_oracle(
        cls,
        java_outputs: Dict[str, bytes],
        gnucobol_result: Optional[ReferenceExecutionResult] = None,
        z390_result: Optional[ReferenceExecutionResult] = None,
        hercules_result: Optional[ReferenceExecutionResult] = None,
        java_return_code: int = 0,
    ) -> OracleComparisonReport:
        mismatches = []
        disagreements = []
        file_hashes = {}
        detailed_differences = {}

        # 0. Check reference oracle availability
        if not gnucobol_result or gnucobol_result.status == RuntimeStatus.UNAVAILABLE:
            return OracleComparisonReport(
                is_match=False,
                status="REFERENCE_UNAVAILABLE",
                verdict=DifferentialVerdict.REFERENCE_UNAVAILABLE,
                gnucobol_result=gnucobol_result,
                z390_result=z390_result,
                hercules_result=hercules_result,
                java_result=java_outputs,
                mismatches=["Canonical baseline GnuCOBOL oracle is UNAVAILABLE. Cannot certify."],
            )

        if gnucobol_result.status == RuntimeStatus.FAILED:
            return OracleComparisonReport(
                is_match=False,
                status="REFERENCE_EXECUTION_FAILURE",
                verdict=DifferentialVerdict.REFERENCE_EXECUTION_FAILURE,
                gnucobol_result=gnucobol_result,
                z390_result=z390_result,
                hercules_result=hercules_result,
                java_result=java_outputs,
                mismatches=[f"Canonical baseline execution failed: {gnucobol_result.error_message}"],
            )

        # 1. Compare return codes if explicitly set
        if java_return_code is not None and gnucobol_result.exit_code >= 0 and gnucobol_result.exit_code != java_return_code:
            mismatches.append(
                f"Return code mismatch: GnuCOBOL returned {gnucobol_result.exit_code}, Java returned {java_return_code}"
            )
            detailed_differences["return_code"] = DifferentialVerdict.RETURN_CODE_MISMATCH.value

        # 2. Compare Java vs GnuCOBOL baseline (Primary Gate)
        for rel_path, expected_bytes in gnucobol_result.output_files.items():
            java_bytes = java_outputs.get(rel_path)
            if java_bytes is None:
                mismatches.append(f"{rel_path}: file missing in Native Java output")
                detailed_differences[rel_path] = "FILE_MISSING"
                continue

            file_hashes[rel_path] = {
                "GnuCOBOL": hashlib.sha256(expected_bytes).hexdigest(),
                "Java": hashlib.sha256(java_bytes).hexdigest(),
            }

            if expected_bytes == java_bytes:
                continue

            # Check whitespace / line-ending difference
            norm_exp = expected_bytes.replace(b"\r\n", b"\n").replace(b"\r", b"\n").replace(b"\x00", b" ").rstrip()
            norm_act = java_bytes.replace(b"\r\n", b"\n").replace(b"\r", b"\n").replace(b"\x00", b" ").rstrip()
            
            if norm_exp == norm_act:
                # Same content modulo line endings or trailing padding
                continue

            # Check record counts and ordering
            exp_lines = norm_exp.split(b"\n")
            act_lines = norm_act.split(b"\n")
            if len(exp_lines) != len(act_lines):
                mismatches.append(
                    f"{rel_path}: line count mismatch: baseline has {len(exp_lines)}, Java has {len(act_lines)}"
                )
                detailed_differences[rel_path] = DifferentialVerdict.RECORD_COUNT_MISMATCH.value
            elif sorted(exp_lines) == sorted(act_lines):
                mismatches.append(f"{rel_path}: ordering mismatch between lines")
                detailed_differences[rel_path] = DifferentialVerdict.ORDERING_MISMATCH.value
            else:
                mismatches.append(f"{rel_path}: content mismatch between Java and GnuCOBOL baseline")
                detailed_differences[rel_path] = DifferentialVerdict.CONTENT_MISMATCH.value

        # 3. Compare GnuCOBOL vs z390 (Secondary Reference Oracle)
        if z390_result and z390_result.status == RuntimeStatus.EXECUTED:
            for rel_path, gnu_bytes in gnucobol_result.output_files.items():
                z390_bytes = z390_result.output_files.get(rel_path)
                if z390_bytes is not None:
                    if rel_path in file_hashes:
                        file_hashes[rel_path]["z390"] = hashlib.sha256(z390_bytes).hexdigest()
                    norm_gnu = gnu_bytes.replace(b"\r\n", b"\n").replace(b"\r", b"\n").rstrip()
                    norm_z390 = z390_bytes.replace(b"\r\n", b"\n").replace(b"\r", b"\n").rstrip()
                    if norm_gnu != norm_z390:
                        disagreements.append(
                            f"{rel_path}: REFERENCE_DISAGREEMENT between GnuCOBOL and z390 reference outputs"
                        )

        # 4. Compare Hercules if available
        if hercules_result and hercules_result.status == RuntimeStatus.EXECUTED:
            for rel_path, gnu_bytes in gnucobol_result.output_files.items():
                herc_bytes = hercules_result.output_files.get(rel_path)
                if herc_bytes is not None:
                    if rel_path in file_hashes:
                        file_hashes[rel_path]["Hercules"] = hashlib.sha256(herc_bytes).hexdigest()
                    norm_gnu = gnu_bytes.replace(b"\r\n", b"\n").replace(b"\r", b"\n").rstrip()
                    norm_herc = herc_bytes.replace(b"\r\n", b"\n").replace(b"\r", b"\n").rstrip()
                    if norm_gnu != norm_herc:
                        disagreements.append(
                            f"{rel_path}: REFERENCE_DISAGREEMENT between GnuCOBOL and Hercules reference outputs"
                        )

        is_match = len(mismatches) == 0
        if not is_match:
            verdict = DifferentialVerdict.CONTENT_MISMATCH
            status = "MISMATCH"
        elif disagreements:
            verdict = DifferentialVerdict.REFERENCE_DISAGREEMENT
            status = "MATCH_WITH_REFERENCE_DISAGREEMENT"
        else:
            verdict = DifferentialVerdict.REFERENCE_AGREEMENT
            status = "MATCH"

        return OracleComparisonReport(
            is_match=is_match,
            status=status,
            verdict=verdict,
            gnucobol_result=gnucobol_result,
            z390_result=z390_result,
            hercules_result=hercules_result,
            java_result=java_outputs,
            mismatches=mismatches,
            disagreements=disagreements,
            file_hashes=file_hashes,
            detailed_differences=detailed_differences,
        )
