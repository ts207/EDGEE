import argparse
import json
import logging
import os
from pathlib import Path
from typing import List, Optional

from project import PROJECT_ROOT

logger = logging.getLogger(__name__)


def get_data_root() -> Path:
    """Return the canonical data root from environment or default."""
    return Path(os.getenv("BACKTEST_DATA_ROOT", PROJECT_ROOT.parent / "data"))


DATA_ROOT: Path = get_data_root()


def find_latest_review(data_root: Path | None = None) -> Path | None:
    """Find the most recently modified benchmark review file, preferring canonical."""
    root = data_root or get_data_root()
    
    # Priority 1: Canonical 'benchmarks'
    canonical_path = root / "reports" / "benchmarks" / "history"
    if canonical_path.exists():
        reviews = list(canonical_path.glob("**/benchmark_review.json"))
        if reviews:
            return max(reviews, key=lambda x: x.stat().st_mtime)
            
    # Priority 2: Legacy 'perf_benchmarks'
    legacy_path = root / "reports" / "perf_benchmarks" / "history"
    if legacy_path.exists():
        reviews = list(legacy_path.glob("**/benchmark_review.json"))
        if reviews:
            return max(reviews, key=lambda x: x.stat().st_mtime)
 
    return None


def find_historical_reviews(matrix_id: str, limit: int = 5) -> list[Path]:
    """Return the N latest review paths for a specific matrix_id."""
    root = get_data_root()
    search_paths = [
        root / "reports" / "benchmarks" / "history",
        root / "reports" / "perf_benchmarks" / "history",
    ]
 
    matches: list[Path] = []
    for p in search_paths:
        if p.exists():
            # Look for directories starting with matrix_id
            for d in p.iterdir():
                if d.is_dir() and d.name.startswith(f"{matrix_id}_"):
                    review_file = d / "benchmark_review.json"
                    if review_file.exists():
                        matches.append(review_file)
 
    # Sort by mtime descending
    matches.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return matches[:limit]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark_run_id", type=str, help="Specific benchmark run ID")
    parser.add_argument("--latest", action="store_true", help="Show latest benchmark")
    args = parser.parse_args()

    reports_dir = Path("data/reports/benchmarks")
    if not reports_dir.exists():
        print("No benchmarks found.")
        return 1
        
    run_dir = None
    if args.latest:
        runs = sorted([d for d in reports_dir.iterdir() if d.is_dir()], key=lambda x: x.stat().st_mtime, reverse=True)
        if not runs:
            print("No benchmarks found.")
            return 1
        run_dir = runs[0]
    elif args.benchmark_run_id:
        run_dir = reports_dir / args.benchmark_run_id
        if not run_dir.exists():
            print(f"Benchmark {args.benchmark_run_id} not found.")
            return 1
    else:
        print("Please provide --benchmark_run_id or --latest")
        return 1

    summary_path = run_dir / "benchmark_summary.json"
    if not summary_path.exists():
        print(f"No summary found at {summary_path}")
        return 1
        
    with open(summary_path, "r", encoding="utf-8") as f:
        summaries = json.load(f)
        
    print(f"=== Benchmark Review: {run_dir.name} ===")
    
    # Process summaries
    for s in summaries:
        print(f"\nSlice: {s.get('slice_id')} | Mode: {s.get('mode_name')}")
        status = "PASS" if s.get("benchmark_pass") else "FAIL"
        print(f"  Status: {status}")
        if s.get("failed_thresholds"):
            print(f"  Failed: {', '.join(s.get('failed_thresholds', []))}")
        print(f"  Expectancy BPS: {s.get('top_n_median_after_cost_expectancy_bps', 0):.2f} (Delta: {s.get('delta_after_cost_expectancy_vs_baseline', 0):.2f})")
        print(f"  Fold Sign Consistency: {s.get('top_n_median_fold_sign_consistency', 0):.2f}")
        
if __name__ == "__main__":
    main()
