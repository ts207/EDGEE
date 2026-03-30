# Remediation Plan

## Priority 0

### Remove repository-wide `Zone.Identifier` contamination and fail fast in hygiene workflows

Actions:

- purge all ADS sidecars under the repo root, including `docs/`, `project/`, `.codex/`, and `data/`
- run `project/scripts/check_repo_hygiene.sh`
- rerun `pytest -q project/tests/contracts/test_repository_hygiene.py -q`
- decide whether generated/runtime artifact directories should remain under repo root for normal development

Why first:

- This is already failing a maintained test.
- It contaminates evidence collection for every future audit.

## Priority 1

### Make objective/profile resolution fail closed or rewrite provenance to the actual source used

Actions:

- in `project/specs/objective.py`, validate manifest-sourced paths before preserving them into `ObjectiveProfileContract`
- in `project/spec_registry/loaders.py`, stop silently falling through from a missing explicit path when `required=True`
- alternatively, return the actual resolved file path from the loader and store that in the contract
- optionally restrict manifest/env paths to the active repo root unless an explicit escape hatch is approved

Why next:

- This is a contract-integrity defect on policy-bearing economic controls.
- It can silently change research or deployment assumptions.

## Priority 2

### Fix the live incubation ledger default path

Actions:

- change `project/live/runner.py` to use `PROJECT_ROOT / "live" / "incubation_ledger.json"` or a config/env-provided path
- add a regression test that instantiates `LiveEngineRunner` without overriding the ledger and asserts the resolved path
- decide whether live state belongs under repo storage at all or should be operator-configured outside the checkout

Why next:

- The bug affects live graduation gating.
- The fix is narrowly scoped and low risk.

## Priority 3

### Quarantine or clean stale local artifacts that encode prior worktree paths

Actions:

- remove or archive stale runs under `data/runs/` and stale experiment bundles under `data/artifacts/experiments/`
- if stale runs must remain, mark them clearly and exclude them from default audit/hygiene scans
- add a bounded verification that rejects manifest provenance paths outside the active repo root when resuming or replaying

## Verification Block After Fixes

```bash
pytest -q project/tests/contracts/test_repository_hygiene.py -q
pytest -q project/tests/pipelines/test_objective_profile_contract.py -q
pytest -q project/tests/live/test_runner.py -q
pytest -q project/tests/regressions/test_run_success_requires_outputs.py -q
project/scripts/check_repo_hygiene.sh
```
