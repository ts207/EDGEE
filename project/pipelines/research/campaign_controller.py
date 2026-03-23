"""
Campaign Controller: Orchestrates autonomous research sequences.

Phase 2.1 — Intelligence loop implemented.
Phase 2.2 — Frontier unification and quality-weighted ordering.

_propose_next_request() now reads the memory system on every cycle before
deciding what to run next. The priority order is:

  Step 1 — REPAIR:  pending mechanical failures in next_actions.json must be
                    resolved before any new event is proposed.
  Step 2 — EXPLOIT: if the last reflection recommends exploit_promising_region,
                    construct a confirmatory run from recommended_next_experiment.
  Step 3 — EXPLORE: explore_adjacent entries in next_actions.json generate runs
                    that vary one dimension of a near-miss region.
  Step 4 — SCAN:    advance the untested event frontier, quality-weighted from
                    search_space.yaml annotations, filtered against high-confidence
                    avoid_regions in belief_state.json.

Phase 2.2 changes:
  - The two legacy frontier systems (_update_frontier + a parallel write from
    update_campaign_stats) have been removed. _update_campaign_stats now
    delegates to update_search_intelligence() from search_intelligence.py,
    unifying under the richer implementation that writes candidate_next_moves.
  - Quality weights are sourced from the centralised
    spec_registry.search_space.load_event_priority_weights() loader, which
    parses both [QUALITY: HIGH/MODERATE/LOW] labels AND raw IG float values
    from search_space.yaml comment lines. Raw IG values are added as a
    fractional bonus (× IG_SCALE_FACTOR) enabling within-tier tiebreaking
    without violating tier ordering.
  - _load_event_quality_weights() is retained as a backward-compat shim.
"""

import argparse
import hashlib
import json
import logging
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Set

import pandas as pd
import yaml

from project.core.config import get_data_root
from project.pipelines.research.experiment_engine import build_experiment_plan, RegistryBundle
from project.pipelines.research.search_intelligence import update_search_intelligence
from project.research.knowledge.memory import memory_paths, read_memory_table
from project.spec_registry.search_space import (
    load_event_priority_weights,
    QUALITY_SCORES as _QUALITY_SCORES_MAP,
    DEFAULT_EVENT_PRIORITY_WEIGHT as _DEFAULT_QUALITY,
)
_LOG = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Phase 2.2: Quality weights are now sourced from the centralised
# spec_registry.search_space loader which also parses raw IG values.
#
# _QUALITY_SCORES and _DEFAULT_QUALITY are kept as module-level names so
# that existing test imports continue to work without modification.
# _load_event_quality_weights is retained as a thin shim over the
# centralised implementation.
# ---------------------------------------------------------------------------
_QUALITY_SCORES: Dict[str, float] = _QUALITY_SCORES_MAP


def _load_event_quality_weights(search_space_path: Path) -> Dict[str, float]:
    """Shim → delegates to ``spec_registry.search_space.load_event_priority_weights``.

    Retained for backward compatibility with existing test imports.
    Phase 2.2 canonical implementation lives in
    ``project/spec_registry/search_space.py``.
    """
    return load_event_priority_weights(search_space_path)


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass
class CampaignConfig:
    program_id: str
    max_runs: int = 5
    max_hypotheses_total: int = 5000
    max_consecutive_no_signal: int = 2
    halt_on_empty_share: float = 0.8
    halt_on_unsupported_share: float = 0.5
    # Phase 2.1/2.3: research mode controls proposal strategy
    # "scan"    — quality-weighted frontier (default)
    # "exploit" — only propose from promising_regions in belief_state
    # "explore" — cross-family batches from explore_adjacent queue
    research_mode: Literal["scan", "exploit", "explore"] = "scan"
    # Phase 3.1: trigger types to activate in sequence.
    # ["EVENT"] → after event frontier exhausted → adds STATE → then TRANSITION.
    # ["EVENT", "STATE", "TRANSITION", "FEATURE_PREDICATE"] activates all four on init.
    scan_trigger_types: List[str] = None  # type: ignore[assignment]
    # Phase 3.2: enable vol_regime context conditioning on proposals.
    # False  — unconditional (default, safe for initial event scan).
    # True   — adds vol_regime: [low, high] to every Step 4 proposal, tripling
    #           the regime-conditional hypothesis count per run.
    enable_context_conditioning: bool = False

    # Phase 4.4: optional live portfolio snapshot consumed by downstream
    # blueprint/allocation compilation for portfolio-aware sizing.
    portfolio_state_path: str | None = None
    # Phase 4.1: automatically run feature_mi_scan before the first proposal
    # cycle so the controller always has fresh MI-derived predicate candidates.
    # Set to False to skip (e.g. when features are unavailable or for speed).
    auto_run_mi_scan: bool = False
    # Symbols and timeframe used for the auto MI scan — must match the feature
    # table available for this program.
    mi_scan_symbols: str = "BTCUSDT"
    mi_scan_timeframe: str = "5m"

    def __post_init__(self) -> None:
        # Default to EVENT-only; caller can expand to full trigger sequence
        if self.scan_trigger_types is None:
            self.scan_trigger_types = ["EVENT"]


@dataclass
class CampaignSummary:
    program_id: str
    total_runs: int = 0
    total_generated: int = 0
    total_evaluated: int = 0
    total_empty_sample: int = 0
    total_insufficient_sample: int = 0
    total_unsupported: int = 0
    total_skipped: int = 0
    top_hypotheses: List[Dict[str, Any]] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps(self.__dict__, indent=2)


# ---------------------------------------------------------------------------
# Controller
# ---------------------------------------------------------------------------


class CampaignController:
    def __init__(self, config: CampaignConfig, data_root: Path, registry_root: Path):
        self.config = config
        self.data_root = data_root
        self.registry_root = registry_root
        self.campaign_dir = data_root / "artifacts" / "experiments" / config.program_id
        self.campaign_dir.mkdir(parents=True, exist_ok=True)
        self.ledger_path = self.campaign_dir / "tested_ledger.parquet"
        self.summary_path = self.campaign_dir / "campaign_summary.json"
        self.registries = RegistryBundle(registry_root)

        # Phase 2.2: quality weights now loaded via the centralised
        # spec_registry.search_space loader, which also captures raw IG values
        # from comment annotations as fractional tiebreakers.
        _candidates = [
            Path("spec/search_space.yaml"),
            Path(__file__).parent.parent.parent.parent / "spec" / "search_space.yaml",
        ]
        self._search_space_path: Path = next(
            (p for p in _candidates if p.exists()), Path("spec/search_space.yaml")
        )
        self._quality_weights: Dict[str, float] = load_event_priority_weights(
            self._search_space_path
        )

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run_campaign(self):
        _LOG.info("Starting campaign: %s (mode=%s)", self.config.program_id, self.config.research_mode)

        # Phase 4.1 — Run MI scan once before the first proposal cycle so the
        # controller has fresh data-driven predicate candidates from the start.
        if self.config.auto_run_mi_scan:
            self._run_mi_scan_pre_step()

        for run_idx in range(self.config.max_runs):
            _LOG.info("Iteration %d/%d", run_idx + 1, self.config.max_runs)

            request_dict = self._propose_next_request()
            if not request_dict:
                _LOG.info("No more search frontier. Campaign complete.")
                break

            run_id = (
                f"run_{run_idx + 1}_"
                f"{hashlib.md5(json.dumps(request_dict, sort_keys=True).encode()).hexdigest()[:8]}"
            )
            config_path = self.campaign_dir / f"{run_id}_config.yaml"
            config_path.write_text(yaml.dump(request_dict))

            try:
                build_experiment_plan(
                    config_path, self.registry_root, out_dir=self.campaign_dir / run_id
                )
            except Exception as exc:
                _LOG.error("Failed to build plan for %s: %s", run_id, exc)
                continue

            self._execute_pipeline(config_path, run_id)

            summary = self._update_campaign_stats()
            if self._should_halt(summary):
                _LOG.warning("Halt criteria met. Ending campaign.")
                break

        _LOG.info("Campaign %s finished.", self.config.program_id)

    # ------------------------------------------------------------------
    # Phase 2.1 — Memory-driven proposal (the core change)
    # Phase 2.3 — research_mode routes Step 4 to appropriate scan variant
    # ------------------------------------------------------------------

    def _propose_next_request(self) -> Optional[Dict[str, Any]]:
        """Select the next experiment by reading the memory system first.

        Priority order:
          1. Repair  — resolve open mechanical failures before any new work.
          2. Exploit — confirmatory run when last reflection says to exploit.
          3. Explore — dimension-varying run from the explore_adjacent queue.
          4. Scan    — quality-weighted untested frontier (filtered by avoidance).

        research_mode modifies Step 4 behaviour:
          - "exploit" — never reaches Step 4; returns None when promising_regions empty.
          - "explore" — Step 4 uses cross-family batching (all families at once).
          - "scan"    — Step 4 restricts each batch to the highest-quality untested
                        family, keeping attribution unambiguous (default).
        """
        mem = self._read_memory()

        # ── Step 1: REPAIR ────────────────────────────────────────────────────
        repair_proposal = self._step_repair(mem)
        if repair_proposal is not None:
            return repair_proposal

        # ── Step 2: EXPLOIT ───────────────────────────────────────────────────
        # In exploit mode only propose from promising_regions; otherwise check
        # if the last reflection recommends an exploit run.
        if self.config.research_mode == "exploit":
            exploit_proposal = self._step_exploit_from_promising(mem)
            if exploit_proposal is not None:
                return exploit_proposal
            _LOG.info("Exploit mode: promising_regions exhausted, nothing to propose.")
            return None

        exploit_proposal = self._step_exploit_from_reflection(mem)
        if exploit_proposal is not None:
            return exploit_proposal

        # ── Step 3: EXPLORE ───────────────────────────────────────────────────
        explore_proposal = self._step_explore_adjacent(mem)
        if explore_proposal is not None:
            return explore_proposal

        # ── Step 4: SCAN ──────────────────────────────────────────────────────
        # explore mode: cross-family batches (wider surface, weaker attribution).
        # scan mode (default): single-family batches (narrow attribution first).
        if self.config.research_mode == "explore":
            return self._step_scan_frontier_cross_family(mem)
        return self._step_scan_frontier(mem)

    # ------------------------------------------------------------------
    # Memory reader — loads all relevant artefacts once per cycle
    # ------------------------------------------------------------------

    def _read_memory(self) -> Dict[str, Any]:
        """Read the full memory state for this program into a single dict."""
        paths = memory_paths(self.config.program_id, data_root=self.data_root)

        def _json(path: Path) -> Dict[str, Any]:
            if path.exists():
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                    return payload if isinstance(payload, dict) else {}
                except Exception:
                    return {}
            return {}

        def _parquet(path: Path) -> pd.DataFrame:
            if path.exists():
                try:
                    return pd.read_parquet(path)
                except Exception:
                    return pd.DataFrame()
            return pd.DataFrame()

        belief_state = _json(paths.belief_state)
        next_actions = _json(paths.next_actions)
        reflections = _parquet(paths.reflections)

        # Latest reflection row as a dict (empty dict if none yet)
        latest_reflection: Dict[str, Any] = {}
        if not reflections.empty:
            latest_reflection = reflections.sort_values(
                "created_at", ascending=False
            ).iloc[0].to_dict()

        # Avoid regions from belief_state: list of dicts with region metadata
        avoid_region_keys: Set[str] = {
            str(r.get("region_key", ""))
            for r in belief_state.get("avoid_regions", [])
            if r.get("region_key")
        }
        # Also collect avoided event_types for Step 4 frontier filtering
        avoid_event_types: Set[str] = {
            str(r.get("event_type", ""))
            for r in belief_state.get("avoid_regions", [])
            if r.get("event_type")
        }

        # Phase 2.4 — collect stages whose failures have already been superseded
        # so _step_repair can skip re-queuing them.
        superseded_stages: Set[str] = set()
        try:
            failures_df = read_memory_table(
                self.config.program_id, "failures", data_root=self.data_root
            )
            if not failures_df.empty and "superseded_by_run_id" in failures_df.columns:
                superseded_stages = set(
                    failures_df[
                        failures_df["superseded_by_run_id"].astype(str).str.strip() != ""
                    ]["stage"].astype(str).unique()
                )
        except Exception:
            pass

        return {
            "belief_state": belief_state,
            "next_actions": next_actions,
            "latest_reflection": latest_reflection,
            "avoid_region_keys": avoid_region_keys,
            "avoid_event_types": avoid_event_types,
            "promising_regions": belief_state.get("promising_regions", []),
            "superseded_stages": superseded_stages,
        }

    # ------------------------------------------------------------------
    # Step 1 — Repair
    # ------------------------------------------------------------------

    def _step_repair(self, mem: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """If there are open mechanical failures, propose a targeted diagnostic run.

        A repair run uses a minimal 1-event, 1-template scope so attribution
        is unambiguous. It targets the event family from the latest failed region
        or falls back to a safe known event.

        Phase 2.4: Entries in the repair queue whose stage is already superseded
        (superseded_by_run_id is populated in the failures table) are skipped so
        the controller does not re-propose repairs for stages that have recovered.
        """
        repair_queue: List[Dict[str, Any]] = mem["next_actions"].get("repair", [])
        if not repair_queue:
            return None

        # Phase 2.4 — filter superseded repairs from the queue before acting
        superseded_stages: Set[str] = mem.get("superseded_stages", set())
        open_repairs = [
            r for r in repair_queue
            if str(r.get("proposed_scope", {}).get("stage", "")) not in superseded_stages
        ]
        if not open_repairs:
            _LOG.info("STEP 1 REPAIR: all queued repairs are superseded — skipping.")
            return None

        top_repair = open_repairs[0]
        stage = str(top_repair.get("proposed_scope", {}).get("stage", "unknown"))
        _LOG.info("STEP 1 REPAIR: open failure in stage=%s — proposing diagnostic run", stage)

        # Use the most recent reflection's top_event if available, else a safe default
        try:
            mf = json.loads(mem["latest_reflection"].get("market_findings", "{}") or "{}")
            event_type = str(mf.get("top_event", "")).strip()
        except Exception:
            event_type = ""

        events_registry = self.registries.events.get("events", {})
        enabled = [e for e, m in events_registry.items() if m.get("enabled", True)]
        if not event_type or event_type not in events_registry:
            event_type = enabled[0] if enabled else "ZSCORE_STRETCH"

        return self._build_proposal(
            events=[event_type],
            templates=["mean_reversion"],
            horizons=[12],
            description=f"Repair diagnostic — stage={stage}",
            promotion_enabled=False,
            date_scope=("2024-01-01", "2024-01-07"),
        )

    # ------------------------------------------------------------------
    # Step 2a — Exploit from reflection (scan/explore modes)
    # ------------------------------------------------------------------

    def _step_exploit_from_reflection(self, mem: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """If the latest reflection recommends exploiting a region, do it.

        Constructs a confirmatory run with promotion enabled, broader date scope,
        and all templates valid for the event's family.
        """
        reflection = mem["latest_reflection"]
        action = str(reflection.get("recommended_next_action", "")).strip()
        if action != "exploit_promising_region":
            return None

        try:
            experiment = json.loads(
                str(reflection.get("recommended_next_experiment", "{}") or "{}")
            )
        except Exception:
            return None

        event_type = str(experiment.get("event_type", "")).strip()
        if not event_type:
            return None

        _LOG.info("STEP 2 EXPLOIT (reflection): event=%s", event_type)

        templates = self._templates_for_event(event_type)
        return self._build_proposal(
            events=[event_type],
            templates=templates,
            horizons=[12, 24, 48],
            description=f"Exploit confirmatory — {event_type}",
            promotion_enabled=True,
            date_scope=("2023-10-01", "2024-03-31"),
        )

    # ------------------------------------------------------------------
    # Step 2b — Exploit from promising_regions (exploit mode only)
    # ------------------------------------------------------------------

    def _step_exploit_from_promising(self, mem: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Propose from the top promising region in belief_state.

        Used when research_mode == "exploit".
        """
        for region in mem["promising_regions"]:
            event_type = str(region.get("event_type", "")).strip()
            if not event_type:
                continue
            _LOG.info("STEP 2 EXPLOIT (promising): event=%s", event_type)
            templates = self._templates_for_event(event_type)
            return self._build_proposal(
                events=[event_type],
                templates=templates,
                horizons=[12, 24, 48],
                description=f"Exploit promising region — {event_type}",
                promotion_enabled=True,
                date_scope=("2023-10-01", "2024-03-31"),
            )
        return None

    # ------------------------------------------------------------------
    # Step 3 — Explore adjacent
    # ------------------------------------------------------------------

    def _step_explore_adjacent(self, mem: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Vary one dimension of a near-miss region from the explore_adjacent queue.

        Tries a broader horizon set and an adjacent template to identify
        the dimension that was limiting the prior result.
        """
        explore_queue: List[Dict[str, Any]] = mem["next_actions"].get("explore_adjacent", [])
        if not explore_queue:
            return None

        entry = explore_queue[0]
        try:
            scope = entry.get("proposed_scope", {})
            if isinstance(scope, str):
                scope = json.loads(scope)
        except Exception:
            scope = {}

        event_type = str(scope.get("event_type", "")).strip()
        if not event_type:
            return None

        _LOG.info("STEP 3 EXPLORE ADJACENT: event=%s", event_type)

        # Propagate any context conditioning embedded in the explore scope.
        # Regime-conditional explore entries (from Phase 4.2 regime signal injection)
        # carry a contexts dict so the follow-up run targets the specific regime.
        raw_contexts = scope.get("contexts", {})
        contexts = raw_contexts if isinstance(raw_contexts, dict) else {}
        # Merge with config-level context conditioning (config wins on conflict)
        if self.config.enable_context_conditioning and not contexts:
            contexts = self._context_for_proposal()

        # Use all templates for the family — the adjacent exploration tests template sensitivity
        templates = self._templates_for_event(event_type)
        return self._build_proposal(
            events=[event_type],
            templates=templates,
            horizons=[6, 12, 24, 48],
            description=f"Explore adjacent — {event_type}",
            promotion_enabled=False,
            date_scope=("2024-01-01", "2024-06-30"),
            contexts=contexts,
        )

    # ------------------------------------------------------------------
    # Step 4 — Quality-weighted frontier scan
    # ------------------------------------------------------------------

    def _step_scan_frontier(self, mem: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Advance the untested frontier — sequences through scan_trigger_types.

        Phase 3.1: The controller now works through the trigger-type list in
        order.  EVENT triggers are exhausted first; then STATE, TRANSITION,
        and FEATURE_PREDICATE are activated in turn.  This preserves the
        narrow-attribution discipline from the vision doc — each type is only
        activated after the prior tier is exhausted.

        Phase 3.2: Context conditioning is applied to every Step-4 proposal
        when config.enable_context_conditioning is True.

        Phase 3.3 (single-family constraint within EVENT tier): All events in
        a batch come from the highest-quality untested family.
        """
        for trigger_type in self.config.scan_trigger_types:
            result = self._step_scan_for_type(trigger_type, mem)
            if result is not None:
                return result
        _LOG.info("STEP 4 SCAN: all trigger-type tiers exhausted.")
        return None

    def _step_scan_for_type(
        self, trigger_type: str, mem: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Propose the next batch for a specific trigger type.

        Dispatches to the appropriate per-type scan helper.
        """
        t = trigger_type.upper()
        if t == "EVENT":
            return self._step_scan_events(mem)
        if t == "STATE":
            return self._step_scan_states(mem)
        if t == "TRANSITION":
            return self._step_scan_transitions(mem)
        if t == "FEATURE_PREDICATE":
            return self._step_scan_feature_predicates(mem)
        if t == "SEQUENCE":
            return self._step_scan_sequences(mem)
        if t == "INTERACTION":
            return self._step_scan_interactions(mem)
        _LOG.warning("STEP 4 SCAN: unknown trigger_type=%s — skipping.", trigger_type)
        return None

    # ---- EVENT scan (Phase 3.1 + single-family constraint from Phase 2.3) ----

    def _step_scan_events(self, mem: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Quality-weighted, single-family EVENT frontier scan (scan mode).

        Enforces the single-family constraint from Phase 2.3: all events in
        the batch come from the highest-quality untested family, keeping
        attribution unambiguous.  Returns None when the EVENT frontier is
        exhausted so the caller can move on to the next trigger type.
        """
        events_registry = self.registries.events.get("events", {})

        tested_events: Set[str] = set()
        try:
            tested_df = read_memory_table(
                self.config.program_id, "tested_regions", data_root=self.data_root
            )
            if not tested_df.empty and "event_type" in tested_df.columns:
                tested_events = set(tested_df["event_type"].astype(str).unique())
        except Exception:
            pass

        if self.ledger_path.exists():
            try:
                ledger = pd.read_parquet(self.ledger_path)
                if "trigger_payload" in ledger.columns:
                    def _eid(p: object) -> Optional[str]:
                        try:
                            parsed = json.loads(str(p))
                            v = str(parsed.get("event_id", "")).strip()
                            return v or None
                        except Exception:
                            return None
                    extra = set(
                        ledger["trigger_payload"].apply(_eid).dropna().astype(str)
                    )
                    tested_events |= extra
            except Exception:
                pass

        avoid_events: Set[str] = mem["avoid_event_types"]

        # Build per-family buckets (untested, non-avoided)
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

        def _family_best_weight(fam_events: List[str]) -> float:
            return max(self._quality_weights.get(e, _DEFAULT_QUALITY) for e in fam_events)

        best_family = max(family_candidates, key=lambda f: _family_best_weight(family_candidates[f]))
        candidates = sorted(
            family_candidates[best_family],
            key=lambda e: self._quality_weights.get(e, _DEFAULT_QUALITY),
            reverse=True,
        )
        to_test = candidates[:3]
        _LOG.info(
            "STEP 4 SCAN [EVENT family=%s]: events=%s quality=%s",
            best_family, to_test,
            [self._quality_weights.get(e, _DEFAULT_QUALITY) for e in to_test],
        )
        return self._build_proposal(
            events=to_test,
            templates=["mean_reversion", "continuation"],
            horizons=[12, 24],
            description=f"EVENT scan [{best_family}] — {', '.join(to_test)}",
            promotion_enabled=False,
            date_scope=("2024-01-01", "2024-01-31"),
            trigger_type="EVENT",
            contexts=self._context_for_proposal(),
        )

    # ---- STATE scan (Phase 3.1) ----

    def _step_scan_states(self, mem: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Propose the next batch of STATE triggers from search_space.yaml.

        Phase 3.1: STATE triggers capture carry, persistence, and
        regime-conditional mean reversion.  States from search_space.yaml
        that have not yet been tested are batched up to 4 at a time.
        """
        ss_states = self._load_search_space_states()
        if not ss_states:
            return None

        tested_states: Set[str] = set()
        try:
            tested_df = read_memory_table(
                self.config.program_id, "tested_regions", data_root=self.data_root
            )
            if not tested_df.empty and "event_type" in tested_df.columns:
                # STATE triggers store the state_id in event_type column
                if "trigger_type" in tested_df.columns:
                    state_rows = tested_df[tested_df["trigger_type"].astype(str) == "STATE"]
                else:
                    state_rows = pd.DataFrame()
                if not state_rows.empty:
                    tested_states = set(state_rows["event_type"].astype(str).unique())
        except Exception:
            pass

        candidates = [s for s in ss_states if s not in tested_states]
        if not candidates:
            _LOG.info("STEP 4 SCAN [STATE]: frontier exhausted.")
            return None

        to_test = candidates[:4]
        _LOG.info("STEP 4 SCAN [STATE]: states=%s", to_test)
        return self._build_proposal(
            events=[],
            templates=["mean_reversion", "continuation"],
            horizons=[12, 24],
            description=f"STATE scan — {', '.join(to_test)}",
            promotion_enabled=False,
            date_scope=("2024-01-01", "2024-03-31"),
            trigger_type="STATE",
            states=to_test,
            contexts=self._context_for_proposal(),
        )

    # ---- TRANSITION scan (Phase 3.1) ----

    def _step_scan_transitions(self, mem: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Propose regime-change TRANSITION triggers from search_space.yaml.

        Phase 3.1: TRANSITION triggers fire at the highest dislocation point —
        the exact moment of regime change.  Each transition is a from→to pair.
        """
        ss_transitions = self._load_search_space_transitions()
        if not ss_transitions:
            return None

        tested_keys: Set[str] = set()
        try:
            tested_df = read_memory_table(
                self.config.program_id, "tested_regions", data_root=self.data_root
            )
            if not tested_df.empty and "trigger_type" in tested_df.columns:
                tr_rows = tested_df[tested_df["trigger_type"].astype(str) == "TRANSITION"]
                if not tr_rows.empty and "event_type" in tr_rows.columns:
                    tested_keys = set(tr_rows["event_type"].astype(str).unique())
        except Exception:
            pass

        # Filter transitions not yet tested (key = "from→to")
        candidates = [
            t for t in ss_transitions
            if f"{t['from_state']}→{t['to_state']}" not in tested_keys
        ]
        if not candidates:
            _LOG.info("STEP 4 SCAN [TRANSITION]: frontier exhausted.")
            return None

        to_test = candidates[:3]
        labels = [f"{t['from_state']}→{t['to_state']}" for t in to_test]
        _LOG.info("STEP 4 SCAN [TRANSITION]: %s", labels)
        return self._build_proposal(
            events=[],
            templates=["mean_reversion", "continuation"],
            horizons=[12, 24],
            description=f"TRANSITION scan — {', '.join(labels)}",
            promotion_enabled=False,
            date_scope=("2024-01-01", "2024-03-31"),
            trigger_type="TRANSITION",
            transitions=to_test,
            contexts=self._context_for_proposal(),
        )

    # ---- FEATURE_PREDICATE scan (Phase 3.5) ----

    def _step_scan_feature_predicates(self, mem: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Propose FEATURE_PREDICATE triggers from static + MI-generated candidates.

        Phase 3.5: Static predicates from search_space.yaml are always included.
        Phase 4.1: MI-generated predicates from the most recent feature_mi_scan
        run are merged in, sorted by MI score descending so the highest-signal
        data-driven predicates are proposed first.

        Deduplication is by (feature, operator, threshold) key — if a static
        predicate overlaps with an MI-generated one, it is kept once.
        """
        static_preds = self._load_search_space_predicates()
        mi_preds = self._load_mi_candidate_predicates()

        # Merge: static first (preserves manual curation), MI fills in new ones
        def _pred_key(p: Dict[str, Any]) -> str:
            return f"{p['feature']}|{p['operator']}|{p['threshold']}"

        seen_keys: set[str] = set()
        merged: List[Dict[str, Any]] = []
        for pred in static_preds:
            k = _pred_key(pred)
            if k not in seen_keys:
                seen_keys.add(k)
                merged.append(pred)

        # MI predicates sorted by score descending — best signal first
        mi_sorted = sorted(mi_preds, key=lambda p: float(p.get("mi_score", 0.0)), reverse=True)
        for pred in mi_sorted:
            k = _pred_key(pred)
            if k not in seen_keys:
                seen_keys.add(k)
                merged.append(pred)

        if not merged:
            _LOG.info("STEP 4 SCAN [FEATURE_PREDICATE]: no predicates available.")
            return None

        tested_keys: set[str] = set()
        try:
            tested_df = read_memory_table(
                self.config.program_id, "tested_regions", data_root=self.data_root
            )
            if not tested_df.empty and "trigger_type" in tested_df.columns:
                fp_rows = tested_df[tested_df["trigger_type"].astype(str) == "FEATURE_PREDICATE"]
                if not fp_rows.empty and "event_type" in fp_rows.columns:
                    tested_keys = set(fp_rows["event_type"].astype(str).unique())
        except Exception:
            pass

        candidates = [p for p in merged if _pred_key(p) not in tested_keys]
        if not candidates:
            _LOG.info("STEP 4 SCAN [FEATURE_PREDICATE]: frontier exhausted.")
            return None

        to_test = candidates[:8]
        mi_count = sum(1 for p in to_test if p.get("source") == "mi_scan")
        _LOG.info(
            "STEP 4 SCAN [FEATURE_PREDICATE]: %d predicates (%d static, %d MI-generated)",
            len(to_test), len(to_test) - mi_count, mi_count,
        )
        return self._build_proposal(
            events=[],
            templates=["mean_reversion", "continuation"],
            horizons=[12, 24],
            description=f"FEATURE_PREDICATE scan — {len(to_test)} predicates ({mi_count} MI)",
            promotion_enabled=False,
            date_scope=("2024-01-01", "2024-03-31"),
            trigger_type="FEATURE_PREDICATE",
            feature_predicates=to_test,
            contexts=self._context_for_proposal(),
        )

    # ---- SEQUENCE scan (Phase 3.4) ----

    def _step_scan_sequences(self, mem: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate SEQUENCE triggers seeded from weak-signal event pairs.

        Phase 3.4: After the event scan, reads tested_regions for event pairs
        where mean_return_bps > 0 and t_stat nominally significant (> 1.0)
        but which did not pass promotion gates.  These are candidates for
        temporal co-occurrence alpha — neither event alone is strong enough,
        but the sequence may be.
        """
        pairs = self._find_weak_signal_event_pairs()
        if not pairs:
            _LOG.info("STEP 4 SCAN [SEQUENCE]: no weak-signal pairs found.")
            return None

        sequences = [list(p) for p in pairs[:5]]
        labels = [f"{a}→{b}" for a, b in sequences]
        _LOG.info("STEP 4 SCAN [SEQUENCE]: pairs=%s", labels)
        return self._build_proposal(
            events=[],
            templates=["mean_reversion", "continuation"],
            horizons=[12, 24],
            description=f"SEQUENCE scan — {', '.join(labels)}",
            promotion_enabled=False,
            date_scope=("2024-01-01", "2024-03-31"),
            trigger_type="SEQUENCE",
            sequences={"include": sequences, "max_gaps_bars": [6, 12]},
            contexts=self._context_for_proposal(),
        )

    # ---- INTERACTION scan (sixth trigger type — cross-dimensional motifs) ----

    def _step_scan_interactions(self, mem: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Propose INTERACTION triggers from spec/grammar/interaction_registry.yaml.

        INTERACTION triggers fire when two conditions are simultaneously true
        (op=AND/CONFIRM) or when one fires while another is absent (op=EXCLUDE).
        They capture cross-dimensional alpha that neither constituent alone detects.

        Motifs are loaded from the domain interaction registry and proposed in
        batches of up to 3.  Already-tested interaction keys are filtered out.
        """
        motifs = self._load_interaction_motifs()
        if not motifs:
            _LOG.info("STEP 4 SCAN [INTERACTION]: no motifs in interaction_registry.yaml.")
            return None

        tested_keys: Set[str] = set()
        try:
            tested_df = read_memory_table(
                self.config.program_id, "tested_regions", data_root=self.data_root
            )
            if not tested_df.empty and "trigger_type" in tested_df.columns:
                int_rows = tested_df[tested_df["trigger_type"].astype(str) == "INTERACTION"]
                if not int_rows.empty and "event_type" in int_rows.columns:
                    tested_keys = set(int_rows["event_type"].astype(str).unique())
        except Exception:
            pass

        def _motif_key(m: Dict[str, Any]) -> str:
            return f"{m['left']}|{m['op']}|{m['right']}"

        candidates = [m for m in motifs if _motif_key(m) not in tested_keys]
        if not candidates:
            _LOG.info("STEP 4 SCAN [INTERACTION]: frontier exhausted.")
            return None

        to_test = candidates[:3]
        labels = [f"{m['left']} {m['op']} {m['right']}" for m in to_test]
        _LOG.info("STEP 4 SCAN [INTERACTION]: %s", labels)

        # Build interaction specs for the trigger_space
        interactions = [
            {
                "left": m["left"],
                "right": m["right"],
                "op": m["op"].upper(),
                "lag": int(m.get("lag", 6)),
            }
            for m in to_test
        ]

        return self._build_proposal(
            events=[],
            templates=["mean_reversion", "continuation"],
            horizons=[12, 24],
            description=f"INTERACTION scan — {', '.join(labels)}",
            promotion_enabled=False,
            date_scope=("2024-01-01", "2024-03-31"),
            trigger_type="INTERACTION",
            interactions=interactions,
            contexts=self._context_for_proposal(),
        )

    def _load_interaction_motifs(self) -> List[Dict[str, Any]]:
        """Load interaction motifs from spec/grammar/interaction_registry.yaml."""
        try:
            import yaml as _yaml
            candidates = [
                self._search_space_path.parent / "grammar" / "interaction_registry.yaml",
                Path(__file__).parent.parent.parent.parent / "spec" / "grammar" / "interaction_registry.yaml",
            ]
            path = next((p for p in candidates if p.exists()), None)
            if path is None:
                return []
            raw = _yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            motifs = raw.get("motifs", [])
            return [
                m for m in motifs
                if isinstance(m, dict) and "left" in m and "right" in m and "op" in m
            ]
        except Exception:
            return []

    # ---- Cross-family explore (Phase 2.3, updated for trigger types) ----

    def _step_scan_frontier_cross_family(self, mem: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Advance the EVENT frontier across all families (explore mode).

        Phase 2.3 / Phase 3.1: explore mode removes the single-family
        constraint and selects up to 5 events across all families.  Context
        conditioning is applied when enabled.
        """
        events_registry = self.registries.events.get("events", {})
        enabled_events: List[str] = [
            eid for eid, meta in events_registry.items() if meta.get("enabled", True)
        ]

        tested_events: Set[str] = set()
        try:
            tested_df = read_memory_table(
                self.config.program_id, "tested_regions", data_root=self.data_root
            )
            if not tested_df.empty and "event_type" in tested_df.columns:
                tested_events = set(tested_df["event_type"].astype(str).unique())
        except Exception:
            pass

        if self.ledger_path.exists():
            try:
                ledger = pd.read_parquet(self.ledger_path)
                if "trigger_payload" in ledger.columns:
                    def _eid2(p: object) -> Optional[str]:
                        try:
                            parsed = json.loads(str(p))
                            v = str(parsed.get("event_id", "")).strip()
                            return v or None
                        except Exception:
                            return None
                    extra = set(ledger["trigger_payload"].apply(_eid2).dropna().astype(str))
                    tested_events |= extra
            except Exception:
                pass

        avoid_events: Set[str] = mem["avoid_event_types"]
        candidates = [e for e in enabled_events if e not in tested_events and e not in avoid_events]
        if not candidates:
            _LOG.info("STEP 4 EXPLORE (cross-family): frontier exhausted.")
            return None

        candidates.sort(key=lambda e: self._quality_weights.get(e, _DEFAULT_QUALITY), reverse=True)
        to_test = candidates[:5]
        families = {str(events_registry.get(e, {}).get("family", "?")) for e in to_test}
        _LOG.info("STEP 4 EXPLORE (cross-family=%s): events=%s", sorted(families), to_test)

        return self._build_proposal(
            events=to_test,
            templates=["mean_reversion", "continuation"],
            horizons=[12, 24],
            description=f"Cross-family explore — {', '.join(to_test)}",
            promotion_enabled=False,
            date_scope=("2024-01-01", "2024-03-31"),
            trigger_type="EVENT",
            contexts=self._context_for_proposal(),
        )

    # ---- Search-space YAML helpers (Phase 3.1/3.4/3.5) ----

    def _load_search_space_states(self) -> List[str]:
        """Return state IDs from spec/search_space.yaml triggers.states section."""
        try:
            import yaml as _yaml
            if not self._search_space_path.exists():
                return []
            raw = _yaml.safe_load(self._search_space_path.read_text(encoding="utf-8"))
            return [str(s) for s in (raw or {}).get("triggers", {}).get("states", [])]
        except Exception:
            return []

    def _load_search_space_transitions(self) -> List[Dict[str, str]]:
        """Return transition dicts from spec/search_space.yaml triggers.transitions."""
        try:
            import yaml as _yaml
            if not self._search_space_path.exists():
                return []
            raw = _yaml.safe_load(self._search_space_path.read_text(encoding="utf-8"))
            out = []
            for t in (raw or {}).get("triggers", {}).get("transitions", []):
                if isinstance(t, dict) and "from" in t and "to" in t:
                    out.append({"from_state": str(t["from"]), "to_state": str(t["to"])})
            return out
        except Exception:
            return []

    def _load_search_space_predicates(self) -> List[Dict[str, Any]]:
        """Return feature predicate dicts from spec/search_space.yaml."""
        try:
            import yaml as _yaml
            if not self._search_space_path.exists():
                return []
            raw = _yaml.safe_load(self._search_space_path.read_text(encoding="utf-8"))
            preds = (raw or {}).get("triggers", {}).get("feature_predicates", [])
            return [p for p in preds if isinstance(p, dict) and "feature" in p]
        except Exception:
            return []

    def _load_mi_candidate_predicates(self) -> List[Dict[str, Any]]:
        """Phase 4.1 — Load MI-generated predicate candidates.

        Scans ``data/reports/feature_mi/*/candidate_predicates.json`` for the
        most recently written MI scan artefact and returns its predicate list.
        Returns ``[]`` on any I/O or parse failure so the controller always
        falls back gracefully to the static predicate set.
        """
        try:
            feature_mi_root = self.data_root / "reports" / "feature_mi"
            if not feature_mi_root.exists():
                return []
            # Find all candidate_predicates.json files under any run sub-dir
            candidates = sorted(
                feature_mi_root.rglob("candidate_predicates.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            if not candidates:
                return []
            most_recent = candidates[0]
            raw = json.loads(most_recent.read_text(encoding="utf-8"))
            if not isinstance(raw, list):
                return []
            # Keep only well-formed predicate dicts
            valid = [
                p for p in raw
                if isinstance(p, dict) and all(k in p for k in ("feature", "operator", "threshold"))
            ]
            # Sort by MI score descending — highest-signal first regardless of file order
            valid.sort(key=lambda p: float(p.get("mi_score", 0.0)), reverse=True)
            return valid
        except Exception as exc:
            _LOG.debug("_load_mi_candidate_predicates: %s", exc)
            return []

    def _find_weak_signal_event_pairs(self) -> List[tuple]:
        """Phase 3.4 — find event pairs with weak individual signal for SEQUENCE seeding.

        Returns pairs of (event_a, event_b) where both events have
        mean_return_bps > 0 and t_stat > 1.0 but did not pass promotion gates,
        sorted by combined mean_return_bps descending.
        """
        try:
            tested_df = read_memory_table(
                self.config.program_id, "tested_regions", data_root=self.data_root
            )
        except Exception:
            return []

        if tested_df.empty:
            return []

        required = {"event_type", "mean_return_bps", "gate_promo_statistical"}
        if not required.issubset(tested_df.columns):
            return []

        # Candidates: positive return, nominally significant, but not promoted
        candidates = tested_df[
            (pd.to_numeric(tested_df["mean_return_bps"], errors="coerce").fillna(0) > 0)
            & (tested_df["gate_promo_statistical"].astype(str).str.lower().isin(["false", "0", "fail"]))
            & (tested_df["trigger_type"].astype(str) == "EVENT" if "trigger_type" in tested_df.columns else True)
        ].copy()

        if candidates.empty or "event_type" not in candidates.columns:
            return []

        # Aggregate per event_type — pick events with best avg mean_return_bps
        agg = (
            candidates.groupby("event_type")["mean_return_bps"]
            .apply(lambda s: pd.to_numeric(s, errors="coerce").mean())
            .sort_values(ascending=False)
        )

        top_events = list(agg.head(6).index)  # Up to 6 events → up to 15 pairs
        pairs = []
        for i, a in enumerate(top_events):
            for b in top_events[i + 1:]:
                pairs.append((a, b))

        return pairs[:5]  # Return top 5 pairs

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _templates_for_event(self, event_id: str) -> List[str]:
        """Return allowed templates for an event's canonical family.

        Falls back to ["mean_reversion", "continuation"] if the event or
        its family cannot be resolved from the registry.
        """
        events_registry = self.registries.events.get("events", {})
        family = str(events_registry.get(event_id, {}).get("family", "")).strip()
        template_reg = self.registries.templates.get("families", {})
        templates: List[str] = template_reg.get(family, {}).get("allowed_templates", [])
        if not templates:
            templates = ["mean_reversion", "continuation"]
        return templates

    def _build_proposal(
        self,
        *,
        events: List[str],
        templates: List[str],
        horizons: List[int],
        description: str,
        promotion_enabled: bool,
        date_scope: tuple[str, str],
        # Phase 3.1 — trigger type (default EVENT for backward compat)
        trigger_type: str = "EVENT",
        # Phase 3.1 — non-event trigger payload (states/transitions/predicates)
        states: Optional[List[str]] = None,
        transitions: Optional[List[Dict[str, str]]] = None,
        feature_predicates: Optional[List[Dict[str, Any]]] = None,
        sequences: Optional[Dict[str, Any]] = None,
        interactions: Optional[List[Dict[str, Any]]] = None,
        # Phase 3.2 — context conditioning
        contexts: Optional[Dict[str, List[str]]] = None,
    ) -> Dict[str, Any]:
        """Construct a valid experiment config dict ready for yaml.dump().

        Phase 3.1: trigger_type controls which expansion path runs.
        Phase 3.2: contexts adds regime conditioning to the proposal.
        """
        start, end = date_scope
        trigger_space: Dict[str, Any] = {
            "allowed_trigger_types": [trigger_type],
        }
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
            "program_id": self.config.program_id,
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
            # Phase 3.2: pass through context conditioning if provided
            "contexts": {"include": contexts or {}},
            "search_control": {
                "max_hypotheses_total": 1000,
                "max_hypotheses_per_template": 500,
                "max_hypotheses_per_event_family": 500,
            },
            "promotion": {"enabled": promotion_enabled},
        }

    def _context_for_proposal(self) -> Dict[str, List[str]]:
        """Return context conditioning dict based on config.enable_context_conditioning.

        Phase 3.2: When enabled, returns vol_regime: [low, high] so the
        expansion engine generates regime-conditional hypotheses in a single
        pass.  Extending to vol × trend uses the same mechanism — just add
        the trend_state key.
        """
        if not self.config.enable_context_conditioning:
            return {}
        return {"vol_regime": ["low", "high"]}

    # ------------------------------------------------------------------
    # Pipeline execution
    # ------------------------------------------------------------------

    def _run_mi_scan_pre_step(self) -> None:
        """Phase 4.1 — Run feature MI scan once before the first proposal cycle.

        Loads features for the configured symbols/timeframe, runs
        run_feature_mi_scan(), and writes candidate_predicates.json to
        data/reports/feature_mi/<program_id>/ so _load_mi_candidate_predicates()
        picks it up on the first Step-4 proposal.

        Failures are logged and swallowed — a missing MI scan should never
        block a campaign from starting.
        """
        try:
            from project.pipelines.research.feature_mi_scan import run_feature_mi_scan
            from project.research.phase2 import load_features

            symbols = [s.strip().upper() for s in self.config.mi_scan_symbols.split(",") if s.strip()]
            parts = []
            for sym in symbols:
                df = load_features(self.data_root, self.config.program_id, sym,
                                   timeframe=self.config.mi_scan_timeframe)
                if not df.empty:
                    df = df.copy()
                    df["symbol"] = sym
                    parts.append(df)

            if not parts:
                _LOG.info("MI scan pre-step: no features found for %s — skipping.", symbols)
                return

            import pandas as _pd
            features = _pd.concat(parts, ignore_index=True)

            out_dir = self.data_root / "reports" / "feature_mi" / self.config.program_id
            result = run_feature_mi_scan(features, out_dir=out_dir)
            _LOG.info(
                "MI scan pre-step complete: %d MI rows, %d candidate predicates → %s",
                result["mi_rows"], result["candidate_predicates"], result["out_dir"],
            )
        except Exception as exc:
            _LOG.warning("MI scan pre-step failed (non-fatal): %s", exc)

    def _execute_pipeline(self, config_path: Path, run_id: str):
        _LOG.info("Executing pipeline for %s...", run_id)
        cmd = [
            sys.executable,
            "-m",
            "project.pipelines.run_all",
            "--mode",
            "research",
            "--run_id",
            run_id,
            "--experiment_config",
            str(config_path),
            "--registry_root",
            str(self.registry_root),
        ]
        _LOG.info("Command: %s", " ".join(cmd))
        subprocess.run(cmd, check=True, cwd=str(Path.cwd()))

    # ------------------------------------------------------------------
    # Stats update — now delegates to update_search_intelligence
    # ------------------------------------------------------------------

    def _update_campaign_stats(self) -> CampaignSummary:
        """Update campaign summary and frontier via the unified search_intelligence.

        Phase 2.1: replaces the dual _update_frontier + ledger-based system with
        a single call to update_search_intelligence(), which writes the richer
        campaign_summary.json and search_frontier.json (with candidate_next_moves).
        """
        # Always run search intelligence update regardless of ledger state
        try:
            update_search_intelligence(
                self.data_root,
                self.registry_root,
                self.config.program_id,
            )
        except Exception as exc:
            _LOG.warning("update_search_intelligence failed: %s", exc)

        if not self.ledger_path.exists():
            return CampaignSummary(self.config.program_id)

        df = pd.read_parquet(self.ledger_path)
        summary = CampaignSummary(
            program_id=self.config.program_id,
            total_runs=int(df["run_id"].nunique()) if "run_id" in df.columns else 0,
            total_generated=len(df),
            total_evaluated=int((df["eval_status"] == "evaluated").sum())
            if "eval_status" in df.columns else 0,
            total_empty_sample=int((df["eval_status"] == "empty_sample").sum())
            if "eval_status" in df.columns else 0,
            total_insufficient_sample=int((df["eval_status"] == "insufficient_sample").sum())
            if "eval_status" in df.columns else 0,
            total_unsupported=int(
                (df["eval_status"] == "unsupported_trigger_evaluator").sum()
            ) if "eval_status" in df.columns else 0,
            total_skipped=int(
                (df["eval_status"] == "not_executed_or_missing_data").sum()
            ) if "eval_status" in df.columns else 0,
        )

        if not df.empty and "expectancy" in df.columns and "eval_status" in df.columns:
            top = (
                df[df["eval_status"] == "evaluated"]
                .sort_values("expectancy", ascending=False)
                .head(5)
            )
            summary.top_hypotheses = top.to_dict(orient="records")

        self.summary_path.write_text(summary.to_json())
        return summary

    # ------------------------------------------------------------------
    # Halt check
    # ------------------------------------------------------------------

    def _should_halt(self, summary: CampaignSummary) -> bool:
        if summary.total_generated == 0:
            return False

        empty_share = summary.total_empty_sample / summary.total_generated
        if empty_share > self.config.halt_on_empty_share:
            _LOG.warning("High empty sample share: %.1f%%", empty_share * 100)
            return True

        unsupported_share = summary.total_unsupported / summary.total_generated
        if unsupported_share > self.config.halt_on_unsupported_share:
            _LOG.warning("High unsupported trigger share: %.1f%%", unsupported_share * 100)
            return True

        return False


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="Run an autonomous EDGE research campaign.")
    parser.add_argument("--program_id", required=True)
    parser.add_argument("--max_runs", type=int, default=3)
    parser.add_argument("--registry_root", default="project/configs/registries")
    parser.add_argument(
        "--research_mode",
        choices=["scan", "exploit", "explore"],
        default="scan",
        help="Proposal strategy: scan=frontier, exploit=promising regions, explore=adjacent",
    )
    args = parser.parse_args()

    data_root = get_data_root()
    config = CampaignConfig(
        program_id=args.program_id,
        max_runs=args.max_runs,
        research_mode=args.research_mode,
    )
    controller = CampaignController(config, data_root, Path(args.registry_root))
    controller.run_campaign()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
