from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from project.research.seed_bootstrap import build_promotion_seed_inventory
from project.research.seed_empirical import run_empirical_seed_pass
from project.research.thesis_evidence_runner import build_founding_thesis_evidence


def _write_raw_partition(root: Path, symbol: str, dataset: str, frame: pd.DataFrame, *, year: int, month: int, stem: str) -> None:
    out_dir = root / "lake" / "raw" / "perp" / symbol / dataset / f"year={year}" / f"month={month:02d}"
    out_dir.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(out_dir / f"{stem}.parquet", index=False)


def _synthetic_bars() -> pd.DataFrame:
    timestamps = list(pd.date_range("2021-01-01", periods=240, freq="5min", tz="UTC"))
    timestamps += list(pd.date_range("2022-01-01", periods=240, freq="5min", tz="UTC"))
    close = []
    price = 100.0
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
            "symbol": "BTCUSDT",
            "source": "synthetic",
        }
    )


def test_build_founding_thesis_evidence_writes_bundle(tmp_path: Path, monkeypatch) -> None:
    data_root = tmp_path / "data"
    docs = tmp_path / "docs"
    monkeypatch.setenv("BACKTEST_DATA_ROOT", str(data_root))

    bars = _synthetic_bars()
    _write_raw_partition(data_root, "BTCUSDT", "ohlcv_5m", bars[bars["timestamp"].dt.year == 2021], year=2021, month=1, stem="ohlcv_BTCUSDT_5m_2021-01")
    _write_raw_partition(data_root, "BTCUSDT", "ohlcv_5m", bars[bars["timestamp"].dt.year == 2022], year=2022, month=1, stem="ohlcv_BTCUSDT_5m_2022-01")

    policy_path = tmp_path / "founding_policy.yaml"
    policy_path.write_text(
        yaml.safe_dump(
            {
                "founding_theses": [
                    {
                        "candidate_id": "THESIS_VOL_TEST",
                        "event_type": "VOL_SHOCK",
                        "detector_kind": "vol_shock",
                        "symbols": ["BTCUSDT"],
                        "horizons": [2, 4],
                        "payoff_mode": "absolute_return",
                        "fees_bps": 1.0,
                        "params": {"rv_window": 3, "baseline_window": 12, "shock_quantile": 0.8},
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    out = build_founding_thesis_evidence(policy_path=policy_path, docs_dir=docs, data_root=data_root)
    bundle_path = data_root / "reports" / "promotions" / "THESIS_VOL_TEST" / "evidence_bundles.jsonl"
    assert bundle_path.exists()
    rows = [json.loads(line) for line in bundle_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert rows
    row = rows[0]
    assert row["candidate_id"] == "THESIS_VOL_TEST"
    assert row["sample_definition"]["test_samples"] > 0
    assert row["metadata"]["has_realized_oos_path"] is True
    assert "THESIS_VOL_TEST" in out["json"].read_text(encoding="utf-8")


def test_empirical_confirm_candidate_requires_explicit_bundle(tmp_path: Path, monkeypatch) -> None:
    docs = tmp_path / "docs"
    data_root = tmp_path / "data"
    monkeypatch.setenv("BACKTEST_DATA_ROOT", str(data_root))
    build_promotion_seed_inventory(docs_dir=docs)

    for run_id, event_type in (("run-vol", "VOL_SHOCK"), ("run-liq", "LIQUIDITY_VACUUM")):
        out_dir = data_root / "reports" / "promotions" / run_id
        out_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "candidate_id": f"THESIS_{event_type}",
            "event_family": event_type,
            "event_type": event_type,
            "sample_definition": {"n_events": 120, "validation_samples": 40, "test_samples": 40},
            "effect_estimates": {"estimate_bps": 20.0},
            "uncertainty_estimates": {"q_value": 0.03},
            "stability_tests": {"stability_score": 0.10},
            "falsification_results": {"negative_control_pass_rate": 0.01, "session_transition": {"passed": True}},
            "cost_robustness": {"net_expectancy_bps": 10.0},
            "metadata": {"has_realized_oos_path": True},
        }
        (out_dir / "evidence_bundles.jsonl").write_text(json.dumps(payload) + "\n", encoding="utf-8")

    out = run_empirical_seed_pass(docs_dir=docs, inventory_path=docs / "promotion_seed_inventory.csv", data_root=data_root)
    rows = json.loads(out["json"].read_text(encoding="utf-8"))
    confirm = next(row for row in rows if row["candidate_id"] == "THESIS_VOL_SHOCK_LIQUIDITY_CONFIRM")
    assert int(confirm["matched_bundle_count"]) == 0
    assert confirm["empirical_decision"] == "needs_more_evidence"
