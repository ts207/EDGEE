# Audit Findings

## Verified Defects

### VD-1 High: Repository hygiene is red due to widespread `Zone.Identifier` contamination

Files:

- `project/tests/contracts/test_repository_hygiene.py:6`
- examples under `docs/`, `project/`, `.codex/`, and `data/`

What was verified:

- `pytest -q project/tests/contracts/test_repository_hygiene.py -q` fails immediately.
- The failure reported `2755` offenders.
- Direct filesystem inspection confirmed sidecars on source files, generated docs, and runtime artifacts.

Why it matters:

- This is a current, reproducible artifact-integrity failure.
- Any workflow that trusts repo-root file enumeration is now exposed to non-canonical garbage files.
- CI and operator hygiene gates are already broken.

Validation:

```bash
pytest -q project/tests/contracts/test_repository_hygiene.py -q
find . -type f \( -name '*:Zone.Identifier' -o -name '*#Uf03aZone.Identifier' -o -name '*#Uf03aZone.Identifier:Zone.Identifier' \) | wc -l
```

### VD-2 High: Objective/profile contract provenance is not trustworthy

Files:

- `project/specs/objective.py:255`
- `project/specs/objective.py:273`
- `project/specs/objective.py:290`
- `project/spec_registry/loaders.py:170`
- `project/spec_registry/loaders.py:197`

What was verified:

- Manifest-sourced spec paths are preserved into the returned contract.
- The loaders silently fall back to repo defaults when those paths are absent.
- A controlled repro returned a valid contract while reporting nonexistent manifest paths.

Why it matters:

- Research objective gates and retail profile constraints are economic controls.
- A contract that records the wrong source path undermines replay, auditability, and operator trust.
- If the manifest path exists in another checkout, the active repo can load foreign policy without any repo-boundary enforcement.

Validation:

```bash
.venv/bin/python -c "from pathlib import Path; import json, tempfile; from project import PROJECT_ROOT; from project.specs.objective import resolve_objective_profile_contract; td=Path(tempfile.mkdtemp()); data_root=td/'data'; run_dir=data_root/'runs'/'r_fake'; run_dir.mkdir(parents=True); (run_dir/'run_manifest.json').write_text(json.dumps({'run_id':'r_fake','objective_name':'retail_profitability','objective_spec_path':'/definitely/missing/objective.yaml','retail_profile_name':'capital_constrained','retail_profile_spec_path':'/definitely/missing/retail_profiles.yaml'}), encoding='utf-8'); c=resolve_objective_profile_contract(project_root=PROJECT_ROOT, data_root=data_root, run_id='r_fake', required=True); print(c.objective_spec_path, c.min_trade_count, c.retail_profile_spec_path, c.min_tob_coverage)"
```

### VD-3 Medium: Live incubation gating persists to the wrong default path

Files:

- `project/__init__.py:8`
- `project/live/runner.py:99`
- `project/portfolio/incubation.py:15`

What was verified:

- `PROJECT_ROOT` resolves to `/home/irene/Edge/project`.
- `LiveEngineRunner` constructs `PROJECT_ROOT / "project" / "live" / "incubation_ledger.json"`.
- Runtime reproduction resolved that path to `/home/irene/Edge/project/project/live/incubation_ledger.json`.

Why it matters:

- Incubation graduation is a live-trading gate.
- Persisting the ledger to a duplicated non-canonical path can split or reset strategy graduation state.
- The defect sits on the engine/live boundary and affects runtime safety, not just local developer ergonomics.

Validation:

```bash
.venv/bin/python -c "from project import PROJECT_ROOT; from project.live.runner import LiveEngineRunner; r=LiveEngineRunner(['btcusdt'], data_manager=object(), runtime_mode='monitor_only'); print(PROJECT_ROOT); print(r.incubation_ledger.path)"
```

## Likely Defects

### LD-1 Medium: Stale prior-checkout artifacts remain in the active data root and interact badly with manifest-preferred path resolution

Files:

- `data/runs/smoke_test_dry_e4ccf5ca/run_manifest.json`
- `data/artifacts/experiments/btc_2021_2m_research/btc_vol_test/*`
- `project/specs/objective.py:264`
- `project/specs/objective.py:281`

Why it matters:

- Artifact integrity is a top-level repo promise.
- Preserved prior-checkout manifests increase the probability of stale-policy reuse during reruns or audits.

## Speculative Concerns

### SC-1 Low: `LiveEngineRunner` always constructs a blank Binance client before runtime mode and environment validation are fully applied

Files:

- `project/live/runner.py:51`
- `project/scripts/run_live_engine.py:399`

Why it matters:

- I did not verify a concrete failure in this turn.
- The default blank client is still an unnecessary footgun on a live system surface.

## Architectural Debt

### AD-1: Objective/profile resolution spans two loader stacks with different fallback semantics

Files:

- `project/specs/loader.py`
- `project/spec_registry/loaders.py`
- `project/specs/objective.py:320`

Why it matters:

- This loader split is the structural reason VD-2 exists.
- It weakens contract clarity and makes provenance harder to reason about.

## Checks Run

- `pytest -q project/tests/contracts/test_repository_hygiene.py -q` -> failed
- `pytest -q project/tests/regressions/test_run_success_requires_outputs.py -q` -> passed
- `pytest -q project/tests/pipelines/test_run_all_smoke.py -q` -> passed
