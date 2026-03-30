# Experiment Review

## Run Scope

- Run ID: `btc_forced_flow_exhaustion_2022_20260330_v3`
- Program ID: `btc_exhaustion_campaign`
- Hypothesis ID: `btc_exhaustion_202201_202212_forced_flow_exhaustion_v3`
- Canonical regime: `TREND_FAILURE_EXHAUSTION`
- Mechanism: forced flow should locally exhaust and allow a short-horizon reversal.
- Tradable expression: Long `BTCUSDT` spot after `FORCED_FLOW_EXHAUSTION`, `5m`, `12` bars, `1`-bar entry lag.
- Purpose of this rerun: widen only the date window to full-year 2022 after the repaired proposal and zero-event semantics were validated.

## Files And Artifacts Reviewed

- Run manifest: `data/runs/btc_forced_flow_exhaustion_2022_20260330_v3/run_manifest.json`
- Event summary: `data/reports/directional_exhaustion_after_forced_flow/btc_forced_flow_exhaustion_2022_20260330_v3/forced_flow_exhaustion_summary.json`
- Phase-2 diagnostics: `data/reports/phase2/btc_forced_flow_exhaustion_2022_20260330_v3/phase2_diagnostics.json`
- Phase-2 log: `data/runs/btc_forced_flow_exhaustion_2022_20260330_v3/phase2_search_engine.log`
- Evaluated hypotheses: `data/reports/phase2/btc_forced_flow_exhaustion_2022_20260330_v3/hypotheses/BTCUSDT/evaluated_hypotheses.parquet`
- Gate failures: `data/reports/phase2/btc_forced_flow_exhaustion_2022_20260330_v3/hypotheses/BTCUSDT/gate_failures.parquet`
- Promotion diagnostics: `data/reports/promotions/btc_forced_flow_exhaustion_2022_20260330_v3/promotion_diagnostics.json`
- Conditional expectancy: `data/reports/expectancy/btc_forced_flow_exhaustion_2022_20260330_v3/conditional_expectancy.json`

## Key Outputs

- Raw event count: `0`
- Evaluated hypothesis count: `1`
- Candidate count: `0`
- Promoted count: `0`
- Valid sample count: `n=0`
- Split counts: `train=0`, `validation=0`, `test=0`
- Primary reject gate: `no_trigger_hits`

## Cost-Aware Result Analysis

- Mean return: `0.0 bps`
- Cost-adjusted return: `0.0 bps`
- t-stat: `0.0`
- p-value: `1.0`
- Robustness score: `0.0`
- Stress score: `0.0`
- Hit rate: `0.0`
- After-cost expectancy: `no evidence`
- Does the edge survive realistic execution assumptions: `no`

## Mechanism Confirmation Or Disconfirmation

- What the run supports: The repaired canonical-regime proposal path remains clean on the wider window, and the zero-event slice still resolves correctly as `no_trigger_hits`.
- What the run contradicts: The branch is not merely narrow-window sparse. Full-year 2022 still produces zero `FORCED_FLOW_EXHAUSTION` episodes for BTCUSDT 5m in this repo.
- Was the mechanism visible in the intended regime: No.
- Did the tradable expression actually isolate the mechanism: Yes well enough to conclude there is no executable sample for this branch under the current detector behavior.

## Decision

- Decision: `kill`
- Evidence strength: `weak`
- Why: There is still no statistical test to run because the detector yields zero events even after widening to full-year 2022. The branch is exhausted as a practical research candidate in the current repo.

## Next Bounded Step

- Exact next run or repair: Stop this mechanism family in the current campaign sweep. Only revisit if detector semantics change materially or a different symbol/timeframe is justified explicitly.
- Same regime: `no`
- Same mechanism family: `no`
- Same expression unless explicitly justified: `n/a`
