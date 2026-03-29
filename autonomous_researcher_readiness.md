# Autonomous Researcher Readiness

## Executive Assessment

This repository is close to being usable by a bounded autonomous research agent, but it was not yet packaged as one disciplined operating surface.

Verified strengths:

- Event and regime ontology already compile through `project.domain.compiled_registry.get_domain_registry()` backed by `spec/events/event_registry_unified.yaml`.
- Regime routing already has an authoritative audit surface in `project.research.regime_routing` backed by `spec/events/regime_routing.yaml`.
- Proposal parsing, proposal translation, and bounded experiment planning already exist in `project.research.agent_io.proposal_schema`, `project.research.agent_io.proposal_to_experiment`, `project.research.agent_io.execute_proposal`, `project.research.agent_io.issue_proposal`, and `project.research.experiment_engine`.
- Regime-aware phase-2 discovery already exists in `project.research.phase2_search_engine` and `project.research.services.candidate_discovery_service`.
- Promotion, evidence-bundle shaping, and decision diagnostics already exist in `project.research.services.promotion_service` and `project.research.validation.evidence_bundle`.
- Strategy lineage can already propagate into tradable contracts through `project.research.compile_strategy_blueprints`, `project.strategy.dsl.schema`, `project.strategy.models.executable_strategy_spec`, and `project.engine.runner.run_engine_for_specs`.
- Experiment review loops already exist in pieces through `project.research.services.run_comparison_service`, `project.research.search_intelligence`, and `project.research.knowledge.query`.

The main readiness gap was not missing research machinery. It was missing an explicit operator contract that stops an autonomous agent from treating those primitives as license for broad search, silent contract edits, or overclaiming from backtest outputs.

## Verified Operating Surfaces

### Already implemented

- Event and regime registry
  - Authority: `project/domain/compiled_registry.py`
  - Backing specs: `spec/events/event_registry_unified.yaml`
  - Evidence: compiled registry exposes canonical regime fanout, event lookup, template compatibility, and executable-only filtering.
- Regime routing
  - Authority: `project/research/regime_routing.py`
  - Backing spec: `spec/events/regime_routing.yaml`
  - Evidence: `validate_regime_routing_spec()` audits coverage across executable canonical regimes and template eligibility; tested in `project/tests/research/test_regime_routing.py`.
- Hypothesis and trigger identity
  - Authority: `project/domain/hypotheses.py`
  - Evidence: `TriggerSpec` validates event/state/transition/interaction inputs against the compiled registry; `HypothesisSpec` is the typed research claim.
- Experiment proposal parsing and bounded planning
  - Authority: `project/research/agent_io/proposal_schema.py`, `project/research/agent_io/proposal_to_experiment.py`, `project/research/experiment_engine.py`
  - Evidence: canonical-regime scoped proposals are explicitly supported and tested in `project/tests/research/agent_io/test_proposal_schema.py`.
- Engine execution
  - Authority: `project/engine/runner.py`
  - Engine artifact contract: `project/engine/schema.py`
  - Evidence: `run_engine_for_specs()` preserves proposal/run/hypothesis/candidate/blueprint/regime metadata from executable specs into engine invocation.
- Artifact and report contracts
  - Authority: `project/contracts/pipeline_registry.py`, `project/contracts/schemas.py`, `project/reliability/contracts.py`
  - Evidence: current-format phase-2 artifacts require `candidate_id`, `hypothesis_id`, `event_type`, `symbol`, and `run_id`, and reject collapsed lineage.
- Run comparison
  - Authority: `project/research/services/run_comparison_service.py`
  - CLI entrypoint: `project/scripts/compare_research_runs.py`
  - Evidence: comparison summarizes phase-2, promotion, edge-candidate, and regime-effectiveness drift.

### Partially scaffolded

- Regime-first search loop
  - The code supports regime-first scoping through `trigger_space.canonical_regimes` and the regime-first frontier in `project.research.search_intelligence`.
  - The repository did not previously provide an explicit default operator loop that forces one-regime/one-mechanism/one-expression execution.
- Candidate and promotion regime metadata propagation
  - Phase-2 and promotion schemas include `canonical_regime`, `recommended_bucket`, `regime_bucket`, and `routing_profile_id`.
  - Metadata annotation is present in `project.research.regime_routing.annotate_regime_metadata`.
  - This is still partially scaffolded because compatibility readers and fallback logic remain in `project.research.finalize_experiment`, and bounded runs can still terminate before blueprint emission when nothing is promoted.
- Strategy lineage propagation
  - Blueprints and executable specs carry `proposal_id`, `hypothesis_id`, `candidate_id`, `blueprint_id`, `canonical_event_type`, `canonical_regime`, and `routing_profile_id`.
  - This is still partially scaffolded operationally because the maintained bounded smoke path does not yet guarantee a promotable candidate for end-to-end replay.
- Experiment review loops
  - Memory, reflections, adjacent-region queries, and run comparison exist.
  - They were not previously wrapped into a single operator-facing review template or decision standard.

### Missing but high-value

- A hard operating contract for autonomous research.
- Root-level templates for bounded hypothesis writing, experiment review, and edge-registry updates.
- A single verification block entrypoint that an agent can run after code changes and after experiments.
- A sharply prioritized backlog tied to actual canonical regimes/events/templates instead of generic trading ideas.
- Explicit rules separating research evidence from execution truth and from live-readiness claims.

## Current Fit For Autonomous Research

This codebase is strongest when the agent behaves as a conservative mechanism researcher inside the existing ontology.

Highest-fit research families, verified from the compiled registry and event specs:

- `BASIS_FUNDING_DISLOCATION`
  - Example events: `BASIS_DISLOC`, `FUNDING_EXTREME_ONSET`, `FUNDING_NORMALIZATION_TRIGGER`, `SPOT_PERP_BASIS_SHOCK`, `CROSS_VENUE_DESYNC`
  - Example templates: `basis_repair`, `convergence`, `desync_repair`, `only_if_funding`
- `LIQUIDITY_STRESS`
  - Example events: `LIQUIDITY_VACUUM`, `LIQUIDITY_GAP_PRINT`, `LIQUIDITY_STRESS_DIRECT`, `LIQUIDITY_SHOCK`
  - Example templates: `mean_reversion`, `overshoot_repair`, `tail_risk_avoid`, `only_if_liquidity`
- `POSITIONING_UNWIND_DELEVERAGING`
  - Example events: `DELEVERAGING_WAVE`, `OI_FLUSH`, `POST_DELEVERAGING_REBOUND`
  - Example templates: `exhaustion_reversal`, `momentum_fade`, `convergence`
- `TREND_FAILURE_EXHAUSTION`
  - Example events: `FORCED_FLOW_EXHAUSTION`, `LIQUIDATION_EXHAUSTION_REVERSAL`, `TREND_EXHAUSTION_TRIGGER`
  - Example templates: `exhaustion_reversal`, `false_breakout_reversal`, `stop_run_repair`
- `CROSS_ASSET_DESYNCHRONIZATION`
  - Example events: `CROSS_ASSET_DESYNC_EVENT`, `INDEX_COMPONENT_DIVERGENCE`, `LEAD_LAG_BREAK`
  - Example templates: `lead_lag_follow`, `desync_repair`, `convergence`

## Strongest Anti-Patterns To Avoid

- Universal alpha or asset-agnostic forecasting claims.
- Broad discovery over unrelated regimes in one run.
- Treating phase-2 discovery or promotion outcomes as execution proof.
- Silent edits to contract-defining files such as `project/contracts/schemas.py` or `project/strategy/dsl/schema.py`.
- Threshold relaxation as the first response to a failed experiment.
- Artifact interpretation from headline metrics before reconciling manifests, diagnostics, and schema validity.

## Final Readiness Verdict

Readiness verdict: conditionally ready.

The repository already supports disciplined autonomous research if the agent is constrained to:

- canonical proposal -> validated plan -> bounded run,
- regime-first and mechanism-first scope,
- artifact-first review,
- explicit keep/modify/kill decisions,
- no silent contract drift,
- mandatory verification after changes and after runs.

What was blocked before was operator discipline, not core research machinery. This package supplies that missing discipline layer. The next material technical upgrade should be one maintained bounded fixture that deterministically yields at least one promoted candidate so the blueprint/spec/engine bridge can be verified on run-scoped artifacts without broadening thresholds or scope.
