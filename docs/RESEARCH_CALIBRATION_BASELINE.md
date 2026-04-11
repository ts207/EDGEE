# Research Calibration Baseline

This document records the current bounded calibration baseline for research, validation,
and promotion comparisons. It is intentionally explicit so repository contracts can detect
silent drift.

## Promotion defaults

Canonical promotion defaults are defined in `project/research/services/promotion_service.py`.
Current defaults:

- `min_events = 100`
- `min_dsr = 0.5`
- `max_overlap_ratio = 0.80`
- `max_profile_correlation = 0.90`
- `require_hypothesis_audit = 1`
- `allow_missing_negative_controls = 0`
- `allow_discovery_promotion = 0`

## Calibration thresholds

- `max_phase2_candidate_count_delta_abs = 10`
- `max_phase2_survivor_count_delta_abs = 2.0`
- `max_promotion_promoted_count_delta_abs = 2`
- `max_edge_candidate_count_delta_abs = 2.0`
- `max_edge_median_resolved_cost_bps_delta_abs = 0.25`
- `max_edge_median_expectancy_bps_delta_abs = 0.25`

Observation minimums used in the baseline package:

- `min_total_n_obs = 30`
- `min_total_n_obs = 4`

## Reference runs and scenarios

Primary relaxed-promotion comparison reference:

- `synthetic_2025_full_year_v4_promo_relaxed_dsr0`
- `failed_gate_promo_dsr`

Medium synthetic calibration references:

- `e2e_synth_medium_candidate`
- `e2e_synth_medium_continuation_only`
- `e2e_synth_medium_continuation_only_runall_searchfix_live`
- `e2e_synth_medium_continuation_only_runall_fanout_fix`

Representative command shape:

```bash
PYTHONPATH=. python3 project/pipelines/run_all.py \
  --templates continuation \
  --run_phase2_conditional 1 \
  --skip_ingest_ohlcv 1 \
  --funding_scale decimal
```

The baseline explicitly tracks `tradable_count` in addition to phase-2 and edge exports.

## Known drift examples captured by the baseline

These strings are retained verbatim because downstream repository tests assert them and
because they document the magnitude of historical regressions that the bounded thresholds
are intended to prevent.

- `edge candidate_count delta=-3`
- `phase2 candidate_count delta=3400`
- `phase2 survivor_count delta=3400`
- `edge candidate_count delta=-6`
- `edge median_resolved_cost_bps delta=-6.0`
- `edge median_expectancy_bps delta=6.0`

## Interpretation

The purpose of this baseline is not to freeze the system forever. It exists to force any
meaningful change in search fanout, bridge tradability, or promotion behavior to be made
explicit, reviewed, and accompanied by an updated calibration narrative.
