# Benchmark Guide

This document covers the maintained benchmark posture, how to run the maintenance cycle, how to read certification output, and how benchmark status gates promotion.

For triage when certification fails, see [BENCHMARK_TRIAGE.md](./BENCHMARK_TRIAGE.md) (if present) or the triage section of this doc.

---

## Quick Terminal Review

Get a summary of the latest certified maintenance cycle:

```bash
PYTHONPATH=. python3 project/scripts/show_benchmark_review.py
```

If no artifacts exist locally, you need to run the maintenance cycle first.

---

## Running the Maintenance Cycle

The unified command rebuilds the benchmark matrix and certifies results in one step:

```bash
# Via script
PYTHONPATH=. python3 project/scripts/run_benchmark_maintenance_cycle.py

# Via Makefile (recommended)
make benchmark-maintenance
```

This command:
- Re-runs all maintained benchmark slices.
- Certifies results against absolute thresholds and the prior baseline.
- Generates a `promotion_readiness.json` report.
- Updates the `latest` pointer in `data/reports/benchmarks/`.

---

## When to Run the Maintenance Cycle

Run it:
- Monthly, on the first day of the month after new live data is ingested.
- After modifying core event detectors or feature schemas.
- Before starting a new research program.

---

## Reading Certification Output

After the cycle completes, check certification status:

```bash
PYTHONPATH=. python3 project/scripts/show_benchmark_review.py \
  --path data/reports/benchmarks/latest/benchmark_review.json
```

- **PASS** — proceed to confirmatory checks.
- **FAIL** — follow the triage path below. Do not promote candidates from failed families.

Check promotion readiness:

```bash
PYTHONPATH=. python3 project/scripts/show_promotion_readiness.py \
  --review data/reports/benchmarks/latest/benchmark_review.json \
  --cert data/reports/benchmarks/latest/benchmark_certification.json
```

---

## Current Maintained Benchmark Slices

### Status Definitions

| Status | Meaning |
|---|---|
| `authoritative` | Maintained slice with a real artifact surface worth using for operator decisions. |
| `informative` | Non-empty and useful, but does not currently produce a stronger decision boundary than the authoritative slice. |
| `quality_boundary` | Confidence-aware context changes the benchmark decision outcome even if the winning hypothesis ID does not change. |
| `foundation_only` | Use for live-data readiness and contract checks only. Not a maintained comparison benchmark. |
| `coverage_limited` | Do not treat as a maintained comparison benchmark yet. |

### Current Maintained Slices

| Event | Run ID | Status | Use |
|---|---|---|---|
| `VOL_SHOCK` | `bench_vol_shock_btc_2024q1` | `informative` | Live BTC 2024Q1 context-comparison slice |
| `ZSCORE_STRETCH` | `bench_zscore_stretch_btc_2025jan` | `informative` | Live statistical-dislocation comparison slice |
| `LIQUIDITY_GAP_PRINT` | *(see BENCHMARK_STATUS.md)* | `informative` | Live liquidity-dislocation comparison slice |
| `OI_SPIKE_POSITIVE` | *(see BENCHMARK_STATUS.md)* | `informative` | Live positioning-extremes comparison slice |
| `SPREAD_BLOWOUT` | *(see BENCHMARK_STATUS.md)* | `informative` | Live execution-friction comparison slice |
| `FALSE_BREAKOUT` | *(see BENCHMARK_STATUS.md)* | `quality_boundary` | Use when testing confidence-aware context demotion |
| `BASIS_DISLOC` (synthetic) | *(see BENCHMARK_STATUS.md)* | `informative` | Synthetic statistical-dislocation authority |

> **Note:** `FND_DISLOC` live slice has been superseded by the `ZSCORE_STRETCH` live slice. Do not use `FND_DISLOC` as a current maintained benchmark.

---

## Promotion Gating by Benchmark Health

| Benchmark health | Promotion status |
|---|---|
| Certified | Candidates can be promoted if they pass all standard statistical and economic gates. |
| Degraded | Promotion is blocked for that family. Resolve benchmark issues first. |

---

## Drift Analysis

The certification report includes a historical drift table (last 5 baselines).

| Deviation type | Interpretation |
|---|---|
| Small deviations | Normal variance in sampling or data cleaning. |
| Large deviations (>20%) | Systemic change in event frequency or data quality. Investigate. |
| Steady decline | Potential data decay or detector desensitization. |

---

## Artifact Locations

| Artifact | Path |
|---|---|
| Latest benchmark review | `data/reports/benchmarks/latest/benchmark_review.json` |
| Latest certification | `data/reports/benchmarks/latest/benchmark_certification.json` |
| Promotion readiness | `data/reports/benchmarks/latest/promotion_readiness.json` |
| History (last 5 certified) | `data/reports/benchmarks/history/` |

Uncertified runs and dry-runs are automatically pruned when they become older than the oldest retained certified baseline.

---

## Failure Escalation

| Transition | Impact | Action |
|---|---|---|
| `informative → coverage_limited` | Promotion blocked for this family | File defect, fix in next sprint. |
| `coverage_limited → foundation_only` (with blocked readiness) | Severe platform regression | Halt all research for this family. Revert recent changes or escalate to architecture review. |
| `hard_evaluated_rows → 0` | Detector broken or search space missing events | Urgent fix. Debug `phase2` search engine output for the affected benchmark run. |

---

## Confirmatory Rerun Contract

For high-trust families, confirmatory reruns must satisfy:
- `decision_lag_bars: 1`
- `calibration_mode: train_fit`

See `spec/benchmarks/confirmatory_rerun_contract_*.yaml` for per-family specs.

---

## Acceptance Thresholds

Per-slice acceptance floors are codified in:

```
spec/benchmarks/benchmark_acceptance_thresholds.yaml
```
