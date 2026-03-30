# Hidden Failure Audit

Date: `2026-03-30`

## Scope

This audit focused on hidden or silent failure modes in three classes:

- spec/runtime contract drift
- artifact read failures that degrade to empty outputs
- pipeline paths that silently downgrade work instead of surfacing the causal error

## Fixed In This Pass

### 1. Event config drift between source specs and composed runtime config

- Root issue: `project/events/config.py` composed runtime parameters from the unified registry row but did not re-overlay the source event spec file, and it did not surface detector class defaults.
- Impact: source spec parameters could disappear from runtime config, and several detectors operated with hidden thresholds not visible in the composed contract.
- Repair:
  - source spec parameters are now overlaid back onto the composed row,
  - detector `defaults` are now surfaced into effective runtime parameters before spec/runtime overrides.
- Verification result: the repo-wide spec/config audit for `spec/events/*.yaml` now reports `issue_count 0`.

### 2. Silent phase-1 event read failures

- Root issue: `project/events/event_repository.py` swallowed read exceptions and silently continued to the next candidate path.
- Impact: corrupted or unreadable event artifacts could be interpreted as "no events found".
- Repair: phase-1 event read failures now emit warnings with the failing path.

### 3. Silent phase-2 artifact read failures

- Root issue: `project/research/phase2.py::_read_csv_or_parquet()` returned an empty frame on read failure without any trace, and the warning path referenced the wrong logger symbol.
- Impact: broken intermediate artifacts could collapse into empty downstream inputs while looking like ordinary sparsity.
- Repair:
  - read failures now log a warning with the failing path,
  - the error path now uses the correct module logger.

### 4. Split engine failures hidden as non-promotable train-only output

- Root issue: `project/research/phase2.py::assign_event_split_labels()` caught all split-assignment failures in research mode and silently relabeled everything as `train` plus `non_promotable=True`.
- Impact: a split-engine bug could look like normal "non-promotable" research output rather than an actual mechanical failure.
- Repair: the fail-closed behavior remains, but it now logs the exception path explicitly.

### 5. Detector preflight failures hidden during basis-feature inference

- Root issue: `project/research/analyze_events.py::_load_detector_input()` swallowed exceptions from detector preflight introspection when deciding whether basis features were required.
- Impact: a broken detector preflight could silently fall back to the wrong feature loader.
- Repair: the path now logs a warning instead of failing invisibly.

## Remaining High-Risk Issues

### 1. Campaign memory corruption still degrades to empty memory

- File: `project/research/campaign_controller.py`
- Path: `_read_memory()`
- Current behavior:
  - JSON parse failure returns `{}`,
  - Parquet read failure returns `pd.DataFrame()`,
  - superseded-stage read failure returns an empty set after warning.
- Why this still matters: a corrupted memory artifact can effectively reset belief state, next actions, or reflections without halting the campaign.

### 2. Research split preparation still treats some mechanical faults as empty output

- File: `project/research/phase2.py`
- Paths:
  - `prepare_events_dataframe()` fail-closed resplit branch
  - `_read_csv_or_parquet()` empty-frame fallback
- Current behavior: better surfaced than before, but still operationally resolves to empty/non-promotable outputs instead of escalating to a mechanical failure state.
- Why this still matters: the repo can still classify infrastructure faults as data scarcity if the operator only watches end artifacts.

### 3. Live runtime loops are resilient, but some failures only log and continue

- Files:
  - `project/live/runner.py`
  - `project/live/oms.py`
- Current behavior: kline/ticker/account-sync/data-health loops generally log exceptions and continue; OMS signature introspection failures are ignored.
- Why this still matters: this is appropriate for some runtime resilience cases, but it means intermittent live-state corruption can persist without a structured degraded-mode marker.

## Verification

Passed:

- `project/tests/events/test_registry_loader.py`
- `project/tests/events/test_event_repository.py`
- `project/tests/pipelines/research/test_phase2_services_orchestration.py`
- `project/tests/pipelines/research/test_analyze_events.py`
- `python -m compileall project/events/config.py project/events/event_repository.py project/research/phase2.py project/research/analyze_events.py`

## Next Step

The next justified repo repair is to decide whether campaign-memory corruption should remain warning-only. If not, the controller should move from "empty fallback" to an explicit memory-integrity failure contract.
