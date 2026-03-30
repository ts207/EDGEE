# Experiment Review

## Run Scope

- Run ID: `btc_oi_flush_202211_202212_20260330_v1`
- Program ID: `btc_deleveraging_campaign`
- Hypothesis ID: `btc_deleveraging_202211_202212_oi_flush_v1`
- Canonical regime: `POSITIONING_UNWIND_DELEVERAGING`
- Mechanism: OI flush should mark exhaustion and lead to a short-horizon spot rebound.
- Tradable expression: Long `BTCUSDT` spot, `5m`, `12` bars, `1`-bar entry lag.
- What changed relative to the blocked primary proposal: Used the authoritative-registry fallback event `OI_FLUSH` after proposal validation rejected `POST_DELEVERAGING_REBOUND`.

## Files And Artifacts Reviewed

- Run manifest: `data/runs/btc_oi_flush_202211_202212_20260330_v1/run_manifest.json`
- Phase-2 diagnostics: `data/reports/phase2/btc_oi_flush_202211_202212_20260330_v1/phase2_diagnostics.json`
- Evaluated hypotheses: `data/reports/phase2/btc_oi_flush_202211_202212_20260330_v1/hypotheses/BTCUSDT/evaluated_hypotheses.parquet`
- Promotion diagnostics: `data/reports/promotions/btc_oi_flush_202211_202212_20260330_v1/promotion_diagnostics.json`
- Conditional expectancy: `data/reports/expectancy/btc_oi_flush_202211_202212_20260330_v1/conditional_expectancy.json`

## Key Outputs

- Raw event count: `40`
- Evaluated hypothesis count: `1`
- Candidate count: `0`
- Promoted count: `0`
- Valid sample count: `n=40`
- Split counts: `train=25`, `validation=10`, `test=5`
- Primary reject gate: `min_t_stat`

## Cost-Aware Result Analysis

- Mean return: `-43.0413 bps`
- Cost-adjusted return: `-45.0413 bps`
- t-stat: `-1.3004`
- p-value: `0.19344822`
- Robustness score: `0.2005`
- Stress score: `0.0`
- Hit rate: `0.35`
- After-cost expectancy: `no evidence`
- Does the edge survive realistic execution assumptions: `no`

## Mechanism Confirmation Or Disconfirmation

- What the run supports: The fallback event is mechanically valid, produced enough observations, and passed experiment verification.
- What the run contradicts: The intended long rebound expression is not just weak; it is directionally negative after costs in this bounded slice.
- Was the mechanism visible in the intended regime: Only as a valid evaluated row, not as a surviving or positive edge.
- Did the tradable expression actually isolate the mechanism: Yes well enough to reject the claimed long spot rebound for this slice.

## Data And Contract Quality

- Missing artifacts: None.
- Schema failures: None; experiment verification passed.
- Manifest/report disagreements: None.
- Regime-routing inconsistencies: None found in the executed scope.
- Separate repo issue discovered during setup: `POST_DELEVERAGING_REBOUND` is available in broader ontology surfaces but proposal validation rejects it because it is absent from the authoritative events registry used by the experiment engine.

## Decision

- Decision: `kill`
- Evidence strength: `moderate`
- Why: The run achieved a valid sample and clean contract path, but the observed return sign is opposite the proposed long rebound mechanism and does not survive the phase-2 statistical gate.

## Next Bounded Step

- Exact next run or repair: Stop this long rebound expression and move to the next backlog item. Track the `POST_DELEVERAGING_REBOUND` registry mismatch separately as a change-management issue rather than mixing it into edge research.
- Same regime: `no`
- Same mechanism family: `no`
- Same expression unless explicitly justified: `n/a`
