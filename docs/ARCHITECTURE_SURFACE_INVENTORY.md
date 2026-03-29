# Architecture Surface Inventory

This inventory separates canonical package surfaces from transitional and removed
surfaces so refactors can be audited without guessing which imports remain valid.

## Canonical Surfaces

- `project.pipelines.run_all`
- `project.contracts.pipeline_registry`
- `project.research.services`
- `project.specs.gates`
- `project.strategy.dsl`
- `project.strategy.runtime.dsl_runtime`

## Transitional Surfaces

- `project.strategy_dsl`
  Transitional alias surface retained only for compatibility accounting and
  architectural metrics.
- `project.strategy_templates`
  Transitional import surface tracked by metrics until all downstream callers are
  migrated to canonical strategy modules.

## Removed Surfaces

- `project.research.compat`
  Removed compatibility layer. New production code should not depend on it.
- Ad hoc wrapper-only orchestration layers that bypass
  `project.research.services` or `project.specs.gates`.

## Notes

- New orchestration code should flow through contracts, service modules, and the
  canonical strategy DSL surface.
- Transitional surfaces should shrink over time and never expand without an
  explicit architecture decision.
