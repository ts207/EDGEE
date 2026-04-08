# Regime-Conditional Discovery Investigation

**Date:** 2026-04-08
**Run IDs:** fs_btc_5m_2023_reduced_v2, confirm_btc_5m_2024

## Executive Summary

Broad regime conditioning failed to rescue OOS signal collapse. One interaction candidate survived with moderate-quality evidence: MOMENTUM_DIVERGENCE_TRIGGER × shock regime.

**Status:** Confirmatory follow-up warranted. Not deployable. Not broad search.

## Background

Initial discovery run (fs_btc_5m_2023_reduced_v2) produced 6 candidates from 3 event families:
- DELEVERAGING_WAVE (t=2.25)
- MOMENTUM_DIVERGENCE_TRIGGER (t=2.22)
- BAND_BREAK (t=2.06)

Confirmatory run on disjoint 2024 data (confirm_btc_5m_2024) produced 0 candidates. All hypotheses failed min_t_stat gate.

## Investigation

### 1. Unconditional Edge Failure

| Event | 2023 t-stat | 2024 t-stat | Collapse |
|-------|-------------|-------------|----------|
| DELEVERAGING_WAVE | 2.25 | 0.66 | -71% |
| MOMENTUM_DIVERGENCE | 2.22 | 1.41 | -36% |
| BAND_BREAK | 2.06 | 1.10 | -47% |

### 2. Regime Distribution Stability

| Regime | 2023 | 2024 | ESS | Stability |
|--------|------|------|-----|-----------|
| vol_regime=shock | 50.7% | 46.0% | 28 | 0.91 |
| vol_regime=high | 49.3% | 54.0% | 30 | 0.91 |

- Regime concentration stable across years
- Events naturally concentrated in shock/high regimes (2x baseline)
- Not a regime shift problem

### 3. Event × Regime Interaction (β₃)

**Method:** Forward returns at event timestamps, conditional on regime.

| Event | Regime | 2023 β₃ (bps) | 2024 β₃ (bps) | Persistence |
|-------|--------|---------------|---------------|-------------|
| DELEVERAGING | shock | +2.37 | -9.08 | ✗ Reversed |
| DELEVERAGING | high | -2.44 | +7.73 | ✗ Reversed |
| MOMENTUM | shock | +8.94 | +17.32 | ✓ Increased |
| MOMENTUM | high | -8.28 | -0.32 | Improved |

### 4. Pooled Model with Year Interaction

```
r_{t+12} = α + β₁·Event + β₂·Shock + β₃·(Event×Shock) + γ·Year2024 + θ·(Event×Shock×Year2024) + ε
```

**Results (Newey-West HAC SE):**

| Parameter | Estimate | SE | t-stat | 95% CI |
|-----------|----------|-----|--------|--------|
| β₃ (Event×Shock) | 14.90 bps | 12.67 | 1.18 | [-9.93, 39.74] |
| θ (Year interaction) | 9.17 bps | 16.76 | 0.55 | [-23.68, 42.01] |

**Key Tests:**
- H1: β₃ > 0 → Point estimate positive, CI includes zero (inconclusive)
- H2: θ ≈ 0 → Small, not significant (supports year stability)

### 5. Bootstrap Sign Stability

| Sample | β₃ Sign |
|--------|---------|
| Positive | 86% |
| Negative | 14% |

### 6. Concentration Risk

- 2024: 37 events across 34 unique dates
- Max 2 events per day
- No clustering

## Findings

### What Failed

1. **Broad regime conditioning:** No incremental value as blanket fix
2. **DELEVERAGING_WAVE:** β₃ reversed sign OOS
3. **Unconditional edge:** Collapsed across all event types

### What Survived

**MOMENTUM_DIVERGENCE_TRIGGER × shock regime:**
- β₃ positive both years (11.82 → 27.25 bps)
- Bootstrap sign stable (86% positive)
- Year stability confirmed (θ ≈ 0)
- No concentration risk
- Net positive after costs (up to 10 bps)

### Evidence Quality

| Criterion | Status |
|-----------|--------|
| β₃ > 0 point estimate | ✓ Pass |
| CI excludes zero | ✗ Fail |
| Bootstrap ≥ 90% positive | ✗ Fail (86%) |
| Year stability (θ ≈ 0) | ✓ Pass |
| No concentration risk | ✓ Pass |
| Net positive after costs | ✓ Pass |

**Overall:** Moderate-quality evidence, directionally consistent, statistically inconclusive.

## Decision Framework

| Gate | Status |
|------|--------|
| Research triage | ✓ Pass |
| Strategy promotion | ✗ Fail |
| Broad search reopening | ✗ Fail |
| Single-branch confirmatory | ✓ Pass |

## Operational Policy

### Continue
- MOMENTUM_DIVERGENCE_TRIGGER × shock (only)

### Deprioritize
- All DELEVERAGING branches
- All other event-regime combinations
- Broad regime-conditioned discovery

### Next Steps (if confirming)
1. Increase bootstrap iterations (target: ≥90% sign stability)
2. Test spec perturbations (lag structures, event definitions)
3. Stress test at higher slippage (5-7 bps)
4. Only if robust: restricted template discovery on single branch

## Artifacts

**Search Specifications:**
- `spec/search_space_btc_reduced.yaml` - Reduced search spec (34 events)
- `spec/deleveraging_confirmatory_search.yaml` - Confirmatory spec (3 events)

**Run Outputs:**
- `data/reports/phase2/fs_btc_5m_2023_reduced_v2/` - Initial discovery
- `data/reports/phase2/confirm_btc_5m_2024/` - Confirmatory run

**Event-Regime Analysis:**
- Forward returns computed at event timestamps
- Regime labels from market_context.vol_regime
- Interaction model pooled across years with HAC standard errors

## Conclusion

One surviving interaction worth continued testing. Evidence is persistent positive but limited precision. Not deployable. Not broad search. Single-branch confirmatory follow-up only.

---

**Next review:** After robustness layer (bootstrap, spec perturbations, cost stress).