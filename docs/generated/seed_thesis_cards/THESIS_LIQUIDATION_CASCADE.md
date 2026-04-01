# THESIS_LIQUIDATION_CASCADE

- Promotion class: `paper_promoted`
- Deployment state: `paper_only`
- Event family: `LIQUIDATION_CASCADE`
- Tier / role: `A` / `trigger`
- Symbols: BTCUSDT, ETHUSDT
- Timeframe: `5m`
- Horizon: 8-24 bars
- Evidence freshness date: `2026-04-01`
- Review due date: `2026-06-30`
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

- sample_size_total: `329`
- validation_samples: `105`
- test_samples: `224`
- median_estimate_bps: `127.451`
- median_net_expectancy_bps: `121.451`
- best_q_value: `0.0`
- best_stability_score: `0.987495`

## Confounders checked

- session_transition
- realized_vol_regime

## Evidence gaps

- none

## Notes

- Raw-data evidence uses a forced-flow proxy requiring an extreme return shock, large open-interest drop, and concurrent funding stretch.
