# Full Project Guide

This document explains the repository as a working system.

It answers five practical questions:

1. what the project is for
2. what the main subsystems are
3. which path is canonical for research
4. where execution and backtest code lives
5. how to use the repository without mixing those layers up

## 1. What This Project Is

This repository is a research system for testing bounded market hypotheses.

The canonical loop is:

`observe -> retrieve memory -> define objective -> propose -> plan -> execute -> evaluate -> reflect -> adapt`

The repository is not primarily a generic backtest sandbox.

The main research path is:

- detect events or trigger conditions
- generate or load bounded hypotheses
- evaluate those hypotheses statistically
- apply multiplicity, robustness, and promotion logic
- write artifacts and memory

Core entrypoints:

- orchestrator: [run_all.py](/home/irene/Edge/project/pipelines/run_all.py)
- proposal execution: [execute_proposal.py](/home/irene/Edge/project/research/agent_io/execute_proposal.py)
- proposal translation: [proposal_to_experiment.py](/home/irene/Edge/project/research/agent_io/proposal_to_experiment.py)
- canonical search stage: [phase2_search_engine.py](/home/irene/Edge/project/research/phase2_search_engine.py)

## 2. System Model

There are four separate layers in the repo.

### A. Data Layer

This is where raw, cleaned, and feature data live.

Main locations:

- raw market data: `data/lake/raw/...`
- run-scoped cleaned bars: `data/lake/runs/<run_id>/cleaned/...`
- run-scoped features: `data/lake/runs/<run_id>/features/...`
- run-scoped metadata: `data/lake/runs/<run_id>/metadata/...`

Main code:

- ingest: [project/pipelines/ingest](/home/irene/Edge/project/pipelines/ingest)
- cleaned bars: [build_cleaned_bars.py](/home/irene/Edge/project/pipelines/clean/build_cleaned_bars.py)
- features: [build_features.py](/home/irene/Edge/project/pipelines/features/build_features.py)

### B. Research Layer

This is the main hypothesis-testing surface.

It owns:

- trigger/event analysis
- hypothesis generation
- hypothesis evaluation
- multiplicity
- promotion and reporting
- campaign memory

Main code:

- research root: [project/research](/home/irene/Edge/project/research)
- evaluator: [evaluator.py](/home/irene/Edge/project/research/search/evaluator.py)
- search feature prep: [search_feature_utils.py](/home/irene/Edge/project/research/search/search_feature_utils.py)
- multiplicity: [multiplicity.py](/home/irene/Edge/project/research/multiplicity.py)
- promotion logic: [project/research/promotion](/home/irene/Edge/project/research/promotion)
- memory: [project/research/knowledge](/home/irene/Edge/project/research/knowledge)

### C. Strategy / DSL Layer

This layer holds the executable strategy representation.

It owns:

- blueprint schema
- blueprint normalization
- DSL interpreter
- runtime-facing strategy logic

Main code:

- DSL schema and normalization: [project/strategy/dsl](/home/irene/Edge/project/strategy/dsl)
- blueprint model facade: [blueprint.py](/home/irene/Edge/project/strategy/models/blueprint.py)
- interpreter facade: [dsl_interpreter_v1.py](/home/irene/Edge/project/strategy/runtime/dsl_interpreter_v1.py)
- interpreter implementation: [interpreter.py](/home/irene/Edge/project/strategy/runtime/dsl_runtime/interpreter.py)
- exits: [exits.py](/home/irene/Edge/project/strategy/runtime/exits.py)

### D. Execution / Engine Layer

This is the actual strategy execution and portfolio ledger layer.

It owns:

- loading bars/features for a run
- generating positions for one or more strategies
- applying execution lag/fill rules
- computing PnL ledger
- portfolio aggregation
- writing execution artifacts

Main code:

- engine runner: [runner.py](/home/irene/Edge/project/engine/runner.py)
- execution ledger: [pnl.py](/home/irene/Edge/project/engine/pnl.py)
- strategy execution: [strategy_executor.py](/home/irene/Edge/project/engine/strategy_executor.py)
- execution costs: [execution_costs.py](/home/irene/Edge/project/core/execution_costs.py)
- runtime/replay: [project/runtime](/home/irene/Edge/project/runtime)

## 3. Canonical Research Path

The canonical research path is the search/evaluation pipeline, not the engine backtest.

Current canonical evaluation path:

1. create or translate a bounded proposal
2. run `run_all`
3. build event registry and feature surface
4. run [phase2_search_engine.py](/home/irene/Edge/project/research/phase2_search_engine.py)
5. evaluate hypotheses in [evaluator.py](/home/irene/Edge/project/research/search/evaluator.py)
6. convert to candidate rows
7. apply multiplicity and bridge/promotion gates
8. write artifacts, reports, and campaign memory

Important fact:

- this path is an event/trigger-conditioned statistical evaluator
- it is not a full execution simulator

What it does:

- resolves trigger hits
- applies entry lag
- measures forward returns at a fixed horizon
- computes statistics
- applies gates

What it does not primarily do:

- simulate a full strategy lifecycle as the core evaluator
- run a portfolio ledger as the core hypothesis test
- perform true validation/test execution as the canonical search mechanism

Main files:

- [phase2_search_engine.py](/home/irene/Edge/project/research/phase2_search_engine.py)
- [evaluator.py](/home/irene/Edge/project/research/search/evaluator.py)
- [evaluator_utils.py](/home/irene/Edge/project/research/search/evaluator_utils.py)

## 4. Backtest / Execution Path

Backtest code does exist in the repo.

It is not the default research path, but it is real and usable.

Main entrypoint:

- [run_engine(...) in runner.py](/home/irene/Edge/project/engine/runner.py)

Example script:

- [run_multi_edge_backtest.py](/home/irene/Edge/project/scripts/run_multi_edge_backtest.py)

What the engine expects:

- a `run_id` with cleaned bars and features already built
- one or more strategies
- strategy params
- for DSL strategies, a blueprint payload under `dsl_blueprint`

What the engine produces:

- strategy return frames
- strategy traces
- portfolio returns
- engine metrics
- engine manifest

Artifacts go under:

- `data/runs/<engine_run_id>/engine/...`

The engine is the place to use when the question is:

- “what happens if I execute this strategy logic over bars?”

The search evaluator is the place to use when the question is:

- “is this bounded hypothesis statistically interesting enough to keep researching?”

## 5. Proposals, Hypotheses, Blueprints, Strategies

These are different things.

### Proposal

A compact operator input that defines a bounded research run.

Main schema:

- [proposal_schema.py](/home/irene/Edge/project/research/agent_io/proposal_schema.py)

### Hypothesis

A single explicit claim evaluated by the search engine.

Main schema:

- [hypotheses.py](/home/irene/Edge/project/domain/hypotheses.py)

### Blueprint

An executable strategy specification used by the DSL/runtime layer.

Main surface:

- [project/strategy/dsl](/home/irene/Edge/project/strategy/dsl)

### Strategy

A runtime object the engine can execute.

Examples:

- DSL interpreter strategy
- non-DSL strategies registered in runtime/strategy surfaces

## 6. Trigger Model

Supported trigger types are documented in:

- [13_TRIGGER_TYPES.md](/home/irene/Edge/docs/13_TRIGGER_TYPES.md)

Supported trigger classes:

- `EVENT`
- `STATE`
- `TRANSITION`
- `FEATURE_PREDICATE`
- `SEQUENCE`
- `INTERACTION`

The canonical research path resolves these into boolean trigger masks over the feature table.

Main code:

- [evaluator_utils.py](/home/irene/Edge/project/research/search/evaluator_utils.py)

## 7. Event Families

Event families are defined in:

- [event_registry_unified.yaml](/home/irene/Edge/spec/events/event_registry_unified.yaml)

Examples:

- `BASIS_FUNDING_DISLOCATION`
- `LIQUIDATION_CASCADE`
- `TREND_CONTINUATION`
- `VOLATILITY_EXPANSION`

The operator policy is to keep runs narrow:

- one event family or narrow trigger set
- one template family
- one bounded date range

## 8. Objectives, Profiles, and Gates

### Objective

The objective defines what success means.

Built-in objective:

- [retail_profitability.yaml](/home/irene/Edge/spec/objectives/retail_profitability.yaml)

### Profiles

The repo uses multiple profile families.

Common ones:

- proposal `promotion_profile`
- pipeline `candidate_promotion_profile`
- execution `retail_profile`

These are different policy surfaces. They are not interchangeable.

### Gates

Gate policy comes from:

- [gates.yaml](/home/irene/Edge/spec/gates.yaml)

Important gate categories:

- sample size
- q-value / multiplicity
- stability
- cost survival
- negative controls
- bridge/promotion viability

## 9. Artifacts

Artifacts are the source of truth.

Read in this order:

1. top-level run manifest
2. stage manifests
3. stage logs
4. reports
5. diagnostics

Important outputs:

- run manifest: `data/runs/<run_id>/run_manifest.json`
- stage artifacts under `data/runs/<run_id>/...`
- reports under `data/reports/...`
- experiment memory under `data/artifacts/experiments/...`

Core contract source:

- [pipeline_registry.py](/home/irene/Edge/project/contracts/pipeline_registry.py)

## 10. When To Use Which Path

### Use the research path when:

- you are testing a bounded claim
- you want event-conditioned expectancy/statistical evidence
- you want campaign memory and promotion-style artifacts
- you are still deciding whether a setup is worth deeper work

### Use the engine/backtest path when:

- you already have executable strategy logic
- you want position, fill, exposure, and PnL traces
- you want portfolio aggregation across strategies
- you want strategy execution artifacts, not just hypothesis metrics

### Use both when:

- you first narrow candidates statistically
- then convert the survivors into executable blueprints
- then validate strategy mechanics with the engine

## 11. Current Practical Limits

Facts that matter operationally:

- the canonical search path is not a full portfolio simulator
- the execution engine exists, but is not the default research evaluator
- DSL/runtime is test-backed for minimal strategy behavior, but full compiler-to-engine fidelity still requires targeted audits per strategy family
- synthetic datasets are calibration and infrastructure tools, not direct proof of live tradability

## 12. Minimal Operator Workflow

For bounded research:

1. query memory and knobs
2. write a compact proposal
3. translate and plan it
4. run one narrow slice
5. read manifests, logs, and reports
6. record one next action:
   - `exploit`
   - `explore`
   - `repair`
   - `hold`
   - `stop`

For executable backtesting:

1. make sure bars/features exist for a `run_id`
2. prepare a strategy or DSL blueprint
3. call `run_engine(...)`
4. inspect strategy traces, portfolio ledger, and engine metrics

## 13. Recommended Reading

Read these next:

1. [03_OPERATOR_WORKFLOW.md](/home/irene/Edge/docs/03_OPERATOR_WORKFLOW.md)
2. [04_COMMANDS_AND_ENTRY_POINTS.md](/home/irene/Edge/docs/04_COMMANDS_AND_ENTRY_POINTS.md)
3. [05_ARTIFACTS_AND_INTERPRETATION.md](/home/irene/Edge/docs/05_ARTIFACTS_AND_INTERPRETATION.md)
4. [06_QUALITY_GATES_AND_PROMOTION.md](/home/irene/Edge/docs/06_QUALITY_GATES_AND_PROMOTION.md)
5. [13_TRIGGER_TYPES.md](/home/irene/Edge/docs/13_TRIGGER_TYPES.md)

## 14. Start From Zero

This section gives two concrete workflows:

1. one bounded research run
2. one executable engine backtest

### A. Start A Bounded Research Run

Goal:

- test one narrow hypothesis on one symbol and one event

Example hypothesis:

- `BTCUSDT`
- `5m`
- event `BASIS_DISLOC`
- template `mean_reversion`
- direction `short`
- horizon `12` bars
- entry lag `1`
- date range `2022-11-01` to `2022-12-31`

Step 1. Check knowledge surfaces first.

```bash
.venv/bin/python -m project.research.knowledge.query knobs
.venv/bin/python -m project.research.knowledge.query static --event BASIS_DISLOC
```

Step 2. Create a proposal file.

Example file: `/tmp/test_one_hypothesis_btc_basis_disloc.yaml`

```yaml
program_id: single_hypothesis_test
description: Test one bounded BASIS_DISLOC hypothesis on BTCUSDT 5m.
run_mode: research
objective_name: retail_profitability
promotion_profile: research
symbols:
  - BTCUSDT
timeframe: 5m
start: "2022-11-01"
end: "2022-12-31"
instrument_classes:
  - crypto
trigger_space:
  allowed_trigger_types:
    - EVENT
  events:
    include:
      - BASIS_DISLOC
templates:
  - mean_reversion
horizons_bars:
  - 12
directions:
  - short
entry_lags:
  - 1
search_control:
  max_hypotheses_total: 1
  max_hypotheses_per_template: 1
artifacts:
  write_candidate_table: true
  write_hypothesis_log: true
  write_reports: true
```

Step 3. Translate and inspect the exact experiment config.

```bash
.venv/bin/python -m project.research.agent_io.proposal_to_experiment \
  --proposal /tmp/test_one_hypothesis_btc_basis_disloc.yaml \
  --registry_root project/configs/registries \
  --config_path /tmp/experiment.yaml \
  --overrides_path /tmp/run_all_overrides.json
```

Step 4. Plan before execution.

```bash
.venv/bin/python -m project.research.agent_io.execute_proposal \
  --proposal /tmp/test_one_hypothesis_btc_basis_disloc.yaml \
  --run_id single_hypothesis_btc_basis_disloc_run \
  --registry_root project/configs/registries \
  --out_dir data/artifacts/experiments/single_hypothesis_test/memory/proposals/single_hypothesis_btc_basis_disloc_run \
  --plan_only 1
```

Step 5. Execute the run.

```bash
.venv/bin/python -m project.pipelines.run_all \
  --run_id single_hypothesis_btc_basis_disloc_run \
  --experiment_config /tmp/experiment.yaml \
  --registry_root project/configs/registries \
  --symbols BTCUSDT \
  --start 2022-11-01 \
  --end 2022-12-31 \
  --candidate_promotion_profile research \
  --mode research \
  --objective_name retail_profitability \
  --program_id single_hypothesis_test
```

Step 6. Read artifacts in the correct order.

```bash
cat data/runs/single_hypothesis_btc_basis_disloc_run/run_manifest.json
cat data/runs/single_hypothesis_btc_basis_disloc_run/phase2_search_engine.json
cat data/reports/single_hypothesis_btc_basis_disloc_run/funnel_summary.json
cat data/runs/single_hypothesis_btc_basis_disloc_run/kpi_scorecard.json
```

What to conclude:

- mechanical: did the run complete and produce artifacts
- statistical: did the hypothesis survive sample and significance gates
- deployment: is there anything worth promoting or is the next action `hold` / `repair`

### B. Start An Engine Backtest Run

Goal:

- execute an actual strategy or DSL blueprint against bars/features and get ledger/PnL artifacts

Requirement:

- the market-data `run_id` already has cleaned bars and features

The engine reads from:

- `data/lake/runs/<run_id>/cleaned/...`
- `data/lake/runs/<run_id>/features/...`

Step 1. Make sure the market-data run exists.

Example:

- `single_hypothesis_btc_basis_disloc_run`

That means the engine can load:

- cleaned bars from `data/lake/runs/single_hypothesis_btc_basis_disloc_run/cleaned/...`
- features from `data/lake/runs/single_hypothesis_btc_basis_disloc_run/features/...`

Step 2. Prepare a blueprint JSON.

Minimal example file: `/tmp/minimal_blueprint.json`

```json
{
  "id": "bp_test",
  "run_id": "single_hypothesis_btc_basis_disloc_run",
  "event_type": "BASIS_DISLOC",
  "candidate_id": "cand_1",
  "symbol_scope": {
    "mode": "single_symbol",
    "symbols": ["BTCUSDT"],
    "candidate_symbol": "BTCUSDT"
  },
  "direction": "short",
  "entry": {
    "triggers": ["basis_disloc_event"],
    "conditions": ["all"],
    "confirmations": [],
    "delay_bars": 0,
    "cooldown_bars": 0,
    "condition_logic": "all",
    "condition_nodes": [],
    "arm_bars": 0,
    "reentry_lockout_bars": 0
  },
  "exit": {
    "time_stop_bars": 12,
    "invalidation": {},
    "stop_type": "percent",
    "stop_value": 0.01,
    "target_type": "percent",
    "target_value": 0.02,
    "trailing_stop_type": "none",
    "trailing_stop_value": 0.0,
    "break_even_r": 0.0
  },
  "execution": {
    "fill_mode": "next_open",
    "allow_intrabar_exits": false,
    "priority_randomisation": true
  },
  "sizing": {
    "mode": "fixed_risk",
    "risk_per_trade": 0.01,
    "target_vol": null,
    "max_gross_leverage": 1.0,
    "max_position_scale": 1.0,
    "portfolio_risk_budget": 1.0,
    "symbol_risk_budget": 1.0
  },
  "overlays": [],
  "evaluation": {
    "min_trades": 1,
    "cost_model": {
      "fees_bps": 2.0,
      "slippage_bps": 2.0,
      "funding_included": true
    },
    "robustness_flags": {
      "oos_required": true,
      "multiplicity_required": true,
      "regime_stability_required": true
    }
  },
  "lineage": {
    "source_path": "manual",
    "compiler_version": "manual",
    "generated_at_utc": "2026-03-29T00:00:00Z"
  }
}
```

Step 3. Run the engine.

```bash
.venv/bin/python - <<'PY'
from pathlib import Path
import json
import pandas as pd

from project.core.config import get_data_root
from project.engine.runner import run_engine

data_root = get_data_root()
blueprint = json.loads(Path("/tmp/minimal_blueprint.json").read_text())

results = run_engine(
    run_id="single_hypothesis_btc_basis_disloc_run",
    symbols=["BTCUSDT"],
    strategies=["dsl_interpreter_v1__manual_test"],
    params={
        "allocator_mode": "heuristic",
        "max_portfolio_gross": 1.0,
        "max_symbol_gross": 1.0,
    },
    params_by_strategy={
        "dsl_interpreter_v1__manual_test": {
            "dsl_blueprint": blueprint,
            "event_feature_ffill_bars": 12,
        }
    },
    cost_bps=1.0,
    data_root=data_root,
    timeframe="5m",
    start_ts=pd.Timestamp("2022-11-01", tz="UTC"),
    end_ts=pd.Timestamp("2022-12-31", tz="UTC"),
)

print(results["engine_dir"])
print(results["metrics"]["portfolio"])
PY
```

Step 4. Read engine artifacts.

Look under:

- `data/runs/<engine_run_id>/engine/`

Important files:

- `metrics.json`
- `portfolio_returns.parquet`
- `strategy_returns_<strategy>.parquet`
- `strategy_trace_<strategy>.parquet`
- engine manifest

What to conclude:

- did the strategy actually generate positions
- what was the realized ledger/PnL path
- what did allocation and costs do
- do the traces match the intended entry/exit logic

## 15. Which Workflow To Start With

Use the research workflow first when:

- you are still testing whether an idea is worth deeper work

Use the engine workflow first when:

- you already know the exact executable strategy logic you want to simulate

Use both when:

- the research path narrows candidates
- then the engine path validates strategy mechanics and portfolio behavior

## 16. Compile Then Backtest

This workflow connects the research path to the engine path.

Use it when:

- a research run has produced candidate rows worth converting into executable strategy form
- you want to inspect the emitted blueprint
- you want to backtest the compiled blueprint with the engine

### Step 1. Run the research slice first

You need a completed research run with candidate artifacts.

Example:

- `single_hypothesis_btc_basis_disloc_run`

Relevant research outputs usually live under:

- `data/reports/phase2/<run_id>/...`
- `data/runs/<run_id>/...`

### Step 2. Compile strategy blueprints

The compiler surface is:

- [compile_strategy_blueprints.py](/home/irene/Edge/project/research/compile_strategy_blueprints.py)

There is also a compatibility wrapper:

- [blueprint_compiler.py](/home/irene/Edge/project/strategy/compiler/blueprint_compiler.py)

Example command shape:

```bash
.venv/bin/python -m project.research.compile_strategy_blueprints \
  --run_id single_hypothesis_btc_basis_disloc_run \
  --symbols BTCUSDT
```

The exact available flags depend on the current CLI surface of the compiler in the repo. If needed, inspect:

```bash
.venv/bin/python -m project.research.compile_strategy_blueprints --help
```

### Step 3. Inspect emitted blueprint artifacts

The compiler writes strategy-blueprint artifacts under:

- `data/reports/strategy_blueprints/...`

One maintained example consumer expects:

- `data/reports/strategy_blueprints/multi_edge_portfolio/blueprints.jsonl`

See:

- [run_multi_edge_backtest.py](/home/irene/Edge/project/scripts/run_multi_edge_backtest.py)

Inspect the blueprint payload directly before backtesting.

Check:

- `event_type`
- `direction`
- `entry.triggers`
- `entry.delay_bars`
- `exit.time_stop_bars`
- `exit.stop_value`
- `exit.target_value`
- `execution.fill_mode`
- `lineage.run_id`

### Step 4. Backtest the compiled blueprint

If the compiler emits JSONL blueprints, use the same loading pattern as [run_multi_edge_backtest.py](/home/irene/Edge/project/scripts/run_multi_edge_backtest.py):

```bash
.venv/bin/python - <<'PY'
from pathlib import Path
import json
import pandas as pd

from project.core.config import get_data_root
from project.engine.runner import run_engine

data_root = get_data_root()
blueprints_path = data_root / "reports" / "strategy_blueprints" / "multi_edge_portfolio" / "blueprints.jsonl"

blueprints = []
with blueprints_path.open("r", encoding="utf-8") as fh:
    for line in fh:
        blueprints.append(json.loads(line))

params_by_strategy = {}
strategies = []
for i, bp in enumerate(blueprints):
    name = f"dsl_interpreter_v1__compiled_{i}"
    strategies.append(name)
    params_by_strategy[name] = {
        "dsl_blueprint": bp,
        "event_feature_ffill_bars": 12,
    }

results = run_engine(
    run_id="single_hypothesis_btc_basis_disloc_run",
    symbols=["BTCUSDT"],
    strategies=strategies,
    params={
        "allocator_mode": "heuristic",
        "max_portfolio_gross": 1.0,
        "max_symbol_gross": 1.0,
    },
    params_by_strategy=params_by_strategy,
    cost_bps=1.0,
    data_root=data_root,
    timeframe="5m",
    start_ts=pd.Timestamp("2022-11-01", tz="UTC"),
    end_ts=pd.Timestamp("2022-12-31", tz="UTC"),
)

print(results["engine_dir"])
print(results["metrics"]["portfolio"])
PY
```

### Step 5. Compare blueprint intent to engine traces

This is the important audit step.

Read:

- the emitted blueprint JSON
- `strategy_trace_<strategy>.parquet`
- `strategy_returns_<strategy>.parquet`
- `portfolio_returns.parquet`

Verify:

- the trigger columns in the blueprint actually exist in the merged feature frame
- the interpreter generates positions on the bars you expect
- entry lag and fill mode behave the way you intend
- exits happen for the reasons you expect
- ledger PnL matches the position path

### Step 6. Decide what failed if results look wrong

If the engine trace is wrong, the problem usually lives in one of three places:

1. research-to-blueprint translation
2. DSL interpreter semantics
3. execution ledger / fill mechanics

Map those to these files:

- compiler path: [compile_strategy_blueprints.py](/home/irene/Edge/project/research/compile_strategy_blueprints.py)
- blueprint normalization: [normalize.py](/home/irene/Edge/project/strategy/dsl/normalize.py)
- interpreter: [interpreter.py](/home/irene/Edge/project/strategy/runtime/dsl_runtime/interpreter.py)
- ledger: [runner.py](/home/irene/Edge/project/engine/runner.py)
- PnL engine: [pnl.py](/home/irene/Edge/project/engine/pnl.py)

### Step 7. What this workflow proves

This workflow can prove:

- whether a compiled blueprint is executable
- whether the engine produces a coherent ledger for it
- whether runtime traces match the intended strategy mechanics

This workflow does not by itself prove:

- that the original research claim was statistically sound
- that the compiled blueprint faithfully captured all intended research semantics

Those require both:

- research-path artifact review
- engine-path trace review

## 17. Glossary

This repo uses several terms that look similar but mean different things.

### Proposal

A compact operator input that defines a bounded research run.

A proposal typically specifies:

- `program_id`
- objective
- symbols
- timeframe
- start/end
- trigger space
- templates
- horizons
- directions
- entry lags

Main surface:

- [proposal_schema.py](/home/irene/Edge/project/research/agent_io/proposal_schema.py)

### Experiment

A repo-native execution config produced from a proposal.

It is the translated, fully structured configuration that the pipeline actually uses.

Main surfaces:

- [proposal_to_experiment.py](/home/irene/Edge/project/research/agent_io/proposal_to_experiment.py)
- [experiment_engine.py](/home/irene/Edge/project/research/experiment_engine.py)

### Run

A concrete execution instance with a specific `run_id`.

Examples:

- a research run through `run_all`
- an engine run through `run_engine(...)`

A run writes artifacts under directories keyed by `run_id`.

### Hypothesis

A single explicit claim evaluated by the research/search layer.

Examples:

- after `BASIS_DISLOC`, `BTCUSDT`, `short`, `12b`, `mean_reversion`
- in a given context, event X followed by effect Y

Main surface:

- [hypotheses.py](/home/irene/Edge/project/domain/hypotheses.py)

### Candidate

A hypothesis that has been evaluated and materialized into a row with metrics and gates.

A candidate is farther along than a raw hypothesis. It has:

- metrics
- fail reasons or pass flags
- promotion-related fields

Examples:

- search candidate row
- bridge-compatible candidate row

### Blueprint

An executable strategy specification.

It describes:

- entry logic
- exit logic
- sizing
- overlays
- lineage

It is the object the DSL/runtime layer interprets.

Main surfaces:

- [project/strategy/dsl](/home/irene/Edge/project/strategy/dsl)
- [blueprint.py](/home/irene/Edge/project/strategy/models/blueprint.py)

### Strategy

A runtime-executable trading logic object.

Examples:

- the DSL interpreter strategy
- any other registered runtime strategy

The engine runs strategies, not raw hypotheses.

### Trigger

The condition that causes a hypothesis or strategy entry logic to activate.

Supported trigger types:

- `EVENT`
- `STATE`
- `TRANSITION`
- `FEATURE_PREDICATE`
- `SEQUENCE`
- `INTERACTION`

Reference:

- [13_TRIGGER_TYPES.md](/home/irene/Edge/docs/13_TRIGGER_TYPES.md)

### Event Family

A canonical regime/family grouping for related event types.

Examples:

- `BASIS_FUNDING_DISLOCATION`
- `LIQUIDATION_CASCADE`
- `TREND_CONTINUATION`

Reference:

- [event_registry_unified.yaml](/home/irene/Edge/spec/events/event_registry_unified.yaml)

### Artifact

A file written by the system that records what happened.

Examples:

- run manifest
- stage manifest
- hypothesis table
- candidate parquet
- funnel summary
- metrics JSON
- engine trace

Artifacts are the source of truth.

### Promotion

The gating process that decides whether a candidate is eligible to move forward.

Promotion is not the same as:

- detection success
- positive expectancy in one slice
- a completed run

Promotion depends on configured policy and gates.

### Backtest

In the strict sense, this means using the engine/runtime path to simulate strategy execution and produce a ledger/PnL trace.

Main surface:

- [runner.py](/home/irene/Edge/project/engine/runner.py)

This is different from the canonical search evaluator, which is a statistical trigger-conditioned evaluation path.

### Evaluation

This word is used in two different senses in the repo.

Research evaluation:

- score a hypothesis statistically in the search pipeline

Execution evaluation:

- run a strategy and evaluate realized ledger/PnL behavior in the engine

Do not treat those as the same thing.
