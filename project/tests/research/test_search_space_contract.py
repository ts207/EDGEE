from __future__ import annotations

from pathlib import Path

import yaml

from project.research.search.generator import generate_hypotheses_with_audit


def test_search_space_includes_vol_shock_event_trigger():
    repo_root = Path(__file__).resolve().parents[3]
    search_space_path = repo_root / "spec" / "search_space.yaml"
    payload = yaml.safe_load(search_space_path.read_text(encoding="utf-8"))

    assert "VOL_SHOCK" in payload["triggers"]["events"]


def test_synthetic_truth_search_spec_expands_event_specific_templates():
    hypotheses, audit = generate_hypotheses_with_audit("synthetic_truth")

    assert hypotheses
    assert audit["counts"]["feasible"] > 0
    assert audit["rejection_reason_counts"].get("validation_error", 0) == 0
