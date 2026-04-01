# Live Thesis Store And Overlap

This document explains the canonical packaged thesis surfaces that downstream live and allocation systems consume.

## Canonical thesis store

The canonical packaged thesis store lives under:

- `data/live/theses/index.json`
- `data/live/theses/<batch>/promoted_theses.json`

The index points at one or more packaged batches. Each batch contains thesis objects with:

- thesis id
- promotion class
- deployment state
- source event and episode contracts
- trigger requirements
- confirmation requirements
- invalidation requirements
- allowed/disallowed regimes
- overlap group id
- evidence gaps and lineage

## What the live layer should consume

The live layer should consume packaged thesis objects, not raw event rows or hand-authored notes.

That means:

- `project/live/retriever.py` loads from the thesis store
- `project/live/decision.py` reasons about thesis clauses, contradictions, and invalidators
- `project/live/context_builder.py` and the event detector provide context to thesis matching
- `project/live/execution_attribution.py` records thesis and overlap metadata on fills

## Promotion class and deployment state

Promotion class answers **how much support exists**.

Deployment state answers **where the thesis may be used right now**.

Typical combinations:

- `seed_promoted` + `monitor_only`
- `paper_promoted` + `paper_only`
- `production_promoted` + a narrower live-eligible deployment state

Do not collapse these two fields into one informal maturity label.

## Overlap graph

The overlap graph lives under:

- `docs/generated/thesis_overlap_graph.json`
- `docs/generated/thesis_overlap_graph.md`

It is built from packaged theses rather than from raw queue entries.

An overlap edge exists when packaged theses share enough structure that the allocator should not treat them as independent. Current overlap signals include:

- shared event families
- shared episode contracts
- shared regime dependencies
- shared invalidation structure
- shared mechanism class

## What a useful overlap graph looks like

A useful overlap graph has:

- real nodes from the packaged thesis store
- overlap groups that explain allocator throttling
- edges only when the structural similarity is meaningful

A graph with nodes but zero edges is not wrong. It simply means the current packaged thesis set is disconnected.

## Typical maintenance loop

After adding or refreshing packaged theses:

1. regenerate packaging artifacts
2. regenerate overlap artifacts
3. inspect `seed_thesis_catalog.md`
4. inspect `thesis_overlap_graph.md`
5. verify that the allocator and live retriever still load the packaged store correctly
