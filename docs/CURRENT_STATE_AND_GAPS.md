# Current State and Documentation Gaps

This document is the bridge between the codebase as it exists now and the role-specific docs.

## What the project already contains

The codebase already includes the following major surfaces:

- Research orchestration: `project/pipelines/research/campaign_controller.py`
- Memory update and reflection handling: `project/pipelines/research/update_campaign_memory.py`
- Frontier and search intelligence: `project/pipelines/research/search_intelligence.py`
- Feature MI scan: `project/pipelines/research/feature_mi_scan.py`
- Hypothesis evaluation, regime analysis, and promotion gating: `project/research/promotion/`
- Hypothesis clustering and PnL similarity: `project/research/clustering/`
- Candidate discovery, reporting, and promotion services: `project/research/services/`
- Strategy blueprint compilation: `project/pipelines/research/compile_strategy_blueprints.py`
- Live execution, drift, kill switch, and OMS state: `project/live/`
- Allocation and sizing: `project/portfolio/`
- Pipeline and artifact contracts: `project/contracts/`
- Ontology, knowledge, and reflection schemas: `project/research/knowledge/`
- Search-space and registry loading: `project/spec_registry/` and `spec/`
- Proposal and agent I/O: `project/research/agent_io/`
- Candidate shaping and recommendation helpers: `project/research/recommendations/` and `project/research/analyzers/`
- Event quality scoring helpers: `project/research/event_quality/`
- Runtime replay and validation pipelines: `project/pipelines/runtime/`
- Alpha bundle and feature assembly pipelines: `project/pipelines/alpha_bundle/`

## What the older docs understate

Several older docs describe the platform as if it were only a narrow event scanner. That is no longer accurate.

The underdocumented but present capabilities are:

1. Memory-aware campaign control
   - The controller reads prior reflections, belief state, and next-action queues.
   - The controller can operate in exploit, explore, or scan mode.

2. Discovery surface expansion
   - The code already contains support for MI-driven candidate predicates.
   - The code also contains clustering utilities for deduplicating correlated hypotheses.
   - Search intelligence and frontier ordering are separate from evaluation.

3. Promotion and compilation
   - Promotion logic includes explicit not-evaluated states for OOS.
   - Blueprint compilation can produce `AllocationSpec` outputs.
   - Portfolio-aware sizing exists as a first-class concern.
   - Promotion scoring is separate from promotion reporting and decision support.

4. Live handoff
   - Live state, drift, and kill-switch support are present.
   - OMS and runner surfaces exist alongside health checks.
   - The docs should describe the research-to-live boundary, not only the research loop.

## Redundancy and logical issues in the older docs

- The same research loop is described in multiple files with slightly different stage names.
- The controller is described as static in some places and adaptive in others.
- Some docs mention generated paths that are not actually present in this repository snapshot.
- The vision roadmap is useful, but it should be labeled as a roadmap archive, not as the current operating manual.

## What this doc is for

Use this file when deciding whether a doc should describe:

- current code behavior,
- a maintained contract,
- a roadmap item, or
- an archived vision note.

If a role doc conflicts with this file, the role doc should be updated to match the code, not the other way around.
