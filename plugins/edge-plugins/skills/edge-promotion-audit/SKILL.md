---
name: edge-promotion-audit
description: Use when reviewing Edge promotion artifacts, candidate diagnostics, or baseline-vs-candidate run comparisons.
---

# Edge Promotion Audit

## Purpose

Use this skill when the task is about:

- phase-2 candidates
- promotion diagnostics
- promotion bundles
- directly comparable run-to-run changes

## Canonical Artifact Order

Review in this order:

1. `data/runs/<run_id>/run_manifest.json`
2. `data/reports/phase2/<run_id>/phase2_diagnostics.json`
3. `data/reports/phase2/<run_id>/phase2_candidates.parquet`
4. `data/reports/promotions/<run_id>/promotion_diagnostics.json`
5. related promotion evidence tables or bundles

Do not jump straight to headline metrics.

## Comparison Rule

Only compare runs when they are directly comparable:

- same regime
- same mechanism family
- same tradable expression
- one intentional change

Use:

```bash
plugins/edge-plugins/scripts/edge_compare_runs.sh <baseline_run_id> <candidate_run_id>
```

## Decision Rule

End with exactly one:

- `keep`
- `modify`
- `kill`

The next step must stay bounded.
