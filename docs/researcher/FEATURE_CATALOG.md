# Feature Catalog

The code registry (`project/core/feature_registry.py`) is the source of truth. This document is the operator-facing quick reference derived from it.

Use it to answer:
1. What canonical feature already exists?
2. What does it mean and what are its units?
3. Which pipeline stage owns it?

Do not add detector-local state to this registry. If a feature is detector-specific and not reusable, keep it local.

---

## Core Price and Basis Features

Produced by stage: `build_features`

| Feature | Meaning | Units | Dependencies |
|---|---|---|---|
| `basis_bps` | Perp vs spot basis in basis points | `bps` | `close`, `spot_close` |
| `basis_zscore` | Rolling z-score of `basis_bps` | `zscore` | `basis_bps` |
| `spread_bps` | Estimated spread from microstructure inputs | `bps` | `close`, `high`, `low`, `volume` |
| `spread_zscore` | Rolling z-score of `spread_bps` | `zscore` | `spread_bps` |
| `rv_96` | Lagged rolling realized volatility, 96-bar window | `volatility` | `close` |
| `rv_pct_17280` | Lagged rolling percentile rank of `rv_96`, long lookback | `percentile` | `rv_96` |

---

## Funding and Microstructure Features

Produced by stage: `build_features`

| Feature | Meaning | Units | Dependencies |
|---|---|---|---|
| `funding_rate_scaled` | Canonical funding rate aligned to bar timestamps | `decimal_rate` | `funding_rate`, `timestamp` |
| `funding_abs_pct` | Lagged rolling percentile rank of absolute funding magnitude | `percentile` | `funding_rate_scaled` |
| `imbalance` | Buy vs sell pressure imbalance | `ratio` | `taker_base_volume`, `volume` |
| `micro_depth_depletion` | Depth-depletion proxy for stressed microstructure | `ratio` | `volume`, `spread_bps` |

---

## Canonical Market-State Features

Produced by stage: `build_market_context`. These are the primary reuse surface for detectors. When a detector can use them, it should prefer them over rebuilding adjacent logic inline.

| Feature | Meaning | Units |
|---|---|---|
| `ms_vol_state` | Canonical volatility state code | `state_code` |
| `ms_liq_state` | Canonical liquidity state code | `state_code` |
| `ms_oi_state` | Canonical open-interest state code | `state_code` |
| `ms_funding_state` | Canonical funding state code | `state_code` |
| `ms_trend_state` | Canonical trend/chop state code | `state_code` |
| `ms_spread_state` | Canonical spread state code | `state_code` |
| `ms_context_state_code` | Encoded composite state (vol + liq + OI + funding + trend + spread) | `state_code` |

---

## Confidence and Entropy Features

Produced by stage: `build_market_context`. Each market-state dimension has a corresponding probability distribution, confidence score, and entropy value. Use these to filter low-confidence regime rows in confidence-aware context mode.

### Volatility Regime Probabilities

| Feature | Meaning | Units |
|---|---|---|
| `prob_vol_low` | P(volatility regime = LOW) | `probability` |
| `prob_vol_mid` | P(volatility regime = MID) | `probability` |
| `prob_vol_high` | P(volatility regime = HIGH) | `probability` |
| `prob_vol_shock` | P(volatility regime = SHOCK) | `probability` |
| `ms_vol_confidence` | Confidence of volatility regime classification | `probability` |
| `ms_vol_entropy` | Normalized entropy of volatility regime distribution | `entropy` |

### Liquidity Regime Probabilities

| Feature | Meaning | Units |
|---|---|---|
| `prob_liq_thin` | P(liquidity regime = THIN) | `probability` |
| `prob_liq_normal` | P(liquidity regime = NORMAL) | `probability` |
| `prob_liq_flush` | P(liquidity regime = FLUSH) | `probability` |
| `ms_liq_confidence` | Confidence of liquidity regime classification | `probability` |
| `ms_liq_entropy` | Normalized entropy of liquidity regime distribution | `entropy` |

### OI Regime Probabilities

| Feature | Meaning | Units |
|---|---|---|
| `prob_oi_decel` | P(OI regime = DECEL) | `probability` |
| `prob_oi_stable` | P(OI regime = STABLE) | `probability` |
| `prob_oi_accel` | P(OI regime = ACCEL) | `probability` |
| `ms_oi_confidence` | Confidence of OI regime classification | `probability` |
| `ms_oi_entropy` | Normalized entropy of OI regime distribution | `entropy` |

### Funding Regime Probabilities

| Feature | Meaning | Units |
|---|---|---|
| `prob_funding_neutral` | P(funding regime = NEUTRAL) | `probability` |
| `prob_funding_persistent` | P(funding regime = PERSISTENT) | `probability` |
| `prob_funding_extreme` | P(funding regime = EXTREME) | `probability` |
| `ms_funding_confidence` | Confidence of funding regime classification | `probability` |
| `ms_funding_entropy` | Normalized entropy of funding regime distribution | `entropy` |

### Trend Regime Probabilities

| Feature | Meaning | Units |
|---|---|---|
| `prob_trend_chop` | P(trend regime = CHOP) | `probability` |
| `prob_trend_bull` | P(trend regime = BULL) | `probability` |
| `prob_trend_bear` | P(trend regime = BEAR) | `probability` |
| `ms_trend_confidence` | Confidence of trend regime classification | `probability` |
| `ms_trend_entropy` | Normalized entropy of trend regime distribution | `entropy` |

### Spread Regime Probabilities

| Feature | Meaning | Units |
|---|---|---|
| `prob_spread_tight` | P(spread regime = TIGHT) | `probability` |
| `prob_spread_wide` | P(spread regime = WIDE) | `probability` |
| `ms_spread_confidence` | Confidence of spread regime classification | `probability` |
| `ms_spread_entropy` | Normalized entropy of spread regime distribution | `entropy` |

---

## Funding Persistence Features

Produced by stage: `build_market_context`

| Feature | Meaning | Units |
|---|---|---|
| `fp_active` | Funding persistence active flag | `flag` |
| `fp_age_bars` | Bars since funding persistence state became active | `bars` |
| `fp_severity` | Funding persistence severity score | `score` |
| `funding_rate_bps` | Funding rate in basis points | `bps` |
| `carry_state_code` | Signed carry regime marker (+1 positive, -1 negative funding) | `state_code` |
| `funding_persistence_state` | Indicator that signed funding has persisted for the configured run-length window | `flag` |

---

## Regime State Flags

Produced by stage: `build_market_context`. Binary indicators for common composite conditions.

| Feature | Meaning | Units |
|---|---|---|
| `high_vol_regime` | RV is in the high-vol percentile band | `flag` |
| `low_vol_regime` | RV is in the low-vol percentile band | `flag` |
| `spread_elevated_state` | `spread_zscore` exceeds the elevated-spread threshold | `flag` |
| `bull_trend_regime` | Rolling returns exceed rolling vol on the upside | `flag` |
| `bear_trend_regime` | Rolling returns exceed rolling vol on the downside | `flag` |
| `chop_regime` | Rolling returns stay within the rolling volatility band | `flag` |
| `compression_state_flag` | Volatility is low and spread is not elevated | `flag` |
| `aftershock_state` | High-vol and elevated-spread states are both active | `flag` |
| `crowding_state` | Open interest is elevated while funding is positive | `flag` |
| `deleveraging_state` | OI decline is large enough to imply active deleveraging | `flag` |
| `refill_lag_state` | OI is falling and liquidity refill is lagging | `flag` |
| `ms_liquidation_state` | Rolling liquidation pressure is elevated vs recent history | `flag` |

---

## Shared Helper Surfaces

These shared helpers provide reusable logic for detectors:

- `project/features/context_guards.py` — canonical `ms_*` state parsing and optional guard construction
- `project/features/rolling_thresholds.py` — lagged rolling quantile thresholds for causal detector comparisons

Prefer these over re-implementing the same rolling-state or lagged-threshold logic inline in a detector.

---

## Working Rules

- Prefer canonical named features before adding detector-local rolling state.
- If a detector needs a new reusable state, add it to the feature registry first.
- If a feature is detector-specific and not reusable elsewhere, keep it local — do not pollute the registry.
- Treat the registry (`project/core/feature_registry.py`) as the contract surface and this doc as the quick reference.
