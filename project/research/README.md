# Research Layer (`project/research`)

The research layer owns hypothesis generation, statistical evaluation, promotion policy, and research memory.

## Ownership

- Candidate discovery and phase-2 evaluation
- Promotion policy and audit generation
- Research reporting and run comparison
- Knowledge, memory, and reflection surfaces for agent-driven workflows
- Search, robustness, gating, and recommendation helpers used by the research pipeline

## Non-Ownership

- Live execution and OMS behavior
- Raw data ingestion and cleaning
- Venue-specific adapters and low-level market interfaces
- Top-level orchestration of the full pipeline DAG

## Canonical Public Surfaces

- `project.research.services.candidate_discovery_service`
- `project.research.services.promotion_service`
- `project.research.services.reporting_service`
- `project.research.services.run_comparison_service`
- `project.research.knowledge.query`
- `project.research.agent_io.{proposal_to_experiment,execute_proposal,issue_proposal}`

## Working Rules

- Keep stable workflow APIs in service modules, not ad hoc wrappers.
- Keep policy logic separate from raw metric computation.
- Keep the layer deterministic for identical inputs and configs.
- Prefer repo-native contracts and schemas over one-off dataframe conventions.
