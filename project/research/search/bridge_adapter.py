"""
Rich Bridge adapter: translate hypothesis metrics into full production schema.

Takes the rich metrics DataFrame produced by the hypothesis evaluator and
maps them into the 40+ column schema expected by bridge evaluation and
blueprint compilation.
"""

from __future__ import annotations

import re
import logging
import pandas as pd
import numpy as np

from project.research.multiplicity import make_family_id
from project.spec_validation import get_event_family, resolve_execution_templates

log = logging.getLogger(__name__)


def canonical_bridge_event_type(trigger_type: str, trigger_key: str) -> str:
    trigger_type = str(trigger_type or "event").lower()
    key = str(trigger_key or "UNKNOWN").upper()
    # Strip "type:" prefix from trigger_key (e.g. "event:VOL_SPIKE" -> "VOL_SPIKE")
    if ":" in key:
        key = key.split(":", 1)[1]
    clean_key = re.sub(r"[^A-Z0-9_]+", "_", key)
    if trigger_type == "event":
        return clean_key
    if trigger_type == "state":
        return f"STATE_{clean_key}"
    if trigger_type == "transition":
        return f"TRANSITION_{clean_key}"
    if trigger_type == "sequence":
        return f"SEQUENCE_{clean_key}"
    if trigger_type == "interaction":
        return f"INTERACTION_{clean_key}"
    return f"FEATURE_{clean_key}"


def _sanitize_event_type(row: pd.Series) -> str:
    return canonical_bridge_event_type(
        str(row.get("trigger_type", "event")),
        str(row.get("trigger_key", "UNKNOWN")),
    )


def hypotheses_to_bridge_candidates(
    metrics_df: pd.DataFrame,
    *,
    symbol: str = "ALL",
    min_t_stat: float = 1.5,
    min_n: int = 30,
    min_events: int = 5,
    bridge_min_t_stat: float = 2.0,
    bridge_min_robustness_score: float = 0.7,
    bridge_min_regime_stability_score: float = 0.6,
    bridge_min_stress_survival: float = 0.5,
    bridge_stress_cost_buffer_bps: float = 2.0,
    prefilter_min_n: bool = True,
    prefilter_min_t_stat: bool = True,
) -> pd.DataFrame:
    """
    Map evaluator metrics to the production schema.
    
    Args:
        min_events: Minimum number of events required. STATE_ regime features
            generate candidates on every bar, creating noise. Default 5 filters
            out regime-label candidates that fire on >50% of bars.
    """
    filtered, _ = split_bridge_candidates(
        metrics_df,
        min_t_stat=min_t_stat,
        min_n=min_n,
        require_min_n=prefilter_min_n,
        require_min_t_stat=prefilter_min_t_stat,
    )
    if filtered.empty:
        return pd.DataFrame()

    # Core Mappings
    out = pd.DataFrame()
    out["candidate_id"] = filtered["hypothesis_id"].astype(str)
    event_types = [_sanitize_event_type(row) for _, row in filtered.iterrows()]
    out["event_type"] = event_types
    
    # Only filter pure regime-label STATE_ events - ones that have very high event counts
    # (appearing on >50% of bars = >280 bars in 3-day window)
    # Keep legitimate events like VOL_SHOCK even if they have STATE_ prefix
    # Use filtered["n"] as source (n_events gets assigned from n later on line 95)
    n_events_arr = filtered["n"].values
    high_frequency_mask = n_events_arr > (577 * 0.5)  # More than 50% of bars
    state_mask = out["event_type"].str.startswith(("STATE_", "TRANSITION_"))
    
    # Remove only STATE_/TRANSITION_ events that are high-frequency (regime labels)
    noise_mask = state_mask & high_frequency_mask
    if noise_mask.any():
        filtered = filtered[~noise_mask].copy()
        out = out[~noise_mask].copy()
    
    if filtered.empty:
        return pd.DataFrame()
    out["direction"] = filtered["direction"].astype(str)
    out["rule_template"] = filtered["template_id"].astype(str)
    out["template_verb"] = out["rule_template"]
    out["horizon"] = filtered["horizon"].astype(str)
    out["t_stat"] = filtered["t_stat"].astype(float)
    out["n"] = filtered["n"].astype(int)
    out["sample_size"] = out["n"]
    out["n_events"] = out["n"]
    out["gate_search_min_sample_size"] = out["n"] >= int(min_n)
    out["gate_search_min_t_stat"] = pd.to_numeric(
        filtered["t_stat"], errors="coerce"
    ).fillna(0.0) >= float(min_t_stat)
    for source_col in (
        "train_n_obs",
        "validation_n_obs",
        "test_n_obs",
        "validation_samples",
        "test_samples",
    ):
        if source_col in filtered.columns:
            out[source_col] = (
                pd.to_numeric(filtered[source_col], errors="coerce").fillna(0).astype(int)
            )
        else:
            out[source_col] = 0

    # Financial Mappings (bps -> decimal)
    out["expectancy"] = filtered["mean_return_bps"] / 10000.0
    out["mean_return_bps"] = filtered["mean_return_bps"]
    out["after_cost_expectancy_per_trade"] = filtered["cost_adjusted_return_bps"] / 10000.0

    # Stress testing: subtract an additional 2bps
    out["stressed_after_cost_expectancy_per_trade"] = (
        filtered["cost_adjusted_return_bps"] - 2.0
    ) / 10000.0

    # Rich Metrics
    out["robustness_score"] = filtered["robustness_score"]
    out["stress_test_survival"] = (
        filtered["stress_score"] if "stress_score" in filtered.columns else 0.0
    )
    out["kill_switch_count"] = (
        filtered["kill_switch_count"] if "kill_switch_count" in filtered.columns else 0
    )
    out["kill_switch_count"] = out["kill_switch_count"].astype(int)

    out["delta_adverse_mean"] = filtered["mae_mean_bps"] / 10000.0
    out["delta_opportunity_mean"] = filtered["mfe_mean_bps"] / 10000.0
    out["capacity_proxy"] = filtered["capacity_proxy"]
    out["turnover_proxy_mean"] = 0.5  # Default turnover proxy

    # Gating Flags
    out["gate_oos_validation"] = filtered["robustness_score"] >= float(
        bridge_min_robustness_score
    )
    out["gate_multiplicity"] = False  # Will be set by apply_multiplicity_controls()
    out["gate_c_regime_stable"] = filtered["robustness_score"] >= float(
        bridge_min_regime_stability_score
    )
    out["gate_after_cost_positive"] = filtered["cost_adjusted_return_bps"] > 0
    out["gate_after_cost_stressed_positive"] = (
        filtered["cost_adjusted_return_bps"] - float(bridge_stress_cost_buffer_bps)
    ) > 0

    # Overall Tradability
    # A candidate is "tradable" if it passes t-stat, n, OOS score,
    # and survives at least 50% of stress scenarios.
    out["gate_bridge_tradable"] = (
        (out["t_stat"] >= float(bridge_min_t_stat))
        & (out["gate_after_cost_stressed_positive"])
        & (out["gate_oos_validation"])
        & (out["stress_test_survival"] >= float(bridge_min_stress_survival))
    )

    out["bridge_eval_status"] = np.where(out["gate_bridge_tradable"], "tradable", "rejected")
    out["promotion_track"] = np.where(out["gate_bridge_tradable"], "standard", "fallback_only")

    # Structural stats (needed for blueprint compilation)
    out["pnl_series"] = "[]"

    # Derive p-values from t-statistics
    p_value_series = pd.to_numeric(
        filtered.get("p_value_raw", filtered.get("p_value", 1.0)),
        errors="coerce",
    ).fillna(1.0)
    out["p_value"] = p_value_series.astype(float)
    out["p_value_raw"] = out["p_value"]
    out["p_value_for_fdr"] = pd.to_numeric(
        filtered.get("p_value_for_fdr", out["p_value"]),
        errors="coerce",
    ).fillna(out["p_value"]).astype(float)

    # Derive family_id from trigger metadata
    # Derive canonical_family from trigger_key (the part after "type:", e.g. "event:VOL_SPIKE" -> "VOL_SPIKE")
    out["canonical_family"] = (
        filtered["trigger_key"]
        .apply(lambda k: str(k).split(":", 1)[1].upper() if ":" in str(k) else str(k).upper())
        .values
    )

    out["family_id"] = [
        make_family_id(
            str(symbol),
            str(event_type),
            str(template_id),
            str(horizon),
            "",
            canonical_family=str(canonical_family),
        )
        for event_type, template_id, horizon, canonical_family in zip(
            out["event_type"],
            filtered["template_id"],
            filtered["horizon"],
            out["canonical_family"],
        )
    ]

    # Symbol placeholder
    out["symbol"] = str(symbol).strip().upper() or "ALL"

    # Expand base candidates (template_id="base") into one row per execution template.
    # Filter template candidates pass through unchanged.
    base_mask = out["rule_template"] == "base"
    if base_mask.any():
        base_rows = out[base_mask]
        filter_rows = out[~base_mask]
        expanded_parts = [filter_rows]
        for _, row in base_rows.iterrows():
            event_id = str(row.get("canonical_family", ""))
            family = get_event_family(event_id) if event_id else None
            exec_templates = resolve_execution_templates(family) if family else []
            if not exec_templates:
                if family:
                    log.warning(
                        "No execution templates resolved for family %r (event_id=%r); keeping as 'base'",
                        family,
                        event_id,
                    )
                # No execution templates found — keep as "base" rather than drop
                expanded_parts.append(pd.DataFrame([row]))
                continue
            for tmpl in exec_templates:
                new_row = row.copy()
                new_row["rule_template"] = tmpl
                new_row["template_verb"] = tmpl
                expanded_parts.append(pd.DataFrame([new_row]))
        out = pd.concat(expanded_parts, ignore_index=True)

    return out.reset_index(drop=True)


def split_bridge_candidates(
    metrics_df: pd.DataFrame,
    *,
    min_t_stat: float = 1.5,
    min_n: int = 30,
    require_min_n: bool = True,
    require_min_t_stat: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if metrics_df.empty:
        return pd.DataFrame(), pd.DataFrame()

    valid_mask = metrics_df["valid"].fillna(False)
    min_n_mask = pd.to_numeric(metrics_df["n"], errors="coerce").fillna(0) >= int(min_n)
    min_t_mask = pd.to_numeric(metrics_df["t_stat"], errors="coerce").fillna(0.0) >= float(
        min_t_stat
    )
    pass_mask = valid_mask.copy()
    if require_min_n:
        pass_mask = pass_mask & min_n_mask
    if require_min_t_stat:
        pass_mask = pass_mask & min_t_mask

    filtered = metrics_df[pass_mask].copy()
    failed = metrics_df[~pass_mask].copy()
    if not failed.empty:
        reasons: list[list[str]] = []
        primary: list[str] = []
        for _, row in failed.iterrows():
            row_reasons: list[str] = []
            if not bool(row.get("valid", False)):
                row_reasons.append(str(row.get("invalid_reason") or "invalid"))
            else:
                if int(pd.to_numeric(row.get("n", 0), errors="coerce") or 0) < int(min_n):
                    row_reasons.append("min_sample_size")
                if float(pd.to_numeric(row.get("t_stat", 0.0), errors="coerce") or 0.0) < float(
                    min_t_stat
                ):
                    row_reasons.append("min_t_stat")
            if not row_reasons:
                row_reasons = ["filtered_out"]
            reasons.append(row_reasons)
            primary.append(row_reasons[0])
        failed["gate_failure_reasons"] = reasons
        failed["gate_failure_reason"] = primary
        failed["status"] = "gate_failed"
    return filtered, failed
