# Synthetic Datasets

## Purpose

Synthetic datasets are for controlled research, not direct evidence of live profitability.

Use them to validate:

- detector truth recovery
- artifact and contract plumbing
- search and promotion behavior under controlled regimes
- falsification on negative controls
- robustness across different synthetic worlds

Do not use them as standalone proof of market edge.

## Built-In Profiles

The generator supports these maintained profiles:

- `default`: balanced baseline with recurring event regimes
- `2021_bull`: stronger drift, faster cycle cadence, more crowding-like behavior
- `range_chop`: lower drift, tighter amplitudes, more resets
- `stress_crash`: wider spreads, higher noise, stronger stress episodes
- `alt_rotation`: stronger cross-sectional and alt-style rotation behavior

## Outputs

Each generated run writes:

- `synthetic/<run_id>/synthetic_generation_manifest.json`
- `synthetic/<run_id>/synthetic_regime_segments.json`
- run-scoped partitions under `data/lake/runs/<run_id>/...`

Synthetic cleaned bars include a minimal microstructure contract:

- `spread_bps`
- `depth_usd`
- `bid_depth_usd`
- `ask_depth_usd`
- `imbalance`

The normal feature and audit paths derive `spread_zscore` from `spread_bps`, so synthetic spread-sensitive
proxies can run through the ordinary pipeline path.

## Generate Data

Generate one dataset:

```bash
python3 -m project.scripts.generate_synthetic_crypto_regimes \
  --run_id synthetic_range_chop \
  --start_date 2026-03-01 \
  --end_date 2026-05-31 \
  --symbols BTCUSDT,ETHUSDT,SOLUSDT \
  --volatility_profile range_chop \
  --noise_scale 0.9
```

Generate the curated suite:

```bash
python3 -m project.scripts.generate_synthetic_crypto_regimes \
  --suite_config project/configs/synthetic_dataset_suite.yaml \
  --run_id synthetic_suite
```

## Validation Modes

### Broad Maintained Workflow

Use the maintained broad workflow when the goal is detector truth and broad synthetic discovery behavior:

```bash
python3 -m project.scripts.run_golden_synthetic_discovery
```

### Fast Certification Workflow

Use the fast workflow when the goal is a narrow detector-and-plumbing check:

```bash
python3 -m project.scripts.run_fast_synthetic_certification
```

That path is intentionally narrow in:

- symbols
- date range
- event fanout
- templates
- search budget

Interpret it accordingly:

- detector truth can pass
- artifact and pipeline plumbing can pass
- discovery and promotion can still produce zero viable candidates because the slice is too small for holdout evidence

## Truth Validation

Validate a synthetic run with:

```bash
python3 -m project.scripts.validate_synthetic_detector_truth \
  --run_id golden_synthetic_discovery
```

Important distinction:

- `expected_event_types` are the hard pass/fail truth contract
- `supporting_event_types` are informational supporting signals

To include supporting-signal reporting without changing the main pass/fail result:

```bash
python3 -m project.scripts.validate_synthetic_detector_truth \
  --run_id my_run \
  --include_supporting_events 1
```

## Recommended Workflow

1. choose the profile that matches the question
2. freeze the profile and slice before reviewing outcomes
3. run the narrowest detector or discovery path that answers the question
4. validate truth before interpreting misses
5. compare against at least one additional profile before strengthening belief

## Selection Heuristics

Use:

- `default` for smoke and balanced discovery checks
- `2021_bull` for strong-trend and crowding-sensitive templates
- `range_chop` for false-breakout and mean-reversion stress
- `stress_crash` for liquidity, deleveraging, and spread-sensitive logic
- `alt_rotation` for multi-symbol rotation and cross-sectional behavior

## Current Limitations

`ABSORPTION_PROXY` and `DEPTH_STRESS_PROXY` are currently:

- measurable on synthetic data
- supporting-only in synthetic reporting
- treated as live-data diagnostics by default

They are not reliable hard synthetic truth targets under the current `liquidity_stress` generator family.

Because of that:

- the default synthetic detector audit skips them
- opt in explicitly with `python3 -m project.scripts.audit_detector_precision_recall --include_live_only_synthetic 1` if you want an informational measurement

## Guardrails

- keep truth validation artifacts with the run
- separate detector recovery claims from profitability claims
- prefer cross-profile survival over single-profile peak performance
- do not redesign directly against one synthetic world
- rerun truth validation after detector or generator changes
- treat short certification windows as calibration unless real holdout support exists
