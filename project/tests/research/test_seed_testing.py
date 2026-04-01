from __future__ import annotations

import csv
from pathlib import Path

from project.research.seed_bootstrap import build_promotion_seed_inventory
from project.research.seed_testing import score_seed_candidates
from project.research.services.promotion_service import (
    default_deployment_state_for_promotion_class,
    normalize_promotion_class,
)


def test_score_seed_candidates_renders_fail_closed_summary(tmp_path: Path) -> None:
    build_promotion_seed_inventory(docs_dir=tmp_path)
    out = score_seed_candidates(docs_dir=tmp_path, inventory_path=tmp_path / "promotion_seed_inventory.csv")

    rows = list(csv.DictReader((tmp_path / "thesis_testing_scorecards.csv").open()))
    assert rows
    decisions = {row["candidate_id"]: row["testing_decision"] for row in rows}
    assert decisions["THESIS_EP_DISLOCATION_REPAIR"] == "needs_repair"
    assert decisions["THESIS_VOL_SHOCK"] == "needs_more_evidence"

    summary = out["md"].read_text(encoding="utf-8")
    assert "No candidate clears seed promotion" in summary
    assert "THESIS_VOL_SHOCK" in summary


def test_promotion_service_seed_class_helpers() -> None:
    assert normalize_promotion_class("seed_promoted") == "seed_promoted"
    assert normalize_promotion_class("unknown") == "paper_promoted"
    assert default_deployment_state_for_promotion_class("seed_promoted") == "monitor_only"
    assert default_deployment_state_for_promotion_class("production_promoted") == "live_enabled"
