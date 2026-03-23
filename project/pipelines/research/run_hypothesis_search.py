"""
Pipeline stage: run the hypothesis search engine.

Sequence:
  1. generate_hypotheses() from the configured search space.
  2. Load feature table for each symbol.
  3. run_distributed_search(hypotheses, features).
  4. [Phase 3.3] cluster_hypotheses() deduplication — mark non-representatives
     as redundant before BH adjustment to improve statistical power.
  5. Write hypothesis_metrics.parquet and hypothesis_search_summary.json.
  6. Optionally write bridge_candidates.parquet (--run_bridge_adapter flag).
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd

from project.core.config import get_data_root
from project.research.search.generator import generate_hypotheses_with_audit
from project.research.search.distributed_runner import run_distributed_search
from project.research.search.bridge_adapter import (
    hypotheses_to_bridge_candidates,
    split_bridge_candidates,
    _sanitize_event_type,
)
from project.research.search.evaluator import evaluated_records_from_metrics
from project.research.phase2 import load_features
from project.io.utils import write_parquet


LOG = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Phase 3.3 — within-run alpha clustering deduplication
# ---------------------------------------------------------------------------


def _cluster_deduplicate(
    metrics: pd.DataFrame,
    *,
    eps: float = 0.3,
    min_samples: int = 1,
) -> pd.DataFrame:
    """Mark redundant hypotheses within a run before BH adjustment.

    Phase 3.3: Runs DBSCAN on pairwise metric-vector distances to identify
    clusters of correlated hypotheses.  For each cluster, only the
    representative (highest Sharpe) is kept; non-representatives are marked
    with ``is_cluster_redundant = True``.

    Since per-bar PnL streams are not available at this pipeline stage, the
    distance metric is computed from a normalised vector of aggregate metrics:
    (mean_return_bps, t_stat, sharpe, hit_rate).  Hypotheses whose aggregate
    profiles are nearly identical — which will generate correlated outcomes —
    are grouped together and deduplicated.

    The ``is_cluster_redundant`` column is written to the metrics parquet so
    downstream stages can filter it before FDR correction.  The full set of
    hypotheses is retained in the file to preserve audit traceability.
    """
    if metrics.empty:
        return metrics

    metrics = metrics.copy()
    metrics["is_cluster_redundant"] = False

    # Metric columns used for similarity proxy
    proxy_cols = [c for c in ["mean_return_bps", "t_stat", "sharpe", "hit_rate"] if c in metrics.columns]
    if not proxy_cols or "hypothesis_id" not in metrics.columns:
        return metrics

    valid = metrics.dropna(subset=proxy_cols)
    if len(valid) < 2:
        return metrics

    # Build normalised feature matrix — each row is one hypothesis
    X = valid[proxy_cols].values.astype(float)
    # Normalise column-wise (z-score); handle zero-std columns
    col_std = X.std(axis=0)
    col_std[col_std == 0] = 1.0
    X_norm = (X - X.mean(axis=0)) / col_std

    # Pairwise Euclidean distance in normalised metric space
    from sklearn.cluster import DBSCAN
    from sklearn.metrics import pairwise_distances

    dist = pairwise_distances(X_norm, metric="euclidean")

    clustering = DBSCAN(eps=eps, min_samples=min_samples, metric="precomputed")
    labels = clustering.fit_predict(dist)

    # Build cluster → hypothesis_id mapping
    h_ids = valid["hypothesis_id"].tolist()
    sharpe_col = "sharpe" if "sharpe" in valid.columns else proxy_cols[0]
    sharpes = valid[sharpe_col].fillna(0.0).tolist()

    cluster_map: dict[int, list[tuple[str, float]]] = {}
    for i, label in enumerate(labels):
        cluster_map.setdefault(int(label), []).append((h_ids[i], sharpes[i]))

    redundant_ids: set[str] = set()
    for label, members in cluster_map.items():
        if label == -1 or len(members) == 1:
            # Noise points or singletons — not redundant
            continue
        # Representative = highest Sharpe in cluster
        best_id = max(members, key=lambda m: m[1])[0]
        for hid, _ in members:
            if hid != best_id:
                redundant_ids.add(hid)

    if redundant_ids:
        mask = metrics["hypothesis_id"].isin(redundant_ids)
        metrics.loc[mask, "is_cluster_redundant"] = True
        LOG.info(
            "Phase 3.3 clustering: %d hypotheses → %d clusters → %d marked redundant",
            len(valid),
            len(cluster_map),
            len(redundant_ids),
        )

    return metrics


def _normalize_audit_frame(rows: list[dict]) -> pd.DataFrame:
    frame = pd.DataFrame(rows or [])
    if frame.empty:
        return frame
    for column in frame.columns:
        if frame[column].dtype != "object":
            continue
        sample = next(
            (
                value
                for value in frame[column]
                if value is not None and not (isinstance(value, float) and pd.isna(value))
            ),
            None,
        )
        if isinstance(sample, (dict, list, tuple)):
            frame[column] = frame[column].map(
                lambda value: (
                    json.dumps(value, sort_keys=True)
                    if isinstance(value, (dict, list, tuple))
                    else value
                )
            )
    return frame


def _write_hypothesis_audit_artifacts(out_dir: Path, audit: dict) -> None:
    write_parquet(
        _normalize_audit_frame(audit.get("generated_rows", [])),
        out_dir / "generated_hypotheses.parquet",
    )
    write_parquet(
        _normalize_audit_frame(audit.get("rejected_rows", [])),
        out_dir / "rejected_hypotheses.parquet",
    )
    write_parquet(
        _normalize_audit_frame(audit.get("feasible_rows", [])),
        out_dir / "feasible_hypotheses.parquet",
    )


def _write_evaluation_artifacts(
    out_dir: Path, metrics: pd.DataFrame, gate_failures: pd.DataFrame
) -> None:
    write_parquet(evaluated_records_from_metrics(metrics), out_dir / "evaluated_hypotheses.parquet")
    write_parquet(gate_failures, out_dir / "gate_failures.parquet")


def _build_regime_conditional_candidates(
    metrics: pd.DataFrame,
    *,
    min_overall_t_stat: float,
    min_regime_t_stat: float = 1.5,
    min_regime_n: int = 20,
) -> pd.DataFrame:
    if metrics.empty:
        return pd.DataFrame()

    required = {
        "hypothesis_id",
        "trigger_type",
        "template_id",
        "direction",
        "horizon",
        "entry_lag",
        "context_json",
        "mean_return_bps",
        "t_stat",
        "best_regime",
        "best_regime_n",
        "best_regime_mean_return_bps",
        "best_regime_t_stat",
        "regime_evaluations_json",
        "valid",
    }
    legacy_required = required - {"regime_evaluations_json"}
    if not (required.issubset(metrics.columns) or legacy_required.issubset(metrics.columns)):
        return pd.DataFrame()

    working = metrics.copy()
    working["valid"] = working["valid"].fillna(False)
    working["mean_return_bps"] = pd.to_numeric(working["mean_return_bps"], errors="coerce")
    working["t_stat"] = pd.to_numeric(working["t_stat"], errors="coerce")
    working["best_regime_mean_return_bps"] = pd.to_numeric(
        working["best_regime_mean_return_bps"], errors="coerce"
    )
    working["best_regime_t_stat"] = pd.to_numeric(
        working["best_regime_t_stat"], errors="coerce"
    )
    working["best_regime_n"] = (
        pd.to_numeric(working["best_regime_n"], errors="coerce").fillna(0).astype(int)
    )
    prefiltered = working[
        working["valid"]
        & (working["mean_return_bps"] > 0.0)
        & (working["t_stat"].abs() < float(min_overall_t_stat))
    ].copy()
    if prefiltered.empty:
        return pd.DataFrame()

    selected_rows: list[dict[str, object]] = []

    for _, row in prefiltered.iterrows():
        regime_payload = row.get("regime_evaluations_json", "[]")
        regime_rows = []
        if isinstance(regime_payload, str) and regime_payload.strip():
            try:
                decoded = json.loads(regime_payload)
                if isinstance(decoded, list):
                    regime_rows = [item for item in decoded if isinstance(item, dict)]
            except json.JSONDecodeError:
                regime_rows = []
        if not regime_rows:
            regime_rows = [
                {
                    "regime": row.get("best_regime"),
                    "n": row.get("best_regime_n"),
                    "mean_return_bps": row.get("best_regime_mean_return_bps"),
                    "t_stat": row.get("best_regime_t_stat"),
                    "valid": True,
                }
            ]

        regime_df = pd.DataFrame(regime_rows)
        if regime_df.empty:
            continue
        regime_df["valid"] = regime_df.get("valid", True).fillna(False)
        regime_df["n"] = pd.to_numeric(regime_df.get("n"), errors="coerce").fillna(0).astype(int)
        regime_df["mean_return_bps"] = pd.to_numeric(
            regime_df.get("mean_return_bps"), errors="coerce"
        )
        regime_df["t_stat"] = pd.to_numeric(regime_df.get("t_stat"), errors="coerce")
        regime_df["regime"] = regime_df.get("regime", "").astype(str)
        regime_df = regime_df[
            regime_df["valid"]
            & (regime_df["n"] >= int(min_regime_n))
            & (regime_df["mean_return_bps"] > 0.0)
            & (regime_df["t_stat"] >= float(min_regime_t_stat))
            & (regime_df["regime"].str.strip() != "")
        ].copy()
        if regime_df.empty:
            continue

        event_type = _sanitize_event_type(row)
        for regime_row in regime_df.to_dict(orient="records"):
            selected_rows.append(
                {
                    "hypothesis_id": row.get("hypothesis_id"),
                    "event_type": event_type,
                    "trigger_type": row.get("trigger_type"),
                    "template_id": row.get("template_id"),
                    "direction": row.get("direction"),
                    "horizon": row.get("horizon"),
                    "entry_lag": row.get("entry_lag"),
                    "context_json": row.get("context_json"),
                    "mean_return_bps": row.get("mean_return_bps"),
                    "t_stat": row.get("t_stat"),
                    "best_regime": regime_row.get("regime"),
                    "best_regime_n": int(regime_row.get("n", 0) or 0),
                    "best_regime_mean_return_bps": regime_row.get("mean_return_bps"),
                    "best_regime_t_stat": regime_row.get("t_stat"),
                }
            )

    if not selected_rows:
        return pd.DataFrame()

    selected = pd.DataFrame(selected_rows)
    selected["priority_score"] = (
        pd.to_numeric(selected["best_regime_t_stat"], errors="coerce").fillna(0.0)
        - pd.to_numeric(selected["t_stat"], errors="coerce").abs().fillna(0.0)
    )
    selected["reason"] = "weak_overall_strong_regime"
    selected = selected.sort_values(
        ["priority_score", "best_regime_mean_return_bps", "mean_return_bps", "best_regime_n"],
        ascending=[False, False, False, False],
    )
    return selected[
        [
            "hypothesis_id",
            "event_type",
            "trigger_type",
            "template_id",
            "direction",
            "horizon",
            "entry_lag",
            "context_json",
            "mean_return_bps",
            "t_stat",
            "best_regime",
            "best_regime_n",
            "best_regime_mean_return_bps",
            "best_regime_t_stat",
            "priority_score",
            "reason",
        ]
    ].reset_index(drop=True)


def _load_all_features(
    symbols: List[str],
    run_id: str,
    timeframe: str,
    data_root: Path,
) -> pd.DataFrame:
    """Load and concatenate features across all symbols."""
    parts: list[pd.DataFrame] = []
    for sym in symbols:
        df = load_features(data_root, run_id, sym, timeframe=timeframe)
        if not df.empty:
            df = df.copy()
            df["symbol"] = sym
            parts.append(df)
    if not parts:
        return pd.DataFrame()
    return pd.concat(parts, ignore_index=True)


def _make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run hypothesis search engine")
    parser.add_argument("--run_id", required=True)
    parser.add_argument("--symbols", required=True)
    parser.add_argument("--timeframe", default="5m")
    parser.add_argument(
        "--n_workers",
        type=int,
        default=0,
        help="0 = auto (cpu_count)",
    )
    parser.add_argument("--chunk_size", type=int, default=256)
    parser.add_argument("--min_t_stat", type=float, default=1.5)
    parser.add_argument("--min_n", type=int, default=30)
    parser.add_argument("--use_context_quality", type=int, default=1)
    parser.add_argument(
        "--run_bridge_adapter",
        type=int,
        default=0,
        help="1 to emit bridge_candidates.parquet alongside metrics",
    )
    parser.add_argument(
        "--search_space_path",
        default=None,
        help="Optional override for search-space YAML path",
    )
    parser.add_argument(
        "--cluster_deduplication",
        type=int,
        default=1,
        help="1 (default) to run within-run alpha clustering before writing output",
    )
    parser.add_argument(
        "--cluster_eps",
        type=float,
        default=0.3,
        help="DBSCAN eps (Euclidean distance in normalised metric space, default 0.3)",
    )
    parser.add_argument(
        "--data_root",
        default=None,
        help="Optional override for data root (defaults to configured data root)",
    )
    parser.add_argument(
        "--out_dir",
        default=None,
        help="Optional override for output directory",
    )
    return parser


def main() -> int:
    parser = _make_parser()
    args = parser.parse_args()

    data_root = Path(args.data_root) if args.data_root else get_data_root()
    out_dir = (
        Path(args.out_dir)
        if args.out_dir
        else (data_root / "reports" / "hypothesis_search" / args.run_id)
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    symbols = [s.strip().upper() for s in str(args.symbols).split(",") if s.strip()]
    n_workers = args.n_workers if args.n_workers > 0 else None
    search_space_path = Path(args.search_space_path) if args.search_space_path else None

    features = _load_all_features(symbols, args.run_id, args.timeframe, data_root)
    try:
        hypotheses, generation_audit = generate_hypotheses_with_audit(
            search_space_path=search_space_path,
            features=None if features.empty else features,
        )
    except Exception as exc:  # pragma: no cover - defensive
        LOG.error("Failed to generate hypotheses: %s", exc)
        return 1

    _write_hypothesis_audit_artifacts(out_dir, generation_audit)
    LOG.info("Generated %d hypotheses", len(hypotheses))

    if features.empty:
        LOG.warning(
            "No features loaded for symbols=%s run_id=%s; writing empty output.",
            symbols,
            args.run_id,
        )
        metrics = pd.DataFrame()
    else:
        try:
            metrics = run_distributed_search(
                hypotheses,
                features,
                n_workers=n_workers,
                chunk_size=args.chunk_size,
                use_context_quality=bool(int(args.use_context_quality)),
            )
        except Exception as exc:  # pragma: no cover - defensive
            LOG.error("Distributed search failed: %s", exc)
            return 1

    # Phase 3.3 — within-run alpha clustering deduplication
    # Mark near-duplicate hypotheses before writing metrics so downstream
    # BH adjustment operates on a deduplicated family.
    if not metrics.empty and int(args.cluster_deduplication):
        metrics = _cluster_deduplicate(metrics, eps=float(args.cluster_eps))

    metrics_path = out_dir / "hypothesis_metrics.parquet"
    if not metrics.empty:
        write_parquet(metrics, metrics_path)
    else:
        # Preserve schema by writing an empty frame with no rows.
        write_parquet(pd.DataFrame(), metrics_path)
    regime_conditional = _build_regime_conditional_candidates(
        metrics,
        min_overall_t_stat=float(args.min_t_stat),
    )
    write_parquet(regime_conditional, out_dir / "regime_conditional_candidates.parquet")
    _, gate_failures = split_bridge_candidates(
        metrics,
        min_t_stat=args.min_t_stat,
        min_n=args.min_n,
    )
    _write_evaluation_artifacts(out_dir, metrics, gate_failures)

    passing = (
        int((metrics["t_stat"].abs() >= args.min_t_stat).sum())
        if (not metrics.empty and "t_stat" in metrics.columns)
        else 0
    )
    redundant_count = (
        int(metrics["is_cluster_redundant"].sum())
        if (not metrics.empty and "is_cluster_redundant" in metrics.columns)
        else 0
    )
    summary = {
        "run_id": args.run_id,
        "symbols": symbols,
        "timeframe": args.timeframe,
        "total_hypotheses": int(
            generation_audit.get("counts", {}).get("generated", len(hypotheses))
        ),
        "feasible_hypotheses": int(
            generation_audit.get("counts", {}).get("feasible", len(hypotheses))
        ),
        "rejected_hypotheses": int(generation_audit.get("counts", {}).get("rejected", 0)),
        "rejection_reason_counts": dict(generation_audit.get("rejection_reason_counts", {})),
        "evaluated": int(len(metrics)) if not metrics.empty else 0,
        "passing_filter": passing,
        "cluster_redundant": redundant_count,
        "use_context_quality": bool(int(args.use_context_quality)),
    }
    (out_dir / "hypothesis_search_summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    if int(args.run_bridge_adapter) and not metrics.empty:
        candidates = hypotheses_to_bridge_candidates(
            metrics,
            min_t_stat=args.min_t_stat,
            min_n=args.min_n,
        )
        write_parquet(candidates, out_dir / "bridge_candidates.parquet")

    LOG.info(
        "Wrote %d evaluated hypotheses (%d passing) to %s",
        len(metrics),
        passing,
        out_dir,
    )
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
