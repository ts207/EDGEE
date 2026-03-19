"""Private helper functions for export_edge_candidates (split to stay under 800-LOC gate)."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import pandas as pd

from project.core.config import get_data_root
from project.core.timeframes import normalize_timeframe

def _is_missing_value(value: object) -> bool:
    return value is None or (isinstance(value, float) and not np.isfinite(value))


def _quiet_float(value: object, default: float) -> float:
    if _is_missing_value(value):
        return float(default)
    coerced = safe_float(value, default)
    return float(default if coerced is None else coerced)


def _quiet_int(value: object, default: int) -> int:
    if _is_missing_value(value):
        return int(default)
    coerced = safe_int(value, default)
    return int(default if coerced is None else coerced)


def _normalize_direction_value(value: object) -> str:
    if _is_missing_value(value):
        return ""
    if isinstance(value, (int, float, np.integer, np.floating)):
        numeric = float(value)
        if numeric > 0:
            return "long"
        if numeric < 0:
            return "short"
        return "flat"
    text = str(value).strip().lower()
    if not text:
        return ""
    if text in {"1", "+1", "1.0", "+1.0", "long", "buy", "up", "bull", "bullish"}:
        return "long"
    if text in {"-1", "-1.0", "short", "sell", "down", "bear", "bearish"}:
        return "short"
    if text in {"0", "0.0", "flat", "neutral", "both"}:
        return "flat"
    return text


def _parse_symbols_csv(symbols_csv: str) -> List[str]:
    symbols = [s.strip().upper() for s in str(symbols_csv).split(",") if s.strip()]
    ordered: List[str] = []
    seen = set()
    for symbol in symbols:
        if symbol not in seen:
            ordered.append(symbol)
            seen.add(symbol)
    return ordered


def _infer_symbol_tag(row: Dict[str, object], run_symbols: Sequence[str]) -> str:
    symbol_value = str(row.get("symbol", "")).strip().upper()
    if symbol_value:
        return symbol_value
    condition = str(row.get("condition", "")).strip().lower()
    if condition.startswith("symbol_"):
        inferred = condition.removeprefix("symbol_").upper()
        if inferred:
            return inferred
    if len(run_symbols) == 1:
        return str(run_symbols[0]).upper()
    return "ALL"


def _candidate_type_from_action(action_name: str) -> str:
    action = str(action_name or "").strip().lower()
    if action == "entry_gate_skip" or action.startswith("risk_throttle_"):
        return "overlay"
    if action == "no_action" or action.startswith("delay_") or action == "reenable_at_half_life":
        return "standalone"
    return "standalone"


def _is_confirmatory_run_mode(run_mode: str) -> bool:
    return str(run_mode or "").strip().lower() in {
        "confirmatory",
        "production",
        "certification",
        "promotion",
        "deploy",
    }


def _load_latest_adjacent_survivorship_index(
    run_id: str,
) -> tuple[Dict[tuple[str, str, str, str], Dict[str, object]], str | None]:
    data_root = get_data_root()
    base = data_root / "reports" / "adjacent_survivorship"
    if not base.exists():
        return {}, None

    candidates = sorted(
        base.glob(f"*/vs_{run_id}/adjacent_survivorship.json"),
        key=lambda path: path.stat().st_mtime if path.exists() else 0.0,
        reverse=True,
    )
    for path in candidates:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(payload, dict):
            continue
        index: Dict[tuple[str, str, str, str], Dict[str, object]] = {}
        rows = payload.get("candidate_rows", [])
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            key = (
                str(row.get("symbol", "")),
                str(row.get("event_type", "")),
                str(row.get("direction", "")),
                str(row.get("horizon", "")),
            )
            index[key] = row
        return index, str(path)
    return {}, None


def _apply_adjacent_survivorship_annotations(
    df: pd.DataFrame, *, run_id: str
) -> tuple[pd.DataFrame, str | None]:
    if df.empty:
        return df.copy(), None
    required = ["candidate_symbol", "event_type", "direction", "horizon"]
    if not all(col in df.columns for col in required):
        out = df.copy()
        out["adjacent_window_survived"] = np.nan
        out["adjacent_window_target_run_id"] = np.nan
        out["adjacent_window_failure_reasons"] = np.nan
        out["adjacent_window_target_after_cost_expectancy_per_trade"] = np.nan
        return out, None

    adjacent_index, report_path = _load_latest_adjacent_survivorship_index(run_id)
    out = df.copy()
    survived: List[object] = []
    target_runs: List[object] = []
    fail_reasons: List[object] = []
    target_expectancy: List[object] = []

    report_target_run_id = None
    if report_path is not None:
        try:
            report_target_run_id = Path(report_path).parent.parent.name
        except Exception:
            report_target_run_id = None

    for _, row in out.iterrows():
        key = (
            str(row.get("candidate_symbol", "")),
            str(row.get("event_type", row.get("event", ""))),
            str(row.get("direction", "")),
            str(row.get("horizon", "")),
        )
        match = adjacent_index.get(key)
        if match is None:
            survived.append(np.nan)
            target_runs.append(np.nan)
            fail_reasons.append(np.nan)
            target_expectancy.append(np.nan)
            continue
        survived.append(bool(match.get("survived_adjacent_window", False)))
        target_runs.append(str(match.get("target_run_id") or report_target_run_id or ""))
        failure_tokens = match.get("failure_reasons", [])
        if isinstance(failure_tokens, list):
            fail_reasons.append(
                "|".join(str(token) for token in failure_tokens if str(token).strip())
            )
        else:
            fail_reasons.append(str(failure_tokens))
        target_expectancy.append(match.get("target_after_cost_expectancy_per_trade"))

    out["adjacent_window_survived"] = survived
    out["adjacent_window_target_run_id"] = target_runs
    out["adjacent_window_failure_reasons"] = fail_reasons
    out["adjacent_window_target_after_cost_expectancy_per_trade"] = target_expectancy
    return out, report_path


def _normalize_edge_candidates_df(
    df: pd.DataFrame,
    *,
    run_mode: str,
    is_confirmatory: bool,
    current_spec_hash: str,
) -> pd.DataFrame:
    out = df.copy()
    if not out.empty:
        out["confirmatory_locked"] = bool(is_confirmatory)
        out["frozen_spec_hash"] = current_spec_hash if is_confirmatory else np.nan
        out["run_mode"] = run_mode

    mandatory_columns = [
        "run_id",
        "candidate_symbol",
        "run_symbols",
        "event",
        "candidate_id",
        "status",
        "candidate_type",
        "overlay_base_candidate_id",
        "edge_score",
        "expected_return_proxy",
        "expectancy_per_trade",
        "after_cost_expectancy_per_trade",
        "stressed_after_cost_expectancy_per_trade",
        "selection_score_executed",
        "bridge_eval_status",
        "bridge_train_after_cost_bps",
        "bridge_validation_after_cost_bps",
        "bridge_validation_stressed_after_cost_bps",
        "bridge_validation_trades",
        "bridge_effective_cost_bps_per_trade",
        "bridge_gross_edge_bps_per_trade",
        "gate_bridge_has_trades_validation",
        "gate_bridge_after_cost_positive_validation",
        "gate_bridge_after_cost_stressed_positive_validation",
        "gate_bridge_edge_cost_ratio",
        "gate_bridge_turnover_controls",
        "gate_bridge_tradable",
        "gate_all_research",
        "cost_ratio",
        "turnover_proxy_mean",
        "avg_dynamic_cost_bps",
        "variance",
        "stability_proxy",
        "robustness_score",
        "event_frequency",
        "capacity_proxy",
        "profit_density_score",
        "n_events",
        "source_path",
        "is_discovery",
        "phase2_quality_score",
        "phase2_quality_components",
        "compile_eligible_phase2_fallback",
        "promotion_track",
        "discovery_start",
        "discovery_end",
        "p_value",
        "q_value",
        "hypothesis_id",
        "train_n_obs",
        "validation_n_obs",
        "test_n_obs",
        "validation_samples",
        "test_samples",
        "sample_size",
        "confirmatory_locked",
        "frozen_spec_hash",
        "run_mode",
        "adjacent_window_survived",
        "adjacent_window_target_run_id",
        "adjacent_window_failure_reasons",
        "adjacent_window_target_after_cost_expectancy_per_trade",
        "effect_raw",
        "effect_shrunk_state",
        "shrinkage_factor",
        "shrinkage_loso_stable",
        "shrinkage_scope",
        "shrinkage_delta",
        "shrinkage_posterior_residual_z",
        "shrinkage_borrowing_dominant",
        "shrinkage_pooling_group_size",
        "p_value_shrunk",
    ]

    all_cols = list(mandatory_columns)
    for c in out.columns:
        if c not in all_cols:
            all_cols.append(c)

    for c in mandatory_columns:
        if c not in out.columns:
            out[c] = np.nan

    if "gate_bridge_tradable" in out.columns:
        out["gate_bridge_tradable"] = out["gate_bridge_tradable"].apply(
            lambda x: (
                "pass"
                if str(x).lower().strip() in ("1", "true", "t", "yes", "y", "on", "pass")
                else "fail"
            )
        )
    if "direction" in out.columns:
        out["direction"] = out["direction"].apply(_normalize_direction_value)

    out = out[all_cols].copy()
    if not out.empty:
        out["selection_score_executed"] = pd.to_numeric(
            out.get("selection_score_executed"), errors="coerce"
        ).fillna(0.0)
        out = out.sort_values(
            ["selection_score_executed", "profit_density_score", "edge_score", "stability_proxy"],
            ascending=[False, False, False, False],
        ).reset_index(drop=True)
    return out


def _phase2_row_to_candidate(
    run_id: str,
    event: str,
    row: Dict[str, object],
    idx: int,
    source_path: Path,
    default_status: str,
    run_symbols: Sequence[str],
) -> Dict[str, object]:
    # Lossless handoff: start with every field from the input row
    candidate = dict(row)

    # Ensure canonical identifiers and standard types
    candidate["run_id"] = str(run_id)
    candidate["event"] = str(event)
    candidate["candidate_id"] = str(row.get("candidate_id", f"{event}_{idx}"))
    candidate["status"] = str(row.get("status", default_status))
    candidate["source_path"] = str(source_path)
    candidate["direction"] = _normalize_direction_value(row.get("direction"))

    # Symbols
    candidate["run_symbols"] = list(run_symbols)
    candidate["candidate_symbol"] = _infer_symbol_tag(row=row, run_symbols=run_symbols)

    # Handle common statistical aliases if missing
    if "n_events" not in candidate:
        candidate["n_events"] = _quiet_int(row.get("sample_size", row.get("count", 0)), 0)
    if "sample_size" not in candidate:
        candidate["sample_size"] = candidate["n_events"]

    # Consistency for score fields often used in sorting or gating
    risk_reduction = max(0.0, -_quiet_float(row.get("delta_adverse_mean"), 0.0))
    opp_delta = _quiet_float(row.get("delta_opportunity_mean"), 0.0)

    if "edge_score" not in candidate:
        candidate["edge_score"] = _quiet_float(
            row.get("edge_score"), risk_reduction + max(0.0, opp_delta)
        )

    expectancy_source = row.get("after_cost_expectancy_per_trade")
    if _is_missing_value(expectancy_source):
        expectancy_source = row.get("expectancy_after_multiplicity")
    if _is_missing_value(expectancy_source):
        expectancy_source = row.get("expectancy_per_trade")
    if _is_missing_value(expectancy_source):
        expectancy_source = row.get("expectancy")

    if "expectancy_per_trade" not in candidate:
        candidate["expectancy_per_trade"] = _quiet_float(
            expectancy_source, _quiet_float(row.get("expected_return_proxy"), opp_delta)
        )

    if "after_cost_expectancy_per_trade" not in candidate:
        candidate["after_cost_expectancy_per_trade"] = _quiet_float(
            row.get("after_cost_expectancy_per_trade", row.get("expectancy")),
            candidate["expectancy_per_trade"],
        )

    # Robustness / Stability
    gate_cols = [
        "gate_a_ci_separated",
        "gate_b_time_stable",
        "gate_c_regime_stable",
        "gate_d_friction_floor",
        "gate_f_exposure_guard",
        "gate_e_simplicity",
    ]
    gates_present = [g for g in gate_cols if g in row]
    if gates_present:
        stability_proxy = float(
            sum(1 for g in gates_present if as_bool(row.get(g))) / len(gates_present)
        )
    else:
        stability_proxy = _quiet_float(row.get("stability_proxy"), 0.0)

    candidate["stability_proxy"] = stability_proxy
    if "robustness_score" not in candidate:
        candidate["robustness_score"] = _quiet_float(row.get("robustness_score"), stability_proxy)

    return candidate


def _build_symbol_eval_lookup(event_dir: Path) -> Dict[str, Dict[str, object]]:
    path = event_dir / "phase2_symbol_evaluation.csv"
    if not path.exists():
        return {}
    try:
        df = pd.read_csv(path)
    except Exception:
        return {}
    if df.empty:
        return {}

    grouped: Dict[str, List[Dict[str, object]]] = {}
    for _, row in df.iterrows():
        cid = str(row.get("candidate_id", "")).strip()
        if not cid:
            continue
        symbol = str(row.get("symbol", "ALL")).strip().upper() or "ALL"
        deployable = as_bool(row.get("deployable", False))
        ev = _quiet_float(row.get("ev"), 0.0)
        variance = _quiet_float(row.get("variance"), 0.0)
        sharpe_like = _quiet_float(row.get("sharpe_like"), 0.0)
        stability_score = _quiet_float(row.get("stability_score"), 0.0)
        capacity_proxy = _quiet_float(row.get("capacity_proxy"), 0.0)
        row_score = ev * max(0.0, sharpe_like) * max(0.0, stability_score)
        grouped.setdefault(cid, []).append(
            {
                "symbol": symbol,
                "deployable": deployable,
                "ev": ev,
                "variance": variance,
                "stability_score": stability_score,
                "capacity_proxy": capacity_proxy,
                "row_score": row_score,
            }
        )

    lookup: Dict[str, Dict[str, object]] = {}
    for cid, items in grouped.items():
        if not items:
            continue
        best = max(items, key=lambda item: float(item.get("row_score", -1e18)))
        symbol_scores = {
            str(item.get("symbol", "ALL")).strip().upper() or "ALL": _quiet_float(
                item.get("row_score"), 0.0
            )
            for item in items
        }
        positive_scores = [score for score in symbol_scores.values() if score > 0.0]
        similar_score_band = True
        if len(positive_scores) > 1:
            max_score = max(positive_scores)
            min_score = min(positive_scores)
            similar_score_band = bool(min_score >= (0.75 * max_score))
        deployable_symbols = [item for item in items if bool(item.get("deployable", False))]
        rollout_eligible = bool(len(deployable_symbols) > 1 and similar_score_band)
        lookup[cid] = {
            "candidate_symbol": str(best.get("symbol", "ALL")).strip().upper() or "ALL",
            "symbol": str(best.get("symbol", "ALL")).strip().upper() or "ALL",
            "symbol_scores": json.dumps(symbol_scores),
            "rollout_eligible": rollout_eligible,
            "expectancy_per_trade": _quiet_float(best.get("ev"), 0.0),
            "variance": _quiet_float(best.get("variance"), 0.0),
            "stability_proxy": _quiet_float(best.get("stability_score"), 0.0),
            "robustness_score": _quiet_float(best.get("stability_score"), 0.0),
            "capacity_proxy": _quiet_float(best.get("capacity_proxy"), 0.0),
            "profit_density_score": _quiet_float(best.get("row_score"), 0.0),
            "status": "PROMOTED" if bool(best.get("deployable", False)) else "DRAFT",
        }
    return lookup


def _build_bridge_eval_lookup(
    *, run_id: str, event_type: str, timeframe: str
) -> Dict[str, Dict[str, object]]:
    bridge_root = bridge_event_out_dir(
        data_root=get_data_root(),
        run_id=run_id,
        event_type=event_type,
        timeframe=timeframe,
    )
    if not bridge_root.exists():
        return {}

    lookup: Dict[str, Dict[str, object]] = {}
    for symbol_dir in sorted(path for path in bridge_root.iterdir() if path.is_dir()):
        bridge_path = symbol_dir / "bridge_evaluation.parquet"
        if not bridge_path.exists():
            continue
        try:
            frame = pd.read_parquet(bridge_path)
        except Exception:
            continue
        if frame.empty or "candidate_id" not in frame.columns:
            continue
        for _, row in frame.iterrows():
            candidate_id = str(row.get("candidate_id", "")).strip()
            if candidate_id:
                lookup[candidate_id] = row.to_dict()
    return lookup


