# Plan: Fix Directional Gating and Detector Robustness

## Objective
Address critical logical errors in the research pipeline where losing directional strategies are promoted due to absolute t-stat gating and two-sided p-values. Additionally, improve detector robustness to synthetic noise by adding absolute signal floors.

## Key Files & Context
- `project/research/gating.py`: Central statistics and p-value logic used for all expectancy calculations.
- `project/research/search/bridge_adapter.py`: Translates raw search metrics into bridge-compatible candidates and applies initial gating.
- `project/events/families/basis.py`: Implementation of basis-related detectors.

## Proposed Solution

### 1. Fix Directional Gating
- Update `project/research/gating.py` to use one-sided p-values for directional hypotheses. This ensures that a strategy with a large negative t-stat (a significant loser) receives a high p-value (approaching 1.0) and is thus rejected by the FDR `q_value` gate.
- Update `project/research/search/bridge_adapter.py` to remove the `.abs()` call from the t-statistic gate. This enforces that `long` strategies must have `t_stat >= min_t_stat` and `short` strategies (which have returns flipped by direction sign) also have `t_stat >= min_t_stat`.

### 2. Improve Detector Robustness
- Update `BasisDislocationDetector` in `project/events/families/basis.py` to include a `min_basis_bps` floor (default 5.0 bps). This prevents the detector from triggering on tiny fluctuations that result in high Z-scores due to low background volatility in synthetic datasets.

## Implementation Plan

### Phase 1: Statistical Gating Alignment
1.  **Modify `project/research/gating.py`**:
    - Update `distribution_stats` to compute a one-sided (right-tail) p-value.
    - Update `two_sided_p_from_t` to be one-sided (or rename/add a one-sided version).
2.  **Modify `project/research/search/bridge_adapter.py`**:
    - Update `split_bridge_candidates` to remove `.abs()` from the `min_t_mask` calculation.
    - Update the p-value calculation in `hypotheses_to_bridge_candidates` to use one-sided p-values.

### Phase 2: Detector Sensitivity Fix
1.  **Modify `project/events/families/basis.py`**:
    - Add `compute_raw_mask` to `BasisDislocationDetector` that includes an absolute `basis_bps` floor.
    - Update `FndDislocDetector` and other subclasses if necessary to inherit or respect this new mask.

### Phase 3: Verification
1.  **Rerun Full Certification**: Execute `project/scripts/run_fast_synthetic_certification.py` with an extended range and multiple detectors.
2.  **Audit Artifacts**:
    - Verify `phase2_candidates.parquet` for `DELEVERAGING_WAVE` long candidates (should now fail the gate).
    - Verify `BASIS_DISLOC` truth recovery precision (should improve significantly).
    - Confirm `q_value` for losers is now high (close to 1.0), preventing false "discovery" claims.

## Migration & Rollback
- No migration required as this only affects research artifact generation.
- Rollback involves reverting the sign-awareness in gating and removing the detector floor.
