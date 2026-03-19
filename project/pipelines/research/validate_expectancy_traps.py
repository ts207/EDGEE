from __future__ import annotations
from project.core.config import get_data_root

import argparse
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np
import pandas as pd

from project.core.feature_schema import feature_dataset_dir_name
from project.io.utils import (
    choose_partition_dir,
    ensure_dir,
    list_parquet_files,
    read_parquet,
    run_scoped_lake_path,
)
from project.core.stats import (
    newey_west_t_stat_for_mean,
    bh_adjust,
)
from project.research.stats.expectancy import (
    distribution_stats,
    circular_block_bootstrap_pvalue,
    oos_diagnostics,
    apply_robust_survivor_gates,
    tail_report,
    capacity_diagnostics,
)
from project.pipelines.research.expectancy_traps_support import (
    load_expectancy_payload,
    parse_horizons,
    pick_window_column,
    rolling_percentile,
    stable_row_seed,
    write_empty_robustness_payload,
)
from project.eval import build_walk_forward_split_labels


from project.pipelines.research.validate_expectancy_traps_support import (
    CompressionEvent,
    _apply_gate_profile_defaults,
    _newey_west_t_stat,
    _circular_block_bootstrap_pvalue,
    _apply_robust_survivor_gates,
    _robust_row_fields,
    _load_symbol_features,
    _build_features,
    _leakage_check,
    _extract_compression_events,
    _first_expansion_after,
    _event_rows,
    _split_sign_report,
    _bar_condition_stats,
    _event_condition_frame,
    _split_overlap_diagnostics,
    _parameter_stability_diagnostics,
)

def main(argv: List[str] | None = None) -> int:
    DATA_ROOT = get_data_root()
    parser = argparse.ArgumentParser(description="Validate conditional expectancy.")
    parser.add_argument("--run_id", required=True)
    parser.add_argument("--symbols", required=True)
    parser.add_argument("--horizons", default="4,16,96")
    parser.add_argument("--htf_window", type=int, default=384)
    parser.add_argument("--htf_lookback", type=int, default=96)
    parser.add_argument("--funding_pct_window", type=int, default=2880)
    parser.add_argument("--max_event_duration", type=int, default=96)
    parser.add_argument("--expansion_lookahead", type=int, default=192)
    parser.add_argument("--mfe_horizon", type=int, default=96)
    parser.add_argument(
        "--gate_profile",
        choices=["discovery", "promotion", "custom", "synthetic"],
        default="discovery",
    )
    parser.add_argument("--retail_profile", default="capital_constrained")
    parser.add_argument("--tstat_threshold", type=float, default=2.0)
    parser.add_argument("--min_samples", type=int, default=100)
    parser.add_argument("--robust_hac_t_threshold", type=float, default=1.96)
    parser.add_argument("--robust_bootstrap_alpha", type=float, default=0.10)
    parser.add_argument("--robust_fdr_q", type=float, default=0.10)
    parser.add_argument("--robust_hac_max_lag", type=int, default=12)
    parser.add_argument("--robust_bootstrap_iters", type=int, default=800)
    parser.add_argument("--robust_bootstrap_block_size", type=int, default=8)
    parser.add_argument("--robust_bootstrap_seed", type=int, default=7)
    parser.add_argument("--oos_min_samples", type=int, default=40)
    parser.add_argument("--require_oos_positive", type=int, default=1)
    parser.add_argument("--require_oos_sign_consistency", type=int, default=1)
    parser.add_argument("--embargo_bars", type=int, default=0)
    parser.add_argument("--stability_sample_delta", type=int, default=20)
    parser.add_argument("--stability_tstat_delta", type=float, default=0.5)
    parser.add_argument("--capacity_min_events_per_day", type=float, default=0.5)
    parser.add_argument("--out_dir", default=None)
    args = parser.parse_args(argv)
    args = _apply_gate_profile_defaults(args)

    symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
    horizons = parse_horizons(args.horizons)

    out_dir = (
        Path(args.out_dir) if args.out_dir else DATA_ROOT / "reports" / "expectancy" / args.run_id
    )
    ensure_dir(out_dir)
    expectancy_payload = load_expectancy_payload(out_dir / "conditional_expectancy.json")
    if expectancy_payload and not bool(expectancy_payload.get("expectancy_exists", False)):
        return write_empty_robustness_payload(
            out_dir=out_dir,
            run_id=args.run_id,
            symbols=symbols,
            horizons=horizons,
            skip_reason="expectancy_analysis_reported_no_evidence",
        )

    leakage = {}
    all_bar_df = []
    all_event_rows: List[Dict[str, object]] = []
    event_summary_rows: List[Dict[str, object]] = []

    for symbol in symbols:
        df = _load_symbol_features(symbol, run_id=args.run_id)
        df = _build_features(df, args.htf_window, args.htf_lookback, args.funding_pct_window)
        leakage[symbol] = _leakage_check(df, args.htf_window, args.htf_lookback)
        events = _extract_compression_events(
            df, symbol=symbol, max_duration=args.max_event_duration
        )
        rows = _event_rows(
            df,
            events,
            horizons=horizons,
            expansion_lookahead=args.expansion_lookahead,
            mfe_horizon=args.mfe_horizon,
        )
        all_event_rows.extend(rows)
        all_bar_df.append(df)

        breakout_count = sum(1 for e in events if e.end_reason == "breakout")
        event_summary_rows.append(
            {
                "symbol": symbol,
                "event_count": len(events),
                "breakout_end_count": breakout_count,
                "breakout_end_rate": float(breakout_count / len(events)) if events else 0.0,
            }
        )

    master_bars = pd.concat(all_bar_df, ignore_index=True)
    events_df = pd.DataFrame(all_event_rows, columns=EVENT_ROW_COLUMNS)
    if not events_df.empty:
        events_df["enter_ts"] = pd.to_datetime(events_df["enter_ts"], utc=True, errors="coerce")
        events_df["split_label"] = build_walk_forward_split_labels(events_df, time_col="enter_ts")

    split_overlap = _split_overlap_diagnostics(events_df, embargo_bars=args.embargo_bars)

    conditions = ["compression", "compression_plus_htf_trend", "compression_plus_funding_low"]
    trap_rows = []
    split_rows = []
    tail_rows = []
    symmetry_rows = []
    expansion_rows = []

    rng = np.random.default_rng(11)

    for condition in conditions:
        for horizon in horizons:
            bar_stats = _bar_condition_stats(master_bars, condition, horizon)
            event_frame, ret_col = _event_condition_frame(events_df, condition, horizon)
            event_series = (
                event_frame[ret_col] if ret_col in event_frame else pd.Series(dtype=float)
            )
            event_stats = distribution_stats(event_series)
            robust_fields = _robust_row_fields(
                event_frame=event_frame,
                ret_col=ret_col,
                condition=condition,
                horizon=int(horizon),
                hac_max_lag=int(args.robust_hac_max_lag),
                bootstrap_block_size=int(args.robust_bootstrap_block_size),
                bootstrap_iters=int(args.robust_bootstrap_iters),
                bootstrap_seed=int(args.robust_bootstrap_seed),
                oos_min_samples=int(args.oos_min_samples),
                require_oos_positive=int(args.require_oos_positive),
                require_oos_sign_consistency=int(args.require_oos_sign_consistency),
            )

            trap_rows.append(
                {
                    "condition": condition,
                    "horizon": horizon,
                    "bar_samples": bar_stats["samples"],
                    "bar_mean": bar_stats["mean_return"],
                    "bar_t": bar_stats["t_stat"],
                    "event_samples": event_stats["samples"],
                    "event_mean": event_stats["mean_return"],
                    "event_t": event_stats["t_stat"],
                    **robust_fields,
                }
            )

            year_split = _split_sign_report(event_frame, "year", ret_col)
            vol_split = _split_sign_report(event_frame, "vol_q", ret_col)
            bull_split = _split_sign_report(event_frame, "bull_bear", ret_col)

            split_rows.append(
                {
                    "condition": condition,
                    "horizon": horizon,
                    "year_stable_sign": year_split["stable_sign"],
                    "vol_q_stable_sign": vol_split["stable_sign"],
                    "bull_bear_stable_sign": bull_split["stable_sign"],
                    "year_means": year_split["groups"],
                    "vol_q_means": vol_split["groups"],
                    "bull_bear_means": bull_split["groups"],
                }
            )

            tail = tail_report(
                event_frame[ret_col] if ret_col in event_frame else pd.Series(dtype=float)
            )
            tail_rows.append(
                {
                    "condition": condition,
                    "horizon": horizon,
                    "mean": event_stats["mean_return"],
                    "median": tail["median"],
                    "p25": tail["p25"],
                    "p75": tail["p75"],
                    "top_1pct_contribution": tail["top_1pct_contribution"],
                    "top_5pct_contribution": tail["top_5pct_contribution"],
                }
            )

            if condition == "compression_plus_htf_trend":
                base = event_frame[ret_col].dropna()
                opp = -base
                rand_sign = pd.Series(rng.choice([-1.0, 1.0], size=len(base)), index=base.index)
                rnd = base.abs() * rand_sign
                symmetry_rows.append(
                    {
                        "condition": condition,
                        "horizon": horizon,
                        "base_mean": float(base.mean()) if len(base) else 0.0,
                        "base_t": distribution_stats(base)["t_stat"],
                        "opposite_mean": float(opp.mean()) if len(opp) else 0.0,
                        "opposite_t": distribution_stats(opp)["t_stat"],
                        "random_mean": float(rnd.mean()) if len(rnd) else 0.0,
                        "random_t": distribution_stats(rnd)["t_stat"],
                    }
                )

        cond_all, _ = _event_condition_frame(events_df, condition, horizons[0])
        cond_all = (
            cond_all.drop_duplicates(
                subset=[
                    "symbol",
                    "year",
                    "vol_q",
                    "bull_bear",
                    "time_to_expansion_bars",
                    "mfe_post_end",
                    "trend_state",
                    "funding_bucket",
                    "end_reason",
                    "breakout_dir",
                ]
            )
            if not cond_all.empty
            else cond_all
        )
        expansion_rows.append(
            {
                "condition": condition,
                "events": int(len(cond_all)),
                "time_to_expansion_median": float(cond_all["time_to_expansion_bars"].median())
                if not cond_all.empty
                else np.nan,
                "time_to_expansion_p25": float(cond_all["time_to_expansion_bars"].quantile(0.25))
                if not cond_all.empty
                else np.nan,
                "time_to_expansion_p75": float(cond_all["time_to_expansion_bars"].quantile(0.75))
                if not cond_all.empty
                else np.nan,
                "mfe_median": float(cond_all["mfe_post_end"].median())
                if not cond_all.empty
                else np.nan,
                "mfe_mean": float(cond_all["mfe_post_end"].mean())
                if not cond_all.empty
                else np.nan,
                "breakout_align_rate": float(cond_all["breakout_aligns_htf"].dropna().mean())
                if not cond_all.empty
                else np.nan,
            }
        )

    trap_df = pd.DataFrame(trap_rows)
    trap_df = apply_robust_survivor_gates(
        trap_df,
        min_samples=int(args.min_samples),
        legacy_tstat_threshold=float(args.tstat_threshold),
        robust_hac_t_threshold=float(args.robust_hac_t_threshold),
        bootstrap_alpha=float(args.robust_bootstrap_alpha),
        fdr_q=float(args.robust_fdr_q),
        oos_min_samples=int(args.oos_min_samples),
        require_oos_positive=int(args.require_oos_positive),
        require_oos_sign_consistency=int(args.require_oos_sign_consistency),
    )

    stability = _parameter_stability_diagnostics(
        trap_df,
        base_min_samples=args.min_samples,
        base_tstat_threshold=args.tstat_threshold,
        sample_delta=args.stability_sample_delta,
        tstat_delta=args.stability_tstat_delta,
    )
    capacity = capacity_diagnostics(
        events_df, symbols=symbols, min_events_per_day=args.capacity_min_events_per_day
    )

    payload = {
        "run_id": args.run_id,
        "symbols": symbols,
        "horizons": horizons,
        "stability_diagnostics": stability,
        "capacity_diagnostics": capacity,
        "survivors": trap_df[trap_df["gate_robust_survivor"]].to_dict(orient="records"),
    }

    json_path = out_dir / "conditional_expectancy_robustness.json"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    print(f"Wrote {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
