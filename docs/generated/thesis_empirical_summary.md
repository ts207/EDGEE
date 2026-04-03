# Thesis empirical summary

This pass consumes real promotion evidence bundles when they exist and maps them onto the founding seed queue.
Unlike the governance-only Block B scorecards, this artifact can clear a thesis when valid empirical evidence, holdout support, and confounder coverage are present.

- candidates_reviewed: `13`
- empirical_matches: `4`
- decision_counts: `needs_more_evidence=5`, `needs_repair=4`, `seed_promote=4`

## Key conclusion

4 candidate(s) clear empirical seed promotion gates under the current evidence corpus.

## Top empirical candidates

| Candidate | Bundles | Coverage | Total score | Decision | Evidence gaps | Next action |
|---|---:|---:|---:|---|---|---|
| THESIS_LIQUIDATION_CASCADE | 2 | 1.00 | 33 | seed_promote |  | package_seed_thesis |
| THESIS_LIQUIDITY_VACUUM | 2 | 1.00 | 33 | seed_promote |  | package_seed_thesis |
| THESIS_VOL_SHOCK | 2 | 1.00 | 33 | seed_promote |  | package_seed_thesis |
| THESIS_VOL_SHOCK_LIQUIDITY_CONFIRM | 2 | 1.00 | 30 | seed_promote | direct_pair_event_study_missing | package_seed_thesis |
| THESIS_EP_LIQUIDITY_SHOCK | 0 | 0.00 | 19 | needs_more_evidence | empirical_evidence_bundle_missing|required_contract_coverage_incomplete|holdout_check_missing|confounder_sanity_check_missing | run_empirical_event_study |
| THESIS_EP_VOLATILITY_BREAKOUT | 0 | 0.00 | 19 | needs_more_evidence | empirical_evidence_bundle_missing|required_contract_coverage_incomplete|holdout_check_missing|confounder_sanity_check_missing | run_empirical_event_study |
| THESIS_BASIS_DISLOC | 0 | 0.00 | 18 | needs_more_evidence | empirical_evidence_bundle_missing|holdout_check_missing|confounder_sanity_check_missing | run_empirical_event_study |
| THESIS_FND_DISLOC | 0 | 0.00 | 18 | needs_more_evidence | empirical_evidence_bundle_missing|holdout_check_missing|confounder_sanity_check_missing | run_empirical_event_study |
