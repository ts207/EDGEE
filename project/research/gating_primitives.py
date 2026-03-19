"""
Phase 2 Gating Logic: Expectancy calculation, FDR adjustment, and Drawdown gating.
Refactored to improve testability and separate concerns.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

try:
    from scipy import stats
except ModuleNotFoundError:
    from project.core.stats import stats

from project.core.constants import HORIZON_BARS_BY_TIMEFRAME
from project.core.validation import ts_ns_utc
from project.research.direction_semantics import resolve_effect_sign
from project.research.holdout_integrity import assert_no_lookahead_join
from project.research.helpers.shrinkage import (
    _asymmetric_tau_days,
    _effective_sample_size,
    _event_direction_from_joined_row,
    _regime_conditioned_tau_days,
    _time_decay_weights,
)

log = logging.getLogger(__name__)


def bh_adjust(p_values: np.ndarray) -> np.ndarray:
    """Benjamini-Hochberg FDR adjustment."""
    if len(p_values) == 0:
        return p_values
    n = len(p_values)
    idx = np.argsort(p_values)
    sorted_p = p_values[idx]
    adj_p = np.zeros(n)
    min_p = 1.0
    for i in range(n - 1, -1, -1):
        q = sorted_p[i] * n / (i + 1)
        min_p = min(min_p, q)
        adj_p[i] = min_p
    # map back to original order
    rev_idx = np.zeros(n, dtype=int)
    rev_idx[idx] = np.arange(n)
    return adj_p[rev_idx]


def distribution_stats(returns: np.ndarray) -> Dict[str, float]:
    """Compute mean, std, t-stat, p-value for a return distribution."""
    if len(returns) < 2:
        return {"mean": 0.0, "std": 0.0, "t_stat": 0.0, "p_value": 1.0}
    mean = np.mean(returns)
    std = np.std(returns, ddof=1)
    if std == 0:
        return {"mean": mean, "std": 0.0, "t_stat": 0.0, "p_value": 1.0}
    t_stat = mean / (std / np.sqrt(len(returns)))
    p_value = 2 * (1 - stats.t.cdf(np.abs(t_stat), df=len(returns) - 1))
    return {"mean": mean, "std": std, "t_stat": t_stat, "p_value": p_value}


def two_sided_p_from_t(t_stat: float, df: int) -> float:
    if df < 1:
        return 1.0
    return float(2.0 * stats.t.sf(np.abs(t_stat), df=df))


def horizon_to_bars(horizon: str) -> int:
    return HORIZON_BARS_BY_TIMEFRAME.get(horizon.lower().strip(), 12)


def join_events_to_features(
    events_df: pd.DataFrame,
    features_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Merge event timestamps to the features table using a backward merge.
    """
    ts_col = "enter_ts" if "enter_ts" in events_df.columns else "timestamp"
    if ts_col not in events_df.columns:
        return pd.DataFrame()

    evt = events_df.copy()
    evt["event_ts"] = ts_ns_utc(evt[ts_col], allow_nat=True)
    evt = evt.dropna(subset=["event_ts"]).sort_values("event_ts").reset_index(drop=True)
    if evt.empty:
        return pd.DataFrame()

    if "timestamp" not in features_df.columns:
        return pd.DataFrame()
    feat = features_df.copy()
    feat["feature_ts"] = ts_ns_utc(feat["timestamp"], allow_nat=True)
    feat = feat.dropna(subset=["feature_ts"]).sort_values("feature_ts").reset_index(drop=True)
    if feat.empty:
        return pd.DataFrame()
    feat["_feature_pos"] = feat.index.astype(int)

    # Use merge_asof: for each event, find the latest feature bar <= event_ts
    extra_evt_cols = [
        col
        for col in (
            "vol_regime",
            "liquidity_state",
            "market_liquidity_state",
            "depth_state",
            "event_direction",
            "direction",
            "signal_direction",
            "flow_direction",
            "breakout_direction",
            "shock_direction",
            "move_direction",
            "leader_direction",
            "return_1",
            "return_sign",
            "sign",
            "polarity",
            "funding_z",
            "basis_z",
            "side",
            "trade_side",
            "direction_label",
            "split_label",
        )
        if col in evt.columns
    ]

    evt_cols = ["event_ts"] + extra_evt_cols
    evt_for_join = evt[evt_cols].rename(columns={c: f"evt_{c}" for c in extra_evt_cols})

    merged = pd.merge_asof(
        evt_for_join,
        feat,
        left_on="event_ts",
        right_on="feature_ts",
        direction="backward",
    )
    assert_no_lookahead_join(
        merged,
        event_ts_col="event_ts",
        feature_ts_col="feature_ts",
        context="project.research.gating.join_events_to_features",
    )
    return merged


def empty_expectancy_stats() -> Dict[str, Any]:
    return {
        "mean_return": 0.0,
        "p_value": 1.0,
        "n_events": 0.0,
        "n_effective": 0.0,
        "stability_pass": False,
        "std_return": 0.0,
        "t_stat": 0.0,
        "time_weight_sum": 0.0,
        "mean_weight_age_days": 0.0,
        "mean_tau_days": 0.0,
        "learning_rate_mean": 0.0,
        "mean_tau_up_days": 0.0,
        "mean_tau_down_days": 0.0,
        "tau_directional_ratio": 0.0,
        "directional_up_share": 0.0,
        "mean_train_return": 0.0,
        "mean_validation_return": 0.0,
        "mean_test_return": 0.0,
        "train_samples": 0,
        "validation_samples": 0,
        "test_samples": 0,
        "t_train": 0.0,
        "t_validation": 0.0,
        "t_test": 0.0,
    }


__all__ = [
    "bh_adjust",
    "distribution_stats",
    "empty_expectancy_stats",
    "horizon_to_bars",
    "join_events_to_features",
    "two_sided_p_from_t",
]
