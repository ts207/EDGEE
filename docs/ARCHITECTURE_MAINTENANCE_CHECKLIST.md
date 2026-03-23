# Architecture Maintenance Checklist

## Contracts and Generated Docs

- regenerate architecture and ontology artifacts after structural changes
- keep docs under `docs/generated/` in sync with the checked-in package layout

## Research Services and Wrappers

- pipeline wrappers should stay thin and delegate to research service/spec modules
- broken compatibility fragments should be removed or completed, not left partially extracted

## Strategy Surfaces

- prefer `project.strategy.dsl` over deprecated strategy DSL import paths
- keep runtime and compiler entrypoints exposed from canonical package roots

## Metrics and Guardrails

- watch LOC thresholds for large modules before adding new behavior
- refresh architecture metrics snapshots when moving or deleting surfaces
