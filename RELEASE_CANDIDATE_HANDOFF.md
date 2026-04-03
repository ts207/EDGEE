# EDGE Runtime Rewrite RC1

## What changed

This release candidate consolidates the Phase 1–7 rewrite into one repo state:

- runtime retrieval is thesis-clause-first
- template kinds are enforced operationally
- generated artifact summaries are hermetic and workspace-local
- state truth converges from `spec/states/*.yaml`
- `spec/domain/domain_graph.yaml` is a slimmer runtime read model
- default search is Tier 1 (`event × expression template`) with BTC/ETH, 12/24/48, lag 1
- visible operator path is `discover / package / validate / review`

## Compatibility intentionally preserved

- `event_family` remains compatibility metadata in live thesis contracts and overlap surfaces
- legacy `scripts.baseline.*` imports are preserved via a top-level compatibility shim
- graph/runtime loaders remain tolerant of older graph payloads where useful during the transition

## Final integrated fixes applied during RC sweep

- restored legacy `scripts.baseline._common` import surface
- repaired promoted-thesis export so unlinked runtime contracts recover governance from authored thesis definitions when appropriate
- prevented explicit multi-clause metadata exports from being overwritten by generic authored-thesis fallback matching
- restored compiled event governance fields into contract sidecars
- fixed event config composition to seed family/runtime compatibility from compiled event parameters before overlaying slim graph rows
- adjusted instrument-class validation so empty registry instrument-class lists are treated as unspecified rather than hard-blocking
- raised `max_events_per_run` in search limits to accommodate the bounded regime-shakeout matrix

## Validation performed

Directly verified in the RC workspace:

- `project/tests/contracts` ✅
- `project/tests/domain` ✅
- `project/tests/scripts` ✅
- `project/tests/live` ✅
- targeted research/operator regression set ✅
  - `project/tests/research/test_live_export.py`
  - `project/tests/research/test_live_export_governance.py`
  - `project/tests/research/agent_io/test_issue_proposal.py`
  - `project/tests/core/test_operator_preflight.py`
  - `project/tests/research/test_search_profile.py`
  - `project/tests/research/test_phase2_search_engine_scope.py`
  - `project/tests/research/test_search_space_contract.py`
- `make help` operator surface smoke ✅

## Canonical operator path

- `make discover`
- `make package`
- `make validate`
- `make review`

## Deferred debt

- remove compatibility shims after downstream consumers stop importing legacy paths
- tighten CI around the integrated acceptance matrix
- prune stale generated artifacts and legacy docs once the RC is accepted
