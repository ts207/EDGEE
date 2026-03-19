from __future__ import annotations
from project.core.config import get_data_root

from project.core.coercion import safe_float, safe_int, as_bool

import argparse
import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Sequence

import pandas as pd
import numpy as np
from project import PROJECT_ROOT

from project.core.timeframes import normalize_timeframe
from project.io.utils import ensure_dir, write_parquet
from project.research.services.pathing import bridge_event_out_dir
from project.specs.ontology import ontology_spec_hash
from project.specs.manifest import finalize_manifest, start_manifest
from project.events.phase2 import PHASE2_EVENT_CHAIN as _CANONICAL_PHASE2_EVENT_CHAIN

PHASE2_EVENT_CHAIN = list(_CANONICAL_PHASE2_EVENT_CHAIN)



from project.pipelines.research.export_edge_candidates_support import (
    _is_missing_value,
    _quiet_float,
    _quiet_int,
    _normalize_direction_value,
    _parse_symbols_csv,
    _infer_symbol_tag,
    _candidate_type_from_action,
    _is_confirmatory_run_mode,
    _load_latest_adjacent_survivorship_index,
    _apply_adjacent_survivorship_annotations,
    _normalize_edge_candidates_df,
    _phase2_row_to_candidate,
    _build_symbol_eval_lookup,
    _build_bridge_eval_lookup,
)

def _run_research_chain(
    run_id: str,
    symbols: str,
) -> None:
    phase2_script_path = PROJECT_ROOT / "pipelines" / "research" / "phase2_candidate_discovery.py"
    registry_script_path = PROJECT_ROOT / "pipelines" / "research" / "build_event_registry.py"
    bridge_script_path = PROJECT_ROOT / "pipelines" / "research" / "bridge_evaluate_phase2.py"
    for event_type, script, extra_args in PHASE2_EVENT_CHAIN:
        script_path = PROJECT_ROOT / "pipelines" / "research" / script
        if not script_path.exists():
            logging.warning("Missing phase1 script (skipping): %s", script_path)
            continue

        cmd = [
            sys.executable,
            str(script_path),
            "--run_id",
            run_id,
            "--symbols",
            symbols,
            *extra_args,
        ]
        result = subprocess.run(cmd)
        if result.returncode != 0:
            logging.warning("Phase1 stage failed (non-blocking): %s", script)
            continue

        if not phase2_script_path.exists():
            logging.warning("Missing phase2 script (skipping): %s", phase2_script_path)
            continue
        if registry_script_path.exists():
            registry_cmd = [
                sys.executable,
                str(registry_script_path),
                "--run_id",
                run_id,
                "--symbols",
                symbols,
                "--event_type",
                event_type,
                "--timeframe",
                "5m",
            ]
            registry_result = subprocess.run(registry_cmd)
            if registry_result.returncode != 0:
                logging.warning("Event registry stage failed (non-blocking): %s", event_type)
                continue
        else:
            logging.warning("Missing event-registry script (skipping): %s", registry_script_path)
            continue

        phase2_cmd = [
            sys.executable,
            str(phase2_script_path),
            "--run_id",
            run_id,
            "--event_type",
            event_type,
            "--symbols",
            symbols,
            "--mode",
            "research",
        ]
        phase2_result = subprocess.run(phase2_cmd)
        if phase2_result.returncode != 0:
            logging.warning("Phase2 stage failed (non-blocking): %s", event_type)
            continue
        if bridge_script_path.exists():
            bridge_cmd = [
                sys.executable,
                str(bridge_script_path),
                "--run_id",
                run_id,
                "--event_type",
                event_type,
                "--symbols",
                symbols,
            ]
            bridge_result = subprocess.run(bridge_cmd)
            if bridge_result.returncode != 0:
                logging.warning("Bridge stage failed (non-blocking): %s", event_type)


def _collect_phase2_candidates(run_id: str, run_symbols: Sequence[str]) -> List[Dict[str, object]]:
    DATA_ROOT = get_data_root()
    rows: List[Dict[str, object]] = []
    phase2_root = DATA_ROOT / "reports" / "phase2" / run_id
    if not phase2_root.exists():
        return rows

    for event_dir in sorted([p for p in phase2_root.iterdir() if p.is_dir()]):
        candidate_root = event_dir
        if (
            not (candidate_root / "phase2_candidates.csv").exists()
            and not (candidate_root / "phase2_candidates.parquet").exists()
        ):
            timeframe_roots = [
                child
                for child in sorted(event_dir.iterdir())
                if child.is_dir()
                and (
                    (child / "phase2_candidates.csv").exists()
                    or (child / "phase2_candidates.parquet").exists()
                )
            ]
        else:
            timeframe_roots = [candidate_root]
        for candidate_root in timeframe_roots:
            promoted_json = candidate_root / "promoted_candidates.json"
            candidate_csv = candidate_root / "phase2_candidates.csv"
            candidate_parquet = candidate_root / "phase2_candidates.parquet"
            symbol_eval_lookup = _build_symbol_eval_lookup(candidate_root)
            timeframe = normalize_timeframe(
                candidate_root.name if candidate_root != event_dir else "5m"
            )
            bridge_eval_lookup = _build_bridge_eval_lookup(
                run_id=run_id,
                event_type=event_dir.name,
                timeframe=timeframe,
            )
            event_rows: List[Dict[str, object]] = []
            phase2_lookup: Dict[str, Dict[str, object]] = {}
            if candidate_csv.exists() or candidate_parquet.exists():
                try:
                    phase2_df = (
                        pd.read_csv(candidate_csv)
                        if candidate_csv.exists()
                        else pd.read_parquet(candidate_parquet)
                    )
                except Exception:
                    phase2_df = pd.DataFrame()
                if not phase2_df.empty:
                    for idx, payload in enumerate(phase2_df.to_dict(orient="records")):
                        cid = str(payload.get("candidate_id", "")).strip()
                        if not cid:
                            cond = str(payload.get("condition", "")).strip()
                            act = str(payload.get("action", "")).strip()
                            if cond and act:
                                cid = f"{cond}__{act}"
                                payload["candidate_id"] = cid
                        if cid:
                            phase2_lookup[cid] = payload

            if promoted_json.exists():
                payload = json.loads(promoted_json.read_text(encoding="utf-8"))
                promoted = payload.get("candidates", []) if isinstance(payload, dict) else []
                for idx, candidate in enumerate(promoted):
                    if not isinstance(candidate, dict):
                        continue
                    candidate_row = dict(candidate)
                    cid = str(candidate_row.get("candidate_id", "")).strip()
                    if not cid:
                        cond = str(candidate_row.get("condition", "")).strip()
                        act = str(candidate_row.get("action", "")).strip()
                        if cond and act:
                            cid = f"{cond}__{act}"
                            candidate_row["candidate_id"] = cid
                    if cid and cid in phase2_lookup:
                        merged = dict(phase2_lookup[cid])
                        merged.update(candidate_row)
                        candidate_row = merged
                    if ("gate_bridge_tradable" in candidate_row) and (
                        not as_bool(candidate_row.get("gate_bridge_tradable", False))
                    ):
                        continue
                    if cid and cid in symbol_eval_lookup:
                        candidate_row.update(symbol_eval_lookup[cid])
                    if cid and cid in bridge_eval_lookup:
                        candidate_row.update(bridge_eval_lookup[cid])
                    event_name = (
                        str(
                            candidate_row.get(
                                "event_type", candidate_row.get("event", event_dir.name)
                            )
                        ).strip()
                        or event_dir.name
                    )
                    event_rows.append(
                        _phase2_row_to_candidate(
                            run_id=run_id,
                            event=event_name,
                            row=candidate_row,
                            idx=idx,
                            source_path=promoted_json,
                            default_status="PROMOTED",
                            run_symbols=run_symbols,
                        )
                    )

            if not event_rows and (candidate_csv.exists() or candidate_parquet.exists()):
                df = (
                    pd.read_csv(candidate_csv)
                    if candidate_csv.exists()
                    else pd.read_parquet(candidate_parquet)
                )
                if not df.empty:
                    if "gate_all_research" in df.columns:
                        df = df[df["gate_all_research"].map(as_bool)].copy()
                    elif "gate_all" in df.columns:
                        df = df[df["gate_all"].map(as_bool)].copy()
                    if "gate_bridge_tradable" in df.columns:
                        df = df[df["gate_bridge_tradable"].map(as_bool)].copy()
                    if not df.empty:
                        for idx, row in df.iterrows():
                            row_payload = row.to_dict()
                            row_payload["status"] = (
                                str(row_payload.get("status", "PROMOTED_RESEARCH")).strip()
                                or "PROMOTED_RESEARCH"
                            )
                            cid = str(row_payload.get("candidate_id", "")).strip()
                            if not cid:
                                cond = str(row_payload.get("condition", "")).strip()
                                act = str(row_payload.get("action", "")).strip()
                                if cond and act:
                                    cid = f"{cond}__{act}"
                                    row_payload["candidate_id"] = cid
                            if cid and cid in symbol_eval_lookup:
                                row_payload.update(symbol_eval_lookup[cid])
                            if cid and cid in bridge_eval_lookup:
                                row_payload.update(bridge_eval_lookup[cid])
                            event_name = (
                                str(
                                    row_payload.get(
                                        "event_type", row_payload.get("event", event_dir.name)
                                    )
                                ).strip()
                                or event_dir.name
                            )
                            event_rows.append(
                                _phase2_row_to_candidate(
                                    run_id=run_id,
                                    event=event_name,
                                    row=row_payload,
                                    idx=idx,
                                    source_path=candidate_csv
                                    if candidate_csv.exists()
                                    else candidate_parquet,
                                    default_status="PROMOTED_RESEARCH",
                                    run_symbols=run_symbols,
                                )
                            )

            rows.extend(event_rows)
    return rows


def main() -> int:
    DATA_ROOT = get_data_root()
    parser = argparse.ArgumentParser(description="Expand and normalize edge candidate universe")
    parser.add_argument("--run_id", required=True)
    parser.add_argument(
        "--symbols", required=True, help="Comma-separated discovery symbols for this run"
    )
    parser.add_argument("--execute", type=int, default=0)
    parser.add_argument("--hypothesis_datasets", default="auto", help=argparse.SUPPRESS)
    parser.add_argument("--hypothesis_max_fused", type=int, default=24, help=argparse.SUPPRESS)
    parser.add_argument("--log_path", default=None)
    args = parser.parse_args()

    log_handlers = [logging.StreamHandler(sys.stdout)]
    if args.log_path:
        ensure_dir(Path(args.log_path).parent)
        log_handlers.append(logging.FileHandler(args.log_path))
    logging.basicConfig(
        level=logging.INFO, handlers=log_handlers, format="%(asctime)s %(levelname)s %(message)s"
    )

    run_symbols = _parse_symbols_csv(args.symbols)
    if not run_symbols:
        print("--symbols must include at least one symbol", file=sys.stderr)
        return 1

    params = {
        "run_id": args.run_id,
        "symbols": run_symbols,
        "execute": int(args.execute),
        "hypothesis_datasets": str(args.hypothesis_datasets),
        "hypothesis_max_fused": int(args.hypothesis_max_fused),
    }
    inputs: List[Dict[str, object]] = []
    outputs: List[Dict[str, object]] = []
    manifest = start_manifest("export_edge_candidates", args.run_id, params, inputs, outputs)

    try:
        if int(args.execute):
            _run_research_chain(
                run_id=args.run_id,
                symbols=args.symbols,
            )

        rows = _collect_phase2_candidates(args.run_id, run_symbols=run_symbols)

        # S1/S2: Apply Hierarchical Shrinkage across the collected candidate universe
        from project.research.helpers.shrinkage import _apply_hierarchical_shrinkage
        from project.specs.manifest import load_run_manifest

        run_manifest = load_run_manifest(args.run_id)
        run_mode = str(run_manifest.get("run_mode", "exploratory")).strip().lower()
        is_confirmatory = _is_confirmatory_run_mode(run_mode)
        current_spec_hash = ontology_spec_hash(PROJECT_ROOT.parent)

        candidates_df = pd.DataFrame(rows)
        if not candidates_df.empty:
            # We need standard columns for shrinkage:
            # - canonical_family, canonical_event_type, template_verb, horizon, state_id, symbol
            # These are already in the candidate rows.
            shrunk_df = _apply_hierarchical_shrinkage(
                candidates_df,
                train_only_lambda=True,  # Enforce S1 requirement
                split_col="split_label",
                run_mode=run_mode,
            )
            # Merge back the shrunk columns
            # (Note: _apply_hierarchical_shrinkage returns a full DF, so we just use it)
            df = shrunk_df
        else:
            df = candidates_df

        if not df.empty:
            df["confirmatory_locked"] = bool(is_confirmatory)
            df["frozen_spec_hash"] = current_spec_hash if is_confirmatory else np.nan
            df["run_mode"] = run_mode
        df, adjacent_report_path = _apply_adjacent_survivorship_annotations(df, run_id=args.run_id)

        out_dir = DATA_ROOT / "reports" / "edge_candidates" / args.run_id
        ensure_dir(out_dir)
        out_csv = out_dir / "edge_candidates_normalized.parquet"
        out_json = out_dir / "edge_candidates_normalized.json"
        df = _normalize_edge_candidates_df(
            df,
            run_mode=run_mode,
            is_confirmatory=is_confirmatory,
            current_spec_hash=current_spec_hash,
        )
        write_parquet(df, out_csv)
        out_json.write_text(df.to_json(orient="records", indent=2), encoding="utf-8")

        outputs.append(
            {"path": str(out_csv), "rows": int(len(df)), "start_ts": None, "end_ts": None}
        )
        outputs.append(
            {"path": str(out_json), "rows": int(len(df)), "start_ts": None, "end_ts": None}
        )
        finalize_manifest(
            manifest,
            "success",
            stats={
                "candidate_count": int(len(df)),
                "adjacent_survivorship_report_path": adjacent_report_path,
            },
        )
        return 0
    except Exception as exc:  # pragma: no cover
        logging.exception("Edge candidate export failed")
        finalize_manifest(manifest, "failed", error=str(exc), stats={})
        return 1


if __name__ == "__main__":
    sys.exit(main())
