# Thesis Bootstrap And Promotion

This document explains the founding-thesis workflow that sits between bounded research runs and the canonical thesis store.

## Why this lane exists

A strong event system and a strong phase-2 pipeline are not enough by themselves. The live retriever, overlap graph, and allocator consume **packaged theses**, not raw event rows or raw run summaries.

The bootstrap lane exists to answer:

- which candidate theses deserve deeper testing
- which ones have enough empirical support to package
- which packaged theses are only `seed_promoted`
- which packaged theses clear the stronger `paper_promoted` bar

## Canonical lifecycle

Use this lifecycle exactly:

1. `candidate`
2. `tested`
3. `seed_promoted`
4. `paper_promoted`
5. `production_promoted`

A thesis must never skip directly from candidate to production.

## Bootstrap blocks

### Block A — seed inventory

Creates the bounded founding queue.

Outputs:

- `docs/generated/thesis_bootstrap_baseline.md`
- `docs/generated/promotion_seed_inventory.csv`
- `docs/generated/seed_promotion_policy.md`

### Block B — thesis testing

Scores queue entries on governance, contract fit, invalidation clarity, and readiness.

Outputs:

- `docs/generated/thesis_testing_scorecards.csv`
- `docs/generated/thesis_testing_summary.md`

### Block C — empirical mapping

Maps real evidence bundles onto the queue and decides whether a thesis still needs evidence, needs repair, or clears a higher stage.

Outputs:

- `docs/generated/thesis_empirical_scorecards.csv`
- `docs/generated/thesis_empirical_summary.md`

### Block D — founding evidence generation

Generates canonical evidence bundles for selected theses.

Outputs:

- `data/reports/promotions/<THESIS_ID>/evidence_bundles.jsonl`
- `docs/generated/founding_thesis_evidence_summary.md`

### Block E — packaging

Writes the canonical thesis store and human-readable cards.

Outputs:

- `data/live/theses/index.json`
- `data/live/theses/<batch>/promoted_theses.json`
- `docs/generated/seed_thesis_cards/*.md`
- `docs/generated/seed_thesis_catalog.md`
- `docs/generated/seed_thesis_packaging_summary.md`

### Block F — structural confirmation

Allows conservative bridge theses derived from supported component evidence. These are intentionally capped at `seed_promoted` until direct paired evidence exists.

Outputs:

- `docs/generated/structural_confirmation_summary.md`
- updated packaged thesis store and overlap graph

## Commands

Use these maintained entry points:

```bash
python -m project.scripts.build_seed_bootstrap_artifacts
python -m project.scripts.build_seed_testing_artifacts
python -m project.scripts.build_seed_empirical_artifacts
python -m project.scripts.build_founding_thesis_evidence
python -m project.scripts.build_seed_packaging_artifacts
python -m project.scripts.build_structural_confirmation_artifacts
python -m project.scripts.build_thesis_overlap_artifacts
./project/scripts/regenerate_artifacts.sh
```

## Current policy rules

- `seed_promoted` is enough for monitor-only retrieval and overlap graph generation.
- `paper_promoted` is enough for paper-style retrieval and review.
- `production_promoted` remains a separate later-phase decision.
- Derived structural confirmation support must not be upgraded to `paper_promoted` without direct paired-event evidence.

## What to inspect first

If you need to understand the current bootstrap state, read in this order:

1. `docs/generated/promotion_seed_inventory.md`
2. `docs/generated/thesis_testing_summary.md`
3. `docs/generated/thesis_empirical_summary.md`
4. `docs/generated/founding_thesis_evidence_summary.md`
5. `docs/generated/seed_thesis_catalog.md`
6. `docs/generated/thesis_overlap_graph.md`
