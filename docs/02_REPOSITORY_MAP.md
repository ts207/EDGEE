# Repository map

This document explains the top-level repo shape and the ownership of the major implementation surfaces.

## Top-level layout

### `project/`

Python implementation.

Key subtrees:

- `project/apps/` — ChatGPT app scaffold and related handlers
- `project/configs/` — runnable configs, registries, venue config, synthetic overlays
- `project/contracts/` — stage-family and artifact contracts, system-map support
- `project/domain/` — compiled registry/domain models
- `project/events/` — event contracts, canonicalization, detector support, ontology helpers
- `project/live/` — thesis retrieval, context building, policy, decisioning, OMS, replay, runtime state
- `project/operator/` — preflight, proposal explain/lint, bounded validation, campaign engine, review reports
- `project/pipelines/` — run orchestration, planning, execution, stage wrappers
- `project/portfolio/` — overlap-aware portfolio and sizing support
- `project/research/` — search, promotion, reporting, knowledge, packaging, candidate services
- `project/scripts/` — generated-doc builders, audits, bootstrap utilities, verification helpers
- `project/tests/` — contract, architecture, runtime, research, pipeline, docs, and strategy tests

### `spec/`

Authored specs and policy inputs.

Notable areas:

- `spec/events/` — event contracts and registry inputs
- `spec/episodes/` — episode contracts and registry
- `spec/promotion/` — bootstrap and founding-thesis policies
- `spec/search/` and `spec/search_space.yaml` — search surfaces and search profiles
- `spec/runtime/` — runtime/lane/firewall configuration
- `spec/concepts/` — concept-level documentation and discovery references
- `spec/templates/`, `spec/theses/`, `spec/regimes/`, `spec/states/` — authored domain surfaces

### `docs/`

Human docs plus generated inventories.

- `docs/*.md` — canonical narrative docs and maintenance references
- `docs/generated/` — generated inventories and artifact summaries
- `docs/templates/` — operator templates
- `docs/research/` — non-canonical research notes

### `data/`

Data roots and runtime/report artifacts.

Important patterns:

- `data/lake/` — raw and prepared datasets
- `data/runs/<run_id>/run_manifest.json` — run manifest and run-scoped artifacts
- `data/reports/` — phase2, promotions, operator, shadow-live, benchmark, and related reports
- `data/live/theses/` — packaged thesis store

### `deploy/`

Systemd units and env examples for live engine deployment.

### `agents/`

Human-readable analyst/compiler/coordinator playbooks and templates.

### `plugins/`

Repo-local plugin surfaces and helper scripts.

## Subsystem ownership

### Operator surface

Owned primarily by:

- `project.cli`
- `project.operator.preflight`
- `project.operator.proposal_tools`
- `project.operator.stability`
- `project.operator.campaign_engine`

This is the front door for bounded work.

### Pipeline orchestration

Owned primarily by:

- `project.pipelines.run_all`
- `project.pipelines.pipeline_planning`
- `project.pipelines.pipeline_execution`
- `project.pipelines.stage_registry`
- `project.pipelines.stages.*`

This is the coordinator layer. It should remain coordination-heavy, not policy-heavy.

### Discovery and promotion

Owned primarily by:

- `project.research.services.candidate_discovery_service`
- `project.research.services.promotion_service`
- `project.research.services.reporting_service`
- `project.research.agent_io.*`

The canonical planner-owned discovery stage is `project/research/phase2_search_engine.py`, surfaced through the service layer and stage registry. `phase2_candidate_discovery.py` exists only as a compatibility wrapper and is not the canonical planner-owned discovery stage.

### Event and domain model

Owned primarily by:

- `project/events/`
- `project/domain/`
- `project/spec_registry/`
- `project/episodes/`

These surfaces define what events, states, templates, regimes, and theses mean.

### Runtime and portfolio

Owned primarily by:

- `project/live/retriever.py`
- `project/live/context_builder.py`
- `project/live/decision.py`
- `project/live/thesis_store.py`
- `project/portfolio/thesis_overlap.py`
- `project/portfolio/risk_budget.py`

These surfaces consume packaged theses, not raw run notes.

## Directory-to-question mapping

Use this shortcut when navigating.

- “What does the repo know how to talk about?” -> `spec/`, `project/domain/`, `project/events/`
- “How does a proposal become a run?” -> `project/research/agent_io/`, `project/operator/`, `project/cli.py`
- “How does the DAG get built and executed?” -> `project/pipelines/`
- “How are candidates scored and promoted?” -> `project/research/services/`
- “How is packaging done?” -> `project/scripts/build_*`, `project/research/*bootstrap*`, `project/research/live_export.py`
- “What does live/runtime consume?” -> `project/live/`, `project/portfolio/`, `data/live/theses/`
- “What guards the repo shape?” -> `project/tests/`, `docs/VERIFICATION.md`, `docs/generated/system_map.md`

## Generated versus authored surfaces

Some paths are generated outputs rather than authored source.

Generated or derived surfaces include:

- `docs/generated/*`
- many files under `data/reports/*`
- the packaged thesis store under `data/live/theses/*`
- run manifests under `data/runs/*`

Authored source of truth usually lives in:

- `project/`
- `spec/`
- `project/configs/`
- a small number of maintenance docs under `docs/`

## Navigation rule

When tracing behavior, follow this order:

1. operator or CLI entrypoint
2. service or orchestration module
3. stage or helper implementation
4. generated output or report

That keeps you on the execution path instead of getting lost in inventories.
