# Edge — Deep Audit & Patch Plan

**Generated:** 2026-03-23  
**Codebase:** Edge-main (Python algo-trading / quant strategy framework)  
**Scope:** Full source analysis — logical, statistical, structural, and technical issues

---

## Executive Summary

Edge is a sophisticated quantitative trading platform with a well-designed event DSL, multi-strategy execution engine, and layered statistical guardrails. The architecture shows strong intent around PIT safety, data contracts, and multiple-testing correction. However, the audit found **21 distinct issues** across four severity tiers, ranging from a variable-name crash bug in production code to a structural fragmentation of the event ontology across three directories.

---

## Issue Registry

### CRITICAL (P0) — Breaks correctness or crashes

---

#### C-1 · `NameError` crash in `deflated_sharpe_ratio`
**File:** `project/eval/selection_bias.py:53`

`deflated_sharpe_ratio` assigns the cleaned array to `n_arr`, then immediately references `pnl_arr` (which only exists inside `probabilistic_sharpe_ratio`). This crashes with `NameError: name 'pnl_arr' is not defined` on every call when `n_trials > 1`.

```python
# BUG — current code
n_arr = pd.to_numeric(pnl, errors="coerce").dropna().values
n = len(pnl_arr)   # ← NameError: pnl_arr not defined here

# FIX
pnl_arr = pd.to_numeric(pnl, errors="coerce").dropna().values
n = len(pnl_arr)
```

**Impact:** DSR is completely non-functional for multi-trial comparisons. Any selection-bias gating that calls `deflated_sharpe_ratio` with `n_trials > 1` will crash the pipeline.

---

#### C-2 · `trailing_percentile_rank` — wrong lag shift creates look-ahead bias
**File:** `project/core/causal_primitives.py:115`

Every other causal primitive shifts by `lag` when `lag > 0`. `trailing_percentile_rank` silently shifts by `lag - 1`, so the default `lag=1` applies **zero shift** — the value at bar `t` includes bar `t`'s own data.

```python
# BUG — all other functions use .shift(lag)
return (
    rolled.shift(lag - 1) if lag > 0 else rolled   # ← lag=1 → shift(0) = no shift
)

# FIX — match all other causal primitives
return (
    rolled.shift(lag) if lag > 0 else rolled
)
```

**Impact:** Any event detector or feature that uses `trailing_percentile_rank` with default lag embeds a one-bar look-ahead. Backtest returns will be artificially inflated, and the bias will not appear in live trading.

---

### HIGH (P1) — Statistical invalidity or silent wrong answers

---

#### H-1 · `fit_t_copula` hardcodes `df=4.0` — no MLE
**File:** `project/core/copula.py:46`

`select_best_copula` correctly runs grid-search MLE for degrees of freedom. But `fit_t_copula` itself hardcodes `df = 4.0` with the comment "For now, we'll use a fixed df=4.0". Any code path that calls `fit_t_copula` directly (e.g. in pairs trading detectors) will always use df=4, silently bypassing the AIC-selected value.

**Fix:** `fit_t_copula` should call `_estimate_t_df_mle` internally:
```python
def fit_t_copula(u1, u2):
    tau, _ = scipy_stats.kendalltau(u1, u2)
    rho = float(np.sin(np.pi / 2 * tau))
    df = _estimate_t_df_mle(u1, u2, rho)  # ← was: df = 4.0
    return rho, df
```

**Impact:** Tail-dependence estimates for copula-pairs strategies are wrong when the market-implied df is far from 4 (common in trending or low-volatility regimes where df could be 8–15). Conditional entry probabilities for COPULA_PAIRS_TRADING events are miscalibrated.

---

#### H-2 · Cointegration p-value approximation ignores sample size
**File:** `project/core/stats.py:86–102`

`_approx_coint_pvalue` accepts an `n` argument but never uses it. MacKinnon (1994) tables explicitly vary critical values by sample size — for n=30 the 5% critical value is around -3.80, not the asymptotic -3.34. For small samples this function will report significance too liberally.

Additionally, the right-tail approximation uses a logistic function with arbitrary parameters (`-1.5 * (t + 2.5)`) that bears no relationship to the actual ADF distribution. For t-stats between -3.04 and 0, p-values will be uniformly wrong.

**Fix:** Either add MacKinnon's finite-sample response-surface coefficients (published as a regression in beta of the critical value on `1/n`) or add a hard minimum sample size gate (n ≥ 50) before calling the fallback.

---

#### H-3 · PSR formula uses `(kurt + 3)/4` — incorrect coefficient
**File:** `project/eval/selection_bias.py:33`

The Bailey & Lopez de Prado (2012) formula for the standard error of the SR uses the coefficient `γ₂/4` where γ₂ is the **excess** kurtosis. Since `scipy.stats.kurtosis(fisher=True)` already returns excess kurtosis, the correct coefficient is `kurt/4`. The code uses `(kurt + 3) / 4`, which would be correct only for the *non-excess* (Pearson) kurtosis.

```python
# BUG
radicand = (1.0 + 0.5 * sr**2 - skew * sr + ((kurt + 3.0) / 4.0) * sr**2) / (n - 1)

# FIX (using excess kurtosis returned by fisher=True)
radicand = (1.0 + 0.5 * sr**2 - skew * sr + (kurt / 4.0) * sr**2) / (n - 1)
```

**Impact:** For leptokurtic return distributions (common in crypto), excess kurtosis of 4–8 is typical. The inflated coefficient overstates SE, making the PSR conservative — strategies with genuine edge can be incorrectly rejected.

---

#### H-4 · Correlation allocation uses position-change covariance, not return covariance
**File:** `project/engine/risk_allocator.py:~430`

When `enable_correlation_allocation=True`, the inverse-covariance weighting uses `df.diff().cov()` — the covariance of *position changes* (turnover). Two strategies that are both continuously long and never rebalance have zero position-change correlation but identical P&L correlation. Minimum-variance weights computed from turnover covariance are meaningless for sizing.

**Fix:** Compute covariance of position-weighted returns (not raw positions or position diffs):
```python
# FIX
weighted_rets = df_req.multiply(close_returns, axis=0)  # requires close_returns passed in
cov = weighted_rets.cov()
```

**Impact:** Correlation-based allocation will silently undersize strategies with low turnover and oversize high-turnover strategies, exactly backward from the intent.

---

#### H-5 · `_equity_curve_from_pnl` — fragile heuristic misclassifies PnL units
**File:** `project/engine/risk_allocator.py:24`

The function determines whether PnL values are "dollar PnL" or "per-bar returns" using:
```python
if clean.abs().median() > 1.0 or clean.abs().max() > 2.0:
    return 1.0 + clean.cumsum()   # dollar mode
return (1.0 + clean).cumprod()   # return mode
```

A strategy running on $10k capital with typical per-bar returns of 0.05–0.5% will have dollar P&L in the range of $5–$50 — well above the 1.0 median threshold but correctly classified as dollar P&L. However, a strategy with very high capital base ($1M) generating small-but-frequent profits can hit bar-level P&L of $100–$1000, triggering the same path. Conversely, a levered strategy can have single-bar returns > 2%, entering dollar mode.

**Fix:** Accept an explicit `pnl_mode: Literal["dollar", "return"]` argument. Remove the heuristic. Drawdown and vol-scaling calculations downstream depend on the equity curve being correct.

---

#### H-6 · Rolling pairwise correlation computed on allocated positions, not returns
**File:** `project/engine/risk_allocator.py:~490–540`

When `max_pairwise_correlation` is set, the correlation constraint is evaluated on the allocated *position series* (dollars), not on position-weighted returns. The "pairwise correlation" of two USD-denominated position series is dominated by position magnitude, not by return co-movement. Two strategies with $1M and $10k exposure, both long BTC, show a correlation of ~1.0 by dollar position but also ~1.0 by return — however, the scale distortion means any magnitude imbalance produces a spuriously low correlation number.

**Fix:** Compute rolling correlation of strategy-level equity returns for the constraint check.

---

### MEDIUM (P2) — Correctness issues that degrade but don't break

---

#### M-1 · Deprecated `compute_pnl_components` still called in production template
**File:** `project/strategy/templates/evaluate.py:9`

`compute_pnl_components` is marked deprecated with a `DeprecationWarning` and documented as failing to correctly handle flip trades in `next_open` mode. Yet it is still imported and called in the strategy evaluator template. Every strategy evaluation emits a `DeprecationWarning` and uses the less accurate PnL semantics.

**Fix:** Migrate `evaluate.py` to `compute_pnl_ledger`. The ledger API requires price data to be passed alongside positions, which may require a small interface change.

---

#### M-2 · Funding PnL overcounting possible when `use_event_aligned_funding=False`
**File:** `project/engine/pnl.py:241`

`compute_pnl_ledger` defaults `use_event_aligned_funding=True` (correct). But `compute_pnl_components` defaults it to `True` in its call but the deprecated direct callers (tests, legacy paths) can pass `False`, accumulating funding every bar instead of every 8 hours — a 24× overcount for 5-minute bars.

**Fix:** Add an assertion at the entry of both functions that if `funding_rate` is non-zero and the index has sub-hourly frequency, `use_event_aligned_funding` must be `True`.

---

#### M-3 · `audited_merge_asof` hard-fails on 5% staleness — no graceful degradation
**File:** `project/core/audited_join.py:70`

The 5% stale-rate threshold is correct for normal operation, but the function raises a `RuntimeError` unconditionally. There is no way for callers to request a warning-only mode. During exchange downtime or funding-rate publication delays, this causes the entire pipeline to abort rather than falling back to stale values with logged warnings.

**Fix:** Add a `stale_action: Literal["raise", "warn", "ignore"] = "raise"` parameter. The current hard-fail should remain the default but callers that have explicitly accepted stale-data risk should be able to proceed.

---

#### M-4 · Vol scaling operates on portfolio-level vol but applies uniformly to all strategies
**File:** `project/engine/risk_allocator.py:~560–580`

`target_annual_vol` scaling estimates portfolio-level volatility from `portfolio_pnl_series`, then applies the same scale factor uniformly to every strategy. If one high-vol strategy dominates portfolio risk, all other lower-vol strategies are scaled down equally — a correct portfolio-level result, but one that discards the per-strategy volatility information available in `allocated`.

**Fix:** Compute per-strategy vol scaling using each strategy's individual PnL series before the portfolio sum, then apply a portfolio-level correction as a second pass.

---

#### M-5 · `_clamp_positions_py` — pure Python loop, no numpy fallback
**File:** `project/engine/risk_allocator.py:~35`

When `numba` is unavailable, position clamping falls back to a Python `for` loop over the full position array. For a 1-year backtest at 5-minute bars (105,120 bars) with 10 strategies, this is 1M Python iterations. The loop is not vectorizable in its current recursive (path-dependent) form, but can be replaced with a `np.minimum.accumulate`-based approach for the common case.

**Fix:** Add a comment documenting that the loop is path-dependent and cannot be vectorized naively. As a partial improvement, add an early-exit check: if `max_new_exposure_per_bar >= raw.max()`, no clamping is needed and the array can be returned as-is.

---

#### M-6 · `compute_funding_pnl_event_aligned` — no UTC enforcement on index
**File:** `project/engine/pnl.py:66`

The function checks `pos.index.hour.isin(funding_hours)` where `funding_hours = (0, 8, 16)`. These hours are UTC Binance funding timestamps. If the index is naive (tz-unaware) or localized to a non-UTC timezone, the hour check will silently fire at the wrong times.

**Fix:** Add `assert pos.index.tz is not None and str(pos.index.tz) == "UTC"` at function entry.

---

### LOW (P3) — Code quality, structural, and maintenance issues

---

#### L-1 · Triple-redundant event ontology — no single source of truth
**Directories:**
- `spec/events/*.yaml`  
- `project/artifacts/baseline/specs/events/*.yaml`  
- `spec/ontology/events/*.yaml`

All three directories contain overlapping YAML files for the same 60+ event types. There is no documented relationship between them. If a parameter is changed in `spec/events/` but not the other copies, strategies compiled from different registry paths will have different behavior. The `canonical_event_registry.yaml` exists but is duplicated across two directories.

**Fix:** Designate `spec/events/` as the authoritative source. Move the `artifacts/baseline` copies to be auto-generated from spec. Delete `spec/ontology/events/` and replace with symlinks or build-time verification.

---

#### L-2 · `_t_copula_log_likelihood` has placeholder dead code
**File:** `project/core/copula.py:130`

```python
# This line is immediately overwritten — dead code
log_bivariate_t = (
    np.log(df / 2.0 + 0.5 * (t1 ** 2 + t2 ** 2 - 2 * rho * t1 * t2))  # placeholder
)
# Exact formula follows and overwrites the variable
import math
log_bivariate_t = (...)
```

The `# placeholder` line is a leftover from development. It computes an incorrect value and is immediately overwritten. Also, `import math` inside a function body is a Python antipattern.

**Fix:** Remove the placeholder line. Move `import math` to the module top.

---

#### L-3 · `_resolve_policy_weights` deterministic optimizer has circular dependency
**File:** `project/engine/risk_allocator.py:~345`

In `deterministic_optimizer` mode, policy weights are computed from pre-cap exposures (`requested`), then the weights are applied to the same `requested` positions to derive `allocated`. Later, strategy and family caps are applied to `allocated`. The final scale actually applied to a strategy's positions depends on a chain of: (1) pre-cap weights, (2) post-weight positions, (3) post-cap scale-back. The per-strategy weight computed in step 1 is not aware of the caps applied in step 3, so the effective risk budget split is not what the policy configuration specifies.

**Fix:** Document the intended ordering explicitly. If the policy is meant to respect caps, the weight normalization step should run after cap application (not before).

---

#### L-4 · Doc-code drift — `CURRENT_STATE_AND_GAPS.md` references paths that don't exist
**File:** `docs/CURRENT_STATE_AND_GAPS.md`

The document lists paths like `project/pipelines/research/campaign_controller.py`, `project/research/promotion/`, `project/live/`, `project/portfolio/` as "present in the codebase." Several of these paths do not exist in the uploaded repository snapshot, suggesting either the document is ahead of the code or was written against a different version.

**Fix:** Add CI step that validates all path references in documentation exist. Tag document sections clearly as "current" vs "roadmap."

---

#### L-5 · Newey-West lag formula can produce excessive lags for long series
**File:** `project/core/stats.py:~420`

The automatic lag selection formula `floor(4 * (n/100)^(2/9))` is Andrews (1991)'s rule of thumb. For a full 2-year 5-minute backtest (210,240 bars), this produces `max_lag ≈ 36` — which consumes a meaningful fraction of autocorrelation structure but is fine. However, for feature evaluation runs on multi-year datasets (1M+ bars), the formula can produce lags of 100+. At that point the Newey-West variance estimate is numerically unstable.

**Fix:** Add a hard cap: `max_lag = min(max_lag, 50)` and document the reasoning.

---

#### L-6 · `plans/` directory contains AI-directed Gemini task files in production repo
**Files:** `docs/plans/2026-03-23-edgee-bug-fixes.md`, `docs/plans/2026-03-24-edgee-bug-fixes-batch-2.md`

These files contain explicit task instructions written for Gemini (`> For Gemini: REQUIRED SUB-SKILL...`). They are committed to the main branch of a production repository. This is a workflow-management concern rather than a code defect, but it suggests the repo may be used as a scratch pad for AI agent prompts, which risks accidental execution of stale task instructions.

**Fix:** Move AI-directed plans to a separate `.ai-tasks/` directory excluded from the main docs build.

---

## Patch Plan — Phases and Milestones

---

### Phase 1 — Critical Fixes (1–2 days)

**Goal:** Eliminate crashes and look-ahead bias. No new features. Strict regression testing required after each fix.

| ID | File | Fix | Test |
|----|------|-----|------|
| C-1 | `eval/selection_bias.py` | Rename `n_arr` → `pnl_arr` | Add `test_dsr_n_trials_gt_1_no_crash` |
| C-2 | `core/causal_primitives.py` | Change `shift(lag-1)` → `shift(lag)` | Add `test_trailing_percentile_rank_no_lookahead` with synthetic forward-leak assertion |

**Milestone 1 gate:** `pytest project/tests/` passes with zero failures. No DeprecationWarnings from the `compute_pnl_components` hot path.

---

### Phase 2 — Statistical Correctness (3–5 days)

**Goal:** Correct the four statistical validity issues that produce wrong numbers silently.

| ID | File | Fix | Test |
|----|------|-----|------|
| H-1 | `core/copula.py` | Call `_estimate_t_df_mle` inside `fit_t_copula` | Assert returned df varies across different input distributions |
| H-2 | `core/stats.py` | Add MacKinnon (1994) finite-sample surface or n≥50 gate | Compare fallback p-values against `statsmodels.coint` for small n |
| H-3 | `eval/selection_bias.py` | Change `(kurt+3)/4` to `kurt/4` | Assert PSR matches reference implementation for known SR/skew/kurt tuple |
| H-4 | `engine/risk_allocator.py` | Fix correlation allocation to use position-weighted returns | Add test: two identical strategies should receive equal weight regardless of position scale |

**Milestone 2 gate:** PSR/DSR values match Bailey & Lopez de Prado reference examples within ±0.01. Copula df MLE activated and tested against synthetic t-distributed data.

---

### Phase 3 — Engine Correctness (1 week)

**Goal:** Fix PnL and risk management correctness issues.

| ID | File | Fix | Test |
|----|------|-----|------|
| H-5 | `engine/risk_allocator.py` | Replace heuristic equity-curve with explicit `pnl_mode` param | Test drawdown calculation for dollar-PnL and return-PnL strategies |
| H-6 | `engine/risk_allocator.py` | Fix pairwise correlation to use equity returns | Verify correlation constraint actually reduces portfolio correlation |
| M-1 | `strategy/templates/evaluate.py` | Migrate to `compute_pnl_ledger` | Existing tests still pass; flip-trade scenarios produce correct net_pnl |
| M-2 | `engine/pnl.py` | Add sub-hourly frequency guard for `use_event_aligned_funding` | Funding overcount scenario: 5-min bars, 3 events/day should accumulate ~3× not ~288× |
| M-6 | `engine/pnl.py` | Assert UTC index in `compute_funding_pnl_event_aligned` | Naive-index test should raise with clear message |

**Milestone 3 gate:** Full backtest on synthetic BTC dataset produces identical PnL to manual calculation. Flip-trade test: long→short→flat in 3 bars, check net_pnl is correct for both `close` and `next_open` modes.

---

### Phase 4 — Robustness & Operational Safety (3–5 days)

**Goal:** Fix operational failure modes — hard crashes on stale data, performance cliffs without numba, vol scaling that penalizes all strategies equally.

| ID | File | Fix | Test |
|----|------|-----|------|
| M-3 | `core/audited_join.py` | Add `stale_action` param, default `"raise"` | Test that `"warn"` mode logs warning without raising |
| M-4 | `engine/risk_allocator.py` | Per-strategy vol scaling before portfolio correction | Two strategies with 2× vol difference should get 2× different scale factors |
| M-5 | `engine/risk_allocator.py` | Add early-exit to Python clamp loop | Benchmark: 100k-bar array, confirm no perf regression vs numba |

**Milestone 4 gate:** Pipeline survives 10% stale funding data in warn mode. Vol scaling produces monotonically lower scale for higher-vol strategies.

---

### Phase 5 — Structural Cleanup (1–2 weeks)

**Goal:** Eliminate technical debt and documentation drift. Low risk changes.

| ID | Target | Action |
|----|--------|--------|
| L-1 | `spec/events/`, `artifacts/baseline/specs/events/`, `spec/ontology/events/` | Designate single source of truth; add CI diff check between copies |
| L-2 | `core/copula.py` | Remove placeholder line; move `import math` to module top |
| L-3 | `engine/risk_allocator.py` | Document cap-then-weight vs weight-then-cap ordering; add inline comment |
| L-4 | `docs/` | Add CI step validating all doc path references exist in repo |
| L-5 | `core/stats.py` | Cap Newey-West max_lag at 50; add `# Andrews (1991) rule of thumb` comment |
| L-6 | `docs/plans/` | Move AI-directed task files to `.ai-tasks/` with `.gitignore` exclusion from build |

**Milestone 5 gate:** Single `spec/events/` directory is the only authoritative event registry. CI passes with path validation. All tests green.

---

## Risk Matrix

| Phase | Regression Risk | Behavioral Change | Reversibility |
|-------|----------------|-------------------|---------------|
| 1 — Critical fixes | Low | PIT safety restored; PSR now callable | Easy — single-line changes |
| 2 — Stats correctness | Medium | PSR values shift; copula df changes | Reversible via feature flag |
| 3 — Engine correctness | High | PnL numbers change for flip trades | Requires golden-regression refresh |
| 4 — Robustness | Low | Operationally transparent | Easy to roll back |
| 5 — Structural cleanup | Low | No runtime behavior change | Easy |

**Recommendation on ordering:** Do not merge Phase 3 without refreshing the golden regression benchmarks in `spec/benchmarks/`. The `compute_pnl_ledger` migration will produce different PnL for strategies with flip trades in `next_open` mode, which is the *correct* behavior — but the existing golden numbers were computed with the incorrect semantics and must be regenerated.

---

## Appendix — File-Level Impact Map

```
project/
├── core/
│   ├── causal_primitives.py    C-2 (critical)
│   ├── copula.py               H-1, L-2
│   └── stats.py                H-2, H-3, L-5
├── engine/
│   ├── pnl.py                  M-2, M-6
│   └── risk_allocator.py       H-4, H-5, H-6, M-3, M-4, M-5, L-3
├── eval/
│   └── selection_bias.py       C-1, H-3
├── strategy/templates/
│   └── evaluate.py             M-1
└── core/audited_join.py        M-3

spec/                           L-1 (ontology dedup)
project/artifacts/baseline/     L-1 (ontology dedup)
docs/                           L-4, L-6
```
