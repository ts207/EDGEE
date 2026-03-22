# Synthetic Datasets

Synthetic datasets are controlled research worlds, not substitutes for live-market evidence. Use them to validate mechanisms, contracts, and detector behavior under known conditions.

---

## What Synthetic Data Is For

Use synthetic data to validate:
- Detector truth recovery under planted event conditions
- Artifact and contract plumbing
- Search and promotion pipeline behavior under controlled regimes
- Negative controls
- Robustness across different synthetic worlds

**Do not** use synthetic output as standalone proof of live profitability.

---

## Maintained Profiles

| Profile | Characteristics | Best used for |
|---|---|---|
| `default` | Balanced baseline, recurring event regimes | General discovery checks |
| `2021_bull` | Stronger drift, faster cycle cadence, more crowding-like behavior | Trend and crowding-sensitive templates |
| `range_chop` | Lower drift, tighter amplitudes, more resets | False-breakout and mean-reversion stress |
| `stress_crash` | Wider spreads, higher noise, stronger stress episodes | Liquidity, deleveraging, spread-sensitive logic |
| `alt_rotation` | Stronger cross-sectional rotation behavior | Multi-symbol rotation behavior |

---

## What Gets Written

Each generated run writes:

```
synthetic/<run_id>/synthetic_generation_manifest.json
synthetic/<run_id>/synthetic_regime_segments.json
data/lake/runs/<run_id>/...   (run-scoped lake partitions)
```

Synthetic cleaned bars include a minimal microstructure contract:
- `spread_bps`
- `depth_usd`
- `bid_depth_usd`
- `ask_depth_usd`
- `imbalance`

---

## Main Workflows

### Broad Maintained Workflow

For detector truth and broad synthetic discovery:

```bash
python3 -m project.scripts.run_golden_synthetic_discovery
```

### Fast Certification Workflow

For narrow detector-and-plumbing certification:

```bash
python3 -m project.scripts.run_fast_synthetic_certification
```

This path is intentionally narrow in symbols, date range, event fanout, templates, and search budget. Interpret it as: detector truth and artifacts can pass, but discovery and promotion may produce zero viable candidates because holdout support is too small.

---

## Truth Validation

After any synthetic run, validate detector truth before interpreting results:

```bash
python3 -m project.scripts.validate_synthetic_detector_truth \
  --run_id golden_synthetic_discovery
```

**Important distinction:**
- `expected_event_types` — hard pass/fail truth contract. Enforces both an off-regime ceiling and a minimum in-regime precision threshold.
- `supporting_event_types` — informational supporting signals, not pass/fail.

Include supporting-signal reporting without changing pass/fail:

```bash
python3 -m project.scripts.validate_synthetic_detector_truth \
  --run_id my_run \
  --include_supporting_events 1
```

Override the precision floor:

```bash
python3 -m project.scripts.validate_synthetic_detector_truth \
  --run_id my_run \
  --min_precision_fraction 0.5
```

---

## Known Synthetic Limitations

`ABSORPTION_PROXY` and `DEPTH_STRESS_PROXY` are currently:
- Measurable on synthetic data.
- Supporting-only in synthetic reporting.
- Treated as live-data diagnostics by default.

They are not reliable hard synthetic truth targets under the current `liquidity_stress` generator family. The default synthetic detector audit skips them. Opt in explicitly when you want informational measurement.

---

## Recommended Workflow

1. Choose the profile that matches the question (see table above).
2. Freeze the profile and date slice before reviewing outcomes.
3. Run the narrowest path that answers the question.
4. Validate truth before interpreting misses.
5. Compare against at least one additional profile before strengthening belief.

---

## Guardrails

- Keep truth validation artifacts with the run.
- Separate detector recovery claims from profitability claims.
- Prefer cross-profile survival over single-profile peak performance.
- Do not redesign a detector against one synthetic world.
- Rerun truth validation after any detector or generator changes.
- Treat short certification windows as calibration unless real holdout support exists.
