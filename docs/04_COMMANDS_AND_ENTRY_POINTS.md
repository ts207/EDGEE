# Commands And Entry Points

This file lists the main maintained ways to interact with the repository.

## Console Scripts

Defined in [pyproject.toml](/home/irene/Edge/pyproject.toml):

- `edge-run-all`: full orchestrator
- `edge-live-engine`: live runtime entry point
- `edge-phase2-discovery`: phase-2 discovery entry point
- `edge-promote`: promotion entry point
- `edge-smoke`: smoke workflow
- `compile-strategy-blueprints`
- `build-strategy-candidates`
- `ontology-consistency-audit`

## Main Python Entry Points

- [project/pipelines/run_all.py](/home/irene/Edge/project/pipelines/run_all.py)
- [project/research/agent_io/execute_proposal.py](/home/irene/Edge/project/research/agent_io/execute_proposal.py)
- [project/research/agent_io/issue_proposal.py](/home/irene/Edge/project/research/agent_io/issue_proposal.py)
- [project/research/agent_io/proposal_to_experiment.py](/home/irene/Edge/project/research/agent_io/proposal_to_experiment.py)
- [project/research/knowledge/query.py](/home/irene/Edge/project/research/knowledge/query.py)

## `make` Targets

Maintained targets from `make help`:

- `discover-blueprints`: full research pipeline
- `discover-edges`: phase-2 discovery for all events
- `discover-target`: targeted discovery for specific symbols and events
- `run`: ingest, clean, and feature preparation
- `baseline`: full discovery plus profitable strategy packaging
- `golden-workflow`: canonical end-to-end smoke workflow
- `golden-certification`: golden workflow plus certification manifest
- `test-fast`: fast research test profile
- `lint`
- `format-check`
- `format`
- `style`
- `governance`
- `benchmark-m0`
- `benchmark-maintenance-smoke`
- `benchmark-maintenance`
- `minimum-green-gate`

## Best Usage By Intent

### I want to inspect prior work

Use:

```bash
.venv/bin/python -m project.research.knowledge.query knobs
.venv/bin/python -m project.research.knowledge.query memory --program_id btc_campaign
.venv/bin/python -m project.research.knowledge.query static --event VOL_SHOCK
```

### I want to translate a proposal without executing it

Use:

```bash
.venv/bin/python -m project.research.agent_io.proposal_to_experiment \
  --proposal /abs/path/to/proposal.yaml \
  --registry_root project/configs/registries \
  --config_path /tmp/experiment.yaml \
  --overrides_path /tmp/run_all_overrides.json
```

### I want to inspect a full plan first

Use:

```bash
.venv/bin/python -m project.research.agent_io.execute_proposal \
  --proposal /abs/path/to/proposal.yaml \
  --run_id my_run \
  --registry_root project/configs/registries \
  --out_dir data/artifacts/experiments/my_program/proposals/my_run \
  --plan_only 1
```

### I want memory bookkeeping with proposal issuance

Use:

```bash
.venv/bin/python -m project.research.agent_io.issue_proposal \
  --proposal /abs/path/to/proposal.yaml \
  --registry_root project/configs/registries \
  --plan_only 1
```

### I want a narrow direct run

Use `run_all` directly when you already know the slice:

```bash
.venv/bin/python -m project.pipelines.run_all \
  --run_id btc_vol_shock_slice \
  --symbols BTCUSDT \
  --start 2022-11-01 \
  --end 2022-12-31 \
  --mode research \
  --phase2_event_type VOL_SHOCK \
  --phase2_gate_profile discovery
```

## Command Selection Rule

Prefer:

- `knowledge.query` for reading prior state
- proposal tools for disciplined research issuance
- `run_all` for direct bounded execution
- `make` targets for maintained common workflows

Do not default to ad hoc Python one-offs when a maintained entry point already exists.
