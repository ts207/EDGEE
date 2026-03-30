# Repository Map

This file explains where the important logic lives and what each layer owns.

## High-Level Layout

- [project/](../project): Python implementation
- [spec/](../spec): YAML domain specs and policies
- [data/](../data): run outputs, raw lake, reports, artifacts
- [tests/](../tests): top-level tests
- [docs/](.): hand-authored documentation

## `project/`

Most day-to-day work lands in these directories:

- [project/pipelines/](../project/pipelines): orchestration, planning, stage execution, manifests
- [project/research/](../project/research): discovery, search, robustness, promotion, reporting, memory
- [project/contracts/](../project/contracts): stage-family and artifact contracts
- [project/engine/](../project/engine): execution engine and ledger infrastructure
- [project/strategy/](../project/strategy): strategy DSL, templates, and models
- [project/core/](../project/core): foundational classes and shared components
- [project/features/](../project/features): feature engineering and event detector implementations
- [project/events/](../project/events): detector loading, event helpers, runtime event semantics
- [project/runtime/](../project/runtime): replay and runtime invariants
- [project/scripts/](../project/scripts): auxiliary scripts and utilities
- [project/reliability/](../project/reliability): smoke and reliability workflows
- [project/domain/](../project/domain): compiled registry model and loader surfaces
- [project/specs/](../project/specs): code-side accessors for YAML specs like gates

## `spec/`

This is the policy and ontology surface. Important areas:

- [spec/events/](../spec/events): event rows and unified registry
- [spec/templates/](../spec/templates): template compatibility
- [spec/grammar/](../spec/grammar): families, states, stress scenarios, interactions, sequences
- [spec/search_space.yaml](../spec/search_space.yaml): default broad search surface
- [spec/gates.yaml](../spec/gates.yaml): phase-2, bridge, and fallback gate policies

## `data/`

Key subtrees:

- `data/lake/raw/...`: raw ingested market data
- `data/runs/<run_id>/`: stage logs and manifests for a run
- `data/reports/<...>/<run_id>/`: stage outputs and summaries
- `data/reports/phase2/<run_id>/search_engine/`: search outputs
- `data/reports/edge_candidates/<run_id>/`: edge export outputs

## Ownership Boundaries

Use these boundaries when debugging:

- orchestration bug: start in [project/pipelines/](../project/pipelines)
- artifact contract mismatch: start in [project/contracts/](../project/contracts)
- detector semantics issue: start in [project/features/](../project/features) and [spec/events/](../spec/events)
- search/robustness/gating issue: start in [project/research/](../project/research) and [spec/gates.yaml](../spec/gates.yaml)

## Highest-Value Files

If you only have time to learn ten files, start with:

- [project/pipelines/run_all.py](../project/pipelines/run_all.py)
- [project/contracts/pipeline_registry.py](../project/contracts/pipeline_registry.py)
- [project/research/phase2_search_engine.py](../project/research/phase2_search_engine.py)
- [project/research/bridge_evaluate_phase2.py](../project/research/bridge_evaluate_phase2.py)
- [project/research/analyze_events.py](../project/research/analyze_events.py)
- [project/features/](../project/features)
- [project/research/knowledge/query.py](../project/research/knowledge/query.py)
- [project/research/agent_io/execute_proposal.py](../project/research/agent_io/execute_proposal.py)
- [spec/events/event_registry_unified.yaml](../spec/events/event_registry_unified.yaml)
- [spec/gates.yaml](../spec/gates.yaml)
