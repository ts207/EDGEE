# Worked Example: Historical Mechanical Failure

This walkthrough shows how to recognize a run that is not trustworthy even though the top-level process exited with `status = success`.

It uses a historical run from March 28, 2026:

- run id: `codex_real_btc_vol_shock_20260328_4`
- manifest: [run_manifest.json](/home/irene/Edge/data/runs/codex_real_btc_vol_shock_20260328_4/run_manifest.json)

This example is valuable because it shows a failure mode that new researchers commonly miss:

"The command finished, candidates were written, but the run was still mechanically invalid."

## The Intended Question

The intended question was narrow:

"On BTCUSDT 5m bars from January 1, 2024 through January 31, 2024, does `VOL_SHOCK` produce any usable candidates?"

Boundaries:

- one symbol: `BTCUSDT`
- one timeframe: `5m`
- one event pin: `VOL_SHOCK`
- one month: January 1, 2024 to January 31, 2024

That sounds narrow. The failure was that the execution did not stay narrow.

## Step 1: Read The Manifest First

Open:

- [run_manifest.json](/home/irene/Edge/data/runs/codex_real_btc_vol_shock_20260328_4/run_manifest.json)

Important fields:

- `status = success`
- `runtime_invariants_status = violations`
- `runtime_postflight_status = failed`
- `runtime_postflight_violation_count = 134`
- `runtime_watermark_violation_count = 134`
- `runtime_postflight_event_count = 67`

Correct interpretation:

- the process completed
- the run is not mechanically clean
- the runtime audit found 134 violations

This is the first training rule:

`status = success` is not enough. Runtime postflight can still invalidate the run.

## Step 2: Check Whether Scope Stayed Narrow

Open:

- [phase2_search_engine.log](/home/irene/Edge/data/runs/codex_real_btc_vol_shock_20260328_4/phase2_search_engine.log)

What the log shows:

- search spec used: `spec/search_space.yaml`
- generated `6048` hypotheses
- search surface included `events=35 states=15 transitions=6 features=10`
- `16128` invalid hypothesis specs were skipped
- rejections included:
  - `validation_error: 11760`
  - `missing_state_column: 1680`
  - `missing_transition_state_column: 336`
  - `missing_feature_column: 2352`

Correct interpretation:

- the run did not stay `VOL_SHOCK`-scoped
- it expanded into the broad global search surface
- huge invalid-generation volume is a warning sign that the search spec did not match the intended question

This is the second training rule:

If the question is narrow but the search engine expands to the global frontier, attribution is already compromised.

## Step 3: Read The Discovery Summary

Open:

- [discovery_quality_summary.json](/home/irene/Edge/data/reports/phase2/codex_real_btc_vol_shock_20260328_4/discovery_quality_summary.json)
- [funnel_summary.json](/home/irene/Edge/data/reports/codex_real_btc_vol_shock_20260328_4/funnel_summary.json)

What they show:

- total phase-2 candidates: `42`
- event families present:
  - `FEATURE_FUNDING_ABS_PCT_0_95`
  - `TRANSITION_CHOP_STATE_TRENDING_STATE`
  - `TRANSITION_TRENDING_STATE_CHOP_STATE`
  - `VOL_SHOCK`
- `VOL_SHOCK` itself contributed `0` phase-2 candidates
- all bridge-pass counts were `0`

Correct interpretation:

- the output was polluted by unrelated triggers
- the run cannot answer the original narrow `VOL_SHOCK` question cleanly
- even if one of those unrelated candidates looked good, it would still not answer the actual run objective

This is the third training rule:

If unrelated families dominate the output, the run may be statistically interesting but still operationally wrong for the question asked.

## Step 4: Check Event-Specific Stages

Open:

- [bridge_evaluate_phase2__VOL_SHOCK_5m.log](/home/irene/Edge/data/runs/codex_real_btc_vol_shock_20260328_4/bridge_evaluate_phase2__VOL_SHOCK_5m.log)

It says:

- "No candidates found for evaluation across all symbols for `VOL_SHOCK`. Skipping evaluation."

Correct interpretation:

- the dedicated `VOL_SHOCK` path produced nothing bridge-evaluable
- the 42 candidates came from the broad search-engine path, not from the narrow event-specific path

That means the run was doubly misleading:

- the intended event pin did not produce usable candidates
- the broad search engine still produced unrelated rows that could distract a careless reader

## Step 5: Notice The Additional Warnings

The same search log also contained repeated warnings from the regime labeler:

- trend and spread state columns were missing for expected dimensions
- those dimensions were labelled `unknown_<dim>` for all bars

Correct interpretation:

- regime robustness surfaces were degraded
- any regime-conditioned interpretation from this run is weaker than it appears

This was another mechanical-quality issue, not just a statistical one.

## The Correct Final Interpretation

Separate the conclusions the same way you would for a good run.

### Mechanical

The run is not valid for decision-making. Runtime postflight failed with `134` violations, and the narrow event pin did not constrain the search engine.

### Statistical

The search engine produced `42` candidates, but they came from unrelated triggers after broad search expansion. That means the candidate set does not cleanly answer the intended `VOL_SHOCK` question.

### Deployment

Nothing passed bridge, and deployment interpretation should stop after the mechanical failure anyway.

## Why This Example Matters

This run teaches three durable habits:

1. never trust `status = success` alone
2. always confirm the search scope actually matched the question
3. reject runs whose artifact trail answers a different question than the one you intended to ask

## Historical Note

This specific failure mode was later repaired. The repository now narrows event-pinned search runs correctly and avoids this broad-search leakage for `VOL_SHOCK`.

That does not make the old run acceptable. It makes it a useful training example.

## What The Next Action Should Have Been

The correct next action from this historical run was `repair`, not `explore` or `exploit`.

Why:

- runtime invariants were broken
- the search scope was wrong
- the event-specific question was not answered cleanly

The right repair path was:

1. fix runtime postflight semantics for next-bar detector events
2. constrain event-pinned search runs to event-scoped search specs
3. rerun the same bounded slice

That is exactly the pattern you should follow whenever a run is mechanically invalid:

- repair first
- rerun second
- interpret only after artifacts reconcile
