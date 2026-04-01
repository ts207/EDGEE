from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Mapping

from project.spec_registry.loaders import repo_root
from project.research.seed_bootstrap import (
    DOCS_GENERATED,
    SEED_POLICY_PATH,
    build_promotion_seed_inventory,
    load_seed_promotion_policy,
)

TESTING_SCORECARD_FIELDS: tuple[str, ...] = (
    "candidate_id",
    "source_type",
    "source_contract_ids",
    "governance_tier",
    "operational_role",
    "deployment_disposition",
    "current_evidence_source",
    "ontology_fidelity",
    "implementation_fidelity",
    "evidence_strength",
    "regime_clarity",
    "invalidation_clarity",
    "confounder_handling",
    "holdout_quality",
    "deployment_suitability",
    "total_score",
    "testing_decision",
    "lifecycle_class",
    "evidence_gap_summary",
    "recommended_next_action",
)


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def _load_inventory(path: str | Path | None = None) -> list[dict[str, str]]:
    inventory_path = Path(path) if path is not None else DOCS_GENERATED / "promotion_seed_inventory.csv"
    if not inventory_path.exists():
        build_promotion_seed_inventory(docs_dir=inventory_path.parent)
    if not inventory_path.exists():
        return []
    with inventory_path.open("r", encoding="utf-8", newline="") as handle:
        return [
            {str(key): str(value) for key, value in row.items()}
            for row in csv.DictReader(handle)
        ]


def _score_tier(value: str) -> int:
    token = str(value or "").strip().upper()
    if token == "A":
        return 5
    if token == "B":
        return 4
    if token == "C":
        return 2
    if token == "D":
        return 1
    return 0


def _ontology_fidelity(row: Mapping[str, str]) -> int:
    score = _score_tier(row.get("governance_tier", ""))
    if row.get("source_contract_ids", "").strip():
        score = max(score, 3)
    return min(5, score)


def _implementation_fidelity(row: Mapping[str, str]) -> int:
    status = str(row.get("detector_fidelity_status", "")).strip().lower()
    promotion_status = str(row.get("promotion_status", "")).strip().lower()
    if "governed_contract_available" in status or "episode_contract_available" in status:
        return 2 if promotion_status == "needs_repair" else 5
    if status:
        return 2
    return 0


def _source_has_empirical_artifact(source: str) -> bool:
    token = str(source or "").strip()
    if not token:
        return False
    lowered = token.lower()
    if lowered.startswith("event_contract_fallback:") or lowered.startswith("episode_contract_fallback:"):
        return False
    if lowered.startswith("file:"):
        return Path(token.split(":", 1)[1]).exists()
    if lowered.startswith("path:"):
        return Path(token.split(":", 1)[1]).exists()
    return False


def _evidence_strength(row: Mapping[str, str]) -> int:
    source = str(row.get("current_evidence_source", "")).strip()
    lowered = source.lower()
    if _source_has_empirical_artifact(source):
        return 4
    if not source:
        return 0
    if lowered.startswith("event_contract_fallback:") or lowered.startswith("episode_contract_fallback:"):
        return 1
    return 2


def _regime_clarity(row: Mapping[str, str]) -> int:
    assumptions = str(row.get("regime_assumptions", "")).strip()
    if not assumptions:
        return 0
    if len(assumptions) >= 30:
        return 4
    return 3


def _invalidation_clarity(row: Mapping[str, str]) -> int:
    invalidation = str(row.get("invalidation_rule", "")).strip()
    if not invalidation:
        return 0
    if "still needs empirical refinement" in invalidation.lower():
        return 2
    if len(invalidation) >= 24:
        return 4
    return 3


def _confounder_handling(row: Mapping[str, str]) -> int:
    raw = str(row.get("confounders_checked", "")).strip()
    if not raw or raw.lower() == "none_yet":
        return 0
    count = len([item for item in raw.replace(",", "|").split("|") if item.strip()])
    if count >= 3:
        return 4
    if count == 2:
        return 3
    return 2


def _holdout_quality(row: Mapping[str, str]) -> int:
    source = str(row.get("current_evidence_source", "")).strip().lower()
    if any(token in source for token in ("holdout", "oos", "out_of_sample", "out-of-sample")):
        return 4
    if _source_has_empirical_artifact(str(row.get("current_evidence_source", ""))):
        return 2
    return 0


def _deployment_suitability(row: Mapping[str, str]) -> int:
    role = str(row.get("operational_role", "")).strip().lower()
    disposition = str(row.get("deployment_disposition", "")).strip().lower()
    status = str(row.get("promotion_status", "")).strip().lower()
    tier = str(row.get("governance_tier", "")).strip().upper()
    if status == "needs_repair" or role in {"context", "filter", "research_only", "sequence_component"}:
        return 1
    if disposition in {"context_only", "research_only", "repair_before_promotion", "inactive", "deprecated", "alias_only"}:
        return 1
    if role == "trigger" and tier == "A":
        return 5
    if role in {"trigger", "confirm"} and tier in {"A", "B"}:
        return 4
    return 3


def _testing_thresholds(policy: Mapping[str, Any]) -> dict[str, int]:
    payload = dict(policy.get("testing_score_thresholds", {}))
    defaults = {
        "reject_max_total": 12,
        "seed_promote_min_total": 27,
        "paper_candidate_min_total": 34,
        "minimum_evidence_strength_for_seed": 3,
        "minimum_holdout_quality_for_seed": 2,
        "minimum_confounder_handling_for_seed": 2,
    }
    out: dict[str, int] = {}
    for key, default in defaults.items():
        try:
            out[key] = int(payload.get(key, default))
        except (TypeError, ValueError):
            out[key] = int(default)
    return out


def _lifecycle_class_for_decision(decision: str) -> str:
    token = str(decision or "").strip().lower()
    if token in {"seed_promote", "paper_candidate"}:
        return "tested_thesis"
    if token in {"needs_more_evidence", "needs_repair"}:
        return "candidate_thesis"
    if token == "reject":
        return "candidate_thesis"
    return "candidate_thesis"


def _evidence_gaps(row: Mapping[str, str], scores: Mapping[str, int]) -> list[str]:
    gaps: list[str] = []
    if scores.get("evidence_strength", 0) < 3:
        gaps.append("empirical_evidence_bundle_missing")
    if scores.get("holdout_quality", 0) < 2:
        gaps.append("holdout_check_missing")
    if scores.get("confounder_handling", 0) < 2:
        gaps.append("confounder_sanity_check_missing")
    if scores.get("deployment_suitability", 0) <= 1:
        gaps.append("governance_role_or_disposition_blocked")
    if scores.get("invalidation_clarity", 0) < 3:
        gaps.append("invalidation_rule_needs_refinement")
    return gaps


def _decision_for_row(row: Mapping[str, str], scores: Mapping[str, int], policy: Mapping[str, Any]) -> str:
    thresholds = _testing_thresholds(policy)
    promotion_status = str(row.get("promotion_status", "")).strip().lower()
    total = int(scores["total_score"])
    if promotion_status == "needs_repair" or scores["deployment_suitability"] <= 1:
        return "needs_repair"
    if total <= thresholds["reject_max_total"]:
        return "reject"
    evidence_ok = scores["evidence_strength"] >= thresholds["minimum_evidence_strength_for_seed"]
    holdout_ok = scores["holdout_quality"] >= thresholds["minimum_holdout_quality_for_seed"]
    conf_ok = scores["confounder_handling"] >= thresholds["minimum_confounder_handling_for_seed"]
    invalidation_ok = scores["invalidation_clarity"] >= 3
    if evidence_ok and holdout_ok and conf_ok and invalidation_ok:
        if total >= thresholds["paper_candidate_min_total"]:
            return "paper_candidate"
        if total >= thresholds["seed_promote_min_total"]:
            return "seed_promote"
    return "needs_more_evidence"


def _next_action_for_decision(decision: str, gaps: list[str]) -> str:
    token = str(decision or "").strip().lower()
    if token == "needs_repair":
        return "repair_governance_or_role_conflict"
    if token == "reject":
        return "archive_candidate"
    if token == "seed_promote":
        return "package_seed_thesis"
    if token == "paper_candidate":
        return "run_paper_promotion_review"
    if "empirical_evidence_bundle_missing" in gaps:
        return "run_empirical_event_study"
    if "holdout_check_missing" in gaps:
        return "run_holdout_validation"
    if "confounder_sanity_check_missing" in gaps:
        return "run_confounder_sanity_checks"
    return "review_candidate_manually"


def score_seed_candidates(
    *,
    docs_dir: str | Path | None = None,
    inventory_path: str | Path | None = None,
    policy_path: str | Path | None = None,
) -> dict[str, Path]:
    out_dir = _ensure_dir(Path(docs_dir) if docs_dir is not None else DOCS_GENERATED)
    rows = _load_inventory(inventory_path)
    policy = load_seed_promotion_policy(policy_path or SEED_POLICY_PATH)

    scorecard_rows: list[dict[str, Any]] = []
    for row in rows:
        scores = {
            "ontology_fidelity": _ontology_fidelity(row),
            "implementation_fidelity": _implementation_fidelity(row),
            "evidence_strength": _evidence_strength(row),
            "regime_clarity": _regime_clarity(row),
            "invalidation_clarity": _invalidation_clarity(row),
            "confounder_handling": _confounder_handling(row),
            "holdout_quality": _holdout_quality(row),
            "deployment_suitability": _deployment_suitability(row),
        }
        total_score = sum(scores.values())
        scores["total_score"] = total_score
        decision = _decision_for_row(row, scores, policy)
        gaps = _evidence_gaps(row, scores)
        scorecard_rows.append(
            {
                "candidate_id": row.get("candidate_id", ""),
                "source_type": row.get("source_type", ""),
                "source_contract_ids": row.get("source_contract_ids", ""),
                "governance_tier": row.get("governance_tier", ""),
                "operational_role": row.get("operational_role", ""),
                "deployment_disposition": row.get("deployment_disposition", ""),
                "current_evidence_source": row.get("current_evidence_source", ""),
                **scores,
                "testing_decision": decision,
                "lifecycle_class": _lifecycle_class_for_decision(decision),
                "evidence_gap_summary": "|".join(gaps) if gaps else "",
                "recommended_next_action": _next_action_for_decision(decision, gaps),
            }
        )

    csv_path = out_dir / "thesis_testing_scorecards.csv"
    json_path = out_dir / "thesis_testing_scorecards.json"
    md_path = out_dir / "thesis_testing_summary.md"

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(TESTING_SCORECARD_FIELDS))
        writer.writeheader()
        writer.writerows(scorecard_rows)

    json_path.write_text(json.dumps(scorecard_rows, indent=2), encoding="utf-8")

    decision_counts: dict[str, int] = {}
    for row in scorecard_rows:
        decision = str(row["testing_decision"])
        decision_counts[decision] = decision_counts.get(decision, 0) + 1

    sorted_rows = sorted(scorecard_rows, key=lambda item: (-int(item["total_score"]), str(item["candidate_id"])))
    lines = [
        "# Thesis testing summary",
        "",
        "This is a governance-first Block B testing pass over the seed queue.",
        "It scores ontology, implementation, invalidation clarity, and deployment readiness from current repo artifacts.",
        "It does **not** claim that empirical holdout/confounder testing exists where the evidence source is still a contract fallback.",
        "",
        f"- candidates_reviewed: `{len(scorecard_rows)}`",
        "- decision_counts: " + ", ".join(f"`{key}={value}`" for key, value in sorted(decision_counts.items())),
        "",
    ]
    if decision_counts.get("seed_promote", 0) == 0 and decision_counts.get("paper_candidate", 0) == 0:
        lines.extend(
            [
                "## Key conclusion",
                "",
                "No candidate clears seed promotion under the current repo snapshot because the founding queue still lacks empirical evidence bundles, holdout checks, and confounder sanity checks.",
                "This is the intended fail-closed behavior for Block B on a bootstrap-only inventory.",
                "",
            ]
        )
    lines.extend([
        "## Highest-scoring candidates",
        "",
        "| Candidate | Total score | Decision | Evidence gaps | Next action |",
        "|---|---:|---|---|---|",
    ])
    for row in sorted_rows[:8]:
        lines.append(
            "| {candidate_id} | {total_score} | {testing_decision} | {evidence_gap_summary} | {recommended_next_action} |".format(**row)
        )
    lines.extend([
        "",
        "## Scoring rubric",
        "",
        "Fields scored 0–5: ontology fidelity, implementation fidelity, evidence strength, regime clarity, invalidation clarity, confounder handling, holdout quality, deployment suitability.",
        "",
    ])
    md_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return {"csv": csv_path, "json": json_path, "md": md_path}


__all__ = ["score_seed_candidates"]
