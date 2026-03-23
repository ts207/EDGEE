# Architecture Surface Inventory

## Canonical Surfaces

- `project.artifacts`
- `project.compilers`
- `project.eval`
- `project.live`
- `project.portfolio`
- `project.spec_validation`
- `project.strategy.dsl`

## Transitional Surfaces

- `project.pipelines.research`
- `project.pipelines.eval`
- compatibility wrappers that re-export canonical package roots while older callers migrate

## Removed Surfaces

- `project.strategy_dsl`
- `project.strategy_templates`
- direct cross-domain deep imports that bypass package roots
