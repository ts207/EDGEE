---
name: edge-detector-spec
description: Use when changing Edge detector logic, family implementations, or spec-backed event thresholds.
---

# Edge Detector Spec

## Purpose

Use this skill for work on:

- `project/events/detectors/`
- `project/events/families/`
- `spec/events/`

## Working Rules

- Treat event specs as the source of truth for configurable thresholds and windows.
- If a detector appears configurable, verify the spec keys are actually consumed by code.
- Preserve PIT-safe rolling behavior when changing thresholds or windows.
- Do not add new detectors, events, regimes, or ontology structures without explicit approval.

## Required Review Sequence

1. Read the owning event spec in `spec/events/`.
2. Read the detector or family implementation that consumes it.
3. Check nearby tests in `project/tests/events/` and any targeted synthetic or audit tests.
4. Change the code and spec together if config semantics are intended.

## Minimum Verification

Run the targeted block first:

```bash
plugins/edge-plugins/scripts/edge_checks.sh
```

Then add any focused tests that prove the specific spec key is live.
