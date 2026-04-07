Good. The benchmark is now doing the hard part: **running the real search pipeline across A–F**.

Your current bottleneck is no longer execution. It is **evaluation semantics**.

## What the results already prove

Two things are already established:

### 1. The benchmark is valid as an execution harness

* all 30 jobs ran
* event fixtures survived into phase 2
* hypotheses were generated
* candidates were produced

That means the benchmark system is now a real experimental surface.

### 2. Hierarchical search is the only component with an obvious signal so far

From your counts:

* `A/B/C` often produce `0`
* `D/E/F` rescue multiple slices

That is not enough for full promotion, but it is enough to say:

**hierarchical search has the first real positive signal**

Everything else is still unevaluated, not disproven.

## What is missing

Right now the scorecard is mostly asking:

* promotion density
* placebo fail rate
* diversity score
* cost-adjusted expectancy
* cost survival

But your current result summary is mostly based on:

* candidate counts
* whether a mode produced anything at all

So the scorecard is inconclusive because **the benchmark output does not yet translate discovery artifacts into decision metrics strongly enough**.

## The exact next move

Do **not** add more pipeline logic.

Add a **benchmark metric extraction layer** that turns each mode’s candidate parquet into decision-grade metrics.

## What to compute next

For each `slice × mode`, compute these:

### Core quality

* `candidate_count`
* `top10_candidate_count`
* `median_discovery_quality_score`
* `max_discovery_quality_score`
* `median_t_stat`
* `median_estimate_bps`
* `median_cost_survival_ratio`

### Integrity

* `median_falsification_component`
* `placebo_fail_rate_top10`
* `median_fold_stability_component`
* `sign_consistency_top10`

### Diversity

* `unique_family_id_top10`
* `unique_template_id_top10`
* `unique_comp_key_top10`
* `overlap_penalty_rate_top10`

### Search-topology value

This one is important for D vs C:

* `candidate_emergence_rate` = whether mode found any valid candidates on the slice
* `top_quality_when_nonzero`
* `runtime_seconds`

That lets you say:

* flat failed, hierarchical found valid candidates
* and whether those candidates are actually any good

## Minimal change to make the benchmark decision-capable

The fastest way is to upgrade `_extract_benchmark_metrics(...)` in `discovery_benchmark.py`.

It already extracts some metrics. Extend it to include:

```python
{
  "candidate_count": ...,
  "top10_count": ...,
  "top10": {
    "promotion_density": ...,
    "placebo_fail_rate": ...,
    "rank_diversity_score": ...,
    "median_after_cost_expectancy_bps": ...,
    "median_cost_survival_ratio": ...,
    "median_discovery_quality_score": ...,
    "median_t_stat": ...,
    "median_falsification_component": ...,
    "median_fold_stability_component": ...,
    "unique_family_id": ...,
    "unique_template_id": ...,
    "emergence": 0 or 1,
  }
}
```

The important addition is:

* `emergence`
* `median_discovery_quality_score`
* `median_t_stat`
* `fold / falsification summaries`

Because candidate count alone is too weak, but emergence + quality is enough to distinguish D from C.

## How to interpret your current results right now

### A → B

No evidence yet that v2 scoring helps or hurts.

Status: **hold**

### B → C

No evidence yet that folds improve integrity.

Status: **hold**

### C → D

Clear signal that hierarchical search increases discovery coverage.

But you still need to know:

* are these rescued candidates any good?
* or is hierarchical just surfacing more junk?

Status: **provisional hold leaning promote pending quality metrics**

### D → E

No current evidence that ledger changes anything meaningful.

Status: **hold**

### E → F

No current evidence that diversification changes anything meaningful.

Status: **hold**

## One very important issue

### `m1_noisy_event` is currently not an informative slice

You said it has `0 FUNDING_EXTREME_ONSET events`.

That slice is currently functioning as:

* empty coverage case
* pipeline robustness check

It is **not** a meaningful discovery comparison slice.

So either:

* replace its fixture with a slice that actually contains that event family, or
* explicitly mark it as a negative-control/empty-coverage slice and exclude it from component promotion logic

That matters because otherwise it dilutes the benchmark.

## Best next implementation order

### Step 1

Upgrade metric extraction in `discovery_benchmark.py`

### Step 2

Re-run the benchmark suite

### Step 3

Inspect `benchmark_scorecard.json` again

### Step 4

Only if hierarchical still looks good on quality, move it to `stable-internal`

## Strongest recommendation

Do not try to make **all** components decision-capable at once.

Make the benchmark good enough to answer this one first:

**Are the D-mode rescued candidates actually better than zero-output flat search in a statistically and economically meaningful way?**

