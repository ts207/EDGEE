# THESIS_VOL_SHOCK_LIQUIDITY_CONFIRM

- Promotion class: `paper_promoted`
- Deployment state: `paper_only`
- Event family: `VOL_SHOCK`
- Tier / role: `A` / `confirm`
- Symbols: BTCUSDT, ETHUSDT
- Timeframe: `5m`
- Horizon: 8-24 bars
- Evidence freshness date: `2026-04-01`
- Review due date: `2026-04-22`
- Staleness class: `fresh`

## What it is

When VOL_SHOCK + LIQUIDITY_VACUUM align in the same episode window, the combined setup should be stronger than either event alone.

## Why it should work

Expect volatility expansion and directional follow-through after onset.

## Trigger

VOL_SHOCK, LIQUIDITY_VACUUM

## Invalidation

Realized vol re-expands above shock threshold within phase_tolerance_bars; Second shock occurs before first relaxation completes OR Volume returns above-median within 1 bar of event end; Range compresses below 0.8 * range_med within 2 bars

## Evidence summary

- sample_size_total: `110`
- validation_samples: `59`
- test_samples: `51`
- median_estimate_bps: `102.707`
- median_net_expectancy_bps: `96.707`
- best_q_value: `6e-06`
- best_stability_score: `0.921471`

## Confounders checked

- session_transition
- realized_vol_regime

## Evidence gaps

- none

## Notes

- Raw-data evidence requires a VOL_SHOCK trigger with a nearby LIQUIDITY_VACUUM confirmation, producing a stronger post-shock move thesis than either event alone.
