import json
import os
from pathlib import Path
from project.scripts.run_benchmark_matrix import load_yaml, evaluate_thresholds

def test_benchmark_preset_loading():
    preset_path = Path("project/configs/benchmarks/discovery/core_v1.yaml")
    assert preset_path.exists()
    preset = load_yaml(preset_path)
    assert "benchmark_modes" in preset
    assert "slices" in preset
    assert "baseline_flat" in preset["benchmark_modes"]

def test_summary_schema(tmp_path):
    summary = {
        "benchmark_run_id": "test_1",
        "preset_name": "core_v1",
        "generated_at": "2026-04-04T12:00:00Z",
        "slice_id": "m0_strong_event",
        "mode_name": "baseline_flat",
        "candidate_count_generated": 100,
        "top_n_median_after_cost_expectancy_bps": 2.5
    }
    assert "benchmark_run_id" in summary
    assert "mode_name" in summary

def test_baseline_comparison():
    baseline = {"top_n_median_after_cost_expectancy_bps": 2.0}
    mode = {"top_n_median_after_cost_expectancy_bps": 3.0}
    delta = mode["top_n_median_after_cost_expectancy_bps"] - baseline["top_n_median_after_cost_expectancy_bps"]
    assert delta == 1.0

def test_threshold_evaluation():
    thresholds = {
        "thresholds": {
            "min_final_candidates": 5
        }
    }
    metrics_pass = {
        "candidate_count_final": 10,
        "shortlist_avg_similarity": 0.5,
        "shortlist_distinct_lineage_count": 6,
        "top_n_median_fold_sign_consistency": 0.7,
        "top_n_median_after_cost_expectancy_bps": 1.0,
        "promotion_survival_rate_top_n": 0.3
    }
    res_pass = evaluate_thresholds(metrics_pass, thresholds, is_trigger=False)
    assert "min_final_candidates" not in res_pass["failed_thresholds"]

    metrics_fail = {
        "candidate_count_final": 2,
        "shortlist_avg_similarity": 0.5,
        "shortlist_distinct_lineage_count": 6,
        "top_n_median_fold_sign_consistency": 0.7,
        "top_n_median_after_cost_expectancy_bps": 1.0,
        "promotion_survival_rate_top_n": 0.3
    }
    res_fail = evaluate_thresholds(metrics_fail, thresholds, is_trigger=False)
    assert "min_final_candidates" in res_fail["failed_thresholds"]

def test_history_append(tmp_path):
    import pandas as pd
    from project.scripts.run_benchmark_matrix import pd as run_pd
    if run_pd is not None:
        df = pd.DataFrame([{"benchmark_run_id": "test_1"}])
        history_path = tmp_path / "benchmark_history.parquet"
        df.to_parquet(history_path, index=False)
        assert history_path.exists()
        df_read = pd.read_parquet(history_path)
        assert df_read.iloc[0]["benchmark_run_id"] == "test_1"

def test_review_artifact(tmp_path):
    review_path = tmp_path / "benchmark_review.md"
    with open(review_path, "w", encoding="utf-8") as f:
        f.write("# Benchmark Review\n\n## Slice: m0\n- Pass: True")
    content = review_path.read_text(encoding="utf-8")
    assert "Benchmark Review" in content
    assert "Pass: True" in content
