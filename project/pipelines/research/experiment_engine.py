"""Experiment engine: validation, expansion, and planning for agent experiment requests."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from project.core.config import get_data_root
from project.domain.hypotheses import HypothesisSpec, TriggerSpec, TriggerType
from project.pipelines.research.experiment_engine_schema import (
    AgentExperimentRequest,
    ContextSelection,
    EvaluationConfig,
    InstrumentScope,
    PromotionConfig,
    RegistryBundle,
    SearchControl,
    TemplateSelection,
    TriggerSpace,
    ValidatedExperimentPlan,
)

log = logging.getLogger(__name__)

def load_agent_experiment_config(path: Path) -> AgentExperimentRequest:
    raw = yaml.safe_load(path.read_text())
    return AgentExperimentRequest(
        program_id=raw["program_id"],
        run_mode=raw["run_mode"],
        description=raw.get("description", ""),
        instrument_scope=InstrumentScope(**raw["instrument_scope"]),
        trigger_space=TriggerSpace(**raw["trigger_space"]),
        templates=TemplateSelection(**raw["templates"]),
        evaluation=EvaluationConfig(**raw["evaluation"]),
        contexts=ContextSelection(**raw["contexts"]),
        search_control=SearchControl(**raw["search_control"]),
        promotion=PromotionConfig(**raw["promotion"]),
        artifacts=raw.get("artifacts", {}),
    )


def validate_agent_request(
    request: AgentExperimentRequest,
    registries: RegistryBundle,
) -> None:
    # 1. Platform-level Validations (Invariants)
    _validate_templates(request, registries)
    _validate_instrument_compatibility(request, registries)
    _validate_contexts(request, registries)
    _validate_search_limits(request, registries)

    # 2. Campaign-level Safeguards & State
    _validate_campaign_status(request, registries)

    # 3. Proposal Quality Checks (Agent Steering)
    _validate_proposal_quality(request, registries)

    # 4. Trigger-specific validations
    for t_type in request.trigger_space.allowed_trigger_types:
        t_type_upper = t_type.upper()
        if t_type_upper == "EVENT":
            _validate_event_trigger(request, registries)
        elif t_type_upper == "STATE":
            _validate_state_trigger(request, registries)
        elif t_type_upper == "TRANSITION":
            _validate_transition_trigger(request, registries)
        elif t_type_upper == "SEQUENCE":
            _validate_sequence_trigger(request, registries)
        elif t_type_upper == "FEATURE_PREDICATE":
            _validate_feature_predicate_trigger(request, registries)
        elif t_type_upper == "INTERACTION":
            _validate_interaction_trigger(request, registries)
        else:
            raise ValueError(f"Unsupported trigger type in experiment config: {t_type}")



from project.pipelines.research.experiment_engine_validators import (
    _validate_campaign_status,
    _validate_proposal_quality,
    _validate_templates,
    _validate_instrument_compatibility,
    _validate_contexts,
    _validate_search_limits,
    _validate_event_trigger,
    _validate_state_trigger,
    _validate_transition_trigger,
    _validate_sequence_trigger,
    _validate_feature_predicate_trigger,
    _validate_interaction_trigger,
    expand_hypotheses,
    _expand_event_triggers,
    _expand_state_triggers,
    _expand_transition_triggers,
    _expand_sequence_triggers,
    _expand_feature_predicate_triggers,
    _expand_interaction_triggers,
)


def resolve_required_detectors(
    hypotheses: List[HypothesisSpec],
    registries: RegistryBundle,
) -> List[str]:
    detector_map = registries.detectors.get("detector_ownership", {})
    required = set()
    for h in hypotheses:
        t = h.trigger
        if t.trigger_type == "event":
            det = detector_map.get(t.event_id)
            if det:
                required.add(det)
        elif t.trigger_type == "sequence":
            required.add("EventSequenceDetector")
            if t.events:
                for eid in t.events:
                    det = detector_map.get(eid)
                    if det:
                        required.add(det)
        elif t.trigger_type == "interaction":
            required.add("EventInteractionDetector")
            for operand in [t.left, t.right]:
                det = detector_map.get(operand)
                if det:
                    required.add(det)

    return sorted(list(required))


def resolve_required_features(
    hypotheses: List[HypothesisSpec],
    registries: RegistryBundle,
) -> List[str]:
    required = set()
    event_meta = registries.events.get("events", {})

    for h in hypotheses:
        t = h.trigger
        # 1. Direct feature predicates
        if t.trigger_type == "feature_predicate":
            if t.feature:
                required.add(t.feature)

        # 2. Event dependencies
        if t.trigger_type == "event":
            meta = event_meta.get(t.event_id, {})
            for f in meta.get("requires_features", []):
                required.add(f)

        # 3. Sequence constituent dependencies
        if t.trigger_type == "sequence" and t.events:
            for eid in t.events:
                meta = event_meta.get(eid, {})
                for f in meta.get("requires_features", []):
                    required.add(f)

        # 4. Interaction operand dependencies
        if t.trigger_type == "interaction":
            for operand in [t.left, t.right]:
                meta = event_meta.get(operand, {})
                for f in meta.get("requires_features", []):
                    required.add(f)

    return sorted(list(required))


def resolve_required_states(
    hypotheses: List[HypothesisSpec],
    registries: RegistryBundle,
) -> List[str]:
    required = set()
    for h in hypotheses:
        t = h.trigger
        if t.trigger_type == "state":
            if t.state_id:
                required.add(t.state_id)
        elif t.trigger_type == "transition":
            if t.from_state:
                required.add(t.from_state)
            if t.to_state:
                required.add(t.to_state)
        elif t.trigger_type == "interaction":
            state_registry = registries.states.get("states", {})
            for operand in [t.left, t.right]:
                if operand in state_registry:
                    required.add(operand)

    return sorted(list(required))


def export_experiment_artifacts(
    plan: ValidatedExperimentPlan,
    config_path: Path,
    registry_root: Path,
    out_dir: Path,
) -> None:
    import shutil
    import hashlib
    import json
    import pandas as pd

    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. request.yaml
    shutil.copy(config_path, out_dir / "request.yaml")

    # 2. hashes
    req_bytes = (out_dir / "request.yaml").read_bytes()
    (out_dir / "request_hash.txt").write_text(hashlib.sha256(req_bytes).hexdigest())

    reg_hash = hashlib.sha256()
    for y in sorted(registry_root.glob("*.yaml")):
        reg_hash.update(y.name.encode("utf-8"))
        reg_hash.update(y.read_bytes())
    (out_dir / "registry_hash.txt").write_text(reg_hash.hexdigest())

    # 3. Validated plan & execution requirements
    plan_dict = {
        "program_id": plan.program_id,
        "estimated_hypothesis_count": plan.estimated_hypothesis_count,
        "required_detectors": plan.required_detectors,
        "required_features": plan.required_features,
        "required_states": plan.required_states,
    }
    (out_dir / "validated_plan.json").write_text(json.dumps(plan_dict, indent=2))

    req_dict = {
        "detectors": plan.required_detectors,
        "features": plan.required_features,
        "state_engines": plan.required_states,
    }
    (out_dir / "execution_requirements.json").write_text(json.dumps(req_dict, indent=2))

    # 4. Expanded hypotheses
    rows = []
    for h in plan.hypotheses:
        row = h.to_dict()
        row["hypothesis_id"] = h.hypothesis_id()
        row["trigger_type"] = h.trigger.trigger_type
        row["context_slice"] = json.dumps(h.context) if h.context else None
        row["trigger_payload"] = json.dumps(h.trigger.to_dict())

        # Clean up nested dicts to keep parquet flat
        if "trigger" in row:
            del row["trigger"]
        if "feature_condition" in row:
            del row["feature_condition"]
        if "context" in row:
            del row["context"]

        rows.append(row)

    df = pd.DataFrame(rows)
    # Ensure all required schema columns even if empty
    for col in [
        "hypothesis_id",
        "trigger_type",
        "trigger_payload",
        "template_id",
        "horizon",
        "direction",
        "entry_lag",
        "context_slice",
    ]:
        if col not in df.columns:
            df[col] = None

    from project.io.utils import write_parquet

    write_parquet(df, out_dir / "expanded_hypotheses.parquet")


def build_experiment_plan(
    config_path: Path, registry_root: Path, out_dir: Optional[Path] = None
) -> ValidatedExperimentPlan:
    registries = RegistryBundle(registry_root)
    request = load_agent_experiment_config(config_path)
    validate_agent_request(request, registries)
    hypotheses = expand_hypotheses(request, registries)

    detectors = resolve_required_detectors(hypotheses, registries)
    features = resolve_required_features(hypotheses, registries)
    states = resolve_required_states(hypotheses, registries)

    plan = ValidatedExperimentPlan(
        program_id=request.program_id,
        hypotheses=hypotheses,
        required_detectors=detectors,
        required_features=features,
        required_states=states,
        estimated_hypothesis_count=len(hypotheses),
    )

    if out_dir:
        export_experiment_artifacts(plan, config_path, registry_root, out_dir)

    return plan
