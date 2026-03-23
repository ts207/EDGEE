# Developer Onboarding

This repo is organized around explicit contracts between pipelines, research services, promotion, portfolio, and live execution. When you change one surface, expect at least one consumer on another surface to need an update.

## Repo layout

- `project/pipelines/` - stage entrypoints, research orchestration, maintenance scripts
- `project/research/` - discovery, evaluation, promotion, clustering, knowledge, services
- `project/contracts/` - stage DAGs, artifact schemas, temporal and system contracts
- `project/live/` - live runner, OMS, kill switch, drift, health checks
- `project/portfolio/` - sizing, allocation, and risk budget
- `spec/` - search space, ontology, hypotheses, objectives, and registries
- `docs/` - maintained operating docs and the cross-role audit

## Install

```bash
pip install -e .
pip install -e ".[dev]"
```

With Nautilus Trader support:

```bash
pip install -e ".[nautilus]"
```

## Common build commands

```bash
make test
make test-fast
make lint
make format-check
make format
python3 -m project.scripts.build_system_map --check
python3 -m project.scripts.ontology_consistency_audit
```

## CLI entry points that matter

- `edge-run-all`
- `edge-phase2-discovery`
- `edge-promote`
- `compile-strategy-blueprints`
- `edge-live-engine`
- `edge-smoke`

## Change discipline

1. Update the code.
2. Update the tests.
3. Update any schema or contract file.
4. Update the relevant docs.
5. Run the smallest targeted verification first, then broader checks.

A change is not done if only the happy path works.

## What to inspect before editing research logic

- `project/contracts/`
- `project/research/knowledge/`
- `project/research/services/`
- `project/pipelines/research/`
- `spec/search_space.yaml`
- `spec/ontology/`
- `project/live/` if the change affects promotion or sizing

## Docs to keep in sync

- `docs/CURRENT_STATE_AND_GAPS.md`
- `docs/researcher/ARTIFACTS_AND_CONTRACTS.md`
- `docs/researcher/MEMORY_AND_REFLECTION.md`
- `docs/developer/ARCHITECTURE.md`

If a feature exists in code but not in docs, add it to the docs before the change settles.
