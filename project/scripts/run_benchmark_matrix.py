import argparse
import json
import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import yaml

try:
    import pandas as pd
except ImportError:
    pd = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_yaml(path: Path) -> Dict[str, Any]:
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def run_mock_benchmark(slice_def: Dict[str, Any], mode_name: str, mode_def: Dict[str, Any]) -> Dict[str, Any]:
    # Mock output matching required schema
    import random
    
    baseline_offset = 1.0 if mode_name == 'baseline_flat' else random.uniform(0.9, 1.2)
    
    return {
        "candidate_count_generated": int(1000 * baseline_offset),
        "candidate_count_evaluated": int(800 * baseline_offset),
        "candidate_count_final": int(10 * baseline_offset),
        "search_budget_used": 100.0,
        "wall_clock_seconds": 120.0 * baseline_offset,
        "top_n_median_after_cost_expectancy_bps": 2.5 * baseline_offset,
        "top_n_median_adjusted_q_value": 0.8 * baseline_offset,
        "top_n_median_fold_sign_consistency": 0.65 * baseline_offset,
        "top_n_median_discovery_quality_score": 0.7 * baseline_offset,
        "promotion_survival_rate_top_n": 0.25 * baseline_offset,
        "raw_top_n_cluster_count": 5,
        "shortlist_cluster_count": 3,
        "shortlist_avg_similarity": 0.6,
        "shortlist_distinct_trigger_family_count": 2,
        "shortlist_distinct_lineage_count": 6,
        "trigger_proposal_count": 10 if mode_name.startswith('trigger') else 0,
        "mean_registry_novelty_score": 0.3 if mode_name.startswith('trigger') else 0.0,
        "mean_trigger_candidate_quality_score": 0.15 if mode_name.startswith('trigger') else 0.0,
        "redundant_trigger_ratio": 0.5 if mode_name.startswith('trigger') else 0.0,
    }

def evaluate_thresholds(metrics: Dict[str, Any], thresholds: Dict[str, Any], is_trigger: bool) -> Dict[str, Any]:
    failed = []
    warnings = []
    t = thresholds.get("thresholds", {})
    
    if metrics["candidate_count_final"] < t.get("min_final_candidates", 5):
        failed.append("min_final_candidates")
    if metrics["top_n_median_fold_sign_consistency"] < t.get("min_top10_median_fold_sign_consistency", 0.6):
        failed.append("min_top10_median_fold_sign_consistency")
    if metrics["top_n_median_after_cost_expectancy_bps"] < t.get("min_top10_after_cost_expectancy_bps", 0.0):
        failed.append("min_top10_after_cost_expectancy_bps")
    if metrics["promotion_survival_rate_top_n"] < t.get("min_top10_promotion_survival_rate", 0.2):
        failed.append("min_top10_promotion_survival_rate")
    if metrics["shortlist_avg_similarity"] > t.get("max_shortlist_avg_similarity", 0.75):
        warnings.append("max_shortlist_avg_similarity")
    if metrics["shortlist_distinct_lineage_count"] < t.get("min_shortlist_distinct_lineage_count", 5):
        failed.append("min_shortlist_distinct_lineage_count")
        
    if is_trigger:
        tt = thresholds.get("trigger_discovery", {})
        if metrics["mean_registry_novelty_score"] < tt.get("min_mean_registry_novelty_score", 0.2):
            failed.append("min_mean_registry_novelty_score")
        if metrics["redundant_trigger_ratio"] > tt.get("max_redundant_trigger_ratio", 0.7):
            failed.append("max_redundant_trigger_ratio")
        if metrics["mean_trigger_candidate_quality_score"] < tt.get("min_trigger_candidate_quality_score", 0.1):
            failed.append("min_trigger_candidate_quality_score")
            
    return {
        "benchmark_pass": len(failed) == 0,
        "failed_thresholds": failed,
        "warning_thresholds": warnings
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preset", type=str, required=True, help="Preset name (e.g. core_v1)")
    args = parser.parse_args()

    # Load preset
    base_dir = Path("project/configs/benchmarks/discovery")
    preset_path = base_dir / f"{args.preset}.yaml"
    if not preset_path.exists():
        logger.error(f"Preset {preset_path} not found.")
        return 1
        
    preset = load_yaml(preset_path)
    modes = preset.get("benchmark_modes", {})
    slices = preset.get("slices", [])
    
    thresholds_path = base_dir / "thresholds_v1.yaml"
    thresholds = load_yaml(thresholds_path) if thresholds_path.exists() else {"thresholds": {}, "trigger_discovery": {}}

    benchmark_run_id = f"run_{uuid.uuid4().hex[:8]}"
    generated_at = datetime.now(timezone.utc).isoformat()
    
    out_dir = Path("data/reports/benchmarks") / benchmark_run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    
    summaries = []
    
    for slice_file in slices:
        slice_path = base_dir / slice_file
        if not slice_path.exists():
            logger.warning(f"Slice {slice_path} not found.")
            continue
            
        slice_def = load_yaml(slice_path)
        slice_id = slice_def.get("slice_id", slice_file)
        
        baseline_metrics = None
        slice_results = []
        
        # Run baseline first to compute deltas
        if "baseline_flat" in modes:
            metrics = run_mock_benchmark(slice_def, "baseline_flat", modes["baseline_flat"])
            baseline_metrics = metrics
            
        for mode_name, mode_def in modes.items():
            metrics = run_mock_benchmark(slice_def, mode_name, mode_def)
            is_trigger = "trigger" in mode_name
            threshold_outcomes = evaluate_thresholds(metrics, thresholds, is_trigger)
            
            # Compute deltas
            if baseline_metrics and mode_name != "baseline_flat":
                metrics["delta_after_cost_expectancy_vs_baseline"] = metrics["top_n_median_after_cost_expectancy_bps"] - baseline_metrics["top_n_median_after_cost_expectancy_bps"]
                metrics["delta_fold_sign_consistency_vs_baseline"] = metrics["top_n_median_fold_sign_consistency"] - baseline_metrics["top_n_median_fold_sign_consistency"]
                metrics["delta_candidate_count_vs_baseline"] = metrics["candidate_count_final"] - baseline_metrics["candidate_count_final"]
                metrics["delta_shortlist_similarity_vs_baseline"] = metrics["shortlist_avg_similarity"] - baseline_metrics["shortlist_avg_similarity"]
                metrics["delta_promotion_survival_vs_baseline"] = metrics["promotion_survival_rate_top_n"] - baseline_metrics["promotion_survival_rate_top_n"]
            elif mode_name == "baseline_flat":
                metrics["delta_after_cost_expectancy_vs_baseline"] = 0.0
                metrics["delta_fold_sign_consistency_vs_baseline"] = 0.0
                metrics["delta_candidate_count_vs_baseline"] = 0
                metrics["delta_shortlist_similarity_vs_baseline"] = 0.0
                metrics["delta_promotion_survival_vs_baseline"] = 0.0
                
            summary = {
                "benchmark_run_id": benchmark_run_id,
                "preset_name": args.preset,
                "generated_at": generated_at,
                "slice_id": slice_id,
                "symbols": slice_def.get("symbols", []),
                "timeframe": slice_def.get("timeframe", ""),
                "start": str(slice_def.get("date_range", ["", ""])[0]),
                "end": str(slice_def.get("date_range", ["", ""])[1]),
                "mode_name": mode_name,
                **metrics,
                **threshold_outcomes
            }
            summaries.append(summary)
            slice_results.append(summary)
            
    # Write JSON summary
    summary_path = out_dir / "benchmark_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summaries, f, indent=2)
        
    # Write Markdown review
    review_path = out_dir / "benchmark_review.md"
    with open(review_path, "w", encoding="utf-8") as f:
        f.write(f"# Benchmark Review: {benchmark_run_id}\n\n")
        for s in summaries:
            f.write(f"## Slice: {s['slice_id']} | Mode: {s['mode_name']}\n")
            f.write(f"- Pass: {s['benchmark_pass']}\n")
            if s['failed_thresholds']:
                f.write(f"- Failed: {', '.join(s['failed_thresholds'])}\n")
            f.write(f"- Expectancy BPS: {s['top_n_median_after_cost_expectancy_bps']:.2f} (Delta: {s.get('delta_after_cost_expectancy_vs_baseline', 0):.2f})\n")
            f.write(f"- Fold Sign Consistency: {s['top_n_median_fold_sign_consistency']:.2f}\n")
            f.write("\n")
            
    # Append to history parquet
    if pd is not None:
        history_dir = Path("data/artifacts/benchmarks/history")
        history_dir.mkdir(parents=True, exist_ok=True)
        history_path = history_dir / "benchmark_history.parquet"
        
        df = pd.DataFrame(summaries)
        if history_path.exists():
            try:
                existing_df = pd.read_parquet(history_path)
                df = pd.concat([existing_df, df], ignore_index=True)
            except Exception as e:
                logger.error(f"Failed to read existing parquet: {e}")
        try:
            df.to_parquet(history_path, index=False)
        except Exception as e:
            logger.error(f"Failed to write parquet: {e}")
    else:
        logger.warning("pandas not installed, skipping parquet history append.")
        
    logger.info(f"Benchmark {benchmark_run_id} complete. Results in {out_dir}")
    
if __name__ == "__main__":
    main()
