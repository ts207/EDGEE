# THESIS_LIQUIDATION_CASCADE

- Promotion class: `seed_promoted`
- Deployment state: `monitor_only`
- Primary event id: `LIQUIDATION_CASCADE`
- Compatibility event family: `LIQUIDATION_CASCADE`
- Tier / role: `D` / `trigger`
- Symbols: BTCUSDT, ETHUSDT
- Timeframe: `5m`
- Horizon: 8-24 bars
- Evidence freshness date: `2026-04-03`
- Review due date: `2026-05-03`
- Staleness class: `fresh`

## What it is

When LIQUIDATION_CASCADE fires under governed contract semantics, expect the declared post-event path to materialize over 8-24 bars unless position unwinds within expected horizon; funding reverses sign

## Why it should work

Expect forced flow to culminate in either continued stress or a sharp repair window.

## Trigger

LIQUIDATION_CASCADE

## Invalidation

Position unwinds within expected horizon; Funding reverses sign

## Evidence summary

- sample_size_total: `375`
- validation_samples: `200`
- test_samples: `175`
- median_estimate_bps: `125.7448`
- median_net_expectancy_bps: `119.7448`
- best_q_value: `0.0`
- best_stability_score: `0.98492`

## Confounders checked

- session_transition
- realized_vol_regime

## Evidence gaps

- none

## Notes

- Evidence prefers raw liquidation plus open-interest flow when available, and otherwise falls back to a feature-schema forced-flow proxy using return shock, funding stretch, depth depletion, and spread stress.
