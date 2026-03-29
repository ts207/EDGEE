# A. Executive assessment

This repository is a serious research platform, not a toy, but it is not in the target state and it is not yet trustworthy as a capital-allocation system. The strongest parts are real: compiled registry loading, stage contracts, orchestration, proposal-driven research, smoke workflows, and a large passing test tree. The main problem is semantic split-brain rather than obvious breakage. Discovery still runs canonical and legacy paths in parallel, `candidate_id` still collapses onto `hypothesis_id`, event/regime meaning still leaks through mixed `canonical_regime` / `canonical_family` / `legacy_family` usage, and storage readers/writers disagree on phase-2 locations. That combination can keep tests green while making lineage, comparison, and promotion conclusions on compatibility-shaped data.

# B. What is genuinely strong

- The repository has real scale and a broad validation surface. Counts observed from the working tree: `1219` Python files, `346` YAML files, `427` test files, and `2407` generated docs/artifact files under `docs/generated`, `data/reports`, `data/artifacts`, and `artifacts`.
- The compiled registry is real code authority, not README theater. `project/domain/compiled_registry.py` and `project/domain/registry_loader.py` load the unified event registry plus state/template metadata into `project/domain/models.py`.
- The regime routing layer is coherent. `project/research/regime_routing.py` validates `spec/events/regime_routing.yaml`; the validation probe returned `is_valid=true`, `routing_rows=14`, `executable_regimes=14`.
- The orchestration stack is substantial. `project/pipelines/run_all.py` is backed by `project/pipelines/pipeline_planning.py`, `project/pipelines/effective_config.py`, and `project/contracts/pipeline_registry.py` rather than ad hoc shell glue.
- Proposal-driven research is materially implemented. `project/research/agent_io/proposal_schema.py`, `proposal_to_experiment.py`, `execute_proposal.py`, `issue_proposal.py`, and `closed_loop.py` form an end-to-end proposal surface.
- Artifact contracts and schema checks exist in code. `project/contracts/pipeline_registry.py`, `project/contracts/schemas.py`, `project/engine/schema.py`, and the contract tests are active and nontrivial.
- The core test tree is large and currently healthy. `pytest -q --maxfail=25 project/tests` passed locally, as did the focused architecture and smoke suites.
- The live runtime is scaffolded with meaningful controls. `project/live/runner.py`, `project/live/oms.py`, `project/live/state.py`, `project/live/kill_switch.py`, and `project/scripts/run_live_engine.py` include kill switches, sync, reconciliation, telemetry, and environment validation.

# C. What is misleading, stale, or broken

- The repository still runs dual discovery architectures. `project/pipelines/stages/research.py` appends legacy per-event `phase2_conditional_hypotheses__...` stages and also appends `phase2_search_engine`. The same file says “we run both and compare first.” `project/research/phase2_search_engine.py` also states it runs in parallel with the older candidate-discovery stage. That contradicts the target-state requirement that the legacy conditional path be compatibility debt, not a first-class runtime path.
- Identity remains collapsed. `project/research/search/bridge_adapter.py:84` sets `candidate_id = filtered["hypothesis_id"]`. `project/research/discovery.py:498` emits `"candidate_id": h.hypothesis_id()`. `project/research/finalize_experiment.py:76-108` explicitly falls back across `hypothesis_id` and `candidate_id`. The target-state identity chain Proposal -> Experiment -> Hypothesis -> Candidate -> Blueprint -> Engine run is not preserved.
- Phase-2 storage paths are not singular. `project/research/services/pathing.py:8-17` writes event discovery under `data/reports/phase2/<run>/<EVENT>/<TF>/`. `project/research/phase2_search_engine.py` writes under `data/reports/phase2/<run>/search_engine/`. `project/artifacts/catalog.py:66-71` expects `data/reports/phase2/<run>/<event>/phase2_candidates.{parquet,csv}`. `project/research/services/run_comparison_service.py:30-49` expects diagnostics under `search_engine`. Readers and writers are talking about different trees.
- Test-tree documentation is misleading. `pytest.ini:4` sets `testpaths = project/tests`, but `docs/02_REPOSITORY_MAP.md:10` still presents `tests/` as the top-level test home. The top-level `tests/` tree exists and passes when invoked directly, but default pytest and CI entrypoints are centered on `project/tests`.
- Generated-doc truthfulness is unstable. `README.md` presents `docs/generated/` as authoritative, but `project/scripts/build_system_map.py --check` initially failed because `docs/generated/system_map.md` and `.json` were missing from the checkout, and those files are not tracked. `project/scripts/build_architecture_metrics.py --check` failed on coupling drift, proving the generated metrics can disagree with source at HEAD.
- Proposal compatibility aliases are still active, not isolated. `project/research/agent_io/proposal_schema.py:160-166` still accepts legacy `objective` and `promotion_mode`. `project/research/agent_io/proposal_to_experiment.py:96-109` still emits the legacy `candidate_promotion_profile` override into `run_all`.
- The engine entry contract is still strategy-name/params based. `project/engine/runner.py:229-241` defines `run_engine(run_id, symbols, strategies, params, ...)`, not a typed `ExecutableStrategySpec`/Blueprint-first contract, even though DSL support exists downstream.
- The live runtime is configuration-gated into monitor-only mode. `project/configs/live_paper.yaml` and `project/configs/live_production.yaml` both set `runtime_mode: monitor_only`, so the repo contains live scaffolding but not an enabled trading workflow.

# D. Root-cause issue clusters

- Compatibility debt is still in the control plane, not at boundaries.
  Files: `project/pipelines/stages/research.py`, `project/research/phase2_search_engine.py`, `project/research/discovery.py`, `project/research/agent_io/proposal_schema.py`, `project/research/agent_io/proposal_to_experiment.py`.
  Effect: legacy and target-state semantics coexist inside authoritative execution paths instead of being translated at ingress/egress.

- Storage contracts are defined, but storage locations are not singular.
  Files: `project/research/services/pathing.py`, `project/artifacts/catalog.py`, `project/research/services/reporting_service.py`, `project/research/services/run_comparison_service.py`, `project/research/compile_strategy_blueprints.py`.
  Effect: different services can inspect different candidate surfaces for the same run and still appear internally consistent.

- Identity lineage is under-specified after hypothesis generation.
  Files: `project/research/search/bridge_adapter.py`, `project/research/discovery.py`, `project/research/finalize_experiment.py`, `project/research/blueprint_compilation.py`, `project/strategy/models/executable_strategy_spec.py`.
  Effect: “claim evaluated,” “candidate selected,” and “blueprint exported” are not cleanly separable units.

- The ontology is compiled cleanly but consumed inconsistently.
  Files: `project/domain/registry_loader.py`, `project/research/services/candidate_discovery_scoring.py`, `project/research/search/bridge_adapter.py`, `project/research/gating.py`, `project/research/regime_routing.py`.
  Effect: canonical registry concepts exist, but some downstream code still reconstructs family/regime labels from string heuristics.

- CI/generation truth depends on local generated state.
  Files: `project/scripts/build_system_map.py`, `project/scripts/build_architecture_metrics.py`, `.github/workflows/tier1.yml`, `docs/generated/*`.
  Effect: clean-clone structural checks are less trustworthy than the workflows imply.

- Production-readiness claims outrun empirical proof.
  Files: `project/live/runner.py`, `project/live/oms.py`, `project/live/state.py`, `project/scripts/run_live_engine.py`, `project/configs/live_*.yaml`.
  Effect: the live system has architecture, but not evidence of a full trading-grade workflow exercised end to end.

# E. Architecture map

- Repository inventory and layout.
  Top-level implementation lives in `project/`.
  Spec and ontology surfaces live in `spec/`.
  Runtime outputs live in `data/`.
  Checked-in and local golden/synthetic material also lives in top-level `artifacts/`.
  Active tests are in `project/tests/`; a secondary top-level `tests/` tree still exists.
  CI and automation live in `.github/workflows/`.
  Deploy/systemd material lives in `deploy/`.
  Hand-authored docs live in `docs/`; generated docs live in `docs/generated/`.

- Split-brain layout is a real structural property.
  `project/tests/` vs `tests/`
  `spec/` vs `project/configs/registries/`
  `data/artifacts/` vs top-level `artifacts/`
  per-event phase-2 outputs vs `search_engine` outputs
  `canonical_regime` vs `canonical_family` vs `legacy_family`

- True execution/control surfaces.
  Main CLIs are declared in `pyproject.toml` under `[project.scripts]`, including `edge-run-all`, `edge-live-engine`, `edge-phase2-discovery`, `edge-promote`, and `edge-smoke`.
  The main orchestrator is `project/pipelines/run_all.py`.
  Planning authority lives in `project/pipelines/pipeline_planning.py`, `project/pipelines/planner.py`, and `project/pipelines/effective_config.py`.
  Stage-family and artifact-contract authority lives in `project/contracts/pipeline_registry.py`.
  Proposal translation and bounded research issuance live in `project/research/agent_io/*`.
  Discovery/promotion/comparison/reporting services live in `project/research/services/*`.
  Engine execution authority is `project/engine/runner.py`.
  Strategy packaging is split across `project/research/compile_strategy_blueprints.py`, `project/research/blueprint_compilation.py`, `project/strategy/dsl/*`, and `project/strategy/models/executable_strategy_spec.py`.

- Actual runtime flow.
  `project/pipelines/run_all.py` resolves effective config, builds the stage plan, executes stage families, writes manifests, and runs postflight comparison/reporting hooks.
  Research-stage construction happens in `project/pipelines/stages/research.py`.
  If `experiment_config` is supplied, the file is parsed and `build_experiment_plan()` is called before stage creation.
  The same stage builder still composes legacy event-parameterized phase-1/phase-2 stages and also the search-engine stage.
  Candidate discovery outputs are then consumed by reporting, promotion, blueprint compilation, and comparison services, but those consumers do not all agree on location or identity contracts.

- Authoritative files by concern.
  Pipeline planning: `project/pipelines/pipeline_planning.py`
  Effective runtime config: `project/pipelines/effective_config.py`
  Stage registry and artifact families: `project/contracts/pipeline_registry.py`
  Research discovery: `project/research/services/candidate_discovery_service.py`, `project/research/phase2_search_engine.py`, `project/research/discovery.py`
  Promotion: `project/research/services/promotion_service.py`
  Regime routing: `project/research/regime_routing.py`
  Strategy lineage/packaging: `project/research/compile_strategy_blueprints.py`, `project/research/blueprint_compilation.py`, `project/strategy/models/executable_strategy_spec.py`
  Audit/report generation: `project/research/services/reporting_service.py`, `project/research/services/run_comparison_service.py`, `project/scripts/build_system_map.py`, `project/scripts/build_architecture_metrics.py`

# F. Regime/event system assessment

- What is canonical in code.
  `spec/events/event_registry_unified.yaml` is the canonical event table.
  `project/domain/registry_loader.py` compiles it into `EventDefinition` records.
  `canonical_regime` is the closest thing to the intended canonical research grouping.
  `spec/events/regime_routing.yaml` plus `project/research/regime_routing.py` define executable regime routing.
  State ontology still partly depends on `spec/grammar/state_registry.yaml` through `project/domain/registry_loader.py:116-205`.

- What is implementation detail and should remain that way.
  search-engine bridge rows
  per-event stage naming
  `reports_dir` and events-file materialization details
  temporary compatibility aliases in proposal loading

- What is research scaffolding and should be demoted.
  `legacy_family`
  heuristically derived `canonical_family`
  raw string parsing of event names into family labels
  search-time bridge schemas that preserve old candidate identities by aliasing

- Internal consistency findings.
  The registry itself is mostly coherent. The audit probe found `70` events, `15` canonical regimes, `72` states, `30` template operators, `4` composites, `4` context tags, `1` strategy construct, `4` research-only events, and `1` strategy-only event.
  `project/domain/registry_loader.py:50-90` still merges defaults by `legacy_family` when present. That is deliberate compatibility logic, but it keeps legacy grouping live in the compiled registry path.
  `project/research/services/candidate_discovery_scoring.py:498` derives `canonical_family` as `event_type.split("_")[0]`. That is not ontology-clean and is not registry-backed.
  `project/research/search/bridge_adapter.py` also reconstructs event semantics from row text instead of resolving from the compiled registry.
  The result is partial propagation, not full propagation. Regime metadata is present in routing and some reporting, but family/regime meaning is still reconstructed opportunistically in candidate evaluation and bridge adaptation.

- Practical assessment.
  The event/regime model is strong enough for bounded research and reporting.
  It is not yet ontologically clean enough for trustworthy regime-first search, robust deconfliction, or ML feature learning across regime buckets.
  Structural/forced-flow edge work is supportable if run narrowly through explicit event types and reviewed artifacts.
  Broad regime-first discovery remains exposed to dilution because the system still permits family/regime aliasing and mixed path semantics.
  Candidate ranking exists, but confidence/deconfliction logic remains more rule- and gate-shaped than fully canonical.
  ML would fit cleanly only after identity and ontology cleanup. Before that, ML would mostly learn compatibility residue, path leakage, and mixed event-family semantics.

# G. Test/CI/validation reality

- What I ran locally.
  `.venv/bin/python -m compileall -q project project/tests` -> passed
  `.venv/bin/pytest project/tests/architecture -q` -> passed
  `.venv/bin/python -m project.spec_validation.cli` -> passed with a module-import runtime warning
  `.venv/bin/python project/scripts/ontology_consistency_audit.py --output docs/generated/ontology_audit.json --check` -> passed
  `.venv/bin/python project/scripts/detector_coverage_audit.py --md-out docs/generated/detector_coverage.md --json-out docs/generated/detector_coverage.json --check` -> passed
  `.venv/bin/pytest project/tests/smoke/test_research_smoke.py -q` -> passed
  `.venv/bin/pytest project/tests/smoke/test_promotion_smoke.py -q` -> passed
  `.venv/bin/pytest project/tests/smoke/test_engine_smoke.py -q` -> passed
  `.venv/bin/pytest -q --maxfail=25 project/tests` -> passed
  `.venv/bin/pytest tests -q` -> passed when invoked explicitly

- What failed or drifted.
  `.venv/bin/python project/scripts/build_system_map.py --check` initially failed because `docs/generated/system_map.md` and `.json` were absent from the checkout.
  `.venv/bin/python project/scripts/build_architecture_metrics.py --check` failed with `FAILED: Coupling increased from 2476 to 2497`.
  `.venv/bin/pyright project` could not be reproduced locally because `pyright` was not installed in the current `.venv`; CI installs it separately in workflow. I cannot verify local type-check health beyond the workflow definition.

- CI/workflow reality.
  `.github/workflows/tier1.yml`, `tier2.yml`, and `tier3.yml` are active and meaningful.
  Tier 1 runs compile, architecture tests, spec validation, ontology drift, detector coverage, system-map drift, architecture metrics drift, and smoke subsets.
  The workflows are not obviously stale, but the doc-generation checks are sensitive to generated-state drift and incomplete tracked artifacts.

- Root-cause clusters for validation risk.
  Documentation/generation checks are less reproducible than unit tests.
  Default pytest ignores `tests/`, so the repository has two passing test trees but only one is part of the default collection contract.
  Warnings indicate maintenance debt even where tests pass. Repeated deprecation warnings around engine PnL helpers and Pandas FutureWarnings suggest upcoming churn risk.

# H. Operational readiness

- Architecturally present.
  Kill-switch support exists in `project/live/kill_switch.py`.
  Position/account sync and persisted state exist in `project/live/state.py` and are wired through `project/live/runner.py`.
  Execution telemetry and degradation logic exist in `project/live/runner.py:155-192`.
  OMS abstraction exists in `project/live/oms.py`.
  Environment and credential validation exists in `project/scripts/run_live_engine.py:137-198`.

- Tested in smoke-like paths.
  The repository has smoke tests for engine, research, and promotion.
  I did not find evidence of a full live-trading smoke that exercises authenticated venue connectivity, order placement, reconciliation, degradation action, and recovery in one workflow.

- Empirically proven in repo artifacts.
  I did not verify any artifact trail proving a full live or paper-trading session with post-run reconciliation and order telemetry. Uncertainty is explicit here: the code may have been exercised externally, but that proof is not established from the checked-in repository state I inspected.

- Likely fragile under live conditions.
  `project/live/runner.py:50-55` unconditionally constructs a `BinanceFuturesClient` with empty credentials in `LiveEngineRunner.__init__`. That client is then used as the default REST client for the data manager. Even if a properly credentialed `OrderManager` is injected later, the runner itself still owns an empty-credential client.
  `project/live/oms.py` supports exchange-backed market orders but rejects exchange-backed limit orders, which narrows operational flexibility.
  Both live configs are monitor-only, so the default operational path is explicitly non-trading.
  `spec/grammar/kill_switch_config.yaml` exposes a narrow candidate-feature set for kill-switch learning/selection, which limits robustness against unseen failure modes.

- Production-readiness assessment.
  Research/pipeline operations: reasonably mature.
  Backtest/replay/packaging: strong enough for disciplined internal research.
  Live monitor-only runtime: plausible.
  Live trading: scaffolded, not proven.

# I. Highest-value remediation plan

- Phase 1: collapse discovery control to one authoritative path.
  Objective: make search-based phase-2 the only authoritative discovery engine and demote legacy conditional discovery to boundary compatibility only.
  Files/modules to change: `project/pipelines/stages/research.py`, `project/research/phase2_search_engine.py`, `project/research/discovery.py`, relevant smoke tests in `project/tests/smoke/`, contract tests under `project/tests/contracts/`.
  Exact contract/behavior to fix: remove parallel first-class scheduling of legacy `phase2_conditional_hypotheses__...` when search mode is active; make any remaining legacy path explicit compatibility tooling, not default pipeline behavior.
  Validation commands: `pytest project/tests/smoke/test_research_smoke.py -q`, `pytest project/tests/contracts -q`, `python -m project.pipelines.run_all ... --plan_only 1` for a narrow event run, then inspect `data/runs/<run_id>/run_manifest.json` and `data/reports/phase2/<run_id>/`.
  Risks/rollback notes: removing the old path may expose hidden consumers that depended on legacy artifact locations; keep a boundary translator for one release window.

- Phase 2: repair identity lineage end to end.
  Objective: make Proposal, Experiment, Hypothesis, Candidate, Blueprint, and Engine run distinct IDs with explicit parent references.
  Files/modules to change: `project/research/search/bridge_adapter.py`, `project/research/discovery.py`, `project/research/finalize_experiment.py`, `project/research/blueprint_compilation.py`, `project/strategy/models/executable_strategy_spec.py`, schema definitions in `project/contracts/schemas.py`.
  Exact contract/behavior to fix: stop aliasing `candidate_id` to `hypothesis_id`; require candidate rows to carry both `hypothesis_id` and a distinct `candidate_id`; propagate blueprint lineage fields without fallback matching.
  Validation commands: targeted lineage unit tests, `pytest project/tests/research -q`, `pytest project/tests/strategy -q`, and an end-to-end proposal issuance plus blueprint compilation on a tiny run.
  Risks/rollback notes: historical run comparison may need migration adapters; do not silently backfill IDs without marking migrated lineage.

- Phase 3: unify phase-2 storage contracts.
  Objective: make one canonical phase-2 directory contract for writers, readers, comparison, and packaging.
  Files/modules to change: `project/research/services/pathing.py`, `project/artifacts/catalog.py`, `project/research/services/reporting_service.py`, `project/research/services/run_comparison_service.py`, `project/research/compile_strategy_blueprints.py`, associated tests.
  Exact contract/behavior to fix: choose one canonical layout for combined candidates, symbol candidates, and diagnostics; make all consumers use the same path helper instead of hardcoded tree fragments.
  Validation commands: `pytest project/tests/artifacts -q`, `pytest project/tests/research/services -q`, and a narrow run followed by explicit path reconciliation of phase-2, promotion, and blueprint outputs.
  Risks/rollback notes: historical run readers will break unless compatibility readers are kept at the read boundary only.

- Phase 4: finish ontology cleanup at consumption sites.
  Objective: stop deriving family/regime semantics from event-name text and route all semantics through the compiled registry.
  Files/modules to change: `project/research/services/candidate_discovery_scoring.py`, `project/research/search/bridge_adapter.py`, `project/research/gating.py`, `project/domain/registry_loader.py`, `project/research/regime_routing.py`.
  Exact contract/behavior to fix: demote `legacy_family`; eliminate `event_type.split("_")[0]` style derivations; treat `canonical_regime` as the research grouping and preserve any family aliases as metadata only.
  Validation commands: `python -m project.spec_validation.cli`, ontology audits, regime-routing tests, and targeted comparison/regime-effectiveness tests.
  Risks/rollback notes: some reports may currently depend on family labels that look familiar but are semantically wrong; update reports deliberately rather than preserving misleading columns.

- Phase 5: harden IO semantics and comparison reliability.
  Objective: eliminate silent read fallbacks and cross-run ambiguity in research-critical paths.
  Files/modules to change: `project/io/utils.py`, `project/io/parquet_compat.py`, consumers that call `read_table_auto`, `project/research/services/run_comparison_service.py`.
  Exact contract/behavior to fix: distinguish missing-path, schema-mismatch, and unreadable-artifact outcomes; restrict cross-run fallback outside explicit compatibility tools; make parquet-compat provenance explicit.
  Validation commands: IO contract tests, comparison-service tests, and negative-control tests with intentionally missing/corrupt artifacts.
  Risks/rollback notes: stricter reads will surface latent problems immediately; that is desirable, but rollout should start in research-comparison and promotion-critical paths first.

- Phase 6: make docs and generated checks truthfully reproducible.
  Objective: ensure a clean checkout can satisfy structural/doc drift checks without hidden generated state.
  Files/modules to change: `project/scripts/build_system_map.py`, `project/scripts/build_architecture_metrics.py`, `.github/workflows/tier1.yml`, `README.md`, `docs/02_REPOSITORY_MAP.md`.
  Exact contract/behavior to fix: either track required generated files or generate them deterministically before `--check`; align repo-map docs with the actual active test tree and current layout.
  Validation commands: run the Tier-1 generation/check commands from a clean checkout and confirm zero drift without manual intervention.
  Risks/rollback notes: if metrics are intentionally ratcheted, document the ratchet process; otherwise drift checks become theater.

- Phase 7: decide whether live trading is an active product or a scaffold.
  Objective: either complete a paper-to-live readiness pathway or clearly demote live trading to non-production research support.
  Files/modules to change: `project/live/runner.py`, `project/live/oms.py`, `project/scripts/run_live_engine.py`, `project/configs/live_paper.yaml`, `project/configs/live_production.yaml`, live tests/smokes.
  Exact contract/behavior to fix: remove empty-credential default clients from runner construction, define an authenticated paper-trading smoke path, and prove reconcile/degradation/kill-switch behavior with artifacts.
  Validation commands: authenticated paper environment validation, live-engine smoke test with mocked venue plus one paper-session artifact run, reconciliation assertions against saved snapshots.
  Risks/rollback notes: do not enable `runtime_mode='trading'` before a paper-trading artifact trail exists.

# J. “Do next” recommendation

The single best next bounded step is Phase 1 plus Phase 3 together on a narrow scope: make one authoritative phase-2 discovery path and one canonical phase-2 artifact layout, then run one small proposal-issued experiment and verify that discovery, promotion, blueprint compilation, and comparison all consume the same candidate set without fallback logic. That is the highest-leverage move because it removes the main trust failure: different parts of the system reasoning over different discoveries with ambiguous identities.
