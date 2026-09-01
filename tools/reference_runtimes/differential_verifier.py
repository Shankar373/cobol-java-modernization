"""Multi-Oracle Differential Verifier for Mainframe Reference Runtimes."""

from dataclasses import dataclass, field
import hashlib
from typing import Any, Dict, List, Optional, Set
from .base import ReferenceExecutionResult, RuntimeStatus


@dataclass
class OracleComparisonReport:
    is_match: bool
    status: str
    gnucobol_result: Optional[ReferenceExecutionResult] = None
    z390_result: Optional[ReferenceExecutionResult] = None
    java_result: Optional[Dict[str, bytes]] = None
    mismatches: List[str] = field(default_factory=list)
    disagreements: List[str] = field(default_factory=list)
    file_hashes: Dict[str, Dict[str, str]] = field(default_factory=dict)


class MultiOracleDifferentialVerifier:
    """Verifies Native Java output against multiple reference oracles simultaneously."""

    @classmethod
    def compare_multi_oracle(
        cls,
        java_outputs: Dict[str, bytes],
        gnucobol_result: Optional[ReferenceExecutionResult] = None,
        z390_result: Optional[ReferenceExecutionResult] = None,
    ) -> OracleComparisonReport:
        mismatches = []
        disagreements = []
        file_hashes = {}

        # 1. Compare Java vs GnuCOBOL baseline (Primary Gate)
        if gnucobol_result and gnucobol_result.status == RuntimeStatus.EXECUTED:
            for rel_path, expected_bytes in gnucobol_result.output_files.items():
                java_bytes = java_outputs.get(rel_path)
                if java_bytes is None:
                    mismatches.append(f"{rel_path}: file missing in Native Java output")
                    continue
                # Normalize line endings and trailing nulls for fair comparison
                norm_exp = expected_bytes.replace(b"\r", b"").replace(b"\x00", b" ").rstrip()
                norm_act = java_bytes.replace(b"\r", b"").replace(b"\x00", b" ").rstrip()
                if norm_exp != norm_act:
                    mismatches.append(f"{rel_path}: content mismatch between Java and GnuCOBOL baseline")

                file_hashes[rel_path] = {
                    "GnuCOBOL": hashlib.sha256(expected_bytes).hexdigest(),
                    "Java": hashlib.sha256(java_bytes).hexdigest(),
                }

        # 2. Compare GnuCOBOL vs z390 (Secondary Reference Oracle)
        if z390_result and z390_result.status == RuntimeStatus.EXECUTED:
            if gnucobol_result and gnucobol_result.status == RuntimeStatus.EXECUTED:
                for rel_path, gnu_bytes in gnucobol_result.output_files.items():
                    z390_bytes = z390_result.output_files.get(rel_path)
                    if z390_bytes is not None:
                        if rel_path in file_hashes:
                            file_hashes[rel_path]["z390"] = hashlib.sha256(z390_bytes).hexdigest()
                        norm_gnu = gnu_bytes.replace(b"\r", b"").rstrip()
                        norm_z390 = z390_bytes.replace(b"\r", b"").rstrip()
                        if norm_gnu != norm_z390:
                            disagreements.append(
                                f"{rel_path}: REFERENCE_DISAGREEMENT between GnuCOBOL and z390 reference outputs"
                            )

        is_match = len(mismatches) == 0
        status = "MATCH" if is_match else "MISMATCH"
        if disagreements and is_match:
            status = "MATCH_WITH_REFERENCE_DISAGREEMENT"

        return OracleComparisonReport(
            is_match=is_match,
            status=status,
            gnucobol_result=gnucobol_result,
            z390_result=z390_result,
            java_result=java_outputs,
            mismatches=mismatches,
            disagreements=disagreements,
            file_hashes=file_hashes,
        )
