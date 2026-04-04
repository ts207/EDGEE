# Discovery Benchmarks

## Overview
This document explains the benchmark configurations, thresholds, and review processes for the discovery layer.

## Benchmark Presets
Presets are fixed combinations of slices and discovery modes.
- **core_v1**: The canonical preset evaluating multiple modes across 5 benchmark slices (`m0` to `m4`).

## Modes
Fixed discovery modes ensure comparability.
- `baseline_flat`: Flat search, basic scoring.
- `folds_plus_ledger`: Repeated walkforward with ledger.
- `hierarchical_v1`: Hierarchical search.
- `hierarchical_plus_diversified`: Hierarchical search with diversification selection.

## Metrics
- **Efficiency**: `candidate_count_generated`, `wall_clock_seconds`
- **Quality**: `top_n_median_after_cost_expectancy_bps`, `top_n_median_fold_sign_consistency`
- **Distinctness**: `shortlist_avg_similarity`, `shortlist_distinct_lineage_count`

## Thresholds
Explicit thresholds define PASS/WARN/FAIL states for benchmark slices.
See `project/configs/benchmarks/discovery/thresholds_v1.yaml`.

## Review Flow
1. Run Matrix: `make benchmark-core`
2. Review Results: `make benchmark-review`
3. Certify: `make benchmark-certify`
