# Assurance & Benchmarks

This document describes the benchmarking methodology and regression testing used to ensure system integrity.

## Benchmark Methodology
Every code change is tested against a set of *Baseline Snapshots*.
* **Baseline Snapshots**: Known successful research runs that must remain consistent across versions.
* **Performance Regression**: Metrics for ensuring discovery and validation performance does not rot over time.

## Certification
Promotion often requires a *Certification* step, which is an automated or semi-automated verification of a candidate's out-of-sample behavior.

## Regression Suites
* **Adversarial Tests**: Tests that attempt to break validation gates using known noise patterns.
* **Contract Integrity**: Tests that ensure artifact schemas remain compatible across stages.

---

## Change Log: Statistical and Execution Integrity Fixes

### April 2026 — Deep System Audit

A comprehensive audit of the research pipeline, execution model, and live engine identified and corrected the following issues. All code changes are tracked in git; this section records the *intent* of each change for future researchers.

#### Statistics

| ID | File | Change | Impact |
|----|------|--------|--------|
| B1 | `research/gating.py` | Gate t-stat now computed on train+val only; test split excluded | Holdout independence restored |
| B2 | `research/helpers/estimation_kernels.py` | LOSO single-symbol groups now marked `stable=False` | BTC-only hypotheses no longer pass stability gate silently |
| B6 | `research/gating.py`, `research/gating_primitives.py` | `two_sided_p_from_t` emits ERROR-level log in addition to DeprecationWarning | Deprecated calls visible in production log aggregators |
| B8 | `research/gating.py` | NW degrees of freedom: `n_eff - 1` → `n_gate - 1` | Weighted and unweighted p-values now use the same df convention |
| — | `research/validate_expectancy_traps.py` | Surviving local two-sided `_p_from_t` replaced with `one_sided_p_from_t` | Eliminates last instance of two-sided computation in validation path |
| — | `spec/gates.yaml` | `min_t_stat` 1.5→2.0, regime ESS 2→3, conditioned bucket floor 30→75, synthetic t-stat 0.25→1.0, bridge t-stat 1.5→2.0, deployable `min_regimes_supported` 2→3 | Tightened discovery and promotion gates |
| — | `research/validate_expectancy_traps.py` | Bootstrap iterations: standard 400→2000, promotion 800→2000, synthetic 100→500 | SE on empirical p-value at α=0.05 drops from ±1.4% to ±0.5% |
| — | `research/helpers/estimation_kernels.py` | `_apply_hierarchical_shrinkage` gains `elapsed_days` + `lambda_decay_halflife_days` parameters; decay now time-based | Cross-session lambda continuity no longer degrades from session-count accumulation |
| — | `project/tests/core/test_stats.py` | BH test expectations corrected: `adj_smaller[2]` expectation changed from `0.013` to `0.01333` (exact rational value); monotonicity test added | Statistical test correctness; monotonic conservatism verified |
| — | `research/multiplicity.py` | `side_policy='both'` now correctly weighted as 2 tests in BH denominator | Two-sided hypotheses no longer undercounted in multiplicity correction |
| — | `research/promotion/promotion_gate_evaluators.py` | DSR `n_trials` precedence: `num_tests_effective` → `num_tests_campaign` → `num_tests_family` → fallback to 1 with WARNING | Selection bias penalty now uses most granular available multiplicity count |

#### Live Execution

| ID | File | Change | Impact |
|----|------|--------|--------|
| — | `live/kill_switch.py` | `PSI_ERROR_THRESHOLD` 0.50→0.25; `PSI_WARN_THRESHOLD` 0.25→0.10; TIER1 features expanded from 3 to 6 | Kill switch triggers on minor-to-major shift boundary; more features monitored |
| — | `live/drift.py` | Adaptive PSI binning (≥30 obs/bin); outer edges extended to ±∞; KS statistic added | PSI estimates stable at small research sample sizes; tail drift detectable |
| — | `live/scoring.py` | `MIN_SETUP_MATCH = 0.20` hard gate added | Prevents trades when no qualifying event has fired |
| — | `live/decay.py` | `default_decay_rules()` added; `LiveEngineRunner` uses it when none supplied | Per-thesis degradation monitoring always active |
| — | `engine/risk_allocator.py` | `AllocationPolicy.mode` default: `"heuristic"` → `"deterministic_optimizer"` | Allocation decisions reproducible by default |
| — | `engine/risk_allocator.py` | `stressed_regime_values` expanded to cover uppercase and alternate naming conventions | Stress correlation limit activates regardless of registry label convention |
| B5 | `engine/pnl.py` | `FUNDING_HOURS_BYBIT_4H` constant added; `compute_pnl_ledger` and `compute_pnl_components` accept `funding_hours` parameter | Bybit 4-hour contracts can now use correct funding schedule |
| — | `live/thesis_reconciliation.py` | New module: thesis-batch reconciliation on live startup | Detects added/removed/superseded/downgraded theses; enforces fail-safe rules before live trading |
| — | `live/runner.py` | Added `_reconcile_thesis_batch()` called at startup when `reconcile_at_startup=True` | Runtime state drift blocked; removed/downgraded theses with open positions trigger kill-switch |
| — | `core/regime_classifier.py` | New unified `classify_regime()` function with `RESEARCH_EXACT` and `RUNTIME_APPROX` modes | Live and research use shared logic; approximation path is explicit and documented |

#### Open Issues (not yet fixed)

| ID | Description | Location | Status |
|----|-------------|----------|--------|
| B3 | DSR `n_trials` scoped to mechanism family (~10–20), not full campaign (~hundreds) | `promotion/promotion_gate_evaluators.py:393` | **Partially fixed**: Precedence chain implemented (`effective` → `campaign` → `family`); family-level not yet automatic |
| B4 | ~~`side_policy='both'` counted as 1 test in BH denominator~~ | `research/multiplicity.py` | **Fixed** (April 2026): Now correctly weighted as 2 |
| A1 | Research batch feature computation and live REST polling are independent implementations | `build_features.py` vs `runner.py` | **Still open**: No shared feature builder yet |
| A2 | ~~Live regime classifier uses single-bar bps threshold; research used rolling percentile state machine~~ | `live/runner.py:_classify_canonical_regime` | **Partially fixed**: Unified `classify_regime()` exists; live uses `runtime_approx` with explicit metadata when research features unavailable |
| A4 | BH FDR applied within mechanism groups only; no cross-campaign correction | `research/multiplicity.py` | **Still open**: `apply_cross_campaign_fdr()` exists but not wired into canonical workflow |
| A5 | ~~No documented thesis-state reconciliation procedure when a new export is written between engine restarts~~ | `live/thesis_store.py`, `live/thesis_state.py` | **Fixed** (April 2026): `thesis_reconciliation.py` added; startup reconciliation enforced |
