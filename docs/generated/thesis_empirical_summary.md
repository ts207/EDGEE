# Thesis empirical summary

This pass consumes real promotion evidence bundles when they exist and maps them onto the founding seed queue.
Unlike the governance-only Block B scorecards, this artifact can clear a thesis when valid empirical evidence, holdout support, and confounder coverage are present.

- candidates_reviewed: `12`
- empirical_matches: `5`
- decision_counts: `needs_more_evidence=7`, `paper_candidate=4`, `seed_promote=1`

## Key conclusion

5 candidate(s) clear empirical seed promotion gates under the current evidence corpus.

## Top empirical candidates

| Candidate | Bundles | Coverage | Total score | Decision | Evidence gaps | Next action |
|---|---:|---:|---:|---|---|---|
| THESIS_LIQUIDATION_CASCADE | 2 | 1.00 | 37 | paper_candidate |  | run_paper_promotion_review |
| THESIS_LIQUIDITY_VACUUM | 2 | 1.00 | 37 | paper_candidate |  | run_paper_promotion_review |
| THESIS_VOL_SHOCK | 2 | 1.00 | 37 | paper_candidate |  | run_paper_promotion_review |
| THESIS_VOL_SHOCK_LIQUIDITY_CONFIRM | 2 | 1.00 | 36 | paper_candidate |  | run_paper_promotion_review |
| THESIS_LIQUIDITY_VACUUM_CASCADE_CONFIRM | 1 | 1.00 | 33 | seed_promote |  | package_seed_thesis |
| THESIS_BASIS_DISLOC | 0 | 0.00 | 22 | needs_more_evidence | empirical_evidence_bundle_missing|holdout_check_missing|confounder_sanity_check_missing | run_empirical_event_study |
| THESIS_FND_DISLOC | 0 | 0.00 | 22 | needs_more_evidence | empirical_evidence_bundle_missing|holdout_check_missing|confounder_sanity_check_missing | run_empirical_event_study |
| THESIS_BASIS_FND_CONFIRM | 0 | 0.00 | 21 | needs_more_evidence | empirical_evidence_bundle_missing|required_contract_coverage_incomplete|holdout_check_missing|confounder_sanity_check_missing | run_empirical_event_study |
