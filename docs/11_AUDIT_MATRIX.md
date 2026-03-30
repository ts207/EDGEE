# Audit Matrix

This file turns the repository into explicit audit units and explicit audit passes.

Use it when the goal is not "read the code" but "certify what is known, what is broken, and what still lacks evidence."

## How To Use This Matrix

For each audit unit:

1. run the passes in order
2. attach evidence
3. mark the status conservatively
4. record one next action

Do not collapse multiple passes into one verdict. A unit can be:

- mechanically clean
- semantically wrong
- statistically weak
- operationally hard to use

all at the same time.

## Status Legend

- `mapped`: files and ownership are identified
- `partial`: some direct evidence exists, but the unit is not fully certified
- `repaired`: a known failure was fixed and spot-verified
- `pending`: audit not yet performed or lacks evidence

## Audit Passes

1. `static_inventory`: enumerate files, entry points, ownership, and declared surfaces
2. `spec_code`: verify specs and code consumers agree
3. `contract`: verify stage and artifact boundaries
4. `semantics`: verify names and behavior actually match
5. `causality`: verify timestamps, replay, and runtime invariants
6. `search_integrity`: verify narrow questions remain narrow
7. `stat_policy`: verify gates, multiplicity, robustness, and stress are auditable and spec-driven
8. `synthetic_truth`: verify detector and infrastructure behavior on synthetic truth surfaces
9. `historical_runs`: verify behavior against bounded real or historical runs
10. `reconciliation`: verify manifest, logs, diagnostics, and output artifacts agree
11. `failure_injection`: verify the unit fails loudly and locally when inputs are broken
12. `operator_usability`: verify a new researcher can use the surface correctly

## Matrix

| Audit Unit | Key Files | Current Status | Strongest Existing Evidence | Next Audit Pass |
| --- | --- | --- | --- | --- |
| Operator surface | [README.md](../README.md), [docs/README.md](README.md), [project/research/agent_io/](../project/research/agent_io), [project/research/knowledge/query.py](../project/research/knowledge/query.py) | `partial` | New doc set, maintained CLI help for `execute_proposal`, `issue_proposal`, `knowledge.query` | `operator_usability` |
| Contracts and orchestration | [project/contracts/pipeline_registry.py](../project/contracts/pipeline_registry.py), [project/contracts/](../project/contracts), [project/pipelines/run_all.py](../project/pipelines/run_all.py), [project/pipelines/](../project/pipelines) | `mapped` | Repo structure mapped; real runs reconcile at manifest level | `contract` |
| Specs and ontology | [spec/events/event_registry_unified.yaml](../spec/events/event_registry_unified.yaml), [spec/templates/event_template_registry.yaml](../spec/templates/event_template_registry.yaml), [spec/search_space.yaml](../spec/search_space.yaml), [spec/gates.yaml](../spec/gates.yaml) | `partial` | `VOL_SHOCK` semantic drift corrected; bridge thresholds made spec-driven | `spec_code` |
| Data and feature pipeline | [project/pipelines/ingest/](../project/pipelines/ingest), [project/pipelines/clean/](../project/pipelines/clean), [project/pipelines/features/](../project/pipelines/features), [project/features/](../project/features) | `partial` | Real bounded runs complete through features and market context | `reconciliation` |
| Event detection | [project/features/](../project/features), [project/events/](../project/events), [spec/events/](../spec/events) | `partial` | `VOL_SHOCK` detector, spec, and event artifacts were directly audited | `synthetic_truth` |
| Runtime invariants | [project/runtime/](../project/runtime), [spec/runtime/](../spec/runtime) | `repaired` | Historical run [codex_real_btc_vol_shock_20260328_4](../data/runs/codex_real_btc_vol_shock_20260328_4) failed postflight; later run [codex_real_btc_vol_shock_202211_202212_20260328_5](../data/runs/codex_real_btc_vol_shock_202211_202212_20260328_5) passed with `0` violations | `causality` |
| Search and statistical evaluation | [project/research/phase2_search_engine.py](../project/research/phase2_search_engine.py), [project/research/search/](../project/research/search), [project/research/robustness/](../project/research/robustness) | `repaired` | Event-pinned search scoping and template compatibility were fixed and rerun | `historical_runs` |
| Bridge and promotion | [project/research/search/bridge_adapter.py](../project/research/search/bridge_adapter.py), [project/research/bridge_evaluate_phase2.py](../project/research/bridge_evaluate_phase2.py), [project/research/promotion/](../project/research/promotion) | `partial` | Bridge thresholds now come from [spec/gates.yaml](../spec/gates.yaml); recent `VOL_SHOCK` candidates still fail bridge for substantive reasons | `stat_policy` |
| Reliability and tests | [project/reliability/](../project/reliability), [project/tests/](../project/tests), [tests/](../tests), [Makefile](../Makefile) | `partial` | `pytest -q -m "not slow" --maxfail=1` passed; full smoke passed; maintained targets documented | `failure_injection` |
| Artifacts and historical evidence | [data/runs/](../data/runs), [data/reports/](../data/reports) | `partial` | Good and bad worked examples now documented; multiple bounded historical runs available | `reconciliation` |

## Pass Details By Unit

### 1. Operator Surface

Goal:

- verify a new researcher can orient, plan a run, and interpret outputs without tribal knowledge

Method:

- follow [docs/00_START_HERE.md](00_START_HERE.md)
- run `--help` on `knowledge.query`, `execute_proposal`, `issue_proposal`, `run_all`
- have a new operator follow [docs/09_WORKED_EXAMPLE_VOL_SHOCK.md](09_WORKED_EXAMPLE_VOL_SHOCK.md)

Evidence to collect:

- exact commands used
- points of confusion
- stale or ambiguous docs

### 2. Contracts And Orchestration

Goal:

- verify stages only communicate through declared artifacts and manifests

Method:

- compare [project/contracts/pipeline_registry.py](../project/contracts/pipeline_registry.py) against actual run artifacts
- inspect [project/pipelines/](../project/pipelines) for undeclared file reads or writes

Evidence to collect:

- one bounded run manifest
- stage logs
- missing or undeclared artifact accesses

### 3. Specs And Ontology

Goal:

- verify event, template, state, search, and gate specs match code behavior

Method:

- trace one event end to end from spec row to code consumer
- trace one gate parameter from YAML to code to artifact

Evidence to collect:

- spec path
- consumer path
- exact behavior observed in a run

### 4. Data And Feature Pipeline

Goal:

- verify raw-to-feature transformations are stable and artifacts are complete

Method:

- run one bounded slice
- inspect cleaned bars, features, market context, and integrity validation outputs

Evidence to collect:

- row counts
- feature coverage warnings
- schema version and hash

### 5. Event Detection

Goal:

- verify detector semantics, timestamps, and emitted diagnostics

Method:

- inspect event parquet columns and counts
- compare detector code with spec text
- run synthetic truth where available

Evidence to collect:

- event parquet
- detector implementation path
- spec row

### 6. Runtime Invariants

Goal:

- verify causal correctness and timestamp discipline

Method:

- inspect runtime postflight status and violation counts
- compare historical failing and repaired runs

Evidence to collect:

- [codex_real_btc_vol_shock_20260328_4](../data/runs/codex_real_btc_vol_shock_20260328_4)
- [codex_real_btc_vol_shock_202211_202212_20260328_5](../data/runs/codex_real_btc_vol_shock_202211_202212_20260328_5)

### 7. Search And Statistical Evaluation

Goal:

- verify narrow questions stay narrow and generated candidates are attributable

Method:

- inspect resolved search specs
- compare broad leaked run vs event-scoped rerun

Evidence to collect:

- [phase2_search_engine.log](../data/runs/codex_real_btc_vol_shock_202211_202212_20260328_5/phase2_search_engine.log)
- [resolved_search_spec__VOL_SHOCK.yaml](../data/reports/phase2/codex_real_btc_vol_shock_202211_202212_20260328_5/search_engine/resolved_search_spec__VOL_SHOCK.yaml)

### 8. Bridge And Promotion

Goal:

- verify tradability and promotion rules are explicit and auditable

Method:

- trace bridge thresholds from [spec/gates.yaml](../spec/gates.yaml) into [project/specs/gates.py](../project/specs/gates.py) and [project/research/search/bridge_adapter.py](../project/research/search/bridge_adapter.py)
- inspect surviving candidate rows and bridge failure reasons

Evidence to collect:

- candidate parquet
- gate spec
- bridge adapter logic

### 9. Reliability And Tests

Goal:

- verify the fast gate, smoke gate, and maintained workflows cover the expected failure modes

Method:

- run `make test-fast`
- run full smoke
- identify untested historical failure classes

Evidence to collect:

- command output
- missing regression tests for known historical bugs

### 10. Artifacts And Historical Evidence

Goal:

- verify the repo leaves behind enough evidence to diagnose failures after the fact

Method:

- inspect one good run and one bad run end to end
- verify the doc examples match the underlying artifacts

Evidence to collect:

- [docs/09_WORKED_EXAMPLE_VOL_SHOCK.md](09_WORKED_EXAMPLE_VOL_SHOCK.md)
- [docs/10_WORKED_EXAMPLE_MECHANICAL_FAILURE.md](10_WORKED_EXAMPLE_MECHANICAL_FAILURE.md)

## Recommended Full Audit Sequence

Run the units in this order:

1. operator surface
2. contracts and orchestration
3. specs and ontology
4. runtime invariants
5. search and statistical evaluation
6. bridge and promotion
7. reliability and tests
8. data and feature pipeline
9. event detection
10. artifacts and historical evidence

Reason:

- operator confusion causes false audit conclusions
- contract and spec drift invalidate everything downstream
- runtime and search integrity determine whether historical evidence is even meaningful

## Audit Record Template

Use this template for every audit cell you complete:

```text
unit:
pass:
files:
method:
evidence:
result:
next_action:
```

That keeps the audit reproducible and prevents summary-only conclusions.
