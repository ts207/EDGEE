# Migration Guide

This guide helps users transition from legacy terminology and commands to the canonical four-stage model.

## 1. Command Mapping

| Legacy Command | Canonical Replacement |
| :--- | :--- |
| `edge operator run` | `edge discover run` |
| `edge operator plan` | `edge discover plan` |
| `edge operator preflight` | `edge discover plan` |
| `edge operator compare` | `edge validate report` |
| `edge operator regime-report` | `edge validate report` |
| `edge operator diagnose` | `edge validate diagnose` |
| `edge pipeline run-all` | `edge discover run` (with full pipeline enabled) |

## 2. Terminology Mapping

| Legacy Term | Canonical Term |
| :--- | :--- |
| `trigger` | `anchor` |
| `state` | `filter` |
| `proposal` | `structured hypothesis` |
| `certification` | `promotion` |
| `strategy` | `thesis` |

## 3. Deprecation and Support Phases

Temporary compatibility becomes permanent debt unless it has an explicit shutdown path. We manage legacy APIs through the following explicit phases:

* **Phase 1: Supported + Warned** (Standard Output warnings, silent remapping)
* **Phase 2: Supported + Noisy Warning** (Loud STDERR warnings, execution pauses)
* **Phase 3: Compatibility-Flag Only** (Requires explicit `--legacy_compatibility 1` to run)
* **Phase 4: Removed** (Code deleted, execution fails)

Currently, the CLI and Schema parsing are in **Phase 3**. Silent remapping has been stopped; you must pass explicit flags to use legacy paths.

> **Note on Tracking:** We now actively log legacy usage paths (to `data/logs/legacy_usage.log`) so we know exactly what systems are still relying on deprecated interfaces before advancing to Phase 4.

## 4. How to Migrate your Specs

In your YAML proposals:
1. Rename `trigger_type` to `anchor`.
2. Ensure `context_filters` are clearly distinguished from the `anchor`.
3. Update any internal documentation to refer to `theses` instead of `strategies`.

## 5. Success Criteria Checklist

We measure progress not by how many features are added, but by whether the repository exhibits clear, semantic stage definitions. Use this live checklist to assess the health of the overhaul:

* [ ] Can a new user explain the repo as `discover → validate → promote → deploy`?
* [ ] Is there zero ambiguity between `anchor`, `filter`, `sampling policy`, and `template`?
* [ ] Can you answer separately whether a thesis is discovered, validated, promoted, or deployed?
* [ ] Are persistence and overlap handled explicitly?
* [ ] Can **only** promoted theses reach deployment?
