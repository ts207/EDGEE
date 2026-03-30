# Experiment Review

## Run Scope

- Run ID: `btc_forced_flow_exhaustion_202211_202212_20260330_v2`
- Program ID: `btc_exhaustion_campaign`
- Hypothesis ID: `btc_exhaustion_202211_202212_forced_flow_exhaustion_v2`
- Canonical regime: `TREND_FAILURE_EXHAUSTION`
- Mechanism: forced flow should locally exhaust and allow a short-horizon reversal.
- Tradable expression: Long `BTCUSDT` spot after `FORCED_FLOW_EXHAUSTION`, `5m`, `12` bars, `1`-bar entry lag.
- Purpose of this rerun: validate the repaired canonical-regime proposal path and confirm that a zero-event slice now fails as trigger scarcity rather than `missing_event_column`.

## Files And Artifacts Reviewed

- Run manifest: `data/runs/btc_forced_flow_exhaustion_202211_202212_20260330_v2/run_manifest.json`
- Event summary: `data/reports/directional_exhaustion_after_forced_flow/btc_forced_flow_exhaustion_202211_202212_20260330_v2/forced_flow_exhaustion_summary.json`
- Phase-2 diagnostics: `data/reports/phase2/btc_forced_flow_exhaustion_202211_202212_20260330_v2/phase2_diagnostics.json`
- Phase-2 log: `data/runs/btc_forced_flow_exhaustion_202211_202212_20260330_v2/phase2_search_engine.log`
- Evaluated hypotheses: `data/reports/phase2/btc_forced_flow_exhaustion_202211_202212_20260330_v2/hypotheses/BTCUSDT/evaluated_hypotheses.parquet`
- Gate failures: `data/reports/phase2/btc_forced_flow_exhaustion_202211_202212_20260330_v2/hypotheses/BTCUSDT/gate_failures.parquet`
- Promotion diagnostics: `data/reports/promotions/btc_forced_flow_exhaustion_202211_202212_20260330_v2/promotion_diagnostics.json`
- Conditional expectancy: `data/reports/expectancy/btc_forced_flow_exhaustion_202211_202212_20260330_v2/conditional_expectancy.json`

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

## Repair Validation Outcome

- Canonical-regime proposal validation: `pass`. The same branch now validates with `canonical_regimes: [TREND_FAILURE_EXHAUSTION]` included.
- Zero-event classification: `pass`. The evaluated hypothesis now fails as `no_trigger_hits`, not `missing_event_column`.
- Diagnostics improvement: `phase2_diagnostics.json` now reports `event_flag_columns_merged=2`, confirming the event signal surface was materialized even with zero hits.

## Decision

- Decision: `stop`
- Evidence strength: `weak`
- Why: The repo repair is validated, but the bounded slice still contains zero `FORCED_FLOW_EXHAUSTION` episodes and produces no candidate, promotion, or expectancy evidence.

## Next Bounded Step

- Exact next run or repair: Stop the current backlog sweep here. Future work should focus on broader date windows only after the repaired planning and zero-event semantics are accepted as the new baseline.
- Same regime: `no`
- Same mechanism family: `no`
- Same expression unless explicitly justified: `n/a`
