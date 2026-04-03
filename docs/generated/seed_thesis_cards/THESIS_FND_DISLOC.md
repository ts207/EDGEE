# THESIS_FND_DISLOC

- Promotion class: `paper_promoted`
- Deployment state: `paper_only`
- Primary event id: `FND_DISLOC`
- Compatibility event family: `FND_DISLOC`
- Tier / role: `A` / `trigger`
- Symbols: BTCUSDT
- Timeframe: `5m`
- Horizon: 8-24 bars
- Evidence freshness date: `2026-04-03`
- Review due date: `2026-07-02`
- Staleness class: `fresh`

## What it is

When FND_DISLOC fires under governed contract semantics, expect the declared post-event path to materialize over 8-24 bars unless basis normalizes within horizon; z-score returns to mean

## Why it should work

Expect volatility expansion and directional follow-through after onset.

## Trigger

FND_DISLOC

## Invalidation

Basis normalizes within horizon; Z-score returns to mean

## Evidence summary

- sample_size_total: `35`
- validation_samples: `24`
- test_samples: `11`
- median_estimate_bps: `108.7192`
- median_net_expectancy_bps: `102.7192`
- best_q_value: `4e-06`
- best_stability_score: `0.969604`

## Confounders checked

- session_transition
- realized_vol_regime

## Evidence gaps

- none

## Notes

- Feature-schema funding dislocation evidence uses canonical basis and funding columns from the cleaned feature lake.
