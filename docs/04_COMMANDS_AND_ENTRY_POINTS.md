# Commands and entry points

This document tells you which surface to use for each job.

## Rule of thumb

Prefer the highest-level surface that still does exactly what you need.

Use this order of preference:

1. `make discover|package|validate|review`
2. `edge operator ...`
3. dedicated console scripts such as `edge-run-all`, `edge-phase2-discovery`, `edge-promote`, `edge-live-engine`
4. direct `python -m project.scripts.*` maintenance scripts

## Canonical operator commands

### Bounded discovery and review

```bash
edge operator preflight --proposal <proposal.yaml>
edge operator plan --proposal <proposal.yaml>
edge operator run --proposal <proposal.yaml>
edge operator lint --proposal <proposal.yaml>
edge operator explain --proposal <proposal.yaml>
edge operator diagnose --run_id <run_id>
edge operator regime-report --run_id <run_id>
edge operator compare --run_ids <run_a,run_b>
edge operator campaign start <campaign_spec.yaml> --plan_only 1
```

These are the canonical operator surfaces exposed by `project.cli`.

### Canonical `make` actions

```bash
make discover PROPOSAL=<proposal.yaml> DISCOVER_ACTION=preflight|plan|run
make package
make validate
make review RUN_ID=<run_id> REVIEW_ACTION=diagnose|regime-report
make review REVIEW_ACTION=compare RUN_IDS=<baseline_run,followup_run>
```

These should be the first surfaces taught to a new operator.

## Pipeline entry points

### Full pipeline orchestrator

```bash
edge-run-all --run_id <run_id> --symbols BTCUSDT --start 2025-01-01 --end 2025-01-31
```

Equivalent module surface:

```bash
python -m project.pipelines.run_all ...
```

Use `run_all` when you need direct control over stage flags, configs, or planning behavior beyond the bounded proposal interface.

### Pipeline subcommands exposed through `edge`

```bash
edge pipeline run-all
edge ingest --run_id <run_id> --symbols BTCUSDT --start 2025-01-01 --end 2025-01-31
```

These are lower-level than `edge operator ...`.

## Research and promotion console scripts

The package exposes several stable console scripts through `pyproject.toml`.

Important ones:

```bash
edge-phase2-discovery
edge-promote
compile-strategy-blueprints
build-strategy-candidates
edge-live-engine
edge-chatgpt-app
edge-smoke
backtest
edge-backtest
```

When to use them:

- `edge-phase2-discovery` — direct candidate-discovery control outside the full operator workflow
- `edge-promote` — direct promotion flow control
- `compile-strategy-blueprints` / `build-strategy-candidates` — strategy packaging lane
- `edge-live-engine` — live engine/runtime surface
- `edge-chatgpt-app` — app scaffold inspection and serving
- `edge-smoke` — smoke validation

## Packaging and generated-doc scripts

These scripts live under `project/scripts/` and should be treated as advanced or maintenance entry points.

Primary bootstrap lane:

```bash
python -m project.scripts.build_seed_bootstrap_artifacts
python -m project.scripts.build_seed_testing_artifacts
python -m project.scripts.build_seed_empirical_artifacts
python -m project.scripts.build_founding_thesis_evidence
python -m project.scripts.build_seed_packaging_artifacts
python -m project.scripts.build_structural_confirmation_artifacts
python -m project.scripts.build_thesis_overlap_artifacts
./project/scripts/regenerate_artifacts.sh
```

Verification and governance:

```bash
python -m project.scripts.run_researcher_verification --mode contracts
python -m project.scripts.build_system_map
python -m project.scripts.generate_operator_surface_inventory
```

## Surface selection guide

### You have a proposal and want to know if it is valid

Use:

```bash
edge operator preflight --proposal <proposal.yaml>
```

### You want to see the resolved search surface without committing to a run

Use:

```bash
edge operator explain --proposal <proposal.yaml>
edge operator plan --proposal <proposal.yaml>
```

### You want a durable bounded run

Use:

```bash
edge operator run --proposal <proposal.yaml>
```

or the `make discover` alias.

### You already have a run and want structured review

Use:

```bash
edge operator diagnose --run_id <run_id>
edge operator regime-report --run_id <run_id>
edge operator compare --run_ids <run_a,run_b>
```

### You want to rebuild the packaged thesis store

Use:

```bash
make package
```

### You changed contracts or architecture and want guardrails

Use:

```bash
make validate
python -m project.scripts.run_researcher_verification --mode contracts
```

## Advanced `make` targets

The Makefile also contains advanced bundles such as:

- `discover-target`
- `discover-concept`
- `discover-blueprints`
- `discover-edges`
- `discover-hybrid`
- `baseline`
- `golden-workflow`
- `golden-certification`
- `synthetic-demo`
- `governance`
- `minimum-green-gate`

These are useful, but they are not the primary teaching surface.

## Common misuse to avoid

- Do not teach `run_all` before the proposal path.
- Do not teach individual builder scripts before `make package`.
- Do not treat compatibility wrappers as preferred surfaces.
- Do not jump to live/runtime commands when the thesis store is not understood.
