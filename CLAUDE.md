# Edge

Governed event-driven crypto research engine. Proposal → plan → run → artifacts → diagnosis → hypothesis → next proposal.

## Commands

```bash
# Setup
pip install -e .                    # editable install, requires Python 3.11+

# Test
make test-fast                      # fast tests (no slow markers), fail-fast
make test                           # full test suite
make minimum-green-gate             # compile + arch tests + lint + smoke (required baseline)

# Lint / Format (changed files only, vs origin/main)
make lint                           # ruff check
make format                         # ruff format in-place
make style                          # lint + format-check

# Research proposal lifecycle
.venv/bin/python -m project.research.agent_io.proposal_to_experiment \
  --proposal <path>.yaml --registry_root project/configs/registries \
  --config_path /tmp/experiment.yaml --overrides_path /tmp/overrides.json
.venv/bin/python -m project.research.agent_io.execute_proposal \
  --proposal <path>.yaml --run_id <id> --registry_root project/configs/registries \
  --out_dir <out> --plan_only 1                          # plan only
.venv/bin/python -m project.research.agent_io.issue_proposal \
  --proposal <path>.yaml --registry_root project/configs/registries \
  --run_id <id> --plan_only 0                            # execute

# Discovery
make discover-target SYMBOLS=BTCUSDT EVENT=VOL_SHOCK     # single-event targeted
make discover-edges                                       # full phase2 all events
make discover-blueprints                                  # full pipeline + strategy

# Artifact inspection
.venv/bin/python -c "import pandas as pd; df = pd.read_parquet('data/reports/phase2/<run_id>/phase2_candidates.parquet'); print(len(df)); print(df[['event_type','template_verb','horizon','direction','effect_raw','p_value','q_value','selection_score','fail_gate_primary']].head(10))"
cat data/runs/<run_id>/run_manifest.json | python -m json.tool
cat data/reports/phase2/<run_id>/phase2_diagnostics.json | python -m json.tool
```

## Architecture

```
project/           Python implementation (the package)
  research/         Phase2 search engine, gating, promotion, agent_io
  pipelines/        run_all orchestrator, stage execution
  contracts/        Pipeline registry, schemas (FORBIDDEN to edit without approval)
  domain/           Hypotheses, compiled_registry
  engine/           Execution engine schema (FORBIDDEN)
  core/             Constants, timeframes, horizon parsing
  strategy/         DSL, models, blueprints (schema files FORBIDDEN)
spec/              YAML domain specs (source of truth)
  events/           ~70 event definitions, _families.yaml, regime_routing.yaml
  templates/        event_template_registry.yaml (template-to-family mapping)
  proposals/        Proposal YAML files
  gates.yaml        Gate policy for phase2, bridge, promotion
data/              Runtime artifacts (gitignored)
  runs/<run_id>/    Run manifests, stage manifests
  reports/phase2/   phase2_candidates.parquet, phase2_diagnostics.json
  reports/promotions/
  artifacts/experiments/  Program memory, proposal copies
agents/            Specialist agent specs (analyst, mechanism_hypothesis, compiler)
docs/              Extensive documentation (00-15 numbered guides)
```

## Forbidden Files

Do NOT edit without explicit human approval:
- `spec/events/event_registry_unified.yaml`
- `spec/events/regime_routing.yaml`
- `project/contracts/pipeline_registry.py`
- `project/contracts/schemas.py`
- `project/engine/schema.py`
- `project/research/experiment_engine_schema.py`
- `project/strategy/dsl/schema.py`
- `project/strategy/models/executable_strategy_spec.py`

Do NOT add new events, regimes, templates, detectors, or states during routine research.
Do NOT relax promotion thresholds or cost assumptions.

## Research Workflow

One regime-scoped experiment at a time. Workflow:
1. Write proposal YAML (`spec/proposals/`)
2. Translate: `proposal_to_experiment`
3. Plan: `execute_proposal --plan_only 1`
4. Execute: `issue_proposal --plan_only 0`
5. Inspect: `run_manifest.json`, `phase2_diagnostics.json`, `phase2_candidates.parquet`
6. Decide: keep / modify / kill

Bounded hypothesis must state exactly one: regime, mechanism, trigger family, template family,
symbol set, timeframe, date window, horizon set, direction set, entry-lag set, success test, kill condition.

See `docs/AGENT_CONTRACT.md` for the full operating contract.

## Scope Discipline

Never silently widen symbols, dates, templates, trigger families, horizons, or conditioning axes.
If candidates are empty, inspect upstream `evaluated_hypotheses` and `gate_failures` before proposing changes.
Any major hypothesis rewrite after validation must become a new version, not an in-place edit.

## Specialist Agents

See `agents/coordinator_playbook.md` for the full pipeline.
- `agents/analyst.md` — diagnose completed runs
- `agents/mechanism_hypothesis.md` — formulate bounded hypotheses
- `agents/compiler.md` — compile proposals with validation

## Gotchas

- **entry_lags must be >= 1**: enforced in `proposal_schema.py:252` to prevent same-bar entry leakage
- **Horizon mismatch**: Proposals use integer bar counts via `expand_hypotheses` (Path A).
  The search engine's `validate_hypothesis_spec` only accepts 8 time-label strings (Path B).
  Proposal path works, but `72b` would fail if routed through Path B. See `agents/compiler.md`.
- **Horizon authority**: `project/core/constants.py:parse_horizon_bars` (runtime parser, accepts any int).
  `project/research/search/validation.py:VALID_HORIZONS` (generator whitelist, only 8 labels). Proposals bypass the whitelist.
- **Search limits**: `project/configs/registries/search_limits.yaml` — max 1000 hypotheses, 12 events, 6 templates, 5 horizons per run
- **promotion_profile=disabled** means the run is exploratory-only, not valid for the default autonomous loop
- **Ruff lint/format runs on changed files only** (vs `origin/main`), not the whole repo
- **`data/` is gitignored** — all runtime artifacts are local
- **pytest markers**: `slow` (deselect with `-m "not slow"`), `contract`, `audit`
- **Feature schema is v2**: canonical artifacts are `features.perp.v2` and `features.spot.v2`
- **Detector registration is explicit**, not import-side-effect driven
