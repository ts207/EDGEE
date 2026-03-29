# Architecture Maintenance Checklist

Use this checklist whenever architectural surfaces, wrappers, or generated
inventory artifacts change.

## Contracts and Generated Docs

- Regenerate `docs/generated/architecture_metrics.json` after structural edits.
- Regenerate governance outputs in `docs/generated/` when detector or ontology
  surfaces move.
- Keep the architecture surface inventory consistent with the actual import
  boundaries.

## Research Services and Wrappers

- Wrapper CLIs should delegate into `project.research.services` instead of
  reimplementing policy.
- Gate resolution should remain spec-driven through `project.specs.gates`.
- Audit any new bridge or promotion wrapper for undocumented hardcoded policy.

## Strategy Surfaces

- Prefer `project.strategy.dsl` for canonical strategy schema and validation.
- Do not add new callers to transitional compatibility surfaces unless migration
  is blocked and documented.
- Remove dead aliases once importers reach zero and the generated metrics confirm
  the shrinkage.

## Metrics and Guardrails

- Watch `module_coupling_count`, `cross_boundary_import_count`, and
  `circular_dependency_count`.
- Keep generated metric snapshots current before declaring the architecture
  surface clean.
- Treat increases in transitional import counts as explicit repair work, not
  background drift.
