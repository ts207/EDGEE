# Experiment Review

## Run Scope

- Run ID: `btc_basis_norm_202211_202212_20260330_v2`
- Program ID: `btc_basis_disloc_campaign`
- Hypothesis ID: `btc_basis_disloc_202211_202212_funding_normalization_v1`
- Canonical regime: `BASIS_FUNDING_DISLOCATION`
- Mechanism: Funding normalization should lead to basis repair and a short-horizon spot rebound.
- Tradable expression: Long `BTCUSDT` spot, `5m`, `12` bars, `1`-bar entry lag.
- What changed relative to the prior run: Re-ran the same bounded proposal after repairing proposal-driven promotion staging, zero-row promotion artifact schema output, and misleading phase-2 invalid-reason logging.

## Files And Artifacts Reviewed

- Run manifest: `data/runs/btc_basis_norm_202211_202212_20260330_v2/run_manifest.json`
- Phase-2 diagnostics: `data/reports/phase2/btc_basis_norm_202211_202212_20260330_v2/phase2_diagnostics.json`
- Phase-2 candidates: `data/reports/phase2/btc_basis_norm_202211_202212_20260330_v2/phase2_candidates.parquet`
- Evaluated hypotheses: `data/reports/phase2/btc_basis_norm_202211_202212_20260330_v2/hypotheses/BTCUSDT/evaluated_hypotheses.parquet`
- Promotion diagnostics: `data/reports/promotions/btc_basis_norm_202211_202212_20260330_v2/promotion_diagnostics.json`
- Promotion decisions: `data/reports/promotions/btc_basis_norm_202211_202212_20260330_v2/promotion_decisions.parquet`
- Promotion audit: `data/reports/promotions/btc_basis_norm_202211_202212_20260330_v2/promotion_statistical_audit.parquet`
- Evidence bundles: `data/reports/promotions/btc_basis_norm_202211_202212_20260330_v2/evidence_bundles.jsonl`
- Blueprint/spec artifacts: `none`
- Comparison report: `not requested`

## Key Outputs

- Candidate count: `0`
- Survivor count: `0`
- Promoted count: `0`
- Regime metadata present: `not materially testable because no candidate rows survived`
- Distinct `candidate_id` vs `hypothesis_id`: `n/a`
- Primary reject gate: `incompatible_template_family`
- Recommended next action from diagnostics: `KEEP_RESEARCH` in checklist; research verdict remains `modify`

## Cost-Aware Result Analysis

- After-cost expectancy: `no evidence`
- Stressed after-cost expectancy: `no evidence`
- Cost survivability: `failed to establish`
- Turnover realism: `not testable with zero surviving rows`
- Slippage/funding realism: `not testable with zero surviving rows`
- Does the edge survive realistic execution assumptions: `no`

## Mechanism Confirmation Or Disconfirmation

- What the run supports: The detector materialized one `FUNDING_NORMALIZATION_TRIGGER` event cleanly in the intended window, and the repaired proposal-driven research path now emits a complete promotion bundle and passes experiment verification.
- What the run contradicts: This exact event/template pairing did not reach a valid hypothesis evaluation; the single row failed as `incompatible_template_family`.
- Was the mechanism visible in the intended regime: Only at the detector layer, not at the candidate or expectancy layer.
- Did the tradable expression actually isolate the mechanism: No; the template/event pair failed before producing a testable candidate.

## Data And Contract Quality

- Missing artifacts: None in the reviewed v2 run.
- Schema failures: None in the reviewed v2 run; experiment verification passed after promotion artifact repair.
- Manifest/report disagreements: None in the repaired v2 run; the phase-2 log now reports `incompatible_template_family=1`, which matches the evaluated-hypotheses artifact and diagnostics.
- Regime-routing inconsistencies: None found in the executed scope.
- Suspected fixture or pipeline defects: The v1 defects were repaired locally before v2: proposal-driven promotion staging, research-mode promotion acceptance, zero-row promotion artifact schema completion, and evaluator invalid-reason logging.

## Logical Inconsistencies

- Any claim that the outputs do not support: Any statement that the mechanism has positive after-cost evidence in this slice.
- Any place the review would overstate evidence: Treating the single detected event as meaningful market evidence rather than detector-level support only.
- Any place execution truth is being conflated with research evidence: Passing experiment verification confirms contract integrity only; it does not add statistical support when the only evaluated hypothesis is invalid.

## Local Fix Candidates

- Fix candidate: None remaining that block this bounded research slice.
- Touched path: `n/a`
- Why this is local and contract-preserving: The run-critical defects uncovered in v1 were repaired and verified before the v2 rerun.
- Required targeted verification: Already completed for the repaired staging, promotion bundle schema, and evaluator logging paths.

## Decision

- Decision: `modify`
- Evidence strength: `weak`
- Why: The mechanism is not disproven, but this exact slice yielded one event, zero valid metrics rows, zero candidates, zero expectancy evidence, and the only evaluated row failed on `incompatible_template_family`.

## Next Bounded Step

- Exact next run or repair: Keep the same regime and symbol but change one thing only: either swap to an event-compatible template for `FUNDING_NORMALIZATION_TRIGGER` or keep `basis_repair` and move to the hypothesis-documented fallback event family `SPOT_PERP_BASIS_SHOCK`, then run a single wider 2022 window.
- Same regime: `yes`
- Same mechanism family: `yes`
- Same expression unless explicitly justified: `yes`
- Stop condition before any broader search: Do not broaden to multiple events or templates in one run; the next attempt should isolate template compatibility as the only changed dimension.
