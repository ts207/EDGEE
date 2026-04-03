# THESIS_VOL_SHOCK

- Promotion class: `paper_promoted`
- Deployment state: `paper_only`
- Primary event id: `VOL_SHOCK`
- Compatibility event family: `VOL_SHOCK`
- Tier / role: `A` / `trigger`
- Symbols: BTCUSDT, ETHUSDT
- Timeframe: `5m`
- Horizon: 8-24 bars
- Evidence freshness date: `2026-04-03`
- Review due date: `2026-07-02`
- Staleness class: `fresh`

## What it is

When VOL_SHOCK fires under governed contract semantics, expect the declared post-event path to materialize over 8-24 bars unless realized vol re-expands above shock threshold within phase_tolerance_bars; second shock occurs before first relaxation completes

## Why it should work

Expect volatility expansion and directional follow-through after onset.

## Trigger

VOL_SHOCK

## Invalidation

Realized vol re-expands above shock threshold within phase_tolerance_bars; Second shock occurs before first relaxation completes

## Evidence summary

- sample_size_total: `6618`
- validation_samples: `2067`
- test_samples: `4551`
- median_estimate_bps: `90.2454`
- median_net_expectancy_bps: `84.2454`
- best_q_value: `0.0`
- best_stability_score: `0.902033`

## Confounders checked

- session_transition
- realized_vol_regime

## Evidence gaps

- none

## Notes

- Raw-data evidence uses absolute post-shock move, which matches the contract's volatility-expansion semantics better than directional continuation.
