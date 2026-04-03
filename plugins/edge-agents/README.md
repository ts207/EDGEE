# Edge agents plugin

Repo-local Codex/plugin surface for the Edge repository.

## Purpose

Provide guided wrappers around the canonical bounded workflow without creating a parallel operator model.

## What is included

- skills for repo orientation, maintenance, ChatGPT-app development, coordination, analysis, compiler flow, and thesis bootstrap
- thin wrappers around the canonical `make discover|package|validate|review` and `edge operator ...` surfaces
- hook definitions for contract-sensitive edits and recent-run awareness

## Important scripts

- `scripts/edge_query_knowledge.sh`
- `scripts/edge_preflight_proposal.sh`
- `scripts/edge_lint_proposal.sh`
- `scripts/edge_explain_proposal.sh`
- `scripts/edge_plan_proposal.sh`
- `scripts/edge_run_proposal.sh`
- `scripts/edge_diagnose_run.sh`
- `scripts/edge_regime_report.sh`
- `scripts/edge_chatgpt_app.sh`
- `scripts/edge_sync_plugin.sh`
- `scripts/edge_governance.sh`
- `scripts/edge_validate_repo.sh`
- `scripts/edge_verify_contracts.sh`
- `scripts/edge_verify_run.sh`
- `scripts/edge_compare_runs.sh`
- `scripts/edge_show_run_artifacts.sh`
- `scripts/edge_package_theses.sh`
- `scripts/edge_bootstrap_theses.sh`

## Dependency rule

These wrappers should remain thin around:

- `make discover|package|validate|review`
- `edge operator ...`
- `python -m project.scripts.run_researcher_verification`
- generated run and thesis artifacts

They are convenience surfaces, not policy owners.

## Maintenance focus

The plugin now helps route common developer change types:

- operator or proposal-surface changes -> `make validate` plus operator inventory regeneration
- event, ontology, or registry changes -> validation plus event-contract and system-map regeneration
- thesis packaging or overlap changes -> `make package` and overlap regeneration
- ChatGPT app changes -> `edge-chatgpt-app` inspection/serve helpers plus canonical operator surfaces
- plugin changes -> local plugin-cache sync and sync checks

## Relationship to docs

See:

- `docs/03_OPERATOR_WORKFLOW.md`
- `docs/04_COMMANDS_AND_ENTRY_POINTS.md`
- `docs/09_THESIS_BOOTSTRAP_AND_PROMOTION.md`
- `docs/VERIFICATION.md`
