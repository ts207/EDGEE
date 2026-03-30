# Quality Gates And Promotion

This repository uses multiple gate layers. You should know where a candidate died before you argue about its quality.

## Gate Policy Source

The maintained gate policy is [spec/gates.yaml](../spec/gates.yaml).

Code-side accessors live in [project/specs/gates.py](../project/specs/gates.py).

## Phase-2 Gates

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

## Bridge Gates

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

## Fallback Gates

`gate_v1_fallback` exists for alternate filtering logic when fallback behavior is required. It is not the default interpretation surface for a normal narrow research run.

## Promotion Discipline

A candidate that survives phase 2 still is not automatically promotion-worthy.

Promotion-oriented reasoning should ask:

- did the candidate survive bridge
- did negative controls behave acceptably
- did stressed expectancy remain positive
- is the edge reproducible enough to carry into strategy packaging or live-adjacent workflows

## Common Analytical Mistake

New researchers often stop at:

- event count exists
- `t_stat` is above 2
- after-cost expectancy is positive

That is not sufficient in this repo. A candidate still fails if robustness and stress-survival are weak.

## Practical Reading Rule

When you see a candidate row, identify all four statuses:

1. phase-2 statistical survival
2. bridge tradability
3. promotion relevance
4. packaging or export relevance

Do not compress these into a single "good" or "bad" label.
