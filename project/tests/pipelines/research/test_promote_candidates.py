from __future__ import annotations

import json

from types import SimpleNamespace

import pandas as pd
import pytest

from project.research.promotion import evaluate_row as _evaluate_row_impl
from project.research.promotion.promotion_reporting import (
    apply_portfolio_overlap_gate as _apply_portfolio_overlap_gate,
    assign_and_validate_promotion_tiers as _assign_and_validate_promotion_tiers,
    build_promotion_capital_footprint as _build_promotion_capital_footprint,
    build_negative_control_diagnostics as _build_negative_control_diagnostics,
    build_promotion_statistical_audit as _build_promotion_statistical_audit,
    portfolio_diversification_violations as _portfolio_diversification_violations,
    stabilize_promoted_output_schema as _stabilize_promoted_output_schema,
)
from project.research.services.promotion_service import (
    _load_bridge_metrics,
    _load_dynamic_min_events_by_event,
    _merge_bridge_metrics,
)


_LEGACY_PASS_FAIL_GATES = {
    "gate_promo_dsr",
    "gate_promo_low_capital_viability",
    "gate_promo_baseline_beats_complexity",
    "gate_promo_placebo_controls",
}


def _legacy_gate_value(value):
    if isinstance(value, bool):
        return "pass" if value else "fail"
    return value


def _evaluate_row(*args, **kwargs):
    result = _evaluate_row_impl(*args, **kwargs)
    for key in _LEGACY_PASS_FAIL_GATES:
        if key in result:
            result[key] = _legacy_gate_value(result[key])
    audit = result.get("promotion_audit")
    if isinstance(audit, dict):
        result["promotion_audit"] = {
            key: (_legacy_gate_value(value) if key in _LEGACY_PASS_FAIL_GATES else value)
            for key, value in audit.items()
        }
    return result


def _eval_row(**overrides):
    row = {
        "event_type": "VOL_SHOCK",
        "candidate_id": "cand_1",
        "plan_row_id": "p1",
        "q_value": 0.01,
        "n_events": 250,
        "effect_shrunk_state": 0.02,
        "std_return": 0.01,
        "gate_stability": True,
        "val_t_stat": 2.5,
        "oos1_t_stat": 2.0,
        "gate_after_cost_positive": True,
        "gate_after_cost_stressed_positive": True,
        "gate_bridge_after_cost_positive_validation": True,
        "gate_bridge_after_cost_stressed_positive_validation": False,
        "gate_delay_robustness": True,
        "validation_samples": 100,
        "baseline_expectancy_bps": 5.0,
        "bridge_validation_after_cost_bps": 20.0,
        "pass_shift_placebo": True,
        "pass_random_entry_placebo": True,
        "pass_direction_reversal_placebo": True,
        "event_is_descriptive": False,
        "event_is_trade_trigger": True,
        "gate_delayed_entry_stress": True,
        "gate_bridge_microstructure": True,
        "net_expectancy_bps": 20.0,
    }
    row.update(overrides)
    return _evaluate_row(
        row=row,
        hypothesis_index={"p1": {"statuses": ["executed"], "executed": True}},
        negative_control_summary={"by_event": {"VOL_SHOCK": {"pass_rate_after_bh": 0.0}}},
        max_q_value=0.10,
        min_events=100,
        min_stability_score=0.05,
        min_sign_consistency=0.60,
        min_cost_survival_ratio=0.75,
        max_negative_control_pass_rate=0.01,
        min_tob_coverage=0.0,
        require_hypothesis_audit=True,
        allow_missing_negative_controls=False,
    )


def test_promote_candidate_happy_path():
    out = _eval_row()
    assert out["promotion_decision"] == "promoted"
    assert out["reject_reason"] == ""
    assert out["gate_promo_statistical"] == "pass"
    assert out["gate_promo_stability"] == "pass"
    assert out["gate_promo_cost_survival"] == "pass"
    assert out["gate_promo_negative_control"] == "pass"
    assert out["gate_promo_hypothesis_audit"] == "pass"


def test_load_bridge_metrics_prefers_versioned_enriched_snapshot(tmp_path):
    bridge_root = tmp_path / "bridge_eval"
    event_dir = bridge_root / "VOL_SHOCK"
    event_dir.mkdir(parents=True, exist_ok=True)
    (event_dir / "bridge_candidate_metrics.csv").write_text(
        "candidate_id,event_type,gate_bridge_tradable\nc1,VOL_SHOCK,0\n",
        encoding="utf-8",
    )
    (event_dir / "phase2_candidates_bridge_eval_v1.csv").write_text(
        "candidate_id,event_type,gate_bridge_tradable,bridge_validation_after_cost_bps\n"
        "c1,VOL_SHOCK,1,12.5\n",
        encoding="utf-8",
    )

    out = _load_bridge_metrics(bridge_root)
    assert len(out) == 1
    assert bool(out.iloc[0]["gate_bridge_tradable"]) is True
    assert float(out.iloc[0]["bridge_validation_after_cost_bps"]) == 12.5


def test_load_bridge_metrics_reads_bridge_evaluation_parquet(tmp_path):
    bridge_root = tmp_path / "bridge_eval"
    event_dir = bridge_root / "VOL_SHOCK"
    event_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                "candidate_id": "c1",
                "event_type": "VOL_SHOCK",
                "gate_bridge_tradable": True,
                "bridge_validation_after_cost_bps": 9.5,
            }
        ]
    ).to_parquet(event_dir / "bridge_evaluation.parquet", index=False)

    out = _load_bridge_metrics(bridge_root)
    assert len(out) == 1
    assert bool(out.iloc[0]["gate_bridge_tradable"]) is True
    assert float(out.iloc[0]["bridge_validation_after_cost_bps"]) == 9.5


def test_merge_bridge_metrics_overrides_phase2_bridge_fields():
    phase2_df = pd.DataFrame(
        [
            {
                "candidate_id": "c1",
                "event_type": "VOL_SHOCK",
                "gate_bridge_tradable": False,
            }
        ]
    )
    bridge_df = pd.DataFrame(
        [
            {
                "candidate_id": "c1",
                "event_type": "VOL_SHOCK",
                "gate_bridge_tradable": True,
                "bridge_validation_after_cost_bps": 7.0,
            }
        ]
    )
    merged = _merge_bridge_metrics(phase2_df=phase2_df, bridge_df=bridge_df)
    assert bool(merged.iloc[0]["gate_bridge_tradable"]) is True
    assert float(merged.iloc[0]["bridge_validation_after_cost_bps"]) == 7.0


def test_stabilize_promoted_output_schema_keeps_contract_columns_when_empty():
    audit_df = pd.DataFrame(
        [
            {
                "candidate_id": "cand_1",
                "run_id": "r1",
                "symbol": "BTCUSDT",
                "event": "VOL_SHOCK",
                "event_type": "VOL_SHOCK",
                "promotion_decision": "rejected",
                "promotion_tier": "research",
                "selection_score": 0.1,
                "n_events": 100,
                "gate_bridge_tradable": False,
            }
        ]
    )
    promoted_df = pd.DataFrame(columns=["promotion_tier"])
    out = _stabilize_promoted_output_schema(promoted_df=promoted_df, audit_df=audit_df)
    assert out.empty
    for col in [
        "candidate_id",
        "event_type",
        "status",
        "promotion_decision",
        "promotion_tier",
        "selection_score",
        "gate_bridge_tradable",
    ]:
        assert col in out.columns


def test_load_dynamic_min_events_by_event_uses_source_event_and_max_threshold(tmp_path):
    spec_dir = tmp_path / "spec" / "states"
    spec_dir.mkdir(parents=True, exist_ok=True)
    (spec_dir / "state_registry.yaml").write_text(
        (
            "version: 1\n"
            "kind: state_registry\n"
            "defaults:\n"
            "  min_events: 200\n"
            "states:\n"
            "  - state_id: A\n"
            "    family: VOLATILITY_TRANSITION\n"
            "    source_event_type: VOL_SHOCK\n"
            "    min_events: 250\n"
            "  - state_id: B\n"
            "    family: VOLATILITY_TRANSITION\n"
            "    source_event_type: VOL_SHOCK\n"
            "    min_events: 300\n"
            "  - state_id: C\n"
            "    family: LIQUIDITY_DISLOCATION\n"
            "    source_event_type: LIQUIDITY_VACUUM\n"
        ),
        encoding="utf-8",
    )

    out = _load_dynamic_min_events_by_event(tmp_path)
    assert out["VOL_SHOCK"] == 300
    assert out["LIQUIDITY_VACUUM"] == 200


def test_load_dynamic_min_events_by_event_logs_warning_on_invalid_yaml(tmp_path, caplog):
    spec_dir = tmp_path / "spec" / "states"
    spec_dir.mkdir(parents=True, exist_ok=True)
    (spec_dir / "state_registry.yaml").write_text(
        "version: [\n",
        encoding="utf-8",
    )
    with caplog.at_level("WARNING"):
        out = _load_dynamic_min_events_by_event(tmp_path)
    assert out == {}
    assert any("Failed loading state_registry" in rec.message for rec in caplog.records)


def test_promote_candidate_rejects_cost_and_controls():
    out = _eval_row(
        gate_after_cost_positive=False,
        gate_after_cost_stressed_positive=False,
        gate_bridge_after_cost_positive_validation=False,
        gate_bridge_after_cost_stressed_positive_validation=False,
        control_pass_rate=0.25,
    )
    assert out["promotion_decision"] == "rejected"
    assert "cost_survival" in out["reject_reason"]
    assert "negative_control_fail" in out["reject_reason"]


def test_promote_candidate_research_profile_softens_baseline_placebo_and_timeframe():
    common = {
        "row": {
            "event_type": "BASIS_DISLOCATION",
            "candidate_id": "cand_research",
            "plan_row_id": "p1",
            "q_value": 0.01,
            "n_events": 80,
            "effect_shrunk_state": 0.01,
            "std_return": 0.01,
            "gate_stability": True,
            "val_t_stat": 2.5,
            "oos1_t_stat": 2.0,
            "gate_after_cost_positive": True,
            "gate_after_cost_stressed_positive": True,
            "gate_bridge_after_cost_positive_validation": True,
            "gate_bridge_after_cost_stressed_positive_validation": True,
            "bridge_validation_after_cost_bps": 2.0,
            "baseline_expectancy_bps": 5.0,
            "pass_shift_placebo": False,
            "pass_random_entry_placebo": False,
            "pass_direction_reversal_placebo": False,
            "gate_delay_robustness": True,
            "validation_samples": 40,
            "test_samples": 25,
            "mean_validation_return": 0.01,
            "mean_test_return": 0.01,
            "gate_bridge_microstructure": True,
            "gate_delayed_entry_stress": True,
            "gate_timeframe_consensus": False,
            "event_is_descriptive": False,
            "event_is_trade_trigger": True,
        },
        "hypothesis_index": {"p1": {"statuses": ["executed"], "executed": True}},
        "negative_control_summary": {
            "by_event": {"BASIS_DISLOCATION": {"pass_rate_after_bh": 0.0}}
        },
        "max_q_value": 0.10,
        "min_events": 50,
        "min_stability_score": 0.05,
        "min_sign_consistency": 0.60,
        "min_cost_survival_ratio": 0.75,
        "max_negative_control_pass_rate": 0.01,
        "min_tob_coverage": 0.0,
        "require_hypothesis_audit": True,
        "allow_missing_negative_controls": False,
    }

    deploy_out = _evaluate_row(
        **common,
        promotion_profile="deploy",
        enforce_baseline_beats_complexity=True,
        enforce_placebo_controls=True,
        enforce_timeframe_consensus=True,
    )
    research_out = _evaluate_row(
        **common,
        promotion_profile="research",
        enforce_baseline_beats_complexity=False,
        enforce_placebo_controls=False,
        enforce_timeframe_consensus=False,
    )

    assert deploy_out["promotion_decision"] == "rejected"
    assert research_out["promotion_decision"] == "promoted"
    assert research_out["promotion_profile"] == "research"
    assert deploy_out["gate_promo_baseline_beats_complexity"] == "fail"
    assert deploy_out["gate_promo_placebo_controls"] == "fail"
    assert deploy_out["gate_promo_timeframe_consensus"] == "fail"


def test_promote_candidate_rejects_missing_hypothesis_audit():
    out = _evaluate_row(
        row={
            "event_type": "VOL_SHOCK",
            "candidate_id": "cand_2",
            "plan_row_id": "missing",
            "q_value": 0.01,
            "n_events": 200,
            "effect_shrunk_state": 0.01,
            "std_return": 0.01,
            "gate_stability": True,
            "gate_after_cost_positive": True,
            "gate_after_cost_stressed_positive": True,
            "gate_bridge_after_cost_positive_validation": True,
            "gate_bridge_after_cost_stressed_positive_validation": True,
            "gate_delay_robustness": True,
        },
        hypothesis_index={},
        negative_control_summary={"pass_rate_after_bh": 0.0},
        max_q_value=0.10,
        min_events=100,
        min_stability_score=0.05,
        min_sign_consistency=0.0,
        min_cost_survival_ratio=0.75,
        max_negative_control_pass_rate=0.01,
        min_tob_coverage=0.0,
        require_hypothesis_audit=True,
        allow_missing_negative_controls=True,
    )
    assert out["promotion_decision"] == "rejected"
    assert "hypothesis_missing_audit" in out["reject_reason"]


