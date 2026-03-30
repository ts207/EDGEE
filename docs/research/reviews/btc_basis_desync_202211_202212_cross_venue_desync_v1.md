# Experiment Review

## Run Scope

- Run ID: `btc_cross_venue_desync_202211_202212_20260330_v1`
- Program ID: `btc_basis_disloc_campaign`
- Hypothesis ID: `btc_basis_desync_202211_202212_cross_venue_desync_v1`
- Canonical regime: `BASIS_FUNDING_DISLOCATION`
- Mechanism: temporary cross-venue desync should converge after routing and positioning friction normalizes.
- Tradable expression: Long `BTCUSDT` spot proxy, `5m`, `12` bars, `1`-bar entry lag.
- What changed relative to prior basis runs: used `CROSS_VENUE_DESYNC` with the compatible `desync_repair` template instead of `basis_repair`.

## Files And Artifacts Reviewed

- Run manifest: `data/runs/btc_cross_venue_desync_202211_202212_20260330_v1/run_manifest.json`
- Event summary: `data/reports/cross_venue_desync/btc_cross_venue_desync_202211_202212_20260330_v1/cross_venue_desync_summary.json`
- Edge summary: `data/reports/cross_venue_desync/btc_cross_venue_desync_202211_202212_20260330_v1/cross_venue_desync_edge_summary.json`
- Phase-2 diagnostics: `data/reports/phase2/btc_cross_venue_desync_202211_202212_20260330_v1/phase2_diagnostics.json`
- Evaluated hypotheses: `data/reports/phase2/btc_cross_venue_desync_202211_202212_20260330_v1/hypotheses/BTCUSDT/evaluated_hypotheses.parquet`
- Gate failures: `data/reports/phase2/btc_cross_venue_desync_202211_202212_20260330_v1/hypotheses/BTCUSDT/gate_failures.parquet`
- Promotion diagnostics: `data/reports/promotions/btc_cross_venue_desync_202211_202212_20260330_v1/promotion_diagnostics.json`
- Conditional expectancy: `data/reports/expectancy/btc_cross_venue_desync_202211_202212_20260330_v1/conditional_expectancy.json`

## Key Outputs

- Raw event count: `3`
- Evaluated hypothesis count: `1`
- Candidate count: `0`
- Promoted count: `0`
- Valid sample count: `n=3`
- Split counts: `train=0`, `validation=0`, `test=0`
- Primary reject gate: `min_sample_size`

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

- What the run supports: The detector path, event registry, template compatibility, and proposal execution path are mechanically clean.
- What the run contradicts: The bounded slice does not provide enough desync episodes to evaluate the convergence claim statistically.
- Was the mechanism visible in the intended regime: Only mechanically. The event report shows `3` desync events and a descriptive best net mean, but phase-2 rejects the hypothesis before any valid inference.
- Did the tradable expression actually isolate the mechanism: Not enough to matter; sample scarcity dominates the result.

## Data And Contract Quality

- Missing artifacts: None.
- Schema failures: None.
- Manifest/report disagreements: None found.
- Regime-routing inconsistencies: None found in the executed scope.
- Promotion or expectancy path defects: None. Both executed and correctly reported zero evidence.

## Decision

- Decision: `kill`
- Evidence strength: `weak`
- Why: This bounded desync slice produced only `3` events, failed `min_sample_size`, and generated no candidate, promotion, or expectancy evidence. The branch does not justify further broadening under the same Priority 3 thesis family.

## Next Bounded Step

- Exact next run or repair: Move to Priority 4 and test `LIQUIDITY_VACUUM` with `tail_risk_avoid` as an abstention-first run. Do not combine abstention and rebound in one experiment.
- Same regime: `no`
- Same mechanism family: `no`
- Same expression unless explicitly justified: `n/a`
