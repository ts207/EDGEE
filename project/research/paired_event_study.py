from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

from project.core.config import get_data_root
from project.research.thesis_evidence_runner import (
    DOCS_DIR,
    FoundingThesisSpec,
    _event_mask_for_kind,
    _load_raw_dataset,
    _negative_control_pass_rate,
    _paired_confirmation_events,
    _payoff_series,
    _policy_specs,
    _session_confounder,
    _stability_score,
    _ttest_greater,
    _vol_regime_confounder,
)

DEFAULT_CANDIDATE_ID = "THESIS_VOL_SHOCK_LIQUIDITY_CONFIRM"
DEFAULT_STUDY_DIRNAME = "paired_event_studies"


@dataclass(frozen=True)
class CohortSample:
    cohort_id: str
    symbol: str
    horizon: int
    timestamps: pd.Series
    values: pd.Series
    realized_vol: pd.Series


@dataclass(frozen=True)
class PairStudySpec:
    pair: FoundingThesisSpec
    trigger: FoundingThesisSpec
    confirm: FoundingThesisSpec
    trigger_kind: str
    confirm_kind: str
    confirmation_window: int
    require_confirmation_after_trigger: bool


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def _label_for_event(event_contract_ids: Sequence[str], fallback: str) -> str:
    base = str(event_contract_ids[0] if event_contract_ids else fallback).strip().lower()
    return f"{base}_only"


def _display_label(label: str) -> str:
    return label.replace("_only", "").replace("_", " ").upper()


def _load_pair_study_spec(candidate_id: str, policy_path: str | Path | None = None) -> PairStudySpec:
    specs = {spec.candidate_id: spec for spec in _policy_specs(policy_path)}
    pair = specs.get(candidate_id)
    if pair is None:
        raise ValueError(f"Unknown paired thesis candidate: {candidate_id}")
    params = pair.params if isinstance(pair.params, Mapping) else {}
    trigger_kind = str(params.get("trigger_kind", "")).strip().lower()
    confirm_kind = str(params.get("confirm_kind", "")).strip().lower()
    if not trigger_kind or not confirm_kind:
        raise ValueError(f"Paired thesis {candidate_id} must declare trigger_kind and confirm_kind")
    trigger = next((spec for spec in specs.values() if spec.detector_kind == trigger_kind), None)
    confirm = next((spec for spec in specs.values() if spec.detector_kind == confirm_kind), None)
    if trigger is None or confirm is None:
        raise ValueError(f"Paired thesis {candidate_id} requires component policy specs for {trigger_kind} and {confirm_kind}")
    return PairStudySpec(
        pair=pair,
        trigger=trigger,
        confirm=confirm,
        trigger_kind=trigger_kind,
        confirm_kind=confirm_kind,
        confirmation_window=int(params.get("confirmation_window_bars", 3) or 3),
        require_confirmation_after_trigger=bool(params.get("require_confirmation_after_trigger", True)),
    )


def _confirm_window_mask(
    trigger_mask: pd.Series,
    confirm_mask: pd.Series,
    *,
    confirmation_window: int,
    require_confirmation_after_trigger: bool,
) -> pd.Series:
    paired_trigger_idx = np.flatnonzero(trigger_mask.to_numpy(dtype=bool))
    confirm_idx = np.flatnonzero(confirm_mask.to_numpy(dtype=bool))
    paired_confirm = pd.Series(False, index=confirm_mask.index, dtype=bool)
    if paired_trigger_idx.size == 0 or confirm_idx.size == 0:
        return paired_confirm
    for idx in confirm_idx:
        if require_confirmation_after_trigger:
            lo, hi = idx - confirmation_window, idx
        else:
            lo, hi = idx - confirmation_window, idx + confirmation_window
        if np.any((paired_trigger_idx >= max(0, lo)) & (paired_trigger_idx <= hi)):
            paired_confirm.iloc[idx] = True
    return paired_confirm


def _cohort_masks(
    bars: pd.DataFrame,
    spec: PairStudySpec,
    *,
    funding: pd.DataFrame | None = None,
    open_interest: pd.DataFrame | None = None,
) -> tuple[dict[str, pd.Series], dict[str, str]]:
    trigger_label = _label_for_event(spec.trigger.event_contract_ids or (spec.trigger.event_type,), spec.trigger.event_type)
    confirm_label = _label_for_event(spec.confirm.event_contract_ids or (spec.confirm.event_type,), spec.confirm.event_type)
    trigger_mask = _event_mask_for_kind(spec.trigger_kind, bars, spec.trigger.params, funding=funding, open_interest=open_interest)
    confirm_mask = _event_mask_for_kind(spec.confirm_kind, bars, spec.confirm.params, funding=funding, open_interest=open_interest)
    pair_mask = _paired_confirmation_events(
        bars,
        spec.pair.params,
        funding=funding,
        open_interest=open_interest,
    )
    paired_confirm_mask = _confirm_window_mask(
        trigger_mask,
        confirm_mask,
        confirmation_window=spec.confirmation_window,
        require_confirmation_after_trigger=spec.require_confirmation_after_trigger,
    )
    return (
        {
            trigger_label: (trigger_mask & ~pair_mask).fillna(False).astype(bool),
            confirm_label: (confirm_mask & ~paired_confirm_mask).fillna(False).astype(bool),
            "joint_trigger": pair_mask.fillna(False).astype(bool),
        },
        {"trigger_label": trigger_label, "confirm_label": confirm_label},
    )


def _cohort_sample(*, cohort_id: str, symbol: str, horizon: int, bars: pd.DataFrame, event_mask: pd.Series) -> CohortSample:
    payoff = _payoff_series(bars, horizon=horizon, payoff_mode="absolute_return")
    values = payoff[event_mask].dropna().astype(float)
    timestamps = bars.loc[event_mask, "timestamp"].loc[values.index].reset_index(drop=True)
    close = pd.to_numeric(bars["close"], errors="coerce")
    realized_vol = np.sqrt(np.log(close / close.shift(1)).pow(2).rolling(12, min_periods=12).mean())
    realized_vol = pd.to_numeric(realized_vol.reindex(values.index), errors="coerce").reset_index(drop=True)
    return CohortSample(
        cohort_id=cohort_id,
        symbol=symbol,
        horizon=int(horizon),
        timestamps=timestamps,
        values=values.reset_index(drop=True),
        realized_vol=realized_vol,
    )


def _regime_slices(sample: CohortSample) -> dict[str, Any]:
    if sample.values.empty:
        return {"available": False}
    aligned_vol = pd.to_numeric(sample.realized_vol, errors="coerce")
    if aligned_vol.dropna().empty:
        return {"available": False}
    median_vol = float(aligned_vol.median())
    high = sample.values[aligned_vol >= median_vol].dropna().astype(float)
    low = sample.values[aligned_vol < median_vol].dropna().astype(float)
    if high.empty or low.empty:
        return {"available": False}
    return {
        "available": True,
        "high_vol": {"n_events": int(len(high)), "mean_bps": float(high.mean())},
        "low_vol": {"n_events": int(len(low)), "mean_bps": float(low.mean())},
        "median_realized_vol": median_vol,
    }


def _summary_from_samples(samples: Sequence[CohortSample]) -> dict[str, Any]:
    values = pd.concat([sample.values for sample in samples], ignore_index=True) if samples else pd.Series(dtype=float)
    timestamps = pd.concat([sample.timestamps for sample in samples], ignore_index=True) if samples else pd.Series(dtype="datetime64[ns, UTC]")
    realized_vol = pd.concat([sample.realized_vol for sample in samples], ignore_index=True) if samples else pd.Series(dtype=float)
    if values.empty or timestamps.empty:
        return {
            "n_events": 0,
            "validation_samples": 0,
            "test_samples": 0,
            "estimate_bps": None,
            "validation_mean_bps": None,
            "test_mean_bps": None,
            "q_value": None,
            "stability_score": 0.0,
            "negative_control_pass_rate": None,
            "session_transition": {"available": False},
            "realized_vol_regime": {"available": False},
            "regime_slices": {"available": False},
            "has_realized_oos_path": False,
        }
    years = timestamps.dt.year
    validation = values[years <= 2021].dropna().astype(float)
    test = values[years >= 2022].dropna().astype(float)
    session_check = _session_confounder(timestamps, values)
    regime_check = _vol_regime_confounder(realized_vol, values)
    negative_control = _negative_control_pass_rate(values.tolist(), values, len(values))
    return {
        "n_events": int(len(values)),
        "validation_samples": int(len(validation)),
        "test_samples": int(len(test)),
        "estimate_bps": float(values.mean()),
        "validation_mean_bps": float(validation.mean()) if not validation.empty else None,
        "test_mean_bps": float(test.mean()) if not test.empty else None,
        "q_value": _ttest_greater(test.tolist()) if not test.empty else None,
        "stability_score": _stability_score(validation.tolist(), test.tolist()) if not validation.empty and not test.empty else 0.0,
        "negative_control_pass_rate": negative_control,
        "session_transition": session_check,
        "realized_vol_regime": regime_check,
        "regime_slices": _regime_slices(
            CohortSample(
                cohort_id=samples[0].cohort_id,
                symbol="AGGREGATE",
                horizon=samples[0].horizon,
                timestamps=timestamps.reset_index(drop=True),
                values=values.reset_index(drop=True),
                realized_vol=realized_vol.reset_index(drop=True),
            )
        ),
        "has_realized_oos_path": bool(len(test) >= 20 and float(test.mean()) > 0.0),
    }


def _pair_advantage(summary: Mapping[str, Any], trigger_label: str, confirm_label: str) -> dict[str, Any]:
    joint = summary.get("joint_trigger", {}) if isinstance(summary.get("joint_trigger", {}), Mapping) else {}
    trigger_payload = summary.get(trigger_label, {}) if isinstance(summary.get(trigger_label, {}), Mapping) else {}
    confirm_payload = summary.get(confirm_label, {}) if isinstance(summary.get(confirm_label, {}), Mapping) else {}
    out = {
        "trigger_label": trigger_label,
        "confirm_label": confirm_label,
        "beats_trigger_only": False,
        "beats_confirmation_only": False,
        "joint_minus_trigger_only_bps": None,
        "joint_minus_confirmation_only_bps": None,
        "joint_validation_advantage_vs_trigger_only_bps": None,
        "joint_validation_advantage_vs_confirmation_only_bps": None,
        "joint_test_advantage_vs_trigger_only_bps": None,
        "joint_test_advantage_vs_confirmation_only_bps": None,
    }
    joint_mean = joint.get("estimate_bps")
    trigger_mean = trigger_payload.get("estimate_bps")
    confirm_mean = confirm_payload.get("estimate_bps")
    if joint_mean is not None and trigger_mean is not None:
        gap = float(joint_mean) - float(trigger_mean)
        out["joint_minus_trigger_only_bps"] = gap
        out["beats_trigger_only"] = gap > 0.0
    if joint_mean is not None and confirm_mean is not None:
        gap = float(joint_mean) - float(confirm_mean)
        out["joint_minus_confirmation_only_bps"] = gap
        out["beats_confirmation_only"] = gap > 0.0
    for prefix, jv, tv, cv in (
        ("joint_validation_advantage", joint.get("validation_mean_bps"), trigger_payload.get("validation_mean_bps"), confirm_payload.get("validation_mean_bps")),
        ("joint_test_advantage", joint.get("test_mean_bps"), trigger_payload.get("test_mean_bps"), confirm_payload.get("test_mean_bps")),
    ):
        if jv is not None and tv is not None:
            out[f"{prefix}_vs_trigger_only_bps"] = float(jv) - float(tv)
        if jv is not None and cv is not None:
            out[f"{prefix}_vs_confirmation_only_bps"] = float(jv) - float(cv)
    # compatibility aliases for existing block-G consumers
    if trigger_label == "vol_shock_only":
        out["beats_vol_shock_only"] = out["beats_trigger_only"]
        out["joint_minus_vol_shock_only_bps"] = out["joint_minus_trigger_only_bps"]
        out["joint_validation_advantage_vs_vol_shock_only_bps"] = out["joint_validation_advantage_vs_trigger_only_bps"]
        out["joint_test_advantage_vs_vol_shock_only_bps"] = out["joint_test_advantage_vs_trigger_only_bps"]
    if confirm_label == "liquidity_vacuum_only":
        out["beats_liquidity_vacuum_only"] = out["beats_confirmation_only"]
        out["joint_minus_liquidity_vacuum_only_bps"] = out["joint_minus_confirmation_only_bps"]
        out["joint_validation_advantage_vs_liquidity_vacuum_only_bps"] = out["joint_validation_advantage_vs_confirmation_only_bps"]
        out["joint_test_advantage_vs_liquidity_vacuum_only_bps"] = out["joint_test_advantage_vs_confirmation_only_bps"]
    return out


def _select_horizon(samples_by_horizon: Mapping[int, Mapping[str, Sequence[CohortSample]]]) -> int:
    best_horizon = next(iter(samples_by_horizon))
    best_score = float("-inf")
    for horizon, cohort_samples in samples_by_horizon.items():
        joint = _summary_from_samples(cohort_samples.get("joint_trigger", []))
        score = float(joint.get("validation_mean_bps") or float("-inf"))
        if score > best_score:
            best_score = score
            best_horizon = int(horizon)
    return int(best_horizon)


def _load_existing_pair_bundles(candidate_id: str, data_root: Path) -> list[dict[str, Any]]:
    path = data_root / "reports" / "promotions" / candidate_id / "evidence_bundles.jsonl"
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        if isinstance(payload, dict):
            rows.append(payload)
    return rows


def _write_pair_bundles(candidate_id: str, data_root: Path, rows: Sequence[Mapping[str, Any]]) -> Path:
    out_path = data_root / "reports" / "promotions" / candidate_id / "evidence_bundles.jsonl"
    _ensure_dir(out_path.parent)
    with out_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(dict(row)) + "\n")
    return out_path


def build_direct_paired_event_study(
    *,
    candidate_id: str = DEFAULT_CANDIDATE_ID,
    policy_path: str | Path | None = None,
    data_root: str | Path | None = None,
    docs_dir: str | Path | None = None,
) -> dict[str, Path]:
    resolved_data_root = Path(data_root) if data_root is not None else Path(get_data_root())
    resolved_docs = _ensure_dir(Path(docs_dir) if docs_dir is not None else DOCS_DIR)
    study_docs_dir = _ensure_dir(resolved_docs / DEFAULT_STUDY_DIRNAME)
    study_report_dir = _ensure_dir(resolved_data_root / "reports" / "promotions" / candidate_id)
    spec = _load_pair_study_spec(candidate_id, policy_path)

    trigger_label = _label_for_event(spec.trigger.event_contract_ids or (spec.trigger.event_type,), spec.trigger.event_type)
    confirm_label = _label_for_event(spec.confirm.event_contract_ids or (spec.confirm.event_type,), spec.confirm.event_type)
    samples_by_horizon: dict[int, dict[str, list[CohortSample]]] = {
        int(horizon): {trigger_label: [], confirm_label: [], "joint_trigger": []}
        for horizon in spec.pair.horizons
    }
    symbol_horizon_summaries: dict[str, dict[int, dict[str, Any]]] = {}

    for symbol in spec.pair.symbols:
        bars = _load_raw_dataset(symbol, "ohlcv_5m", data_root=resolved_data_root)
        if bars.empty:
            continue
        funding = _load_raw_dataset(symbol, "funding", data_root=resolved_data_root)
        open_interest = _load_raw_dataset(symbol, "open_interest", data_root=resolved_data_root)
        masks, _ = _cohort_masks(bars, spec, funding=funding, open_interest=open_interest)
        symbol_horizon_summaries[symbol] = {}
        for horizon in spec.pair.horizons:
            horizon_payload: dict[str, Any] = {}
            for cohort_id, event_mask in masks.items():
                sample = _cohort_sample(cohort_id=cohort_id, symbol=symbol, horizon=int(horizon), bars=bars, event_mask=event_mask)
                samples_by_horizon[int(horizon)][cohort_id].append(sample)
                horizon_payload[cohort_id] = _summary_from_samples([sample])
            horizon_payload["pair_advantage"] = _pair_advantage(horizon_payload, trigger_label, confirm_label)
            symbol_horizon_summaries[symbol][int(horizon)] = horizon_payload

    if not samples_by_horizon:
        raise ValueError(f"No supported horizons found for paired thesis: {candidate_id}")

    selected_horizon = _select_horizon(samples_by_horizon)
    aggregate_horizon_summaries: dict[int, dict[str, Any]] = {}
    for horizon, cohort_samples in samples_by_horizon.items():
        horizon_payload = {cohort_id: _summary_from_samples(samples) for cohort_id, samples in cohort_samples.items()}
        horizon_payload["pair_advantage"] = _pair_advantage(horizon_payload, trigger_label, confirm_label)
        aggregate_horizon_summaries[int(horizon)] = horizon_payload

    selected_summary = aggregate_horizon_summaries[selected_horizon]
    trigger_name = _display_label(trigger_label)
    confirm_name = _display_label(confirm_label)
    payload = {
        "study_id": f"{candidate_id}_direct_pair_event_study",
        "generated_at_utc": _utc_now(),
        "thesis_id": candidate_id,
        "thesis_contract_id": candidate_id,
        "thesis_contract_ids": [candidate_id],
        "event_contract_ids": list(spec.pair.event_contract_ids),
        "symbols": list(spec.pair.symbols),
        "selected_horizon_bars": int(selected_horizon),
        "horizons_tested": [int(horizon) for horizon in spec.pair.horizons],
        "split_definition": {"split_scheme_id": "calendar_year_holdout_2022", "validation_window": "2021", "test_window": "2022"},
        "comparison_design": {
            trigger_label: f"{trigger_name} trigger without the paired {confirm_name} confirmation inside the declared confirmation window.",
            confirm_label: f"{confirm_name} event without the paired {trigger_name} trigger inside the declared confirmation window.",
            "joint_trigger": f"{trigger_name} trigger with nearby {confirm_name} confirmation, anchored at the trigger timestamp.",
        },
        "aggregate_horizon_summaries": aggregate_horizon_summaries,
        "selected_horizon_summary": selected_summary,
        "symbol_horizon_summaries": symbol_horizon_summaries,
        "decision_support": {
            "direct_pair_evidence_present": True,
            "direct_pair_event_study_required_gap_closed": True,
            "pair_beats_trigger_only": bool(selected_summary["pair_advantage"].get("beats_trigger_only", False)),
            "pair_beats_confirmation_only": bool(selected_summary["pair_advantage"].get("beats_confirmation_only", False)),
            "promotion_commentary": (
                f"Direct paired-event evidence now exists for {candidate_id}. "
                f"Use the pair-vs-component comparison for {trigger_name} and {confirm_name} to decide whether the thesis should remain confirmation-scoped or be treated as a stronger paper-grade object."
            ),
        },
    }

    json_path = study_report_dir / "direct_paired_event_study.json"
    md_path = study_docs_dir / f"{candidate_id}.md"
    docs_json_path = study_docs_dir / f"{candidate_id}.json"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    docs_json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        f"# Direct paired-event study — {candidate_id}",
        "",
        f"- thesis_id: `{candidate_id}`",
        f"- selected_horizon_bars: `{selected_horizon}`",
        f"- symbols: `{', '.join(spec.pair.symbols)}`",
        f"- trigger_component: `{trigger_name}`",
        f"- confirm_component: `{confirm_name}`",
        f"- split: `2021 validation / 2022 test`",
        "",
        "## Aggregate selected-horizon comparison",
        "",
        "| Cohort | Events | Validation mean (bps) | Test mean (bps) | Total mean (bps) | Stability | Q-value |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for cohort_id in (trigger_label, confirm_label, "joint_trigger"):
        row = selected_summary.get(cohort_id, {})
        lines.append(
            "| {cohort} | {n} | {val} | {test} | {total} | {stab} | {q} |".format(
                cohort=cohort_id,
                n=row.get("n_events", 0),
                val="" if row.get("validation_mean_bps") is None else f"{float(row['validation_mean_bps']):.2f}",
                test="" if row.get("test_mean_bps") is None else f"{float(row['test_mean_bps']):.2f}",
                total="" if row.get("estimate_bps") is None else f"{float(row['estimate_bps']):.2f}",
                stab=f"{float(row.get('stability_score', 0.0)):.3f}",
                q="" if row.get("q_value") is None else f"{float(row['q_value']):.6f}",
            )
        )
    pair_advantage = selected_summary.get("pair_advantage", {})
    lines.extend([
        "",
        "## Pair advantage diagnostics",
        "",
        f"- joint_minus_trigger_only_bps: `{pair_advantage.get('joint_minus_trigger_only_bps')}`",
        f"- joint_minus_confirmation_only_bps: `{pair_advantage.get('joint_minus_confirmation_only_bps')}`",
        f"- joint_test_advantage_vs_trigger_only_bps: `{pair_advantage.get('joint_test_advantage_vs_trigger_only_bps')}`",
        f"- joint_test_advantage_vs_confirmation_only_bps: `{pair_advantage.get('joint_test_advantage_vs_confirmation_only_bps')}`",
        "",
        "## Interpretation",
        "",
        "This study closes the missing direct paired-event evidence gap for the packaged confirmation thesis.",
        "Use the pair-vs-component comparison to decide whether the thesis should stay confirmation-scoped or be granted broader paper-grade use.",
        "",
    ])
    md_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    bundle_rows = _load_existing_pair_bundles(candidate_id, resolved_data_root)
    if bundle_rows:
        updated_rows: list[dict[str, Any]] = []
        for row in bundle_rows:
            payload_row = dict(row)
            metadata = payload_row.get("metadata", {}) if isinstance(payload_row.get("metadata", {}), Mapping) else {}
            summary = symbol_horizon_summaries.get(str(payload_row.get("symbol", "")).strip().upper(), {}).get(selected_horizon, {})
            cohort_summary = summary.get("joint_trigger", {}) if isinstance(summary.get("joint_trigger", {}), Mapping) else {}
            updated_metadata = {
                **dict(metadata),
                "direct_pair_event_evidence": True,
                "direct_pair_event_study_id": f"{candidate_id}_direct_pair_event_study",
                "direct_pair_event_study_path": str(json_path),
                "direct_pair_event_selected_horizon_bars": int(selected_horizon),
                "direct_pair_event_component_benchmarks": [spec.trigger.candidate_id, spec.confirm.candidate_id],
                "paired_vs_components": summary.get("pair_advantage", {}),
                "pair_selected_summary": cohort_summary,
            }
            payload_row["metadata"] = updated_metadata
            updated_rows.append(payload_row)
        _write_pair_bundles(candidate_id, resolved_data_root, updated_rows)

    return {"report_json": json_path, "report_md": md_path, "report_docs_json": docs_json_path}


__all__ = ["DEFAULT_CANDIDATE_ID", "build_direct_paired_event_study"]
