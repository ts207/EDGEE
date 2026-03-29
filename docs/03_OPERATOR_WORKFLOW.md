# Operator Workflow

The repository is designed for disciplined research loops, not ad hoc command execution.

Canonical loop:

`observe -> retrieve memory -> define objective -> propose -> plan -> execute -> evaluate -> reflect -> adapt`

## Preferred Workflow

### 1. Query knowledge first

Use maintained knowledge surfaces before creating a new run:

```bash
.venv/bin/python -m project.research.knowledge.query knobs
.venv/bin/python -m project.research.knowledge.query memory --program_id btc_campaign
.venv/bin/python -m project.research.knowledge.query static --event VOL_SHOCK
```

This tells you:

- current knobs
- prior campaign memory
- static event information

### 2. Translate proposal to repo-native config

```bash
.venv/bin/python -m project.research.agent_io.proposal_to_experiment \
  --proposal /abs/path/to/proposal.yaml \
  --registry_root project/configs/registries \
  --config_path /tmp/experiment.yaml \
  --overrides_path /tmp/run_all_overrides.json
```

Use this when you want to inspect the exact config that a proposal becomes.

### 3. Plan before execution

```bash
.venv/bin/python -m project.research.agent_io.execute_proposal \
  --proposal /abs/path/to/proposal.yaml \
  --run_id btc_vol_shock_probe \
  --registry_root project/configs/registries \
  --out_dir data/artifacts/experiments/btc_campaign/proposals/btc_vol_shock_probe \
  --plan_only 1
```

This is the default safe mode. Read the plan. Confirm the date range, symbols, trigger scope, search surface, and output locations.

### 4. Execute one bounded run

Only after the plan looks right, execute.

Good run shape:

- one symbol or very small symbol set
- one timeframe
- one event or one narrow family
- one main template family
- one bounded date range

### 5. Evaluate the run on three layers

Every meaningful run needs:

1. mechanical conclusion
2. statistical conclusion
3. deployment conclusion

Do not collapse these into a single yes/no answer.

## Direct CLI Workflow

If you are not using the proposal layer, [project/pipelines/run_all.py](/home/irene/Edge/project/pipelines/run_all.py) is the end-to-end orchestrator.

Useful direct controls from `run_all --help`:

- `--symbols`
- `--start`
- `--end`
- `--mode {research,production,certification}`
- `--phase2_event_type`
- `--templates`
- `--horizons`
- `--directions`
- `--contexts`
- `--phase2_gate_profile`
- `--search_spec`

Use direct CLI only when you already know the exact bounded slice you want.

## Synthetic Workflow

Synthetic data is for:

- detector truth recovery
- infrastructure validation
- negative controls
- stress calibration

It is not direct evidence of live tradability.

Maintained synthetic commands:

```bash
python3 -m project.scripts.generate_synthetic_crypto_regimes \
  --suite_config project/configs/synthetic_dataset_suite.yaml \
  --run_id synthetic_suite
python3 -m project.scripts.run_golden_synthetic_discovery
python3 -m project.scripts.run_fast_synthetic_certification
python3 -m project.scripts.validate_synthetic_detector_truth \
  --run_id golden_synthetic_discovery
```

## Stop Conditions

Stop broadening a run when any of these becomes true:

- you cannot describe the claim in one sentence
- unrelated triggers are entering the same search surface
- the artifacts no longer support narrow attribution
- you are rerunning without changing the actual question

When that happens, split the work into smaller runs instead of adding more knobs.
