# Quality Gates And Promotion

This repository uses multiple gate layers. You should know where a candidate died before you argue about its quality.

## Gate policy source

The maintained gate policy is [spec/gates.yaml](../spec/gates.yaml).

Code-side accessors live in [project/specs/gates.py](../project/specs/gates.py).

Promotion staging for thesis bootstrap lives in:

- [spec/promotion/seed_promotion_policy.yaml](../spec/promotion/seed_promotion_policy.yaml)
- [spec/promotion/founding_thesis_eval_policy.yaml](../spec/promotion/founding_thesis_eval_policy.yaml)

## Phase-2 gates

`gate_v1_phase2` defines the main search filtering policy.

Important controls include:

- `max_q_value`
- `min_after_cost_expectancy_bps`
- `conservative_cost_multiplier`
- `require_sign_stability`
- `min_sample_size`
- regime ESS constraints
- timeframe consensus constraints

There are also profiles under `gate_v1_phase2_profiles`, including a `discovery` profile that is intentionally looser than promotion-oriented settings.

## Bridge gates

`gate_v1_bridge` governs search-to-bridge tradability.

Important controls include:

- `edge_cost_k`
- `stressed_cost_multiplier`
- `min_validation_trades`
- `search_bridge_min_t_stat`
- `search_bridge_min_robustness_score`
- `search_bridge_min_regime_stability_score`
- `search_bridge_min_stress_survival`
- `search_bridge_stress_cost_buffer_bps`

These gates are materially stricter than simple discovery survival.

## Thesis promotion ladder

A candidate that survives phase 2 still is not automatically promotion-worthy.

Use this ladder:

1. `candidate`
   - structured idea or queue entry
2. `tested`
   - bounded claim with testing artifacts but not yet packaged
3. `seed_promoted`
   - packaged for monitor-only / bootstrap use
4. `paper_promoted`
   - packaged and eligible for paper-style retrieval / review
5. `production_promoted`
   - rare, highest bar

### Important restrictions

- `seed_promoted` is enough for thesis store membership and overlap graph generation.
- `seed_promoted` is not enough for production deployment.
- `paper_promoted` still does not imply production readiness.
- `deployment_state` further narrows what a packaged thesis may be used for (`monitor_only`, `paper_only`, etc.).

## Bootstrap-specific gates

The bootstrap lane adds evidence and packaging requirements on top of discovery:

- founding queue membership in `promotion_seed_inventory.*`
- testing scorecards in `thesis_testing_scorecards.*`
- empirical evidence in `thesis_empirical_scorecards.*`
- canonical evidence bundles under `data/reports/promotions/<thesis_id>/evidence_bundles.jsonl`
- packaging summary and thesis cards before the thesis store is treated as authoritative

A thesis that has not cleared these bootstrap steps must not be treated as a canonical packaged edge.

## Fallback gates

`gate_v1_fallback` exists for alternate filtering logic when fallback behavior is required. It is not the default interpretation surface for a normal narrow research run.

## Promotion discipline

Promotion-oriented reasoning should ask:

- did the candidate survive phase 2
- did bridge tradability survive
- did negative controls behave acceptably
- did stressed expectancy remain positive
- is there enough holdout and confounder coverage for the intended thesis class
- does the packaging class match the evidence class

## Common analytical mistakes

New researchers often stop at:

- event count exists
- `t_stat` is above 2
- after-cost expectancy is positive

That is not sufficient in this repo. A candidate still fails if robustness and stress-survival are weak.

The current bootstrap lane adds two more common mistakes to avoid:

- treating `seed_promoted` as equivalent to `paper_promoted`
- treating derived or bridge evidence as equivalent to direct paired-event evidence

## Practical reading rule

When you see a candidate or thesis row, identify all five statuses:

1. phase-2 statistical survival
2. bridge tradability
3. thesis testing status
4. promotion class
5. deployment state / packaging relevance

Do not compress these into a single "good" or "bad" label.
