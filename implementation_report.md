# Implementation Report

## 1. Summary of Completed Phases

- Phase 1 completed: `phase2_search_engine` is the sole authoritative phase-2 discovery stage, canonical phase-2 path helpers now resolve `reports/phase2/<run_id>/...`, and downstream readers/writers were moved onto shared helpers.
- Phase 2 completed: current-format artifacts now carry both `hypothesis_id` and distinct `candidate_id`, lineage fallback joins were removed from the current-format path, and lineage fields were propagated into blueprint and executable-spec contracts.
- Phase 3 completed: research-critical consumers were moved off string-splitting heuristics and onto compiled-registry/regime-routing semantics for canonical grouping.
- Phase 4 completed: canonical `promotion_profile` now drives proposal/planning overrides, legacy proposal aliases remain ingress-only, and default planning no longer emits the legacy peer phase-2 path.
- Phase 5 completed: executable-spec lineage was expanded, a typed engine entry path was added, and engine metadata now preserves upstream lineage fields without recomputation.

## 2. Exact Files Changed

- `project/artifacts/__init__.py`
- `project/artifacts/catalog.py`
- `project/contracts/schemas.py`
- `project/engine/runner.py`
- `project/pipelines/pipeline_planning.py`
- `project/pipelines/research/phase2_candidate_discovery.py`
- `project/pipelines/stages/research.py`
- `project/reliability/smoke_data.py`
- `project/research/agent_io/proposal_to_experiment.py`
- `project/research/blueprint_compilation.py`
- `project/research/compile_strategy_blueprints.py`
- `project/research/discovery.py`
- `project/research/finalize_experiment.py`
- `project/research/multiplicity.py`
- `project/research/phase2_search_engine.py`
- `project/research/search/bridge_adapter.py`
- `project/research/services/candidate_discovery_scoring.py`
- `project/research/services/candidate_discovery_service.py`
- `project/research/services/pathing.py`
- `project/research/services/regime_shakeout_service.py`
- `project/research/services/reporting_service.py`
- `project/research/services/run_comparison_service.py`
- `project/research/validation/evidence_bundle.py`
- `project/strategy/dsl/schema.py`
- `project/strategy/models/executable_strategy_spec.py`
- `project/tests/artifacts/test_artifact_catalog_paths.py`
- `project/tests/contracts/test_phase5_contracts.py`
- `project/tests/contracts/test_promotion_artifacts_schema.py`
- `project/tests/research/services/test_candidate_discovery_service.py`
- `project/tests/research/services/test_regime_shakeout_service.py`
- `project/tests/research/services/test_reporting_service.py`
- `project/tests/research/services/test_run_comparison_service.py`
- `project/tests/research/test_bridge_adapter.py`
- `runresults.md`
- `implementation_report.md`

Verification-only local artifacts created for the bounded experiment:

- `/home/irene/Edge/.tmp/phase2_surface_smoke_proposal.yaml`
- `/home/irene/Edge/.tmp/phase2_surface_smoke_data/...`

## 3. Plan Deviations and Why They Were Necessary

- The post-implementation bounded experiment used a repo-local smoke-data scaffold rooted at `/home/irene/Edge/.tmp/phase2_surface_smoke_data` and remapped it onto a proposal-issued run ID. This was the minimum bounded way to inspect canonical phase-2, promotion, and blueprint outputs without running a full live-data proposal execution.
- The bounded run did not generate promoted candidates, so it produced `0` blueprints and `0` executable specs. Because of that, run-scoped typed-engine execution could not be exercised from this bounded run’s own artifacts. Phase-5 behavior was verified through the required smoke/unit/contract tests instead.
- During full-suite verification, `project/tests/test_architectural_integrity.py::test_preferred_root_surfaces_replace_cross_domain_deep_imports` failed once because a few modules imported `project.artifacts.catalog` directly. I corrected those imports to use the package root surface (`project.artifacts`) and re-ran the full test suite successfully. This was a minimum correction required by code verification.

## 4. Verification Commands Run

```bash
.venv/bin/pytest project/tests/research/test_bridge_adapter.py -q
.venv/bin/pytest project/tests/contracts/test_phase5_contracts.py -q
.venv/bin/pytest project/tests/research/services/test_reporting_service.py -q
.venv/bin/pytest project/tests/artifacts/test_artifact_catalog_paths.py -q
.venv/bin/pytest project/tests/pipelines/test_pipeline_discovery_mode.py -q
.venv/bin/pytest project/tests/research/services/test_run_comparison_service.py -q
.venv/bin/pytest project/tests/research/services/test_regime_shakeout_service.py -q
.venv/bin/pytest project/tests/research/services/test_candidate_discovery_service.py -q
.venv/bin/pytest project/tests/research/agent_io -q
.venv/bin/pytest project/tests/pipelines/test_pipeline_discovery_mode.py project/tests/pipelines/test_planner_dependencies.py -q
.venv/bin/pytest project/tests/contracts -q
.venv/bin/pytest project/tests/strategy -q
.venv/bin/pytest project/tests/research -q
.venv/bin/python -m project.spec_validation.cli
.venv/bin/python project/scripts/ontology_consistency_audit.py --output docs/generated/ontology_audit.json --check
.venv/bin/python project/scripts/detector_coverage_audit.py --md-out docs/generated/detector_coverage.md --json-out docs/generated/detector_coverage.json --check
.venv/bin/pytest project/tests/architecture -q
.venv/bin/pytest project/tests/smoke/test_research_smoke.py -q
.venv/bin/pytest project/tests/smoke/test_promotion_smoke.py -q
.venv/bin/pytest project/tests/smoke/test_engine_smoke.py -q
.venv/bin/python -m compileall -q project project/tests
.venv/bin/pytest project/tests/test_architectural_integrity.py::test_preferred_root_surfaces_replace_cross_domain_deep_imports -q
.venv/bin/pytest -q --maxfail=25 project/tests
.venv/bin/python -m project.pipelines.run_all --help
.venv/bin/python -m project.research.agent_io.execute_proposal --proposal /home/irene/Edge/.tmp/phase2_surface_smoke_proposal.yaml --run_id phase2_surface_smoke --registry_root project/configs/registries --out_dir data/artifacts/experiments/smoke_program/proposals/phase2_surface_smoke --plan_only 1
.venv/bin/python -m project.research.agent_io.issue_proposal --proposal /home/irene/Edge/.tmp/phase2_surface_smoke_proposal.yaml --registry_root project/configs/registries --plan_only 1
.venv/bin/python - <<'PY'
import json
from pathlib import Path
from project.engine.runner import run_engine_for_specs
from project.research.services.run_comparison_service import compare_run_ids
from project.strategy.models.executable_strategy_spec import ExecutableStrategySpec

root = Path('/home/irene/Edge/.tmp/phase2_surface_smoke_data')
run_id = 'smoke_program_20260329T122054Z_1988fdc9e1'
blueprint_dir = root / 'reports' / 'strategy_blueprints' / run_id
spec_index = blueprint_dir / 'executable_strategy_spec_index.json'
summary = {'run_id': run_id, 'root': str(root), 'spec_index_exists': spec_index.exists()}
if spec_index.exists():
    index_payload = json.loads(spec_index.read_text())
    specs = index_payload.get('executable_strategy_specs', [])
    summary['spec_count'] = len(specs)
    summary['spec_paths'] = [item.get('path') for item in specs]
    if specs:
        spec_path = root / specs[0]['path']
        spec = ExecutableStrategySpec.model_validate_json(spec_path.read_text())
        engine = run_engine_for_specs([spec], data_root=str(root), run_id=f'{run_id}_typed_engine_check', cost_model='basic')
        summary['engine'] = {
            'strategy_count': len(engine.get('strategies', {})),
            'metadata_keys': sorted(engine.get('metrics', {}).get('strategy_metadata', {}).keys()),
        }
summary['comparison'] = compare_run_ids(data_root=root, baseline_run_id=run_id, candidate_run_id=run_id)
print(json.dumps(summary, indent=2, default=str))
PY
```

## 5. Verification Results

- All targeted phase-level test groups passed.
- `project.spec_validation.cli` passed.
- `ontology_consistency_audit.py --check` passed and left `docs/generated/ontology_audit.json` current.
- `detector_coverage_audit.py --check` passed and left `docs/generated/detector_coverage.md` and `docs/generated/detector_coverage.json` current.
- `compileall` passed.
- Full repository suite passed: `.venv/bin/pytest -q --maxfail=25 project/tests`
- `run_all --help` passed and exposed canonical `--promotion_profile` alongside legacy compatibility flags.
- `execute_proposal --plan_only` passed and emitted a plan with `discovery_paths=search_engine:True legacy_conditional:False`, plus `phase2_search_engine` as the sole authoritative discovery stage.
- `issue_proposal --plan_only` passed and produced proposal-issued run ID `smoke_program_20260329T122054Z_1988fdc9e1`.
- Bounded experiment artifact inspection passed for canonical phase-2 pathing, distinct lineage IDs, and downstream promotion/comparison surfaces.
- Bounded typed-engine inspection reported `spec_count: 0`, so no run-scoped executable spec or engine run was available from that experiment.

Warnings observed but not in scope for this plan:

- Existing deprecation warnings around `compute_pnl_components`
- Existing pandas `FutureWarning` emissions in unrelated feature/research tests

## 6. Remaining Known Limitations

- The bounded experiment produced zero promoted candidates, which meant zero blueprints and zero executable strategy specs for that run.
- Because of the zero-spec outcome, the post-implementation experiment could not prove run-scoped typed-engine execution from proposal-issued artifacts, even though the typed path itself passed smoke/unit/contract verification.
- The bounded smoke fixture used for artifact inspection does not currently materialize canonical event/regime columns on the phase-2 parquet; those semantics were confirmed downstream in promotion outputs and across the test suite instead.
- Historical compatibility readers remain at boundaries for legacy artifact readability by design.

## 7. Ready-for-Experiment Statement

Ready for experiment: yes, with one bounded caveat. The repository now passes the required verification suite and the bounded run verified canonical phase-2 storage, explicit lineage, canonical proposal control fields, and downstream registry-backed semantics. The next experiment should be chosen to guarantee at least one promoted candidate so the typed blueprint-to-engine path is exercised on run-scoped artifacts, not only by smoke tests.
