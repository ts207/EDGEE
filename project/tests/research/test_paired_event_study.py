from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from project.research.paired_event_study import build_direct_paired_event_study
from project.research.thesis_evidence_runner import build_founding_thesis_evidence


def _write_raw_partition(root: Path, symbol: str, dataset: str, frame: pd.DataFrame, *, year: int, month: int, stem: str) -> None:
    out_dir = root / "lake" / "raw" / "perp" / symbol / dataset / f"year={year}" / f"month={month:02d}"
    out_dir.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(out_dir / f"{stem}.parquet", index=False)


def _synthetic_bars(symbol: str) -> pd.DataFrame:
    timestamps = list(pd.date_range("2021-01-01", periods=240, freq="5min", tz="UTC"))
    timestamps += list(pd.date_range("2022-01-01", periods=240, freq="5min", tz="UTC"))
    close = []
    price = 100.0 if symbol == "BTCUSDT" else 50.0
    for idx, _ts in enumerate(timestamps):
        cycle = idx % 12
        if cycle == 0:
            price *= 1.08
        elif cycle in {1, 2, 3}:
            price *= 1.01
        else:
            price *= 1.0005
        close.append(price)
    close = np.asarray(close)
    open_ = np.concatenate([[close[0] / 1.001], close[:-1]])
    high = np.maximum(open_, close) * 1.002
    low = np.minimum(open_, close) * 0.998
    volume = np.where(np.arange(len(close)) % 12 == 0, 2000.0, 500.0)
    return pd.DataFrame(
        {
            "timestamp": pd.to_datetime(timestamps, utc=True),
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
            "quote_volume": volume * close,
            "taker_base_volume": volume * 0.55,
            "symbol": symbol,
            "source": "synthetic",
        }
    )


def test_build_direct_paired_event_study_updates_bundle_metadata(tmp_path: Path, monkeypatch) -> None:
    data_root = tmp_path / "data"
    docs = tmp_path / "docs"
    monkeypatch.setenv("BACKTEST_DATA_ROOT", str(data_root))

    for symbol in ("BTCUSDT", "ETHUSDT"):
        bars = _synthetic_bars(symbol)
        for year in (2021, 2022):
            subset = bars[bars["timestamp"].dt.year == year]
            _write_raw_partition(data_root, symbol, "ohlcv_5m", subset, year=year, month=1, stem=f"ohlcv_{symbol}_5m_{year}-01")

    policy_path = tmp_path / "founding_policy.yaml"
    policy_path.write_text(
        yaml.safe_dump(
            {
                "founding_theses": [
                    {
                        "candidate_id": "THESIS_VOL_SHOCK",
                        "event_type": "VOL_SHOCK",
                        "detector_kind": "vol_shock",
                        "symbols": ["BTCUSDT", "ETHUSDT"],
                        "horizons": [2, 4],
                        "payoff_mode": "absolute_return",
                        "fees_bps": 1.0,
                        "params": {"rv_window": 3, "baseline_window": 12, "shock_quantile": 0.8},
                    },
                    {
                        "candidate_id": "THESIS_LIQUIDITY_VACUUM",
                        "event_type": "LIQUIDITY_VACUUM",
                        "detector_kind": "liquidity_vacuum",
                        "symbols": ["BTCUSDT", "ETHUSDT"],
                        "horizons": [2, 4],
                        "payoff_mode": "absolute_return",
                        "fees_bps": 1.0,
                        "params": {
                            "shock_quantile": 0.8,
                            "shock_window": 12,
                            "volume_window": 6,
                            "vol_ratio_floor": 0.95,
                            "range_multiplier": 1.0,
                            "lookahead_bars": 3,
                            "min_vacuum_bars": 1,
                        },
                    },
                    {
                        "candidate_id": "THESIS_VOL_SHOCK_LIQUIDITY_CONFIRM",
                        "event_type": "VOL_SHOCK_LIQUIDITY_CONFIRM",
                        "event_contract_ids": ["VOL_SHOCK", "LIQUIDITY_VACUUM"],
                        "detector_kind": "vol_shock_liquidity_confirm",
                        "symbols": ["BTCUSDT", "ETHUSDT"],
                        "horizons": [2, 4],
                        "payoff_mode": "absolute_return",
                        "fees_bps": 1.0,
                        "params": {
                            "confirmation_window_bars": 3,
                            "require_confirmation_after_trigger": True,
                            "trigger_kind": "vol_shock",
                            "confirm_kind": "liquidity_vacuum",
                            "trigger_params": {"rv_window": 3, "baseline_window": 12, "shock_quantile": 0.8},
                            "confirm_params": {
                                "shock_quantile": 0.8,
                                "shock_window": 12,
                                "volume_window": 6,
                                "vol_ratio_floor": 0.95,
                                "range_multiplier": 1.0,
                                "lookahead_bars": 3,
                                "min_vacuum_bars": 1,
                            },
                        },
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    build_founding_thesis_evidence(policy_path=policy_path, docs_dir=docs, data_root=data_root)
    bundle_dir = data_root / "reports" / "promotions" / "THESIS_VOL_SHOCK_LIQUIDITY_CONFIRM"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    bundle_payload = {
        "candidate_id": "THESIS_VOL_SHOCK_LIQUIDITY_CONFIRM",
        "event_type": "VOL_SHOCK_LIQUIDITY_CONFIRM",
        "event_family": "VOL_SHOCK",
        "symbol": "BTCUSDT",
        "sample_definition": {"n_events": 25, "validation_samples": 12, "test_samples": 13, "symbol": "BTCUSDT", "horizon_bars": 2},
        "effect_estimates": {"estimate_bps": 50.0, "validation_mean_bps": 55.0, "test_mean_bps": 45.0, "payoff_mode": "absolute_return"},
        "cost_robustness": {"fees_bps": 1.0, "net_expectancy_bps": 49.0, "gross_expectancy_bps": 50.0},
        "uncertainty_estimates": {"q_value": 0.01, "effect_p_value": 0.01},
        "stability_tests": {"stability_score": 0.8, "validation_mean_bps": 55.0, "test_mean_bps": 45.0, "validation_test_gap_bps": 10.0},
        "falsification_results": {"negative_control_pass_rate": 0.0, "session_transition": {"available": True, "passed": True}, "realized_vol_regime": {"available": True, "passed": True}},
        "multiplicity_adjustment": {"correction_method": "single_test_founding_thesis", "adjusted_q_value": 0.01},
        "metadata": {"has_realized_oos_path": True, "thesis_id": "THESIS_VOL_SHOCK_LIQUIDITY_CONFIRM", "event_contract_ids": ["VOL_SHOCK", "LIQUIDITY_VACUUM"], "thesis_contract_id": "THESIS_VOL_SHOCK_LIQUIDITY_CONFIRM", "thesis_contract_ids": ["THESIS_VOL_SHOCK_LIQUIDITY_CONFIRM"], "input_symbols": ["BTCUSDT", "ETHUSDT"], "notes": "seed bundle"},
    }
    (bundle_dir / "evidence_bundles.jsonl").write_text(json.dumps(bundle_payload) + "\n", encoding="utf-8")
    out = build_direct_paired_event_study(policy_path=policy_path, docs_dir=docs, data_root=data_root)

    payload = json.loads(out["report_json"].read_text(encoding="utf-8"))
    assert payload["thesis_id"] == "THESIS_VOL_SHOCK_LIQUIDITY_CONFIRM"
    assert payload["selected_horizon_bars"] in {2, 4}
    assert payload["decision_support"]["direct_pair_evidence_present"] is True

    bundle_path = data_root / "reports" / "promotions" / "THESIS_VOL_SHOCK_LIQUIDITY_CONFIRM" / "evidence_bundles.jsonl"
    rows = [json.loads(line) for line in bundle_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert rows
    for row in rows:
        metadata = row["metadata"]
        assert metadata["direct_pair_event_evidence"] is True
        assert metadata["direct_pair_event_study_id"] == "THESIS_VOL_SHOCK_LIQUIDITY_CONFIRM_direct_pair_event_study"
