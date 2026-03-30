# Worked Example: Narrow `VOL_SHOCK` Run

This walkthrough shows how to read a real bounded run from question to interpretation.

It uses:

- run id: `codex_real_btc_vol_shock_202211_202212_20260328_5`
- run manifest: [run_manifest.json](../data/runs/codex_real_btc_vol_shock_202211_202212_20260328_5/run_manifest.json)

## The Question

The run asked a narrow question:

"On BTCUSDT 5m bars from November 1, 2022 through December 31, 2022, does the `VOL_SHOCK` event produce any short- or long-side phase-2 candidates that survive bridge filtering?"

That is a good research question because it is bounded by:

- one symbol: `BTCUSDT`
- one timeframe: `5m`
- one event: `VOL_SHOCK`
- one date range: `2022-11-01` to `2022-12-31`
- promotion disabled

## The Exact Run Shape

The manifest shows the effective CLI:

```bash
.venv/bin/python -m project.pipelines.run_all \
  --run_id codex_real_btc_vol_shock_202211_202212_20260328_5 \
  --symbols BTCUSDT \
  --start 2022-11-01 \
  --end 2022-12-31 \
  --timeframes 5m \
  --run_phase2_conditional 1 \
  --phase2_event_type VOL_SHOCK \
  --run_edge_candidate_universe 1 \
  --run_strategy_builder 0 \
  --run_expectancy_analysis 0 \
  --run_expectancy_robustness 0 \
  --run_recommendations_checklist 0 \
  --run_candidate_promotion 0
```

That matters because it proves this was a narrow research slice, not a broad all-trigger search.

## Step 1: Read The Manifest

The manifest is the first artifact to inspect:

- [run_manifest.json](../data/runs/codex_real_btc_vol_shock_202211_202212_20260328_5/run_manifest.json)

Key mechanical facts:

- `status = success`
- `runtime_postflight_status = pass`
- `runtime_postflight_violation_count = 0`
- `runtime_postflight_event_count = 128`
- planned stages include event analysis, event registry build, conditional hypotheses, bridge evaluation, search engine, discovery summary, naive entry evaluation, and edge export

Interpretation:

- the run executed cleanly
- the runtime audit found no causality violations
- the detector produced `128` `VOL_SHOCK` events

Mechanical conclusion at this stage:

"The pipeline is healthy enough for this slice. Continue to search diagnostics."

## Step 2: Inspect The Event Output

The event parquet is:

- [vol_shock_relaxation_events.parquet](../data/reports/vol_shock_relaxation/codex_real_btc_vol_shock_202211_202212_20260328_5/vol_shock_relaxation_events.parquet)

Facts from the file:

- `128` rows
- event timestamps are carried through columns like `anchor_ts`, `eval_bar_ts`, `enter_ts`, `detected_ts`, `signal_ts`
- the file also contains context and feature columns such as `high_vol_regime`, `low_vol_regime`, `prob_spread_wide`, `deleveraging_state`, `aftershock_state`, and price/volume/funding fields

Interpretation:

- detector materialization is real
- event rows carry both event-level and context-level information
- event existence alone still does not prove a tradeable edge

## Step 3: Inspect Search Diagnostics

The search diagnostics are:

- [phase2_diagnostics.json](../data/reports/phase2/codex_real_btc_vol_shock_202211_202212_20260328_5/phase2_diagnostics.json)
- [phase2_search_engine.log](../data/runs/codex_real_btc_vol_shock_202211_202212_20260328_5/phase2_search_engine.log)
- resolved spec: [resolved_search_spec__VOL_SHOCK.yaml](../data/reports/phase2/codex_real_btc_vol_shock_202211_202212_20260328_5/resolved_search_spec__VOL_SHOCK.yaml)

Important facts:

- `hypotheses_generated = 80`
- `feasible_hypotheses = 80`
- `rejected_hypotheses = 0`
- `valid_metrics_rows = 20`
- `rejected_invalid_metrics = 60`
- `bridge_candidates_rows = 10`

The log adds the causal explanation:

- the run used the event-scoped resolved search spec, not the broad global frontier
- only `1` event was searched
- `0` states, `0` transitions, `0` features were added to widen the search
- `80` hypotheses were generated
- `20` had valid metrics
- `60` fell below `min_sample_size = 30`

Interpretation:

- the search surface was correctly narrowed
- there was no template-family waste
- most candidate attempts died on insufficient sample support
- only `10` candidates became bridge-evaluable

Statistical conclusion at this stage:

"There is some evidence, but most combinations are too thin. Continue to the candidate rows."

## Step 4: Inspect The Candidate Parquet

Candidate output:

- [phase2_candidates.parquet](../data/reports/phase2/codex_real_btc_vol_shock_202211_202212_20260328_5/phase2_candidates.parquet)

Top rows by `t_stat`:

1. `only_if_regime`, `short`, `60m`, `n=61`, `t_stat=2.2958`, after-cost expectancy `9.43`, robustness `0.3882`, stress survival `0.0`
2. `mean_reversion`, `short`, `60m`, `n=64`, `t_stat=2.2601`, after-cost expectancy `8.67`, robustness `0.3892`, stress survival `0.0`
3. `continuation`, `short`, `60m`, same metric profile
4. `trend_continuation`, `short`, `60m`, same metric profile
5. `volatility_expansion_follow`, `short`, `60m`, same metric profile

Critical candidate columns to inspect:

- `event_type`
- `rule_template`
- `direction`
- `horizon`
- `n`
- `t_stat`
- `after_cost_expectancy_per_trade`
- `stressed_after_cost_expectancy_per_trade`
- `robustness_score`
- `stress_test_survival`
- `gate_bridge_tradable`
- `bridge_eval_status`

Interpretation:

- the slice found plausible short-side ideas
- the best rows are statistically interesting
- none are bridge-tradable
- the real blocker is not `t_stat`; it is weak robustness and zero stress survival

## Step 5: Inspect The Summaries

Summary artifacts:

- [discovery_quality_summary.json](../data/reports/phase2/codex_real_btc_vol_shock_202211_202212_20260328_5/discovery_quality_summary.json)
- [funnel_summary.json](../data/reports/codex_real_btc_vol_shock_202211_202212_20260328_5/funnel_summary.json)

Key summary facts:

- `phase2_candidates = 10`
- `bridge_evaluable = 10`
- `bridge_pass_val = 0`
- `wf_survivors = 0`
- only family present is `VOL_SHOCK`

Interpretation:

- attribution is clean
- nothing from unrelated families polluted the run
- all candidates died before bridge pass

## The Correct Final Interpretation

Separate the three layers explicitly.

### Mechanical

The run succeeded, artifacts reconciled, and runtime postflight passed with `0` violations.

### Statistical

`VOL_SHOCK` materialized `128` events, `80` hypotheses were evaluated cleanly, and `10` candidates survived phase-2 filtering. The best short `60m` rows had `t_stat` above `2.0` and positive after-cost expectancy.

### Deployment

Nothing was deployable. All `10` bridge-evaluable rows failed bridge tradability because robustness stayed around `0.39` and stress survival stayed at `0.0`.

That is the key lesson:

"A run can be mechanically correct and statistically interesting while still failing the deployment bar."

## Why This Is A Good Training Example

This run is useful for new researchers because it shows all three outcomes at once:

- pipeline health: yes
- evidence exists: yes
- bridge-worthy candidate: no

That is a normal and informative research result.

## What The Next Action Should Be

The next action from this run is `explore`, not `exploit`.

Reason:

- the system is working
- the event is real
- the edge is not robust enough

Good follow-up questions:

- does the same event behave better in another window
- does a tighter context improve robustness
- does the signal only work in a specific regime subset

Bad follow-up questions:

- can we ignore bridge thresholds
- can we call this good because `t_stat > 2`
- can we broaden the run to hide the failure

## How To Use This Example

If you are new, open these files in order and write one sentence after each:

1. [run_manifest.json](../data/runs/codex_real_btc_vol_shock_202211_202212_20260328_5/run_manifest.json)
2. [vol_shock_relaxation_events.parquet](../data/reports/vol_shock_relaxation/codex_real_btc_vol_shock_202211_202212_20260328_5/vol_shock_relaxation_events.parquet)
3. [phase2_diagnostics.json](../data/reports/phase2/codex_real_btc_vol_shock_202211_202212_20260328_5/phase2_diagnostics.json)
4. [phase2_candidates.parquet](../data/reports/phase2/codex_real_btc_vol_shock_202211_202212_20260328_5/phase2_candidates.parquet)
5. [funnel_summary.json](../data/reports/codex_real_btc_vol_shock_202211_202212_20260328_5/funnel_summary.json)

If your five sentences do not clearly answer:

- what was tested
- what survived
- why the survivors still failed

then reread [05_ARTIFACTS_AND_INTERPRETATION.md](05_ARTIFACTS_AND_INTERPRETATION.md) and [06_QUALITY_GATES_AND_PROMOTION.md](06_QUALITY_GATES_AND_PROMOTION.md).
