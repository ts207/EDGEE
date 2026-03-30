# Experiment Review

## Run Scope

- Run ID: `btc_forced_flow_exhaustion_202211_202212_20260330_v1`
- Program ID: `btc_exhaustion_campaign`
- Hypothesis ID: `btc_exhaustion_202211_202212_forced_flow_exhaustion_v1`
- Canonical regime: `TREND_FAILURE_EXHAUSTION`
- Mechanism: forced flow should locally exhaust and allow a short-horizon reversal.
- Tradable expression: Long `BTCUSDT` spot after `FORCED_FLOW_EXHAUSTION`, `5m`, `12` bars, `1`-bar entry lag.
- Important setup detail: the backlog-framed regime-plus-event proposal was blocked by a non-authoritative dependency on `FLOW_EXHAUSTION_PROXY`, so the executed run was narrowed to the explicit event-only path `FORCED_FLOW_EXHAUSTION`.

## Files And Artifacts Reviewed

- Run manifest: `data/runs/btc_forced_flow_exhaustion_202211_202212_20260330_v1/run_manifest.json`
- Event summary: `data/reports/directional_exhaustion_after_forced_flow/btc_forced_flow_exhaustion_202211_202212_20260330_v1/forced_flow_exhaustion_summary.json`
- Phase-2 diagnostics: `data/reports/phase2/btc_forced_flow_exhaustion_202211_202212_20260330_v1/phase2_diagnostics.json`
- Phase-2 log: `data/runs/btc_forced_flow_exhaustion_202211_202212_20260330_v1/phase2_search_engine.log`
- Evaluated hypotheses: `data/reports/phase2/btc_forced_flow_exhaustion_202211_202212_20260330_v1/hypotheses/BTCUSDT/evaluated_hypotheses.parquet`
- Gate failures: `data/reports/phase2/btc_forced_flow_exhaustion_202211_202212_20260330_v1/hypotheses/BTCUSDT/gate_failures.parquet`
- Promotion diagnostics: `data/reports/promotions/btc_forced_flow_exhaustion_202211_202212_20260330_v1/promotion_diagnostics.json`
- Conditional expectancy: `data/reports/expectancy/btc_forced_flow_exhaustion_202211_202212_20260330_v1/conditional_expectancy.json`

## Key Outputs

- Raw event count: `0`
- Evaluated hypothesis count: `1`
- Candidate count: `0`
- Promoted count: `0`
- Valid sample count: `n=0`
- Split counts: `train=0`, `validation=0`, `test=0`
- Primary reject gate: `missing_event_column`

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

- What the run supports: The narrowed event-only proposal is executable and the pipeline completed cleanly.
- What the run contradicts: Nothing statistical. The bounded slice never reached a real reversal test because the detector produced `0` events and phase 2 recorded `missing_event_column`.
- Was the mechanism visible in the intended regime: No. There were no detected `FORCED_FLOW_EXHAUSTION` episodes in this bounded BTCUSDT 5m window.
- Did the tradable expression actually isolate the mechanism: No; detector scarcity dominated before the template could be evaluated.

## Data And Contract Quality

- Missing artifacts: None.
- Schema failures: None.
- Manifest/report disagreements: None found.
- Mechanical defect discovered during planning: Adding the canonical regime caused proposal validation to reach for `FLOW_EXHAUSTION_PROXY`, which is not in the authoritative event registry.
- Mechanical defect observed during execution: The event stage wrote a valid summary with `rows=0`, but phase 2 then failed the hypothesis as `missing_event_column`.

## Decision

- Decision: `hold`
- Evidence strength: `weak`
- Why: This is not a meaningful statistical rejection of the exhaustion-reversal idea. It is a mechanically clean zero-event slice with an additional regime-surface registry defect, so broadening this branch inside the current session is not justified.

## Next Bounded Step

- Exact next run or repair: Track the `FLOW_EXHAUSTION_PROXY` authoritative-registry defect separately. No further bounded backlog run remains justified in the current sweep.
- Same regime: `no`
- Same mechanism family: `no`
- Same expression unless explicitly justified: `n/a`
