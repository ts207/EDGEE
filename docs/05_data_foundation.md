# Data Foundation

This document explains the current data roots, artifact paths, and lineage expectations in the Edge repo.

The old docs were too vague here. The repo now has a real distinction between:

- market data and derived features
- research-stage artifacts
- run-scoped manifests and checklists
- exported runtime thesis inventory

## Data Roots

### `data/lake/`

Primary storage for market data and derived research inputs.

Common subtrees:

- `data/lake/raw/`
- `data/lake/cleaned/`
- `data/lake/features/`
- `data/lake/runs/`

### `data/reports/`

Canonical location for stage outputs, diagnostics, and research reports.

Important subtrees include:

- `data/reports/phase2/`
- `data/reports/validation/`
- `data/reports/promotions/`
- `data/reports/operator/`
- `data/reports/context_quality/`
- `data/reports/data_quality/`

### `data/runs/`

Run-scoped manifests and related operational artifacts.

Common contents include:

- `run_manifest.json`
- runtime output directories
- research checklist and release signoff artifacts

### `data/live/theses/`

Runtime-facing thesis inventory written by `promote export`.

This is the critical runtime boundary older docs did not explain well.

## Canonical Artifact Paths

The repo exposes path helpers from `project/artifacts/catalog.py`. Those helpers define the paths operators should trust.

| Purpose | Canonical path |
|---------|----------------|
| Run root | `data/runs/<run_id>/` |
| Run manifest | `data/runs/<run_id>/run_manifest.json` |
| Discovery candidates | `data/reports/phase2/<run_id>/phase2_candidates.parquet` |
| Discovery diagnostics | `data/reports/phase2/<run_id>/phase2_diagnostics.json` |
| Validation bundle | `data/reports/validation/<run_id>/validation_bundle.json` |
| Promotion root | `data/reports/promotions/<run_id>/` |
| Promotion summary | `data/reports/promotions/<run_id>/promotion_summary.json` |
| Runtime thesis root | `data/live/theses/` |
| Exported thesis batch | `data/live/theses/<run_id>/promoted_theses.json` |
| Thesis index | `data/live/theses/index.json` |

Some helper functions also resolve legacy fallback locations for older runs. That compatibility behavior exists so inspection commands keep working, but new docs should teach the canonical paths above.

## Stage Lineage

The artifact chain is:

1. proposal YAML in `spec/proposals/`
2. discovery outputs in `data/reports/phase2/<run_id>/`
3. validation outputs in `data/reports/validation/<run_id>/`
4. promotion outputs in `data/reports/promotions/<run_id>/`
5. exported thesis inventory in `data/live/theses/<run_id>/`

This separation matters because:

- validation should not guess from raw discovery tables
- deploy should not read promotion tables directly
- runtime inventory should remain inspectable even when research directories are large or noisy

## Source Data Families

The main source data families in the repo are:

- OHLCV
- funding
- open interest
- mark/index price where supported
- derived cleaned bars
- derived feature tables
- market context and microstructure summaries

Venue support in the repo currently centers on:

- Bybit derivatives as the primary path
- Binance support through explicit venue selection in legacy or support flows

## Reproducibility

A run is reproducible only if three things stay aligned:

- the proposal or campaign contract
- the relevant registry state
- the data root contents used at execution time

Persisted artifacts exist so later stages can be rerun without recomputing the entire world, but reproducibility still depends on explicit lineage rather than vague "same code, same result" assumptions.

## Operational Guidance

- Use artifact helper paths when writing tooling.
- Prefer stage commands that list or resolve artifacts rather than hard-coding legacy directories.
- Treat `data/live/theses/` as the only runtime thesis inventory source.
- Do not document `data/reports/promoted_theses/` as canonical; the current runtime path is `data/live/theses/`.
