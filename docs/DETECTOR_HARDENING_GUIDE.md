# Detector Hardening Guide

This note records the detector-contract hardening policy for the research platform.

It is not a detector catalog and not a synthetic audit ledger. It explains what a detector must do to be
considered safe, comparable, and research-usable.

## Purpose

The detector layer is structurally strong, but small contract mistakes can poison downstream research.

The main hardening goals are:

1. preserve causality
2. preserve direction semantics
3. preserve subtype meaning
4. preserve event-intensity meaning
5. preserve comparability across detectors and families

If a detector fires correctly but emits ambiguous direction, retrospective labels, or mixed subtypes, the
research layer will still learn the wrong lesson.

## Core Detector Contract

Every detector should satisfy the following contract:

- explicit `event_type`
- explicit required columns
- causal or explicitly retrospective behavior
- normalized raw event direction
- stable event intensity semantics
- stable event metadata for downstream interpretation

Current repository policy:

- raw event directions emitted by detector code should resolve to `up`, `down`, or `non_directional`
- detector metadata should include `causal`
- retrospective detectors must declare `causal = False`

## Causality Policy

Detectors fall into two categories:

### Causal detectors

These use only information available at or before the evaluation bar.

Examples:

- threshold crossings based on rolling history
- onset transitions based on prior bars
- episode clustering over causal base masks

These are eligible for live-style use, subject to the rest of the contract.

### Retrospective detectors

These confirm an event by looking at future bars.

Examples in the current repo:

- `FUNDING_FLIP`
- `FEE_REGIME_CHANGE_EVENT`

These are useful as labels, diagnostics, or retrospective studies, but they are not live detectors unless
rewritten to remove future confirmation.

## Direction Policy

Detector direction is not the same thing as hypothesis direction.

Detector direction should describe the event itself in normalized event vocabulary:

- `up`
- `down`
- `non_directional`

Research and strategy layers may later translate those into trade directions like `long` or `short`.

Why this matters:

- the base event contract stores both `direction` and numeric `sign`
- if detectors emit mixed vocabularies, downstream sign inference becomes ambiguous
- some earlier detector code emitted `long` / `short`, which made raw-event contracts inconsistent

Current policy:

- raw detector emission should use normalized event direction
- downstream hypothesis construction may still use `long` / `short`

## Episode Policy

Episode detectors should not be treated as second-class emitters.

An episode detector must preserve the same contract as a point detector:

- direction
- severity
- causality
- event index
- episode metadata such as start/end/peak/duration

If the episode path bypasses direction or severity logic, downstream comparisons become misleading.

## Intensity Policy

Intensity should mean one thing per detector.

Good:

- z-score magnitude for a dislocation detector
- normalized spread stress for a friction detector
- reversal impulse size for an exhaustion detector

Bad:

- event triggers on one quantity but intensity measures a different quantity with a different interpretation
- heterogeneous trigger paths share one label but one generic intensity

When a detector has multiple trigger paths, either:

- split the detector into subtypes
- or emit subtype metadata and keep intensity interpretable within each subtype

## Subtype Policy

Composite detectors should not hide materially different mechanisms under one label.

Known example:

- `FUNDING_PERSISTENCE_TRIGGER` currently mixes acceleration-triggered events and run-length persistence events

Recommended rule:

- if two trigger paths imply different market stories or different expected horizon behavior, they should be
  separate event types or at least explicit subtypes in metadata

## Family-Specific Hardening Priorities

### Funding family

Primary issues:

- lifecycle detectors discard sign by relying on absolute funding magnitude
- persistence mixes multiple trigger modes
- normalization intensity is only loosely tied to the event story

Recommended direction:

- preserve signed funding alongside magnitude
- split persistence into explicit subtypes
- keep retrospective labels clearly marked as non-causal

### Exhaustion family

Primary issues:

- detectors are structurally richer but more parameter-sensitive
- direction and subtype semantics matter more because trigger logic is composite

Recommended direction:

- keep normalized direction
- keep trigger-path metadata when multiple mechanisms can fire
- treat synthetic performance carefully because false positives can cluster in trend-heavy regimes

### Trend family

Primary issues:

- some detectors are more heuristic and timeframe-sensitive
- `SUPPORT_RESISTANCE_BREAK` is still effectively a stub

Recommended direction:

- remove or implement stubs
- avoid presenting heuristic trend detectors as fully calibrated live-safe signals without family-level review

### Temporal and fee-regime detectors

Primary issues:

- some are timing labels rather than alpha events
- `FEE_REGIME_CHANGE_EVENT` is retrospective under current implementation

Recommended direction:

- keep timing and structural labels, but mark retrospective confirmation clearly
- do not overinterpret them as live trade triggers without additional filtering

## Live-Safe Detector Subset

The project should maintain a strict live-safe subset.

A detector belongs in that subset only when all of the following are true:

1. `causal = True`
2. raw event direction is normalized and coherent
3. event intensity matches event meaning
4. trigger path is semantically narrow enough to interpret
5. synthetic and or historical audit results do not show chronic ontology confusion

This subset should be intentionally smaller than the full detector inventory.

Published code surface:

- [project/events/policy.py](/home/tstuv/workspace/trading/EDGEE/project/events/policy.py)

The current policy module also separates:

- `LIVE_SAFE_EVENT_TYPES`
- `RETROSPECTIVE_EVENT_TYPES`
- `LEGACY_EVENT_TYPES`

## Recommended Hardening Order

### Tier 1: contract hygiene

- add explicit causality metadata everywhere
- normalize raw event direction
- repair episode-detector emission parity

### Tier 2: semantic hygiene

- preserve funding sign in lifecycle detectors
- split composite subtypes where needed
- realign intensity with trigger meaning

### Tier 3: inventory hygiene

- remove or implement stubs
- prune or namespace legacy aliases
- define and publish the live-safe subset

## Interpretation Rules For Research

Do not interpret detector work at only one level.

Separate:

- detector contract correctness
- detector truth recovery
- hypothesis economics
- promotion viability

A detector can be:

- mechanically correct
- ontologically clear
- statistically recover the planted regime

and still fail as a useful trade trigger.

That is not a contradiction. It is normal.

## Definition Of Done

A detector hardening change is only done when all of the following are true:

- the detector contract is explicit
- focused regression tests exist
- synthetic or historical audit interpretation is updated
- docs explain whether the detector is causal, supporting-only, live-only, or live-safe

Without those, the change is still just local code churn.
