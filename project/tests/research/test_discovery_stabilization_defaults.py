import pytest
import pandas as pd
from pathlib import Path
from project.research import phase2_search_engine
from project.research.services.candidate_discovery_scoring import build_discovery_quality_score

def test_v2_scoring_defaults():
    # Mock row
    row = pd.Series({
        "t_stat": 3.0,
        "mean_return_bps": 10.0,
        "placebo_shift_effect": 1.0,
        "null_strength_ratio": 5.0,
        "cost_survival_ratio": 0.8,
        "event_family_key": "fam1",
        "template_family_key": "tpl1",
        "direction_key": "long",
        "horizon_bucket": "1h",
        "is_discovery": True
    })
    
    config = {
        "falsification_weight": 1.0,
        "tradability_weight": 1.0,
        "novelty_weight": 1.0,
        "overlap_penalty_weight": 1.0,
        "fragility_penalty_weight": 1.0
    }
    
    overlap_context = {"fam1|tpl1|long|1h": 1}
    
    score_data = build_discovery_quality_score(row, overlap_context, config)
    
    # Check that all expected components are present
    expected_cols = [
        "falsification_component",
        "tradability_component",
        "novelty_component",
        "support_component",
        "significance_component",
        "fold_stability_bonus",
        "fold_stability_penalty",
        "overlap_penalty",
        "fragility_penalty",
        "discovery_quality_score",
        "rank_primary_reason",
        "demotion_reason_codes"
    ]
    for col in expected_cols:
        assert col in score_data, f"Missing {col} in score decomposition"

def test_search_engine_v2_default(monkeypatch):
    # Check that run() has enable_discovery_v2_scoring=True by default
    import inspect
    sig = inspect.signature(phase2_search_engine.run)
    assert sig.parameters["enable_discovery_v2_scoring"].default is True

def test_search_space_mode_default():
    import yaml
    from project import PROJECT_ROOT
    spec_path = PROJECT_ROOT.parent / "spec/search_space.yaml"
    with open(spec_path, "r") as f:
        spec = yaml.safe_load(f)
        # Assert flat mode is default
        assert spec["discovery_search"]["mode"] == "flat"

def test_ledger_config_default_disabled():
    import yaml
    from project import PROJECT_ROOT
    config_path = PROJECT_ROOT.parent / "project/configs/discovery_ledger.yaml"
    if config_path.exists():
        with open(config_path, "r") as f:
            cfg = yaml.safe_load(f)
            # Assert ledger is disabled officially
            assert cfg["discovery_scoring"]["ledger_adjustment"]["enabled"] is False

def test_shortlist_diversification_default_disabled():
    import yaml
    from project import PROJECT_ROOT
    # If shortlist config exists, ensure it's disabled or mode is basic
    spec_path = PROJECT_ROOT.parent / "spec/search_space.yaml"
    with open(spec_path, "r") as f:
        spec = yaml.safe_load(f)
        # In current spec, if no explicit diversified_shortlist block, it's disabled.
        # If it exists, it must be disabled.
        if "diversified_shortlist" in spec:
            assert spec["diversified_shortlist"].get("enabled", False) is False
