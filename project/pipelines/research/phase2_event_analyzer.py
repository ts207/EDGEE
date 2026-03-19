from __future__ import annotations
from project.core.config import get_data_root

import logging
from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple

import numpy as np
import pandas as pd

from project.core.feature_schema import feature_dataset_dir_name
from project.io.utils import (
    choose_partition_dir,
    list_parquet_files,
    read_parquet,
    run_scoped_lake_path,
)
from project.spec_registry import load_global_defaults

LOGGER = logging.getLogger(__name__)
MAX_DYNAMIC_CONDITIONS_PER_COLUMN = 12


@dataclass(frozen=True)
class ConditionSpec:
    name: str
    description: str
    mask_fn: Callable[[pd.DataFrame], pd.Series]


@dataclass(frozen=True)
class ActionSpec:
    name: str
    family: str
    params: Dict[str, object]


def _first_existing(df: pd.DataFrame, candidates: List[str]) -> str | None:
    for name in candidates:
        if name in df.columns:
            return name
    return None


def _numeric_non_negative(df: pd.DataFrame, col: str | None, n: int) -> pd.Series:
    if col is None:
        return pd.Series(0.0, index=df.index)
    out = pd.to_numeric(df[col], errors="coerce").fillna(0.0).astype(float).clip(lower=0.0)
    if len(out) != n:
        return pd.Series(0.0, index=df.index)
    return out


def _numeric_any(df: pd.DataFrame, col: str | None, n: int, default: float = np.nan) -> pd.Series:
    if col is None:
        return pd.Series(default, index=df.index)
    out = pd.to_numeric(df[col], errors="coerce").astype(float)
    if len(out) != n:
        return pd.Series(default, index=df.index)
    return out


def build_conditions(events: pd.DataFrame) -> List[ConditionSpec]:
    conds: List[ConditionSpec] = [
        ConditionSpec("all", "all events", lambda d: pd.Series(True, index=d.index))
    ]

    try:
        defaults = load_global_defaults()
        if not isinstance(defaults, dict):
            raise ValueError("global defaults spec must decode to a mapping")
        config_cols = defaults.get("defaults", {}).get("conditioning_cols", [])
        if not isinstance(config_cols, list):
            raise ValueError("defaults.conditioning_cols must be a list")
    except Exception as exc:
        raise RuntimeError(f"Failed to load conditioning config from spec registry: {exc}") from exc

    # Add dynamic categorical conditions from events columns
    for col in config_cols:
        if col in events.columns:
            # Skip handled specially
            if col in ["tod_bucket", "anchor_hour", "t_rv_peak"]:
                continue

            value_counts = events[col].dropna().astype(str).value_counts()
            unique_vals = sorted(
                value_counts.index.tolist(), key=lambda v: (-int(value_counts.get(v, 0)), str(v))
            )
            if len(unique_vals) > MAX_DYNAMIC_CONDITIONS_PER_COLUMN:
                LOGGER.warning(
                    "Capping dynamic conditions for %s at %d of %d distinct values",
                    col,
                    MAX_DYNAMIC_CONDITIONS_PER_COLUMN,
                    len(unique_vals),
                )
                unique_vals = unique_vals[:MAX_DYNAMIC_CONDITIONS_PER_COLUMN]
            for val in unique_vals:
                if val == "nan":
                    continue
                conds.append(
                    ConditionSpec(
                        name=f"{col}_{val}",
                        description=f"{col} == {val}",
                        mask_fn=lambda d, c=col, v=val: d[c].astype(str) == v,
                    )
                )

    if "tod_bucket" in events.columns:
        conds.extend(
            [
                ConditionSpec(
                    "session_asia",
                    "enter hour in [0,7]",
                    lambda d: d["tod_bucket"].between(0, 7, inclusive="both"),
                ),
                ConditionSpec(
                    "session_eu",
                    "enter hour in [8,15]",
                    lambda d: d["tod_bucket"].between(8, 15, inclusive="both"),
                ),
                ConditionSpec(
                    "session_us",
                    "enter hour in [16,23]",
                    lambda d: d["tod_bucket"].between(16, 23, inclusive="both"),
                ),
            ]
        )
    elif "anchor_hour" in events.columns:
        conds.extend(
            [
                ConditionSpec(
                    "session_asia",
                    "enter hour in [0,7]",
                    lambda d: d["anchor_hour"].between(0, 7, inclusive="both"),
                ),
                ConditionSpec(
                    "session_eu",
                    "enter hour in [8,15]",
                    lambda d: d["anchor_hour"].between(8, 15, inclusive="both"),
                ),
                ConditionSpec(
                    "session_us",
                    "enter hour in [16,23]",
                    lambda d: d["anchor_hour"].between(16, 23, inclusive="both"),
                ),
            ]
        )

    if "t_rv_peak" in events.columns:
        conds.extend(
            [
                ConditionSpec(
                    "age_bucket_0_8",
                    "t_rv_peak in [0,8]",
                    lambda d: d["t_rv_peak"].fillna(10**9).between(0, 8, inclusive="both"),
                ),
                ConditionSpec(
                    "age_bucket_9_30",
                    "t_rv_peak in [9,30]",
                    lambda d: d["t_rv_peak"].fillna(10**9).between(9, 30, inclusive="both"),
                ),
                ConditionSpec(
                    "age_bucket_31_96",
                    "t_rv_peak in [31,96]",
                    lambda d: d["t_rv_peak"].fillna(10**9).between(31, 96, inclusive="both"),
                ),
            ]
        )
    if "rv_decay_half_life" in events.columns:
        conds.append(
            ConditionSpec(
                "near_half_life",
                "rv_decay_half_life <= 30",
                lambda d: d["rv_decay_half_life"].fillna(10**9) <= 30,
            )
        )
    if {"t_rv_peak", "duration_bars"}.issubset(events.columns):
        conds.extend(
            [
                ConditionSpec(
                    "fractional_age_0_33",
                    "t_rv_peak / duration_bars <= 0.33",
                    lambda d: (
                        (
                            d["t_rv_peak"].fillna(10**9) / d["duration_bars"].replace(0, np.nan)
                        ).fillna(10**9)
                        <= 0.33
                    ),
                ),
                ConditionSpec(
                    "fractional_age_34_66",
                    "t_rv_peak / duration_bars in (0.33, 0.66]",
                    lambda d: (
                        (
                            (
                                d["t_rv_peak"].fillna(10**9) / d["duration_bars"].replace(0, np.nan)
                            ).fillna(10**9)
                            > 0.33
                        )
                        & (
                            (
                                d["t_rv_peak"].fillna(10**9) / d["duration_bars"].replace(0, np.nan)
                            ).fillna(10**9)
                            <= 0.66
                        )
                    ),
                ),
                ConditionSpec(
                    "fractional_age_67_100",
                    "t_rv_peak / duration_bars > 0.66",
                    lambda d: (
                        (
                            d["t_rv_peak"].fillna(10**9) / d["duration_bars"].replace(0, np.nan)
                        ).fillna(10**9)
                        > 0.66
                    ),
                ),
            ]
        )

    seen = set()
    out = []
    for cond in conds:
        if cond.name in seen:
            continue
        seen.add(cond.name)
        out.append(cond)
    return out


def build_actions() -> List[ActionSpec]:
    return [
        ActionSpec("no_action", "baseline", {}),
        ActionSpec("entry_gate_skip", "entry_gating", {"k": 0.0}),
        ActionSpec("risk_throttle_0.5", "risk_throttle", {"k": 0.5}),
        ActionSpec("risk_throttle_0", "risk_throttle", {"k": 0.0}),
        ActionSpec("delay_0", "timing", {"delay_bars": 0}),
        ActionSpec("delay_8", "timing", {"delay_bars": 8}),
        ActionSpec("delay_30", "timing", {"delay_bars": 30}),
        ActionSpec("reenable_at_half_life", "timing", {"landmark": "rv_decay_half_life"}),
    ]


def candidate_type_from_action(action_name: str) -> str:
    action = str(action_name or "").strip().lower()
    if action == "entry_gate_skip" or action.startswith("risk_throttle_"):
        return "overlay"
    if action == "no_action" or action.startswith("delay_") or action == "reenable_at_half_life":
        return "standalone"
    return "standalone"


def assign_candidate_types_and_overlay_bases(
    candidates: pd.DataFrame, event_type: str
) -> pd.DataFrame:
    if candidates.empty:
        return candidates
    out = candidates.copy()
    action_series = (
        out["action"] if "action" in out.columns else pd.Series("", index=out.index, dtype=str)
    )
    out["candidate_type"] = action_series.astype(str).map(candidate_type_from_action)
    out["overlay_base_candidate_id"] = ""

    no_action_rows = out[action_series.astype(str) == "no_action"]
    base_by_condition: Dict[str, str] = {}
    for _, row in no_action_rows.iterrows():
        cond = str(row.get("condition", "")).strip()
        candidate_id = str(row.get("candidate_id", "")).strip()
        if cond and candidate_id and cond not in base_by_condition:
            base_by_condition[cond] = candidate_id
    fallback_base = f"BASE_TEMPLATE::{str(event_type).strip().lower()}"
    overlay_mask = out["candidate_type"].astype(str) == "overlay"
    for idx in out[overlay_mask].index:
        condition = str(out.at[idx, "condition"]).strip() if "condition" in out.columns else ""
        out.at[idx, "overlay_base_candidate_id"] = base_by_condition.get(condition, fallback_base)
    return out


def attach_forward_opportunity(
    events: pd.DataFrame,
    controls: pd.DataFrame,
    run_id: str,
    symbols: List[str],
    timeframe: str,
    horizon_bars: int,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    DATA_ROOT = get_data_root()
    if events.empty:
        return events, controls

    out_events = events.copy()
    out_controls = controls.copy()
    if "enter_ts" not in out_events.columns:
        for col in ["anchor_ts", "timestamp"]:
            if col in out_events.columns:
                out_events["enter_ts"] = out_events[col]
                break
    if "enter_idx" not in out_events.columns and "start_idx" in out_events.columns:
        out_events["enter_idx"] = pd.to_numeric(out_events["start_idx"], errors="coerce")
    out_events["enter_ts"] = pd.to_datetime(out_events.get("enter_ts"), utc=True, errors="coerce")

    rows = []
    for symbol in symbols:
        bars_candidates = [
            run_scoped_lake_path(DATA_ROOT, run_id, "cleaned", "perp", symbol, f"bars_{timeframe}"),
            DATA_ROOT / "lake" / "cleaned" / "perp" / symbol / f"bars_{timeframe}",
        ]
        bars_dir = choose_partition_dir(bars_candidates)
        bars = read_parquet(list_parquet_files(bars_dir)) if bars_dir else pd.DataFrame()
        if bars.empty:
            continue
        bars["timestamp"] = pd.to_datetime(bars["timestamp"], utc=True, errors="coerce")
        bars = bars.dropna(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
        dupes = int(bars["timestamp"].duplicated(keep="last").sum())
        if dupes > 0:
            logging.warning(
                "Dropping %s duplicate bars for %s (%s) before forward opportunity join.",
                dupes,
                symbol,
                timeframe,
            )
            bars = bars.drop_duplicates(subset=["timestamp"], keep="last").reset_index(drop=True)
        close = bars["close"].astype(float)
        fwd_abs_return = (close.shift(-horizon_bars) / close - 1.0).abs()
        rows.append(
            pd.DataFrame(
                {
                    "symbol": symbol,
                    "bar_idx": np.arange(len(bars), dtype=int),
                    "timestamp": bars["timestamp"],
                    "forward_abs_return_h": fwd_abs_return,
                }
            )
        )

    if not rows:
        out_events["forward_abs_return_h"] = np.nan
        out_events["forward_abs_return_h_ctrl"] = np.nan
        out_events["opportunity_value_excess"] = np.nan
        return out_events, out_controls

    fwd = pd.concat(rows, ignore_index=True)
    fwd_ts = fwd.rename(columns={"timestamp": "enter_ts"})

    out_events = out_events.merge(
        fwd_ts[["symbol", "enter_ts", "forward_abs_return_h"]],
        on=["symbol", "enter_ts"],
        how="left",
        validate="many_to_one",
    )
    if "enter_idx" in out_events.columns:
        out_events = out_events.merge(
            fwd[["symbol", "bar_idx", "forward_abs_return_h"]].rename(
                columns={"bar_idx": "enter_idx", "forward_abs_return_h": "forward_abs_return_h_idx"}
            ),
            on=["symbol", "enter_idx"],
            how="left",
            validate="many_to_one",
        )
        out_events["forward_abs_return_h"] = out_events["forward_abs_return_h"].where(
            out_events["forward_abs_return_h"].notna(),
            out_events["forward_abs_return_h_idx"],
        )
        out_events = out_events.drop(columns=["forward_abs_return_h_idx"])

    if (
        not out_controls.empty
        and "event_id" in out_controls.columns
        and "control_idx" in out_controls.columns
    ):
        event_to_symbol = out_events[["event_id", "symbol"]].drop_duplicates()
        if "symbol" not in out_controls.columns:
            out_controls = out_controls.merge(
                event_to_symbol, on="event_id", how="left", validate="many_to_one"
            )
        else:
            out_controls = out_controls.merge(
                event_to_symbol.rename(columns={"symbol": "event_symbol"}),
                on="event_id",
                how="left",
                validate="many_to_one",
            )
            out_controls["symbol"] = out_controls["symbol"].where(
                out_controls["symbol"].notna(),
                out_controls["event_symbol"],
            )
            out_controls = out_controls.drop(columns=["event_symbol"])

        if "symbol" in out_controls.columns:
            out_controls = out_controls.merge(
                fwd[["symbol", "bar_idx", "forward_abs_return_h"]].rename(
                    columns={
                        "bar_idx": "control_idx",
                        "forward_abs_return_h": "forward_abs_return_h_ctrl_row",
                    }
                ),
                on=["symbol", "control_idx"],
                how="left",
                validate="many_to_one",
            )
            ctrl_mean = out_controls.groupby("event_id", as_index=False)[
                "forward_abs_return_h_ctrl_row"
            ].mean()
            out_events = out_events.merge(
                ctrl_mean.rename(
                    columns={"forward_abs_return_h_ctrl_row": "forward_abs_return_h_ctrl"}
                ),
                on="event_id",
                how="left",
            )
        else:
            out_events["forward_abs_return_h_ctrl"] = np.nan
    else:
        out_events["forward_abs_return_h_ctrl"] = np.nan

    out_events["opportunity_value_excess"] = (
        out_events["forward_abs_return_h"] - out_events["forward_abs_return_h_ctrl"]
    )
    out_events["opportunity_value_excess"] = out_events["opportunity_value_excess"].where(
        out_events["opportunity_value_excess"].notna(),
        out_events["forward_abs_return_h"],
    )
    return out_events, out_controls



from project.pipelines.research.phase2_event_analyzer_support import (
    attach_event_market_features,
    prepare_baseline,
    apply_action_proxy,
    expectancy_from_effect_vectors,
    expectancy_for_action,
    combine_with_delay_override,
    compute_drawdown_profile,
)
