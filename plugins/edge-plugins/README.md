# Edge Plugins

Project-local Codex plugin scaffold for the `Edge` repository.

This plugin now includes repo-specific skills, scripts, and assets for:

- detector and event-spec work
- bounded proposal-driven research loops
- pipeline and artifact-contract debugging
- targeted verification and audit workflows

Main surfaces:

- `skills/edge-repo/` for repository orientation
- `skills/edge-detector-spec/` for detector plus spec changes
- `skills/edge-bounded-research/` for proposal and bounded run discipline
- `skills/edge-maintenance/` for verification and maintenance gates
- `skills/edge-promotion-audit/` for promotion evidence and run comparison
- `skills/edge-artifact-triage/` for missing or contradictory run artifacts
- `scripts/edge_checks.sh` for targeted detector verification
- `scripts/edge_query_knowledge.sh` for knowledge and memory lookup
- `scripts/edge_verify_contracts.sh` for maintained contract verification
- `scripts/edge_verify_run.sh` for experiment verification on a completed run
- `scripts/edge_plan_proposal.sh` for proposal planning
- `scripts/edge_discover_target.sh` for bounded direct discovery runs
- `scripts/edge_compare_runs.sh` for baseline vs candidate run comparison
- `scripts/edge_show_run_artifacts.sh` for canonical artifact-path inspection

The plugin is local to this repository and does not create marketplace entries unless requested separately.


No external MCP servers or app registrations are configured in this snapshot.
