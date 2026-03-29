# Standing Bounded Experiment Template

This document is the control template for future work after the baseline cleanup.

Use it to keep the repository in the narrow research loop unless a change is truly structural.

## 1. Control Baseline

Treat the following as the trusted release-style checkpoint:

- [target_state.md](/home/irene/Edge/target_state.md)
- [audit.md](/home/irene/Edge/audit.md)
- [plan.md](/home/irene/Edge/plan.md)
- [implementation_report.md](/home/irene/Edge/implementation_report.md)
- [runresults.md](/home/irene/Edge/runresults.md)
- [final.md](/home/irene/Edge/final.md)

Freeze these with it:

- passing verification command inventory in [implementation_report.md](/home/irene/Edge/implementation_report.md)
- maintained verification surface in [docs/08_TESTING_AND_MAINTENANCE.md](/home/irene/Edge/docs/08_TESTING_AND_MAINTENANCE.md)
- active audit/workflow schedule in [docs/12_AUDIT_RUN_SCHEDULE.md](/home/irene/Edge/docs/12_AUDIT_RUN_SCHEDULE.md)
- canonical ontology/routing artifacts under [docs/generated/](/home/irene/Edge/docs/generated)
- current calibration baseline in [docs/RESEARCH_CALIBRATION_BASELINE.md](/home/irene/Edge/docs/RESEARCH_CALIBRATION_BASELINE.md)
- one known-good bounded experiment result in [runresults.md](/home/irene/Edge/runresults.md)

Current control conclusion:

- canonical phase-2 pathing is repaired
- lineage is explicit through promotion artifacts
- canonical regime-routing metadata survives the bounded replay
- the remaining bounded gap is one promotable fixture that proves run-scoped blueprint to engine flow

That is the baseline to protect. Do not reopen taxonomy or architecture unless a new defect crosses a structural contract boundary.

## 2. Lane Selection

Use exactly one lane per run.

### Lane A: Change-Management Lane

Use this lane only when at least one of these changed materially:

- architecture boundaries
- artifact or schema contracts
- registry or routing semantics
- storage path semantics
- identity models or lineage rules

Required sequence:

1. target-state refresh
2. audit
3. plan
4. implementation
5. bounded experiment

Default verification floor:

- `make minimum-green-gate`
- targeted tests for the changed surface
- one bounded artifact reconciliation run

Stop condition:

- stop after the bounded experiment and leave a next action of `explore`, `repair`, `hold`, or `stop`

### Lane B: Research / Edge Lane

Use this lane for normal progress after the baseline is stable.

Required sequence:

1. bounded hypothesis proposal
2. experiment execution
3. result analysis
4. local fixes if obvious
5. promotion or rejection decision

Default verification floor:

- `make test-fast`
- targeted tests for any local fix touched by the experiment
- regime/routing or artifact validation only for the changed local surface

Stop condition:

- stop once the hypothesis is classified as `proposed`, `active`, `rejected`, or `archived`

Decision rule:

- if the defect changes how the system means something, routes something, names something, stores something, or joins something, use Lane A
- if the defect only changes one hypothesis loop, one local report inconsistency, one local schema mismatch, or one obvious bounded replay bug, stay in Lane B

## 3. Standing Research Loop

The default operating loop is one bounded regime-specific edge program at a time.

Recommended starting regimes:

- `LIQUIDITY_STRESS`
- `BASIS_FUNDING_DISLOCATION`
- `CROSS_ASSET_DESYNC`

Default program shape:

1. pick one regime
2. define one mechanism
3. define one trade expression
4. run one bounded campaign
5. inspect manifests, logs, and reports
6. patch only obvious local defects
7. decide `keep`, `modify`, or `kill`

Do not broaden the run by adding unrelated triggers, templates, or symbols to rescue a weak idea.

## 4. Required Run Artifacts

Every Lane B run should leave behind three operator-facing artifacts plus the normal pipeline outputs.

### A. `hypothesis.md`

Write this before execution.

Required fields:

- hypothesis ID
- mechanism
- forced actor
- constraint
- distortion
- unwind path
- trigger regime
- trade expression
- entry logic
- exit logic
- invalidation
- cost assumptions
- expected horizon
- bounded symbol, timeframe, and date window

Template:

```md
# Hypothesis

- Hypothesis ID: `<program_or_run_scoped_id>`
- Regime: `<canonical_regime>`
- Mechanism: `<one sentence>`
- Forced actor: `<who must transact>`
- Constraint: `<balance sheet, margin, funding, inventory, liquidity, or other limit>`
- Distortion: `<what price/flow dislocation should appear>`
- Unwind path: `<why the distortion should mean revert or continue>`
- Trade expression: `<instrument and direction>`
- Entry logic: `<specific trigger>`
- Exit logic: `<time, price, or state exit>`
- Invalidation: `<what observation kills the idea>`
- Costs: `<spread/slippage/funding/borrow assumptions>`
- Expected horizon: `<bars or wall-clock>`
- Scope: `<symbols, timeframe, start, end>`
- Next action if inconclusive: `explore | repair | hold | stop`
```

### B. Proposal YAML

Translate the hypothesis into one compact proposal.

Skeleton:

```yaml
program_id: bounded_edge_program
description: One bounded mechanism test.
run_mode: research
objective_name: retail_profitability
promotion_profile: research
symbols:
  - BTCUSDT
timeframe: 5m
start: "2022-11-01"
end: "2022-12-31"
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

### C. `experiment_review.md`

Write this after execution.

Required fields:

- whether the mechanism matched the observed data
- net-of-cost outcome
- main failure modes
- data-quality issues
- regime/routing quality
- whether to keep, modify, or kill the idea

Template:

```md
# Experiment Review

- Run ID: `<run_id>`
- Hypothesis ID: `<hypothesis_id>`
- Mechanism matched data: `yes | mixed | no`
- Mechanical conclusion: `<pass/fail and why>`
- Statistical conclusion: `<pass/fail and why>`
- Deployment conclusion: `<pass/fail and why>`
- Net-of-cost outcome: `<summary>`
- Main failure modes: `<one line each>`
- Data-quality issues: `<one line each or none>`
- Regime/routing quality: `<clean/mixed/bad and why>`
- Artifact completeness: `<complete/missing items>`
- Promotion decision: `keep | modify | kill`
- Next action: `exploit | explore | repair | hold | stop`
```

### D. Edge Registry Row

Maintain a tracked table such as `edge_registry.md`.

Required fields:

- hypothesis ID
- regime
- status
- evidence strength
- latest run IDs
- next action

Template:

```md
| hypothesis_id | regime | status | evidence_strength | latest_run_ids | next_action | notes |
| --- | --- | --- | --- | --- | --- | --- |
| `basis_norm_001` | `BASIS_FUNDING_DISLOCATION` | `proposed` | `weak` | `run_20260329_a` | `explore` | `First bounded slice.` |
```

## 5. Exact Operator Sequence

Use this exact order for Lane B.

### Step 1. Query memory and knobs

```bash
.venv/bin/python -m project.research.knowledge.query knobs
.venv/bin/python -m project.research.knowledge.query memory --program_id <program_id>
.venv/bin/python -m project.research.knowledge.query static --event <event_name>
```

### Step 2. Translate proposal

```bash
.venv/bin/python -m project.research.agent_io.proposal_to_experiment \
  --proposal /abs/path/to/proposal.yaml \
  --registry_root project/configs/registries \
  --config_path /tmp/experiment.yaml \
  --overrides_path /tmp/run_all_overrides.json
```

### Step 3. Inspect plan before execution

```bash
.venv/bin/python -m project.research.agent_io.execute_proposal \
  --proposal /abs/path/to/proposal.yaml \
  --run_id <run_id> \
  --registry_root project/configs/registries \
  --out_dir data/artifacts/experiments/<program_id>/proposals/<run_id> \
  --plan_only 1
```

Reject the run and narrow it further if any of these are true:

- multiple unrelated trigger families enter the plan
- more than one template family enters the plan without an explicit reason
- symbol or date scope expanded beyond the stated hypothesis
- output locations or promotion profile are not what the hypothesis expects

### Step 4. Execute one bounded run

Use the proposal path or the direct CLI path only after the plan looks right.

### Step 5. Read artifacts in order

Read in this order:

1. top-level run manifest
2. stage manifests
3. stage logs
4. report artifacts
5. generated diagnostics

If they disagree, record the disagreement as the main finding.

## 6. Promotion Gates

Every new idea must pass these gates before it is treated as real.

### Gate 1: Mechanism

Can you state:

- forced actor
- constraint
- distortion
- unwind path
- tradable horizon

### Gate 2: Contract

Does the run populate:

- canonical regime
- subtype
- phase
- evidence mode
- routing profile
- comparison-compatible artifacts

### Gate 3: Cost

Does the idea survive:

- spread
- slippage
- funding or borrow when relevant
- realistic execution assumptions

### Gate 4: Robustness

Does it hold on:

- unseen future window
- related market
- stress versus non-stress split

### Gate 5: Operational Simplicity

Can the idea be run and monitored without creating a brittle machine?

Promotion rule:

- only promoted hypotheses move into later deployment-oriented work

## 7. Governance Cadence

### Every bounded experiment

Run:

- `python -m compileall -q project project/tests`
- `make test-fast`
- targeted tests for the changed area
- regime/routing or local artifact validation tied to the touched surface

### Weekly or every N runs

Run:

- comparison-service compatibility checks
- generated-doc drift checks
- run-comparison summaries
- null/default drift audit on candidate and promotion tables

Useful maintained surfaces:

- [docs/08_TESTING_AND_MAINTENANCE.md](/home/irene/Edge/docs/08_TESTING_AND_MAINTENANCE.md)
- [docs/12_AUDIT_RUN_SCHEDULE.md](/home/irene/Edge/docs/12_AUDIT_RUN_SCHEDULE.md)

### Monthly or after major refactors

Run the heavy lane again.

## 8. What Not To Do

Do not:

- rerun full audits after every small change
- reopen taxonomy or architecture weekly
- add ML before one rule-based edge loop survives
- widen into many simultaneous regimes
- treat green tests as research proof
- treat one profitable backtest as deployment proof

## 9. Current Best Next Stage

The default next stage is one bounded regime-specific edge program.

Recommended shape:

1. choose one regime
2. write `hypothesis.md`
3. create one compact proposal
4. plan the run
5. execute the run
6. write `experiment_review.md`
7. update the edge registry
8. decide `keep`, `modify`, or `kill`

Return point after every run:

- update memory
- record one next action
- stop
