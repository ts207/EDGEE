from __future__ import annotations

import argparse
import json
import logging
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from project import PROJECT_ROOT
from project.core.config import get_data_root
from project.research.services.benchmark_matrix_service import load_benchmark_matrix
from project.research.services.promotion_readiness_service import (
    build_promotion_readiness_report,
    render_promotion_readiness_terminal,
    write_promotion_readiness_report,
)

# Import main from run_benchmark_matrix to reuse orchestration
from project.scripts.run_benchmark_matrix import main as run_matrix_main

def _utc_now_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

def find_historical_reviews(matrix_id: str, history_limit: int = 5) -> List[Path]:
    """
    Find existing benchmark_review.json files in history.
    """
    data_root = get_data_root()
    bench_dir = data_root / "reports" / "benchmarks"
    h_path = bench_dir / "history"
    if not h_path.exists():
        return []
    
    # History dirs are named <matrix_id>_<timestamp>
    # We sort them by name descending (newest first)
    runs = sorted(
        [d for d in h_path.iterdir() if d.is_dir() and d.name.startswith(f"{matrix_id}_")],
        key=lambda x: x.name,
        reverse=True
    )
    
    reviews = []
    for r in runs[:history_limit]:
        review_file = r / "benchmark_review.json"
        if review_file.exists():
            reviews.append(review_file)
            
    return reviews

def main() -> int:
    parser = argparse.ArgumentParser(description="Unified benchmark maintenance cycle.")
    parser.add_argument(
        "--matrix",
        default=str(PROJECT_ROOT.parent / "spec" / "benchmarks" / "research_family_matrix.yaml"),
        help="Path to benchmark matrix YAML.",
    )
    parser.add_argument("--execute", type=int, default=1, help="If 1, execute benchmark runs.")
    parser.add_argument("--history-limit", type=int, default=5, help="Number of historical baselines to keep.")
    args = parser.parse_args()

    data_root = get_data_root()
    timestamp = _utc_now_compact()
    
    # 1. Resolve output directory
    matrix = load_benchmark_matrix(Path(args.matrix))
    matrix_id = matrix.get("matrix_id", "matrix")
    
    bench_dir = data_root / "reports" / "benchmarks"
    history_dir = bench_dir / "history" / f"{matrix_id}_{timestamp}"
    latest_link = bench_dir / "latest"
    
    # Discover priors before we start the new run
    priors = find_historical_reviews(matrix_id=matrix_id, history_limit=args.history_limit)
    print(f"[cycle] Starting maintenance for {matrix_id}...")
    print(f"[cycle] Discovered {len(priors)} historical priors for multi-baseline comparison.")
    print(f"[cycle] Output target: {history_dir}")

    # 2. Run the matrix
    # We call main() with overridden sys.argv
    orig_argv = sys.argv
    matrix_argv = [
        "run_benchmark_matrix.py",
        "--matrix", args.matrix,
        "--execute", str(args.execute),
        "--out_dir", str(history_dir),
    ]
    if priors:
        matrix_argv.extend(["--priors"] + [str(p) for p in priors])
        
    sys.argv = matrix_argv
    try:
        matrix_exit = run_matrix_main()
    finally:
        sys.argv = orig_argv

    if matrix_exit != 0:
        print("[cycle] Matrix run or certification failed. Continuing to report generation.")

    # 3. Generate Promotion Readiness Report
    review_path = history_dir / "benchmark_review.json"
    cert_path = history_dir / "benchmark_certification.json"
    
    if review_path.exists() and cert_path.exists():
        review = json.loads(review_path.read_text(encoding="utf-8"))
        cert = json.loads(cert_path.read_text(encoding="utf-8"))
        
        report = build_promotion_readiness_report(
            benchmark_review=review,
            benchmark_certification=cert,
        )
        write_promotion_readiness_report(out_dir=history_dir, report=report)
        print(f"[cycle] Wrote readiness report: {history_dir / 'promotion_readiness.json'}")
        
        print("")
        print(render_promotion_readiness_terminal(report))
    else:
        print("[cycle] ERROR: Core benchmark artifacts not found. Skipping readiness report.")

    # 4. Update 'latest' pointer (symlink or copy)
    if history_dir.exists():
        if latest_link.exists():
            if latest_link.is_symlink():
                latest_link.unlink()
            else:
                shutil.rmtree(latest_link)
        
        try:
            latest_link.symlink_to(history_dir.relative_to(bench_dir), target_is_directory=True)
            print(f"[cycle] Updated latest pointer: {latest_link} -> {history_dir.name}")
        except Exception:
            shutil.copytree(history_dir, latest_link)
            print(f"[cycle] Copied results to latest pointer: {latest_link}")

    # 5. History Cleanup
    h_path = bench_dir / "history"
    if h_path.exists():
        runs = sorted(
            [d for d in h_path.iterdir() if d.is_dir() and d.name.startswith(f"{matrix_id}_")],
            key=lambda x: x.name,
            reverse=True
        )
        if len(runs) > args.history_limit:
            for old_run in runs[args.history_limit:]:
                print(f"[cycle] Cleaning up old history: {old_run.name}")
                shutil.rmtree(old_run)

    print("")
    print("[cycle] Maintenance cycle COMPLETE.")
    return matrix_exit

if __name__ == "__main__":
    sys.exit(main())
