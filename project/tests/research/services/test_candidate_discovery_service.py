from __future__ import annotations

import json
from types import SimpleNamespace
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import project.research.services.candidate_discovery_service as svc
import project.pipelines.research.experiment_engine as experiment_engine


class _HypothesisRegistry:
    def register(self, hyp):
        return "hyp-1"

    def write_artifacts(self, out_dir):
        return "hash-1"


class _Hypothesis:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


def _make_features(n_bars: int = 80, *, freq: str = "5min") -> pd.DataFrame:
    ts = pd.date_range("2024-01-01", periods=n_bars, freq=freq, tz="UTC")
    close = np.arange(100.0, 100.0 + float(n_bars))
    return pd.DataFrame(
        {
            "timestamp": ts,
            "close": close,
            "atr_14": np.full(n_bars, 1.0),
        }
    )


def _make_events_from_features(
    features: pd.DataFrame, n_events: int = 30, start_bar: int = 5
) -> pd.DataFrame:
    event_ts = features["timestamp"].iloc[start_bar : start_bar + n_events].reset_index(drop=True)
    return pd.DataFrame(
        {
            "enter_ts": event_ts,
            "timestamp": event_ts,
            "symbol": ["BTCUSDT"] * len(event_ts),
            "event_type": ["VOL_SHOCK"] * len(event_ts),
        }
    )


def _run_candidate_discovery(tmp_path, **overrides):
    config = svc.CandidateDiscoveryConfig(
        run_id="r1",
        symbols=("BTCUSDT",),
        config_paths=(),
        data_root=tmp_path,
        event_type="VOL_SHOCK",
        timeframe="5m",
        horizon_bars=24,
        out_dir=tmp_path / "phase2",
        run_mode="exploratory",
        split_scheme_id="WF_60_20_20",
        embargo_bars=0,
        purge_bars=0,
        train_only_lambda_used=0.0,
        discovery_profile="standard",
        candidate_generation_method="phase2_v1",
        concept_file=None,
        entry_lag_bars=1,
        shift_labels_k=0,
        fees_bps=None,
        slippage_bps=None,
        cost_bps=None,
        cost_calibration_mode="auto",
        cost_min_tob_coverage=0.6,
        cost_tob_tolerance_minutes=5,
        candidate_origin_run_id=None,
        frozen_spec_hash=None,
    )
    if overrides:
        config = svc.CandidateDiscoveryConfig(**(config.__dict__ | overrides))
    return svc.execute_candidate_discovery(config)


def test_run_candidate_discovery_service_smoke(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "project.core.execution_costs.load_configs",
        lambda paths: {"fee_bps_per_side": 4.0, "slippage_bps_per_fill": 2.0},
    )
    events = pd.DataFrame(
        {
            "enter_ts": pd.date_range("2024-01-01", periods=8, freq="5min", tz="UTC"),
            "timestamp": pd.date_range("2024-01-01", periods=8, freq="5min", tz="UTC"),
            "symbol": ["BTCUSDT"] * 8,
            "event_type": ["VOL_SHOCK"] * 8,
            "close": [100, 101, 102, 103, 104, 105, 106, 107],
        }
    )
    cands = pd.DataFrame(
        [
            {
                "candidate_id": "cand_1",
                "event_type": "VOL_SHOCK",
                "symbol": "BTCUSDT",
                "direction": 1.0,
                "family_id": "fam_1",
                "horizon": "24",
            }
        ]
    )

    monkeypatch.setattr(svc, "get_data_root", lambda: tmp_path)
    monkeypatch.setattr(svc, "prepare_events_dataframe", lambda **kwargs: events)
    monkeypatch.setattr(
        svc.discovery, "_synthesize_registry_candidates", lambda **kwargs: cands.copy()
    )
    monkeypatch.setattr(svc.discovery, "bars_to_timeframe", lambda bars: "2h")
    monkeypatch.setattr(svc.discovery, "action_name_from_direction", lambda direction: "LONG")
    monkeypatch.setattr(svc, "HypothesisRegistry", _HypothesisRegistry)
    monkeypatch.setattr(svc, "Hypothesis", _Hypothesis)

    result = _run_candidate_discovery(tmp_path)
    assert result.exit_code == 0
    assert not result.combined_candidates.empty
    assert "hypothesis_id" in result.combined_candidates.columns
    assert any((tmp_path / "phase2" / "BTCUSDT").glob("phase2_candidates.*"))
    diagnostics = json.loads(
        (tmp_path / "phase2" / "phase2_diagnostics.json").read_text(encoding="utf-8")
    )
    assert diagnostics["combined_candidate_rows"] == 1
    assert diagnostics["symbol_diagnostics"][0]["prepare_events"]["raw_event_count"] == 8
    assert "false_discovery_diagnostics" in diagnostics
    assert diagnostics["false_discovery_diagnostics"]["global"]["candidates_total"] == 1


def test_false_discovery_diagnostics_summarize_sample_and_survivor_quality():
    combined = pd.DataFrame(
        [
            {
                "candidate_id": "cand_1",
                "symbol": "BTCUSDT",
                "family_id": "fam_a",
                "validation_n_obs": 10,
                "test_n_obs": 8,
                "n_obs": 18,
                "q_value": 0.01,
                "q_value_by": 0.02,
                "estimate_bps": 12.5,
                "resolved_cost_bps": 6.0,
                "is_discovery": True,
            },
            {
                "candidate_id": "cand_2",
                "symbol": "BTCUSDT",
                "family_id": "fam_b",
                "validation_n_obs": 0,
                "test_n_obs": 0,
                "n_obs": 0,
                "q_value": 0.8,
                "q_value_by": 0.9,
                "estimate_bps": -1.0,
                "resolved_cost_bps": 6.0,
                "is_discovery": False,
            },
        ]
    )

    diagnostics = svc._build_false_discovery_diagnostics(combined)

    assert diagnostics["global"]["candidates_total"] == 2
    assert diagnostics["global"]["survivors_total"] == 1
    assert diagnostics["sample_quality"]["zero_eval_rows"] == 1
    assert diagnostics["survivor_quality"]["survivors_total"] == 1
    assert diagnostics["survivor_quality"]["median_q_value"] == pytest.approx(0.01)
    assert diagnostics["by_symbol"]["BTCUSDT"]["sample_quality"]["zero_validation_rows"] == 1


def test_apply_sample_quality_gates_demotes_weak_multiplicity_survivor():
    candidates = pd.DataFrame(
        [
            {
                "candidate_id": "cand_keep",
                "symbol": "BTCUSDT",
                "validation_n_obs": 4,
                "test_n_obs": 3,
                "n_obs": 9,
                "q_value": 0.02,
                "is_discovery": True,
            },
            {
                "candidate_id": "cand_drop",
                "symbol": "BTCUSDT",
                "validation_n_obs": 0,
                "test_n_obs": 2,
                "n_obs": 2,
                "q_value": 0.01,
                "is_discovery": True,
            },
        ]
    )

    out = svc._apply_sample_quality_gates(
        candidates,
        min_validation_n_obs=1,
        min_test_n_obs=1,
        min_total_n_obs=5,
    )

    kept = out.loc[out["candidate_id"] == "cand_keep"].iloc[0]
    dropped = out.loc[out["candidate_id"] == "cand_drop"].iloc[0]
    assert bool(kept["is_discovery"]) is True
    assert bool(kept["gate_sample_quality"]) is True
    assert bool(dropped["is_discovery_pre_sample_quality"]) is True
    assert bool(dropped["is_discovery"]) is False
    assert bool(dropped["rejected_by_sample_quality"]) is True
    assert dropped["sample_quality_fail_reason"] == "min_validation_n_obs"


def test_run_candidate_discovery_service_records_sample_quality_gate_thresholds(
    monkeypatch, tmp_path
):
    monkeypatch.setattr(
        "project.core.execution_costs.load_configs",
        lambda paths: {"fee_bps_per_side": 4.0, "slippage_bps_per_fill": 2.0},
    )
    events = pd.DataFrame(
        {
            "enter_ts": pd.date_range("2024-01-01", periods=8, freq="5min", tz="UTC"),
            "timestamp": pd.date_range("2024-01-01", periods=8, freq="5min", tz="UTC"),
            "symbol": ["BTCUSDT"] * 8,
            "event_type": ["VOL_SHOCK"] * 8,
            "close": [100, 101, 102, 103, 104, 105, 106, 107],
        }
    )
    cands = pd.DataFrame(
        [
            {
                "candidate_id": "cand_1",
                "event_type": "VOL_SHOCK",
                "symbol": "BTCUSDT",
                "direction": 1.0,
                "family_id": "fam_1",
                "horizon": "24",
            }
        ]
    )

    monkeypatch.setattr(svc, "get_data_root", lambda: tmp_path)
    monkeypatch.setattr(svc, "prepare_events_dataframe", lambda **kwargs: events)
    monkeypatch.setattr(
        svc.discovery, "_synthesize_registry_candidates", lambda **kwargs: cands.copy()
    )
    monkeypatch.setattr(svc.discovery, "bars_to_timeframe", lambda bars: "2h")
    monkeypatch.setattr(svc.discovery, "action_name_from_direction", lambda direction: "LONG")
    monkeypatch.setattr(svc, "HypothesisRegistry", _HypothesisRegistry)
    monkeypatch.setattr(svc, "Hypothesis", _Hypothesis)

    result = _run_candidate_discovery(
        tmp_path,
        min_validation_n_obs=2,
        min_test_n_obs=2,
        min_total_n_obs=6,
    )

    assert result.exit_code == 0
    diagnostics = json.loads(
        (tmp_path / "phase2" / "phase2_diagnostics.json").read_text(encoding="utf-8")
    )
    assert diagnostics["sample_quality_gate_thresholds"] == {
        "min_validation_n_obs": 2,
        "min_test_n_obs": 2,
        "min_total_n_obs": 6,
    }


def test_run_candidate_discovery_service_records_non_directional_registry_policy(
    monkeypatch, tmp_path
):
    monkeypatch.setattr(
        "project.core.execution_costs.load_configs",
        lambda paths: {"fee_bps_per_side": 4.0, "slippage_bps_per_fill": 2.0},
    )
    events = pd.DataFrame(
        {
            "enter_ts": pd.date_range("2024-01-01", periods=8, freq="5min", tz="UTC"),
            "timestamp": pd.date_range("2024-01-01", periods=8, freq="5min", tz="UTC"),
            "symbol": ["BTCUSDT"] * 8,
            "event_type": ["ZSCORE_STRETCH"] * 8,
            "direction": ["non_directional"] * 8,
            "close": [100, 101, 102, 103, 104, 105, 106, 107],
        }
    )

    monkeypatch.setattr(svc, "get_data_root", lambda: tmp_path)
    monkeypatch.setattr(svc, "prepare_events_dataframe", lambda **kwargs: events)
    monkeypatch.setattr(
        svc.discovery, "_synthesize_registry_candidates", lambda **kwargs: pd.DataFrame()
    )
    monkeypatch.setattr(
        svc.discovery,
        "resolve_registry_direction_policy",
        lambda *args, **kwargs: {
            "policy": "non_directional_skip",
            "source": "unresolved",
            "resolved": False,
            "direction_sign": 0.0,
        },
    )
    monkeypatch.setattr(svc, "HypothesisRegistry", _HypothesisRegistry)
    monkeypatch.setattr(svc, "Hypothesis", _Hypothesis)

    result = _run_candidate_discovery(tmp_path, event_type="ZSCORE_STRETCH")

    assert result.exit_code == 0
    diagnostics = json.loads(
        (tmp_path / "phase2" / "phase2_diagnostics.json").read_text(encoding="utf-8")
    )
    symbol_diag = diagnostics["symbol_diagnostics"][0]
    assert symbol_diag["direction_policy"]["policy"] == "non_directional_skip"
    assert symbol_diag["direction_policy"]["resolved"] is False
    assert symbol_diag["direction_policy"]["skipped_non_directional_registry_generation"] is True


def test_resolve_sample_quality_policy_uses_profile_defaults():
    standard = svc._resolve_sample_quality_policy(
        svc.CandidateDiscoveryConfig(
            run_id="r1",
            symbols=("BTCUSDT",),
            config_paths=(),
            data_root=Path("/tmp"),
            event_type="VOL_SHOCK",
            timeframe="5m",
            horizon_bars=24,
            out_dir=None,
            run_mode="exploratory",
            split_scheme_id="WF_60_20_20",
            embargo_bars=0,
            purge_bars=0,
            train_only_lambda_used=0.0,
            discovery_profile="standard",
            candidate_generation_method="phase2_v1",
            concept_file=None,
            entry_lag_bars=1,
            shift_labels_k=0,
            fees_bps=None,
            slippage_bps=None,
            cost_bps=None,
            cost_calibration_mode="auto",
            cost_min_tob_coverage=0.6,
            cost_tob_tolerance_minutes=5,
            candidate_origin_run_id=None,
            frozen_spec_hash=None,
        )
    )
    synthetic = svc._resolve_sample_quality_policy(
        svc.CandidateDiscoveryConfig(
            run_id="r2",
            symbols=("BTCUSDT",),
            config_paths=(),
            data_root=Path("/tmp"),
            event_type="VOL_SHOCK",
            timeframe="5m",
            horizon_bars=24,
            out_dir=None,
            run_mode="exploratory",
            split_scheme_id="WF_60_20_20",
            embargo_bars=0,
            purge_bars=0,
            train_only_lambda_used=0.0,
            discovery_profile="synthetic",
            candidate_generation_method="phase2_v1",
            concept_file=None,
            entry_lag_bars=1,
            shift_labels_k=0,
            fees_bps=None,
            slippage_bps=None,
            cost_bps=None,
            cost_calibration_mode="auto",
            cost_min_tob_coverage=0.6,
            cost_tob_tolerance_minutes=5,
            candidate_origin_run_id=None,
            frozen_spec_hash=None,
        )
    )

    assert standard["min_validation_n_obs"] == 10
    assert standard["min_test_n_obs"] == 10
    assert standard["min_total_n_obs"] == 30
    assert synthetic["min_validation_n_obs"] == 1
    assert synthetic["min_test_n_obs"] == 1
    assert synthetic["min_total_n_obs"] == 4


def test_run_candidate_discovery_service_passes_timeframe_to_prepare_events(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "project.core.execution_costs.load_configs",
        lambda paths: {"fee_bps_per_side": 4.0, "slippage_bps_per_fill": 2.0},
    )
    events = pd.DataFrame(
        {
            "enter_ts": pd.date_range("2024-01-01", periods=4, freq="15min", tz="UTC"),
            "timestamp": pd.date_range("2024-01-01", periods=4, freq="15min", tz="UTC"),
            "symbol": ["BTCUSDT"] * 4,
            "event_type": ["VOL_SHOCK"] * 4,
            "close": [100, 101, 102, 103],
        }
    )
    cands = pd.DataFrame(
        [
            {
                "candidate_id": "cand_1",
                "event_type": "VOL_SHOCK",
                "symbol": "BTCUSDT",
                "direction": 1.0,
                "family_id": "fam_1",
                "horizon": "24",
            }
        ]
    )
    captured: dict[str, object] = {}

    def _prepare(**kwargs):
        captured["timeframe"] = kwargs.get("timeframe")
        return events

    monkeypatch.setattr(svc, "get_data_root", lambda: tmp_path)
    monkeypatch.setattr(svc, "prepare_events_dataframe", _prepare)
    monkeypatch.setattr(
        svc.discovery, "_synthesize_registry_candidates", lambda **kwargs: cands.copy()
    )
    monkeypatch.setattr(svc.discovery, "bars_to_timeframe", lambda bars: "6h")
    monkeypatch.setattr(svc.discovery, "action_name_from_direction", lambda direction: "LONG")
    monkeypatch.setattr(svc, "HypothesisRegistry", _HypothesisRegistry)
    monkeypatch.setattr(svc, "Hypothesis", _Hypothesis)

    result = _run_candidate_discovery(
        tmp_path,
        run_id="r2",
        timeframe="15m",
    )

    assert result.exit_code == 0
    assert captured["timeframe"] == "15m"


