# Architecture

This document lists the package surfaces that should be treated as canonical in the current repository snapshot.

## Canonical surfaces

| Surface | Primary path | Role |
|---|---|---|
| Pipeline entrypoints | `project/pipelines/` | Run orchestration and stage wiring |
| Research orchestration | `project/pipelines/research/` | Campaign control, discovery, promotion, reporting |
| Research knowledge | `project/research/knowledge/` | Memory, reflections, schemas, query helpers |
| Research services | `project/research/services/` | Business logic wrappers used by pipelines and operators |
| Research promotion | `project/research/promotion/` | Promotion scoring, gates, clustering, reporting |
| Research clustering | `project/research/clustering/` | PnL similarity and cluster representative selection |
| Contracts | `project/contracts/` | Artifact, stage, and temporal contracts |
| Live execution | `project/live/` | OMS, runner, health checks, drift, kill switch |
| Portfolio | `project/portfolio/` | Allocation spec, sizing, and risk budget |
| Strategy compilation | `project/compilers/` and `project/strategy/` | Blueprint/spec transformation and execution-facing strategy surfaces |
| Spec registry | `project/spec_registry/` | Search-space and registry loading |
| Domain models | `project/domain/` | Hypothesis and registry models |

## Import policy

Prefer imports from these surfaces rather than reaching into implementation details from unrelated packages.

Examples:

- Use contracts for schema and stage agreement.
- Use research services for reusable orchestration logic.
- Use promotion modules for scoring and gate logic.
- Use live and portfolio modules only where deployment state or sizing is genuinely needed.

## Compatibility facades

Some modules remain for compatibility with older paths or maintenance scripts. Treat them as facades unless the module is clearly the maintained source of truth for its surface.

If a facade and a canonical surface disagree, the canonical surface wins.

## Missing or underdocumented surfaces

The codebase contains real implementations that are easy to miss in older docs:

- `project/pipelines/research/campaign_controller.py`
- `project/pipelines/research/search_intelligence.py`
- `project/pipelines/research/feature_mi_scan.py`
- `project/research/clustering/alpha_clustering.py`
- `project/research/clustering/pnl_similarity.py`
- `project/research/promotion/promotion_gate_evaluators.py`
- `project/live/state.py`
- `project/live/kill_switch.py`

These should be treated as first-class surfaces when editing docs or behavior.

## Keeping this doc current

Update this file when:

- a new top-level package becomes part of the supported architecture,
- a canonical import path changes,
- a compatibility facade is removed, or
- a new contract layer is introduced.
