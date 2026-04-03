# THESIS_BASIS_DISLOC

- Promotion class: `paper_promoted`
- Deployment state: `paper_only`
- Primary event id: `BASIS_DISLOC`
- Compatibility event family: `BASIS_DISLOC`
- Tier / role: `A` / `trigger`
- Symbols: BTCUSDT
- Timeframe: `5m`
- Horizon: 8-24 bars
- Evidence freshness date: `2026-04-03`
- Review due date: `2026-07-02`
- Staleness class: `fresh`

## What it is

When BASIS_DISLOC fires under governed contract semantics, expect the declared post-event path to materialize over 8-24 bars unless basis normalizes within horizon; z-score returns to mean

## Why it should work

Expect volatility expansion and directional follow-through after onset.

## Trigger

BASIS_DISLOC

## Invalidation

Basis normalizes within horizon; Z-score returns to mean

## Evidence summary

- sample_size_total: `47`
- validation_samples: `32`
- test_samples: `15`
- median_estimate_bps: `129.4869`
- median_net_expectancy_bps: `123.4869`
- best_q_value: `0.001769`
- best_stability_score: `0.949255`

## Confounders checked

- session_transition
- realized_vol_regime

## Evidence gaps

- none

## Notes

- Feature-schema basis dislocation evidence uses canonical basis_bps and basis_zscore columns when bootstrap raw spot/perp pairing is unavailable as a separate archive.
