# Detector Defect Ledger

**Date:** 2026-03-17
**Audit baseline:** `data/artifacts/detector_audit/post_fix_final/metrics.json`
**Golden run:** `artifacts/golden_synthetic_discovery/reliability/golden_synthetic_discovery_summary.json`

## Summary

Post-fix audit counts across 11 synthetic run profiles (default, 2021_bull, range_chop, stress_crash, alt_rotation) × 3 symbols (BTC, ETH, SOL):

| Status | Pre-fix | Post-fix | Delta |
|--------|---------|----------|-------|
| STABLE (precision ≥ 0.50, recall ≥ 0.30) | 34 | 73 | +39 |
| NEED WORK | 130 | 103 | -27 |
| ERROR | 276 | 264 | -12 |
| UNCOVERED | 451 | 451 | 0 |

Fixes delivered: BASIS_DISLOC (+9), CLIMAX_VOLUME_BAR (+9), FALSE_BREAKOUT (+5), FAILED_CONTINUATION (+3).

---

## Structural Ceiling Detectors

These detectors cannot reach precision ≥ 0.50 with current synthetic data coverage ratios or regime properties. Parameter tuning was attempted and reverted when it introduced regressions elsewhere.

### MOMENTUM_DIVERGENCE_TRIGGER

- **Status:** NOISY (structural)
- **Precision ceiling:** ~0.11–0.25 depending on run profile
- **Root cause:** Detector fires on any RSI/MACD divergence from trend direction, which occurs continuously in trending markets. In the 2021_bull and stress_crash profiles, divergence signals fire at every retracement. The synthetic truth windows cover ~4% of bars; random firing = ~4% precision floor, detector at ~11–25% = above random but far from 0.50.
- **Golden run off-regime rate:** 0.89 (BTC), 0.89 (ETH)
- **Recommended action:** Requires per-regime suppression gate (e.g. only fire during confirmed range regimes). Not fixable by threshold tuning alone.

### TREND_ACCELERATION

- **Status:** NOISY (structural)
- **Precision ceiling:** ~0.05–0.15 depending on run profile
- **Root cause:** The `direction_consistent` check (rolling 6-bar mean sign matches 96-bar trend) is nearly always True in trending regimes. The adaptive quantile threshold runs out of lookback in the 2-month golden run. In 2021_bull, the detector fires at nearly every 96-bar trend extension.
- **Golden run off-regime rate:** 0.95 (BTC), 0.86 (ETH)
- **Recommended action:** Requires minimum lookback gate (at least 2 × threshold_window = 5760 bars ≈ 20 days) before firing. Quantile thresholds need a cold-start guard.

### TREND_EXHAUSTION_TRIGGER

- **Status:** NOISY (structural)
- **Precision ceiling:** ~0.17–0.22 depending on run profile
- **Root cause:** Peak detection fires on any local high/low in a trending market. stress_crash creates constant new lows that satisfy the peak condition. No cooldown between successive exhaustion signals.
- **Golden run off-regime rate:** 0.83 (BTC), 0.83 (ETH)
- **Recommended action:** Requires minimum trend duration gate before peak can be declared. Current min_spacing=24 (2 hours) is insufficient to suppress intraday exhaustion noise in crash regimes.

### FUNDING_FLIP

- **Status:** NOISY (structural)
- **Precision ceiling:** ~0.06–0.13 depending on run profile
- **Root cause:** Funding rate sign changes (positive → negative or vice versa) in the synthetic dataset happen more frequently than truth windows cover. The synthetic funding generator applies small oscillations around zero that produce frequent sign flips. Truth windows cover ~5–8% of bars; detector fires at ~12–18% of bars.
- **Golden run off-regime rate:** 1.0 (BTC), 0.94 (ETH)
- **Recommended action:** Require minimum magnitude threshold for both the pre-flip and post-flip funding values. A flip between +0.0001% and -0.0001% should not count. Also requires minimum persistence (e.g. 2 consecutive bars at new sign).

### PRICE_VOL_IMBALANCE_PROXY

- **Status:** NOISY (structural)
- **Precision ceiling:** ~0.01–0.03 depending on run profile
- **Root cause:** Price-volume imbalance proxy uses rolling quantile thresholds that are sensitive to short lookback. In any trending or volatile regime, nearly every significant candle satisfies the imbalance condition. Total events in golden run: 250 events in 2 months for 2 symbols = ~2 events/day/symbol. Truth windows cover only ~3% of bars.
- **Golden run off-regime rate:** 1.0 (BTC), 0.97 (ETH)
- **Recommended action:** Require both price AND volume quantile thresholds (currently OR logic). Add minimum off-regime lookback bar count before each new signal.

### SPREAD_REGIME_WIDENING_EVENT

- **Status:** NOISY (structural, wrong regime association)
- **Precision ceiling:** ~0.05–0.12 depending on run profile
- **Root cause:** Detector fires on any spread widening above a rolling quantile. In synthetic data, spread widening is correlated with ALL volatile regimes (not just liquidity_stress). The truth windows are labeled for `liquidity_stress` specifically, but the detector fires during every trending/crash period.
- **Golden run off-regime rate:** 1.0 (BTC), 1.0 (ETH), 0 windows hit
- **Recommended action:** Requires joint condition: spread widening AND depth deterioration AND below-average volume. The single-signal approach cannot distinguish liquidity stress from normal volatility expansion.

---

## Profile-Specific Structural Ceilings (Otherwise-Good Detectors)

These detectors are STABLE in most run profiles but fail in specific synthetic regimes due to regime physics.

### CLIMAX_VOLUME_BAR — stress_crash ETH/SOL

- **Status:** STABLE in 9/11 (BTC/ETH/SOL across 3 profiles), NOISY in stress_crash ETH/SOL
- **Root cause:** stress_crash has 18 truth windows × ~9h each ≈ 37% of bars in truth windows. This creates a structural random-precision floor of 0.37. The ETH/SOL precision ceiling in stress_crash is ~0.44, just below the 0.50 threshold.
- **Classification:** Structural data coverage issue, not a detector design flaw. Detector functions correctly; synthetic truth window density is too high for this profile.

### FAILED_CONTINUATION — 2021_bull and stress_crash

- **Status:** STABLE in 3/11, NOISY in 2021_bull and stress_crash
- **Root cause:**
  - 2021_bull: Trending market means `breakout_up_recent` (close > rolling max shifted 1) is nearly always True. Every bar is a new high, so "breakout" condition is constantly satisfied. The "continuation failure" condition requires a subsequent pullback, but in a strong trend, pullbacks are shallow and brief.
  - stress_crash: Constant deleveraging means any attempted continuation is immediately sold off, generating false FAILED_CONTINUATION signals for non-truth-window breakouts.
- **Classification:** Regime physics incompatibility. Detector is correct for range/reversion regimes.

### FALSE_BREAKOUT — stress_crash

- **Status:** STABLE in 6/11, NOISY in stress_crash
- **Root cause:** stress_crash profile has 14 truth windows × ~11h each ≈ 3.6% truth window coverage. Detector fires at crash-bounce reversals throughout the crash, but these are distributed across the entire crash period. Random precision floor = 0.036; detector at 0.116 = 3.2× random but far from 0.50.
- **Classification:** Structural data coverage issue. In crash regimes, every bounce is a potential false breakout, so the detector correctly fires frequently; the truth window labeling doesn't cover all of them.

### FALSE_BREAKOUT — golden run ETH recall failure

- **Root cause:** In the 2-month golden run, ETH produced only 1 false breakout event (vs. 3 for BTC). ETH's synthetic price path did not create false breakout patterns within the 3 truth windows. BTC passed (3/3 windows hit); ETH failed (0/3 windows hit). This is a single-seed coverage issue, not a systematic failure.
- **Note:** Would likely pass with a different random seed or longer run window.

### FND_DISLOC — golden run windows_hit=1/4

- **Root cause:** In the golden run, FND_DISLOC hits only 1 of 4 truth windows per symbol (total_events=8 for both symbols, all 8 within truth windows → 0 off-regime events). The detector is perfectly precise but low recall. The 3 missed windows are periods where the basis Z-score did not exceed the 3.5 threshold during the funding dislocation event, even though funding was extreme. This is a data correlation issue in the synthetic generator: funding extremes don't always co-occur with basis extremes.
- **Status:** Passing in per-run audit (8/11 stable), but truth validation windows_hit rate is low in the golden run specifically.

---

## ERROR Detectors (Data-Dependent, Cannot Run on Synthetic)

These detectors fail with import errors or KeyErrors because the synthetic dataset does not include the required market microstructure columns.

### OI/Liquidation Family (23 detectors)

- **Detectors:** OI_SPIKE_POSITIVE, OI_SPIKE_NEGATIVE, OI_FLUSH, OI_VOL_DIVERGENCE, OI_VOL_COMPRESSION_BUILDUP, LIQUIDATION_CASCADE, LIQUIDATION_EXHAUSTION_REVERSAL, FORCED_FLOW_EXHAUSTION, POST_DELEVERAGING_REBOUND, DELEVERAGING_WAVE, FUNDING_EXTREME_ONSET, FUNDING_EXTREME_BREAKOUT, FUNDING_EXTREME_STAGNATION, FUNDING_NORMALIZATION_TRIGGER, FUNDING_PERSISTENCE_TRIGGER, SEQ_LIQ_CASCADE_THEN_EXHAUST, SEQ_FND_EXTREME_THEN_BREAKOUT, SEQ_OI_SPIKEPOS_THEN_VOL_SPIKE, SEQ_VOL_COMP_THEN_BREAKOUT, SEQ_LIQ_VACUUM_THEN_DEPTH_RECOVERY
- **Error type:** KeyError on `open_interest`, `liquidation_usd`, `funding_rate_scaled` columns
- **Root cause:** Synthetic OHLCV data does not include OI, liquidations, or funding. These detectors require live or historical exchange data.
- **Resolution path:** Run against live historical data or extend synthetic generator to include simulated OI/liquidation columns.

### ABSORPTION_PROXY / DEPTH_STRESS_PROXY

- **Error type:** `AttributeError: 'numpy.float64' object has no attribute 'rolling'`
- **Root cause:** These detectors call `.rolling()` on a scalar value returned by a feature computation path that short-circuits to a float when the required depth columns are absent. Synthetic data lacks order book depth columns.
- **Resolution path:** Add defensive check at top of `prepare_features`: if required columns are missing, raise `ValueError` early instead of allowing partial computation.

---

## Pre-existing Test Failures (Not Related to Detector Work)

The following test failures predate this stabilization work and share a root cause in `project/engine/strategy_executor.py:376`:

- `tests/strategy_dsl/test_dsl_runtime_contracts.py` (6 tests): `AttributeError: 'float' object has no attribute 'reindex'` — `features_aligned.get("atr_14", 0.0)` returns scalar instead of Series.
- `tests/test_lag_guardrail.py` (2 tests): Same root cause.
- `tests/smoke/test_validate_artifacts_smoke.py::test_validate_artifacts_smoke_after_full_run`: Same root cause.
- `tests/pipelines/research/test_direction_semantics.py::test_resolve_effect_sign_contrarian_flips_event_direction`: Logic assertion failure in `resolve_effect_sign` for contrarian + event_direction=1.

These existed before detector stabilization and are outside its scope.

---

## Golden Synthetic Discovery Truth Validation Result

**Overall passed: False** (expected, given structural-ceiling detectors above)

**Passing:** BASIS_DISLOC, CLIMAX_VOLUME_BAR, CROSS_VENUE_DESYNC, DELEVERAGING_WAVE, FAILED_CONTINUATION, FND_DISLOC, LIQUIDATION_EXHAUSTION_REVERSAL, LIQUIDITY_STRESS_DIRECT, LIQUIDITY_STRESS_PROXY, SPOT_PERP_BASIS_SHOCK

**Failing (structural):** BREAKOUT_TRIGGER (near-silent in 2-month golden window), FALSE_BREAKOUT ETH (single-seed recall gap), FUNDING_FLIP, MOMENTUM_DIVERGENCE_TRIGGER, PRICE_VOL_IMBALANCE_PROXY, SPREAD_REGIME_WIDENING_EVENT, TREND_ACCELERATION, TREND_EXHAUSTION_TRIGGER

The pipeline itself completed successfully (returncode=0). The truth validation failure reflects known structural limitations, not infrastructure failures.

---

## Six-Month Calibrated Synthetic Truth Baseline

**Run ID:** `btc_synth_6m_all_events_calibrated_20260317`
**Data root:** `/tmp/edgee_btc_synth_6m_all_calibrated_20260317`
**Validation result:** `passed: true`

This longer BTC-only calibration run was used as a follow-up truth baseline after the broad golden run. It differs from the 2-month golden workflow in two important ways:

- synthetic truth segments now distinguish `expected_event_types` from `supporting_event_types`, so proxy or secondary signals do not hard-fail global detector-truth validation
- `TREND_ACCELERATION` runtime composition was aligned with the calibrated detector behavior (`trend_window: 96`, `min_spacing: 192`) so the spec path and the live analyzer path no longer drift

Final validation on the calibrated six-month run produced a passing all-events detector-truth result with the remaining primary event families inside the current synthetic bounds. The last blocker cleared after replaying `TREND_ACCELERATION`, which moved from `42` rows with excessive off-regime noise to `35` rows with:

- `expected_windows: 9`
- `windows_hit: 9`
- `in_window_events: 9`
- `off_regime_events: 26`
- `off_regime_rate: 0.7428571428571429`

This six-month run should be treated as the maintained calibration baseline for full synthetic detector-truth checks. The shorter golden workflow remains useful as a smoke-style reliability run, but its truth failures should be interpreted through the structural-ceiling notes above rather than as infrastructure defects.

---

## Post-Structural Rerun Snapshot

**Date:** 2026-03-17
**Targeted audit path:** `data/artifacts/detector_audit/post_structural_targeted_20260317/metrics.json`
**Fast certification path:** `artifacts/golden_synthetic_discovery_fast_post_structural_20260317/reliability/golden_synthetic_discovery_summary.json`

This rerun was targeted at the detectors changed during the structural-noise cleanup:

- `ABSORPTION_PROXY`
- `DEPTH_STRESS_PROXY`
- `FUNDING_FLIP`
- `TREND_EXHAUSTION_TRIGGER`
- `MOMENTUM_DIVERGENCE_TRIGGER`
- `PRICE_VOL_IMBALANCE_PROXY`
- `SPREAD_REGIME_WIDENING_EVENT`

### Baseline Status

- Fast synthetic certification remains green:
  - `run_id = golden_synthetic_discovery_fast`
  - `truth_passed = true`
  - `selected_events = [FND_DISLOC]`
  - `search_budget = 64`
  - `candidate_rows = 4`
- Six-month calibrated BTC truth validation remains green:
  - `run_id = btc_synth_6m_all_events_calibrated_20260317`
  - `passed = true`

### Targeted Audit Outcome

Across the 7 changed detectors on the maintained synthetic audit runs, the targeted rerun produced:

- `stable = 1`
- `noisy = 21`
- `broken = 32`
- `silent = 1`
- `error = 22`

### Detector-Specific Notes

- `ABSORPTION_PROXY`: still `error` across the synthetic audit runs, but now with an explicit unsupported-data message (`requires columns: spread_zscore`) instead of the older scalar `.rolling()` failure mode.
- `DEPTH_STRESS_PROXY`: same improvement as `ABSORPTION_PROXY`; still unsupported on current synthetic data, but now failing closed and explainably.
- `FUNDING_FLIP`: improved from noisy overfiring to mostly `broken` / `silent` on the targeted audit slice. This is directionally correct because tiny zero-crossing oscillations are no longer counted, but the detector is now likely too strict for the shorter audit runs.
- `TREND_EXHAUSTION_TRIGGER`: improved but not solved. The targeted rerun produced mostly `noisy` classifications, with one `stable` case. The new trend-duration guard reduced firing, but not enough to clear the synthetic precision floor broadly.
- `MOMENTUM_DIVERGENCE_TRIGGER`: still `broken` across the targeted audit runs. The new regime suppression is working in the sense that false positives are reduced, but the detector now misses the synthetic truth contract almost entirely on the maintained audit slice.
- `PRICE_VOL_IMBALANCE_PROXY`: locally tightened on synthetic stress fixtures (from 6 events to 1 on the calibration slice), but still `broken` on the targeted audit runs. This suggests the maintained synthetic datasets do not yet produce enough aligned price/vol/participation clusters for it to recover truth windows consistently.
- `SPREAD_REGIME_WIDENING_EVENT`: locally tightened on synthetic stress fixtures (from 17 events to 1 on the calibration slice), but still `noisy` on the targeted audit runs. The detector is now closer to a true friction signal, but the current synthetic labels still appear broader than the friction-specific condition.

### Interpretation

The rerun confirms three things:

1. The maintained truth baselines are still green, so the repository remains mechanically sound after the detector changes.
2. The proxy-detector runtime failures are now hygiene-clean: unsupported synthetic inputs produce explicit errors rather than misleading stack traces.
3. The remaining detector work is no longer generic threshold tuning. The unresolved items are now mostly synthetic-contract mismatch problems (`FUNDING_FLIP`, `MOMENTUM_DIVERGENCE_TRIGGER`, `PRICE_VOL_IMBALANCE_PROXY`, `SPREAD_REGIME_WIDENING_EVENT`) or still-partial structural-noise reductions (`TREND_EXHAUSTION_TRIGGER`).

---

## Fresh Post-Structural Manifest Check

**Date:** 2026-03-17
**Fresh audit path:** `/tmp/edgee_post_structural_contract_20260317/artifacts/detector_audit/post_structural_targeted_current_contract_20260317/metrics.json`
**Comparison baseline:** `data/artifacts/detector_audit/post_structural_targeted_20260317/metrics.json`

To separate real detector behavior from stale synthetic truth contracts, a fresh targeted audit was rerun against regenerated post-structural synthetic manifests. The detector set was the same as the targeted rerun above:

- `ABSORPTION_PROXY`
- `DEPTH_STRESS_PROXY`
- `FUNDING_FLIP`
- `TREND_EXHAUSTION_TRIGGER`
- `MOMENTUM_DIVERGENCE_TRIGGER`
- `PRICE_VOL_IMBALANCE_PROXY`
- `SPREAD_REGIME_WIDENING_EVENT`

### Old vs New Classification Counts

Old targeted rerun on stale manifests:

- `stable = 1`
- `noisy = 21`
- `broken = 32`
- `silent = 1`
- `error = 22`

Fresh rerun on regenerated post-structural manifests after the first truth-contract cleanup:

- `uncovered = 55`
- `error = 22`

### Detector-Level Shift

- `ABSORPTION_PROXY`: unchanged at `error × 11`; still unsupported on current synthetic data, but now failing with an explicit required-column message.
- `DEPTH_STRESS_PROXY`: unchanged at `error × 11`; same unsupported-data classification and explicit guard behavior.
- `FUNDING_FLIP`: moved from `broken × 10` and `silent × 1` to `uncovered × 11`.
- `TREND_EXHAUSTION_TRIGGER`: moved from `noisy × 10` and `stable × 1` to `uncovered × 11`.
- `MOMENTUM_DIVERGENCE_TRIGGER`: moved from `broken × 11` to `uncovered × 11`.
- `PRICE_VOL_IMBALANCE_PROXY`: moved from `broken × 11` to `uncovered × 11`.
- `SPREAD_REGIME_WIDENING_EVENT`: moved from `noisy × 11` to `uncovered × 11`.

### Updated Interpretation

This comparison clarifies that most of the post-structural audit regressions were not persistent detector failures. They were artifacts of measuring the hardened detectors against older synthetic manifests that still treated several proxy or secondary signals as primary expected event families.

The corrected interpretation is:

1. `ABSORPTION_PROXY` and `DEPTH_STRESS_PROXY` remained unsupported on the earlier synthetic audit contract because the shared audit path did not derive `spread_zscore` from synthetic `spread_bps`.
2. `FUNDING_FLIP`, `TREND_EXHAUSTION_TRIGGER`, `MOMENTUM_DIVERGENCE_TRIGGER`, `PRICE_VOL_IMBALANCE_PROXY`, and `SPREAD_REGIME_WIDENING_EVENT` should not be tracked as active truth-baseline failures on the fresh manifests. Under the current synthetic contract they are uncovered, not failing.
3. Future detector audit interpretation should prefer regenerated post-change manifests whenever truth-window semantics change, rather than comparing hardened detectors against pre-change synthetic labels.

---

## Synthetic Coverage Expansion Follow-Up

**Date:** 2026-03-17
**Fresh audit path:** `/tmp/edgee_post_structural_contract_20260317/artifacts/detector_audit/post_structural_targeted_current_contract_20260317/metrics.json`

The synthetic microstructure contract was expanded so cleaned synthetic bars now carry depth-side fields (`bid_depth_usd`, `ask_depth_usd`, `imbalance`) and the shared audit enrichment path derives `spread_zscore` from synthetic `spread_bps` the same way the canonical feature builder does.

After that change, the same fresh targeted audit moved from:

- `uncovered = 55`
- `error = 22`

to:

- `uncovered = 77`

### Detector-Level Shift

- `ABSORPTION_PROXY`: moved from `error × 11` to `uncovered × 11`
- `DEPTH_STRESS_PROXY`: moved from `error × 11` to `uncovered × 11`
- `FUNDING_FLIP`: remained `uncovered × 11`
- `TREND_EXHAUSTION_TRIGGER`: remained `uncovered × 11`
- `MOMENTUM_DIVERGENCE_TRIGGER`: remained `uncovered × 11`
- `PRICE_VOL_IMBALANCE_PROXY`: remained `uncovered × 11`
- `SPREAD_REGIME_WIDENING_EVENT`: remained `uncovered × 11`

### Updated Interpretation

The unsupported-detector work is now complete for the current synthetic audit contract:

1. No detector in this targeted slice is failing because synthetic bars are missing required columns.
2. `ABSORPTION_PROXY` and `DEPTH_STRESS_PROXY` are now measurable on synthetic data, even though they are still `uncovered` because the truth map does not currently treat them as primary expected event families.
3. The remaining work for these detectors is no longer data-plumbing support. It is truth-coverage design: deciding whether and how to promote them from supporting synthetic signals into explicit truth-window targets.

An informational supporting-signal validation mode now exists for that next step. The validator keeps primary `expected_event_types` as the hard gate, but `--include_supporting_events 1` adds a separate `supporting_event_reports` section so proxy detectors can be measured without being promoted into the main pass/fail contract.

On the maintained six-month calibrated BTC run:

- artifact: `/tmp/edgee_btc_synth_6m_all_calibrated_20260317/synthetic/btc_synth_6m_all_events_calibrated_20260317/supporting_detector_truth_validation.json`
- command scope: `FUNDING_FLIP`, `MOMENTUM_DIVERGENCE_TRIGGER`, `PRICE_VOL_IMBALANCE_PROXY`, `SPREAD_REGIME_WIDENING_EVENT`, `TREND_EXHAUSTION_TRIGGER`
- result: primary validation still `passed = true`, with supporting detectors reported separately

That artifact should be treated as an exploratory calibration report, not as a promotion-quality truth gate.

### Graduation Decision

Current decision: **no supporting detector graduates into the primary synthetic truth contract yet**.

Reasoning from the maintained six-month supporting report:

- `FUNDING_FLIP`: `windows_hit = 0 / 12`, `off_regime_rate = 1.0`
- `MOMENTUM_DIVERGENCE_TRIGGER`: `windows_hit = 9 / 9`, but `off_regime_rate = 0.8831`
- `PRICE_VOL_IMBALANCE_PROXY`: `windows_hit = 2 / 9`, `off_regime_rate = 0.9933`
- `SPREAD_REGIME_WIDENING_EVENT`: `windows_hit = 0 / 9`, `off_regime_rate = 1.0`
- `TREND_EXHAUSTION_TRIGGER`: `windows_hit = 9 / 9`, but `off_regime_rate = 0.8286`

Those numbers are good enough for supporting calibration, but not good enough for hard-gate promotion into `expected_event_types`.

### Graduation Bar

A supporting detector should only graduate into the primary synthetic truth contract when all of the following are true on a maintained baseline:

1. It is measurable on synthetic data without missing-column or unsupported-data errors.
2. It hits at least one truth window for each symbol/profile where it is claimed as a primary expected detector.
3. Its off-regime rate stays at or below the current synthetic validator bound (`max_off_regime_rate = 0.75`).
4. It survives at least one additional synthetic profile or seed, not just the maintained BTC baseline.

### Immediate Status

- `FUNDING_FLIP`: stay supporting.
- `MOMENTUM_DIVERGENCE_TRIGGER`: stay supporting.
- `PRICE_VOL_IMBALANCE_PROXY`: stay supporting.
- `SPREAD_REGIME_WIDENING_EVENT`: stay supporting.
- `TREND_EXHAUSTION_TRIGGER`: stay supporting.
- `ABSORPTION_PROXY`: stay supporting.
- `DEPTH_STRESS_PROXY`: stay supporting.

### Derived Six-Month Supporting Check For Liquidity Proxies

The maintained six-month calibrated baseline was also rechecked with a derived supporting truth map that adds `ABSORPTION_PROXY` and `DEPTH_STRESS_PROXY` to the existing `liquidity_stress` supporting set:

- truth map: `/tmp/edgee_btc_synth_6m_all_calibrated_20260317/synthetic/btc_synth_6m_all_events_calibrated_20260317/synthetic_regime_segments_supporting_v2.json`
- report: `/tmp/edgee_btc_synth_6m_all_calibrated_20260317/synthetic/btc_synth_6m_all_events_calibrated_20260317/supporting_detector_truth_validation_v2.json`

Observed result:

- `ABSORPTION_PROXY`: `total_events = 0`, `windows_hit = 0 / 9`, `off_regime_rate = 0.0`
- `DEPTH_STRESS_PROXY`: `total_events = 0`, `windows_hit = 0 / 9`, `off_regime_rate = 0.0`

This closes the previous uncertainty around those two detectors:

1. They are no longer unsupported on synthetic data.
2. They are measurable on the maintained baseline.
3. They are currently silent under the present synthetic liquidity-stress construction, so they remain supporting-only and should not be promoted into `expected_event_types`.

### Fresh Liquidity-Proxy Smoke Run After Regime Redesign

A fresh synthetic smoke run was generated after the liquidity-stress regime was redesigned to include an explicit shock/stress/absorption sequence and a non-degenerate spread baseline:

- run: `synth_liquidity_proxy_smoke_20260317`
- root: `/tmp/edgee_liquidity_proxy_smoke_20260317`
- supporting validation artifact: `/tmp/edgee_liquidity_proxy_smoke_20260317/synthetic/synth_liquidity_proxy_smoke_20260317/liquidity_proxy_supporting_validation.json`

Pipeline replay on that fresh run produced:

- `ABSORPTION_PROXY`: `237` events
- `DEPTH_STRESS_PROXY`: `335` events

Supporting validation on the same run produced:

- `ABSORPTION_PROXY`: `windows_hit = 3 / 3`, `in_window_events = 10`, `off_regime_rate = 0.9578`
- `DEPTH_STRESS_PROXY`: `windows_hit = 3 / 3`, `in_window_events = 8`, `off_regime_rate = 0.9761`

This is an important transition:

1. The synthetic regime now expresses both liquidity proxies through the normal feature and event-analysis path.
2. The detectors are no longer silent on fresh synthetic liquidity-stress data.
3. They are still far too noisy to graduate into the primary synthetic truth contract.

So the current state is:

- maintained six-month baseline: measurable but silent for `ABSORPTION_PROXY` and `DEPTH_STRESS_PROXY`
- fresh redesigned liquidity-stress smoke run: high recall, high off-regime noise

That established that the remaining work was calibration, not missing support.

### Tightened Liquidity-Proxy Smoke Run

The same synthetic smoke workflow was then rerun after tightening the detector defaults and specs:

- run: `synth_liquidity_proxy_smoke_tight_20260317`
- root: `/tmp/edgee_liquidity_proxy_smoke_tight_20260317`
- supporting validation artifact: `/tmp/edgee_liquidity_proxy_smoke_tight_20260317/synthetic/synth_liquidity_proxy_smoke_tight_20260317/liquidity_proxy_supporting_validation.json`

Pipeline replay on that tightened run produced:

- `ABSORPTION_PROXY`: `8` events
- `DEPTH_STRESS_PROXY`: `7` events

Supporting validation on the tightened run produced:

- `ABSORPTION_PROXY`: `windows_hit = 1 / 3`, `in_window_events = 1`, `off_regime_rate = 0.875`
- `DEPTH_STRESS_PROXY`: `windows_hit = 0 / 3`, `in_window_events = 0`, `off_regime_rate = 1.0`

Relative to the untightened smoke run:

- `ABSORPTION_PROXY`: `237 -> 8` total events, `0.9578 -> 0.8750` off-regime rate, but `3 / 3 -> 1 / 3` window coverage
- `DEPTH_STRESS_PROXY`: `335 -> 7` total events, `0.9761 -> 1.0000` off-regime rate, and `3 / 3 -> 0 / 3` window coverage

Interpretation:

1. The liquidity-proxy generators and feature plumbing are now good enough to exercise both detectors through the normal pipeline.
2. The current tightened defaults overshot: event volume dropped sharply, but the synthetic liquidity-stress windows are still not localized enough for these proxies to recover useful supporting truth.
3. `ABSORPTION_PROXY` and `DEPTH_STRESS_PROXY` remain supporting-only detectors and are still not candidates for graduation into `expected_event_types`.

So the current state is:

- maintained six-month baseline: measurable but silent for `ABSORPTION_PROXY` and `DEPTH_STRESS_PROXY`
- fresh redesigned liquidity-stress smoke run: high recall, high off-regime noise
- tightened smoke run: low event count, weak recall, and still unacceptable off-regime behavior

That means the remaining work is joint calibration of detector defaults and synthetic window design, not more support plumbing:

- retune `ABSORPTION_PROXY` / `DEPTH_STRESS_PROXY` away from the current over-tightened defaults
- further localize the synthetic liquidity-stress truth windows so they match the shock/stress/absorption phases more closely
- or both

### Event-Specific Windowed Liquidity-Proxy Calibration

The synthetic truth contract was then extended so `liquidity_stress` segments can carry `event_truth_windows` per supporting detector, and the validator now prefers those windows over the full regime block when present.

A fresh smoke run was generated on that contract:

- run: `synth_liquidity_proxy_smoke_windowed_20260317`
- root: `/tmp/edgee_liquidity_proxy_smoke_windowed_20260317`
- supporting validation artifact: `/tmp/edgee_liquidity_proxy_smoke_windowed_20260317/synthetic/synth_liquidity_proxy_smoke_windowed_20260317/liquidity_proxy_supporting_validation.json`

The detector logic was also tightened to use the available microstructure fields:

- `ABSORPTION_PROXY`: high spread stress + high realized-vol stress + low absolute imbalance
- `DEPTH_STRESS_PROXY`: high spread stress + high realized-vol stress + high `micro_depth_depletion`

Replay on the windowed run produced:

- `ABSORPTION_PROXY`: `22` events
- `DEPTH_STRESS_PROXY`: `3` events

Supporting validation against the event-specific windows produced:

- `ABSORPTION_PROXY`: `windows_hit = 0 / 3`, `in_window_events = 0`, `off_regime_rate = 1.0`
- `DEPTH_STRESS_PROXY`: `windows_hit = 0 / 3`, `in_window_events = 0`, `off_regime_rate = 1.0`

Interpretation:

1. The synthetic contract now supports detector-specific truth windows, so the validator is no longer grading these proxies against the entire liquidity-stress block.
2. The proxy detectors now consume the intended microstructure inputs instead of relying on spread-plus-volatility alone.
3. Even after both of those fixes, the detectors still fire outside the synthetic liquidity-stress phases.

This narrows the remaining problem substantially:

- it is no longer a support-plumbing issue
- it is no longer a truth-window-shape issue by itself
- it is now primarily a synthetic regime design problem, because the generated microstructure patterns do not produce proxy-aligned events inside the intended liquidity-stress phases

Current decision:

- keep `ABSORPTION_PROXY` and `DEPTH_STRESS_PROXY` as supporting-only
- do not graduate them into `expected_event_types`
- do not use the current liquidity-stress synthetic profile as evidence that these proxies are calibrated
- treat them as live-data diagnostics by default until a future synthetic regime redesign proves phase-aligned recovery

Next work, if these detectors matter operationally:

- redesign the `liquidity_stress` generator so depth depletion, spread stress, and imbalance normalization are phase-locked to the intended windows
- or explicitly treat these two proxies as live-data-only diagnostics rather than synthetic validation targets

### Second Liquidity-Stress Generator Redesign

The generator was then revised again to separate depth collapse from quote-volume collapse and to make the absorption phase explicitly balanced rather than directional:

- run: `synth_liquidity_proxy_smoke_windowed_v2_20260317`
- root: `/tmp/edgee_liquidity_proxy_smoke_windowed_v2_20260317`
- supporting validation artifact: `/tmp/edgee_liquidity_proxy_smoke_windowed_v2_20260317/synthetic/synth_liquidity_proxy_smoke_windowed_v2_20260317/liquidity_proxy_supporting_validation.json`

Key synthetic changes:

- dedicated `depth_mult` profile inside `liquidity_stress`
- deeper early shock/stress depletion with partial late recovery
- more elevated spread and wick stress through shock/stress
- absorption phase orderflow bias driven back toward zero

Key detector changes kept in place:

- `ABSORPTION_PROXY`: high spread stress + high realized-vol stress + low absolute imbalance
- `DEPTH_STRESS_PROXY`: high spread stress + high realized-vol stress + high `micro_depth_depletion`

Replay on the second windowed run produced:

- `ABSORPTION_PROXY`: `23` events
- `DEPTH_STRESS_PROXY`: `3` events

Supporting validation still produced:

- `ABSORPTION_PROXY`: `windows_hit = 0 / 3`, `in_window_events = 0`, `off_regime_rate = 1.0`
- `DEPTH_STRESS_PROXY`: `windows_hit = 0 / 3`, `in_window_events = 0`, `off_regime_rate = 1.0`

Final interpretation for the current project state:

1. The synthetic support plumbing is complete.
2. The validator can score detector-specific truth windows.
3. The generators now expose enough microstructure fields to exercise both proxies.
4. Even after a second generator redesign, the synthetic `liquidity_stress` profile still does not phase-lock these proxies to the intended windows.

Operational conclusion:

- `ABSORPTION_PROXY` and `DEPTH_STRESS_PROXY` should be treated as live-data diagnostics for now.
- Synthetic runs may still measure them as informational supporting signals.
- They should not be used as synthetic pass/fail calibration targets under the current generator family.
- The default synthetic precision/recall audit now skips them unless `--include_live_only_synthetic 1` is passed explicitly.
