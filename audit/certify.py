"""Automated 5-Tier Certification Engine.

Evaluates evidence bundles against the 5-Tier Certification Model and generates
cryptographically verifiable scorecards (certification_scorecard.json) and markdown reports.
"""
from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .evidence import EvidenceBundle, TierEvidence, Verdict
from .manifest import generate_manifest


def evaluate_certification(bundle: EvidenceBundle) -> Dict[str, Any]:
    """Evaluate certification status and grade an evidence bundle."""
    tier_scores = {}
    total_tiers = 5
    passed_tiers = 0
    warnings: List[str] = []
    blockers: List[str] = []

    for tier_num in range(1, total_tiers + 1):
        tier_ev = bundle.tiers.get(tier_num)
        if not tier_ev:
            tier_scores[f"tier_{tier_num}"] = {
                "verdict": Verdict.UNPROVEN.value,
                "status": "NOT_EVALUATED",
                "score": 0,
            }
            continue

        score = 0
        if tier_ev.verdict == Verdict.PASS:
            score = 20
            passed_tiers += 1
        elif tier_ev.verdict == Verdict.WARNING:
            score = 15
            warnings.extend(tier_ev.warnings or ["Tier passed with warnings"])
        elif tier_ev.verdict == Verdict.FAIL:
            score = 0
            blockers.extend(tier_ev.errors or ["Tier verification failed"])
        elif tier_ev.verdict == Verdict.BLOCKED:
            score = 0
            blockers.append(f"Tier {tier_num} blocked by prerequisites")
        else:
            score = 5

        tier_scores[f"tier_{tier_num}"] = {
            "name": tier_ev.name,
            "verdict": tier_ev.verdict.value,
            "score": score,
            "details": tier_ev.details,
            "warnings": tier_ev.warnings,
            "errors": tier_ev.errors,
        }

    total_score = sum(t["score"] for t in tier_scores.values())

    # Determine certification grade
    if blockers:
        cert_verdict = Verdict.FAIL.value
        cert_grade = "REJECTED"
    elif total_score == 100:
        cert_verdict = Verdict.PASS.value
        cert_grade = "CERTIFIED_FULL_PARITY"
    elif total_score >= 80:
        cert_verdict = Verdict.WARNING.value if warnings else Verdict.PASS.value
        cert_grade = "CERTIFIED_COMPATIBILITY"
    elif total_score >= 50:
        cert_verdict = Verdict.WARNING.value
        cert_grade = "PARTIALLY_CERTIFIED"
    else:
        cert_verdict = Verdict.UNPROVEN.value
        cert_grade = "UNPROVEN"

    scorecard = {
        "scorecard_version": "2.0.0",
        "workload": bundle.workload,
        "evaluation_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "certification_verdict": cert_verdict,
        "certification_grade": cert_grade,
        "total_score": total_score,
        "max_score": 100,
        "tier_breakdown": tier_scores,
        "warnings": warnings,
        "blockers": blockers,
        "unsupported_constructs": bundle.unsupported_constructs,
        "manifest_sha256": bundle.manifest_sha256,
    }
    return scorecard


def generate_scorecard(
    workload: str,
    pipeline_out: Union[str, Path],
    evidence_bundle: Optional[EvidenceBundle] = None,
    differential_result: Optional[Dict[str, Any]] = None,
    output_dir: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """Generate scorecard JSON and Markdown report, saving to output directory."""
    from .evidence import collect_evidence

    bundle = evidence_bundle or collect_evidence(
        workload=workload,
        pipeline_out=pipeline_out,
        differential_result=differential_result,
    )

    scorecard = evaluate_certification(bundle)

    if output_dir:
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        json_file = out_path / "certification_scorecard.json"
        md_file = out_path / "CERTIFICATION_REPORT.md"

        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(scorecard, f, indent=2)

        md_content = render_scorecard_markdown(scorecard)
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_content)

    return scorecard


def render_scorecard_markdown(scorecard: Dict[str, Any]) -> str:
    """Render human-readable Markdown certification report."""
    verdict = scorecard["certification_verdict"]
    grade = scorecard["certification_grade"]
    score = scorecard["total_score"]
    workload = scorecard["workload"]

    badge_color = "green" if verdict == "PASS" else ("yellow" if verdict == "WARNING" else "red")

    lines = [
        f"# Certification Scorecard: {workload}",
        "",
        f"**Verdict:** `{verdict}` | **Grade:** `{grade}` | **Score:** `{score}/100`  ",
        f"**Evaluation UTC:** `{scorecard['evaluation_timestamp_utc']}`  ",
        "",
        "---",
        "",
        "## 1. 5-Tier Certification Breakdown",
        "",
        "| Tier | Description | Verdict | Score | Status / Details |",
        "|---|---|---|---|---|",
    ]

    for tier_key, tier_data in scorecard["tier_breakdown"].items():
        t_num = tier_key.replace("tier_", "Tier ")
        t_name = tier_data.get("name", t_num)
        t_verdict = tier_data["verdict"]
        t_score = tier_data["score"]
        t_notes = ", ".join(tier_data.get("warnings", [])) or "Verified" if t_verdict == "PASS" else (
            ", ".join(tier_data.get("errors", [])) or "Pending"
        )
        lines.append(f"| **{t_num}** | {t_name} | `{t_verdict}` | `{t_score}/20` | {t_notes} |")

    lines.extend([
        "",
        "---",
        "",
        "## 2. Warnings & Blockers",
        "",
    ])

    if scorecard.get("warnings"):
        lines.append("### Warnings:")
        for w in scorecard["warnings"]:
            lines.append(f"- ⚠️ {w}")
    else:
        lines.append("- No warnings recorded.")

    if scorecard.get("blockers"):
        lines.append("\n### Blockers:")
        for b in scorecard["blockers"]:
            lines.append(f"- ❌ {b}")
    else:
        lines.append("\n- No blocking failures recorded.")

    lines.extend([
        "",
        "---",
        "",
        "## 3. Cryptographic Verification Chain",
        "",
        f"- **Manifest SHA-256:** `{scorecard.get('manifest_sha256', 'N/A')}`",
        f"- **Certification Engine Version:** `{scorecard['scorecard_version']}`",
        "",
    ])

    return "\n".join(lines)
