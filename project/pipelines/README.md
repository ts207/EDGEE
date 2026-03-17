# Pipelines Layer (`project/pipelines`)

The pipelines layer handles data ingestion, feature generation, orchestration, manifest bookkeeping, and stage execution.

## Ownership

- `run_all.py` and its helper modules for full-pipeline orchestration
- ingestion, clean, feature, and context stage scripts
- pipeline planning, execution, provenance, and summary utilities
- research-facing stage entrypoints under `project/pipelines/research/`

## Non-Ownership

- detector business logic
- research policy and promotion rules
- low-latency runtime execution
- schema ownership for stage and artifact contracts

## Important Modules

- `run_all.py`
- `run_all_bootstrap.py`
- `run_all_support.py`
- `run_all_finalize.py`
- `pipeline_planning.py`
- `pipeline_execution.py`
- `pipeline_provenance.py`
- `pipeline_summary.py`

## Constraints

- Each stage should communicate through declared artifacts rather than shared in-memory state.
- Wrappers should stay thin when a canonical service module already exists.
- Orchestration code should remain coordinator-oriented rather than absorbing domain logic.
