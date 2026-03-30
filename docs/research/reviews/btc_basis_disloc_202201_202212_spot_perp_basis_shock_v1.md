# Experiment Review

## Run Scope

- Run ID: `btc_basis_shock_2022_20260330_v1`
- Program ID: `btc_basis_disloc_campaign`
- Hypothesis ID: `btc_basis_disloc_202201_202212_spot_perp_basis_shock_v1`
- Canonical regime: `BASIS_FUNDING_DISLOCATION`
- Mechanism: Spot-perp basis shock should mean-revert through basis repair and a short-horizon spot rebound.
- Tradable expression: Long `BTCUSDT` spot, `5m`, `12` bars, `1`-bar entry lag.
- What changed relative to the prior run: Widened only the date range from November to December 2022 to all of 2022.

## Files And Artifacts Reviewed

- Run manifest: `data/runs/btc_basis_shock_2022_20260330_v1/run_manifest.json`
- Phase-2 diagnostics: `data/reports/phase2/btc_basis_shock_2022_20260330_v1/phase2_diagnostics.json`
- Evaluated hypotheses: `data/reports/phase2/btc_basis_shock_2022_20260330_v1/hypotheses/BTCUSDT/evaluated_hypotheses.parquet`
- Promotion diagnostics: `data/reports/promotions/btc_basis_shock_2022_20260330_v1/promotion_diagnostics.json`
- Conditional expectancy: `data/reports/expectancy/btc_basis_shock_2022_20260330_v1/conditional_expectancy.json`

## Key Outputs

- Raw event count: `24`
- Evaluated hypothesis count: `1`
- Candidate count: `0`
- Promoted count: `0`
- Primary reject gate: `min_sample_size`
- Exact evaluated sample count: `n=24`

## Cost-Aware Result Analysis

- After-cost expectancy: `no evidence`
- Stressed after-cost expectancy: `no evidence`
- Cost survivability: `failed to establish`
- Does the edge survive realistic execution assumptions: `no`

## Mechanism Confirmation Or Disconfirmation

- What the run supports: The compatible companion event can be detected across the full-year 2022 regime slice and produces more observations than the short window.
- What the run contradicts: Even the full-year 2022 slice does not clear the repository minimum sample threshold for this BTC spot expression.
- Was the mechanism visible in the intended regime: Detector-level only; no candidate or expectancy evidence emerged.
- Did the tradable expression actually isolate the mechanism: No deployable evidence was established.

## Data And Contract Quality

- Missing artifacts: None.
- Schema failures: None; experiment verification passed.
- Manifest/report disagreements: None.
- Regime-routing inconsistencies: None found in the executed scope.

## Decision

- Decision: `kill`
- Evidence strength: `weak`
- Why: The exact mechanism family was tested through the compatible event and a wider 2022 window, but still failed the hard `min_n=30` gate with only `n=24`. Continuing would be sample-chasing rather than a bounded hypothesis test.

## Next Bounded Step

- Exact next run or repair: Stop this spot-expression mechanism family and move to the next backlog item rather than broadening time, symbols, or template scope again.
- Same regime: `no`
- Same mechanism family: `no`
- Same expression unless explicitly justified: `n/a`
