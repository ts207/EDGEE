# THESIS_LIQUIDITY_VACUUM

- Promotion class: `paper_promoted`
- Deployment state: `paper_only`
- Event family: `LIQUIDITY_VACUUM`
- Tier / role: `A` / `trigger`
- Symbols: BTCUSDT, ETHUSDT
- Timeframe: `5m`
- Horizon: 8-24 bars
- Evidence freshness date: `2026-04-01`
- Review due date: `2026-06-30`
- Staleness class: `fresh`

## What it is

When LIQUIDITY_VACUUM fires under governed contract semantics, expect the declared post-event path to materialize over 8-24 bars unless volume returns above-median within 1 bar of event end; range compresses below 0.8 * range_med within 2 bars

## Why it should work

Expect unstable liquidity conditions that either amplify the move or attract a repair response.

## Trigger

LIQUIDITY_VACUUM

## Invalidation

Volume returns above-median within 1 bar of event end; Range compresses below 0.8 * range_med within 2 bars

## Evidence summary

- sample_size_total: `1083`
- validation_samples: `601`
- test_samples: `482`
- median_estimate_bps: `101.432`
- median_net_expectancy_bps: `95.432`
- best_q_value: `0.0`
- best_stability_score: `0.932391`

## Confounders checked

- session_transition
- realized_vol_regime

## Evidence gaps

- none

## Notes

- Raw-data evidence uses post-event absolute move after low-volume, wide-range continuation bars following the initiating shock.
