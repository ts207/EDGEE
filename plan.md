# Goal of the remediation

The end state is a single-path research and execution architecture in which phase-2 discovery is scheduled and persisted through one authoritative control path, candidate artifacts live under one canonical storage contract, lineage is explicit and non-collapsed across `Proposal -> Experiment -> Hypothesis -> Candidate -> Blueprint -> Engine run`, ontology semantics are read from the compiled registry and regime-routing surfaces instead of string heuristics, and downstream promotion, blueprint compilation, comparison, and engine execution consume typed contracts and stable artifact locations without fallback joins, parallel legacy execution, or silent semantic aliases in the control plane.

## Phase 1. Collapse phase-2 control and storage to one authoritative surface

Objective:
Make `phase2_search_engine` the only first-class phase-2 discovery stage and make all phase-2 readers/writers use one canonical directory contract.

Exact files/modules to modify:
- `project/pipelines/stages/research.py`
- `project/research/phase2_search_engine.py`
- `project/research/services/pathing.py`
- `project/artifacts/catalog.py`
- `project/research/services/reporting_service.py`
- `project/research/services/run_comparison_service.py`
- `project/research/compile_strategy_blueprints.py`
- `project/pipelines/research/phase2_candidate_discovery.py`
- `project/tests/smoke/test_research_smoke.py`
- `project/tests/contracts/`
- `project/tests/research/services/`
- `project/tests/artifacts/`

Exact contracts/behaviors to change:
- Stop scheduling `phase2_conditional_hypotheses__*` as a peer discovery path from [`/home/irene/Edge/project/pipelines/stages/research.py`](/home/irene/Edge/project/pipelines/stages/research.py). The pipeline must plan exactly one authoritative phase-2 discovery stage per run: `phase2_search_engine`.
- Keep [`/home/irene/Edge/project/pipelines/research/phase2_candidate_discovery.py`](/home/irene/Edge/project/pipelines/research/phase2_candidate_discovery.py) only as an explicit compatibility entrypoint, not a default scheduled stage. It may delegate inward for one release window if needed, but it must not produce a competing canonical candidate surface.
- Introduce one canonical path helper for all phase-2 outputs under `data/reports/phase2/<run_id>/...` and route all writers and readers through it. Eliminate hardcoded disagreement between per-event trees, `search_engine/`, and artifact catalog assumptions.
- Define one canonical location for:
  `phase2_candidates.parquet`
  `phase2_diagnostics.json`
  hypothesis audit artifacts
  any run-level combined candidate surface used by promotion/blueprint/comparison
- Restrict compatibility reads for historical runs to read-boundary helpers only. No business logic module may scan multiple roots and merge them opportunistically.

Why this phase comes before the next one:
Identity repair is not trustworthy until every downstream consumer is reading the same candidate surface. If storage and scheduling remain split, distinct-ID work will still operate on inconsistent inputs.

Risks and rollback notes:
- Hidden consumers may still expect `phase2_conditional_hypotheses__*` stage names or `search_engine/` diagnostics paths.
- Historical run readers may break if path fallback is removed too aggressively.
- Rollback is limited to restoring boundary-only compatibility readers and wrappers. Do not reintroduce dual canonical scheduling.

Acceptance criteria:
- `build_research_stages()` emits `phase2_search_engine` as the sole authoritative phase-2 discovery stage for experiment-backed and non-experiment-backed runs.
- No default run manifest contains `phase2_conditional_hypotheses__*` as an active discovery stage.
- `project/artifacts/catalog.py`, reporting, comparison, and blueprint compilation all resolve phase-2 artifacts through shared path helpers only.
- A narrow research run writes one reconciled phase-2 artifact tree, and promotion/blueprint/comparison read exactly that tree.

Verification commands:
```bash
.venv/bin/pytest project/tests/smoke/test_research_smoke.py -q
.venv/bin/pytest project/tests/contracts -q
.venv/bin/pytest project/tests/research/services -q
.venv/bin/pytest project/tests/artifacts -q
.venv/bin/python -m project.pipelines.run_all --help
.venv/bin/python -m project.research.agent_io.execute_proposal \
  --proposal /abs/path/to/proposal.yaml \
  --run_id phase2_surface_smoke \
  --registry_root project/configs/registries \
  --out_dir data/artifacts/experiments/<program_id>/proposals/phase2_surface_smoke \
  --plan_only 1
```

Artifact expectations:
- Regenerated run plan artifacts for a narrow proposal-issued run
- Canonical phase-2 report tree under `data/reports/phase2/<run_id>/...`
- Updated tests covering stage planning and phase-2 artifact resolution

## Phase 2. Normalize lineage and make candidate identity distinct

Objective:
Make `candidate_id` a real entity distinct from `hypothesis_id`, propagate explicit foreign keys through blueprint packaging, and remove fallback joins that blur research attribution.

Exact files/modules to modify:
- `project/research/discovery.py`
- `project/research/search/bridge_adapter.py`
- `project/research/finalize_experiment.py`
- `project/research/blueprint_compilation.py`
- `project/research/compile_strategy_blueprints.py`
- `project/strategy/models/executable_strategy_spec.py`
- `project/contracts/schemas.py`
- `project/research/candidate_schema.py`
- `project/tests/research/`
- `project/tests/strategy/`
- `project/tests/contracts/`

Exact contracts/behaviors to change:
- Emit both `hypothesis_id` and a distinct `candidate_id` on every candidate-carrying artifact. `candidate_id` must be created at the selection/evaluation layer, not copied from `hypothesis_id`.
- Remove logic in [`/home/irene/Edge/project/research/search/bridge_adapter.py`](/home/irene/Edge/project/research/search/bridge_adapter.py) and [`/home/irene/Edge/project/research/discovery.py`](/home/irene/Edge/project/research/discovery.py) that aliases `candidate_id` to `hypothesis_id`.
- Replace [`/home/irene/Edge/project/research/finalize_experiment.py`](/home/irene/Edge/project/research/finalize_experiment.py) fallback matching with explicit joins on the proper lineage keys. Historical compatibility handling, if retained, must be isolated in a migration adapter and marked as migrated provenance.
- Ensure blueprint and executable strategy specs carry `proposal_id` when available, `run_id`, `hypothesis_id`, `candidate_id`, `blueprint_id`, and canonical event/regime lineage without reconstructing IDs downstream.
- Update schema contracts so candidate, promotion, and blueprint artifacts fail validation if required lineage keys are absent or collapsed.

Why this phase comes before the next one:
Ontology cleanup and packaging reliability depend on stable object identity. If `candidate_id` still collapses onto `hypothesis_id`, there is no clean unit for promotion, deduplication, export, or strategy packaging.

Risks and rollback notes:
- Historical tested ledgers and promotion artifacts may need a read-only migration path.
- Deduplication and clustering code may implicitly assume one ID.
- Rollback is limited to compatibility readers for old artifacts; new writes must never resume collapsed IDs.

Acceptance criteria:
- Fresh phase-2 outputs always include both `hypothesis_id` and `candidate_id`, and they differ whenever multiple evaluation/select/export views of one hypothesis exist.
- Finalization no longer scans candidate rows with heuristic fallback across the two IDs for current-format artifacts.
- Blueprint artifacts and executable specs carry explicit upstream lineage fields and validate against updated contracts.
- Contract tests fail if a current-format candidate artifact omits one of the required lineage keys.

Verification commands:
```bash
.venv/bin/pytest project/tests/research -q
.venv/bin/pytest project/tests/strategy -q
.venv/bin/pytest project/tests/contracts -q
.venv/bin/python -m project.research.agent_io.issue_proposal \
  --proposal /abs/path/to/proposal.yaml \
  --registry_root project/configs/registries \
  --plan_only 1
```

Artifact expectations:
- Updated candidate, evaluation, promotion, and blueprint schemas
- Regenerated narrow-run experiment artifacts showing distinct IDs through blueprint outputs
- Updated tested-ledger or migration-adapter coverage for historical artifact reads

## Phase 3. Remove ontology leakage from consumers and make compiled registry semantics authoritative

Objective:
Stop deriving regime/family meaning from strings and route semantic interpretation through the compiled domain registry and regime-routing surfaces.

Exact files/modules to modify:
- `project/domain/registry_loader.py`
- `project/domain/models.py`
- `project/research/search/bridge_adapter.py`
- `project/research/services/candidate_discovery_scoring.py`
- `project/research/gating.py`
- `project/research/multiplicity.py`
- `project/research/blueprint_compilation.py`
- `project/strategy/models/executable_strategy_spec.py`
- `project/research/regime_routing.py`
- `project/tests/architecture/`
- `project/tests/research/`
- `project/tests/spec_validation/`

Exact contracts/behaviors to change:
- Treat `canonical_regime` as the canonical research grouping at consumer sites. `canonical_family` may remain only as a temporary write-through alias where a contract still requires it.
- Remove heuristic derivations such as `event_type.split("_")[0]` and trigger-key string parsing when registry-backed event metadata is available.
- Ensure bridge adaptation, scoring, gating, multiplicity grouping, and blueprint lineage obtain semantic fields from `get_domain_registry()` or `regime_routing`, not ad hoc string logic.
- Demote `legacy_family` use in [`/home/irene/Edge/project/domain/registry_loader.py`](/home/irene/Edge/project/domain/registry_loader.py) to compatibility-only loading behavior and prohibit new downstream consumption of `legacy_family` as a decision key.
- Preserve temporary alias columns only at boundaries where required for backward compatibility, and explicitly mark them as non-canonical.

Why this phase comes before the next one:
Service consolidation and engine-boundary cleanup need stable semantic contracts. If downstream code still reconstructs regime meaning opportunistically, later cleanup will preserve the wrong ontology.

Risks and rollback notes:
- Some reports or selection rules may currently depend on familiar but incorrect family labels.
- Search and promotion output counts may shift once grouping keys become registry-backed.
- Rollback is limited to alias columns at report boundaries. Do not restore heuristic semantic derivation inside discovery or promotion logic.

Acceptance criteria:
- No research-critical consumer derives canonical grouping from `event_type.split(...)` or equivalent string heuristics.
- Candidate, promotion, and blueprint lineage surfaces resolve canonical event/regime metadata from compiled registry data.
- Tests cover at least one event whose canonical regime differs from its legacy-family-style tokenization and prove correct propagation.

Verification commands:
```bash
.venv/bin/python -m project.spec_validation.cli
.venv/bin/python project/scripts/ontology_consistency_audit.py --output docs/generated/ontology_audit.json --check
.venv/bin/pytest project/tests/architecture -q
.venv/bin/pytest project/tests/research -q
```

Artifact expectations:
- Regenerated ontology audit outputs
- Updated lineage/report fixtures that previously encoded heuristic family values
- Updated architecture/spec-validation tests for canonical regime propagation

## Phase 4. Consolidate research workflow authority and isolate compatibility aliases to boundaries

Objective:
Make `project.research.services` and typed proposal/experiment objects the only workflow authority, while demoting proposal aliases and legacy wrappers to policy-free boundary shells.

Exact files/modules to modify:
- `project/research/agent_io/proposal_schema.py`
- `project/research/agent_io/proposal_to_experiment.py`
- `project/research/agent_io/execute_proposal.py`
- `project/research/agent_io/issue_proposal.py`
- `project/pipelines/stages/research.py`
- `project/research/services/candidate_discovery_service.py`
- `project/research/services/promotion_service.py`
- `project/research/phase2_search_engine.py`
- `project/eval/multiplicity.py`
- `project/tests/research/agent_io/`
- `project/tests/pipelines/`

Exact contracts/behaviors to change:
- Stop using `candidate_promotion_profile` as a control-plane semantic source. Proposal/experiment `promotion_profile` must drive promotion behavior end to end.
- Restrict proposal compatibility aliases `objective` and `promotion_mode` to explicit ingress normalization only, with no re-emission into canonical configs or overrides.
- Ensure pipeline wrappers remain argv-translation shells and do not carry policy that duplicates service-layer workflow logic.
- Treat `project.eval` as computation support only. Workflow orchestration and evaluation policy must remain under `project.research.services`.

Why this phase comes before the next one:
The engine boundary should consume already-clean research contracts. Control-plane alias cleanup prevents the engine-alignment phase from inheriting stale workflow semantics.

Risks and rollback notes:
- External proposal producers may still emit legacy fields.
- Some scripts may import legacy wrappers directly.
- Rollback is limited to ingress alias normalization for one release window. Do not keep alias names as durable internal control-plane knobs.

Acceptance criteria:
- Canonical experiment configs and run-all overrides are driven by `objective_name` and `promotion_profile` only.
- Wrapper modules remain thin and carry no duplicate evaluation/promotion policy.
- Tests prove that legacy proposal fields are accepted only at ingress and are normalized away before internal planning artifacts are written.

Verification commands:
```bash
.venv/bin/pytest project/tests/research/agent_io -q
.venv/bin/pytest project/tests/pipelines -q
.venv/bin/pytest project/tests/research/services -q
```

Artifact expectations:
- Updated proposal/experiment fixtures
- Updated stage-planning and service-layer tests
- Regenerated example proposal-derived configs if checked into docs or fixtures

## Phase 5. Align blueprint packaging and engine entry around typed contracts

Objective:
Make blueprint and executable-strategy contracts the explicit bridge into engine execution, while preserving runtime behavior and avoiding a second semantic authority in the engine.

Exact files/modules to modify:
- `project/research/compile_strategy_blueprints.py`
- `project/research/blueprint_compilation.py`
- `project/strategy/dsl/schema.py`
- `project/strategy/models/executable_strategy_spec.py`
- `project/engine/runner.py`
- `project/tests/strategy/`
- `project/tests/smoke/test_engine_smoke.py`
- `project/tests/contracts/`

Exact contracts/behaviors to change:
- Make blueprint and `ExecutableStrategySpec` lineage complete and canonical before engine invocation.
- Add or harden an engine-facing typed invocation path so engine execution can consume blueprint/spec payloads without reinterpreting research identity from loose params. Existing strategy-name entrypoints may remain temporarily as wrappers, but they must delegate to the typed path.
- Ensure engine metadata emission preserves `run_id`, `candidate_id`, `blueprint_id`, `canonical_event_type`, `canonical_regime`, and `routing_profile_id` without recomputation.
- Do not make engine changes that re-score, re-validate, or reinterpret research evidence.

Why this phase comes last:
The engine boundary should be updated only after phase-2 surfaces, lineage, ontology, and workflow authority are already stable. Otherwise the typed engine contract will encode compatibility debt.

Risks and rollback notes:
- DSL and non-DSL strategy execution currently share runtime plumbing.
- Engine smoke tests may depend on legacy `strategies` plus `params` invocation patterns.
- Rollback is limited to retaining legacy entry wrappers. The typed contract path must remain the authoritative implementation.

Acceptance criteria:
- Engine execution can be invoked through a typed blueprint/spec path without losing lineage.
- Engine artifacts carry canonical lineage fields with no downstream recomputation.
- Legacy engine entrypoints, if retained, are wrappers around the typed path and contain no independent semantic policy.

Verification commands:
```bash
.venv/bin/pytest project/tests/strategy -q
.venv/bin/pytest project/tests/contracts -q
.venv/bin/pytest project/tests/smoke/test_engine_smoke.py -q
.venv/bin/python -m compileall -q project project/tests
```

Artifact expectations:
- Updated blueprint and executable-strategy fixtures
- Regenerated engine smoke artifacts for a narrow typed-contract run
- Updated contract tests for engine metadata fields

## Acceptance criteria

Concrete pass/fail criteria per phase:
- Phase 1 passes only if one discovery stage and one phase-2 artifact tree exist for new runs, and all downstream readers resolve that same tree through shared path helpers.
- Phase 2 passes only if current-format artifacts always carry distinct lineage IDs, fallback joins are removed from current-format flows, and schema validation enforces those fields.
- Phase 3 passes only if research-critical consumers use registry-backed semantics instead of string heuristics and ontology audits remain green.
- Phase 4 passes only if internal planning artifacts use canonical proposal/experiment fields only and wrappers stay policy-free.
- Phase 5 passes only if engine execution accepts typed contracts as the authoritative path and emitted engine artifacts preserve lineage without recomputation.

Explicit definition of done for the full effort:
- A proposal-issued narrow run executes through one phase-2 discovery path, one canonical phase-2 storage layout, explicit lineage from hypothesis through blueprint, registry-backed canonical semantics, service-owned workflow policy, and typed engine execution, with all required tests and audits passing and no current-format artifact reader depending on semantic fallback across duplicate paths or collapsed IDs.

## Verification commands

Compile/test/audit/smoke commands to run after each phase:
```bash
# After Phase 1
.venv/bin/pytest project/tests/smoke/test_research_smoke.py -q
.venv/bin/pytest project/tests/contracts -q
.venv/bin/pytest project/tests/research/services -q
.venv/bin/pytest project/tests/artifacts -q

# After Phase 2
.venv/bin/pytest project/tests/research -q
.venv/bin/pytest project/tests/strategy -q
.venv/bin/pytest project/tests/contracts -q

# After Phase 3
.venv/bin/python -m project.spec_validation.cli
.venv/bin/python project/scripts/ontology_consistency_audit.py --output docs/generated/ontology_audit.json --check
.venv/bin/pytest project/tests/architecture -q
.venv/bin/pytest project/tests/research -q

# After Phase 4
.venv/bin/pytest project/tests/research/agent_io -q
.venv/bin/pytest project/tests/pipelines -q
.venv/bin/pytest project/tests/research/services -q

# After Phase 5
.venv/bin/pytest project/tests/strategy -q
.venv/bin/pytest project/tests/contracts -q
.venv/bin/pytest project/tests/smoke/test_engine_smoke.py -q
.venv/bin/python -m compileall -q project project/tests
```

Final full verification block:
```bash
.venv/bin/python -m compileall -q project project/tests
.venv/bin/python -m project.spec_validation.cli
.venv/bin/python project/scripts/ontology_consistency_audit.py --output docs/generated/ontology_audit.json --check
.venv/bin/python project/scripts/detector_coverage_audit.py --md-out docs/generated/detector_coverage.md --json-out docs/generated/detector_coverage.json --check
.venv/bin/pytest project/tests/architecture -q
.venv/bin/pytest project/tests/smoke/test_research_smoke.py -q
.venv/bin/pytest project/tests/smoke/test_promotion_smoke.py -q
.venv/bin/pytest project/tests/smoke/test_engine_smoke.py -q
.venv/bin/pytest project/tests/contracts -q
.venv/bin/pytest project/tests/research -q
.venv/bin/pytest project/tests/strategy -q
.venv/bin/pytest -q --maxfail=25 project/tests
.venv/bin/python -m project.research.agent_io.issue_proposal \
  --proposal /abs/path/to/proposal.yaml \
  --registry_root project/configs/registries \
  --plan_only 1
```

## Artifact expectations

The implementation series must update or regenerate:
- `plan.md`
- Any touched schema fixtures and golden artifacts under `project/tests/`
- Proposal/experiment fixtures used by `project/research/agent_io` tests
- Canonical phase-2 report artifacts for one narrow verification run
- Blueprint/executable-strategy fixtures and engine smoke artifacts for one narrow verification run
- `docs/generated/ontology_audit.json`
- `docs/generated/detector_coverage.md`
- `docs/generated/detector_coverage.json`
- `runresults.md` after the bounded post-implementation experiment

## Guardrails

What must not be changed:
- Do not change detector math, strategy alpha logic, cost formulas, or promotion thresholds unless required to satisfy the architectural contracts above.
- Do not widen research scope, add new event families, or redesign the ontology schema beyond what is necessary to make canonical surfaces authoritative.
- Do not remove historical artifact readability outright; isolate legacy support to read-boundary compatibility adapters only.

What shortcuts are forbidden:
- No reintroducing dual canonical phase-2 scheduling to preserve old outputs.
- No continuing `candidate_id == hypothesis_id` for newly written artifacts.
- No semantic derivation from `event_type` token splitting when registry-backed metadata exists.
- No hidden fallback scans across multiple phase-2 roots in business logic.
- No engine-side reconstruction of research lineage from loose report rows.

Compatibility behavior allowed temporarily vs not allowed:
- Allowed temporarily: boundary-only wrappers, ingress-only proposal alias normalization, read-only adapters for historical artifact paths, write-through alias columns where required by existing external readers.
- Not allowed temporarily: competing canonical discovery paths, new writes to deprecated phase-2 roots, new current-format artifacts missing canonical lineage keys, or new consumer logic keyed on `legacy_family`.

## Post-implementation bounded experiment

Hypothesis to test:
- After the patch series, one narrow proposal-issued run will produce a single internally consistent candidate surface such that discovery, promotion, blueprint compilation, comparison, and engine smoke execution all reference the same lineage chain and semantic metadata without fallback reconciliation.

Exact run scope:
- One program ID
- One symbol
- One timeframe
- One event family narrowed to a single explicit event type
- One template family
- Horizons limited to two values
- Directions limited to `long` and `short`
- One entry lag
- One proposal-issued run ID dedicated to this experiment

Exact artifacts/logs/manifests/reports to inspect:
- `data/runs/<run_id>/run_manifest.json`
- canonical phase-2 outputs under `data/reports/phase2/<run_id>/...`
- experiment artifacts under `data/artifacts/experiments/<program_id>/<run_id>/...`
- promotion outputs under `data/reports/promotions/<run_id>/...`
- blueprint outputs under `data/reports/strategy_blueprints/<run_id>/...`
- engine artifacts under `data/runs/<run_id>/engine/...`
- any comparison diagnostics emitted for the run

Exact content to save into `runresults.md`:
- proposal path, program ID, run ID, symbol, timeframe, event type, templates, horizons, directions, entry lag
- the canonical phase-2 artifact paths used by each downstream stage
- whether `hypothesis_id`, `candidate_id`, and `blueprint_id` were all present and distinct where required
- whether canonical event/regime lineage matched the compiled registry for the tested event
- candidate counts at discovery, promotion, blueprint, and engine-input boundaries
- explicit pass/fail result for each phase acceptance criterion as exercised by the run
- any residual compatibility adapter hits observed during the run
- the single next action, chosen from `exploit`, `explore`, `repair`, `hold`, or `stop`
