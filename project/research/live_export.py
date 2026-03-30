from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence

import numpy as np
import pandas as pd

from project.artifacts import live_thesis_index_path, promoted_theses_path
from project.core.coercion import safe_float, safe_int
from project.core.config import get_data_root
from project.core.exceptions import DataIntegrityError
from project.io.utils import ensure_dir
from project.live.contracts import PromotedThesis, ThesisEvidence, ThesisLineage


@dataclass(frozen=True)
class PromotedThesisExportResult:
    run_id: str
    output_path: Path
    index_path: Path
    thesis_count: int
    active_count: int
    pending_count: int


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _json_load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DataIntegrityError(f"Failed to read live thesis json artifact {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise DataIntegrityError(f"Live thesis json artifact {path} did not contain an object payload")
    return payload


def _load_table(path: Path) -> pd.DataFrame:
    if path.exists():
        try:
            if path.suffix.lower() == ".parquet":
                return pd.read_parquet(path)
            if path.suffix.lower() == ".csv":
                return pd.read_csv(path)
        except Exception as exc:
            raise DataIntegrityError(f"Failed to read live thesis tabular artifact {path}: {exc}") from exc
    return pd.DataFrame()


def _read_jsonl_records(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        raise DataIntegrityError(f"Failed to read jsonl artifact {path}: {exc}") from exc
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise DataIntegrityError(
                f"Malformed JSONL record in {path} at line {line_number}: {exc}"
            ) from exc
        if isinstance(payload, dict):
            rows.append(payload)
        else:
            raise DataIntegrityError(
                f"JSONL record in {path} at line {line_number} was not an object payload"
            )
    return rows


def _promotion_dir(run_id: str, data_root: Path) -> Path:
    return data_root / "reports" / "promotions" / str(run_id)


def _blueprint_dir(run_id: str, data_root: Path) -> Path:
    return data_root / "reports" / "strategy_blueprints" / str(run_id)


def _load_evidence_bundles(run_id: str, data_root: Path) -> list[dict[str, Any]]:
    return _read_jsonl_records(_promotion_dir(run_id, data_root) / "evidence_bundles.jsonl")


def _load_promoted_candidates(run_id: str, data_root: Path) -> pd.DataFrame:
    promotion_root = _promotion_dir(run_id, data_root)
    for candidate_path in (
        promotion_root / "promoted_candidates.parquet",
        promotion_root / "promoted_candidates.csv",
    ):
        frame = _load_table(candidate_path)
        if not frame.empty:
            return frame
    return pd.DataFrame()


def _load_blueprints(run_id: str, data_root: Path) -> list[dict[str, Any]]:
    return _read_jsonl_records(_blueprint_dir(run_id, data_root) / "blueprints.jsonl")


def _row_by_candidate_id(frame: pd.DataFrame) -> dict[str, dict[str, Any]]:
    if frame.empty or "candidate_id" not in frame.columns:
        return {}
    rows: dict[str, dict[str, Any]] = {}
    for row in frame.to_dict(orient="records"):
        candidate_id = str(row.get("candidate_id", "")).strip()
        if candidate_id and candidate_id not in rows:
            rows[candidate_id] = dict(row)
    return rows


def _blueprint_by_candidate_id(rows: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for row in rows:
        candidate_id = str(row.get("candidate_id", "")).strip()
        if candidate_id and candidate_id not in indexed:
            indexed[candidate_id] = dict(row)
    return indexed


def _timeframe_from_minutes(value: Any) -> str:
    minutes = int(safe_int(value, 0))
    if minutes <= 0:
        return ""
    if minutes % 1440 == 0:
        return f"{minutes // 1440}d"
    if minutes % 60 == 0:
        return f"{minutes // 60}h"
    return f"{minutes}m"


def _finite_or_none(value: Any) -> float | None:
    out = safe_float(value, np.nan)
    return None if not np.isfinite(out) else float(out)


def _coerce_symbol_scope(symbol: str, blueprint: Mapping[str, Any] | None) -> dict[str, Any]:
    if isinstance(blueprint, Mapping):
        scope = blueprint.get("symbol_scope", {})
        if isinstance(scope, Mapping) and scope:
            return dict(scope)
    clean_symbol = str(symbol or "").strip().upper()
    if not clean_symbol:
        return {}
    return {
        "mode": "single_symbol",
        "symbols": [clean_symbol],
        "candidate_symbol": clean_symbol,
    }


def _resolve_event_side(bundle: Mapping[str, Any], blueprint: Mapping[str, Any] | None) -> str:
    if isinstance(blueprint, Mapping):
        direction = str(blueprint.get("direction", "")).strip().lower()
        if direction in {"long", "short", "both", "conditional"}:
            return direction
    estimate_bps = _finite_or_none(bundle.get("effect_estimates", {}).get("estimate_bps"))
    if estimate_bps is None:
        estimate_bps = _finite_or_none(bundle.get("cost_robustness", {}).get("net_expectancy_bps"))
    if estimate_bps is None:
        return "unknown"
    if estimate_bps > 0:
        return "long"
    if estimate_bps < 0:
        return "short"
    return "unknown"


def _promotion_track(bundle: Mapping[str, Any], promoted_row: Mapping[str, Any]) -> str:
    track = str(bundle.get("promotion_decision", {}).get("promotion_track", "")).strip()
    if track:
        return track
    return str(promoted_row.get("promotion_track", "")).strip()


def _build_required_context(
    *,
    symbol: str,
    timeframe: str,
    bundle: Mapping[str, Any],
) -> dict[str, Any]:
    sample = bundle.get("sample_definition", {})
    split = bundle.get("split_definition", {})
    metadata = bundle.get("metadata", {})
    return {
        "symbol": symbol,
        "event_type": str(bundle.get("event_type", "")).strip(),
        "timeframe": timeframe,
        "split_scheme_id": str(split.get("split_scheme_id", "")).strip(),
        "bar_duration_minutes": int(safe_int(split.get("bar_duration_minutes", 0), 0)),
        "event_is_trade_trigger": bool(metadata.get("event_is_trade_trigger", True)),
        "sample_symbol": str(sample.get("symbol", "")).strip(),
    }


def _build_supportive_context(
    *,
    bundle: Mapping[str, Any],
    promoted_row: Mapping[str, Any],
) -> dict[str, Any]:
    metadata = bundle.get("metadata", {})
    return {
        "canonical_regime": str(promoted_row.get("canonical_regime", "")).strip(),
        "subtype": str(promoted_row.get("subtype", "")).strip(),
        "phase": str(promoted_row.get("phase", "")).strip(),
        "evidence_mode": str(promoted_row.get("evidence_mode", "")).strip(),
        "recommended_bucket": str(promoted_row.get("recommended_bucket", "")).strip(),
        "regime_bucket": str(promoted_row.get("regime_bucket", "")).strip(),
        "routing_profile_id": str(promoted_row.get("routing_profile_id", "")).strip(),
        "promotion_track": _promotion_track(bundle, promoted_row),
        "bridge_certified": bool(metadata.get("bridge_certified", False)),
        "has_realized_oos_path": bool(metadata.get("has_realized_oos_path", False)),
    }


def _build_expected_response(
    *,
    bundle: Mapping[str, Any],
    blueprint: Mapping[str, Any] | None,
    event_side: str,
) -> dict[str, Any]:
    effect = bundle.get("effect_estimates", {})
    cost = bundle.get("cost_robustness", {})
    response = {
        "direction": event_side,
        "estimate_bps": _finite_or_none(effect.get("estimate_bps")),
        "net_expectancy_bps": _finite_or_none(cost.get("net_expectancy_bps")),
    }
    if isinstance(blueprint, Mapping):
        exit_spec = blueprint.get("exit", {})
        if isinstance(exit_spec, Mapping):
            response.update(
                {
                    "time_stop_bars": int(safe_int(exit_spec.get("time_stop_bars", 0), 0)),
                    "stop_type": str(exit_spec.get("stop_type", "")).strip(),
                    "stop_value": _finite_or_none(exit_spec.get("stop_value")),
                    "target_type": str(exit_spec.get("target_type", "")).strip(),
                    "target_value": _finite_or_none(exit_spec.get("target_value")),
                }
            )
    return response


def _build_risk_notes(
    *,
    bundle: Mapping[str, Any],
    blueprint: Mapping[str, Any] | None,
    status: str,
) -> list[str]:
    metadata = bundle.get("metadata", {})
    cost = bundle.get("cost_robustness", {})
    notes: list[str] = []
    if status == "pending_blueprint":
        notes.append("missing_blueprint_invalidation")
    if bool(metadata.get("is_reduced_evidence", False)):
        notes.append("reduced_evidence")
    if not bool(metadata.get("has_realized_oos_path", False)):
        notes.append("limited_realized_oos_path")
    if cost.get("retail_net_expectancy_pass") is False:
        notes.append("retail_net_expectancy_gate_failed")
    if isinstance(blueprint, Mapping):
        direction = str(blueprint.get("direction", "")).strip()
        if direction:
            notes.append(f"direction:{direction}")
    return notes


def _status_for_blueprint(blueprint: Mapping[str, Any] | None) -> str:
    if not isinstance(blueprint, Mapping):
        return "pending_blueprint"
    invalidation = blueprint.get("exit", {})
    if isinstance(invalidation, Mapping):
        invalidation = invalidation.get("invalidation", {})
    if isinstance(invalidation, Mapping) and invalidation:
        return "active"
    return "pending_blueprint"


def _build_thesis(
    *,
    run_id: str,
    bundle: Mapping[str, Any],
    promoted_row: Mapping[str, Any],
    blueprint: Mapping[str, Any] | None,
) -> PromotedThesis | None:
    sample = bundle.get("sample_definition", {})
    split = bundle.get("split_definition", {})
    metadata = bundle.get("metadata", {})
    decision = bundle.get("promotion_decision", {})
    effect = bundle.get("effect_estimates", {})
    uncertainty = bundle.get("uncertainty_estimates", {})
    stability = bundle.get("stability_tests", {})
    cost = bundle.get("cost_robustness", {})

    candidate_id = str(bundle.get("candidate_id", "")).strip()
    symbol = str(sample.get("symbol", "") or promoted_row.get("symbol", "")).strip().upper()
    timeframe = _timeframe_from_minutes(split.get("bar_duration_minutes", 0))
    event_family = str(bundle.get("event_family", "") or bundle.get("event_type", "")).strip()
    sample_size = int(safe_int(sample.get("n_events", 0), 0))
    net_expectancy_bps = _finite_or_none(cost.get("net_expectancy_bps"))
    if not candidate_id or not symbol or not timeframe or not event_family or sample_size <= 0:
        return None
    if net_expectancy_bps is None:
        return None

    status = _status_for_blueprint(blueprint)
    event_side = _resolve_event_side(bundle, blueprint)
    invalidation = {}
    proposal_id = ""
    blueprint_id = ""
    if isinstance(blueprint, Mapping):
        blueprint_id = str(blueprint.get("id", "")).strip()
        exit_spec = blueprint.get("exit", {})
        if isinstance(exit_spec, Mapping):
            invalidation = dict(exit_spec.get("invalidation", {}))
        lineage = blueprint.get("lineage", {})
        if isinstance(lineage, Mapping):
            proposal_id = str(lineage.get("proposal_id", "")).strip()

    track = _promotion_track(bundle, promoted_row)
    return PromotedThesis(
        thesis_id=f"thesis::{run_id}::{candidate_id}",
        status=status,
        symbol_scope=_coerce_symbol_scope(symbol, blueprint),
        timeframe=timeframe,
        event_family=event_family,
        event_side=event_side,
        required_context=_build_required_context(symbol=symbol, timeframe=timeframe, bundle=bundle),
        supportive_context=_build_supportive_context(bundle=bundle, promoted_row=promoted_row),
        expected_response=_build_expected_response(
            bundle=bundle,
            blueprint=blueprint,
            event_side=event_side,
        ),
        invalidation=invalidation,
        risk_notes=_build_risk_notes(bundle=bundle, blueprint=blueprint, status=status),
        evidence=ThesisEvidence(
            sample_size=sample_size,
            validation_samples=int(safe_int(sample.get("validation_samples", 0), 0)),
            test_samples=int(safe_int(sample.get("test_samples", 0), 0)),
            estimate_bps=_finite_or_none(effect.get("estimate_bps")),
            net_expectancy_bps=net_expectancy_bps,
            q_value=_finite_or_none(uncertainty.get("q_value")),
            stability_score=_finite_or_none(stability.get("stability_score")),
            cost_survival_ratio=_finite_or_none(cost.get("cost_survival_ratio")),
            tob_coverage=_finite_or_none(cost.get("tob_coverage")),
            rank_score=_finite_or_none(decision.get("rank_score", promoted_row.get("selection_score"))),
            promotion_track=track,
            policy_version=str(bundle.get("policy_version", "")).strip(),
            bundle_version=str(bundle.get("bundle_version", "")).strip(),
        ),
        lineage=ThesisLineage(
            run_id=run_id,
            candidate_id=candidate_id,
            hypothesis_id=str(metadata.get("hypothesis_id", promoted_row.get("hypothesis_id", ""))).strip(),
            plan_row_id=str(metadata.get("plan_row_id", "")).strip(),
            blueprint_id=blueprint_id,
            proposal_id=proposal_id,
        ),
    )


def build_promoted_theses(
    *,
    run_id: str,
    bundles: Sequence[Mapping[str, Any]],
    promoted_df: pd.DataFrame | None = None,
    blueprints: Sequence[Mapping[str, Any]] | None = None,
) -> list[PromotedThesis]:
    promoted_frame = promoted_df.copy() if promoted_df is not None else pd.DataFrame()
    promoted_rows = _row_by_candidate_id(promoted_frame)
    promoted_ids = {
        str(row.get("candidate_id", "")).strip()
        for row in promoted_frame.to_dict(orient="records")
        if "candidate_id" in promoted_frame.columns
        and "PROMOT" in str(row.get("status", "PROMOTED")).upper()
    }
    blueprint_rows = _blueprint_by_candidate_id(blueprints or [])
    theses: list[PromotedThesis] = []
    for bundle in bundles:
        candidate_id = str(bundle.get("candidate_id", "")).strip()
        decision_status = str(bundle.get("promotion_decision", {}).get("promotion_status", "")).strip().lower()
        if promoted_ids and candidate_id not in promoted_ids and decision_status != "promoted":
            continue
        promoted_row = promoted_rows.get(candidate_id, {})
        thesis = _build_thesis(
            run_id=run_id,
            bundle=bundle,
            promoted_row=promoted_row,
            blueprint=blueprint_rows.get(candidate_id),
        )
        if thesis is not None:
            theses.append(thesis)
    theses.sort(key=lambda item: item.thesis_id)
    return theses


def _write_thesis_payload(
    *,
    run_id: str,
    theses: Sequence[PromotedThesis],
    output_path: Path,
) -> None:
    ensure_dir(output_path.parent)
    payload = {
        "schema_version": "promoted_theses_v1",
        "run_id": run_id,
        "generated_at_utc": _utc_now(),
        "thesis_count": len(theses),
        "active_thesis_count": sum(1 for thesis in theses if thesis.status == "active"),
        "pending_thesis_count": sum(
            1 for thesis in theses if thesis.status == "pending_blueprint"
        ),
        "theses": [thesis.model_dump() for thesis in theses],
    }
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _update_thesis_index(
    *,
    run_id: str,
    output_path: Path,
    index_path: Path,
    theses: Sequence[PromotedThesis],
) -> None:
    ensure_dir(index_path.parent)
    index = _json_load(index_path)
    runs = index.get("runs", {})
    if not isinstance(runs, dict):
        runs = {}
    runs[run_id] = {
        "output_path": str(output_path),
        "thesis_count": len(theses),
        "active_thesis_count": sum(1 for thesis in theses if thesis.status == "active"),
        "pending_thesis_count": sum(
            1 for thesis in theses if thesis.status == "pending_blueprint"
        ),
        "updated_at_utc": _utc_now(),
    }
    payload = {
        "schema_version": "promoted_thesis_index_v1",
        "latest_run_id": run_id,
        "runs": runs,
    }
    index_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def export_promoted_theses_for_run(
    run_id: str,
    *,
    data_root: Path | None = None,
    bundles: Sequence[Mapping[str, Any]] | None = None,
    promoted_df: pd.DataFrame | None = None,
    blueprints: Sequence[Mapping[str, Any]] | None = None,
) -> PromotedThesisExportResult:
    resolved_root = Path(data_root) if data_root is not None else get_data_root()
    effective_bundles = list(bundles) if bundles is not None else _load_evidence_bundles(run_id, resolved_root)
    effective_promoted = (
        promoted_df.copy() if promoted_df is not None else _load_promoted_candidates(run_id, resolved_root)
    )
    effective_blueprints = list(blueprints) if blueprints is not None else _load_blueprints(run_id, resolved_root)
    theses = build_promoted_theses(
        run_id=run_id,
        bundles=effective_bundles,
        promoted_df=effective_promoted,
        blueprints=effective_blueprints,
    )
    output_path = promoted_theses_path(run_id, resolved_root)
    index_path = live_thesis_index_path(resolved_root)
    _write_thesis_payload(run_id=run_id, theses=theses, output_path=output_path)
    _update_thesis_index(
        run_id=run_id,
        output_path=output_path,
        index_path=index_path,
        theses=theses,
    )
    return PromotedThesisExportResult(
        run_id=run_id,
        output_path=output_path,
        index_path=index_path,
        thesis_count=len(theses),
        active_count=sum(1 for thesis in theses if thesis.status == "active"),
        pending_count=sum(1 for thesis in theses if thesis.status == "pending_blueprint"),
    )
