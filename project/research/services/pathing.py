from __future__ import annotations

from pathlib import Path

from project.core.timeframes import normalize_timeframe


def phase2_run_dir(
    *,
    data_root: Path,
    run_id: str,
) -> Path:
    return Path(data_root) / "reports" / "phase2" / str(run_id)


def phase2_candidates_path(
    *,
    data_root: Path,
    run_id: str,
) -> Path:
    return phase2_run_dir(data_root=data_root, run_id=run_id) / "phase2_candidates.parquet"


def phase2_diagnostics_path(
    *,
    data_root: Path,
    run_id: str,
) -> Path:
    return phase2_run_dir(data_root=data_root, run_id=run_id) / "phase2_diagnostics.json"


def phase2_hypotheses_dir(
    *,
    data_root: Path,
    run_id: str,
) -> Path:
    return phase2_run_dir(data_root=data_root, run_id=run_id) / "hypotheses"


def phase2_symbol_out_dir(
    *,
    data_root: Path,
    run_id: str,
    symbol: str,
) -> Path:
    return phase2_run_dir(data_root=data_root, run_id=run_id) / "symbols" / str(symbol).upper()


def phase2_event_out_dir(
    *,
    data_root: Path,
    run_id: str,
    event_type: str,
    timeframe: str,
) -> Path:
    # Compatibility-only path for historical event-scoped phase-2 outputs.
    event_name = str(event_type or "ALL").strip().upper() or "ALL"
    tf = normalize_timeframe(timeframe or "5m")
    return phase2_run_dir(data_root=data_root, run_id=run_id) / "legacy" / event_name / tf


def bridge_event_out_dir(
    *,
    data_root: Path,
    run_id: str,
    event_type: str,
    timeframe: str,
) -> Path:
    event_name = str(event_type or "ALL").strip().upper() or "ALL"
    tf = normalize_timeframe(timeframe or "5m")
    return Path(data_root) / "reports" / "bridge_eval" / str(run_id) / event_name / tf


def negative_control_out_dir(
    *,
    data_root: Path,
    run_id: str,
) -> Path:
    return Path(data_root) / "reports" / "negative_control" / str(run_id)
