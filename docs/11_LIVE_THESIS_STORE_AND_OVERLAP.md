# Live thesis store and overlap

This document explains the runtime-facing packaged thesis model.

## Why the thesis store matters

The live/runtime layer should not reason from raw run notes, loose candidate rows, or human summaries.

It should reason from packaged thesis objects with explicit clauses and governance metadata.

That is why `data/live/theses/` exists.

## Canonical thesis-store paths

Primary paths:

- `data/live/theses/index.json`
- `data/live/theses/<batch>/promoted_theses.json`

In this snapshot, the store already contains a packaged batch and the index points to it.

## What a packaged thesis contains

A packaged thesis object typically carries:

- thesis id
- primary event id and event family
- canonical regime
- trigger clause
- confirmation clause
- context clause
- invalidation clause
- governance fields
- evidence summary
- promotion class
- deployment state
- overlap group id
- source lineage
- symbol scope and timeframe

This is the runtime contract. It is much richer than a simple research candidate row.

## Runtime ownership

Primary live/runtime modules include:

- `project/live/thesis_store.py`
- `project/live/retriever.py`
- `project/live/context_builder.py`
- `project/live/decision.py`
- `project/live/policy.py`
- `project/live/execution_attribution.py`
- `project/portfolio/thesis_overlap.py`
- `project/portfolio/risk_budget.py`

These modules assume packaged thesis objects exist and are structurally valid.

## Overlap graph

The overlap graph describes when packaged theses should not be treated as independent bets.

Current generated surfaces:

- `docs/generated/thesis_overlap_graph.json`
- `docs/generated/thesis_overlap_graph.md`

Overlap can be driven by shared structure such as:

- event families
- episode requirements
- canonical regime dependencies
- confirmation structure
- invalidation structure
- mechanism similarity

The point is not just reporting. The overlap graph informs downstream allocation and throttling logic.

## Promotion class and deployment state in runtime

Runtime should read both fields explicitly.

Examples:

- `seed_promoted` + `monitor_only` means the thesis is packaged but still restricted
- `paper_promoted` + `paper_only` means stronger evidence, still not live execution permission by itself
- `production_promoted` + a live-enabled state is the highest-confidence path

Any runtime shortcut that collapses these into one maturity flag is conceptually wrong.

## What to inspect after packaging changes

Use this order:

1. `data/live/theses/index.json`
2. `data/live/theses/<batch>/promoted_theses.json`
3. `docs/generated/seed_thesis_catalog.md`
4. `docs/generated/seed_thesis_packaging_summary.md`
5. `docs/generated/thesis_overlap_graph.md`
6. any shadow-live summaries under `docs/generated/` or `data/reports/shadow_live/`

## Current snapshot implication

Because the thesis store and overlap graph are already present, runtime docs should be written from the standpoint of an active packaged-thesis system.

The runtime layer is not waiting for a future packaging design. It already consumes a real packaged-thesis contract.
