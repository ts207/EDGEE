from __future__ import annotations
import pytest
import pandas as pd
import numpy as np
from project.research.phase2_event_analyzer import (
    ConditionSpec,
    ActionSpec,
    build_conditions,
    build_actions,
    candidate_type_from_action,
    assign_candidate_types_and_overlay_bases,
    expectancy_for_action,
    _numeric_non_negative,
    _numeric_any
)
from unittest.mock import patch, MagicMock

def test_numeric_non_negative():
    df = pd.DataFrame({"a": [1.0, -1.0, "nan", 2.0]})
    res = _numeric_non_negative(df, "a", 4)
    assert res.tolist() == [1.0, 0.0, 0.0, 2.0]
    
    res = _numeric_non_negative(df, "missing", 4)
    assert res.tolist() == [0.0, 0.0, 0.0, 0.0]

def test_numeric_any():
    df = pd.DataFrame({"a": [1.0, -1.0, "nan", 2.0]})
    res = _numeric_any(df, "a", 4)
    assert np.isnan(res[2])
    assert res[0] == 1.0
    assert res[1] == -1.0

def test_build_conditions_basic():
    df = pd.DataFrame({
        "vol_regime": ["low", "high", "low"],
        "tod_bucket": [1, 10, 20]
    })
    
    mock_defaults = {
        "defaults": {
            "conditioning_cols": ["vol_regime"]
        }
    }
    
    with patch("project.research.phase2_event_analyzer.load_global_defaults", return_value=mock_defaults):
        conds = build_conditions(df)
        names = [c.name for c in conds]
        assert "all" in names
        assert "vol_regime_low" in names
        assert "vol_regime_high" in names
        assert "session_asia" in names
        assert "session_eu" in names
        assert "session_us" in names

def test_build_actions():
    actions = build_actions()
    names = [a.name for a in actions]
    assert "no_action" in names
    assert "entry_gate_skip" in names
    assert "risk_throttle_0.5" in names

def test_candidate_type_from_action():
    assert candidate_type_from_action("no_action") == "standalone"
    assert candidate_type_from_action("entry_gate_skip") == "overlay"
    assert candidate_type_from_action("risk_throttle_0.5") == "overlay"
    assert candidate_type_from_action("delay_8") == "standalone"

def test_assign_candidate_types_and_overlay_bases():
    df = pd.DataFrame({
        "candidate_id": ["c1", "c2"],
        "action": ["no_action", "entry_gate_skip"],
        "condition": ["all", "all"]
    })
    res = assign_candidate_types_and_overlay_bases(df, "VOL_SHOCK")
    assert res.at[0, "candidate_type"] == "standalone"
    assert res.at[1, "candidate_type"] == "overlay"
    assert res.at[1, "overlay_base_candidate_id"] == "c1"

def test_expectancy_for_action_no_action():
    df = pd.DataFrame({
        "expectancy_proxy": [0.1, 0.2]
    })
    action = ActionSpec("no_action", "baseline", {})
    assert pytest.approx(expectancy_for_action(df, action)) == 0.15

def test_expectancy_for_action_with_delta():
    df = pd.DataFrame({
        "adverse_proxy_excess": [0.1, 0.2],
        "opportunity_proxy_excess": [0.05, 0.1]
    })
    # Action risk_throttle_0.5: k=0.5
    # exposure_delta = -0.5
    # adverse_delta = -0.5 * adverse = [-0.05, -0.1]
    # opportunity_delta = -0.5 * opp = [-0.025, -0.05]
    # risk_reduction = -mean(adverse_delta) = 0.075
    # opportunity_cost = max(0, -mean(opportunity_delta)) = 0.0375
    # net_benefit = 0.075 - 0.0375 = 0.0375
    action = ActionSpec("risk_throttle_0.5", "risk_throttle", {"k": 0.5})
    assert pytest.approx(expectancy_for_action(df, action)) == 0.0375
