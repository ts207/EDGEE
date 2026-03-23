from project.core.config import get_data_root

DATA_ROOT = get_data_root()

import argparse
import hashlib
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
import yaml
import dataclasses

from project import PROJECT_ROOT
from project.artifacts import (
    checklist_path,
    load_json_dict,
    phase2_candidates_path,
    run_manifest_path,
)
from project.compilers import ExecutableStrategySpec
from project.domain.compiled_registry import get_domain_registry

from project.core.coercion import safe_float, safe_int, as_bool
from project.research.utils.decision_safety import (
    finite_ge,
    finite_le,
    bool_gate,
    coerce_numeric_nan,
    nanmedian_or_nan,
    nanmax_or_nan,
)

from project.core.execution_costs import resolve_execution_costs
from project.io.utils import ensure_dir, write_parquet
from project.portfolio import AllocationSpec
from project.specs.objective import (
    assert_low_capital_contract,
    resolve_objective_profile_contract,
)
from project.specs.manifest import finalize_manifest, start_manifest
from project.specs.ontology import (
    load_run_manifest_hashes,
    ontology_spec_hash,
    ontology_spec_paths,
)
from project.research.candidate_schema import ensure_candidate_schema
from project.research.blueprint_compilation import compile_blueprint
from project.research.clustering.pnl_similarity import calculate_similarity_matrix
from project.research.helpers.selection import (
    choose_event_rows as _selection_choose_event_rows,
    passes_fallback_gate as _selection_passes_fallback_gate,
    rank_key as _selection_rank_key,
)
from project.strategy.dsl.schema import Blueprint


def _copy_model(instance: Any, **updates: object) -> Any:
    model_copy = getattr(instance, "model_copy", None)
    if callable(model_copy):
        return model_copy(update=updates)
    return dataclasses.replace(instance, **updates)


def _candidate_id(row: Dict[str, object], idx: int) -> str:
    candidate_id = str(row.get("candidate_id", "")).strip()
    if candidate_id:
        return candidate_id
    event = str(row.get("event", row.get("event_type", "candidate"))).strip() or "candidate"
    return f"{event}_{idx}"


def _load_gates_spec() -> Dict[str, Any]:
    from project.specs.gates import load_gates_spec

    return load_gates_spec(PROJECT_ROOT.parent)


def _rank_key(row: Dict[str, object]) -> Tuple[float, float, float, float, str]:
    return _selection_rank_key(row, safe_float_fn=safe_float, as_bool_fn=as_bool)


def _passes_fallback_gate(row: Dict[str, object], gates: Dict[str, Any]) -> bool:
    return _selection_passes_fallback_gate(
        row,
        gates,
        safe_float_fn=safe_float,
        safe_int_fn=safe_int,
    )


def _as_bool(value: object) -> bool:
    return as_bool(value)


def _safe_float(value: object, default: float = 0.0) -> float:
    return safe_float(value, default)


def _validate_promoted_candidates_frame(df: pd.DataFrame, source_label: str = "") -> None:
    if df.empty:
        return
    if "status" in df.columns:
        non_promoted = df[df["status"].astype(str).str.upper() != "PROMOTED"]
        if not non_promoted.empty:
            raise ValueError(
                f"non-promoted rows found in promoted candidates frame"
                f" (source={source_label}): {len(non_promoted)} row(s)"
            )


def _choose_event_rows(
    run_id: str,
    event_type: str,
    edge_rows: List[Dict[str, object]],
    phase2_df: pd.DataFrame,
    max_per_event: int,
    allow_fallback_blueprints: bool,
    strict_cost_fields: bool,
    min_events: int,
    *,
    mode: str = "both",
) -> Tuple[List[Dict[str, Any]], Dict[str, Any], Any]:
    return _selection_choose_event_rows(
        run_id=run_id,
        event_type=event_type,
        edge_rows=edge_rows,
        phase2_df=phase2_df,
        max_per_event=max_per_event,
        allow_fallback_blueprints=allow_fallback_blueprints,
        strict_cost_fields=strict_cost_fields,
        min_events=min_events,
        min_robustness=0.0,
        require_positive_expectancy=False,
        expected_cost_digest=None,
        naive_validation=None,
        allow_naive_entry_fail=True,
        mode=str(mode).strip().lower() or "both",
        min_tob_coverage=0.0,
        min_net_expectancy_bps=0.0,
        max_fee_plus_slippage_bps=None,
        max_daily_turnover_multiple=None,
        data_root=DATA_ROOT,
        candidate_id_fn=_candidate_id,
        load_gates_spec_fn=_load_gates_spec,
        passes_quality_floor_fn=_passes_quality_floor,
        rank_key_fn=_rank_key,
        passes_fallback_gate_fn=_passes_fallback_gate,
        as_bool_fn=_as_bool,
        safe_float_fn=_safe_float,
    )


def _passes_quality_floor(
    row: Dict[str, Any],
    *,
    strict_cost_fields: bool = False,
    min_events: int = 0,
    min_robustness: float = 0.0,
    require_positive_expectancy: bool = False,
    expected_cost_digest: str | None = None,
    min_tob_coverage: float = 0.0,
    min_net_expectancy_bps: float = 0.0,
    max_fee_plus_slippage_bps: float = 1e9,
    max_daily_turnover_multiple: float = 1e9,
) -> bool:
    n = safe_int(row.get("n_events"), 0)
    if n < min_events:
        return False
    robustness = coerce_numeric_nan(row.get("robustness_score"))
    if min_robustness > 0.0 and not finite_ge(robustness, min_robustness):
        return False
    tob_cov = coerce_numeric_nan(row.get("tob_coverage"))
    if min_tob_coverage > 0.0 and not finite_ge(tob_cov, min_tob_coverage):
        return False
    net_exp = coerce_numeric_nan(
        row.get(
            "bridge_validation_after_cost_bps",
            row.get("after_cost_expectancy_per_trade", 0.0) * 10_000.0,
        )
    )
    if min_net_expectancy_bps > 0.0 and not finite_ge(net_exp, min_net_expectancy_bps):
        return False
    if require_positive_expectancy and not finite_ge(net_exp, 1e-9):
        return False
    turnover = coerce_numeric_nan(row.get("turnover_proxy_mean"))
    turnover_cap = (
        float(max_daily_turnover_multiple)
        if max_daily_turnover_multiple is not None
        else float("inf")
    )
    if np.isfinite(turnover_cap) and not finite_le(turnover, turnover_cap):
        return False
    if expected_cost_digest is not None:
        actual_digest = str(row.get("cost_config_digest", "")).strip()
        if actual_digest and actual_digest != str(expected_cost_digest).strip():
            return False
    if strict_cost_fields:
        cost = coerce_numeric_nan(row.get("bridge_effective_cost_bps_per_trade"))
        cost_cap = (
            float(max_fee_plus_slippage_bps)
            if max_fee_plus_slippage_bps is not None
            else float("inf")
        )
        if np.isfinite(cost_cap) and not finite_le(cost, cost_cap):
            return False
    return True


def _passes_fallback_gate(row: Dict[str, Any], gate_spec: Dict[str, Any]) -> bool:
    t_stat = coerce_numeric_nan(row.get("t_stat"))
    min_t = coerce_numeric_nan(gate_spec.get("min_t_stat"))
    if not np.isfinite(min_t):
        min_t = 0.0

    if not finite_ge(t_stat, min_t):
        return False

    exp_bps = (
        coerce_numeric_nan(
            row.get("after_cost_expectancy_per_trade", row.get("expectancy_bps", 0.0) / 10_000.0)
        )
        * 10_000.0
    )
    min_exp = coerce_numeric_nan(gate_spec.get("min_after_cost_expectancy_bps"))
    if not np.isfinite(min_exp):
        min_exp = 0.0

    if not finite_ge(exp_bps, min_exp):
        return False

    n = safe_int(row.get("n_events"), 0)
    min_n = safe_int(gate_spec.get("min_sample_size"), 0)
    if n < min_n:
        return False
    return True


def _build_strategy_contract(
    *,
    blueprint: Blueprint,
    run_id: str,
    retail_profile: str,
    low_capital_contract: Dict[str, Any],
    effective_max_concurrent_positions: int,
    effective_per_position_notional_cap_usd: float,
    default_fee_tier: str,
    fees_bps_per_side: float,
    slippage_bps_per_fill: float,
) -> ExecutableStrategySpec:
    return _build_executable_strategy_spec(
        blueprint=blueprint,
        run_id=run_id,
        retail_profile=retail_profile,
        low_capital_contract=low_capital_contract,
        effective_max_concurrent_positions=effective_max_concurrent_positions,
        effective_per_position_notional_cap_usd=effective_per_position_notional_cap_usd,
        default_fee_tier=default_fee_tier,
        fees_bps_per_side=fees_bps_per_side,
        slippage_bps_per_fill=slippage_bps_per_fill,
    )


def _build_executable_strategy_spec(
    *,
    blueprint: Blueprint,
    run_id: str,
    retail_profile: str,
    low_capital_contract: Dict[str, Any],
    effective_max_concurrent_positions: int,
    effective_per_position_notional_cap_usd: float,
    default_fee_tier: str,
    fees_bps_per_side: float,
    slippage_bps_per_fill: float,
) -> ExecutableStrategySpec:
    return ExecutableStrategySpec.from_blueprint(
        blueprint=blueprint,
        run_id=run_id,
        retail_profile=retail_profile,
        low_capital_contract=low_capital_contract,
        effective_max_concurrent_positions=effective_max_concurrent_positions,
        effective_per_position_notional_cap_usd=effective_per_position_notional_cap_usd,
        default_fee_tier=default_fee_tier,
        fees_bps_per_side=fees_bps_per_side,
        slippage_bps_per_fill=slippage_bps_per_fill,
    )


def _build_allocation_spec(
    *,
    blueprint: Blueprint,
    run_id: str,
    retail_profile: str,
    low_capital_contract: Dict[str, Any],
    effective_max_concurrent_positions: int,
    effective_per_position_notional_cap_usd: float,
    default_fee_tier: str,
    fees_bps_per_side: float,
    slippage_bps_per_fill: float,
) -> AllocationSpec:
    return AllocationSpec.from_blueprint(
        blueprint=blueprint,
        run_id=run_id,
        retail_profile=retail_profile,
        low_capital_contract=low_capital_contract,
        effective_max_concurrent_positions=effective_max_concurrent_positions,
        effective_per_position_notional_cap_usd=effective_per_position_notional_cap_usd,
        default_fee_tier=default_fee_tier,
        fees_bps_per_side=fees_bps_per_side,
        slippage_bps_per_fill=slippage_bps_per_fill,
    )


def _validate_strategy_contract(
    strategy_spec: ExecutableStrategySpec,
    *,
    low_capital_contract: Dict[str, Any],
    require_low_capital_contract: bool = False,
) -> None:
    if strategy_spec.entry.order_type_assumption != "market":
        raise ValueError("unsupported order_type_assumption in executable strategy spec")
    if strategy_spec.entry.delay_bars != strategy_spec.execution.policy_executor_config.get(
        "entry_delay_bars"
    ):
        raise ValueError("entry delay mismatch between entry and policy_executor_config")
    if require_low_capital_contract and not low_capital_contract:
        raise ValueError("low_capital_contract is required but empty")


def _write_strategy_contract_artifacts(
    *,
    blueprints: List[Blueprint],
    out_dir: Path,
    run_id: str,
    retail_profile: str,
    low_capital_contract: Dict[str, Any],
    require_low_capital_contract: bool,
    effective_max_concurrent_positions: int,
    effective_per_position_notional_cap_usd: float,
    default_fee_tier: str,
    fees_bps_per_side: float,
    slippage_bps_per_fill: float,
) -> Dict[str, Any]:
    executable_dir = out_dir / "executable_strategy_specs"
    allocation_dir = out_dir / "allocation_specs"
    ensure_dir(executable_dir)
    ensure_dir(allocation_dir)

    executable_entries = []
    allocation_entries = []
    executor_lines = []

    for bp in blueprints:
        executable_spec = _build_executable_strategy_spec(
            blueprint=bp,
            run_id=run_id,
            retail_profile=retail_profile,
            low_capital_contract=low_capital_contract,
            effective_max_concurrent_positions=effective_max_concurrent_positions,
            effective_per_position_notional_cap_usd=effective_per_position_notional_cap_usd,
            default_fee_tier=default_fee_tier,
            fees_bps_per_side=fees_bps_per_side,
            slippage_bps_per_fill=slippage_bps_per_fill,
        )
        allocation_spec = _build_allocation_spec(
            blueprint=bp,
            run_id=run_id,
            retail_profile=retail_profile,
            low_capital_contract=low_capital_contract,
            effective_max_concurrent_positions=effective_max_concurrent_positions,
            effective_per_position_notional_cap_usd=effective_per_position_notional_cap_usd,
            default_fee_tier=default_fee_tier,
            fees_bps_per_side=fees_bps_per_side,
            slippage_bps_per_fill=slippage_bps_per_fill,
        )
        try:
            _validate_strategy_contract(
                executable_spec,
                low_capital_contract=low_capital_contract,
                require_low_capital_contract=require_low_capital_contract,
            )
        except ValueError as exc:
            LOGGER.warning("Strategy contract validation failed for %s: %s", bp.id, exc)
        executable_path = executable_dir / f"{bp.id}.executable_strategy_spec.json"
        executable_path.write_text(
            json.dumps(executable_spec.model_dump(), indent=2), encoding="utf-8"
        )
        executable_entries.append(
            {"id": bp.id, "candidate_id": bp.candidate_id, "path": str(executable_path)}
        )
        allocation_path = allocation_dir / f"{bp.id}.allocation_spec.json"
        allocation_path.write_text(
            json.dumps(allocation_spec.model_dump(), indent=2), encoding="utf-8"
        )
        allocation_entries.append(
            {"id": bp.id, "candidate_id": bp.candidate_id, "path": str(allocation_path)}
        )
        executor_lines.append(json.dumps(executable_spec.execution.policy_executor_config))

    executable_index = {"count": len(executable_entries), "entries": executable_entries}
    (out_dir / "executable_strategy_spec_index.json").write_text(
        json.dumps(executable_index, indent=2), encoding="utf-8"
    )
    allocation_index = {"count": len(allocation_entries), "entries": allocation_entries}
    (out_dir / "allocation_spec_index.json").write_text(
        json.dumps(allocation_index, indent=2), encoding="utf-8"
    )
    (out_dir / "policy_executor_configs.jsonl").write_text(
        "\n".join(executor_lines) + ("\n" if executor_lines else ""), encoding="utf-8"
    )

    return {
        "count": len(executable_entries),
        "entries": executable_entries,
        "strategy_contract_count": len(executable_entries),
        "strategy_contract_entries": executable_entries,
        "executable_strategy_spec_count": len(executable_entries),
        "executable_strategy_spec_entries": executable_entries,
        "allocation_spec_count": len(allocation_entries),
        "allocation_spec_entries": allocation_entries,
    }


def _load_run_mode(run_id: str) -> str:
    path = run_manifest_path(run_id, DATA_ROOT)
    payload = load_json_dict(path)
    mode = payload.get("mode") or payload.get("run_mode") or "research"
    return str(mode).strip().lower()


def _enforce_deploy_mode_retail_viability(
    df: pd.DataFrame,
    *,
    source_label: str = "",
    run_mode: str,
    require_retail_viability: bool,
    forbid_fallback_in_deploy_mode: bool,
) -> None:
    deploy_modes = {"production", "certification", "deploy", "promotion"}
    if str(run_mode).strip().lower() not in deploy_modes:
        return
    if forbid_fallback_in_deploy_mode and "promotion_track" in df.columns:
        fallback_rows = df[
            df["promotion_track"].astype(str).str.contains("fallback", case=False, na=False)
        ]
        if not fallback_rows.empty:
            raise ValueError(
                f"fallback policy violated in deploy-mode compile"
                f" (source={source_label}): {len(fallback_rows)} fallback-track row(s)"
            )


def _build_blueprint(
    *,
    row: Dict[str, Any],
    run_id: str,
    run_symbols: List[str],
    phase2_lookup: Dict[str, Any] | None = None,
    stats: Dict[str, Any],
    fees_bps: float = 0.0,
    slippage_bps: float = 0.0,
    min_events: int = 100,
    cost_config_digest: str = "",
    ontology_spec_hash_value: str = "sha256:unknown",
    operator_registry: Dict[str, Dict[str, Any]] | None = None,
    event_type: str | None = None,
) -> Tuple[Blueprint, int]:
    merged_row = dict(row)
    if event_type and not str(merged_row.get("event_type", "")).strip():
        merged_row["event_type"] = event_type
    if event_type and not str(merged_row.get("event", "")).strip():
        merged_row["event"] = event_type
    return compile_blueprint(
        merged_row=merged_row,
        run_id=run_id,
        run_symbols=run_symbols,
        stats=stats,
        fees_bps=float(fees_bps),
        slippage_bps=float(slippage_bps),
        ontology_spec_hash_value=str(ontology_spec_hash_value),
        cost_config_digest=str(cost_config_digest),
        operator_registry=operator_registry,
        min_events=int(min_events),
    )


def _event_stats(
    run_id: str, event_type: str, train_end_date: Optional[pd.Timestamp] = None
) -> Dict[str, Any]:
    """Load simple event-level move statistics for compilation diagnostics."""
    df = _load_phase2_table(run_id, event_type)
    if df.empty:
        return {"adverse": [], "favorable": [], "count": 0}

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        if train_end_date:
            df = df[df["timestamp"] <= train_end_date].copy()

    return {
        "adverse": df["adverse_move"].tolist() if "adverse_move" in df.columns else [],
        "favorable": df["favorable_move"].tolist() if "favorable_move" in df.columns else [],
        "count": len(df),
    }


LOGGER = logging.getLogger(__name__)


def _load_operator_registry() -> Dict[str, Dict[str, Any]]:
    return get_domain_registry().operator_rows()


def _checklist_decision(run_id: str) -> str:
    payload = load_json_dict(checklist_path(run_id, DATA_ROOT))
    if not payload:
        return "missing"
    return str(payload.get("decision", "missing")).strip().upper() or "missing"


def _load_phase2_table(run_id: str, event_type: str) -> pd.DataFrame:
    path = phase2_candidates_path(run_id, event_type, DATA_ROOT)
    if not path.exists():
        return pd.DataFrame()
    if path.suffix == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path)


def _load_external_validation_strategy_metrics(
    run_id: str,
) -> Tuple[Dict[str, Any], str, str]:
    return {}, "", ""


def _annotate_blueprints_with_external_validation_evidence(
    *,
    blueprints: List[Blueprint],
    run_id: str,
    evidence_hash: str,
) -> Tuple[List[Blueprint], Dict[str, Any]]:
    metrics_map, loaded_hash, source = _load_external_validation_strategy_metrics(run_id)
    effective_hash = str(evidence_hash or loaded_hash or "").strip()
    used = bool(metrics_map)
    annotated: List[Blueprint] = []
    for bp in blueprints:
        lineage = _copy_model(
            bp.lineage,
            wf_status="pass",
            wf_evidence_hash=effective_hash,
        )
        annotated.append(_copy_model(bp, lineage=lineage))
    return annotated, {
        "wf_evidence_used": used,
        "wf_evidence_hash": effective_hash,
        "wf_evidence_source": source,
    }


def _symbol_bucket(symbol: str) -> str:
    normalized = str(symbol or "").strip().upper()
    for suffix in ("USDT", "USDC", "BUSD", "USD", "PERP"):
        if normalized.endswith(suffix) and len(normalized) > len(suffix):
            return normalized[: -len(suffix)]
    return normalized or "UNKNOWN"


def _load_portfolio_state(portfolio_state_path: str | None) -> Dict[str, Any]:
    path_text = str(portfolio_state_path or "").strip()
    if not path_text:
        return {}
    path = Path(path_text)
    if not path.exists():
        LOGGER.warning("Portfolio state path does not exist: %s", path)
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        LOGGER.warning("Failed to load portfolio state from %s: %s", path, exc)
        return {}
    if not isinstance(payload, dict):
        return {}

    account = payload.get("account", {}) if isinstance(payload.get("account"), dict) else {}
    wallet_balance = safe_float(
        account.get("wallet_balance", payload.get("portfolio_value", 0.0)),
        0.0,
    )
    margin_balance = safe_float(account.get("margin_balance"), wallet_balance)
    portfolio_value = (
        float(wallet_balance)
        if float(wallet_balance) > 0.0
        else float(margin_balance if margin_balance > 0.0 else 0.0)
    )
    available_balance = safe_float(account.get("available_balance"), portfolio_value)
    positions = account.get("positions", [])
    bucket_exposures: Dict[str, float] = {}
    gross_exposure = 0.0
    if isinstance(positions, list):
        for pos in positions:
            if not isinstance(pos, dict):
                continue
            symbol = str(pos.get("symbol", "")).strip().upper()
            notional = abs(
                safe_float(pos.get("quantity"), 0.0) * safe_float(pos.get("mark_price"), 0.0)
            )
            if notional <= 0.0:
                continue
            gross_exposure += float(notional)
            bucket = _symbol_bucket(symbol)
            bucket_exposures[bucket] = bucket_exposures.get(bucket, 0.0) + float(notional)

    if not bucket_exposures and isinstance(payload.get("bucket_exposures"), dict):
        bucket_exposures = {
            str(key): float(safe_float(value, 0.0))
            for key, value in payload["bucket_exposures"].items()
        }
    gross_exposure = max(
        gross_exposure,
        float(safe_float(payload.get("gross_exposure"), 0.0)),
    )
    available_balance_ratio = (
        float(np.clip(available_balance / portfolio_value, 0.0, 1.0))
        if portfolio_value > 0.0
        else 1.0
    )
    return {
        "source_path": str(path),
        "portfolio_value": float(portfolio_value),
        "available_balance": float(available_balance),
        "available_balance_ratio": float(available_balance_ratio),
        "gross_exposure": float(gross_exposure),
        "bucket_exposures": bucket_exposures,
        "current_vol": float(
            safe_float(payload.get("current_vol", payload.get("realized_vol")), 0.0)
        ),
        "target_vol": float(safe_float(payload.get("target_vol"), 0.0)),
        "max_gross_leverage": float(safe_float(payload.get("max_gross_leverage"), 1.0) or 1.0),
    }


def _parse_pnl_series(value: Any) -> pd.Series:
    payload = value
    if isinstance(payload, str):
        text = payload.strip()
        if not text:
            return pd.Series(dtype=float)
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            return pd.Series(dtype=float)
    if isinstance(payload, pd.Series):
        series = pd.to_numeric(payload, errors="coerce").dropna().reset_index(drop=True)
        return series.astype(float)
    if isinstance(payload, (list, tuple, np.ndarray)):
        series = pd.to_numeric(pd.Series(list(payload)), errors="coerce").dropna().reset_index(drop=True)
        return series.astype(float)
    return pd.Series(dtype=float)


def _calculate_candidate_correlation_by_candidate(
    edge_df: pd.DataFrame,
    *,
    data_root: Path,
    current_run_id: str,
) -> Dict[str, float]:
    if edge_df.empty or "candidate_id" not in edge_df.columns or "pnl_series" not in edge_df.columns:
        return {}

    current_columns: Dict[str, str] = {}
    series_map: Dict[str, pd.Series] = {}
    for row in edge_df.to_dict(orient="records"):
        candidate_id = str(row.get("candidate_id", "")).strip()
        pnl_series = _parse_pnl_series(row.get("pnl_series"))
        if not candidate_id or len(pnl_series) < 3:
            continue
        column_name = f"current::{candidate_id}"
        current_columns[candidate_id] = column_name
        series_map[column_name] = pnl_series

    promotions_root = data_root / "reports" / "promotions"
    if not current_columns or not promotions_root.exists():
        return {}

    for run_dir in sorted(promotions_root.iterdir()):
        if not run_dir.is_dir() or run_dir.name == str(current_run_id):
            continue
        candidate_path = run_dir / "promoted_candidates.parquet"
        if not candidate_path.exists():
            candidate_path = run_dir / "promoted_candidates.csv"
        if not candidate_path.exists():
            continue
        try:
            historical = (
                pd.read_parquet(candidate_path)
                if candidate_path.suffix == ".parquet"
                else pd.read_csv(candidate_path)
            )
        except Exception:
            continue
        if historical.empty or "pnl_series" not in historical.columns:
            continue
        for idx, row in historical.iterrows():
            candidate_id = str(row.get("candidate_id", "")).strip() or f"row_{idx}"
            pnl_series = _parse_pnl_series(row.get("pnl_series"))
            if len(pnl_series) < 3:
                continue
            column_name = f"historical::{run_dir.name}::{candidate_id}"
            series_map[column_name] = pnl_series

    historical_columns = [name for name in series_map if name.startswith("historical::")]
    if not historical_columns:
        return {}

    similarity_matrix = calculate_similarity_matrix(pd.concat(series_map, axis=1))
    correlations: Dict[str, float] = {}
    for candidate_id, column_name in current_columns.items():
        if column_name not in similarity_matrix.index:
            continue
        values = pd.to_numeric(
            similarity_matrix.loc[column_name, historical_columns],
            errors="coerce",
        ).abs()
        max_corr = values.max(skipna=True)
        correlations[candidate_id] = float(max_corr) if np.isfinite(max_corr) else 0.0
    return correlations


def _resolve_portfolio_risk_multiplier(
    blueprint: Blueprint,
    portfolio_state: Dict[str, Any],
) -> tuple[float, str, float, Dict[str, float]]:
    if not portfolio_state:
        return 1.0, _symbol_bucket(blueprint.symbol_scope.candidate_symbol), 0.0, {}

    portfolio_value = float(safe_float(portfolio_state.get("portfolio_value"), 0.0))
    if portfolio_value <= 0.0:
        return 1.0, _symbol_bucket(blueprint.symbol_scope.candidate_symbol), 0.0, {}

    gross_exposure = float(safe_float(portfolio_state.get("gross_exposure"), 0.0))
    max_gross_leverage = max(float(safe_float(portfolio_state.get("max_gross_leverage"), 1.0)), 1.0)
    gross_ratio = gross_exposure / portfolio_value
    gross_multiplier = max(0.25, 1.0 - min(gross_ratio / max_gross_leverage, 1.0))

    available_ratio = float(
        np.clip(safe_float(portfolio_state.get("available_balance_ratio"), 1.0), 0.25, 1.0)
    )

    bucket = _symbol_bucket(blueprint.symbol_scope.candidate_symbol)
    bucket_exposures = portfolio_state.get("bucket_exposures", {})
    bucket_exposure = float(
        safe_float(bucket_exposures.get(bucket), 0.0) if isinstance(bucket_exposures, dict) else 0.0
    )
    bucket_ratio = bucket_exposure / portfolio_value
    bucket_multiplier = max(0.25, 1.0 - min(bucket_ratio, 0.75))

    current_vol = float(safe_float(portfolio_state.get("current_vol"), 0.0))
    target_vol = float(safe_float(portfolio_state.get("target_vol"), 0.0))
    volatility_multiplier = (
        max(0.25, min(1.0, target_vol / current_vol))
        if current_vol > 0.0 and target_vol > 0.0 and current_vol > target_vol
        else 1.0
    )

    components = {
        "gross": float(gross_multiplier),
        "available": float(available_ratio),
        "bucket": float(bucket_multiplier),
        "volatility": float(volatility_multiplier),
    }
    return min(components.values()), bucket, float(bucket_exposure), components


def _apply_phase4_sizing_adjustments(
    blueprints: List[Blueprint],
    *,
    portfolio_state: Dict[str, Any],
    candidate_correlations: Dict[str, float],
) -> List[Blueprint]:
    adjusted: List[Blueprint] = []
    for bp in blueprints:
        max_corr = float(candidate_correlations.get(bp.candidate_id, 0.0))
        correlation_multiplier = (1.0 - max_corr) if max_corr > 0.8 else 1.0
        portfolio_multiplier, bucket, bucket_exposure, components = _resolve_portfolio_risk_multiplier(
            bp,
            portfolio_state,
        )
        total_multiplier = float(np.clip(correlation_multiplier * portfolio_multiplier, 0.0, 1.0))

        sizing_updates = {
            "portfolio_risk_budget": float(bp.sizing.portfolio_risk_budget) * total_multiplier,
            "symbol_risk_budget": float(bp.sizing.symbol_risk_budget) * total_multiplier,
        }
        if bp.sizing.risk_per_trade is not None:
            sizing_updates["risk_per_trade"] = float(bp.sizing.risk_per_trade) * total_multiplier
        if bp.sizing.target_vol is not None:
            sizing_updates["target_vol"] = float(bp.sizing.target_vol) * portfolio_multiplier
        sizing = _copy_model(bp.sizing, **sizing_updates)

        constraints = dict(bp.lineage.constraints)
        constraints.update(
            {
                "portfolio_state_path": str(portfolio_state.get("source_path", "")),
                "portfolio_value_usd": float(safe_float(portfolio_state.get("portfolio_value"), 0.0)),
                "portfolio_gross_exposure_usd": float(
                    safe_float(portfolio_state.get("gross_exposure"), 0.0)
                ),
                "portfolio_current_vol": float(safe_float(portfolio_state.get("current_vol"), 0.0)),
                "portfolio_target_vol": float(safe_float(portfolio_state.get("target_vol"), 0.0)),
                "portfolio_bucket": bucket,
                "portfolio_bucket_exposure_usd": float(bucket_exposure),
                "portfolio_risk_multiplier": float(portfolio_multiplier),
                "portfolio_risk_components": components,
                "max_promoted_pnl_correlation": float(max_corr),
                "correlation_risk_multiplier": float(correlation_multiplier),
            }
        )
        lineage = _copy_model(bp.lineage, constraints=constraints)
        adjusted.append(_copy_model(bp, sizing=sizing, lineage=lineage))
    return adjusted


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile strategy blueprints.")
    parser.add_argument("--run_id", required=True)
    parser.add_argument("--symbols", required=True)
    parser.add_argument("--max_per_event", type=int, default=2)
    parser.add_argument("--fees_bps", type=float, default=None)
    parser.add_argument("--slippage_bps", type=float, default=None)
    parser.add_argument("--ignore_checklist", type=int, default=0)
    parser.add_argument("--retail_profile", default="capital_constrained")
    parser.add_argument("--cost_bps", type=float, default=None)
    parser.add_argument("--candidates_file", default=None)
    parser.add_argument("--out_dir", default=None)
    parser.add_argument("--allow_non_executable_conditions", type=int, default=0)
    parser.add_argument("--allow_naive_entry_fail", type=int, default=0)
    parser.add_argument("--allow_fallback_blueprints", type=int, default=0)
    parser.add_argument("--min_events_floor", type=int, default=20)
    parser.add_argument("--out_path", default=None)
    parser.add_argument("--portfolio_state_path", default=None)

    parser.add_argument("--quality_floor_fallback", type=float, default=0.0)
    args = parser.parse_args()

    out_dir = (
        Path(args.out_dir)
        if args.out_dir
        else DATA_ROOT / "reports" / "strategy_blueprints" / args.run_id
    )
    ensure_dir(out_dir)

    manifest = start_manifest("compile_strategy_blueprints", args.run_id, vars(args), [], [])

    try:
        # 1. Setup and Loading
        contract = resolve_objective_profile_contract(
            project_root=PROJECT_ROOT,
            data_root=DATA_ROOT,
            run_id=args.run_id,
            required=True,
        )
        low_capital_contract = assert_low_capital_contract(
            contract,
            stage_name="compile_strategy_blueprints",
        )
        resolved_costs = resolve_execution_costs(
            project_root=PROJECT_ROOT,
            config_paths=None,
            fees_bps=args.fees_bps,
            slippage_bps=args.slippage_bps,
            cost_bps=args.cost_bps,
        )
        operator_registry = _load_operator_registry()
        ontology_hash = ontology_spec_hash(PROJECT_ROOT.parent)
        retail_profile = str(
            getattr(contract, "retail_profile_name", args.retail_profile) or args.retail_profile
        )
        require_low_capital_contract = bool(
            getattr(contract, "require_low_capital_contract", False)
        )
        effective_max_concurrent_positions = int(
            safe_int(getattr(contract, "max_concurrent_positions", None), 1)
        )
        effective_per_position_notional_cap_usd = float(
            safe_float(getattr(contract, "effective_per_position_notional_cap_usd", None), 0.0)
        )
        if effective_per_position_notional_cap_usd <= 0.0:
            effective_per_position_notional_cap_usd = float(
                safe_float(low_capital_contract.get("max_position_notional_usd"), 0.0)
            )
        default_fee_tier = str(low_capital_contract.get("fee_tier", "taker") or "taker")

        # 2. Checklist Gate
        if not args.ignore_checklist:
            if _checklist_decision(args.run_id) != "PROMOTE":
                LOGGER.info("Checklist decision is not PROMOTE. Skipping compilation.")
                finalize_manifest(manifest, "success", stats={"blueprint_count": 0})
                return 0

        # 3. Load Promoted Candidates
        if args.candidates_file:
            promoted_path = Path(args.candidates_file)
        else:
            promoted_path = (
                DATA_ROOT / "reports" / "promotions" / args.run_id / "promoted_candidates.parquet"
            )
            if not promoted_path.exists():
                promoted_path = promoted_path.with_suffix(".csv")
        if not promoted_path.exists():
            raise FileNotFoundError(f"Missing promoted candidates: {promoted_path}")

        edge_df = (
            pd.read_parquet(promoted_path)
            if promoted_path.suffix == ".parquet"
            else pd.read_csv(promoted_path)
        )
        edge_df = ensure_candidate_schema(edge_df)
        _validate_promoted_candidates_frame(edge_df, source_label=str(promoted_path))

        # 3b. Deploy-mode retail viability gate
        run_mode = _load_run_mode(args.run_id)
        if run_mode in {"production", "certification", "deploy", "promotion"}:
            retail_gate_col = "gate_promo_retail_viability"
            if retail_gate_col in edge_df.columns:
                failing = edge_df[~edge_df[retail_gate_col].map(as_bool)]
                if not failing.empty:
                    message = f"Deploy-mode retail hard gate violated: {len(failing)} candidate(s) failed {retail_gate_col}"
                    logging.error(message)
                    print(message, file=sys.stderr)
                    finalize_manifest(manifest, "failed", error="deploy-mode retail gate")
                    return 1

        # 4. Compilation Loop
        blueprints: List[Blueprint] = []
        symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]

        for row in edge_df.to_dict("records"):
            # Call Service
            bp, _ = compile_blueprint(
                merged_row=row,
                run_id=args.run_id,
                run_symbols=symbols,
                stats={},  # Placeholder for detailed stats if needed
                fees_bps=resolved_costs.fee_bps_per_side,
                slippage_bps=resolved_costs.slippage_bps_per_fill,
                ontology_spec_hash_value=ontology_hash,
                cost_config_digest=resolved_costs.config_digest,
                operator_registry=operator_registry,
            )
            blueprints.append(bp)

        portfolio_state = _load_portfolio_state(args.portfolio_state_path)
        candidate_correlations = _calculate_candidate_correlation_by_candidate(
            edge_df,
            data_root=DATA_ROOT,
            current_run_id=args.run_id,
        )
        blueprints = _apply_phase4_sizing_adjustments(
            blueprints,
            portfolio_state=portfolio_state,
            candidate_correlations=candidate_correlations,
        )

        # 5. Write Outputs
        out_jsonl = out_dir / "blueprints.jsonl"
        with out_jsonl.open("w", encoding="utf-8") as f:
            for bp in blueprints:
                f.write(json.dumps(bp.to_dict(), sort_keys=True) + "\n")

        contract_artifacts = _write_strategy_contract_artifacts(
            blueprints=blueprints,
            out_dir=out_dir,
            run_id=args.run_id,
            retail_profile=retail_profile,
            low_capital_contract=low_capital_contract,
            require_low_capital_contract=require_low_capital_contract,
            effective_max_concurrent_positions=effective_max_concurrent_positions,
            effective_per_position_notional_cap_usd=effective_per_position_notional_cap_usd,
            default_fee_tier=default_fee_tier,
            fees_bps_per_side=resolved_costs.fee_bps_per_side,
            slippage_bps_per_fill=resolved_costs.slippage_bps_per_fill,
        )

        finalize_manifest(
            manifest,
            "success",
            stats={
                "blueprint_count": len(blueprints),
                "allocation_spec_count": int(contract_artifacts.get("allocation_spec_count", 0)),
                "max_correlation_haircut_count": int(
                    sum(1 for value in candidate_correlations.values() if value > 0.8)
                ),
                "portfolio_state_applied": bool(portfolio_state),
            },
        )
        return 0
    except Exception as exc:
        logging.exception("Compilation failed")
        finalize_manifest(manifest, "failed", error=str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main())
