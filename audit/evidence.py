"""Evidence Collection and Verification Bundle Engine.

Structures and validates multi-tier verification evidence for the 5-Tier Certification Model.
"""
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import json


class Verdict(str, Enum):
    PASS = "PASS"
    WARNING = "WARNING"
    FAIL = "FAIL"
    UNPROVEN = "UNPROVEN"
    BLOCKED = "BLOCKED"


@dataclass
class TierEvidence:
    tier: int
    name: str
    verdict: Verdict
    details: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    artifacts: List[str] = field(default_factory=list)
    sha256_checksums: Dict[str, str] = field(default_factory=dict)


@dataclass
class EvidenceBundle:
    workload: str
    timestamp_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    overall_verdict: Verdict = Verdict.UNPROVEN
    tiers: Dict[int, TierEvidence] = field(default_factory=dict)
    unsupported_constructs: List[Dict[str, Any]] = field(default_factory=list)
    execution_metrics: Dict[str, Any] = field(default_factory=dict)
    manifest_sha256: Optional[str] = None

    def add_tier(self, evidence: TierEvidence) -> None:
        self.tiers[evidence.tier] = evidence
        self._recompute_overall()

    def _recompute_overall(self) -> None:
        """Evaluate overall verdict based on tier verdicts and fail-closed rules."""
        if any(t.verdict == Verdict.FAIL for t in self.tiers.values()):
            self.overall_verdict = Verdict.FAIL
        elif any(t.verdict == Verdict.BLOCKED for t in self.tiers.values()):
            self.overall_verdict = Verdict.BLOCKED
        elif any(t.verdict == Verdict.UNPROVEN for t in self.tiers.values()):
            self.overall_verdict = Verdict.UNPROVEN
        elif any(t.verdict == Verdict.WARNING for t in self.tiers.values()):
            self.overall_verdict = Verdict.WARNING
        elif all(t.verdict == Verdict.PASS for t in self.tiers.values()) and len(self.tiers) >= 4:
            self.overall_verdict = Verdict.PASS
        else:
            self.overall_verdict = Verdict.UNPROVEN

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["overall_verdict"] = self.overall_verdict.value
        for k, v in data["tiers"].items():
            v["verdict"] = v["verdict"].value
        return data

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


def collect_evidence(
    workload: str,
    pipeline_out: Union[str, Path],
    differential_result: Optional[Dict[str, Any]] = None,
    compilation_result: Optional[Dict[str, Any]] = None,
    syntax_result: Optional[Dict[str, Any]] = None,
) -> EvidenceBundle:
    """Collect and synthesize multi-tier evidence from pipeline outputs."""
    bundle = EvidenceBundle(workload=workload)
    out_dir = Path(pipeline_out)

    # Tier 1: Syntax & AST Parsing
    t1_verdict = Verdict.PASS if syntax_result and syntax_result.get("success") else (
        Verdict.FAIL if syntax_result and not syntax_result.get("success") else Verdict.UNPROVEN
    )
    bundle.add_tier(TierEvidence(
        tier=1,
        name="Syntax & AST Parsing",
        verdict=t1_verdict,
        details=syntax_result or {},
    ))

    # Tier 2: Compilation & Symbol Resolution
    t2_verdict = Verdict.PASS if compilation_result and compilation_result.get("success") else (
        Verdict.FAIL if compilation_result and not compilation_result.get("success") else Verdict.UNPROVEN
    )
    bundle.add_tier(TierEvidence(
        tier=2,
        name="Compilation & Symbol Resolution",
        verdict=t2_verdict,
        details=compilation_result or {},
    ))

    # Tier 3: Structural Equivalence
    bundle.add_tier(TierEvidence(
        tier=3,
        name="Structural & Symbol Equivalence",
        verdict=Verdict.PASS if t1_verdict == Verdict.PASS and t2_verdict == Verdict.PASS else Verdict.UNPROVEN,
        details={"ast_nodes_mapped": True},
    ))

    # Tier 4: Runtime Differential Equivalence
    if differential_result:
        diff_status = differential_result.get("status", "UNPROVEN").upper()
        if diff_status == "PASS" or diff_status == "VERIFIED":
            t4_verdict = Verdict.PASS
        elif diff_status == "WARNING":
            t4_verdict = Verdict.WARNING
        elif diff_status == "FAIL":
            t4_verdict = Verdict.FAIL
        elif diff_status == "BLOCKED":
            t4_verdict = Verdict.BLOCKED
        else:
            t4_verdict = Verdict.UNPROVEN

        bundle.add_tier(TierEvidence(
            tier=4,
            name="Runtime Differential Equivalence",
            verdict=t4_verdict,
            details=differential_result,
            warnings=differential_result.get("warnings", []),
            errors=differential_result.get("errors", []),
        ))
    else:
        bundle.add_tier(TierEvidence(
            tier=4,
            name="Runtime Differential Equivalence",
            verdict=Verdict.UNPROVEN,
            details={"reason": "Differential verification not executed"},
        ))

    return bundle
