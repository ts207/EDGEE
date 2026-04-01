# THESIS_LIQUIDITY_VACUUM_CASCADE_CONFIRM

- Promotion class: `seed_promoted`
- Deployment state: `monitor_only`
- Event family: `LIQUIDITY_VACUUM`
- Tier / role: `A` / `confirm`
- Symbols: BTCUSDT, ETHUSDT
- Timeframe: `5m`
- Horizon: 8-24 bars
- Evidence freshness date: `2026-04-01`
- Review due date: `2026-04-22`
- Staleness class: `fresh`

## What it is

When LIQUIDITY_VACUUM + LIQUIDATION_CASCADE align in the same episode window, the combined setup should be stronger than either event alone.

## Why it should work

Expect forced flow to culminate in either continued stress or a sharp repair window.

## Trigger

LIQUIDITY_VACUUM, LIQUIDATION_CASCADE

## Invalidation

Volume returns above-median within 1 bar of event end; Range compresses below 0.8 * range_med within 2 bars OR Position unwinds within expected horizon; Funding reverses sign

## Evidence summary

- sample_size_total: `39`
- validation_samples: `21`
- test_samples: `18`
- median_estimate_bps: `151.9506`
- median_net_expectancy_bps: `145.9506`
- best_q_value: `8.3e-05`
- best_stability_score: `0.877419`

## Confounders checked

- session_transition
- realized_vol_regime

## Evidence gaps

- none

## Notes

- Raw-data evidence requires LIQUIDITY_VACUUM to appear in the same local stress window as LIQUIDATION_CASCADE, producing a stronger forced-flow/liquidity-stress setup than either event alone.
