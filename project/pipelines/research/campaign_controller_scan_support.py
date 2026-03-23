from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import pandas as pd
import yaml
from project.spec_registry.search_space import DEFAULT_EVENT_PRIORITY_WEIGHT as _DEFAULT_QUALITY

_LOG = logging.getLogger(__name__)


def _read_memory_table(*args: Any, **kwargs: Any) -> pd.DataFrame:
    from project.pipelines.research import campaign_controller as _controller

    return _controller.read_memory_table(*args, **kwargs)


def step_scan_frontier(ctrl: Any, mem: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    for trigger_type in ctrl.config.scan_trigger_types:
        result = ctrl._step_scan_for_type(trigger_type, mem)
        if result is not None:
            return result
    _LOG.info("STEP 4 SCAN: all trigger-type tiers exhausted.")
    return None


def step_scan_for_type(
    ctrl: Any, trigger_type: str, mem: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    t = trigger_type.upper()
    if t == "EVENT":
        return ctrl._step_scan_events(mem)
    if t == "STATE":
        return ctrl._step_scan_states(mem)
    if t == "TRANSITION":
        return ctrl._step_scan_transitions(mem)
    if t == "FEATURE_PREDICATE":
        return ctrl._step_scan_feature_predicates(mem)
    if t == "SEQUENCE":
        return ctrl._step_scan_sequences(mem)
    if t == "INTERACTION":
        return ctrl._step_scan_interactions(mem)
    _LOG.warning("STEP 4 SCAN: unknown trigger_type=%s — skipping.", trigger_type)
    return None


def step_scan_events(ctrl: Any, mem: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    events_registry = ctrl.registries.events.get("events", {})
    avoid_events: Set[str] = set(mem.get("avoid_event_types", set()))

    tested_events: Set[str] = set()
    try:
        tested_df = _read_memory_table(ctrl.config.program_id, "tested_regions", data_root=ctrl.data_root)
        if not tested_df.empty and "event_type" in tested_df.columns:
            tested_events = set(tested_df["event_type"].astype(str).unique())
    except Exception:
        _LOG.warning("Failed to read superseded stages from memory", exc_info=True)

    if ctrl.ledger_path.exists():
        try:
            ledger = pd.read_parquet(ctrl.ledger_path)
            if "trigger_payload" in ledger.columns:
                def _eid(payload: object) -> Optional[str]:
                    try:
                        parsed = json.loads(str(payload))
                        value = str(parsed.get("event_id", "")).strip()
                        return value or None
                    except Exception:
                        return None

                tested_events |= set(ledger["trigger_payload"].apply(_eid).dropna().astype(str))
        except Exception:
            _LOG.warning("Failed to extract tested events from campaign ledger; skipping.", exc_info=True)

    family_candidates: Dict[str, List[str]] = {}
    for eid, meta in events_registry.items():
        if not meta.get("enabled", True):
            continue
        if eid in tested_events or eid in avoid_events:
            continue
        family = str(meta.get("family", "UNKNOWN"))
        family_candidates.setdefault(family, []).append(eid)

    if not family_candidates:
        _LOG.info("STEP 4 SCAN [EVENT]: frontier exhausted.")
        return None

    best_family = max(
        family_candidates,
        key=lambda family: max(
            ctrl._quality_weights.get(event_id, _DEFAULT_QUALITY)
            for event_id in family_candidates[family]
        ),
    )
    candidates = sorted(
        family_candidates[best_family],
        key=lambda event_id: ctrl._quality_weights.get(event_id, _DEFAULT_QUALITY),
        reverse=True,
    )
    to_test = candidates[:3]
    _LOG.info(
        "STEP 4 SCAN [EVENT family=%s]: events=%s quality=%s",
        best_family,
        to_test,
        [ctrl._quality_weights.get(event_id, _DEFAULT_QUALITY) for event_id in to_test],
    )
    return ctrl._build_proposal(
        events=to_test,
        templates=["mean_reversion", "continuation"],
        horizons=[12, 24],
        description=f"EVENT scan [{best_family}] — {', '.join(to_test)}",
        promotion_enabled=False,
        date_scope=("2024-01-01", "2024-01-31"),
        trigger_type="EVENT",
        contexts=ctrl._context_for_proposal(),
    )


def step_scan_states(ctrl: Any, mem: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    del mem
    ss_states = ctrl._load_search_space_states()
    if not ss_states:
        return None

    tested_states: Set[str] = set()
    try:
        tested_df = _read_memory_table(ctrl.config.program_id, "tested_regions", data_root=ctrl.data_root)
        if not tested_df.empty and "event_type" in tested_df.columns and "trigger_type" in tested_df.columns:
            state_rows = tested_df[tested_df["trigger_type"].astype(str) == "STATE"]
            if not state_rows.empty:
                tested_states = set(state_rows["event_type"].astype(str).unique())
    except Exception:
        _LOG.warning("Failed to read superseded stages from memory", exc_info=True)

    candidates = [state_id for state_id in ss_states if state_id not in tested_states]
    if not candidates:
        _LOG.info("STEP 4 SCAN [STATE]: frontier exhausted.")
        return None

    to_test = candidates[:4]
    _LOG.info("STEP 4 SCAN [STATE]: states=%s", to_test)
    return ctrl._build_proposal(
        events=[],
        templates=["mean_reversion", "continuation"],
        horizons=[12, 24],
        description=f"STATE scan — {', '.join(to_test)}",
        promotion_enabled=False,
        date_scope=("2024-01-01", "2024-03-31"),
        trigger_type="STATE",
        states=to_test,
        contexts=ctrl._context_for_proposal(),
    )


def step_scan_transitions(ctrl: Any, mem: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    del mem
    ss_transitions = ctrl._load_search_space_transitions()
    if not ss_transitions:
        return None

    tested_keys: Set[str] = set()
    try:
        tested_df = _read_memory_table(ctrl.config.program_id, "tested_regions", data_root=ctrl.data_root)
        if not tested_df.empty and "trigger_type" in tested_df.columns:
            tr_rows = tested_df[tested_df["trigger_type"].astype(str) == "TRANSITION"]
            if not tr_rows.empty and "event_type" in tr_rows.columns:
                tested_keys = set(tr_rows["event_type"].astype(str).unique())
    except Exception:
        _LOG.warning("Failed to read superseded stages from memory", exc_info=True)

    candidates = [
        transition
        for transition in ss_transitions
        if f"{transition['from_state']}→{transition['to_state']}" not in tested_keys
    ]
    if not candidates:
        _LOG.info("STEP 4 SCAN [TRANSITION]: frontier exhausted.")
        return None

    to_test = candidates[:3]
    labels = [f"{transition['from_state']}→{transition['to_state']}" for transition in to_test]
    _LOG.info("STEP 4 SCAN [TRANSITION]: %s", labels)
    return ctrl._build_proposal(
        events=[],
        templates=["mean_reversion", "continuation"],
        horizons=[12, 24],
        description=f"TRANSITION scan — {', '.join(labels)}",
        promotion_enabled=False,
        date_scope=("2024-01-01", "2024-03-31"),
        trigger_type="TRANSITION",
        transitions=to_test,
        contexts=ctrl._context_for_proposal(),
    )


def step_scan_feature_predicates(ctrl: Any, mem: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    del mem
    static_preds = ctrl._load_search_space_predicates()
    mi_preds = ctrl._load_mi_candidate_predicates()

    def _pred_key(pred: Dict[str, Any]) -> str:
        return f"{pred['feature']}|{pred['operator']}|{pred['threshold']}"

    seen_keys: set[str] = set()
    merged: List[Dict[str, Any]] = []
    for pred in static_preds:
        key = _pred_key(pred)
        if key not in seen_keys:
            seen_keys.add(key)
            merged.append(pred)

    for pred in sorted(mi_preds, key=lambda item: float(item.get("mi_score", 0.0)), reverse=True):
        key = _pred_key(pred)
        if key not in seen_keys:
            seen_keys.add(key)
            merged.append(pred)

    if not merged:
        _LOG.info("STEP 4 SCAN [FEATURE_PREDICATE]: no predicates available.")
        return None

    tested_keys: set[str] = set()
    try:
        tested_df = _read_memory_table(ctrl.config.program_id, "tested_regions", data_root=ctrl.data_root)
        if not tested_df.empty and "trigger_type" in tested_df.columns:
            fp_rows = tested_df[tested_df["trigger_type"].astype(str) == "FEATURE_PREDICATE"]
            if not fp_rows.empty and "event_type" in fp_rows.columns:
                tested_keys = set(fp_rows["event_type"].astype(str).unique())
    except Exception:
        _LOG.warning("Failed to read superseded stages from memory", exc_info=True)

    candidates = [pred for pred in merged if _pred_key(pred) not in tested_keys]
    if not candidates:
        _LOG.info("STEP 4 SCAN [FEATURE_PREDICATE]: frontier exhausted.")
        return None

    to_test = candidates[:8]
    mi_count = sum(1 for pred in to_test if pred.get("source") == "mi_scan")
    _LOG.info(
        "STEP 4 SCAN [FEATURE_PREDICATE]: %d predicates (%d static, %d MI-generated)",
        len(to_test),
        len(to_test) - mi_count,
        mi_count,
    )
    return ctrl._build_proposal(
        events=[],
        templates=["mean_reversion", "continuation"],
        horizons=[12, 24],
        description=f"FEATURE_PREDICATE scan — {len(to_test)} predicates ({mi_count} MI)",
        promotion_enabled=False,
        date_scope=("2024-01-01", "2024-03-31"),
        trigger_type="FEATURE_PREDICATE",
        feature_predicates=to_test,
        contexts=ctrl._context_for_proposal(),
    )


def step_scan_sequences(ctrl: Any, mem: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    del mem
    pairs = ctrl._find_weak_signal_event_pairs()
    if not pairs:
        _LOG.info("STEP 4 SCAN [SEQUENCE]: no weak-signal pairs found.")
        return None

    sequences = [list(pair) for pair in pairs[:5]]
    labels = [f"{left}→{right}" for left, right in sequences]
    _LOG.info("STEP 4 SCAN [SEQUENCE]: pairs=%s", labels)
    return ctrl._build_proposal(
        events=[],
        templates=["mean_reversion", "continuation"],
        horizons=[12, 24],
        description=f"SEQUENCE scan — {', '.join(labels)}",
        promotion_enabled=False,
        date_scope=("2024-01-01", "2024-03-31"),
        trigger_type="SEQUENCE",
        sequences={"include": sequences, "max_gaps_bars": [6, 12]},
        contexts=ctrl._context_for_proposal(),
    )


def step_scan_interactions(ctrl: Any, mem: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    del mem
    motifs = ctrl._load_interaction_motifs()
    if not motifs:
        _LOG.info("STEP 4 SCAN [INTERACTION]: no motifs in interaction_registry.yaml.")
        return None

    tested_keys: Set[str] = set()
    try:
        tested_df = _read_memory_table(ctrl.config.program_id, "tested_regions", data_root=ctrl.data_root)
        if not tested_df.empty and "trigger_type" in tested_df.columns:
            int_rows = tested_df[tested_df["trigger_type"].astype(str) == "INTERACTION"]
            if not int_rows.empty and "event_type" in int_rows.columns:
                tested_keys = set(int_rows["event_type"].astype(str).unique())
    except Exception:
        _LOG.warning("Failed to read superseded stages from memory", exc_info=True)

    def _motif_key(motif: Dict[str, Any]) -> str:
        return f"{motif['left']}|{motif['op']}|{motif['right']}"

    candidates = [motif for motif in motifs if _motif_key(motif) not in tested_keys]
    if not candidates:
        _LOG.info("STEP 4 SCAN [INTERACTION]: frontier exhausted.")
        return None

    to_test = candidates[:3]
    labels = [f"{motif['left']} {motif['op']} {motif['right']}" for motif in to_test]
    _LOG.info("STEP 4 SCAN [INTERACTION]: %s", labels)
    interactions = [
        {
            "left": motif["left"],
            "right": motif["right"],
            "op": motif["op"].upper(),
            "lag": int(motif.get("lag", 6)),
        }
        for motif in to_test
    ]
    return ctrl._build_proposal(
        events=[],
        templates=["mean_reversion", "continuation"],
        horizons=[12, 24],
        description=f"INTERACTION scan — {', '.join(labels)}",
        promotion_enabled=False,
        date_scope=("2024-01-01", "2024-03-31"),
        trigger_type="INTERACTION",
        interactions=interactions,
        contexts=ctrl._context_for_proposal(),
    )


def load_interaction_motifs(ctrl: Any) -> List[Dict[str, Any]]:
    try:
        candidates = [
            ctrl._search_space_path.parent / "grammar" / "interaction_registry.yaml",
            Path(__file__).parent.parent.parent.parent / "spec" / "grammar" / "interaction_registry.yaml",
        ]
        path = next((candidate for candidate in candidates if candidate.exists()), None)
        if path is None:
            return []
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        motifs = raw.get("motifs", [])
        return [
            motif
            for motif in motifs
            if isinstance(motif, dict) and "left" in motif and "right" in motif and "op" in motif
        ]
    except Exception:
        _LOG.warning("Failed to load search space component from %s", ctrl._search_space_path, exc_info=True)
        return []


def step_scan_frontier_cross_family(ctrl: Any, mem: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    events_registry = ctrl.registries.events.get("events", {})
    enabled_events = [
        event_id for event_id, meta in events_registry.items() if meta.get("enabled", True)
    ]

    tested_events: Set[str] = set()
    try:
        tested_df = _read_memory_table(ctrl.config.program_id, "tested_regions", data_root=ctrl.data_root)
        if not tested_df.empty and "event_type" in tested_df.columns:
            tested_events = set(tested_df["event_type"].astype(str).unique())
    except Exception:
        _LOG.warning("Failed to read superseded stages from memory", exc_info=True)

    if ctrl.ledger_path.exists():
        try:
            ledger = pd.read_parquet(ctrl.ledger_path)
            if "trigger_payload" in ledger.columns:
                def _eid(payload: object) -> Optional[str]:
                    try:
                        parsed = json.loads(str(payload))
                        value = str(parsed.get("event_id", "")).strip()
                        return value or None
                    except Exception:
                        return None

                tested_events |= set(ledger["trigger_payload"].apply(_eid).dropna().astype(str))
        except Exception:
            _LOG.warning(
                "Failed to extract tested events from campaign ledger (step 4); skipping.",
                exc_info=True,
            )

    avoid_events: Set[str] = mem["avoid_event_types"]
    candidates = [
        event_id for event_id in enabled_events if event_id not in tested_events and event_id not in avoid_events
    ]
    if not candidates:
        _LOG.info("STEP 4 EXPLORE (cross-family): frontier exhausted.")
        return None

    candidates.sort(key=lambda event_id: ctrl._quality_weights.get(event_id, _DEFAULT_QUALITY), reverse=True)
    to_test = candidates[:5]
    families = {str(events_registry.get(event_id, {}).get("family", "?")) for event_id in to_test}
    _LOG.info("STEP 4 EXPLORE (cross-family=%s): events=%s", sorted(families), to_test)
    return ctrl._build_proposal(
        events=to_test,
        templates=["mean_reversion", "continuation"],
        horizons=[12, 24],
        description=f"Cross-family explore — {', '.join(to_test)}",
        promotion_enabled=False,
        date_scope=("2024-01-01", "2024-03-31"),
        trigger_type="EVENT",
        contexts=ctrl._context_for_proposal(),
    )


def load_search_space_states(ctrl: Any) -> List[str]:
    try:
        if not ctrl._search_space_path.exists():
            return []
        raw = yaml.safe_load(ctrl._search_space_path.read_text(encoding="utf-8"))
        return [str(state_id) for state_id in (raw or {}).get("triggers", {}).get("states", [])]
    except Exception:
        _LOG.warning("Failed to load search space component from %s", ctrl._search_space_path, exc_info=True)
        return []


def load_search_space_transitions(ctrl: Any) -> List[Dict[str, str]]:
    try:
        if not ctrl._search_space_path.exists():
            return []
        raw = yaml.safe_load(ctrl._search_space_path.read_text(encoding="utf-8"))
        out = []
        for transition in (raw or {}).get("triggers", {}).get("transitions", []):
            if isinstance(transition, dict) and "from" in transition and "to" in transition:
                out.append({"from_state": str(transition["from"]), "to_state": str(transition["to"])})
        return out
    except Exception:
        _LOG.warning("Failed to load search space component from %s", ctrl._search_space_path, exc_info=True)
        return []


def load_search_space_predicates(ctrl: Any) -> List[Dict[str, Any]]:
    try:
        if not ctrl._search_space_path.exists():
            return []
        raw = yaml.safe_load(ctrl._search_space_path.read_text(encoding="utf-8"))
        preds = (raw or {}).get("triggers", {}).get("feature_predicates", [])
        return [pred for pred in preds if isinstance(pred, dict) and "feature" in pred]
    except Exception:
        _LOG.warning("Failed to load search space component from %s", ctrl._search_space_path, exc_info=True)
        return []


def load_mi_candidate_predicates(ctrl: Any) -> List[Dict[str, Any]]:
    try:
        feature_mi_root = ctrl.data_root / "reports" / "feature_mi"
        if not feature_mi_root.exists():
            return []
        candidates = sorted(
            feature_mi_root.rglob("candidate_predicates.json"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        if not candidates:
            return []
        raw = json.loads(candidates[0].read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            return []
        valid = [
            pred
            for pred in raw
            if isinstance(pred, dict) and all(key in pred for key in ("feature", "operator", "threshold"))
        ]
        valid.sort(key=lambda pred: float(pred.get("mi_score", 0.0)), reverse=True)
        return valid
    except Exception as exc:
        _LOG.debug("_load_mi_candidate_predicates: %s", exc)
        return []


def find_weak_signal_event_pairs(ctrl: Any) -> List[tuple]:
    try:
        tested_df = _read_memory_table(ctrl.config.program_id, "tested_regions", data_root=ctrl.data_root)
    except Exception:
        _LOG.warning("Failed to load search space component from %s", ctrl._search_space_path, exc_info=True)
        return []

    if tested_df.empty:
        return []

    required = {"event_type", "mean_return_bps", "gate_promo_statistical"}
    if not required.issubset(tested_df.columns):
        return []

    candidates = tested_df[
        (pd.to_numeric(tested_df["mean_return_bps"], errors="coerce").fillna(0) > 0)
        & (tested_df["gate_promo_statistical"].astype(str).str.lower().isin(["false", "0", "fail"]))
        & (
            tested_df["trigger_type"].astype(str) == "EVENT"
            if "trigger_type" in tested_df.columns
            else True
        )
    ].copy()
    if candidates.empty or "event_type" not in candidates.columns:
        return []

    agg = (
        candidates.groupby("event_type")["mean_return_bps"]
        .apply(lambda series: pd.to_numeric(series, errors="coerce").mean())
        .sort_values(ascending=False)
    )
    top_events = list(agg.head(6).index)
    pairs = []
    for idx, left in enumerate(top_events):
        for right in top_events[idx + 1:]:
            pairs.append((left, right))
    return pairs[:5]


def templates_for_event(ctrl: Any, event_id: str) -> List[str]:
    events_registry = ctrl.registries.events.get("events", {})
    family = str(events_registry.get(event_id, {}).get("family", "")).strip()
    template_reg = ctrl.registries.templates.get("families", {})
    templates: List[str] = template_reg.get(family, {}).get("allowed_templates", [])
    return templates or ["mean_reversion", "continuation"]


def build_proposal(
    ctrl: Any,
    *,
    events: List[str],
    templates: List[str],
    horizons: List[int],
    description: str,
    promotion_enabled: bool,
    date_scope: tuple[str, str],
    trigger_type: str = "EVENT",
    states: Optional[List[str]] = None,
    transitions: Optional[List[Dict[str, str]]] = None,
    feature_predicates: Optional[List[Dict[str, Any]]] = None,
    sequences: Optional[Dict[str, Any]] = None,
    interactions: Optional[List[Dict[str, Any]]] = None,
    contexts: Optional[Dict[str, List[str]]] = None,
) -> Dict[str, Any]:
    start, end = date_scope
    trigger_space: Dict[str, Any] = {"allowed_trigger_types": [trigger_type]}
    if trigger_type == "EVENT":
        trigger_space["events"] = {"include": events}
    elif trigger_type == "STATE":
        trigger_space["states"] = {"include": states or []}
    elif trigger_type == "TRANSITION":
        trigger_space["transitions"] = {"include": transitions or []}
    elif trigger_type == "FEATURE_PREDICATE":
        trigger_space["feature_predicates"] = {"include": feature_predicates or []}
    elif trigger_type == "SEQUENCE":
        trigger_space["sequences"] = sequences or {"include": [], "max_gaps_bars": [6, 12]}
    elif trigger_type == "INTERACTION":
        trigger_space["interactions"] = {"include": interactions or []}

    return {
        "program_id": ctrl.config.program_id,
        "run_mode": "research",
        "description": description,
        "instrument_scope": {
            "instrument_classes": ["crypto"],
            "symbols": ["BTCUSDT"],
            "timeframe": "5m",
            "start": start,
            "end": end,
        },
        "trigger_space": trigger_space,
        "templates": {"include": templates},
        "evaluation": {
            "horizons_bars": horizons,
            "directions": ["long", "short"],
            "entry_lags": [1, 2],
        },
        "contexts": {"include": contexts or {}},
        "search_control": {
            "max_hypotheses_total": 1000,
            "max_hypotheses_per_template": 500,
            "max_hypotheses_per_event_family": 500,
        },
        "promotion": {"enabled": promotion_enabled},
    }


def context_for_proposal(ctrl: Any) -> Dict[str, List[str]]:
    if not ctrl.config.enable_context_conditioning:
        return {}
    return {"vol_regime": ["low", "high"]}
