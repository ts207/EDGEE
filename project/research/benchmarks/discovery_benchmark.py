import json
import logging
from pathlib import Path
import pandas as pd
import yaml
import shutil
import tempfile
from project.research import phase2_search_engine
from project import PROJECT_ROOT

log = logging.getLogger(__name__)

BENCHMARK_SPEC_PATH = PROJECT_ROOT.parent / "project/research/benchmarks/discovery_benchmark_spec.yaml"
DATA_ROOT = PROJECT_ROOT.parent / "data"

def run_benchmark(spec_path: Path = BENCHMARK_SPEC_PATH):
    if not spec_path.exists():
        log.error(f"Benchmark spec not found at {spec_path}")
        return

    with open(spec_path, "r") as f:
        spec = yaml.safe_load(f)

    benchmark_id = f"bench_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}"
    base_out_dir = DATA_ROOT / "reports/discovery_benchmarks" / benchmark_id
    base_out_dir.mkdir(parents=True, exist_ok=True)

    results = []

    for case in spec["cases"]:
        case_id = case["id"]
        log.info(f"Running benchmark case: {case_id}")
        
        case_out_dir = base_out_dir / case_id
        case_out_dir.mkdir(parents=True, exist_ok=True)

        symbol = case["symbol"]
        search_spec = case["search_spec"]
        
        # Write case-specific search spec
        spec_file = case_out_dir / "search_spec.yaml"
        with open(spec_file, "w") as f:
            yaml.safe_dump(search_spec, f)

        # Run modes: Legacy (v2 off), V2 (v2 on), Ledger (v2 on + ledger on)
        # Note: Ledger mode currently requires discovery_ledger.yaml modification or monkeypatching
        # For now, we'll focus on Legacy vs V2 as requested.
        
        modes = [
            {"id": "legacy", "v2": False, "ledger": False, "status": "STABLE"},
            {"id": "v2", "v2": True, "ledger": False, "status": "STABLE-INTERNAL"},
        ]
        
        # Check if ledger config exists and we should test it
        ledger_config_path = PROJECT_ROOT.parent / "project/configs/discovery_ledger.yaml"
        if ledger_config_path.exists():
            modes.append({"id": "ledger", "v2": True, "ledger": True, "status": "EXPERIMENTAL"})

        case_results = {}

        for mode in modes:
            mode_id = mode["id"]
            run_id = f"{case_id}_{mode_id}"
            run_out_dir = case_out_dir / mode_id
            run_out_dir.mkdir(parents=True, exist_ok=True)

            log.info(f"  Mode: {mode_id}")
            
            # Monkeypatch ledger config if needed
            original_ledger_content = None
            if mode["ledger"]:
                with open(ledger_config_path, "r") as f:
                    original_ledger_content = f.read()
                # Enable ledger
                new_content = original_ledger_content.replace("enabled: false", "enabled: true")
                with open(ledger_config_path, "w") as f:
                    f.write(new_content)

            try:
                # Actually, phase2_search_engine.run() has enable_discovery_v2_scoring
                # but doesn't have a direct hook for ledger yet (it's in CandidateDiscoveryService)
                # However, for the benchmark, we can manually apply it if the search engine doesn't.
                
                phase2_search_engine.run(
                    run_id=run_id,
                    symbols=symbol,
                    data_root=DATA_ROOT,
                    out_dir=run_out_dir,
                    search_spec=str(spec_file),
                    enable_discovery_v2_scoring=mode["v2"]
                )
                
                candidates_file = run_out_dir / f"phase2_candidates.parquet"
                # Search engine might write to run_out_dir / symbol / ... or directly
                # Actually looking at phase2_search_engine.py:
                # output_path = phase2_candidates_path(data_root=data_root, run_id=run_id)
                # Let's find where it actually went
                candidate_paths = list(run_out_dir.glob("**/phase2_candidates.parquet"))
                if not candidate_paths:
                    # Try data_root/reports/phase2/run_id/...
                    candidate_paths = list((DATA_ROOT / "reports/phase2" / run_id).glob("**/phase2_candidates.parquet"))

                if candidate_paths:
                    df = pd.read_parquet(candidate_paths[0])
                    # If ledger mode but search engine didn't apply it (which it doesn't currently)
                    if mode["ledger"]:
                        from project.research.services.candidate_discovery_scoring import apply_ledger_multiplicity_correction
                        df = apply_ledger_multiplicity_correction(df, data_root=DATA_ROOT, current_run_id=run_id)
                        # Save it back enriched
                        df.to_parquet(candidate_paths[0])
                    
                    case_results[mode_id] = df
                else:
                    log.warning(f"No candidates found for {case_id} {mode_id}")

            finally:
                if original_ledger_content:
                    with open(ledger_config_path, "w") as f:
                        f.write(original_ledger_content)

        # Compare results for this case
        if "legacy" in case_results and "v2" in case_results:
            comparison = summarize_case_comparison(case_id, case_results, case_out_dir)
            results.append(comparison)

    # Global summary
    if results:
        global_summary = summarize_global_benchmark(results, base_out_dir)
        log.info(f"Benchmark complete. Summary at {base_out_dir}/benchmark_summary.md")

def summarize_case_comparison(case_id, case_results, out_dir):
    legacy_df = case_results["legacy"]
    v2_df = case_results["v2"]
    ledger_df = case_results.get("ledger")

    # Align by candidate_id if possible, or build human-readable key
    def add_key(df):
        if df is None or df.empty: 
            return pd.DataFrame(columns=["comp_key", "legacy_rank", "v2_rank", "ledger_rank", "t_stat", "discovery_quality_score"])
        df = df.copy()
        # Handle cases where columns are missing
        for col in ["event_type", "horizon", "direction"]:
            if col not in df.columns:
                df[col] = "unknown"
        df["comp_key"] = df["event_type"] + "|" + df["horizon"] + "|" + df["direction"].apply(str)
        return df

    legacy_df = add_key(legacy_df)
    v2_df = add_key(v2_df)
    
    # Ranks
    if not legacy_df.empty and "t_stat" in legacy_df.columns:
        legacy_df["legacy_rank"] = legacy_df["t_stat"].abs().rank(ascending=False)
    else:
        legacy_df["legacy_rank"] = pd.Series(dtype=int)

    if not v2_df.empty:
        if "discovery_quality_score" in v2_df.columns:
            v2_df["v2_rank"] = v2_df["discovery_quality_score"].rank(ascending=False)
        elif "t_stat" in v2_df.columns:
            v2_df["v2_rank"] = v2_df["t_stat"].abs().rank(ascending=False)
        else:
            v2_df["v2_rank"] = pd.Series(dtype=int)
    else:
        v2_df["v2_rank"] = pd.Series(dtype=int)
    
    # Merge for comparison
    cols_legacy = ["comp_key", "legacy_rank"] + (["t_stat"] if "t_stat" in legacy_df.columns else [])
    cols_v2 = ["comp_key", "v2_rank"] + (["discovery_quality_score"] if "discovery_quality_score" in v2_df.columns else [])
    
    merged = pd.merge(
        legacy_df[cols_legacy] if not legacy_df.empty else pd.DataFrame(columns=cols_legacy),
        v2_df[cols_v2] if not v2_df.empty else pd.DataFrame(columns=cols_v2),
        on="comp_key",
        how="outer",
        suffixes=("_legacy", "_v2")
    )

    if ledger_df is not None and not ledger_df.empty:
        ledger_df = add_key(ledger_df)
        score_col = "discovery_quality_score_v3" if "discovery_quality_score_v3" in ledger_df.columns else "discovery_quality_score"
        if score_col in ledger_df.columns:
            ledger_df["ledger_rank"] = ledger_df[score_col].rank(ascending=False)
        else:
            ledger_df["ledger_rank"] = pd.Series(dtype=int)
        
        cols_ledger = ["comp_key", "ledger_rank"] + ([score_col] if score_col in ledger_df.columns else [])
        merged = pd.merge(
            merged,
            ledger_df[cols_ledger],
            on="comp_key",
            how="outer"
        )

    merged.to_csv(out_dir / "rank_comparison.csv", index=False)
    
    # Top 10 movers
    if "legacy_rank" in merged.columns and "v2_rank" in merged.columns:
        merged["rank_delta_v2"] = merged["legacy_rank"] - merged["v2_rank"]
        movers = merged.sort_values("rank_delta_v2", ascending=False).head(10)
        movers.to_csv(out_dir / "rank_movers.csv", index=False)

    merged.to_csv(out_dir / "rank_comparison.csv", index=False)
    
    # Top 10 movers
    merged["rank_delta_v2"] = merged["legacy_rank"] - merged["v2_rank"]
    movers = merged.sort_values("rank_delta_v2", ascending=False).head(10)
    movers.to_csv(out_dir / "rank_movers.csv", index=False)

    return {
        "case_id": case_id,
        "legacy_count": len(legacy_df),
        "v2_count": len(v2_df),
        "top_10_overlap": len(set(legacy_df.head(10)["comp_key"]) & set(v2_df.head(10)["comp_key"])) if not legacy_df.empty and not v2_df.empty else 0
    }

def summarize_global_benchmark(results, out_dir):
    df = pd.DataFrame(results)
    df.to_csv(out_dir / "benchmark_summary.csv", index=False)
    
    md = [f"# Discovery Benchmark Summary: {out_dir.name}\n"]
    md.append("| Case | Legacy Count | V2 Count | Top-10 Overlap |")
    md.append("| --- | --- | --- | --- |")
    for r in results:
        md.append(f"| {r['case_id']} | {r['legacy_count']} | {r['v2_count']} | {r['top_10_overlap']} |")
    
    with open(out_dir / "benchmark_summary.md", "w") as f:
        f.write("\n".join(md))
    
    with open(out_dir / "benchmark_summary.json", "w") as f:
        json.dump(results, f, indent=2)

    return df

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_benchmark()
