"""Schema types for experiment engine: request, plan, and registry dataclasses."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

import yaml

from project.domain.hypotheses import HypothesisSpec
from project.research.semantic_registry_views import (
    build_canonical_semantic_registry_views,
    canonical_semantic_source_paths,
    runtime_config_source_paths,
)

_LOG = logging.getLogger(__name__)

@dataclass(frozen=True)
class InstrumentScope:
    instrument_classes: List[str]
    symbols: List[str]
    timeframe: str
    start: str
    end: str


@dataclass(frozen=True)
class TriggerSpace:
    allowed_trigger_types: List[str]
    events: Dict[str, List[str]] = field(default_factory=dict)
    canonical_regimes: List[str] = field(default_factory=list)
    subtypes: List[str] = field(default_factory=list)
    phases: List[str] = field(default_factory=list)
    evidence_modes: List[str] = field(default_factory=list)
    tiers: List[str] = field(default_factory=list)
    operational_roles: List[str] = field(default_factory=list)
    deployment_dispositions: List[str] = field(default_factory=list)
    sequences: Dict[str, Any] = field(default_factory=dict)
    states: Dict[str, List[str]] = field(default_factory=dict)
    transitions: Dict[str, List[Dict[str, str]]] = field(default_factory=dict)
    feature_predicates: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    interactions: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)


@dataclass(frozen=True)
class TemplateSelection:
    include: List[str]


@dataclass(frozen=True)
class EvaluationConfig:
    horizons_bars: List[int]
    directions: List[str]
    entry_lags: List[int]


@dataclass(frozen=True)
class ContextSelection:
    include: Dict[str, List[str]]


@dataclass(frozen=True)
class SearchControl:
    max_hypotheses_total: int
    max_hypotheses_per_template: int
    max_hypotheses_per_event_family: int
    random_seed: int = 42


@dataclass(frozen=True)
class PromotionConfig:
    enabled: bool
    track: str = "standard"
    multiplicity_scope: str = "program_id"


@dataclass(frozen=True)
class AgentExperimentRequest:
    program_id: str
    run_mode: str
    description: str
    instrument_scope: InstrumentScope
    trigger_space: TriggerSpace
    templates: TemplateSelection
    evaluation: EvaluationConfig
    contexts: ContextSelection
    search_control: SearchControl
    promotion: PromotionConfig
    avoid_region_keys: List[str] = field(default_factory=list)
    artifacts: Dict[str, bool] = field(default_factory=dict)

@dataclass(frozen=True)
class ValidatedExperimentPlan:
    program_id: str
    hypotheses: List[HypothesisSpec]
    required_detectors: List[str]
    required_features: List[str]
    required_states: List[str]
    estimated_hypothesis_count: int


class RegistryBundle:
    def __init__(self, registry_root: Path):
        self.registry_root = Path(registry_root)
        semantic_views = build_canonical_semantic_registry_views()
        self.events = semantic_views["events"]
        self.states = semantic_views["states"]
        self.templates = semantic_views["templates"]
        self.features = self._load_yaml(self.registry_root / "features.yaml")
        self.contexts = self._load_yaml(self.registry_root / "contexts.yaml")
        self.limits = self._load_yaml(self.registry_root / "search_limits.yaml")
        self.detectors = self._load_yaml(self.registry_root / "detectors.yaml")
        self.semantic_source_paths = canonical_semantic_source_paths()
        self.runtime_config_source_paths = runtime_config_source_paths(self.registry_root)

    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        if not path.exists():
            _LOG.warning(f"Registry file not found: {path}")
            return {}
        payload = yaml.safe_load(path.read_text())
        return payload if isinstance(payload, dict) else {}

    def registry_source_paths(self) -> Dict[str, List[Path]]:
        return {
            **self.semantic_source_paths,
            **self.runtime_config_source_paths,
        }
