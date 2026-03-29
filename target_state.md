# Target State

## 1. Executive target state

The target architecture is a strict layered system in which persisted specs define the ontology, the compiled domain registry is the only read surface for event/state/template identity, research services own bounded search and statistical evaluation, strategy compilation owns the transformation from promoted research artifacts into typed trading contracts, and the engine owns only execution simulation and ledger production. Proposal issuance, experiment planning, hypothesis expansion, candidate evaluation, blueprint compilation, and engine execution remain separate objects with explicit lineage links. Compatibility aliases and wrappers may exist only as temporary edge shims or permanent boundary-only entrypoints; they must never be the semantic center of the system, and no layer may infer canonical meaning from loose dataframe conventions when a typed contract already exists.

## 2. Canonical source-of-truth surfaces

| Concern | Single authoritative surface | Why this is the source of truth |
| --- | --- | --- |
| Event registry | `project.domain.compiled_registry.get_domain_registry()` backed by `spec/events/event_registry_unified.yaml` | Current code already centralizes event alias resolution, family/regime lookup, template compatibility, state/context mapping, and searchable registry views here. Business logic should read through this compiled surface, not by reloading raw fragments. |
| Regime routing | `project.research.regime_routing` backed by `spec/events/regime_routing.yaml` | Routing buckets, template eligibility, routing profile identity, and recommended bucket propagation are all resolved here. |
| Research evaluation | `project.research.services` | `execute_candidate_discovery()` and `execute_promotion()` are the maintained workflow APIs. `project.eval` is a computation library, not the workflow authority, and `evaluation_service.py` is not the architectural center. |
| Engine execution | `project.engine.runner.run_engine` | This is the only surface that should assemble context, call runtime strategies, apply execution/fill logic, allocate portfolio risk, and emit engine manifests plus schema-validated frames. |
| Identity chain | Typed contracts in `project.research.agent_io.proposal_schema`, `project.research.experiment_engine`, `project.domain.hypotheses`, `project.strategy.dsl.schema`, and `project.strategy.models.executable_strategy_spec` | Identity is authoritative only when carried by typed objects and explicit IDs. Dataframe rows are projections, not identity authorities. |
| Artifact contracts | `project.contracts` with `project.contracts.pipeline_registry` as stage/artifact authority, `project.contracts.schemas` as report-frame authority, and `project.engine.schema` as engine-frame authority | Stage IO, report schemas, and engine schemas are already explicitly declared here; artifacts must conform to these contracts rather than ad hoc column conventions. |

## 3. Canonical boundaries

### Research search path

Canonical path: `Proposal -> Experiment -> Hypothesis expansion -> candidate discovery artifacts`.

Allowed:
- validate and normalize operator input
- expand a bounded search space into `HypothesisSpec` objects
- check registry/template/state compatibility
- run discovery scoring, sample-quality filters, multiplicity inputs, and search diagnostics
- write phase-2 candidate artifacts and research memory

Must never pretend to be:
- promotion readiness
- executable strategy packaging
- engine/backtest truth
- live or simulated fill realism

The canonical stage for this path is the search-backed path represented by `project.research.experiment_engine`, `project.research.services.candidate_discovery_service`, and the `phase2_search_engine` stage wrapper. The legacy `phase2_conditional_hypotheses__*` path is compatibility debt, not a second first-class architecture.

### Statistical evaluation path

Canonical path: `Candidate rows -> bridge/promotion evidence -> promotion decision -> reporting`.

Allowed:
- assign splits and holdout integrity
- compute significance, q-values, robustness, stress, cost, placebo, and promotion policy outcomes
- attach evidence bundles and promotion diagnostics
- normalize report outputs under declared schemas

Must never pretend to be:
- ontology ownership
- detector execution
- blueprint compilation
- engine execution or realized tradability proof

Bridge pass and promotion pass are evaluation outcomes only. They are stronger than discovery survival and still weaker than an engine-produced execution ledger.

### Engine/backtest/execution path

Canonical path: `Blueprint or ExecutableStrategySpec -> strategy runtime -> run_engine -> engine artifacts`.

Allowed:
- load bars/features/context
- interpret DSL or executable strategy contracts
- apply entry/exit, fill, cost, allocation, and portfolio aggregation logic
- emit strategy traces, strategy frames, portfolio frames, and engine run manifest artifacts

Must never pretend to be:
- research search
- statistical discovery
- promotion policy
- ontology validation

The engine may consume research lineage, but it must not reconstruct or reinterpret research validity from loose research report rows.

### Strategy lineage path

Canonical path: `Candidate -> Blueprint -> ExecutableStrategySpec -> Engine run metadata`.

Allowed:
- compile surviving research outputs into typed trading contracts
- preserve provenance fields forward without changing their meaning
- enrich runtime metadata with carried lineage fields such as `candidate_id`, `blueprint_id`, `canonical_event_type`, `canonical_regime`, and `routing_profile_id`

Must never pretend to be:
- a new evaluation layer
- a substitute for proposal or experiment planning
- a place to synthesize missing hypothesis/candidate identity from downstream outputs

Strategy packaging is a contract translation step. It is not a place to re-score research claims or collapse multiple identity objects into one.

## 4. Canonical identity model

Exact chain:

`Proposal -> Experiment -> Hypothesis -> Candidate -> Blueprint -> Engine run`

### Proposal

A Proposal is the operator-authored bounded research intent defined by `AgentProposal` in `project.research.agent_io.proposal_schema`. It describes scope, trigger space, templates, contexts, horizons, directions, entry lags, and proposal-settable knobs. It is not yet a validated search plan or executable run. Proposal identity should be carried by `proposal_id` plus the stored proposal artifact under experiment memory.

Forbidden aliases/legacy synonyms:
- `objective`
- `promotion_mode`
- `run_all_overrides`
- `experiment config`
- `run`

### Experiment

An Experiment is the validated, registry-checked search plan produced by `project.research.experiment_engine` from a Proposal. It is the object that fixes the search envelope, required detectors/features/states, and the concrete `HypothesisSpec` expansion space. It should be identified by the validated experiment artifact set rooted under `data/artifacts/experiments/<program_id>/<run_id>/`, not by raw CLI flags. An Experiment is not a campaign, not a proposal, and not a single evaluated hypothesis.

Forbidden aliases/legacy synonyms:
- `proposal`
- `program`
- `campaign`
- `run`
- `search request`

### Hypothesis

A Hypothesis is a single tested research claim materialized as `HypothesisSpec` plus deterministic `hypothesis_id`. It binds one trigger, one direction, one horizon, one template, optional context, and optional feature predicate into a canonical statistical claim. A Hypothesis exists before any selection or promotion judgment. It is the unit of research attribution and must remain stable across replay of the same experiment config.

Forbidden aliases/legacy synonyms:
- `candidate`
- `bridge candidate`
- `strategy`
- `phase2 row`

### Candidate

A Candidate is an evaluated hypothesis row that carries statistical outcomes, diagnostics, and later bridge/promotion decisions. It must retain `hypothesis_id` as lineage and own a separate `candidate_id` once the system starts selecting, deduplicating, promoting, exporting, or packaging it. The current bridge adapter and finalizer still allow `candidate_id` to collapse onto `hypothesis_id`; that is explicitly non-canonical and must end. Candidate identity exists to support evaluation, promotion, export, and packaging decisions across different views of the same underlying tested claim.

Forbidden aliases/legacy synonyms:
- `hypothesis`
- `candidate_id == hypothesis_id`
- `edge export row`
- `strategy candidate`
- `promoted blueprint`

### Blueprint

A Blueprint is the canonical typed strategy contract defined by `project.strategy.dsl.schema.Blueprint`. It is compiled from a surviving Candidate and carries preserved research lineage, symbol scope, entry/exit logic, execution assumptions, sizing, overlays, evaluation expectations, and packaging-time constraints. It is the first object in the chain that describes a tradable strategy contract rather than a statistical research claim.

Forbidden aliases/legacy synonyms:
- `candidate`
- `strategy json`
- `executable strategy spec`
- `promotion row`

### Engine run

An Engine run is a concrete execution/backtest invocation rooted at `project.engine.runner.run_engine` and materialized by `engine_run_manifest.json` plus engine artifact frames. It consumes one or more Blueprints or `ExecutableStrategySpec` payloads and produces simulated execution traces and portfolio ledgers. It must carry upstream lineage such as `run_id`, `candidate_id`, and `blueprint_id`, but it is not itself an Experiment or a research evaluation object.

Forbidden aliases/legacy synonyms:
- `experiment`
- `proposal`
- `candidate`
- `promotion pass`

## 5. Compatibility policy

Compatibility layers are allowed only under two rules:

1. boundary-only wrappers may exist to satisfy CLI, stage, or package-root ergonomics, but they must delegate inward and contain no business policy;
2. semantic compatibility shims are temporary, must be write-through or read-through only, and must be deleted once the explicit removal condition is met.

Compatibility layers must never remain the primary behavior. New code must target canonical surfaces directly.

### Temporary semantic compatibility surfaces

| Surface | Current compatibility behavior | Status | Exact removal condition |
| --- | --- | --- | --- |
| `canonical_family` alongside `canonical_regime` | `canonical_family` is still emitted and treated as a staged alias of `canonical_regime` in the unified registry, lineage fields, and alias properties on event config/spec types | Temporary | Remove when no loader, schema, artifact writer, report reader, or type property references `canonical_family`, and every consumer reads `canonical_regime` only |
| `legacy_family` plus legacy-family merges in `project.domain.registry_loader` and `project.events.config` | legacy family names still drive family-default/template-compat merges and family lookup fallback | Temporary | Remove when family defaults, template compatibility, and family filtering are keyed solely by canonical regime, and `legacy_family` is no longer consulted anywhere in code or schemas |
| `project.events.event_aliases.py` and executable alias translation | alias tokens such as `BASIS_DISLOCATION` and proxy-to-executable mappings are still normalized at read time | Temporary | Remove each mapping when the alias token no longer appears in specs, fixtures, docs, proposal inputs, or artifact readers |
| Dual registry loading in `project.spec_registry.load_template_registry()`, `project.domain.registry_loader._load_states()`, and `project.events.registry.load_milestone_event_registry()` | loaders still merge or fall back across unified specs, legacy specs, and runtime registries | Temporary | Remove when a single spec family exists for templates and states, unified event registry absence is a hard error, and no caller depends on dual-load merge behavior |
| Proposal input aliases `objective` and `promotion_mode` | proposal schema still accepts legacy field names and normalizes them to canonical names | Temporary | Remove when all proposal producers emit `objective_name` and `promotion_profile` only |
| Pipeline alias `candidate_promotion_profile` | `run_all` and stage planning still translate this pipeline-specific name into promotion behavior | Temporary | Remove when promotion selection is driven only from proposal/experiment `promotion_profile` and the pipeline parser no longer accepts `candidate_promotion_profile` |
| Legacy conditional discovery path and `runs_legacy_phase2_conditional` behavior | planning still supports per-event `phase2_conditional_hypotheses__*` stages in parallel with canonical `phase2_search_engine` | Temporary | Remove when every research run uses `phase2_search_engine` only and no stage manifest, run comparison, or reflection logic expects legacy conditional stage names |
| `project.research.search.bridge_adapter` and `project.research.finalize_experiment` hypothesis/candidate fallback | bridge shaping still synthesizes `candidate_id` from `hypothesis_id`, and finalization still falls back between the two | Temporary | Remove when every candidate-carrying artifact contains both `hypothesis_id` and `candidate_id`, and all joins use the explicit pair instead of fallback matching |
| Blueprint normalization of legacy `entry.conditions` strings in `project.strategy.dsl.normalize` | runtime still accepts old string conditions and expands them into `condition_nodes` | Temporary | Remove when all blueprint writers emit canonical `condition_nodes` and runtime loading rejects string-only condition payloads |
| Promotion/report aliases in `project.research.validation.evidence_bundle` and `project.research.promotion.promotion_decision_support` | old gate names and non-boolean gate payloads are normalized into canonical names/booleans | Temporary | Remove when all promotion inputs emit canonical gate keys and native boolean values only |
| `funding_bps` condition key alias in `project.research.condition_key_contract` | condition joins still treat `funding_bps` as alias of `funding_rate_bps` | Temporary | Remove when no blueprint, candidate, or joined feature contract references `funding_bps` |
| `embargo_days` fallback in `project.research.phase2.assign_event_split_labels` | split labeling still converts `embargo_days` into `embargo_bars` when bars are absent | Temporary | Remove when every caller passes `embargo_bars` and no config/help surface documents `embargo_days` |
| Report path fallback in `project.research.finalize_experiment` | finalization still scans both `data/reports/phase2_discovery` and `data/reports/phase2` | Temporary | Remove when all writers emit under `data/reports/phase2` only and no reader depends on the old directory |

### Temporary compatibility wrappers and facades

| Surface | Canonical replacement | Status | Exact removal condition |
| --- | --- | --- | --- |
| `project/strategy/compiler/blueprint_compiler.py` | `project.research.compile_strategy_blueprints` | Temporary | Remove when no imports, scripts, or docs reference the wrapper module |
| `project/research/generic_detector_task.py` | `project.research.analyze_events` | Temporary | Remove when all stage planning and callers invoke `analyze_events` or its maintained CLI directly |
| `project/research/phase2_spec_registry.py` | `project.specs.gates` | Temporary | Remove when all callers import gate/family policy from `project.specs.gates` directly |
| `project.events.config.ComposedEventConfig` and `ComposedTemplateConfig` | `project.events.config.ComposedConfig` | Temporary | Remove when no imports or tests reference the alias names |
| `project/research/candidate_schema.py` | canonical candidate schema owner in `project.research.research_core` | Temporary | Remove when no imports reference the facade module |
| `project/strategy/models/blueprint.py` | `project.strategy.dsl.Blueprint` | Temporary | Remove when imports target `project.strategy.dsl` or the canonical package root only |
| `project/compilers/executable_strategy_spec.py` | `project.strategy.models.executable_strategy_spec` or canonical package root `project.compilers` | Temporary | Remove when no code imports the compatibility submodule directly |
| `project/research/helpers/shrinkage.py` | public names in the parameter/estimation support modules | Temporary | Remove when no caller imports private-prefix names through this facade |
| `project/eval/multiplicity.py` | research validation multiple-testing backend | Temporary | Remove when all callers use the research validation surface directly and no reporting path imports the wrapper |

### Retained boundary-only wrapper entrypoints

These are allowed to remain as wrappers, but only as thin delegation shells. They are not compatibility debt if they stay policy-free.

| Entry point | Canonical delegate | Status | Retention rule |
| --- | --- | --- | --- |
| `project/pipelines/research/phase2_candidate_discovery.py` | pipeline CLI/service path under `project.pipelines.research.cli` and `project.research.services` | Boundary-only | May remain only as argv translation and stage entrypoint |
| `project/pipelines/research/promote_candidates.py` | pipeline CLI/service path under `project.pipelines.research.cli` and `project.research.services` | Boundary-only | May remain only as argv translation and stage entrypoint |
| `project/pipelines/research/phase2_search_engine.py` | `project.research.phase2_search_engine` | Boundary-only | May remain only as stage wrapper with no local policy |
| `project/pipelines/research/bridge_evaluate_phase2.py` | `project.research.bridge_evaluate_phase2` | Boundary-only | May remain only as stage wrapper with no local policy |
| `project/pipelines/research/finalize_experiment.py` | `project.research.finalize_experiment` | Boundary-only | May remain only as stage wrapper with no local policy |
| `project/research/agent_io/{proposal_to_experiment,execute_proposal,issue_proposal}.py` | canonical operator entrypoints around proposal/experiment/run_all orchestration | Boundary-only | May remain because they are operator surfaces, but they must continue to delegate into typed proposal/experiment services rather than reimplement policy |

## 6. Migration order

### Phase 1. Freeze ontology and routing authority

Objective:
- make the compiled domain registry and regime routing the only semantic read surfaces

Scope:
- treat `spec/events/event_registry_unified.yaml` and `spec/events/regime_routing.yaml` as the only persisted authorities
- stop adding new direct reads of raw registry fragments in research, strategy, or engine code
- demote `canonical_family` to a write-through alias and `legacy_family` to compatibility-only status

Dependencies:
- none

Rollback concern:
- tests, fixtures, or old readers that still expect legacy family lookups or raw registry fallback behavior

### Phase 2. Normalize the identity chain

Objective:
- enforce distinct identities for Proposal, Experiment, Hypothesis, Candidate, Blueprint, and Engine run

Scope:
- make `hypothesis_id`, `candidate_id`, and `blueprint.id` distinct and explicit
- remove candidate/hypothesis fallback joins
- ensure every downstream artifact carries upstream foreign keys instead of reconstructing them

Dependencies:
- Phase 1

Rollback concern:
- bridge/finalization/memory code paths that currently rely on `candidate_id == hypothesis_id` or heuristic fallback matching

### Phase 3. Consolidate research discovery and statistical evaluation

Objective:
- make service-layer research APIs the only primary evaluation path

Scope:
- standardize on `project.research.services.candidate_discovery_service` and `project.research.services.promotion_service`
- keep pipeline wrappers thin and policy-free
- retire the legacy conditional discovery path
- treat `project.eval` as library code only, never as a parallel workflow surface

Dependencies:
- Phases 1 and 2

Rollback concern:
- `run_all` stage planning, historical stage names, and report consumers that still expect legacy conditional stages or bridge-shaped candidate rows

### Phase 4. Harden strategy packaging contracts

Objective:
- make `Candidate -> Blueprint -> ExecutableStrategySpec` the only packaging path

Scope:
- standardize on `project.strategy.dsl.schema.Blueprint`
- standardize on `ExecutableStrategySpec.from_blueprint()`
- remove string-condition compatibility from blueprint normalization
- eliminate compile-time facade ambiguity between research compiler modules and compatibility wrappers

Dependencies:
- Phases 1 through 3

Rollback concern:
- existing JSONL blueprint consumers, live portfolio state readers, and scripts importing legacy compiler facades

### Phase 5. Delete remaining shims and path fallbacks

Objective:
- remove temporary compatibility surfaces once canonical call sites are clean

Scope:
- delete temporary wrappers, alias fields, legacy path scanners, and gate alias normalizers
- require hard errors instead of fallback loading for missing canonical artifacts/specs
- reduce compatibility surfaces to permanent boundary-only entrypoints only

Dependencies:
- Phases 1 through 4 plus zero-importer or zero-emitter proof for each removable shim

Rollback concern:
- archived artifacts, notebooks, tests, or synthetic fixtures that were never migrated off old names or old directories

## 7. Non-goals

- Do not change detector math, event semantics, or the ontology meaning of existing event types during this refactor.
- Do not retune discovery, bridge, promotion, or objective thresholds as part of architectural cleanup.
- Do not redesign the fill model, slippage model, allocation logic, or OMS/runtime behavior inside the engine.
- Do not change the data lake layout or historical dataset contents except where a path alias is explicitly being retired after migration.
- Do not broaden the search space, add new strategy templates, or introduce new research product features during the boundary cleanup.
- Do not treat synthetic-data support, calibration profiles, or certification workflows as the primary architectural target; they must follow the same contracts, not drive them.
- Do not preserve ambiguous aliases simply because historical artifacts exist; historical readers may be bridged temporarily, but canonical behavior must stay singular.
