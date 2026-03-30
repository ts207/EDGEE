# Edge

Edge is a research platform for event-driven alpha discovery in crypto markets.

It is built to test explicit claims under artifact, cost, and promotion discipline. The operating unit is a bounded hypothesis carried through a reproducible pipeline.

## Core Model

Edge turns:

`proposal -> validated experiment config -> planned run -> artifacted execution -> gated promotion decision -> strategy candidate / live runtime input`

The platform is centered on:

- event definitions and ontology mapping
- canonical regimes and template legality
- proposal-driven discovery
- manifest-tracked pipeline execution
- promotion gates before deployment-oriented outputs
- replay, determinism, and artifact reconciliation checks

## Pipeline

The end-to-end orchestrator is `project/pipelines/run_all.py`.

At a high level the run flow is defined in `project/pipelines/stages/`:

1. `ingest` & `core`
   - build cleaned bars
   - build features & market context
   - validate missing data & integrity
2. `runtime_invariants`
   - materializes replay stream
   - causal lane ticks & replay validation
3. `research`
   - phase1 event analysis & correlation
   - phase2 search engine / hypothesis generation
   - edge candidate export & naive entry evaluation
   - promote candidates & negative controls
   - memory update & registry management
   - expectancy trappedness checklist
4. `evaluation`
   - strategy blueprint compilation
   - strategy candidate packaging
   - profitable strategy selection

The source of truth for stage families and artifact contracts is `project/contracts/pipeline_registry.py`.

## Repo Layout

There are three different configuration layers:

- `spec/` — YAML domain specs: events, ontology, grammar, objectives, search, runtime, templates, benchmarks, proposals
- `project/configs/` — runnable workflow configs, live configs, synthetic suites, registry defaults, retail profiles
- `project/` — Python implementation

High-value code surfaces:

- `project/pipelines/` — pipeline entry points and orchestration
- `project/research/` — proposal I/O, discovery, promotion, diagnostics, knowledge memory
- `project/events/` — detectors, families, registries, ontology helpers
- `project/strategy/` — DSL, template compatibility, executable strategy models
- `project/live/` and `project/scripts/run_live_engine.py` — live runtime support
- `project/reliability/` — smoke workflows, regression assertions, artifact validation
- `project/contracts/` — stage families, artifact token contracts, schemas
- `project/tests/` — architecture, smoke, contracts, regressions, replay, runtime, docs, domain, strategy, synthetic truth

## Command Surface

Installed console scripts from `pyproject.toml`:

- `edge-run-all`
- `edge-backtest` (alias `backtest`)
- `edge-live-engine`
- `edge-phase2-discovery`
- `edge-promote`
- `edge-smoke`
- `compile-strategy-blueprints`
- `build-strategy-candidates`
- `ontology-consistency-audit`

Maintained `make` targets:

- `make discover-target EVENT=<EVENT> SYMBOLS=<SYMBOLS>`
- `make discover-edges`
- `make discover-blueprints`
- `make run`
- `make baseline`
- `make golden-workflow`
- `make golden-certification`
- `make benchmark-maintenance-smoke`
- `make benchmark-maintenance`
- `make minimum-green-gate`
- `make test`
- `make test-fast`
- `make lint`
- `make format-check`

## Quality Model

A run is only trustworthy when:

- manifests reconcile
- artifacts exist and validate
- costs are accounted for
- promotion evidence is explicit
- drift checks stay within tolerance
- replay / determinism expectations remain intact

Exit status alone is not sufficient.

## Generated Artifacts

Do not treat hand-authored docs as live inventory.

Use `docs/generated/` for current generated surfaces:

- `detector_coverage.{md,json}`
- `ontology_audit.json`
- `event_ontology_audit.{md,json}`
- `regime_routing_audit.{md,json}`
- `architecture_metrics.json`

## Documentation

- [docs/README.md](docs/README.md) — full doc index
- [docs/03_OPERATOR_WORKFLOW.md](docs/03_OPERATOR_WORKFLOW.md) — canonical research loop
- [docs/04_COMMANDS_AND_ENTRY_POINTS.md](docs/04_COMMANDS_AND_ENTRY_POINTS.md) — command reference
- [docs/06_QUALITY_GATES_AND_PROMOTION.md](docs/06_QUALITY_GATES_AND_PROMOTION.md) — gate policy
- [docs/08_TESTING_AND_MAINTENANCE.md](docs/08_TESTING_AND_MAINTENANCE.md) — test and maintenance commands
- [docs/AGENT_CONTRACT.md](docs/AGENT_CONTRACT.md) — agent operating contract
