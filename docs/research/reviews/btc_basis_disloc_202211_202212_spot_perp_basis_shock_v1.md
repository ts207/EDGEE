# Experiment Review

## Run Scope

- Run ID: `btc_basis_shock_202211_202212_20260330_v1`
- Program ID: `btc_basis_disloc_campaign`
- Hypothesis ID: `btc_basis_disloc_202211_202212_spot_perp_basis_shock_v1`
- Canonical regime: `BASIS_FUNDING_DISLOCATION`
- Mechanism: Spot-perp basis shock should mean-revert through basis repair and a short-horizon spot rebound.
- Tradable expression: Long `BTCUSDT` spot, `5m`, `12` bars, `1`-bar entry lag.
- What changed relative to the prior run: Swapped only the event family from `FUNDING_NORMALIZATION_TRIGGER` to the compatible companion event `SPOT_PERP_BASIS_SHOCK`.

## Files And Artifacts Reviewed

- Run manifest: `data/runs/btc_basis_shock_202211_202212_20260330_v1/run_manifest.json`
- Phase-2 diagnostics: `data/reports/phase2/btc_basis_shock_202211_202212_20260330_v1/phase2_diagnostics.json`
- Evaluated hypotheses: `data/reports/phase2/btc_basis_shock_202211_202212_20260330_v1/hypotheses/BTCUSDT/evaluated_hypotheses.parquet`
- Promotion diagnostics: `data/reports/promotions/btc_basis_shock_202211_202212_20260330_v1/promotion_diagnostics.json`
- Conditional expectancy: `data/reports/expectancy/btc_basis_shock_202211_202212_20260330_v1/conditional_expectancy.json`

## Key Outputs

- Raw event count: `5`
- Evaluated hypothesis count: `1`
- Candidate count: `0`
- Promoted count: `0`
- Primary reject gate: `min_sample_size`
- Exact evaluated sample count: `n=5`

## Cost-Aware Result Analysis

- After-cost expectancy: `no evidence`
- Stressed after-cost expectancy: `no evidence`
- Cost survivability: `failed to establish`
- Does the edge survive realistic execution assumptions: `no`

## Mechanism Confirmation Or Disconfirmation

- What the run supports: The companion event is mechanically compatible with `basis_repair` and the proposal-driven research path remains contract-clean.
- What the run contradicts: The November to December 2022 slice is too small for this expression; compatibility alone did not yield a testable sample.
- Was the mechanism visible in the intended regime: Only at the detector layer.
- Did the tradable expression actually isolate the mechanism: Not enough observations to tell.

## Data And Contract Quality

- Missing artifacts: None.
- Schema failures: None; experiment verification passed.
- Manifest/report disagreements: None.
- Regime-routing inconsistencies: None found in the executed scope.

## Decision

- Decision: `modify`
- Evidence strength: `weak`
- Why: The failure mode improved from incompatible template wiring to a clean but undersampled event slice, which justifies one bounded date expansion and nothing broader.

## Next Bounded Step

- Exact next run or repair: Keep `SPOT_PERP_BASIS_SHOCK`, `basis_repair`, and the same BTC spot expression, and widen only the date window to full-year 2022.
- Same regime: `yes`
- Same mechanism family: `yes`
- Same expression unless explicitly justified: `yes`
