# Missing Tests

## MT-1

Missing coverage:

- nonexistent manifest `objective_spec_path`
- nonexistent manifest `retail_profile_spec_path`
- manifest paths outside repo root

Why it matters:

- `project/tests/pipelines/test_objective_profile_contract.py` only covers valid manifest paths and explicit overrides.
- The current gap allowed VD-2 to persist.

Suggested test shape:

- write a temp run manifest with missing absolute paths
- call `resolve_objective_profile_contract()`
- assert one of:
  - fail closed with `FileNotFoundError`, or
  - returned contract paths are rewritten to the actual resolved files

## MT-2

Missing coverage:

- default `LiveEngineRunner` incubation ledger location

Why it matters:

- `project/tests/live/test_runner.py` replaces the ledger path with temp fixtures instead of exercising the default constructor path.
- The current gap allowed VD-3 to persist.

Suggested test shape:

- instantiate `LiveEngineRunner` with a dummy data manager
- assert `runner.incubation_ledger.path` resolves to the canonical location
- assert no duplicated `project/project/` segment appears

## MT-3

Missing evidence:

- fresh end-to-end artifact-producing run covering proposal issuance, search, promotion, and blueprint packaging in one bounded flow

Why it matters:

- This audit confirmed the stage map and finalization guardrails, but it did not generate a new full promotion bundle in this turn.

Suggested bounded run:

```bash
.venv/bin/python -m project.research.agent_io.issue_proposal --proposal <bounded_proposal.yaml> --registry_root project/configs/registries --plan_only 0 --dry_run 0
```
