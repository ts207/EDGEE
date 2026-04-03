# THESIS_VOL_SHOCK_LIQUIDITY_CONFIRM

- Promotion class: `seed_promoted`
- Deployment state: `monitor_only`
- Primary event id: `VOL_SHOCK`
- Compatibility event family: `VOL_SHOCK`
- Tier / role: `D` / `confirm`
- Symbols: BTCUSDT, ETHUSDT
- Timeframe: `5m`
- Horizon: 8-24 bars
- Evidence freshness date: `2026-04-03`
- Review due date: `2026-04-17`
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

- sample_size_total: `541`
- validation_samples: `300`
- test_samples: `241`
- median_estimate_bps: `101.432`
- median_net_expectancy_bps: `95.432`
- best_q_value: `0.0`
- best_stability_score: `0.927282`

## Confounders checked

- realized_vol_regime
- session_transition

## Evidence gaps

- direct_pair_event_study_missing

## Notes

- Derived bridge confirmation thesis synthesized conservatively from existing VOL_SHOCK and LIQUIDITY_VACUUM raw-data bundles; direct paired-event study still missing.
