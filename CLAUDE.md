# Edge

Governed event-driven crypto research engine.

Current end-to-end path:

`single hypothesis proposal -> explain -> preflight -> plan -> run -> review -> export thesis batch -> explicit runtime selection`

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

# Canonical operator workflow
make discover PROPOSAL=<path>.yaml DISCOVER_ACTION=preflight
make discover PROPOSAL=<path>.yaml DISCOVER_ACTION=plan
make discover PROPOSAL=<path>.yaml DISCOVER_ACTION=run
make review RUN_ID=<run_id> REVIEW_ACTION=diagnose
make review RUN_ID=<run_id> REVIEW_ACTION=regime-report
make review REVIEW_ACTION=compare RUN_IDS=<baseline_run,followup_run>
make export RUN_ID=<run_id>
make validate

edge operator explain --proposal <path>.yaml
edge operator preflight --proposal <path>.yaml
edge operator plan --proposal <path>.yaml
edge operator run --proposal <path>.yaml
edge operator diagnose --run_id <run_id>
edge operator regime-report --run_id <run_id>
edge operator compare --run_ids <baseline_run,followup_run>

# Compatibility / low-level proposal surfaces
.venv/bin/python -m project.research.agent_io.proposal_to_experiment --proposal <path>.yaml --registry_root project/configs/registries --config_path /tmp/experiment.yaml --overrides_path /tmp/overrides.json
.venv/bin/python -m project.research.agent_io.execute_proposal --proposal <path>.yaml --run_id <id> --registry_root project/configs/registries --out_dir <out> --plan_only 1
.venv/bin/python -m project.research.agent_io.issue_proposal --proposal <path>.yaml --registry_root project/configs/registries --run_id <id> --plan_only 0

# Discovery
make discover-target SYMBOLS=BTCUSDT EVENT=VOL_SHOCK     # single-event targeted
make discover-edges                                       # full phase2 all events
make discover-blueprints                                  # full pipeline + strategy

# Canonical thesis export
python -m project.research.export_promoted_theses --run_id <run_id>

# Advanced bootstrap and packaging
python -m project.scripts.build_seed_bootstrap_artifacts
python -m project.scripts.build_seed_testing_artifacts
python -m project.scripts.build_seed_empirical_artifacts
python -m project.scripts.build_founding_thesis_evidence
python -m project.scripts.build_seed_packaging_artifacts
python -m project.scripts.build_structural_confirmation_artifacts
python -m project.scripts.build_thesis_overlap_artifacts --run_id <run_id>
./project/scripts/regenerate_artifacts.sh

# Artifact inspection
.venv/bin/python -c "import pandas as pd; df = pd.read_parquet('data/reports/phase2/<run_id>/phase2_candidates.parquet'); print(len(df)); print(df[['event_type','template_verb','horizon','direction','effect_raw','p_value','q_value','selection_score','fail_gate_primary']].head(10))"
cat data/runs/<run_id>/run_manifest.json | python -m json.tool
cat data/reports/phase2/<run_id>/phase2_diagnostics.json | python -m json.tool
```

## Architecture

```
project/           Python implementation (the package)
  research/         Phase2 search engine, gating, promotion, bootstrap, packaging
  episodes/         Episode registry / contract loading
  pipelines/        run_all orchestrator, stage execution
  contracts/        Pipeline registry, schemas (FORBIDDEN to edit without approval)
  engine/           Execution engine schema (FORBIDDEN)
  live/             Thesis retrieval, decisioning, OMS, attribution
  portfolio/        Overlap graph and thesis-aware budget helpers
  core/             Constants, timeframes, horizon parsing
  strategy/         DSL, models, blueprints (schema files FORBIDDEN)
spec/              YAML domain specs (source of truth)
  events/           authoritative event definitions and registry
  episodes/         episode contract and registry
  campaigns/        canonical campaign contract
  promotion/        seed and founding-thesis policies
  proposals/        Proposal YAML files
data/              Runtime artifacts (gitignored)
  runs/<run_id>/    Run manifests, stage manifests
  reports/phase2/   phase2_candidates.parquet, phase2_diagnostics.json
  reports/promotions/
  live/theses/      canonical packaged thesis store
  artifacts/experiments/  Program memory, proposal copies
agents/            Specialist agent specs (analyst, mechanism_hypothesis, compiler)
docs/              Extensive documentation (00-15 numbered guides)
```

## Current thesis lifecycle

Treat evidence state and runtime permission as separate:

- internal promotion ladder: `candidate -> tested -> seed_promoted -> paper_promoted -> production_promoted`
- operator-facing permission: `monitor_only | paper_only | live_enabled`

Important:
- runtime should consume one explicit run-derived thesis batch
- `deployment_state` is the first field to inspect for runtime permission
- `live_enabled` is the only state that may reach trading runtime

## Forbidden files

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
Do NOT treat derived confirmation support as equivalent to direct paired-event evidence.

## Research workflow

One regime-scoped experiment at a time. Workflow:
1. Write proposal YAML (`spec/proposals/`)
2. Inspect normalization: `edge operator explain --proposal <path>`
3. Preflight and plan: `edge operator preflight|plan --proposal <path>`
4. Execute: `edge operator run --proposal <path>`
5. Inspect: `run_manifest.json`, `phase2_diagnostics.json`, `phase2_candidates.parquet`, promotion outputs
6. Decide: repair / confirm / kill / export
7. Export explicit runtime input: `python -m project.research.export_promoted_theses --run_id <run_id>`
8. Use the bootstrap lane only for broader packaging maintenance, not as the default runtime path

See `docs/AGENT_CONTRACT.md` for the full operating contract.

## Scope discipline

Never silently widen symbols, dates, templates, trigger families, horizons, or conditioning axes.
If candidates are empty, inspect upstream `evaluated_hypotheses` and `gate_failures` before proposing changes.
Any major hypothesis rewrite after validation must become a new version, not an in-place edit.

## Specialist agents

See `agents/coordinator_playbook.md` for the full pipeline.
- `agents/analyst.md` — diagnose completed runs
- `agents/mechanism_hypothesis.md` — formulate bounded hypotheses
- `agents/compiler.md` — compile proposals with validation

## Gotchas

- **entry_lags must be >= 1**: enforced in `proposal_schema.py:252` to prevent same-bar entry leakage
- **operator proposals are now single-hypothesis front-door YAML**: they normalize through `load_operator_proposal(...)` into legacy `AgentProposal`
- **Horizon mismatch**: Proposals use integer bar counts via `expand_hypotheses` (Path A).
  The search engine's `validate_hypothesis_spec` only accepts 8 time-label strings (Path B).
  Proposal path works, but `72b` would fail if routed through Path B. See `agents/compiler.md`.
- **Horizon authority**: `project/core/constants.py:parse_horizon_bars` (runtime parser, accepts any int).
  `project/research/search/validation.py:VALID_HORIZONS` (generator whitelist, only 8 labels). Proposals bypass the whitelist.
- **Search limits**: `project/configs/registries/search_limits.yaml` — max 1000 hypotheses, 12 events, 6 templates, 5 horizons per run
- **promotion_profile=disabled** means the run is exploratory-only, not valid for the default autonomous loop
- **export is the canonical runtime bridge**: use explicit run export before any advanced bootstrap maintenance
- **bootstrap artifacts are advanced packaging surfaces**: use them for maintenance, not as the default way to answer “what will runtime consume?”
- **Ruff lint/format runs on changed files only** (vs `origin/main`), not the whole repo
- **`data/` is gitignored** — all runtime artifacts are local
- **pytest markers**: `slow` (deselect with `-m "not slow"`), `contract`, `audit`
- **Feature schema is v2**: canonical artifacts are `features.perp.v2` and `features.spot.v2`
- **Detector registration is explicit**, not import-side-effect driven
