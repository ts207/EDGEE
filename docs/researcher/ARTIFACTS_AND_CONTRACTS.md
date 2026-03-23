# Artifacts and Contracts

## Artifact layers

### 1. Run layer - `data/runs/<run_id>/`

Primary execution outputs, plans, and run-scoped material.

### 2. Research report layer - `data/reports/`

Human-readable summaries, discovery outputs, calibration outputs, and derived tables.

### 3. Event layer - `data/events/<run_id>/`

Event-level outputs and event-specific diagnostics.

### 4. Lake layer - `data/lake/runs/<run_id>/`

Longer-lived, normalized storage for run lineage and reproducibility.

## Trust order

1. The artifact itself
2. Its manifest or schema
3. The producing code
4. The maintained docs

A prose claim is not stronger than the artifact it describes.

## Core contract expectations

- Every run should be traceable by `run_id`.
- Every promoted or rejected result should be attributable to its evaluation inputs.
- Every memory update should preserve enough metadata to explain later blocking decisions.
- Every promotion decision should record whether OOS was actually evaluated.

## Failure classes

The docs should distinguish:

- mechanical failures,
- insufficient sample,
- market failures,
- cost failures,
- overfitting signals,
- and not-evaluated states.

Do not collapse these into one generic failure bucket.

## Missing contract surfaces in older docs

The older docs underdescribe:

- campaign memory schema details,
- search frontier ordering,
- promotion not-evaluated states,
- portfolio state handoff,
- and cluster deduplication before multiplicity correction.

## Practical reading rule

When the docs and artifact disagree, trust the artifact and then fix the docs.
