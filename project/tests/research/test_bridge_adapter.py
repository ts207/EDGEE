from __future__ import annotations

import pandas as pd

from project.research.search.bridge_adapter import hypotheses_to_bridge_candidates


def test_hypotheses_to_bridge_candidates_respects_configured_bridge_thresholds():
    metrics = pd.DataFrame(
        [
            {
                "hypothesis_id": "hyp_1",
                "trigger_type": "event",
                "trigger_key": "event:VOL_SHOCK",
                "direction": "short",
                "horizon": "60m",
                "template_id": "continuation",
                "n": 64,
                "train_n_obs": 30,
                "validation_n_obs": 16,
                "test_n_obs": 18,
                "validation_samples": 16,
                "test_samples": 18,
                "mean_return_bps": 85_000.0,
                "t_stat": 1.9,
                "sharpe": 1.2,
                "hit_rate": 0.55,
                "cost_adjusted_return_bps": 9.0,
                "mae_mean_bps": -12.0,
                "mfe_mean_bps": 23.0,
                "robustness_score": 0.65,
                "stress_score": 0.4,
                "kill_switch_count": 0,
                "capacity_proxy": 1.0,
                "valid": True,
                "invalid_reason": None,
            }
        ]
    )

    default = hypotheses_to_bridge_candidates(metrics)
    relaxed = hypotheses_to_bridge_candidates(
        metrics,
        bridge_min_t_stat=1.8,
        bridge_min_robustness_score=0.65,
        bridge_min_regime_stability_score=0.6,
        bridge_min_stress_survival=0.4,
        bridge_stress_cost_buffer_bps=1.0,
    )

    assert bool(default.iloc[0]["gate_bridge_tradable"]) is False
    assert bool(relaxed.iloc[0]["gate_bridge_tradable"]) is True
    assert bool(default.iloc[0]["gate_oos_validation"]) is False
    assert bool(relaxed.iloc[0]["gate_oos_validation"]) is True
