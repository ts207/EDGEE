"""Helper functions for validate_expectancy_traps (split to stay under 800-LOC gate)."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

try:
    from scipy import stats as scipy_stats
except ModuleNotFoundError:
    scipy_stats = None

from project.core.config import get_data_root

log = logging.getLogger(__name__)

class CompressionEvent:
    symbol: str
    start_idx: int
    end_idx: int
    end_reason: str
    trend_state: int
    funding_bucket: str
    year: int
    vol_q: str
    bull_bear: str
    enter_ts: pd.Timestamp


EVENT_ROW_COLUMNS = [
    "symbol",
    "event_start_idx",
    "enter_ts",
    "split_label",
    "year",
    "vol_q",
    "bull_bear",
    "funding_bucket",
    "horizon",
    "end_reason",
    "trend_state",
    "breakout_dir",
    "breakout_aligns_htf",
    "time_to_expansion_bars",
    "mfe_post_end",
    "event_return",
    "event_directional_return",
]

ROBUST_GATE_PROFILES: Dict[str, Dict[str, float | int]] = {
    "discovery": {
        "min_samples": 60,
        "tstat_threshold": 1.64,
        "robust_hac_t_threshold": 1.64,
        "robust_bootstrap_alpha": 0.20,
        "robust_fdr_q": 0.20,
        "robust_hac_max_lag": 8,
        "robust_bootstrap_iters": 400,
        "robust_bootstrap_block_size": 8,
        "robust_bootstrap_seed": 7,
        "oos_min_samples": 20,
        "require_oos_positive": 1,
        "require_oos_sign_consistency": 0,
    },
    "synthetic": {
        "min_samples": 8,
        "tstat_threshold": 0.5,
        "robust_hac_t_threshold": 0.5,
        "robust_bootstrap_alpha": 0.40,
        "robust_fdr_q": 0.40,
        "robust_hac_max_lag": 4,
        "robust_bootstrap_iters": 100,
        "robust_bootstrap_block_size": 4,
        "robust_bootstrap_seed": 7,
        "oos_min_samples": 4,
        "require_oos_positive": 0,
        "require_oos_sign_consistency": 0,
    },
    "promotion": {
        "min_samples": 100,
        "tstat_threshold": 2.0,
        "robust_hac_t_threshold": 1.96,
        "robust_bootstrap_alpha": 0.10,
        "robust_fdr_q": 0.10,
        "robust_hac_max_lag": 12,
        "robust_bootstrap_iters": 800,
        "robust_bootstrap_block_size": 8,
        "robust_bootstrap_seed": 7,
        "oos_min_samples": 40,
        "require_oos_positive": 1,
        "require_oos_sign_consistency": 1,
    },
}


def _apply_gate_profile_defaults(args: argparse.Namespace) -> argparse.Namespace:
    profile = str(getattr(args, "gate_profile", "custom")).strip().lower()
    if profile == "custom":
        return args
    overrides = ROBUST_GATE_PROFILES.get(profile)
    if not overrides:
        raise ValueError(f"Unknown gate profile: {profile}")
    for key, value in overrides.items():
        setattr(args, key, value)
    return args


def _newey_west_t_stat(series: pd.Series, max_lag: int) -> Tuple[float, float, int]:
    result = newey_west_t_stat_for_mean(series.to_numpy(), max_lag=max_lag)
    t_stat = float(result.t_stat)
    if not np.isfinite(t_stat):
        return 0.0, 1.0, int(result.lag)
    p_value = float(2.0 * (1.0 - 0.5 * (1.0 + math.erf(abs(t_stat) / math.sqrt(2.0)))))
    return t_stat, p_value, int(result.lag)


def _circular_block_bootstrap_pvalue(
    series: pd.Series,
    *,
    block_size: int,
    n_boot: int,
    seed: int,
) -> float:
    return float(
        circular_block_bootstrap_pvalue(
            series,
            block_size=int(block_size),
            n_boot=int(n_boot),
            seed=int(seed),
        )
    )


def _apply_robust_survivor_gates(
    df: pd.DataFrame,
    **kwargs,
) -> pd.DataFrame:
    return apply_robust_survivor_gates(df, **kwargs)


def _robust_row_fields(
    *,
    event_frame: pd.DataFrame,
    ret_col: str,
    condition: str,
    horizon: int,
    hac_max_lag: int,
    bootstrap_block_size: int,
    bootstrap_iters: int,
    bootstrap_seed: int,
    oos_min_samples: int,
    require_oos_positive: int,
    require_oos_sign_consistency: int,
) -> Dict[str, object]:
    series = (
        pd.to_numeric(event_frame[ret_col], errors="coerce")
        if ret_col in event_frame.columns
        else pd.Series(dtype=float)
    )
    hac_res = newey_west_t_stat_for_mean(series.to_numpy(), max_lag=hac_max_lag)

    # P-value from T-stat using normal approximation if student-t is not available
    def _p_from_t(t: float) -> float:
        if not np.isfinite(t):
            return 1.0
        return 2.0 * (1.0 - 0.5 * (1.0 + math.erf(abs(t) / math.sqrt(2.0))))

    hac_p = _p_from_t(hac_res.t_stat)

    boot_seed = stable_row_seed(condition=condition, horizon=horizon, base_seed=bootstrap_seed)
    bootstrap_p = circular_block_bootstrap_pvalue(
        series,
        block_size=int(bootstrap_block_size),
        n_boot=int(bootstrap_iters),
        seed=boot_seed,
    )
    oos = oos_diagnostics(
        event_frame,
        ret_col=ret_col,
        oos_min_samples=int(oos_min_samples),
        require_oos_positive=int(require_oos_positive),
        require_oos_sign_consistency=int(require_oos_sign_consistency),
    )
    return {
        "hac_t": float(hac_res.t_stat),
        "hac_p": float(hac_p),
        "hac_used_lag": int(hac_res.lag),
        "bootstrap_p": float(bootstrap_p),
        **oos,
    }


def _load_symbol_features(symbol: str, run_id: str) -> pd.DataFrame:
    DATA_ROOT = get_data_root()
    feature_dataset = feature_dataset_dir_name()
    candidates = [
        run_scoped_lake_path(DATA_ROOT, run_id, "features", "perp", symbol, "5m", feature_dataset),
        DATA_ROOT / "lake" / "features" / "perp" / symbol / "5m" / feature_dataset,
    ]
    features_dir = choose_partition_dir(candidates)
    files = list_parquet_files(features_dir) if features_dir else []
    if not files:
        raise ValueError(f"No features found for {symbol}: {candidates[0]}")
    df = read_parquet(files)
    if df.empty:
        raise ValueError(f"Empty features for {symbol}")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    return df.sort_values("timestamp").reset_index(drop=True)


def _build_features(
    df: pd.DataFrame, htf_window: int, htf_lookback: int, funding_pct_window: int
) -> pd.DataFrame:
    rv_pct_col = pick_window_column(df.columns, "rv_pct_")
    range_med_col = pick_window_column(df.columns, "range_med_")

    close = df["close"].astype(float)
    htf_ma = close.rolling(window=htf_window, min_periods=htf_window).mean()
    htf_delta = htf_ma - htf_ma.shift(htf_lookback)
    trend_state = pd.Series(
        np.where(htf_delta > 0, 1, np.where(htf_delta < 0, -1, 0)), index=df.index
    )

    funding_pct = rolling_percentile(df["funding_rate_scaled"].astype(float), funding_pct_window)
    funding_bucket = pd.Series(
        np.select(
            [funding_pct <= 20, funding_pct >= 80],
            ["low", "high"],
            default="mid",
        ),
        index=df.index,
    ).where(funding_pct.notna())

    compression = ((df[rv_pct_col] <= 10.0) & (df["range_96"] <= 0.8 * df[range_med_col])).fillna(
        False
    )

    out = df.copy()
    out["trend_state"] = trend_state
    out["funding_bucket"] = funding_bucket
    out["compression"] = compression
    out["prior_high_96"] = out["high_96"].shift(1)
    out["prior_low_96"] = out["low_96"].shift(1)
    out["breakout_up"] = out["close"] > out["prior_high_96"]
    out["breakout_down"] = out["close"] < out["prior_low_96"]
    out["breakout_any"] = out["breakout_up"] | out["breakout_down"]
    out["vol_q"] = pd.qcut(out["rv_96"], q=4, labels=["Q1", "Q2", "Q3", "Q4"], duplicates="drop")
    out["bull_bear"] = np.where(close / close.shift(96) - 1.0 >= 0, "bull", "bear")
    return out


def _leakage_check(df: pd.DataFrame, htf_window: int, htf_lookback: int) -> Dict[str, object]:
    close = df["close"].astype(float)
    full_ma = close.rolling(window=htf_window, min_periods=htf_window).mean()
    full_delta = full_ma - full_ma.shift(htf_lookback)
    full_trend = pd.Series(
        np.where(full_delta > 0, 1, np.where(full_delta < 0, -1, 0)), index=df.index
    )

    rng = np.random.default_rng(7)
    candidates = np.arange(htf_window + htf_lookback, len(df))
    if len(candidates) == 0:
        return {"pass": False, "checked": 0, "mismatches": 0}
    sample = rng.choice(candidates, size=min(500, len(candidates)), replace=False)

    mismatches = 0
    for i in sample:
        partial = close.iloc[: i + 1]
        ma = partial.rolling(window=htf_window, min_periods=htf_window).mean()
        delta = ma - ma.shift(htf_lookback)
        trend_i = int(np.sign(delta.iloc[-1])) if pd.notna(delta.iloc[-1]) else 0
        if trend_i != int(full_trend.iloc[i]):
            mismatches += 1
    return {"pass": mismatches == 0, "checked": int(len(sample)), "mismatches": int(mismatches)}


def _extract_compression_events(
    df: pd.DataFrame, symbol: str, max_duration: int
) -> List[CompressionEvent]:
    events: List[CompressionEvent] = []
    n = len(df)
    i = 1
    while i < n:
        if not bool(df.at[i, "compression"]) or bool(df.at[i - 1, "compression"]):
            i += 1
            continue

        start = i
        max_end = min(n - 1, start + max_duration - 1)
        end = start
        end_reason = "max_duration"

        j = start
        while j <= max_end:
            if bool(df.at[j, "breakout_any"]):
                end = j
                end_reason = "breakout"
                break
            if not bool(df.at[j, "compression"]):
                end = j
                end_reason = "compression_off"
                break
            end = j
            j += 1

        ts = df.at[start, "timestamp"]
        vol_q = df.at[start, "vol_q"]
        events.append(
            CompressionEvent(
                symbol=symbol,
                start_idx=start,
                end_idx=end,
                end_reason=end_reason,
                trend_state=int(df.at[start, "trend_state"])
                if pd.notna(df.at[start, "trend_state"])
                else 0,
                funding_bucket=str(df.at[start, "funding_bucket"])
                if pd.notna(df.at[start, "funding_bucket"])
                else "na",
                year=int(ts.year),
                vol_q=str(vol_q) if pd.notna(vol_q) else "na",
                bull_bear=str(df.at[start, "bull_bear"]),
                enter_ts=pd.to_datetime(ts, utc=True),
            )
        )
        i = end + 1
    return events


def _first_expansion_after(df: pd.DataFrame, idx: int, lookahead: int) -> Tuple[int | None, int]:
    n = len(df)
    end = min(n - 1, idx + lookahead)
    for j in range(idx + 1, end + 1):
        if bool(df.at[j, "breakout_up"]):
            return j, 1
        if bool(df.at[j, "breakout_down"]):
            return j, -1
    return None, 0


def _event_rows(
    df: pd.DataFrame,
    events: List[CompressionEvent],
    horizons: List[int],
    expansion_lookahead: int,
    mfe_horizon: int,
) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    close = df["close"].to_numpy(dtype=float)
    high = df["high"].to_numpy(dtype=float)
    low = df["low"].to_numpy(dtype=float)
    n = len(df)

    for ev in events:
        expansion_idx = ev.end_idx if bool(df.at[ev.end_idx, "breakout_any"]) else None
        breakout_dir = (
            1
            if bool(df.at[ev.end_idx, "breakout_up"])
            else -1
            if bool(df.at[ev.end_idx, "breakout_down"])
            else 0
        )
        if expansion_idx is None:
            expansion_idx, breakout_dir = _first_expansion_after(
                df, ev.end_idx, expansion_lookahead
            )

        time_to_expansion = (expansion_idx - ev.start_idx) if expansion_idx is not None else np.nan
        aligns = (
            bool(breakout_dir == ev.trend_state)
            if breakout_dir != 0 and ev.trend_state != 0
            else np.nan
        )

        mfe = np.nan
        mfe_end = min(n - 1, ev.end_idx + mfe_horizon)
        if breakout_dir != 0 and ev.end_idx + 1 <= mfe_end:
            entry = close[ev.end_idx]
            if breakout_dir > 0:
                mfe = float(np.nanmax(high[ev.end_idx + 1 : mfe_end + 1]) / entry - 1.0)
            else:
                mfe = float(entry / np.nanmin(low[ev.end_idx + 1 : mfe_end + 1]) - 1.0)

        for h in horizons:
            if ev.end_idx + h >= n:
                continue
            ret = float(close[ev.end_idx + h] / close[ev.end_idx] - 1.0)
            directional_ret = float(ret * ev.trend_state) if ev.trend_state != 0 else np.nan
            rows.append(
                {
                    "symbol": ev.symbol,
                    "event_start_idx": ev.start_idx,
                    "enter_ts": ev.enter_ts,
                    "split_label": "",
                    "year": ev.year,
                    "vol_q": ev.vol_q,
                    "bull_bear": ev.bull_bear,
                    "funding_bucket": ev.funding_bucket,
                    "horizon": h,
                    "end_reason": ev.end_reason,
                    "trend_state": ev.trend_state,
                    "breakout_dir": breakout_dir,
                    "breakout_aligns_htf": aligns,
                    "time_to_expansion_bars": time_to_expansion,
                    "mfe_post_end": mfe,
                    "event_return": ret,
                    "event_directional_return": directional_ret,
                }
            )
    return rows


def _split_sign_report(events: pd.DataFrame, col: str, ret_col: str) -> Dict[str, object]:
    if events.empty:
        return {"stable_sign": False, "groups": {}}
    grouped = events.groupby(col, dropna=False)[ret_col].mean().dropna()
    groups = {str(k): float(v) for k, v in grouped.items()}
    if grouped.empty:
        return {"stable_sign": False, "groups": groups}
    positive = grouped > 0
    stable_sign = bool(positive.all() or (~positive).all())
    return {"stable_sign": stable_sign, "groups": groups}


def _bar_condition_stats(df: pd.DataFrame, condition: str, horizon: int) -> Dict[str, float]:
    close = df["close"].astype(float)
    fwd = close.shift(-horizon) / close - 1.0

    if condition == "compression":
        mask = df["compression"]
        ret = fwd.where(mask)
    elif condition == "compression_plus_htf_trend":
        mask = df["compression"] & (df["trend_state"] != 0)
        ret = (fwd * df["trend_state"]).where(mask)
    elif condition == "compression_plus_funding_low":
        mask = df["compression"] & (df["funding_bucket"] == "low")
        ret = fwd.where(mask)
    else:
        raise ValueError(f"Unknown condition: {condition}")

    return distribution_stats(ret)


def _event_condition_frame(
    events_df: pd.DataFrame, condition: str, horizon: int
) -> Tuple[pd.DataFrame, str]:
    ret_col = (
        "event_directional_return" if condition == "compression_plus_htf_trend" else "event_return"
    )

    if events_df.empty or "horizon" not in events_df.columns:
        return pd.DataFrame(columns=EVENT_ROW_COLUMNS), ret_col

    frame = events_df[events_df["horizon"] == horizon].copy()
    if condition == "compression":
        pass
    elif condition == "compression_plus_htf_trend":
        frame = frame[frame["trend_state"] != 0]
    elif condition == "compression_plus_funding_low":
        frame = frame[frame["funding_bucket"] == "low"]
    else:
        raise ValueError(f"Unknown condition: {condition}")

    return frame, ret_col


def _split_overlap_diagnostics(events_df: pd.DataFrame, embargo_bars: int) -> Dict[str, object]:
    if events_df.empty:
        return {"pass": False, "embargo_bars": int(embargo_bars), "details": []}

    unique_events = events_df.drop_duplicates(subset=["symbol", "event_start_idx"]).copy()
    details: List[Dict[str, object]] = []
    global_pass = True

    for symbol, group in unique_events.groupby("symbol", dropna=False):
        g = group.sort_values("event_start_idx").reset_index(drop=True)
        boundary_gaps: Dict[str, int] = {}
        for left, right in [("train", "validation"), ("validation", "test")]:
            left_idx = g.index[g["split_label"] == left]
            right_idx = g.index[g["split_label"] == right]
            if len(left_idx) == 0 or len(right_idx) == 0:
                boundary_gaps[f"{left}_to_{right}"] = -1
                global_pass = False
                continue
            gap = int(right_idx.min() - left_idx.max() - 1)
            boundary_gaps[f"{left}_to_{right}"] = gap
            if gap < int(embargo_bars):
                global_pass = False

        details.append({"symbol": str(symbol), "boundary_gaps": boundary_gaps})

    return {"pass": bool(global_pass), "embargo_bars": int(embargo_bars), "details": details}


def _parameter_stability_diagnostics(
    trap_df: pd.DataFrame,
    *,
    base_min_samples: int,
    base_tstat_threshold: float,
    sample_delta: int,
    tstat_delta: float,
) -> Dict[str, object]:
    if trap_df.empty:
        return {
            "pass": False,
            "rank_consistency": 0.0,
            "performance_decay": 1.0,
            "neighborhood_supported": False,
            "scenarios": [],
        }

    scenarios = [
        {
            "name": "base",
            "min_samples": int(base_min_samples),
            "tstat": float(base_tstat_threshold),
        },
        {
            "name": "tight",
            "min_samples": int(base_min_samples + sample_delta),
            "tstat": float(base_tstat_threshold + tstat_delta),
        },
        {
            "name": "loose",
            "min_samples": max(1, int(base_min_samples - sample_delta)),
            "tstat": max(0.0, float(base_tstat_threshold - tstat_delta)),
        },
    ]

    def _survivor_frame(min_samples: int, tstat: float) -> pd.DataFrame:
        sub = trap_df[
            (trap_df["event_samples"] >= min_samples)
            & (trap_df["event_mean"] > 0)
            & (trap_df["event_t"] >= tstat)
        ]
        return sub.copy()

    def _survivor_set(sub: pd.DataFrame) -> set[str]:
        return {f"{r.condition}|{int(r.horizon)}" for r in sub.itertuples(index=False)}

    base_sub = _survivor_frame(int(base_min_samples), float(base_tstat_threshold))
    base_set = _survivor_set(base_sub)
    rows = []
    overlap_scores = []
    scenario_perf: Dict[str, float] = {}
    for sc in scenarios:
        sub = _survivor_frame(int(sc["min_samples"]), float(sc["tstat"]))
        sset = _survivor_set(sub)
        denom = max(1, len(base_set | sset))
        jaccard = float(len(base_set & sset) / denom)
        overlap_scores.append(jaccard)
        mean_perf = float(sub["event_mean"].mean()) if not sub.empty else np.nan
        scenario_perf[str(sc["name"])] = mean_perf
        rows.append(
            {
                **sc,
                "survivors": len(sset),
                "jaccard_to_base": jaccard,
                "mean_event_return": (None if np.isnan(mean_perf) else mean_perf),
            }
        )

    rank_consistency = float(np.mean(overlap_scores)) if overlap_scores else 0.0
    base_perf = scenario_perf.get("base", np.nan)
    valid_perf = [v for v in scenario_perf.values() if np.isfinite(v)]
    if np.isfinite(base_perf) and base_perf > 0.0 and valid_perf:
        worst_perf = float(min(valid_perf))
        performance_decay = float(max(0.0, (base_perf - worst_perf) / max(abs(base_perf), 1e-9)))
    else:
        performance_decay = 1.0

    neighborhood_supported = any(
        (row.get("name") != "base") and (int(row.get("survivors", 0)) > 0) for row in rows
    )
    passed = bool(
        len(base_set) > 0
        and neighborhood_supported
        and rank_consistency >= 0.3
        and performance_decay <= 1.0
    )
    return {
        "pass": passed,
        "rank_consistency": rank_consistency,
        "performance_decay": performance_decay,
        "neighborhood_supported": bool(neighborhood_supported),
        "scenarios": rows,
    }


