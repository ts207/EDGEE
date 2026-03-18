# Experiment Protocol

## Goal

An experiment converts a research question into a bounded, replayable, and comparable run.

If a run cannot be explained as one experiment or one small batch of related experiments, it is too broad.

## Experiment Card

Every experiment should be describable with:

- objective
- symbols
- time range
- trigger or event
- context or regime
- template
- directions
- horizons
- entry lags

That is the minimal unit of attribution.

## Experiment Types

### Repair

Use when the question is mechanical.

Purpose:

- verify a code fix
- verify a contract repair
- prove a prior failure path is gone

Success looks like:

- expected artifacts exist
- the prior failure no longer reproduces
- no new contract breakage appears

### Narrow Discovery

Use when the question is statistical or structural but still small.

Purpose:

- isolate one signal region
- compare conditioned versus unconditioned behavior
- test a small number of related hypotheses

Success looks like:

- enough split support to interpret the result
- coherent metrics
- an interpretable next action

### Promotion-Path Verification

Use when the question is whether candidates survive downstream handling.

Purpose:

- verify export
- verify promotion logic
- verify registry and memory updates

Success looks like:

- fields survive the chain
- promotion rejects or accepts for substantive reasons

### Synthetic Validation

Use when the question is about mechanism recovery or synthetic guardrails.

Purpose:

- verify detector recovery against planted regimes
- verify discovery and promotion behavior under controlled worlds

Success looks like:

- truth validation passes or misses are explainable
- promotion behavior matches the planted mechanism and cost assumptions
- the result survives at least one additional profile when belief is strengthened

### Full Loop

Use only when the local path is already stable.

Purpose:

- validate end-to-end behavior through the intended DAG path

Success looks like:

- planned stages complete
- manifests reconcile
- outputs are explainable

## Design Rules

- change one important variable at a time when debugging
- keep symbol and time scope narrow during repair
- use explicit contexts for regime-conditioned claims
- avoid broad exploratory runs if prior memory already says the region is weak
- record why the run exists before executing it
- prefer `plan_only` before materially expensive runs
- prefer targeted replay when the goal is verification, not new evidence

## Batch Rules

Every batch should specify:

- the primary hypothesis
- the reason for inclusion
- the prior memory reference
- the stop condition

Recommended sequence:

1. confirm the path works
2. test the strongest hypothesis
3. test one adjacent alternative

## Evaluation Checklist

For each candidate or experiment result, check:

- `train_n_obs`
- `validation_n_obs`
- `test_n_obs`
- `q_value`
- post-cost expectancy
- stressed expectancy
- regime stability
- bridge tradability
- promotion eligibility
- warning surface
- manifest cleanliness

## Reflection Record

For each completed experiment, record:

- objective
- actual executed slice
- key metrics
- anomalies
- belief update
- next action

## Stop Rules

Stop a line of inquiry when:

- repeated runs fail for the same substantive statistical reason
- the region does not survive costs
- support exists only in train and not in validation or test
- the implementation path is still mechanically unstable

## Promotion Discipline

Keep the boundary clear:

- a discovery is not a promoted edge
- a promoted edge is not a production strategy

Synthetic experiments should also record:

- generator profile
- truth-map path
- whether the result survived another profile or only one world
