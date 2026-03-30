# Issue Ledger

## Verified Defects

### VD-1: Repository hygiene and artifact integrity are already broken by Windows ADS sidecars

Evidence:

- `project/tests/contracts/test_repository_hygiene.py:6` fails closed on any `Zone.Identifier` sidecar under repo root.
- Local run: `pytest -q project/tests/contracts/test_repository_hygiene.py -q` failed with `2755` offenders.
- Sample offending paths observed directly:
  - `docs/AGENT_CONTRACT.md:Zone.Identifier`
  - `docs/generated/detector_coverage.json:Zone.Identifier`
  - `data/runs/smoke_test_dry_e4ccf5ca/run_manifest.json:Zone.Identifier`
  - `.codex/config.toml:Zone.Identifier`
  - `project/contracts/pipeline_registry.py:Zone.Identifier`

Why it matters:

- This is a verified false-green blocker for hygiene CI.
- It contaminates runtime artifacts, generated docs, and source surfaces simultaneously.
- Audit and operator tooling that enumerate files under the repo root now see non-canonical artifacts.

How to reproduce:

```bash
pytest -q project/tests/contracts/test_repository_hygiene.py -q
find . -type f \( -name '*:Zone.Identifier' -o -name '*#Uf03aZone.Identifier' -o -name '*#Uf03aZone.Identifier:Zone.Identifier' \) | head
```

### VD-2: Objective/profile provenance can claim one path while loading another source

Evidence:

- `project/specs/objective.py:255` and `project/specs/objective.py:273` preserve manifest-sourced absolute paths without validating they exist.
- `project/specs/objective.py:320` and `project/specs/objective.py:325` pass those paths into loaders.
- `project/spec_registry/loaders.py:170` and `project/spec_registry/loaders.py:197` silently fall back to repo defaults when the explicit path does not exist.
- Controlled repro produced a valid contract from current repo defaults while reporting missing manifest paths:

```json
{
  "objective_id": "retail_profitability",
  "objective_spec_path": "/definitely/missing/objective.yaml",
  "retail_profile_name": "capital_constrained",
  "retail_profile_spec_path": "/definitely/missing/retail_profiles.yaml",
  "min_trade_count": 150,
  "min_tob_coverage": 0.8
}
```

Why it matters:

- Contract integrity is broken: the returned `ObjectiveProfileContract` can misstate the source of economic gates and retail constraints.
- Replays, resumes, and audits can silently consume a different objective/profile than the path recorded in the contract.
- If the manifest path exists in another checkout, the code can source policy from outside the active repo without any boundary check.

How to reproduce:

```bash
.venv/bin/python -c "from pathlib import Path; import json, tempfile; from project import PROJECT_ROOT; from project.specs.objective import resolve_objective_profile_contract; td=Path(tempfile.mkdtemp()); data_root=td/'data'; run_dir=data_root/'runs'/'r_fake'; run_dir.mkdir(parents=True); (run_dir/'run_manifest.json').write_text(json.dumps({'run_id':'r_fake','objective_name':'retail_profitability','objective_spec_path':'/definitely/missing/objective.yaml','retail_profile_name':'capital_constrained','retail_profile_spec_path':'/definitely/missing/retail_profiles.yaml'}), encoding='utf-8'); c=resolve_objective_profile_contract(project_root=PROJECT_ROOT, data_root=data_root, run_id='r_fake', required=True); print(c.objective_spec_path, c.min_trade_count, c.retail_profile_spec_path, c.min_tob_coverage)"
```

### VD-3: Live incubation state persists to a duplicated non-canonical path

Evidence:

- `project/__init__.py:8` defines `PROJECT_ROOT = Path(__file__).resolve().parent`, which is `/home/irene/Edge/project` in this checkout.
- `project/live/runner.py:99` writes the incubation ledger to `PROJECT_ROOT / "project" / "live" / "incubation_ledger.json"`.
- Direct repro showed the resolved path is `/home/irene/Edge/project/project/live/incubation_ledger.json`.
- `project/portfolio/incubation.py:15` creates parent directories and persists to the supplied path, so the bad path is operational, not cosmetic.

Why it matters:

- Live gating state for `is_graduated()` can be written to an unintended location.
- A separate path means production state can fragment across multiple ledgers and reset graduation decisions unexpectedly.
- This is a runtime-safety defect on the engine/live boundary, not just a doc mismatch.

How to reproduce:

```bash
.venv/bin/python -c "from project import PROJECT_ROOT; from project.live.runner import LiveEngineRunner; r=LiveEngineRunner(['btcusdt'], data_manager=object(), runtime_mode='monitor_only'); print(PROJECT_ROOT); print(r.incubation_ledger.path)"
```

## Likely Defects

### LD-1: Stale run artifacts from another checkout remain mixed into the active data root

Evidence:

- `data/runs/smoke_test_dry_e4ccf5ca/run_manifest.json` records `/mnt/data/project_unzipped_v6/Edge-irene/...` absolute paths.
- `data/artifacts/experiments/btc_2021_2m_research/btc_vol_test/*` remains present beside current-checkout artifacts.
- `project/specs/objective.py:264` and `project/specs/objective.py:281` prefer manifest paths during contract resolution.

Why it matters:

- Artifact provenance and resume behavior can drift toward prior worktree state.
- This interacts directly with VD-2 and raises the chance of stale policy reuse during bounded reruns.

How to validate:

```bash
sed -n '1,120p' data/runs/smoke_test_dry_e4ccf5ca/run_manifest.json
find data/artifacts/experiments -maxdepth 4 -type f | head -20
```

## Speculative Concerns

### SC-1: The live runner always constructs a blank Binance REST client even outside validated trading setup

Evidence:

- `project/live/runner.py:51` constructs `BinanceFuturesClient(api_key='', api_secret='')` unconditionally.
- `project/scripts/run_live_engine.py:399` separately constructs the environment-validated exchange client for trading mode.

Why it matters:

- I did not find a failing test or direct exploit path in this audit turn.
- The blank client could still become an accidental call target for future startup or recovery code and fail in a misleading way.

How to validate:

- Trace all signed REST call sites reachable from `LiveEngineRunner.start()` and recovery paths.
- Add a test that asserts trading mode never uses the blank fallback client when environment-backed credentials are supplied.

## Architectural Debt

### AD-1: Two spec-loader surfaces encode different trust models

Evidence:

- `project/specs/loader.py` exposes project-root-aware loaders.
- `project/spec_registry/loaders.py` exposes repo-root global loaders with silent candidate fallback.
- `project/specs/objective.py:320` uses the `project.spec_registry` surface, not the project-root-aware loader.

Why it matters:

- This split is the enabling condition behind VD-2.
- It weakens source-of-truth guarantees because path-bearing contracts are assembled by one module and loaded by another with different fallback semantics.

## Missing Tests / Missing Evidence

### MT-1: No regression test covers nonexistent or out-of-repo manifest objective/profile paths

Evidence:

- `project/tests/pipelines/test_objective_profile_contract.py:9` only covers valid manifest paths and explicit profile overrides.
- No test asserts fail-closed behavior or path rewriting when manifest paths are absent.

### MT-2: No regression test covers the default incubation ledger path in `LiveEngineRunner`

Evidence:

- `project/tests/live/test_runner.py:272` and `project/tests/live/test_runner.py:367` override the ledger path with a temp file.
- No test asserts the default path stays under a canonical repo location.

### MT-3: No automated evidence was collected in this turn for end-to-end proposal execution with real promotion and blueprint artifacts

Evidence:

- The bounded checks run here were hygiene, smoke planning/dry-run, and finalization canaries.
- No fresh full artifact-producing research run was executed in this audit turn.
