---
name: edge-repo
description: Use when working inside the Edge repository on event detectors, specs, research pipelines, or verification tasks.
---

# Edge Repo

## Purpose

Use this skill when the task is specific to the `Edge` codebase and benefits from repo conventions instead of generic coding guidance.

## Repo Model

Edge is an event-driven alpha research platform for crypto markets.

Primary surfaces:

- `spec/` for YAML domain specs and event definitions
- `project/events/` for detector and family implementations
- `project/pipelines/` for stage orchestration
- `project/contracts/` for artifact and stage contracts
- `project/research/` for discovery, promotion, and diagnostics
- `project/tests/` for regression, contract, and architecture coverage

## Working Rules

- Treat specs as the source of truth when detector thresholds or family behavior should be configurable.
- When changing detector behavior, inspect both the event spec and the family or detector implementation before editing.
- Prefer targeted pytest runs around the touched surface before broader sweeps.
- Do not claim repo-wide green unless the full sweep actually completed.

## Useful Checks

- Hardcoded threshold audit:
  `pytest -q tests/param_integrity/test_no_hardcoded_constants.py -q`
- Focused detector regressions:
  `pytest -q project/tests/events/test_detector_hardening.py -q`
- Project hardening smoke:
  `pytest -q project/tests/test_event_hardening_verification.py -q`

## High-Value References

- `README.md`
- `docs/AGENT_CONTRACT.md`
- `docs/08_TESTING_AND_MAINTENANCE.md`
- `project/contracts/pipeline_registry.py`
- `project/events/families/`
- `project/events/detectors/`
