from __future__ import annotations

import json

import pandas as pd

from project.pipelines import pipeline_summary


def test_load_kpi_source_frame_prefers_normalized_edge_candidates(tmp_path, monkeypatch) -> None:
    data_root = tmp_path / "data"
    run_id = "r_edge"
    edge_path = (
        data_root
        / "reports"
        / "edge_candidates"
        / run_id
        / "edge_candidates_normalized.parquet"
    )
    edge_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([{"net_expectancy_bps": 3.5}]).to_parquet(edge_path, index=False)
    monkeypatch.setenv("BACKTEST_DATA_ROOT", str(data_root))

    df, name, path = pipeline_summary.load_kpi_source_frame(run_id)

    assert df is not None
    assert name == "edge_candidates"
    assert path == edge_path


def test_write_run_kpi_scorecard_writes_file_from_normalized_edge_candidates(
    tmp_path, monkeypatch
) -> None:
    data_root = tmp_path / "data"
    run_id = "r_scorecard"
    edge_path = (
        data_root
        / "reports"
        / "edge_candidates"
        / run_id
        / "edge_candidates_normalized.parquet"
    )
    edge_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                "net_expectancy_bps": 4.0,
                "trade_count": 12,
                "max_drawdown_pct": -0.08,
                "sign_consistency": 0.75,
                "turnover_proxy_mean": 1.2,
                "edge_score": 0.4,
            }
        ]
    ).to_parquet(edge_path, index=False)
    monkeypatch.setenv("BACKTEST_DATA_ROOT", str(data_root))

    pipeline_summary.write_run_kpi_scorecard(run_id)

    scorecard_path = data_root / "runs" / run_id / "kpi_scorecard.json"
    assert scorecard_path.exists()
    payload = json.loads(scorecard_path.read_text(encoding="utf-8"))
    assert payload["source"]["name"] == "edge_candidates"
    assert payload["source"]["path"] == str(edge_path)
    assert payload["completeness"] == "partial"
    assert payload["metrics"]["net_expectancy_bps"]["value"] == 4.0


def test_write_run_kpi_scorecard_writes_null_metrics_for_empty_edge_candidates(
    tmp_path, monkeypatch
) -> None:
    data_root = tmp_path / "data"
    run_id = "r_empty_scorecard"
    edge_path = (
        data_root
        / "reports"
        / "edge_candidates"
        / run_id
        / "edge_candidates_normalized.parquet"
    )
    edge_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(columns=["net_expectancy_bps", "trade_count"]).to_parquet(edge_path, index=False)
    monkeypatch.setenv("BACKTEST_DATA_ROOT", str(data_root))

    pipeline_summary.write_run_kpi_scorecard(run_id)

    scorecard_path = data_root / "runs" / run_id / "kpi_scorecard.json"
    assert scorecard_path.exists()
    payload = json.loads(scorecard_path.read_text(encoding="utf-8"))
    assert payload["source"]["path"] == str(edge_path)
    assert payload["metrics"]["net_expectancy_bps"]["value"] is None
    assert payload["metrics"]["trade_count"]["value"] is None
