# Edge

Edge is an event-driven trading research and backtest repository for crypto markets. The current canonical research path is:

`ingest -> clean -> features -> context -> event analysis -> phase2 discovery -> promotion -> strategy packaging`

## Canonical Surfaces

The repo is centered on a small set of maintained public surfaces:

- `project/pipelines/run_all.py` for end-to-end orchestration
- `project/contracts/pipeline_registry.py` for stage and artifact contracts
- `project/research/services/` for typed discovery, promotion, reporting, and comparison workflows
- `project/events/detectors/catalog.py` and `project/events/detectors/registry.py` for detector loading
- `project/strategy/dsl`, `project/strategy/templates`, and `project/strategy/runtime` for public strategy surfaces
- `project/reliability/cli_smoke.py` for deterministic smoke workflows

Compatibility packages such as `project.research.compat`, `project.strategy_dsl`, and `project.strategy_templates` are removed surfaces and should not be reintroduced in new docs or code.

## Install

Base install:

```bash
pip install -e .
```

Optional Nautilus support:

```bash
pip install -e ".[nautilus]"
```

## Common Commands

Plan or run the full pipeline:

```bash
edge-run-all --run_id demo_run --symbols BTCUSDT --start 2024-01-01 --end 2024-01-31 --plan_only 1
```

Run a fast local test profile:

```bash
make test-fast
```

Run a deterministic smoke workflow:

```bash
edge-smoke --mode research
```

Run targeted event discovery:

```bash
make discover-target SYMBOLS=BTCUSDT EVENT=VOL_SHOCK
```

Run broad phase-2 discovery:

```bash
make discover-edges
```

Run the golden synthetic discovery workflow:

```bash
python3 -m project.scripts.run_golden_synthetic_discovery
```

Generate a curated synthetic dataset suite:

```bash
python3 -m project.scripts.generate_synthetic_crypto_regimes \
  --suite_config project/configs/synthetic_dataset_suite.yaml \
  --run_id synthetic_suite
```

Validate detector outputs against the synthetic truth map:

```bash
python3 -m project.scripts.validate_synthetic_detector_truth \
  --run_id golden_synthetic_discovery
```

Regenerate machine-owned architecture artifacts:

```bash
scripts/regenerate_artifacts.sh
```

Inspect or launch the live engine:

```bash
edge-live-engine --config project/configs/golden_certification.yaml --print_session_metadata
edge-live-engine --config project/configs/golden_certification.yaml --snapshot_path artifacts/live_state.json
```

Systemd templates live under `deploy/systemd/`, with environment templates under `deploy/env/`.

## Repository Layout

- `project/`: application code
- `docs/`: maintained reference documentation and generated diagnostics
- `spec/`: ontology, runtime, search, and strategy specs
- `tests/`: regression, contract, smoke, and architecture coverage
- `scripts/`: helper scripts for artifact regeneration, audits, and operations
- `data/`: local run outputs when using the default data root

## Documentation Sets

The repo docs are organized by operating task, not only by file name.

Start with:

- [CLAUDE.md](CLAUDE.md): repo-specific operating guide for external controllers
- [docs/README.md](docs/README.md): workflow-first map of the maintained docs set

Use these sets depending on the question:

- Operator and policy:
  [docs/RESEARCH_OPERATOR_PLAYBOOK.md](docs/RESEARCH_OPERATOR_PLAYBOOK.md),
  [docs/AUTONOMOUS_RESEARCH_LOOP.md](docs/AUTONOMOUS_RESEARCH_LOOP.md),
  [docs/OPERATIONS_AND_GUARDRAILS.md](docs/OPERATIONS_AND_GUARDRAILS.md)
- Experiment design and evaluation:
  [docs/EXPERIMENT_PROTOCOL.md](docs/EXPERIMENT_PROTOCOL.md),
  [docs/ARTIFACTS_AND_CONTRACTS.md](docs/ARTIFACTS_AND_CONTRACTS.md),
  [docs/RESEARCH_WORKFLOW_EXAMPLE.md](docs/RESEARCH_WORKFLOW_EXAMPLE.md)
- Synthetic calibration:
  [docs/SYNTHETIC_DATASETS.md](docs/SYNTHETIC_DATASETS.md),
  [docs/RESEARCH_CALIBRATION_BASELINE.md](docs/RESEARCH_CALIBRATION_BASELINE.md)
- Benchmark and certification:
  [docs/BENCHMARK_STATUS.md](docs/BENCHMARK_STATUS.md),
  [docs/BENCHMARK_GOVERNANCE_RUNBOOK.md](docs/BENCHMARK_GOVERNANCE_RUNBOOK.md),
  [docs/BENCHMARK_TRIAGE.md](docs/BENCHMARK_TRIAGE.md)
- Reference and architecture:
  [docs/FAMILIES_TEMPLATES_AND_REGIMES.md](docs/FAMILIES_TEMPLATES_AND_REGIMES.md),
  [docs/FEATURE_CATALOG.md](docs/FEATURE_CATALOG.md),
  [docs/ARCHITECTURE_SURFACE_INVENTORY.md](docs/ARCHITECTURE_SURFACE_INVENTORY.md),
  [docs/ARCHITECTURE_MAINTENANCE_CHECKLIST.md](docs/ARCHITECTURE_MAINTENANCE_CHECKLIST.md)

Interpretation rules:

- `docs/generated/` is machine-owned evidence. Do not hand-edit it.
- `docs/plans/` and `docs/superpowers/plans/` are planning history, not current policy.
- Use `docs/README.md` as the maintained map when adding or updating docs.

## Agent Quickstart

The shortest safe path for an external research controller is:

1. inspect static knobs and prior memory
2. translate a compact proposal into repo-native config
3. issue a narrow `plan_only` run before any material execution

Examples:

```bash
.venv/bin/python -m project.research.knowledge.query knobs
.venv/bin/python -m project.research.knowledge.query memory --program_id btc_campaign
.venv/bin/python -m project.research.agent_io.issue_proposal \
  --proposal /abs/path/to/proposal.yaml \
  --registry_root project/configs/registries \
  --plan_only 1
```

Use [CLAUDE.md](CLAUDE.md) for the full repo-specific operating guide.
