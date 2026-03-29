# Post-Implementation Bounded Experiment Postmortem

## Hypothesis Tested

After the implementation patch series, one narrow proposal-issued run should produce a single internally consistent candidate surface such that discovery, promotion, blueprint compilation, comparison, and typed-engine entry all reference the same lineage chain and semantic metadata without fallback reconciliation.

## Run Scope And Inputs

- Proposal path: `/home/irene/Edge/.tmp/phase2_surface_smoke_proposal.yaml`
- Proposal-issued run ID: `smoke_program_20260329T130335Z_1988fdc9e1`
- Replay data root: `/home/irene/Edge/.tmp/final_bounded_run_data_v2_smoke_program_20260329T130335Z_1988fdc9e1`
- Program ID: `smoke_program`
- Symbol: `BTCUSDT`
- Timeframe: `5m`
- Event type: `VOL_SHOCK`
- Template family: `continuation`
- Horizons: `12`, `24`
- Directions: `long`, `short`
- Entry lag: `0`

The run remained bounded by replaying the repo-local smoke dataset under the proposal-issued run ID instead of widening into a full live-data execution.

## Commands Executed

```bash
.venv/bin/python -m project.research.agent_io.issue_proposal \
  --proposal /home/irene/Edge/.tmp/phase2_surface_smoke_proposal.yaml \
  --registry_root project/configs/registries \
  --plan_only 1

BACKTEST_DATA_ROOT=/home/irene/Edge/.tmp/final_bounded_run_data_v2_smoke_program_20260329T130335Z_1988fdc9e1 \
.venv/bin/python - <<'PY'
import dataclasses
import json
import os
from pathlib import Path
from project.reliability.smoke_data import build_smoke_dataset, run_research_smoke, run_promotion_smoke

run_id = "smoke_program_20260329T130335Z_1988fdc9e1"
root = Path(os.environ["BACKTEST_DATA_ROOT"])
dataset = build_smoke_dataset(root, seed=20260101, storage_mode="auto")
dataset = dataclasses.replace(dataset, run_id=run_id, symbols=("BTCUSDT",))
(root / "runs" / run_id).mkdir(parents=True, exist_ok=True)
(root / "runs" / run_id / "run_manifest.json").write_text(json.dumps({
    "run_id": run_id,
    "run_mode": "confirmatory",
    "discovery_profile": "smoke",
    "candidate_origin_run_id": run_id,
    "confirmatory_rerun_run_id": "",
    "program_id": "smoke_program",
    "objective_name": "retail_profitability",
    "promotion_profile": "research",
    "symbols": ["BTCUSDT"],
    "proposal_path": "/home/irene/Edge/.tmp/phase2_surface_smoke_proposal.yaml",
}, indent=2, sort_keys=True), encoding="utf-8")
research = run_research_smoke(dataset)
run_promotion_smoke(dataset, research)
PY

BACKTEST_DATA_ROOT=/home/irene/Edge/.tmp/final_bounded_run_data_v2_smoke_program_20260329T130335Z_1988fdc9e1 \
.venv/bin/python -m project.research.compile_strategy_blueprints \
  --run_id smoke_program_20260329T130335Z_1988fdc9e1 \
  --symbols BTCUSDT \
  --ignore_checklist 1

.venv/bin/pytest project/tests/smoke/test_promotion_smoke.py -q
```

## Observed Outputs

- Run manifest: `/home/irene/Edge/.tmp/final_bounded_run_data_v2_smoke_program_20260329T130335Z_1988fdc9e1/runs/smoke_program_20260329T130335Z_1988fdc9e1/run_manifest.json`
- Phase-2 candidates: `/home/irene/Edge/.tmp/final_bounded_run_data_v2_smoke_program_20260329T130335Z_1988fdc9e1/reports/phase2/smoke_program_20260329T130335Z_1988fdc9e1/phase2_candidates.parquet`
- Phase-2 diagnostics: `/home/irene/Edge/.tmp/final_bounded_run_data_v2_smoke_program_20260329T130335Z_1988fdc9e1/reports/phase2/smoke_program_20260329T130335Z_1988fdc9e1/phase2_diagnostics.json`
- Promotion decisions: `/home/irene/Edge/.tmp/final_bounded_run_data_v2_smoke_program_20260329T130335Z_1988fdc9e1/reports/promotions/smoke_program_20260329T130335Z_1988fdc9e1/promotion_decisions.parquet`
- Promotion diagnostics: `/home/irene/Edge/.tmp/final_bounded_run_data_v2_smoke_program_20260329T130335Z_1988fdc9e1/reports/promotions/smoke_program_20260329T130335Z_1988fdc9e1/promotion_diagnostics.json`
- Blueprint index: `/home/irene/Edge/.tmp/final_bounded_run_data_v2_smoke_program_20260329T130335Z_1988fdc9e1/reports/strategy_blueprints/smoke_program_20260329T130335Z_1988fdc9e1/executable_strategy_spec_index.json`
- Comparison output was inspected through `compare_run_ids(... baseline_run_id=run_id, candidate_run_id=run_id)`. It was mechanically valid but not substantively informative because baseline and candidate were the same run.

## Key Metrics

- Discovery candidate count: `2`
- Promotion decision count: `2`
- Promoted candidate count: `0`
- Blueprint count: `0`
- Executable strategy spec count: `0`
- `candidate_id == hypothesis_id` rows in phase-2 output: `0`
- Phase-2 `canonical_regime`: `VOLATILITY_TRANSITION` for both rows after local fix
- Phase-2 `routing_profile_id`: `regime_routing_v1` for both rows after local fix
- Promotion diagnostics `promotion_profile`: `research`
- Promotion primary reject gate: `gate_promo_statistical_program_q_value`
- Promotion rejection classification: `weak_holdout_support`

## Inconsistencies

- The original bounded-run scaffold did not preserve proposal semantics through promotion. It defaulted promotion to `auto`, which resolved to `deploy` because the replay manifest used `confirmatory` mode.
- The original smoke edge-candidate materialization overwrote `hypothesis_id` with `plan_*`, breaking lineage continuity at the replay boundary.
- The original promotion decision export dropped `hypothesis_id` even though upstream artifacts carried it.
- The original smoke phase-2 parquet omitted canonical regime-routing metadata, so the earliest run-scoped artifact was semantically thinner than downstream promotion outputs.
- Even after those local fixes, the bounded run still produces zero promoted candidates and therefore zero blueprints/specs. That means the experiment still does not prove the run-scoped blueprint-to-engine path end to end.

## Logical Errors

- The earlier post-implementation report overstated two points for this bounded run:
  - proposal-driven promotion-profile semantics were not actually preserved in the smoke replay before the fix
  - promotion outputs did not actually preserve `hypothesis_id` before the fix
- The comparison check on the same run ID is only a mechanical smoke, not evidence of cross-run consistency.
- The experiment hypothesis included blueprint compilation and typed-engine entry on run-scoped artifacts, but the chosen bounded dataset is too weak to satisfy that clause under current promotion thresholds.

## Likely Root Causes

- Boundary fixture drift: the smoke replay path in [`/home/irene/Edge/project/reliability/smoke_data.py`](/home/irene/Edge/project/reliability/smoke_data.py) had fallen behind the canonical research contracts.
- Export contract omission: promotion decision shaping in [`/home/irene/Edge/project/research/services/promotion_service.py`](/home/irene/Edge/project/research/services/promotion_service.py) and evidence-bundle flattening in [`/home/irene/Edge/project/research/validation/evidence_bundle.py`](/home/irene/Edge/project/research/validation/evidence_bundle.py) did not preserve `hypothesis_id`.
- Dataset calibration: the bounded smoke candidate set has `q_value=1.0` and fails the primary statistical gate, so no candidate survives into blueprint packaging.

## Obvious Fixes Applied

- In [`/home/irene/Edge/project/reliability/smoke_data.py`](/home/irene/Edge/project/reliability/smoke_data.py):
  - stopped overwriting real `hypothesis_id` values with `plan_*`
  - wrote hypothesis registry rows using real `hypothesis_id` plus explicit `plan_row_id`
  - passed `program_id`, `objective_name`, and `promotion_profile=research` into the promotion smoke helper
  - annotated smoke phase-2 outputs with canonical regime-routing metadata before writing artifacts
- In [`/home/irene/Edge/project/research/validation/evidence_bundle.py`](/home/irene/Edge/project/research/validation/evidence_bundle.py):
  - carried `hypothesis_id` into bundle metadata and flat-record export
- In [`/home/irene/Edge/project/research/services/promotion_service.py`](/home/irene/Edge/project/research/services/promotion_service.py):
  - included `hypothesis_id` in `promotion_decisions.parquet`

## Deferred Fixes

- No change was made to promotion thresholds or candidate scoring. The zero-promotion result is still acceptable for this run because threshold tuning would widen scope and weaken the bounded conclusion.
- No attempt was made to fabricate a promoted candidate purely to force blueprint generation. That would invalidate the experiment’s meaning.

## Acceptance Result By Phase

- Phase 1 canonical phase-2 pathing: `PASS`
- Phase 2 explicit distinct lineage in current-format candidate artifacts: `PASS`
- Phase 3 registry-backed canonical regime semantics present in run-scoped outputs: `PASS` after local smoke-fixture repair
- Phase 4 canonical proposal control fields preserved into promotion replay: `PASS` after local smoke-fixture repair
- Phase 5 run-scoped blueprint/spec/typed-engine exercise: `FAIL`

## What The Run Proved

- The implemented repository can now preserve one canonical phase-2 surface, distinct `candidate_id`/`hypothesis_id`, and canonical regime-routing metadata through the bounded replay path.
- The promotion replay can now preserve proposal control semantics and hypothesis lineage without fallback collapse.

## What The Run Did Not Prove

- It did not prove blueprint packaging or typed-engine invocation from this run’s own promoted artifacts because no candidate survived promotion.

## Recommended Improvements

- Add one maintained bounded fixture that deterministically yields at least one promoted candidate under `promotion_profile=research`, so Phase 5 can be exercised without touching production thresholds.
- Add a targeted regression test asserting that `promotion_decisions.parquet` preserves `hypothesis_id`.
- Add a targeted regression test asserting that smoke phase-2 outputs include `canonical_regime` and `routing_profile_id`.
- Keep comparison checks meaningful by comparing two distinct run IDs or skip the comparison section for self-comparisons.

## Next Action

- `explore`

Reason:
The local contract defects exposed by this run were fixed. The highest-value next bounded step is a slightly stronger maintained fixture or proposal slice that still stays narrow but guarantees at least one promoted candidate, so blueprint/spec/engine lineage can be verified on run-scoped artifacts instead of inferred from separate smoke tests.
