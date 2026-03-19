"""Support functions for phase2_event_analyzer (split to stay under 800-LOC gate)."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from project.spec_registry import load_template_registry

def attach_event_market_features(
    events: pd.DataFrame,
    run_id: str,
    symbols: List[str],
    timeframe: str = "5m",
) -> pd.DataFrame:
    DATA_ROOT = get_data_root()
    if events.empty:
        return events

    out = events.copy()
    out["enter_ts"] = pd.to_datetime(out.get("enter_ts"), utc=True, errors="coerce")
    if out["enter_ts"].isna().all():
        return out

    context_rows: List[pd.DataFrame] = []
    for symbol in symbols:
        feature_dataset = feature_dataset_dir_name()
        features_candidates = [
            run_scoped_lake_path(
                DATA_ROOT, run_id, "features", "perp", symbol, timeframe, feature_dataset
            ),
            DATA_ROOT / "lake" / "features" / "perp" / symbol / timeframe / feature_dataset,
        ]
        bars_candidates = [
            run_scoped_lake_path(DATA_ROOT, run_id, "cleaned", "perp", symbol, f"bars_{timeframe}"),
            DATA_ROOT / "lake" / "cleaned" / "perp" / symbol / f"bars_{timeframe}",
        ]

        features_src = choose_partition_dir(features_candidates)
        features = (
            read_parquet(list_parquet_files(features_src)) if features_src else pd.DataFrame()
        )
        bars_src = choose_partition_dir(bars_candidates)
        bars = read_parquet(list_parquet_files(bars_src)) if bars_src else pd.DataFrame()

        context_candidates = [
            run_scoped_lake_path(DATA_ROOT, run_id, "context", "market_state", symbol, timeframe),
            DATA_ROOT / "lake" / "context" / "market_state" / symbol / timeframe,
        ]
        context_src = choose_partition_dir(context_candidates)
        market_state = (
            read_parquet(list_parquet_files(context_src)) if context_src else pd.DataFrame()
        )

        if features.empty and bars.empty and market_state.empty:
            continue

        if "timestamp" in features.columns:
            features["timestamp"] = pd.to_datetime(features["timestamp"], utc=True, errors="coerce")
        else:
            features["timestamp"] = pd.NaT
        if "timestamp" in bars.columns:
            bars["timestamp"] = pd.to_datetime(bars["timestamp"], utc=True, errors="coerce")
        else:
            bars["timestamp"] = pd.NaT

        feature_cols = [
            "timestamp",
            "spread_bps",
            "atr_14",
            "quote_volume",
            "funding_rate_scaled",
            "close",
            "high",
            "low",
        ]
        feat = features[[col for col in feature_cols if col in features.columns]].copy()
        if feat.empty:
            feat = pd.DataFrame({"timestamp": pd.Series(dtype="datetime64[ns, UTC]")})
        if "timestamp" not in feat.columns:
            feat["timestamp"] = pd.NaT

        bar_cols = ["timestamp", "close", "high", "low", "quote_volume"]
        bar_view = bars[[col for col in bar_cols if col in bars.columns]].copy()
        if not bar_view.empty:
            feat = feat.merge(bar_view, on="timestamp", how="outer", suffixes=("", "_bar"))
            for col in ["close", "high", "low", "quote_volume"]:
                bar_col = f"{col}_bar"
                if bar_col in feat.columns:
                    if col not in feat.columns:
                        feat[col] = feat[bar_col]
                    else:
                        feat[col] = feat[col].where(feat[col].notna(), feat[bar_col])
                    feat = feat.drop(columns=[bar_col])

        state_cols = [
            "timestamp",
            "vol_regime",
            "vol_regime_code",
            "carry_state",
            "carry_state_code",
        ]
        state_view = market_state[[col for col in state_cols if col in market_state.columns]].copy()
        if not state_view.empty:
            feat = feat.merge(state_view, on="timestamp", how="outer")

        feat["symbol"] = str(symbol).upper()
        feat["enter_ts"] = pd.to_datetime(feat["timestamp"], utc=True, errors="coerce")
        feat = feat.dropna(subset=["enter_ts"]).drop_duplicates(
            subset=["symbol", "enter_ts"], keep="last"
        )
        keep_cols = [
            "symbol",
            "enter_ts",
            "spread_bps",
            "atr_14",
            "quote_volume",
            "funding_rate_scaled",
            "close",
            "high",
            "low",
            "vol_regime",
            "vol_regime_code",
            "carry_state",
            "carry_state_code",
        ]
        feat = feat[[col for col in keep_cols if col in feat.columns]]
        context_rows.append(feat)

    if not context_rows:
        return out

    context = pd.concat(context_rows, ignore_index=True).drop_duplicates(
        subset=["symbol", "enter_ts"], keep="last"
    )
    out = out.copy()
    out["enter_ts"] = pd.to_datetime(out["enter_ts"], utc=True, errors="coerce")
    context = context.copy()
    context["enter_ts"] = pd.to_datetime(context["enter_ts"], utc=True, errors="coerce")
    left_parts = []
    for symbol, sub in out.sort_values(["symbol", "enter_ts"]).groupby("symbol", sort=False):
        ctx = context[context["symbol"] == symbol].sort_values("enter_ts")
        if ctx.empty:
            left_parts.append(sub)
            continue
        merged_sub = pd.merge_asof(
            sub, ctx, on="enter_ts", direction="backward", suffixes=("", "_ctx")
        )
        left_parts.append(merged_sub)
    merged = pd.concat(left_parts, ignore_index=True) if left_parts else out.copy()
    for col in [
        "spread_bps",
        "atr_14",
        "quote_volume",
        "funding_rate_scaled",
        "close",
        "high",
        "low",
        "vol_regime",
        "vol_regime_code",
        "carry_state",
        "carry_state_code",
    ]:
        ctx_col = f"{col}_ctx"
        if ctx_col in merged.columns:
            if col not in merged.columns:
                merged[col] = merged[ctx_col]
            else:
                merged[col] = merged[col].where(merged[col].notna(), merged[ctx_col])
            merged = merged.drop(columns=[ctx_col])
    return merged


def prepare_baseline(events: pd.DataFrame, controls: pd.DataFrame) -> pd.DataFrame:
    out = events.copy()
    out["baseline_mode"] = "event_proxy_only"

    adverse_binary_col = _first_existing(
        out, ["secondary_shock_within_h", "secondary_shock_within", "tail_move_within"]
    )
    adverse_mag_col = _first_existing(out, ["range_pct_96", "range_expansion"])
    opportunity_col = _first_existing(out, ["relaxed_within_96", "forward_abs_return_h"])

    adverse_binary = _numeric_non_negative(out, adverse_binary_col, n=len(out))
    adverse_mag = _numeric_non_negative(out, adverse_mag_col, n=len(out))
    if adverse_binary_col and adverse_mag_col:
        out["adverse_proxy"] = 0.5 * adverse_binary + 0.5 * adverse_mag
    elif adverse_binary_col:
        out["adverse_proxy"] = adverse_binary
    elif adverse_mag_col:
        out["adverse_proxy"] = adverse_mag
    else:
        out["adverse_proxy"] = 0.0

    if opportunity_col:
        out["opportunity_proxy"] = _numeric_non_negative(out, opportunity_col, n=len(out))
    elif adverse_binary_col:
        out["opportunity_proxy"] = (1.0 - adverse_binary).clip(lower=0.0)
    else:
        out["opportunity_proxy"] = 0.0

    time_to_adverse_col = _first_existing(out, ["time_to_secondary_shock", "time_to_tail_move"])
    timing_landmark_col = _first_existing(
        out, ["rv_decay_half_life", "parent_time_to_relax", "time_to_relax"]
    )
    out["time_to_adverse"] = _numeric_any(out, time_to_adverse_col, n=len(out), default=np.nan)
    out["timing_landmark"] = _numeric_any(out, timing_landmark_col, n=len(out), default=np.nan)

    if controls.empty or "event_id" not in controls.columns or "event_id" not in out.columns:
        out["adverse_proxy_ctrl"] = np.nan
        out["opportunity_proxy_ctrl"] = np.nan
        out["adverse_proxy_excess"] = out["adverse_proxy"]
        out["opportunity_proxy_excess"] = out["opportunity_proxy"]
        return out

    numeric_ctrl = controls.groupby("event_id", as_index=False).mean(numeric_only=True)
    ctrl_cols = [
        c
        for c in [
            "secondary_shock_within_h",
            "secondary_shock_within",
            "tail_move_within",
            "range_pct_96",
            "range_expansion",
            "relaxed_within_96",
            "forward_abs_return_h",
            "time_to_secondary_shock",
            "time_to_tail_move",
            "rv_decay_half_life",
            "parent_time_to_relax",
            "time_to_relax",
        ]
        if c in numeric_ctrl.columns
    ]
    if not ctrl_cols:
        out["adverse_proxy_ctrl"] = np.nan
        out["opportunity_proxy_ctrl"] = np.nan
        out["adverse_proxy_excess"] = out["adverse_proxy"]
        out["opportunity_proxy_excess"] = out["opportunity_proxy"]
        return out

    rename_map = {c: f"{c}_ctrl" for c in ctrl_cols}
    merged = out.merge(
        numeric_ctrl[["event_id"] + ctrl_cols].rename(columns=rename_map), on="event_id", how="left"
    )

    adverse_binary_ctrl_col = _first_existing(
        merged,
        ["secondary_shock_within_h_ctrl", "secondary_shock_within_ctrl", "tail_move_within_ctrl"],
    )
    adverse_mag_ctrl_col = _first_existing(merged, ["range_pct_96_ctrl", "range_expansion_ctrl"])
    opportunity_ctrl_col = _first_existing(
        merged, ["relaxed_within_96_ctrl", "forward_abs_return_h_ctrl"]
    )

    adverse_binary_ctrl = _numeric_non_negative(merged, adverse_binary_ctrl_col, n=len(merged))
    adverse_mag_ctrl = _numeric_non_negative(merged, adverse_mag_ctrl_col, n=len(merged))
    if adverse_binary_ctrl_col and adverse_mag_ctrl_col:
        merged["adverse_proxy_ctrl"] = 0.5 * adverse_binary_ctrl + 0.5 * adverse_mag_ctrl
    elif adverse_binary_ctrl_col:
        merged["adverse_proxy_ctrl"] = adverse_binary_ctrl
    elif adverse_mag_ctrl_col:
        merged["adverse_proxy_ctrl"] = adverse_mag_ctrl
    else:
        merged["adverse_proxy_ctrl"] = np.nan

    if opportunity_ctrl_col:
        merged["opportunity_proxy_ctrl"] = _numeric_non_negative(
            merged, opportunity_ctrl_col, n=len(merged)
        )
    else:
        merged["opportunity_proxy_ctrl"] = np.nan

    if "time_to_adverse" not in merged.columns:
        merged["time_to_adverse"] = _numeric_any(
            merged,
            _first_existing(merged, ["time_to_secondary_shock", "time_to_tail_move"]),
            n=len(merged),
            default=np.nan,
        )
    if "timing_landmark" not in merged.columns:
        merged["timing_landmark"] = _numeric_any(
            merged,
            _first_existing(
                merged, ["rv_decay_half_life", "parent_time_to_relax", "time_to_relax"]
            ),
            n=len(merged),
            default=np.nan,
        )

    merged["adverse_proxy_excess"] = merged["adverse_proxy"] - merged["adverse_proxy_ctrl"]
    merged["opportunity_proxy_excess"] = (
        merged["opportunity_proxy"] - merged["opportunity_proxy_ctrl"]
    )
    merged["baseline_mode"] = "matched_controls_excess"
    return merged


def apply_action_proxy(
    sub: pd.DataFrame, action: ActionSpec
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    if "adverse_proxy_excess" in sub.columns:
        adverse = sub["adverse_proxy_excess"].fillna(0).astype(float).to_numpy()
    else:
        sec = sub["secondary_shock_within_h"].fillna(0).astype(float).to_numpy()
        rng = sub["range_pct_96"].fillna(0).astype(float).to_numpy()
        adverse = 0.5 * sec + 0.5 * np.clip(rng, 0.0, None)

    if "opportunity_value_excess" in sub.columns:
        opp_value = sub["opportunity_value_excess"].fillna(0).astype(float).to_numpy()
    elif "opportunity_proxy_excess" in sub.columns:
        opp_value = sub["opportunity_proxy_excess"].fillna(0).astype(float).to_numpy()
    else:
        opp_value = sub["relaxed_within_96"].fillna(0).astype(float).to_numpy()

    if action.name in {"no_action", "delay_0"}:
        expectancy = pd.to_numeric(sub.get("expectancy_proxy"), errors="coerce")
        if expectancy.notna().any():
            base = expectancy.fillna(0.0).to_numpy(dtype=float)
        else:
            opp = pd.to_numeric(sub.get("opportunity_proxy_excess"), errors="coerce").fillna(0.0)
            adv = pd.to_numeric(sub.get("adverse_proxy_excess"), errors="coerce").fillna(0.0)
            base = (opp - adv).to_numpy(dtype=float)
        zeros = np.zeros(len(sub), dtype=float)
        return base, zeros, zeros

    if action.family in {"entry_gating", "risk_throttle"}:
        k = float(action.params.get("k", 1.0))
        exposure_delta = np.full(len(sub), -(1.0 - k), dtype=float)
        adverse_delta = -(1.0 - k) * adverse
        opportunity_delta = exposure_delta * opp_value
        return adverse_delta, opportunity_delta, exposure_delta

    if action.name.startswith("delay_"):
        delay = int(action.params.get("delay_bars", 0))
        t_adverse = (
            _numeric_any(
                sub,
                _first_existing(
                    sub, ["time_to_adverse", "time_to_secondary_shock", "time_to_tail_move"]
                ),
                n=len(sub),
                default=10**9,
            )
            .fillna(10**9)
            .to_numpy()
        )
        adverse_delta = -(t_adverse <= delay).astype(float) * adverse
        exposure_delta = -np.full(len(sub), min(1.0, delay / 96.0), dtype=float)
        opportunity_delta = exposure_delta * opp_value
        return adverse_delta, opportunity_delta, exposure_delta

    if action.name == "reenable_at_half_life":
        t_landmark = (
            _numeric_any(
                sub,
                _first_existing(
                    sub,
                    [
                        "timing_landmark",
                        "rv_decay_half_life",
                        "parent_time_to_relax",
                        "time_to_relax",
                    ],
                ),
                n=len(sub),
                default=10**9,
            )
            .fillna(10**9)
            .to_numpy()
        )
        t_adverse = (
            _numeric_any(
                sub,
                _first_existing(
                    sub, ["time_to_adverse", "time_to_secondary_shock", "time_to_tail_move"]
                ),
                n=len(sub),
                default=10**9,
            )
            .fillna(10**9)
            .to_numpy()
        )
        adverse_delta = -(t_adverse <= t_landmark).astype(float) * adverse
        exposure_delta = -np.clip(t_landmark / 96.0, 0.0, 1.0)
        opportunity_delta = exposure_delta * opp_value
        return adverse_delta, opportunity_delta, exposure_delta

    raise ValueError(f"Unsupported action: {action.name}")


def expectancy_from_effect_vectors(
    adverse_delta_vec: np.ndarray, opp_delta_vec: np.ndarray
) -> float:
    mean_adv = float(np.nanmean(adverse_delta_vec)) if len(adverse_delta_vec) else np.nan
    mean_opp = float(np.nanmean(opp_delta_vec)) if len(opp_delta_vec) else np.nan
    if not np.isfinite(mean_adv):
        return 0.0
    risk_reduction = float(-mean_adv)
    opportunity_cost = float(max(0.0, -mean_opp)) if np.isfinite(mean_opp) else 0.0
    net_benefit = float(risk_reduction - opportunity_cost)
    return float(net_benefit) if np.isfinite(net_benefit) else 0.0


def expectancy_for_action(sub: pd.DataFrame, action: ActionSpec) -> float:
    if sub.empty:
        return 0.0
    if action.name in {"no_action", "delay_0"}:
        base_expectancy = pd.to_numeric(sub.get("expectancy_proxy"), errors="coerce")
        if base_expectancy.notna().any():
            return float(base_expectancy.mean())
        opp = pd.to_numeric(sub.get("opportunity_proxy_excess"), errors="coerce")
        adv = pd.to_numeric(sub.get("adverse_proxy_excess"), errors="coerce")
        proxy = opp.fillna(0.0) - adv.fillna(0.0)
        return float(proxy.mean()) if len(proxy) else 0.0
    adverse_delta_vec, opp_delta_vec, _ = apply_action_proxy(sub, action)
    return expectancy_from_effect_vectors(adverse_delta_vec, opp_delta_vec)


def combine_with_delay_override(sub: pd.DataFrame, action: ActionSpec, delay_bars: int) -> float:
    if sub.empty:
        return 0.0
    base_value = expectancy_for_action(sub, action)
    if int(delay_bars) <= 0:
        return base_value
    delay_action = ActionSpec(
        name=f"delay_{int(delay_bars)}",
        family="timing",
        params={"delay_bars": int(delay_bars)},
    )
    delay_adv, delay_opp, _ = apply_action_proxy(sub, delay_action)
    delay_delta = expectancy_from_effect_vectors(delay_adv, delay_opp)
    return float(base_value + delay_delta)


def compute_drawdown_profile(pnl: np.ndarray) -> float:
    arr = np.asarray(pnl, dtype=float)
    arr = arr[np.isfinite(arr)]
    if len(arr) == 0:
        return 0.0
    cum = np.cumsum(arr)
    running_peak = np.maximum.accumulate(cum)
    drawdown = cum - running_peak
    return float(np.min(drawdown)) if len(drawdown) else 0.0
