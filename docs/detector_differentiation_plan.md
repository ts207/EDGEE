# Detector Differentiation Plan

## Goal
Make each detector encode a distinct market hypothesis instead of sharing nearly the same signal path with only different thresholds.

## Design rules
1. Each detector must have a unique feature surface.
2. Each detector must have at least one gate that no sibling detector uses.
3. Similar families may share utilities, but not the final trigger logic.
4. Metadata must record the detector profile so downstream analysis can tell the hypotheses apart.
5. The canonical proxy family and the temporal pair-trading family must both remain backward compatible with existing event specs.

## Family-by-family differentiation

### Price / volume shock proxy
Hypothesis: sudden flow pressure with return expansion and volatility confirmation.
- Core features: return impulse, RV z-score, volume pressure, flow pressure.
- Unique gate: combined flow pressure confirmation.
- Distinctive metadata: directional flow profile.

### Wick reversal / sweep stop-run
Hypothesis: a long wick is only meaningful when the bar reclaims the body and the wick is dominant on one side.
- Core features: upper wick, lower wick, wick ratio, dominance, reclaim strength.
- Unique gate: one-sided wick dominance plus body reclaim.
- Sweep stop-run variant: stricter dominance and reclaim rules.

### Absorption proxy
Hypothesis: spread and volatility rise while imbalance fades, indicating absorption rather than outright collapse.
- Core features: spread z-score, RV z-score, imbalance compression.
- Unique gate: absorption score that rewards high spread / vol against low imbalance.

### Depth stress / depth collapse
Hypothesis: order-book stress is broader than spread alone; collapse requires acceleration in depth failure.
- Core features: spread pressure, RV pressure, depth depletion, stress score.
- Unique gate: collapse impulse on top of the stress score.
- Depth collapse variant: stricter depth and impulse thresholds.

### Copula pair trading
Hypothesis: pair dislocations should only trigger when the pair is in the explicit universe and the spread reversion is confirmed.
- Core features: pair spread, pair z-score, mean reversion, pair-universe membership.
- Unique gate: pair-universe membership plus pair-spread confirmation.
- Fallback: still works on `pairs_zscore` when pair-close data is absent.

## Rollout / acceptance criteria
- Each detector keeps its event type unchanged.
- Existing regression tests continue to pass.
- New tests prove detectors are not merely threshold clones.
- Copula universe contains more than one pair so pair detection is not locked to BTC/ETH only.
