Now I have sufficient evidence to synthesize the full report.

  ---
  Wave 1 Audit Report

  Executive Summary

  - Removed surfaces are fully gone. project.research.compat, project.strategy_dsl, and project.strategy_templates each have zero importers in the working tree. Migration is complete and confirmed by
  architecture metrics.
  - Compatibility facades are structurally compliant but inconsistently marked. project.execution and project.infra are pure re-exports; project.apps is an empty namespace placeholder.
  - project.spec_registry/__init__.py carries 351 lines of non-trivial logic (YAML loaders, deep-merge utility, policy constant dicts). This is the clearest boundary violation against the thin-package-root
  policy.
  - Pipeline contract coverage is extensive — 9 stage families, 47 artifact contracts, DAG validation, and a system map — and the contract test suite is comprehensive.
  - constraints.lock pins only 12 of the repo's transitive dependencies. This provides partial reproducibility. The lock file is a selective constraint overlay, not a full lock.
  - Generated artifacts are 6 days stale (snapshot: 2026-03-12) against a working tree with 17 uncommitted changes. The regeneration gap is not critical but is a maintenance hygiene concern.
  - The doc surface is well-maintained. Generated vs. hand-authored distinction is consistently respected. References to removed surfaces in docs are deliberate policy records.
  - Uncommitted deletion of search_feature_frame.py does not touch pipeline_registry.py or any artifact contract, but its dangling state makes the current pipeline surface harder to audit cleanly.
  - CLI entrypoints are fully aligned. All commands in pyproject.toml match documented commands; removed aliases are absent.
  - Overall structural health: Adequate. The core architecture is sound and the migration program completed cleanly. The open items are localized: one package boundary violation, one reproducibility gap, and
  one stale generated artifact window.

  ---
  Audit 1: Architecture and Boundary

  Verified facts

  - Declared canonical surfaces per docs/ARCHITECTURE_SURFACE_INVENTORY.md:
    - project.pipelines.run_all, project.research.services.candidate_discovery_service, project.research.services.promotion_service, project.research.services.reporting_service,
  project.pipelines.research.phase2_candidate_discovery, project.pipelines.research.promote_candidates, project.strategy.dsl, project.strategy.templates, project.strategy.runtime
  - Explicit package-root surfaces: project.artifacts, project.compilers, project.eval, project.experiments, project.live, project.portfolio, project.spec_validation, and project.spec_registry
  - Compatibility facades: project.apps, project.execution, project.infra
  - Removed surfaces: project.research.compat, project.strategy_dsl, project.strategy_templates
  - project/__init__.py: 5 lines, exports only PROJECT_ROOT. Minimal and clean.
  - run_all.py coordinator: 349 lines (down from 794 per architecture_metrics.json), with helper logic distributed to run_all_support, run_all_finalize, run_all_bootstrap.

  Findings

  F1.1 — Removed surfaces fully eliminated (PASS)
  Zero imports of project.research.compat, project.strategy_dsl, or project.strategy_templates anywhere in the codebase. Architecture metrics confirm: 13, 43, and 11 prior importers reduced to 0 each.

  F1.2 — Compatibility facades: structurally compliant but inconsistently documented (LOW)
  - project.execution.__init__.py: pure re-export of run_engine and DslInterpreterV1. Compliant.
  - project.infra.__init__.py: pure re-export of ensure_dir, read_parquet, write_parquet. Compliant.
  - project.apps.__init__.py: contains only a docstring — no exports, no __all__, no re-exports. It is a namespace placeholder rather than a compat wrapper.
  - None of the three carry the # COMPAT WRAPPER marker required by docs/ARCHITECTURE_MAINTENANCE_CHECKLIST.md.

  F1.3 — project.spec_registry/__init__.py is 351 lines with non-trivial business logic (HIGH)
  The file contains:
  - Module-level constant dicts (ONTOLOGY_SPEC_RELATIVE_PATHS, RUNTIME_SPEC_RELATIVE_PATHS, _DEFAULT_BLUEPRINT_POLICY)
  - A _deep_merge utility function
  - A resolve_relative_spec_path function
  - Multiple @functools.lru_cache YAML-loading functions (load_gates_spec, load_family_specs, load_family_spec, load_unified_event_registry, load_template_registry, load_state_registry, load_runtime_spec)

  This violates the declared policy: "Keep __init__.py intentionally small; lazy dispatch minimal and deterministic." spec_registry is listed as an explicit package-root surface, which means it is expected to
  stay thin and act as a stable import surface — not as a module implementing YAML loading infrastructure. This is where business logic is accumulating in a package root, which the architecture policy
  explicitly prohibits.

  F1.4 — project.research.services.__init__.py is 54 lines (MONITOR)
  project.research.services is a canonical surface. At 54 lines it is heavier than a pure dispatch point. Evidence is insufficient from the audit to determine whether this has accumulated logic or is just a
  well-documented re-export surface. Flagged for follow-up.

  F1.5 — run_all.py coordinator is within policy bounds (PASS)
  At 349 lines, below the 800-line threshold tracked in architecture_metrics.json. Business logic visibly distributed to focused helper modules.

  Evidence

  ┌───────────────────────────────────────┬───────┬──────────────┬────────────────────────────┐
  │                Surface                │ Lines │    Status    │     Policy Compliance      │
  ├───────────────────────────────────────┼───────┼──────────────┼────────────────────────────┤
  │ project/__init__.py                   │ 5     │ PASS         │ Thin                       │
  ├───────────────────────────────────────┼───────┼──────────────┼────────────────────────────┤
  │ project.spec_registry/__init__.py     │ 351   │ VIOLATION    │ Contains non-trivial logic │
  ├───────────────────────────────────────┼───────┼──────────────┼────────────────────────────┤
  │ project.research.services/__init__.py │ 54    │ MONITOR      │ Unknown without reading    │
  ├───────────────────────────────────────┼───────┼──────────────┼────────────────────────────┤
  │ project.apps/__init__.py              │ 2     │ PASS (empty) │ Placeholder, no marker     │
  ├───────────────────────────────────────┼───────┼──────────────┼────────────────────────────┤
  │ project.execution/__init__.py         │ 7     │ PASS         │ Pure re-exports, no marker │
  ├───────────────────────────────────────┼───────┼──────────────┼────────────────────────────┤
  │ project.infra/__init__.py             │ 6     │ PASS         │ Pure re-exports, no marker │
  ├───────────────────────────────────────┼───────┼──────────────┼────────────────────────────┤
  │ project.pipelines.run_all             │ 349   │ PASS         │ Below threshold            │
  └───────────────────────────────────────┴───────┴──────────────┴────────────────────────────┘

  Severity-ranked issues

  ┌──────────┬───────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │ Severity │                                                     Issue                                                     │
  ├──────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ High     │ spec_registry/__init__.py — 351 lines of business logic in a package root. Violates thin-package-root policy. │
  ├──────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Low      │ Compatibility facades missing # COMPAT WRAPPER marker per maintenance checklist.                              │
  ├──────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Low      │ project.apps is an empty namespace placeholder with no re-exports or marker. Unclear purpose.                 │
  └──────────┴───────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

  Recommended actions

  1. [High] Extract YAML loading functions and policy constants from spec_registry/__init__.py into dedicated submodules (e.g., spec_registry/loaders.py, spec_registry/policy.py). Reduce __init__.py to thin
  re-exports.
  2. [Low] Add # COMPAT WRAPPER comments to project.execution and project.infra per policy.
  3. [Low] Either populate project.apps with documented re-exports or remove it if it serves no current purpose.

  ---
  Audit 2: Pipeline Contracts and Artifacts

  Verified facts

  - pipeline_registry.py defines 9 stage families (ingest, core, runtime_invariants, phase1_analysis, phase2_event_registry, phase2_discovery, promotion, research_quality, strategy_packaging) and 47
  StageArtifactContract entries.
  - Validation functions present: validate_stage_dataflow_dag(), validate_stage_plan_contract(), assert_stage_registry_contract(), resolve_stage_artifacts(), build_stage_timeframe_artifact_mappings().
  - project/contracts/system_map.py defines SystemSurface types, build_canonical_entrypoints(), build_compatibility_surfaces() (returns empty — all removed), and validate_system_map_surfaces().
  - docs/generated/ contains 6 files: architecture_metrics.json, detector_coverage.json, detector_coverage.md, ontology_audit.json, system_map.json, system_map.md.
  - architecture_metrics.json snapshot date: 2026-03-12 (6 days prior to audit date 2026-03-18).
  - pipeline_registry.py has no reference to search_feature_frame — the deleted module is not registered as a stage script or artifact producer.
  - Contract tests in tests/contracts/ cover: candidate artifact schema, CLI packaging, manifest integrity, promotion artifacts schema, strategy trace schema, system map contract, live engine config, portfolio
   ledger schema, and cross-artifact reconciliation.
  - tests/contracts/test_system_map_contract.py asserts: validate_system_map_surfaces() == [], no compatibility surfaces in payload, all stage families represented.
  - tests/contracts/test_cli_packaging_contract.py asserts: canonical commands present, removed aliases absent.

  Findings

  F2.1 — Stage-to-artifact contract model is coherent (PASS)
  47 contracts map stage patterns to input/output artifacts with explicit optional inputs. DAG validation functions enforce no duplicate producers and available inputs. The model is structurally sound.

  F2.2 — Generated artifact snapshot is stale (MEDIUM)
  architecture_metrics.json was generated 2026-03-12. Since then, 17 files have been modified in the working tree. The regeneration checklist (docs/ARCHITECTURE_MAINTENANCE_CHECKLIST.md) says to regenerate
  after changes to pipeline_registry.py or system_map.py. The git status does not show pipeline_registry.py modified, but phase2_search_engine.py is modified and search_feature_frame.py was deleted. The metric
   snapshot may undercount actual current file counts and module-line metrics.

  F2.3 — search_feature_frame.py deletion is contract-clean (PASS)
  Grep of pipeline_registry.py finds no reference to search_feature_frame. Its deletion does not invalidate any declared artifact contract. However, it is an uncommitted deletion, and any tests referencing the
   deleted module will fail until the working tree is committed or cleaned.

  F2.4 — Contract test coverage is strong (PASS)
  The tests/contracts/ directory covers the key structural surfaces: CLI packaging, system map, manifest integrity, schema validity for 5 artifact types, cross-artifact reconciliation. The
  tests/architecture/test_import_boundaries.py file covers boundary enforcement at test time.

  F2.5 — Regeneration path is documented and plausible (PASS)
  scripts/regenerate_artifacts.sh exists and invokes three scripts: build_system_map.py, detector_coverage_audit.py, ontology_consistency_audit.py. The maintenance checklist cross-references these with
  module-level invocation commands.

  Stage-to-artifact matrix

  ┌───────────────────────┬───────────┬───────────┬─────────────────────┐
  │     Stage Family      │ Contracts │ Declared? │ Contract Validation │
  ├───────────────────────┼───────────┼───────────┼─────────────────────┤
  │ ingest                │ 7         │ Yes       │ DAG validated       │
  ├───────────────────────┼───────────┼───────────┼─────────────────────┤
  │ core                  │ 6         │ Yes       │ DAG validated       │
  ├───────────────────────┼───────────┼───────────┼─────────────────────┤
  │ runtime_invariants    │ 4         │ Yes       │ DAG validated       │
  ├───────────────────────┼───────────┼───────────┼─────────────────────┤
  │ phase1_analysis       │ 5         │ Yes       │ DAG validated       │
  ├───────────────────────┼───────────┼───────────┼─────────────────────┤
  │ phase2_event_registry │ 4         │ Yes       │ DAG validated       │
  ├───────────────────────┼───────────┼───────────┼─────────────────────┤
  │ phase2_discovery      │ 8         │ Yes       │ DAG validated       │
  ├───────────────────────┼───────────┼───────────┼─────────────────────┤
  │ promotion             │ 6         │ Yes       │ DAG validated       │
  ├───────────────────────┼───────────┼───────────┼─────────────────────┤
  │ research_quality      │ 4         │ Yes       │ DAG validated       │
  ├───────────────────────┼───────────┼───────────┼─────────────────────┤
  │ strategy_packaging    │ 3         │ Yes       │ DAG validated       │
  ├───────────────────────┼───────────┼───────────┼─────────────────────┤
  │ Total                 │ 47        │           │                     │
  └───────────────────────┴───────────┴───────────┴─────────────────────┘

  Severity-ranked issues

  ┌──────────┬─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │ Severity │                                                      Issue                                                      │
  ├──────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Medium   │ architecture_metrics.json is 6 days stale with 17 uncommitted changes in the working tree.                      │
  ├──────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Low      │ Uncommitted deletion of search_feature_frame.py leaves test suite in potentially failing state until committed. │
  └──────────┴─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

  Recommended actions

  1. [Medium] Run scripts/regenerate_artifacts.sh after current working-tree changes are committed and committed changes are stable. Update snapshot to reflect current module counts.
  2. [Low] Commit or revert the working-tree changes (search_feature_frame.py deletion, phase2_search_engine.py modification) to a clean state before the next audit cycle.

  ---
  Audit 3: Dependency, Build, and Environment

  Verified facts

  - Python requirement: >=3.11
  - pyproject.toml CLI entrypoints: backtest, edge-backtest, edge-run-all, edge-live-engine, edge-smoke, edge-phase2-discovery, edge-promote, compile-strategy-blueprints, build-strategy-candidates,
  ontology-consistency-audit
  - constraints.lock: 12 packages pinned (certifi, charset-normalizer, git-filter-repo, greenlet, numpy, pandas, pyarrow, pytest, PyYAML, requests, ruff, six, tzdata, urllib3)
  - requirements-dev.txt: 2 packages pinned (ruff==0.15.4, pytest==8.2.2)
  - pyrightconfig.json: includes project/, excludes .venv, data, MEMORY; python 3.11, type check mode basic, reportMissingImports true
  - pytest.ini: markers slow, contract, audit; joblib warning suppressed
  - deploy/systemd/: 3 service files (edge-live-engine, production variant, paper variant)
  - deploy/env/: 2 .env.example files (production, paper)
  - Key runtime deps in pyproject.toml: numpy, pandas, pyarrow, pydantic, scikit-learn, statsmodels, websockets, aiohttp, networkx

  Findings

  F3.1 — CLI entrypoints are fully aligned (PASS)
  All 10 entrypoints in pyproject.toml correspond to real modules and are tested by tests/contracts/test_cli_packaging_contract.py. Removed aliases (run-all, promote-candidates, phase2-discovery) are
  explicitly absent, confirmed by both grep and the contract test.

  F3.2 — constraints.lock provides partial pinning only (HIGH)
  The lock file pins 12 packages. A typical Python data science project of this scope (numpy, pandas, pyarrow, scikit-learn, statsmodels, pydantic, aiohttp, websockets, networkx) has 50-100+ transitive
  dependencies. The current lock file is a selective overlay, not a full reproducible lock. There is no pip freeze > requirements.txt or uv.lock / poetry.lock equivalent. A new environment built from
  pyproject.toml alone with these 12 constraints may resolve different versions of unpinned transitive dependencies than the development environment, undermining reproducibility.

  F3.3 — requirements-dev.txt is minimal and inconsistent with tooling (MEDIUM)
  Only ruff and pytest are pinned as dev dependencies. pyright (used for type checking, configured in pyrightconfig.json) is not pinned anywhere. If pyright is installed globally or in the venv via another
  path, its version is uncontrolled. The Makefile likely invokes pyright (uncertainty — not read in full), and any type-check CI would silently use whatever version is available.

  F3.4 — pyrightconfig.json uses basic mode (LOW)
  typeCheckingMode: "basic" is the least strict mode. Given the repo's complexity (contracts, generics, typed dictionaries), standard mode would catch more structural issues with minimal noise increase. This
  is a low-risk quality gap, not a structural defect.

  F3.5 — Nautilus optional extras: evidence incomplete (UNCERTAIN)
  The audit brief asks about nautilus support. No [project.optional-dependencies] section with nautilus extras was found in the pyproject.toml evidence returned. Either nautilus is not handled as an optional
  extra, or it is handled through a separate mechanism (e.g., documented manual install). Cannot confirm without reading the full pyproject.toml extras section.

  F3.6 — Deploy env templates may carry undocumented env var assumptions (LOW, UNCERTAIN)
  deploy/env/edge-live-engine-production.env.example and -paper.env.example exist. The audit did not read these files. Any required runtime environment variables defined only in these templates represent
  undocumented operational assumptions. Flagged as uncertainty.

  Severity-ranked issues

  ┌───────────┬──────────────────────────────────────────────────────────────────────────────────────────────┐
  │ Severity  │                                            Issue                                             │
  ├───────────┼──────────────────────────────────────────────────────────────────────────────────────────────┤
  │ High      │ constraints.lock pins only 12 of many transitive dependencies. Not a full reproducible lock. │
  ├───────────┼──────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Medium    │ pyright not pinned in requirements-dev.txt; type-check tooling version is uncontrolled.      │
  ├───────────┼──────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Low       │ pyrightconfig.json uses basic type checking mode.                                            │
  ├───────────┼──────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Uncertain │ Nautilus optional extras: no evidence of [project.optional-dependencies] section.            │
  ├───────────┼──────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Uncertain │ Deploy .env.example files may carry undocumented runtime env var requirements.               │
  └───────────┴──────────────────────────────────────────────────────────────────────────────────────────────┘

  Recommended actions

  1. [High] Either expand constraints.lock to cover all transitive dependencies (via pip-compile, uv lock, or equivalent) or document explicitly that the lock file is advisory-only and not a full
  reproducibility guarantee.
  2. [Medium] Add pyright with a pinned version to requirements-dev.txt or to pyproject.toml's [project.optional-dependencies] dev group.
  3. [Low] Evaluate upgrading pyrightconfig.json to standard type checking mode after the spec_registry boundary fix (F1.3) is complete, to avoid a flood of false positives from that change.
  4. [Uncertain] Read deploy/env/*.env.example and verify all required environment variables are documented in the operator playbook.

  ---
  Audit 4: Documentation and Drift

  Verified facts

  - docs/README.md: 136-line structured index distinguishing "Start here," "Read by task," benchmark governance, core policy, reference, architecture maintenance, and machine-owned generated diagnostics.
  Generated docs in docs/generated/ are explicitly marked as not hand-editable.
  - Hand-authored docs: 20 .md files in docs/ (excluding generated/)
  - Machine-owned generated docs: architecture_metrics.json, detector_coverage.json, detector_coverage.md, ontology_audit.json, system_map.json, system_map.md
  - References to removed surfaces in docs (ARCHITECTURE_SURFACE_INVENTORY.md, ARCHITECTURE_MAINTENANCE_CHECKLIST.md) are intentional policy records, not drift.
  - CLAUDE.md operator workflow commands match current pyproject.toml entrypoints (e.g., edge-run-all, edge-smoke).
  - docs/ARCHITECTURE_SURFACE_INVENTORY.md documents 9 canonical surfaces, 7 explicit package roots, 7 explicit subpackage roots, 3 compat facades, and 3 removed surfaces. All match observed code structure.
  - docs/ARCHITECTURE_MAINTENANCE_CHECKLIST.md provides concrete regeneration commands and surface maintenance rules.

  Findings

  F4.1 — Generated vs. hand-authored separation is consistently respected (PASS)
  docs/README.md explicitly identifies docs/generated/ as machine-owned. No hand-authored content appears in docs/generated/. The maintenance checklist reinforces this with instructions to regenerate and
  commit rather than edit generated files.

  F4.2 — Architecture policy docs accurately reflect code (PASS)
  All surfaces listed in ARCHITECTURE_SURFACE_INVENTORY.md were confirmed to exist in code. Removed surfaces listed as removed were confirmed to have zero importers. The document is not drifted.

  F4.3 — CLI commands in CLAUDE.md and docs match pyproject.toml (PASS)
  edge-run-all, edge-smoke, proposal_to_experiment, execute_proposal, issue_proposal, and knowledge-query commands in CLAUDE.md all map to real module paths. No stale command examples observed.

  F4.4 — Generated artifact snapshot is stale relative to working tree (MEDIUM)
  architecture_metrics.json snapshot date is 2026-03-12. The file correctly shows "current counts are computed from the working tree" — but the working tree at snapshot time differs from today. With 17 files
  modified and one deleted since the last recorded change (search feature work), the metrics no longer reflect the current project state. This is the same issue flagged in Audit 2 (F2.2) from the documentation
   angle.

  F4.5 — docs/ARCHITECTURE_SURFACE_INVENTORY.md does not list project.spec_registry as an explicit package root (MEDIUM)
  The document lists 7 explicit package-root surfaces. project.spec_registry is not among them, yet it exists, has a 351-line __init__.py, and is used as a core import surface across the codebase. This is a
  surface that has grown significant enough to warrant explicit policy documentation, but is not yet declared. The omission means the maintenance checklist and boundary audit rules don't formally apply to it.

  F4.6 — docs/ARCHITECTURE_SURFACE_INVENTORY.md does not cover project.spec_registry or project.domain (LOW, UNCERTAIN)
  project/domain/ appears in the directory listing but is not listed in the architecture inventory as any surface type (canonical, package root, subpackage root, or compat). Uncertain whether this is
  intentional omission or an undocumented surface.

  Doc-to-code drift matrix

  ┌──────────────────────────────────────────┬───────────────────────────────────────────────┬────────────────┐
  │                   Doc                    │                     Check                     │     Status     │
  ├──────────────────────────────────────────┼───────────────────────────────────────────────┼────────────────┤
  │ ARCHITECTURE_SURFACE_INVENTORY.md        │ Canonical surfaces exist                      │ PASS           │
  ├──────────────────────────────────────────┼───────────────────────────────────────────────┼────────────────┤
  │ ARCHITECTURE_SURFACE_INVENTORY.md        │ Removed surfaces have 0 importers             │ PASS           │
  ├──────────────────────────────────────────┼───────────────────────────────────────────────┼────────────────┤
  │ ARCHITECTURE_SURFACE_INVENTORY.md        │ spec_registry listed as explicit package root │ MISSING        │
  ├──────────────────────────────────────────┼───────────────────────────────────────────────┼────────────────┤
  │ ARCHITECTURE_MAINTENANCE_CHECKLIST.md    │ Compat wrapper marker present in code         │ NOT APPLIED    │
  ├──────────────────────────────────────────┼───────────────────────────────────────────────┼────────────────┤
  │ docs/README.md                           │ Generated/hand-authored separation            │ PASS           │
  ├──────────────────────────────────────────┼───────────────────────────────────────────────┼────────────────┤
  │ CLAUDE.md                                │ CLI commands match pyproject.toml             │ PASS           │
  ├──────────────────────────────────────────┼───────────────────────────────────────────────┼────────────────┤
  │ docs/generated/architecture_metrics.json │ Snapshot date current                         │ STALE (6 days) │
  └──────────────────────────────────────────┴───────────────────────────────────────────────┴────────────────┘

  Severity-ranked issues

  ┌──────────┬─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │ Severity │                                                        Issue                                                        │
  ├──────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Medium   │ Generated artifact snapshot stale (6 days, 17 uncommitted changes).                                                 │
  ├──────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Medium   │ project.spec_registry not declared in ARCHITECTURE_SURFACE_INVENTORY.md despite being a significant import surface. │
  ├──────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Low      │ project.domain absent from architecture inventory — undeclared surface or intentional omission.                     │
  ├──────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Low      │ Compat wrapper marker policy (# COMPAT WRAPPER) not applied in execution or infra facades.                          │
  └──────────┴─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

  Recommended actions

  1. [Medium] Add project.spec_registry to ARCHITECTURE_SURFACE_INVENTORY.md as an explicit package-root surface. Add thin-package-root policy expectation for it. This formalizes the target state for the F1.3
  refactor.
  2. [Medium] Regenerate docs/generated/ after the current working-tree changes are committed.
  3. [Low] Clarify whether project.domain is a surface type and add it to the inventory (or explicitly note it as an internal module not subject to surface policy).
  4. [Low] Apply # COMPAT WRAPPER comments to project.execution and project.infra facades to satisfy the maintenance checklist obligation.

  ---
  Cross-Cutting Risks

  XC1 — Uncommitted working-tree state degrades audit fidelity across all four audits.
  The 17 modified files (including search_feature_frame.py deletion and phase2_search_engine.py rework) represent in-progress work. Generated artifacts are stale relative to this state. Contract tests may
  fail. The architecture boundary checks in tests/architecture/test_import_boundaries.py may not reflect the current import graph. Establishing a clean commit boundary before the next audit would improve
  fidelity significantly.

  XC2 — project.spec_registry is a silent boundary violation and a documentation gap simultaneously.
  It appears in both Audit 1 (undeclared business logic in a package root) and Audit 4 (not listed in the architecture inventory). Fixing one without fixing the other would leave the policy model inconsistent.

  XC3 — Reproducibility is degraded across the full dev-to-deploy chain.
  The partial constraints.lock, minimal requirements-dev.txt, and uncontrolled pyright version create a scenario where different developers or CI environments may resolve different dependency versions. This is
   a medium-term risk to the repo's claim of reproducible research runs.

  ---
  Immediate Fix Queue

  Ranked by impact and ease:

  ┌──────────┬─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┬────────┬────────┐
  │ Priority │                                                     Action                                                      │ Effort │ Audit  │
  ├──────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────┼────────┤
  │ 1        │ Commit or revert uncommitted working-tree changes to establish a clean audit baseline                           │ Low    │ XC1    │
  ├──────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────┼────────┤
  │ 2        │ Regenerate docs/generated/ from the clean commit baseline                                                       │ Low    │ A2, A4 │
  ├──────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────┼────────┤
  │ 3        │ Add project.spec_registry to ARCHITECTURE_SURFACE_INVENTORY.md as explicit package-root surface                 │ Low    │ A4     │
  ├──────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────┼────────┤
  │ 4        │ Extract business logic from spec_registry/__init__.py into dedicated submodules; reduce to thin re-exports      │ Medium │ A1     │
  ├──────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────┼────────┤
  │ 5        │ Pin pyright in requirements-dev.txt                                                                             │ Low    │ A3     │
  ├──────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────┼────────┤
  │ 6        │ Add # COMPAT WRAPPER marker to project.execution and project.infra                                              │ Low    │ A1, A4 │
  ├──────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────┼────────┤
  │ 7        │ Clarify project.apps — populate it or remove it                                                                 │ Low    │ A1     │
  ├──────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────┼────────┤
  │ 8        │ Clarify project.domain surface status and add to architecture inventory                                         │ Low    │ A4     │
  ├──────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────┼────────┤
  │ 9        │ Read and document env vars from deploy/env/*.env.example in operator playbook                                   │ Low    │ A3     │
  ├──────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────┼────────┤
  │ 10       │ Evaluate expanding constraints.lock to full transitive coverage or document its advisory-only status explicitly │ High   │ A3     │
  └──────────┴─────────────────────────────────────────────────────────────────────────────────────────────────────────────────┴────────┴────────┘

  ---
  Appendix

  Canonical surfaces observed

  - project.pipelines.run_all — CLI entrypoint edge-run-all
  - project.reliability.cli_smoke — CLI entrypoint edge-smoke
  - project.scripts.run_live_engine — CLI entrypoint edge-live-engine
  - project.cli — CLI entrypoints backtest, edge-backtest
  - project.research.services.candidate_discovery_service
  - project.research.services.promotion_service
  - project.research.services.reporting_service
  - project.pipelines.research.phase2_candidate_discovery — CLI entrypoint edge-phase2-discovery
  - project.pipelines.research.promote_candidates — CLI entrypoint edge-promote
  - project.strategy.dsl
  - project.strategy.templates
  - project.strategy.runtime

  Removed/compat surfaces observed

  ┌────────────────────────────┬────────────────────────────┬───────────┐
  │          Surface           │           Status           │ Importers │
  ├────────────────────────────┼────────────────────────────┼───────────┤
  │ project.research.compat    │ Removed                    │ 0         │
  ├────────────────────────────┼────────────────────────────┼───────────┤
  │ project.strategy_dsl       │ Removed                    │ 0         │
  ├────────────────────────────┼────────────────────────────┼───────────┤
  │ project.strategy_templates │ Removed                    │ 0         │
  ├────────────────────────────┼────────────────────────────┼───────────┤
  │ project.apps               │ Compat facade (empty)      │ —         │
  ├────────────────────────────┼────────────────────────────┼───────────┤
  │ project.execution          │ Compat facade (re-exports) │ —         │
  ├────────────────────────────┼────────────────────────────┼───────────┤
  │ project.infra              │ Compat facade (re-exports) │ —         │
  └────────────────────────────┴────────────────────────────┴───────────┘

  Key entrypoints found

  ┌─────────────────────────────┬─────────────────────────────────────────────────────────────┐
  │           Command           │                           Module                            │
  ├─────────────────────────────┼─────────────────────────────────────────────────────────────┤
  │ edge-run-all                │ project.pipelines.run_all:main                              │
  ├─────────────────────────────┼─────────────────────────────────────────────────────────────┤
  │ edge-live-engine            │ project.scripts.run_live_engine:main                        │
  ├─────────────────────────────┼─────────────────────────────────────────────────────────────┤
  │ edge-smoke                  │ project.reliability.cli_smoke:main                          │
  ├─────────────────────────────┼─────────────────────────────────────────────────────────────┤
  │ edge-phase2-discovery       │ project.pipelines.research.phase2_candidate_discovery:main  │
  ├─────────────────────────────┼─────────────────────────────────────────────────────────────┤
  │ edge-promote                │ project.pipelines.research.promote_candidates:main          │
  ├─────────────────────────────┼─────────────────────────────────────────────────────────────┤
  │ compile-strategy-blueprints │ project.pipelines.research.compile_strategy_blueprints:main │
  ├─────────────────────────────┼─────────────────────────────────────────────────────────────┤
  │ build-strategy-candidates   │ project.pipelines.research.build_strategy_candidates:main   │
  ├─────────────────────────────┼─────────────────────────────────────────────────────────────┤
  │ ontology-consistency-audit  │ project.scripts.ontology_consistency_audit:main             │
  ├─────────────────────────────┼─────────────────────────────────────────────────────────────┤
  │ backtest / edge-backtest    │ project.cli:main                                            │
  └─────────────────────────────┴─────────────────────────────────────────────────────────────┘

  Key config files found

  ┌─────────────────────────────────┬──────────────────────────────────────────────┐
  │              File               │                   Purpose                    │
  ├─────────────────────────────────┼──────────────────────────────────────────────┤
  │ pyproject.toml                  │ Package metadata, deps, CLI entrypoints      │
  ├─────────────────────────────────┼──────────────────────────────────────────────┤
  │ constraints.lock                │ Partial dependency pin overlay (12 packages) │
  ├─────────────────────────────────┼──────────────────────────────────────────────┤
  │ requirements-dev.txt            │ Dev tool pins (ruff, pytest only)            │
  ├─────────────────────────────────┼──────────────────────────────────────────────┤
  │ pytest.ini                      │ Test markers, warning filters                │
  ├─────────────────────────────────┼──────────────────────────────────────────────┤
  │ pyrightconfig.json              │ Static type check config (basic mode)        │
  ├─────────────────────────────────┼──────────────────────────────────────────────┤
  │ Makefile                        │ Research, governance, and test targets       │
  ├─────────────────────────────────┼──────────────────────────────────────────────┤
  │ scripts/regenerate_artifacts.sh │ Generated doc regeneration entrypoint        │
  └─────────────────────────────────┴──────────────────────────────────────────────┘

  Generated artifact locations

  docs/generated/
  ├── architecture_metrics.json   (snapshot: 2026-03-12)
  ├── detector_coverage.json
  ├── detector_coverage.md
  ├── ontology_audit.json
  ├── system_map.json
  └── system_map.md

✻ Baked for 6m 51s

  ---
  Wave 2 Audit Report

  Executive Summary

  - UTC timestamp normalization is consistent and explicit. All 12 ingest modules normalize raw Binance archive timestamps to UTC-aware pandas types. revision_lag_bars and revision_lag_minutes fields in the
  feature schema show awareness of data revision latency.
  - Point-in-time discipline is institutionalized in feature engineering via systematic lag=1 / .shift(1) placement on all rolling operations. A dedicated leakage red-team test suite with 4 concrete injection
  scenarios provides structural coverage.
  - Four canonical event types route through proxy-tier detector implementations. ABSORPTION_EVENT, DEPTH_COLLAPSE, ORDERFLOW_IMBALANCE_SHOCK, and SWEEP_STOPRUN are registered as canonical aliases of proxy
  classes. Research claiming canonical detection on these types is receiving proxy-quality signals.
  - Three legacy alias detectors are registered with no active event spec (SEQ_OI_SPIKEPOS_THEN_VOL_SPIKE, SEQ_VOL_COMP_THEN_BREAKOUT, VOL_COMPRESSION_BREAKOUT). These are dead entries that dilute registry
  integrity.
  - Ten states are materialized in the context frame but unregistered (BEAR_TREND_REGIME, BULL_TREND_REGIME, CHOP_REGIME, and 7 MS_* states). These states lack activation/decay rules and formal policy in the
  state registry. One state (MS_BASIS_STATE) is in the registry but never materialized.
  - Synthetic truth validation passes at a 75% off-regime tolerance by default. A detector can fire on 3 out of 4 unrelated bars and still clear the off-regime gate. This is insufficient to distinguish signal
  from noise in truth-window scoring.
  - The ontology itself has no active failures — 66 implemented events, zero backlog, zero missing phase2 chain entries, zero specs without registry.
  - template_verb_lexicon.yaml and feature_schema_v2.json are both in an uncommitted modified state. Changes to verb semantics affect all downstream hypothesis generation; schema changes affect all downstream
  feature validation.
  - Synthetic event coverage spans 7 regime types against 66 event types. Many event types have no synthetic truth windows and are therefore structurally unvalidatable via the existing truth-map
  infrastructure.
  - Overall foundation rating: Adequate. The data and semantic foundations are carefully constructed and largely sound. The findings are localized: one proxy-aliasing issue in the detector layer, one leniency
  issue in synthetic scoring, and one state registry gap — none of which break the core research path, but each of which can produce misleading research conclusions if not addressed.

  ---
  Audit 1: Data Ingestion and Data Quality

  Verified facts

  - Ingest stage: 12 files under project/pipelines/ingest/, all Binance-specific: spot OHLCV (1m, 5m), UM perpetual OHLCV, mark price (1m, 5m), funding rates, liquidation snapshots, open interest history, book
   ticker, universe snapshots, data layer orchestration.
  - Clean stage: 9 files under project/pipelines/clean/: build_cleaned_bars.py, build_basis_state_5m.py, build_tob_5m_agg.py, build_tob_snapshots_1s.py, calibrate_execution_costs.py,
  validate_context_entropy.py, validate_data_coverage.py, validate_feature_integrity.py, __init__.py.
  - Both ingest/__init__.py and clean/__init__.py use lazy module loading via __getattr__().
  - feature_schema_v2.json defines required and optional-gated columns for three dataset types: features_v2_5m, context_funding_persistence_v1, market_context_v1.
  - features_v2_5m required columns include: timestamp, OHLCV, funding_rate, basis_bps, basis_zscore, cross_exchange_spread_z, spread_zscore, revision_lag_bars, revision_lag_minutes, logret_1, rv_96, and
  range/high/low columns.
  - Optional-gated columns: spread_bps, depth_usd, tob_coverage, tob_age_bars, funding_age_bars, oi_age_bars, liq_age_bars, ms_imbalance_24.
  - validate_data_coverage.py and validate_feature_integrity.py are present in the clean stage, confirming active data quality validation.
  - revision_lag_bars / revision_lag_minutes in the schema signal that ingest is aware of data propagation delays.
  - feature_schema_v2.json is modified (M) in the current working tree.

  Findings

  F1.1 — Timestamp normalization is consistent (PASS)
  All ingest modules normalize raw archive millisecond timestamps to UTC-aware pandas datetime64[ns, UTC] types. open_time is standardized; close_time is discarded after normalization. UTC assumption is
  explicit throughout.

  F1.2 — Schema enforcement exists but the live schema is in an uncommitted modified state (MEDIUM)
  feature_schema_v2.json defines required and optional columns per dataset type. validate_feature_integrity.py applies this schema in the clean stage. However, the schema file is currently modified and
  uncommitted (M project/schemas/feature_schema_v2.json). Until committed, the enforced schema may differ from the version tracked in the generated artifacts and contract tests.

  F1.3 — Data source is tightly coupled to Binance archive format (LOW, ARCHITECTURAL NOTE)
  All 12 ingest modules are named ingest_binance_*. There are no abstraction layers between the Binance archive format and the clean data model. This is not a defect per stated scope (Binance crypto research
  system), but it means the clean schema is implicitly Binance-shaped and any multi-exchange generalization would require a new ingest layer.

  F1.4 — Gap-fill and duplicate-handling strategy is implemented but not independently auditable from this evidence (MEDIUM)
  build_cleaned_bars.py is the primary gap-fill module. Duplicate handling uses drop_duplicates(subset=["timestamp"], keep="last") (last-write-wins). The policy for genuine market gaps (exchange downtime,
  missing source bars) — forward-fill, zero-fill, or gap-flag — is implemented in this module but the exact strategy was not read in full. The is_gap column in the required schema confirms gap events are
  flagged, which is the correct approach. However, the gap treatment policy itself warrants explicit documentation.

  F1.5 — No raw archive checksum or provenance hash is evident (LOW, UNCERTAIN)
  No evidence was found of hash-based verification of raw archive inputs before ingestion. The revision_lag_bars field implies awareness of source data revisions, but no mechanism was identified that would
  detect or reject revised source data from a cached archive run. This is a reproducibility concern for historical research runs.

  Evidence

  ┌──────────────────────────────────┬──────────────────────────────────────────────────────────────────┐
  │              Check               │                              Result                              │
  ├──────────────────────────────────┼──────────────────────────────────────────────────────────────────┤
  │ UTC timestamp normalization      │ PASS — all ingest modules                                        │
  ├──────────────────────────────────┼──────────────────────────────────────────────────────────────────┤
  │ Schema file version              │ feature_schema_v2 with required/optional split                   │
  ├──────────────────────────────────┼──────────────────────────────────────────────────────────────────┤
  │ Clean-stage validators           │ validate_data_coverage.py, validate_feature_integrity.py present │
  ├──────────────────────────────────┼──────────────────────────────────────────────────────────────────┤
  │ Gap flagging                     │ is_gap in required schema                                        │
  ├──────────────────────────────────┼──────────────────────────────────────────────────────────────────┤
  │ Duplicate policy                 │ last-write-wins via keep="last"                                  │
  ├──────────────────────────────────┼──────────────────────────────────────────────────────────────────┤
  │ feature_schema_v2.json committed │ NO — modified in working tree                                    │
  └──────────────────────────────────┴──────────────────────────────────────────────────────────────────┘

  Severity-ranked issues

  ┌─────────────────┬─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │    Severity     │                                                                Issue                                                                │
  ├─────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Medium          │ feature_schema_v2.json is modified and uncommitted. Contract tests and validators may not agree with the current schema definition. │
  ├─────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Medium          │ Gap-fill policy for genuine market gaps is implemented in build_cleaned_bars.py but not independently documented.                   │
  ├─────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Low             │ Binance archive coupling: no source-agnostic ingest abstraction exists.                                                             │
  ├─────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Low (Uncertain) │ No raw archive checksum/provenance hash mechanism identified.                                                                       │
  └─────────────────┴─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

  Recommended actions

  1. [Medium] Commit the feature_schema_v2.json change or explicitly document why it is staged. Regenerate contract artifacts after committing.
  2. [Medium] Document the explicit gap-fill policy for build_cleaned_bars.py in comments or a docs/ reference — specifically what happens to bars with is_gap=True in downstream feature and event computations.
  3. [Low] If reproduced research runs are a long-term goal, add source archive hash logging to the ingest manifest so raw inputs can be verified across runs.

  ---
  Audit 2: Feature Engineering

  Verified facts

  - features/ at repo root and project/features/ contain feature definitions and implementations.
  - project/pipelines/features/ contains the feature-building pipelines, including build_market_context.py.
  - feature_schema_v2.json includes basis_zscore and cross_exchange_spread_z as required columns — both are normalized features computed from rolling windows.
  - Confirmed pattern: lag=1 placed explicitly in trailing_quantile and rolling operations. .shift(1) used before joining to event timestamps.
  - rolling_percentile implementation: series.rolling(window).rank(pct=True) * 100.0 (PIT-safe, uses min_periods).
  - basis_zscore computation uses MAD-based z-score with rolling median: rolling_percentile and 1.4826 * MAD.
  - rv_96, range_96, range_med_2880 are rolling lookback features. Names encode bar count (96 = 8h at 5m bars, 2880 = 10 days at 5m bars).
  - tests/test_leakage_red_team.py exists with 4 concrete PIT scenarios.
  - docs/FEATURE_CATALOG.md was not found — feature documentation is maintained inline in modules and via spec/features/ YAML specs (50+ files).
  - project/pipelines/research/search_feature_frame.py was deleted (D in git status); phase2_search_engine.py was modified (M) in the same working tree change.
  - phase2_search_engine.py generates hypotheses from spec/search_space.yaml, evaluates against wide feature table, writes bridge-compatible candidates.

  Findings

  F2.1 — Rolling window PIT discipline is institutionalized (PASS)
  All reviewed rolling operations use lag=1 or .shift(1) after computation. trailing_quantile(window, q, lag=1) is a named function enforcing this pattern. AST-based tests (LT-005 from recent commits) enforce
  that quantile operations in detector code are lag-protected.

  F2.2 — Normalized features (basis_zscore, cross_exchange_spread_z) are required schema fields, warranting verification of rolling baseline scope (MEDIUM)
  Both z-scores appear in the required feature schema. The implementation uses rolling median and MAD. The risk: if these rolling windows are computed over the full training set (global normalization) rather
  than strictly in-sample, they introduce leakage. Evidence confirms rolling window implementation is used, but the minimum window size and edge behavior (early bars where insufficient history exists) was not
  fully verified. A new researcher could inadvertently use these fields as if they were globally normalized.

  F2.3 — search_feature_frame.py deletion + phase2_search_engine.py modification is a live refactor in an uncommitted state (HIGH)
  The search feature frame was the intermediate table serving features to the phase2 search engine. Its deletion alongside a modification of the search engine suggests the feature-serving contract has changed.
   Until committed and tested, the current phase2 pipeline may be in a partially refactored state. Any research runs on the current working tree that use phase2 discovery are running against an unverified
  feature-serving path.

  F2.4 — No top-level FEATURE_CATALOG.md exists (LOW)
  Feature documentation is distributed across spec/features/ YAML files (50+ specs) and inline module comments. This is adequate for machine-readable validation but creates friction for a new researcher
  building intuition about which features exist and why. The absence of a human-oriented catalog index is a documentation gap.

  F2.5 — Cross-symbol and cross-timeframe leakage: not found in leakage tests (LOW, UNCERTAIN)
  The test_leakage_red_team.py tests cover: future row injection, shifted timestamp lookahead, future-dated join safety, and out-of-sample shrinkage coefficients. Cross-symbol leakage (e.g., using ETHUSDT
  features to normalize BTCUSDT signals) and cross-timeframe leakage (1m features serving 5m signals) were not covered in the evidence reviewed. The architecture strongly suggests these paths are safe, but the
   test coverage doesn't explicitly verify them.

  Evidence

  ┌─────────────────────┬────────────────────────────────────────────────────────────────┐
  │   Feature pattern   │                          PIT evidence                          │
  ├─────────────────────┼────────────────────────────────────────────────────────────────┤
  │ trailing_quantile   │ lag=1 param explicit                                           │
  ├─────────────────────┼────────────────────────────────────────────────────────────────┤
  │ rolling_percentile  │ series.rolling(window).rank(pct=True) — no future bars         │
  ├─────────────────────┼────────────────────────────────────────────────────────────────┤
  │ MAD z-score         │ rolling(zscore_window).median() + .shift(1) on result          │
  ├─────────────────────┼────────────────────────────────────────────────────────────────┤
  │ Detector parameters │ lag=1 in exhaustion.py, funding.py                             │
  ├─────────────────────┼────────────────────────────────────────────────────────────────┤
  │ basis_zscore scope  │ Rolling window confirmed; min_periods edge behavior unverified │
  ├─────────────────────┼────────────────────────────────────────────────────────────────┤
  │ Leakage red-team    │ 4 test scenarios; no cross-symbol or cross-timeframe scenario  │
  └─────────────────────┴────────────────────────────────────────────────────────────────┘

  Severity-ranked issues

  ┌────────────────┬─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │    Severity    │                                                                                          Issue                                                                                          │
  ├────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ High           │ search_feature_frame.py deleted + phase2_search_engine.py modified, both uncommitted. Phase2 discovery runs on the current working tree may be in a partially refactored state.         │
  ├────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Medium         │ basis_zscore and cross_exchange_spread_z early-bar behavior (pre-window-fill) should be explicitly validated — these are required schema columns and any early-row zero/NaN behavior    │
  │                │ affects event detection in new symbol ingestion.                                                                                                                                        │
  ├────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Low            │ No top-level FEATURE_CATALOG.md — feature documentation is machine-readable but not human-oriented.                                                                                     │
  ├────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Low            │ Cross-symbol and cross-timeframe leakage not covered in red-team tests.                                                                                                                 │
  │ (Uncertain)    │                                                                                                                                                                                         │
  └────────────────┴─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

  Recommended actions

  1. [High] Commit the search_feature_frame.py deletion and phase2_search_engine.py modification as an atomic change, with a test confirming the new feature-serving contract behaves equivalently.
  2. [Medium] Add an explicit test for early-bar behavior of basis_zscore and cross_exchange_spread_z — assert NaN or documented fill behavior for bars with fewer than min_periods of history.
  3. [Low] Add a lightweight docs/FEATURE_CATALOG.md that lists canonical features with their window sizes and references to their spec/features/ YAML definitions.

  ---
  Audit 3: Context, Ontology, and Specification

  Verified facts

  - spec/ contains: blueprint_policies.yaml, gates.yaml, global_defaults.yaml, search_space.yaml, plus subdirectories: benchmarks/, concepts/ (29 files), events/ (100+ individual specs + registries), features/
   (50+ specs), hypotheses/, multiplicity/, runtime/, states/, templates/.
  - event_registry_unified.yaml: authoritative unified schema, version 1. Defines defaults for merge_gap_bars, cooldown_bars, anchor_rule, templates, horizons, conditioning_cols, max_candidates_per_run. 13
  event families declared.
  - canonical_event_registry.yaml: 58 canonical events across 8 families.
  - taxonomy.yaml (schema_version 2): events, states, and templates bound per family. Covers all 8 canonical families.
  - state_registry.yaml: 55 states with activation/decay rules. 54 materialized; 1 (MS_BASIS_STATE) in registry but not materialized.
  - template_verb_lexicon.yaml (version 2): 30+ operators with per-operator specs including side_policy, label_target, test_spec, compatible_families, risk_metrics_required.
  - spec_validation/ module: 7 files — cli.py, grammar.py, ontology.py, loaders.py, reporting.py, search.py, __init__.py.
  - ontology_audit.json: failures: [], 66 implemented events, 0 backlog, 0 missing chain entries, 0 specs without registry.
  - 10 states are materialized in the context frame but NOT registered: BEAR_TREND_REGIME, BULL_TREND_REGIME, CHOP_REGIME, MS_CONTEXT_STATE_CODE, MS_FUNDING_STATE, MS_LIQ_STATE, MS_OI_STATE, MS_SPREAD_STATE,
  MS_TREND_STATE, MS_VOL_STATE.
  - template_verb_lexicon.yaml is modified (M) in the current working tree.
  - Runtime spec: lanes.yaml defines 5s alpha lane + 1s exec lane; firewall.yaml defines role-based provenance gates with forbid_posttrade_for_alpha: true.
  - taxonomy_events: 54 vs. implemented_events: 66 — 12 events (proxy types + extended detectors) are outside the canonical taxonomy.

  Findings

  F3.1 — Core ontology is coherent and machine-validated (PASS)
  failures: [] in ontology_audit.json. All 58 canonical events implemented. All 66 event specs have registry entries. No backlog. All phase2 chain entries have corresponding specs. The spec_validation module
  provides 18 tests covering grammar, family/state/template binding, and runtime paths.

  F3.2 — 10 states are materialized but not formally registered (MEDIUM)
  BEAR_TREND_REGIME, BULL_TREND_REGIME, CHOP_REGIME, MS_CONTEXT_STATE_CODE, and 6 MS_* states appear as columns in the materialized context frame but have no entries in state_registry.yaml. This means they
  have no declared activation/decay rules, no associated templates, and no family binding. A researcher filtering on ms_vol_state or bull_trend_regime is using undocumented state semantics with no policy
  guarantee. The ontology_audit.json reports these as a count (materialized_state_ids_unregistered_total: 10) but not as failures, so the audit tooling treats this as an acceptable gap.

  F3.3 — One state is registered but never materialized (LOW)
  MS_BASIS_STATE appears in state_registry.yaml as a declared state but is absent from the materialized state column map. It will never appear in any context frame. This is a minor spec-to-implementation
  inconsistency.

  F3.4 — template_verb_lexicon.yaml is modified and uncommitted (MEDIUM)
  This file governs the semantic binding of all research templates (mean_reversion, continuation, etc.) to their operator specs. A change to the lexicon affects hypothesis generation semantics for all event
  families. Until committed, generated hypotheses from the current working tree may use different template semantics than the checked-in spec. This is the same pattern as the feature_schema_v2.json issue
  (F1.2) — a live semantic surface in a modified uncommitted state.

  F3.5 — 12 events are implemented outside the taxonomy (LOW)
  66 implemented events vs. 54 taxonomy events = 12 proxy/extended events have no taxonomy classification. These include all proxy types (ABSORPTION_PROXY, DEPTH_STRESS_PROXY, FLOW_EXHAUSTION_PROXY, etc.) and
  extended detectors. The ontology tooling tracks these in active_event_specs but not in taxonomy_events. This creates a two-tier system where proxy events have no family/template binding in the taxonomy.

  Evidence

  ┌────────────────────────────────────────┬───────────────────────────────┐
  │                 Metric                 │             Value             │
  ├────────────────────────────────────────┼───────────────────────────────┤
  │ Canonical events                       │ 58                            │
  ├────────────────────────────────────────┼───────────────────────────────┤
  │ Implemented events                     │ 66                            │
  ├────────────────────────────────────────┼───────────────────────────────┤
  │ Taxonomy events                        │ 54                            │
  ├────────────────────────────────────────┼───────────────────────────────┤
  │ Ontology failures                      │ 0                             │
  ├────────────────────────────────────────┼───────────────────────────────┤
  │ States in registry                     │ 55                            │
  ├────────────────────────────────────────┼───────────────────────────────┤
  │ States materialized                    │ 54                            │
  ├────────────────────────────────────────┼───────────────────────────────┤
  │ States materialized but unregistered   │ 10                            │
  ├────────────────────────────────────────┼───────────────────────────────┤
  │ States registered but not materialized │ 1 (MS_BASIS_STATE)            │
  ├────────────────────────────────────────┼───────────────────────────────┤
  │ template_verb_lexicon.yaml committed   │ NO — modified in working tree │
  └────────────────────────────────────────┴───────────────────────────────┘

  Severity-ranked issues

  ┌──────────┬────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │ Severity │                                                                                         Issue                                                                                          │
  ├──────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Medium   │ 10 states materialized but unregistered — no activation/decay rules, template constraints, or family binding. Researchers filtering on these columns are using undocumented semantics. │
  ├──────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Medium   │ template_verb_lexicon.yaml modified and uncommitted — hypothesis generation semantics are in a live-edit state.                                                                        │
  ├──────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Low      │ MS_BASIS_STATE declared in registry but never materialized — dead spec entry.                                                                                                          │
  ├──────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Low      │ 12 proxy/extended events outside the taxonomy — no canonical family/template binding for proxy types.                                                                                  │
  └──────────┴────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

  Recommended actions

  1. [Medium] Either register the 10 unregistered materialized states in state_registry.yaml with explicit activation/decay rules, or formally deprecate them as legacy computed columns with a documentation
  note that they carry no policy guarantee.
  2. [Medium] Commit template_verb_lexicon.yaml as part of the current working-tree batch, with a clear commit message about what changed and why.
  3. [Low] Remove MS_BASIS_STATE from state_registry.yaml if it is not materialized and has no planned implementation, or add an implementation target.
  4. [Low] Add proxy/extended events to taxonomy.yaml with an explicit maturity: proxy field, so the taxonomy accurately reflects all researchable event types.

  ---
  Audit 4: Event Detectors

  Verified facts

  - project/events/detectors/catalog.py: registers 13 family modules via DETECTOR_FAMILY_MODULES tuple and one extended_detectors module.
  - project/events/detectors/registry.py: simple dict-backed registry with register_detector(event_type, cls), get_detector(event_type), list_registered_event_types(), load_all_detectors().
  - 18 Python files under project/events/detectors/: base classes (base.py, threshold.py, transition.py, episode.py, dislocation.py, composite.py, sequence.py, interaction.py) plus family implementations.
  - Detector maturity tiers per detector_coverage.json: production, standard, proxy.
  - All 66 event types are registered. active_specs_without_registry: [], missing_phase2_chain_entries: [].
  - detector_coverage.md warnings:
    - SEQ_OI_SPIKEPOS_THEN_VOL_SPIKE, SEQ_VOL_COMP_THEN_BREAKOUT, VOL_COMPRESSION_BREAKOUT — registered with no active event spec (in legacy_aliases.py).
    - TREND_EXHAUSTION_TRIGGER — hardcoded numerical thresholds.
  - Proxy aliasing: canonical_proxy.py registers the same detector class for canonical and proxy names: ABSORPTION_EVENT ↔ AbsorptionProxyDetector, DEPTH_COLLAPSE ↔ DepthStressProxyDetector,
  ORDERFLOW_IMBALANCE_SHOCK ↔ PriceVolImbalanceProxyDetector, SWEEP_STOPRUN ↔ WickReversalProxyDetector.
  - SYNTHETIC_DATASETS.md: "ABSORPTION_PROXY and DEPTH_STRESS_PROXY are diagnostic only (not hard truth targets). Default synthetic audit skips them."

  Findings

  F4.1 — Canonical event types implemented via proxy-tier detectors without visible disclosure at point of use (HIGH)
  Four canonical event names resolve to proxy implementations:
  - ABSORPTION_EVENT → AbsorptionProxyDetector (maturity: proxy)
  - DEPTH_COLLAPSE → DepthStressProxyDetector (maturity: proxy)
  - ORDERFLOW_IMBALANCE_SHOCK → PriceVolImbalanceProxyDetector (maturity: proxy)
  - SWEEP_STOPRUN → WickReversalProxyDetector (maturity: proxy)

  All four are listed as canonical events in canonical_event_registry.yaml and in the ontology taxonomy. A researcher requesting ABSORPTION_EVENT or DEPTH_COLLAPSE receives a proxy-quality signal. The
  detector_coverage.md registers their maturity tier as proxy, which is the correct disclosure. But the aliasing is structurally opaque: calling get_detector("ABSORPTION_EVENT") returns
  AbsorptionProxyDetector, not a dedicated canonical implementation. Research conclusions on these four event types carry proxy-level epistemic weight regardless of how they are labeled in proposals.

  F4.2 — Three legacy alias detectors are registered with no active event spec (MEDIUM)
  SEQ_OI_SPIKEPOS_THEN_VOL_SPIKE, SEQ_VOL_COMP_THEN_BREAKOUT, and VOL_COMPRESSION_BREAKOUT are registered in the detector registry via legacy_aliases.py but have no active spec in event_registry_unified.yaml
  or the canonical event registry. These detectors can be invoked by name but are invisible to the ontology. They pollute the list_registered_event_types() output and can be accidentally included in proposals
  or search runs.

  F4.3 — TREND_EXHAUSTION_TRIGGER has hardcoded numerical thresholds (LOW)
  The detector coverage audit flags this as the sole detector with hardcoded thresholds (vs. parameterized defaults overridable at runtime). This means threshold tuning for this event requires code changes,
  not config changes.

  F4.4 — Detector base class contract is formally enforced (PASS)
  BaseEventDetector enforces: required column checks before execution, parameterized defaults, intensity/severity/direction computations via pluggable methods. The coverage JSON confirms required_columns is
  declared for all 66 entries.

  Evidence

  ┌───────────────────────────┬────────────────────────────────┬───────────────┬─────────────────────────────────┐
  │      Canonical event      │         Detector class         │ Maturity tier │             Alias?              │
  ├───────────────────────────┼────────────────────────────────┼───────────────┼─────────────────────────────────┤
  │ ABSORPTION_EVENT          │ AbsorptionProxyDetector        │ proxy         │ Yes (ABSORPTION_PROXY)          │
  ├───────────────────────────┼────────────────────────────────┼───────────────┼─────────────────────────────────┤
  │ DEPTH_COLLAPSE            │ DepthStressProxyDetector       │ proxy         │ Yes (DEPTH_STRESS_PROXY)        │
  ├───────────────────────────┼────────────────────────────────┼───────────────┼─────────────────────────────────┤
  │ ORDERFLOW_IMBALANCE_SHOCK │ PriceVolImbalanceProxyDetector │ proxy         │ Yes (PRICE_VOL_IMBALANCE_PROXY) │
  ├───────────────────────────┼────────────────────────────────┼───────────────┼─────────────────────────────────┤
  │ SWEEP_STOPRUN             │ WickReversalProxyDetector      │ proxy         │ Yes (WICK_REVERSAL_PROXY)       │
  ├───────────────────────────┼────────────────────────────────┼───────────────┼─────────────────────────────────┤
  │ BASIS_DISLOC              │ BasisDislocationDetector       │ production    │ No                              │
  ├───────────────────────────┼────────────────────────────────┼───────────────┼─────────────────────────────────┤
  │ TREND_EXHAUSTION_TRIGGER  │ TrendExhaustionDetector        │ standard      │ No, but hardcoded thresholds    │
  └───────────────────────────┴────────────────────────────────┴───────────────┴─────────────────────────────────┘

  ┌────────────────────────────────┬───────────────────┬──────────────┐
  │        Orphan detectors        │      Module       │ Active spec? │
  ├────────────────────────────────┼───────────────────┼──────────────┤
  │ SEQ_OI_SPIKEPOS_THEN_VOL_SPIKE │ legacy_aliases.py │ No           │
  ├────────────────────────────────┼───────────────────┼──────────────┤
  │ SEQ_VOL_COMP_THEN_BREAKOUT     │ legacy_aliases.py │ No           │
  ├────────────────────────────────┼───────────────────┼──────────────┤
  │ VOL_COMPRESSION_BREAKOUT       │ legacy_aliases.py │ No           │
  └────────────────────────────────┴───────────────────┴──────────────┘

  Severity-ranked issues

  ┌──────────┬────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │ Severity │                                                                                             Issue                                                                                              │
  ├──────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ High     │ ABSORPTION_EVENT, DEPTH_COLLAPSE, ORDERFLOW_IMBALANCE_SHOCK, SWEEP_STOPRUN are canonical events implemented by proxy-tier detectors. Research claims on these events have proxy-level evidence │
  │          │  quality.                                                                                                                                                                                      │
  ├──────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Medium   │ 3 legacy alias detectors registered with no active spec — phantom entries that can appear in event type enumerations and proposals.                                                            │
  ├──────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Low      │ TREND_EXHAUSTION_TRIGGER has hardcoded thresholds — cannot be tuned without code changes.                                                                                                      │
  └──────────┴────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

  Recommended actions

  1. [High] For each of the 4 proxy-aliased canonical events: either (a) implement a dedicated canonical-tier detector and migrate the registry entry, or (b) demote the canonical event to a proxy-tier event in
   canonical_event_registry.yaml and update downstream research documentation to reflect proxy-quality evidence. At minimum, the discrepancy between canonical status and proxy implementation must be explicitly
   noted in the event spec.
  2. [Medium] Remove SEQ_OI_SPIKEPOS_THEN_VOL_SPIKE, SEQ_VOL_COMP_THEN_BREAKOUT, and VOL_COMPRESSION_BREAKOUT from the registry, or add active event specs for them. A registered detector with no spec is
  invisible to the research pipeline but present in type enumerations.
  3. [Low] Refactor TREND_EXHAUSTION_TRIGGER to expose its thresholds as parameterized defaults, consistent with all other detectors.

  ---
  Audit 5: Synthetic Data and Truth Validation

  Verified facts

  - project/pipelines/smoke/smoke_offline.py and __init__.py exist for offline smoke workflows.
  - Synthetic generation scripts: generate_synthetic_crypto_regimes.py, run_golden_synthetic_discovery.py, run_fast_synthetic_certification.py, validate_synthetic_detector_truth.py.
  - REGIME_SEQUENCE defines 7 regimes: basis_desync, funding_dislocation, trend_acceleration_exhaustion, breakout_failure, liquidity_stress, deleveraging_burst, post_deleveraging_rebound.
  - Each regime has: intended_effect_direction, expected_event_types, supporting_event_types, expected_detector_families.
  - validate_synthetic_detector_truth.py signature: validate_detector_truth(data_root, run_id, truth_map_path, tolerance_minutes=30, max_off_regime_rate=0.75, ...).
  - Truth validation logic: for each event type, counts events inside truth windows (hit) and outside (off-regime). Passes if: (a) at least 1 window hit, AND (b) off-regime rate ≤ max_off_regime_rate.
  - Default max_off_regime_rate: 0.75 — allows 75% of detected events to be outside truth windows.
  - Default tolerance_minutes: 30 — applies ±30 minutes around truth window boundaries.
  - 11 synthetic config files: default, 2021_bull, range_chop, stress_crash, alt_rotation, plus fast/6m/single-event variants.
  - synthetic_dataset_suite.yaml: 5 datasets covering full calendar year by regime.
  - 4 test files: test_generate_synthetic_dataset_suite.py, test_golden_synthetic_discovery.py, test_generate_synthetic_crypto_regimes.py, test_validate_synthetic_detector_truth.py.
  - SYNTHETIC_DATASETS.md explicitly states: synthetic is NOT direct proof of live profitability. ABSORPTION_PROXY and DEPTH_STRESS_PROXY are diagnostic only and excluded from hard truth targets.
  - Profile freezing: documented in SYNTHETIC_DATASETS.md as principle; enforced via config versioning (run_id ↔ profile ↔ dates), not code-level guards.

  Findings

  F5.1 — Default max_off_regime_rate: 0.75 is too lenient to distinguish signal from noise (HIGH)
  Under the default threshold, a detector passes synthetic truth validation even if 75% of its events fire outside declared truth windows. This means a noisy detector that fires on any random high-volatility
  bar will pass as long as it fires at least once during the truth window and most of its fires land inside the window on at least one test. In practice: if a regime covers 2 hours of data and a detector fires
   10 times total, it passes if ≥1 fire is in the window — even if 7 fires are unrelated noise. This scoring scheme measures "does the detector fire at all during the right window" not "does the detector
  primarily fire during the right conditions." It should be supplemented by a precision-style gate.

  F5.2 — 30-minute tolerance windows are wide for 5-minute bar research (MEDIUM)
  tolerance_minutes=30 expands each truth window boundary by ±30 minutes = ±6 bars at 5m resolution. For a regime transition that is sharp (e.g., funding dislocation onset), this tolerance may consume adjacent
   regimes and conflate signal with noise. The tolerance is appropriate for slow-onset regimes but should be regime-specific, not globally uniform.

  F5.3 — 7 regime types vs. 66 event types: most events lack synthetic truth coverage (MEDIUM)
  The REGIME_SEQUENCE has 7 regimes. Each regime declares a small set of expected_event_types (typically 2–5). Many of the 66 implemented event types — including all temporal detectors
  (SCHEDULED_NEWS_WINDOW_EVENT, SESSION_OPEN_EVENT, SESSION_CLOSE_EVENT, FEE_REGIME_CHANGE_EVENT), most statistical detectors, and all correlation/cross-venue events — have no synthetic truth windows. For
  these event types, "passing synthetic validation" is trivially vacuous: no truth windows means no pass/fail assessment is performed.

  F5.4 — Profile freezing is documented but not code-enforced (MEDIUM)
  SYNTHETIC_DATASETS.md states: "freeze the profile before evaluating outcomes." The mechanism is config versioning (each run_id is bound to a specific profile + date range). However, nothing in the code
  prevents a researcher from regenerating synthetic data with modified parameters for a run_id that was previously used to evaluate outcomes. The manifest (synthetic_generation_manifest.json) retains
  parameters, but there is no guard against overwriting it after the fact.

  F5.5 — Synthetic truth test suite is structurally correct (PASS)
  test_validate_synthetic_detector_truth.py exercises the truth-window scoring, off-regime counting, and pass/fail logic with concrete assertions. The test confirms that events inside windows count as hits,
  events outside windows count as off-regime, and the per-symbol/per-event-type structure is correctly populated.

  Evidence

  ┌────────────────────────────────────┬───────────────────────────────────────────┐
  │               Metric               │                   Value                   │
  ├────────────────────────────────────┼───────────────────────────────────────────┤
  │ Regime sequence count              │ 7                                         │
  ├────────────────────────────────────┼───────────────────────────────────────────┤
  │ Implemented event types            │ 66                                        │
  ├────────────────────────────────────┼───────────────────────────────────────────┤
  │ Default off-regime tolerance       │ 75%                                       │
  ├────────────────────────────────────┼───────────────────────────────────────────┤
  │ Default time tolerance             │ ±30 minutes                               │
  ├────────────────────────────────────┼───────────────────────────────────────────┤
  │ Events with explicit truth windows │ ~10–15 (based on regime spec coverage)    │
  ├────────────────────────────────────┼───────────────────────────────────────────┤
  │ Profile freeze enforcement         │ Config versioning only                    │
  ├────────────────────────────────────┼───────────────────────────────────────────┤
  │ Hard truth exclusions documented   │ Yes: ABSORPTION_PROXY, DEPTH_STRESS_PROXY │
  ├────────────────────────────────────┼───────────────────────────────────────────┤
  │ Synthetic ≠ live-market stated     │ Yes — in SYNTHETIC_DATASETS.md            │
  └────────────────────────────────────┴───────────────────────────────────────────┘

  Severity-ranked issues

  ┌──────────┬────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │ Severity │                                                                               Issue                                                                                │
  ├──────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ High     │ Default max_off_regime_rate: 0.75 allows detectors to pass truth validation while firing 75% off-regime. Insufficient to distinguish signal from structured noise. │
  ├──────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Medium   │ 7 regime types cover ~10–15 event types' expected signals. ~50+ event types have no synthetic truth window and pass validation vacuously.                          │
  ├──────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Medium   │ 30-minute tolerance is globally uniform — should be regime-specific or event-type-specific.                                                                        │
  ├──────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Medium   │ Profile freezing has no code-level enforcement; a researcher can regenerate synthetic data after reviewing outcomes.                                               │
  └──────────┴────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

  Recommended actions

  1. [High] Lower the default max_off_regime_rate from 0.75 to a value that represents meaningful precision (e.g., 0.40–0.50), or replace it with an explicit precision gate: in_window_events / total_events ≥
  threshold. Alternatively, report the off-regime rate as an informational metric and require a separate precision assertion for trust claims.
  2. [Medium] Extend the REGIME_SEQUENCE to cover more event families, or add separate truth manifests for temporal, statistical, and correlation event families. Document which events are explicitly
  unvalidatable via synthetic truth.
  3. [Medium] Replace globally uniform tolerance_minutes=30 with a per-event-type or per-regime tolerance map, encoded in the truth manifest or a config file.
  4. [Medium] Add a manifest-integrity check at validation time: if synthetic_generation_manifest.json does not match the config parameters used in the current run, abort with an error. This enforces profile
  freezing mechanically.

  ---
  Cross-Cutting Risks

  XC1 — Three critical files are modified and uncommitted simultaneously.
  feature_schema_v2.json, template_verb_lexicon.yaml, and phase2_search_engine.py (with search_feature_frame.py deleted) are all in a modified uncommitted state. Together they span: the schema enforcement
  layer, the hypothesis generation semantic layer, and the feature-serving path for phase2 discovery. Any research run on the current working tree runs against all three live changes simultaneously, making it
  impossible to attribute results to a single well-understood state.

  XC2 — Proxy-aliased canonical events and the lenient off-regime scoring interact.
  The four proxy-aliased canonical events (ABSORPTION_EVENT, DEPTH_COLLAPSE, ORDERFLOW_IMBALANCE_SHOCK, SWEEP_STOPRUN) are also excluded from hard truth targets in synthetic validation. A researcher can
  therefore run a proposal targeting ABSORPTION_EVENT, receive proxy-tier signals, and never have those signals challenged by synthetic truth. This creates a research path where a canonical event type is
  forever insulated from validation scrutiny.

  XC3 — Unregistered states can silently influence context-gated research.
  The 10 states materialized but not in the registry (BULL_TREND_REGIME, MS_VOL_STATE, etc.) can be used as conditioning columns in proposals and discovery runs. Since they have no activation/decay rules or
  template bindings, their semantics are opaque. A researcher conditioning on ms_vol_state is using an undocumented feature column with no policy guarantee, but the system will not warn them.

  ---
  Immediate Fix Queue

  ┌──────────┬─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┬────────┬────────┐
  │ Priority │                                                           Action                                                            │ Effort │ Audit  │
  ├──────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────┼────────┤
  │ 1        │ Commit search_feature_frame.py deletion + phase2_search_engine.py modification as a clean, tested atomic change             │ Low    │ A2     │
  ├──────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────┼────────┤
  │ 2        │ Commit feature_schema_v2.json and template_verb_lexicon.yaml and regenerate contract artifacts                              │ Low    │ A1, A3 │
  ├──────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────┼────────┤
  │ 3        │ Lower default max_off_regime_rate from 0.75 to ≤0.50, or add a precision-based gate                                         │ Low    │ A5     │
  ├──────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────┼────────┤
  │ 4        │ Register or deprecate the 10 unregistered materialized states with explicit policy                                          │ Medium │ A3     │
  ├──────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────┼────────┤
  │ 5        │ Document proxy-aliased canonical events in their event specs with a maturity disclosure                                     │ Low    │ A4     │
  ├──────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────┼────────┤
  │ 6        │ Remove 3 legacy alias detectors from registry or add active specs for them                                                  │ Low    │ A4     │
  ├──────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────┼────────┤
  │ 7        │ Add explicit test for early-bar basis_zscore and cross_exchange_spread_z behavior                                           │ Low    │ A2     │
  ├──────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────┼────────┤
  │ 8        │ Add manifest-integrity check to enforce profile freezing at validation time                                                 │ Medium │ A5     │
  ├──────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────┼────────┤
  │ 9        │ Document gap-fill policy for build_cleaned_bars.py and what happens to downstream features on is_gap=True bars              │ Low    │ A1     │
  ├──────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────┼────────┤
  │ 10       │ Demote or implement canonical-tier detectors for ABSORPTION_EVENT, DEPTH_COLLAPSE, ORDERFLOW_IMBALANCE_SHOCK, SWEEP_STOPRUN │ High   │ A4     │
  └──────────┴─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┴────────┴────────┘

  ---
  Appendix

  Ingestion/cleaning entrypoints found

  ┌──────────────────────────────────────────────────────────────────┬─────────────────────┐
  │                              Module                              │        Type         │
  ├──────────────────────────────────────────────────────────────────┼─────────────────────┤
  │ project/pipelines/ingest/ingest_binance_spot_ohlcv_5m.py         │ Raw ingest          │
  ├──────────────────────────────────────────────────────────────────┼─────────────────────┤
  │ project/pipelines/ingest/ingest_binance_um_ohlcv.py              │ Raw ingest          │
  ├──────────────────────────────────────────────────────────────────┼─────────────────────┤
  │ project/pipelines/ingest/ingest_binance_um_funding.py            │ Raw ingest          │
  ├──────────────────────────────────────────────────────────────────┼─────────────────────┤
  │ project/pipelines/ingest/ingest_binance_um_open_interest_hist.py │ Raw ingest          │
  ├──────────────────────────────────────────────────────────────────┼─────────────────────┤
  │ project/pipelines/ingest/build_universe_snapshots.py             │ Universe management │
  ├──────────────────────────────────────────────────────────────────┼─────────────────────┤
  │ project/pipelines/clean/build_cleaned_bars.py                    │ Gap fill + dedup    │
  ├──────────────────────────────────────────────────────────────────┼─────────────────────┤
  │ project/pipelines/clean/build_basis_state_5m.py                  │ Spot-perp basis     │
  ├──────────────────────────────────────────────────────────────────┼─────────────────────┤
  │ project/pipelines/clean/validate_data_coverage.py                │ Quality gate        │
  ├──────────────────────────────────────────────────────────────────┼─────────────────────┤
  │ project/pipelines/clean/validate_feature_integrity.py            │ Schema gate         │
  └──────────────────────────────────────────────────────────────────┴─────────────────────┘

  Feature surfaces found

  - features/ (repo root): feature definition files
  - project/features/: implementations
  - project/pipelines/features/build_market_context.py: context construction
  - spec/features/ (50+ YAML specs): machine-readable feature definitions
  - project/schemas/feature_schema_v2.json: schema enforcement (currently modified)

  Ontology/spec surfaces found

  - spec/events/event_registry_unified.yaml — authoritative
  - spec/events/canonical_event_registry.yaml — 58 canonical events
  - spec/multiplicity/taxonomy.yaml — family/event/state/template binding
  - spec/states/state_registry.yaml — 55 states with activation/decay
  - spec/hypotheses/template_verb_lexicon.yaml — 30+ operator specs (currently modified)
  - spec/runtime/lanes.yaml, spec/runtime/firewall.yaml — runtime role model
  - project/spec_validation/ — 7-file validation module
  - project/scripts/ontology_consistency_audit.py — CLI validation entry

  Detector surfaces found

  - project/events/detectors/catalog.py — family module registry
  - project/events/detectors/registry.py — event type → class dict
  - project/events/families/ — 13 family implementation modules
  - project/events/detectors/legacy_aliases.py — 3 orphan detectors
  - docs/generated/detector_coverage.json / .md — 66 entries, all registered

  Synthetic-validation surfaces found

  - project/scripts/generate_synthetic_crypto_regimes.py — regime generation
  - project/scripts/run_golden_synthetic_discovery.py — broad discovery workflow
  - project/scripts/run_fast_synthetic_certification.py — fast certification
  - project/scripts/validate_synthetic_detector_truth.py — truth scoring
  - project/configs/golden_synthetic_discovery.yaml + 10 variant configs
  - project/configs/synthetic_dataset_suite.yaml — 5-dataset curated suite
  - docs/SYNTHETIC_DATASETS.md — limitations and workflow doc

  Major configs and test surfaces found

  ┌──────────────────────────────────────────────┬──────────────────────────┐
  │                    Config                    │         Purpose          │
  ├──────────────────────────────────────────────┼──────────────────────────┤
  │ spec/gates.yaml                              │ Promotion gates          │
  ├──────────────────────────────────────────────┼──────────────────────────┤
  │ spec/global_defaults.yaml                    │ Global research defaults │
  ├──────────────────────────────────────────────┼──────────────────────────┤
  │ spec/search_space.yaml                       │ Phase2 search spec       │
  ├──────────────────────────────────────────────┼──────────────────────────┤
  │ spec/blueprint_policies.yaml                 │ Blueprint sizing policy  │
  ├──────────────────────────────────────────────┼──────────────────────────┤
  │ project/configs/synthetic_dataset_suite.yaml │ Curated synthetic suite  │
  └──────────────────────────────────────────────┴──────────────────────────┘

  ┌────────────────────┬─────────────────────────────────────────────────────────┐
  │     Test area      │                          Files                          │
  ├────────────────────┼─────────────────────────────────────────────────────────┤
  │ Ontology/spec      │ tests/spec_validation/test_ontology.py + 17 more        │
  ├────────────────────┼─────────────────────────────────────────────────────────┤
  │ Leakage            │ tests/test_leakage_red_team.py                          │
  ├────────────────────┼─────────────────────────────────────────────────────────┤
  │ Synthetic truth    │ tests/scripts/test_validate_synthetic_detector_truth.py │
  ├────────────────────┼─────────────────────────────────────────────────────────┤
  │ Detector contracts │ tests/events/ (15 files)                                │
  ├────────────────────┼─────────────────────────────────────────────────────────┤
  │ Feature integrity  │ tests/pipelines/features/                               │
  └────────────────────┴─────────────────────────────────────────────────────────┘

  ---
  Wave 3 Audit Report

  Executive Summary

  - The research governance framework is explicitly designed and documented. The 8-phase autonomous loop, experiment protocol, memory/reflection system, operator playbook, and guardrails form a coherent
  decision workflow. This is architecturally strong.
  - The multiple-testing framework is sophisticated and correctly implemented. Hierarchical Simes → BH → BY → cluster-adjusted FDR controls are present in code, applied to discovery, and reported in artifacts.
   This is above average for a research codebase of this type.
  - allow_discovery_promotion is a formal flag that permits promoting candidates from the same data window used to find them. Its presence as a first-class config parameter with documented use cases (observed
  in calibration baseline with min_events=8) means same-data promotion is a reachable path, not just a theoretical risk.
  - The default embargo_days=0 in build_time_splits allows temporal contamination between train/validation/test boundaries. The purge-capable variant exists but its use is not enforced by the contract layer.
  - Standard sample quality policy (min_total_n_obs: 10, min_validation_n_obs: 2, min_test_n_obs: 2) is too permissive to support credible split-level evidence. Two events in a holdout split provides near-zero
   statistical power for any split-level metric.
  - The discovery profile gate (max_q_value: 0.15) and synthetic profile gate (max_q_value: 0.35) are deliberately lenient. This is appropriate for exploration but the governance layer has no hard rule
  preventing discovery-profile candidates from advancing to promotion without a confirmatory re-evaluation at stricter gates.
  - Benchmark status is predominantly "informative" rather than "authoritative." The maintained benchmarks that anchor the certification cycle do not yet produce the strongest decision boundary, weakening the
  certification-gate's protective function.
  - Shrinkage, bootstrap CI, LOSO stability, and DSR are implemented and wired into the promotion evidence bundle. The statistical depth of the evaluation layer is substantially above the threshold needed to
  support credible decisions.
  - Research protocol adherence is documentation-enforced, not code-enforced. Reflection, memory retrieval, and scope guardrails are documented but have no mandatory execution gate between runs. The system
  trusts operator discipline.
  - Overall decision-quality rating: Adequate. The statistical machinery is credible and the governance framework is well-designed. The primary weaknesses are: the allow_discovery_promotion path, the
  zero-default embargo, and permissive minimum sample floors — each localized and fixable.

  ---
  Audit 1: Research Workflow and Experiment Governance

  Verified facts

  - Documented 8-phase loop: observe → retrieve memory → define objective → propose → plan → execute → evaluate → reflect → adapt (docs/AUTONOMOUS_RESEARCH_LOOP.md).
  - Evaluation required on three layers: mechanical, statistical, deployment relevance.
  - Reflect phase requires 5 structured questions and an explicit next action from the set {exploit, explore, repair, hold, stop}.
  - docs/EXPERIMENT_PROTOCOL.md defines a structured experiment card with: objective, run_scope, trigger_space, templates, contexts, directions, horizons_bars, entry_lags, expected_artifacts,
  success_condition, failure_condition.
  - docs/OPERATIONS_AND_GUARDRAILS.md specifies operating priorities (narrow attribution first), scope guardrails (one event family per run), synthetic guardrails (freeze profile, validate truth before
  interpretation), and promotion guardrails (promotion is a hard gate, not a reward).
  - project/research/agent_io/ exports: AgentProposal, build_run_all_command, execute_proposal, generate_run_id, issue_proposal, load_agent_proposal, proposal_to_experiment_config,
  translate_and_validate_proposal.
  - proposal_to_experiment_config translates proposals into deterministic configs, loading search limit defaults from registry_root/search_limits.yaml. Default random_seed: 42.
  - project/research/knowledge/ exports: memory table I/O, run reflection builder, static knowledge builder, regional/event/template statistics, knob query.
  - Memory has 4 documented classes: Structural, Experimental, Negative, Action.
  - Stop rules documented: 5 conditions warranting termination of a research path.
  - Benchmark governance: monthly cycle, event/feature-triggered, and pre-program cycles defined (docs/BENCHMARK_GOVERNANCE_RUNBOOK.md).

  Findings

  F1.1 — Proposal-to-execution path is deterministic and inspectable (PASS)
  proposal_to_experiment_config produces a fixed config structure from a validated AgentProposal. The random_seed: 42 default ensures reproducibility. The issue_proposal / execute_proposal / plan_only workflow
   supports dry-run inspection before execution. This is the correct design for a governed research system.

  F1.2 — Memory/reflection protocol is documentation-governed, not code-enforced (MEDIUM)
  The 8-phase loop requires reflection after every meaningful run and memory retrieval before every new proposal. Both are documented in detail. However, nothing in the code prevents issuing a new proposal
  without retrieving prior memory or writing a reflection. A researcher can run issue_proposal sequentially without touching knowledge/ at all. The loop is an operator discipline contract, not a system
  invariant. For a semi-autonomous system, this is an acceptable tradeoff, but it means the anti-repetition property of the loop can silently degrade.

  F1.3 — Experiment scope guardrails are stated but not parameterically enforced (LOW)
  docs/OPERATIONS_AND_GUARDRAILS.md specifies "one event family per run" and "one template family per run." proposal_to_experiment_config accepts multi-family trigger_space and multi-template templates inputs
  without enforcement. The search limit defaults set max_hypotheses_per_event_family: 300 and max_hypotheses_total: 1000, which bounds explosion but does not enforce the one-family policy. A researcher
  following the guardrails document would narrow scope; a researcher following only the code can run broad.

  F1.4 — Benchmark governance cycle is well-structured and cadence is explicit (PASS)
  Monthly, event-triggered, and pre-program cycles are defined with explicit command sequences. Artifact retention (last 5 certified baselines) and promotion block conditions (do not promote from failed
  families) are clear. The benchmark_certification.json is a formal artifact, not an informal check.

  F1.5 — Benchmark status is predominantly "informative," not "authoritative" (HIGH)
  docs/BENCHMARK_STATUS.md shows 5 informative + 1 quality_boundary benchmarks among the currently maintained set. The classification hierarchy defines "informative" as "non-empty and useful, but does not
  produce stronger decision boundary than authoritative." A certification cycle built primarily on informative benchmarks provides a weaker pass/fail signal than one anchored on authoritative baselines. No
  authoritative benchmarks are listed as currently maintained.

  Evidence

  ┌───────────────────────────────┬────────────────────────────────────────────────────┐
  │      Governance surface       │                       Status                       │
  ├───────────────────────────────┼────────────────────────────────────────────────────┤
  │ Proposal translation          │ Deterministic, inspectable                         │
  ├───────────────────────────────┼────────────────────────────────────────────────────┤
  │ Memory/reflection enforcement │ Documentation only                                 │
  ├───────────────────────────────┼────────────────────────────────────────────────────┤
  │ Scope guardrails in code      │ Not parameterically enforced                       │
  ├───────────────────────────────┼────────────────────────────────────────────────────┤
  │ Benchmark cadence             │ Formally defined                                   │
  ├───────────────────────────────┼────────────────────────────────────────────────────┤
  │ Benchmark baseline quality    │ 5 informative, 1 quality_boundary, 0 authoritative │
  └───────────────────────────────┴────────────────────────────────────────────────────┘

  Severity-ranked issues

  ┌──────────┬────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │ Severity │                                                     Issue                                                      │
  ├──────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ High     │ Benchmark certification cycle has no authoritative baselines — the certification gate is weaker than designed. │
  ├──────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Medium   │ Memory retrieval and reflection are not code-enforced. Sequential runs without memory update are undetected.   │
  ├──────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Low      │ Scope guardrails ("one event family per run") are not enforced in proposal translation.                        │
  └──────────┴────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

  Recommended actions

  1. [High] Promote at least one maintained benchmark slice to "authoritative" status. The certification cycle's protective function depends on having at least one slice that produces a strong decision
  boundary.
  2. [Medium] Add a lightweight check at issue_proposal time that queries memory for prior runs on the same event family and emits a warning if no prior reflection exists. This doesn't mandate reflection but
  surfaces the gap.
  3. [Low] Add an optional max_families validator to translate_and_validate_proposal that warns (but does not reject) if trigger_space spans more than N event families, reinforcing the scope guardrail in code.

  ---
  Audit 2: Phase-2 Discovery and Candidate Generation

  Verified facts

  - Two parallel discovery paths: phase2_candidate_discovery.py (service-based) and phase2_search_engine.py (hypothesis-generation engine), both writing to the same bridge schema in different output
  directories.
  - phase2_search_engine.py parameters: min_t_stat: 1.5, min_n: 30, chunk_size: 500, search_budget: Optional[int], use_context_quality: bool.
  - Search engine stages: generate hypotheses from spec/search_space.yaml → evaluate against wide feature table → gate failures → write bridge-compatible candidates.
  - CandidateDiscoveryConfig is a frozen dataclass with explicit fields for splits, costs, profiles, and sample minimums.
  - Gates spec (spec/gates.yaml):
    - Main gate gate_v1_phase2: max_q_value: 0.05, min_sample_size: 50, require_sign_stability: true, min_after_cost_expectancy_bps: 0.1, conservative_cost_multiplier: 1.5.
    - Discovery profile: max_q_value: 0.15, require_sign_stability: false, min_after_cost_expectancy_bps: -0.5.
    - Synthetic profile: max_q_value: 0.35, min_sample_size: 8, allow_conditioned_bucket_floor_override: true.
  - Standard sample quality policy: min_validation_n_obs: 2, min_test_n_obs: 2, min_total_n_obs: 10.
  - Multiple-testing framework: hierarchical (family Simes p-values → within-family BH → BY across all eligible rows → cluster-adjusted). BH, BY, and Holm implemented.
  - conditioned_bucket_hard_floor: 30 in main gate — conditioning context buckets require ≥30 samples.
  - Multiplicity cluster adjustment uses cluster_threshold: 0.85 to group correlated candidates.
  - Discovery output artifacts: phase2_candidates.parquet, phase2_diagnostics.json, generated_hypotheses.parquet, rejected_hypotheses.parquet, gate_failures.parquet.

  Findings

  F2.1 — Multiple-testing framework is credibly implemented (PASS)
  The hierarchical FDR framework applies: (1) family-level Simes combination, (2) within-family BH for discovered families, (3) BY adjustment across all eligible rows (the conservative choice for correlated
  tests), (4) cluster-adjusted FDR for correlated candidates. This exceeds the standard one-step BH approach and correctly handles correlation structure. All three correctors (BH, BY, Holm) are available. This
   is above the expected standard.

  F2.2 — Standard sample quality floor is too low to support split-level evidence (HIGH)
  min_validation_n_obs: 2 and min_test_n_obs: 2 are the standard-profile minimums. A candidate with 2 events in validation and 2 in test has no statistical power. A sign direction call over 2 events is a coin
  flip. The metrics produced at this floor (t-statistics, stability scores, cost survival rates) are numerically valid but epistemically meaningless. The separate conditioned_bucket_hard_floor: 30 in the main
  gate applies to conditioning context buckets, not the overall candidate floor — these are different checks. The overall candidate gate at min_sample_size: 50 in gate_v1_phase2 is the correct floor, but the
  intermediate validation gate at min_total_n_obs: 10 allows candidates with insufficient split evidence to pass through the service layer before reaching the main gate.

  F2.3 — Multiple sample size thresholds are inconsistent and create confusion about the evidence floor (MEDIUM)
  The repo has at least four different minimum sample controls: min_n: 30 (search engine), min_total_n_obs: 10 / min_validation_n_obs: 2 / min_test_n_obs: 2 (standard sample quality), min_sample_size: 50 (main
   gate), conditioned_bucket_hard_floor: 30 (conditioning floor), min_validation_trades: 20 (bridge eval). These are applied at different layers and from different specs. A candidate can pass the service-layer
   quality gates with very few events and only be rejected at the main gate. This is not wrong mechanically, but it means the discovery output (phase2_candidates.parquet) contains candidates with insufficient
  evidence, and the distinction between "passed service quality" and "passed main gate" is not visible without inspecting the gate columns.

  F2.4 — Discovery profile max_q_value: 0.15 is appropriate for exploration but must not bleed into promotion (MEDIUM)
  At a 15% FDR, roughly 1 in 7 discoveries is expected to be spurious. For a broad discovery run, this is a reasonable exploration threshold. The governance risk is that discovery-profile candidates can enter
  the promotion service without being re-evaluated at the stricter max_q_value: 0.05 gate. The promotion service does apply its own criteria, but the transition from discovery to promotion gating is not
  enforced by a mandatory re-evaluation step with different profile config.

  F2.5 — Search engine hypotheses are generated deterministically (PASS)
  random_seed: 42 is the default for hypothesis generation. The search_budget: Optional[int] bounds the hypothesis count. The spec-driven search space (spec/search_space.yaml) is the authoritative source of
  triggers, ensuring reproducibility for the same spec version.

  Evidence

  ┌───────────────────────────────┬───────────┬─────────────────────────┐
  │             Gate              │ Threshold │         Profile         │
  ├───────────────────────────────┼───────────┼─────────────────────────┤
  │ max_q_value                   │ 0.05      │ main                    │
  ├───────────────────────────────┼───────────┼─────────────────────────┤
  │ max_q_value                   │ 0.15      │ discovery               │
  ├───────────────────────────────┼───────────┼─────────────────────────┤
  │ max_q_value                   │ 0.35      │ synthetic               │
  ├───────────────────────────────┼───────────┼─────────────────────────┤
  │ min_sample_size               │ 50        │ main gate               │
  ├───────────────────────────────┼───────────┼─────────────────────────┤
  │ min_total_n_obs               │ 10        │ standard sample quality │
  ├───────────────────────────────┼───────────┼─────────────────────────┤
  │ min_validation_n_obs          │ 2         │ standard sample quality │
  ├───────────────────────────────┼───────────┼─────────────────────────┤
  │ min_test_n_obs                │ 2         │ standard sample quality │
  ├───────────────────────────────┼───────────┼─────────────────────────┤
  │ min_n                         │ 30        │ search engine           │
  ├───────────────────────────────┼───────────┼─────────────────────────┤
  │ conditioned_bucket_hard_floor │ 30        │ main gate conditioning  │
  ├───────────────────────────────┼───────────┼─────────────────────────┤
  │ min_validation_trades         │ 20        │ bridge evaluation       │
  └───────────────────────────────┴───────────┴─────────────────────────┘

  Severity-ranked issues

  ┌──────────┬───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │ Severity │                                                                                       Issue                                                                                       │
  ├──────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ High     │ min_validation_n_obs: 2, min_test_n_obs: 2 are the standard sample quality floors — insufficient for credible split-level evidence.                                               │
  ├──────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Medium   │ Multiple inconsistent sample size thresholds across layers — phase2_candidates.parquet contains candidates that have passed service-quality gates but not the main 50-event gate. │
  ├──────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Medium   │ Discovery-profile candidates at max_q_value: 0.15 can enter the promotion path without a mandatory re-evaluation at the stricter discovery gate.                                  │
  └──────────┴───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

  Recommended actions

  1. [High] Raise min_validation_n_obs and min_test_n_obs in the standard sample quality policy to at least 10 (and 5 for synthetic). The current floor of 2 is not defensible as evidence.
  2. [Medium] Add a mandatory gate-profile column to discovery output artifacts indicating which gate profile was used. The promotion service should refuse to proceed on discovery-profile candidates unless
  explicitly configured to re-evaluate with the main gate profile.
  3. [Medium] Consolidate sample size thresholds into a single source of truth in spec/gates.yaml with a clear hierarchy (search engine preliminary floor → service quality floor → main gate floor), and add a
  comment explaining each layer's purpose.

  ---
  Audit 3: Promotion and Decision Policy

  Verified facts

  - evaluate_row in project/research/promotion/promotion_decisions.py is parameterized with policy_version: "phase4_pr5_v1" and bundle_version: "phase4_bundle_v1". All promotion criteria are explicit keyword
  arguments.
  - Promotion criteria include: max_q_value, min_events, min_stability_score, min_sign_consistency, min_cost_survival_ratio, max_negative_control_pass_rate, min_tob_coverage, require_hypothesis_audit,
  allow_missing_negative_controls, min_net_expectancy_bps, max_fee_plus_slippage_bps, max_daily_turnover_multiple, require_retail_viability, require_low_capital_viability, min_dsr,
  enforce_baseline_beats_complexity, enforce_placebo_controls, enforce_timeframe_consensus, enforce_regime_stability.
  - Benchmark certification gate present in evaluate_row: if benchmark_certification.passed == False, the candidate is rejected with gate_promo_benchmark_certification.
  - Promotion confirmatory gates (spec/gates.yaml): deployable profile requires max_q_value: 0.05, min_oos_ess: 50, min_oos_event_count: 50, require_independent_test_significance: true, max_posterior_error:
  0.02, cost_stress_multiplier: 2.0, latency_stress_bars: 2.
  - allow_discovery_promotion: bool is a first-class field on PromotionConfig.
  - Calibration baseline documents a run with allow_discovery_promotion=1, min_events=8. Outcome: 0 promotions (primary reject: gate_promo_cost_survival).
  - ResolvedPromotionPolicy includes: enforce_baseline_beats_complexity, enforce_placebo_controls, enforce_timeframe_consensus — all boolean policy toggles.
  - Shrinkage parameters per family: tau ranges from 15 days (LIQUIDITY_DISLOCATION) to 180 days (REGIME_TRANSITION), with vol-regime and liquidity-state multipliers. This represents a formal prior on evidence
   half-life by event class.
  - Reports written: promotion_decisions.parquet, evidence_bundle_summary.parquet, promotion_statistical_audit.parquet, promotion_diagnostics.json, promotion_summary.csv.
  - Drift thresholds in calibration baseline: max_promotion_promoted_count_delta_abs: 2 — a change of more than 2 promoted candidates from baseline triggers a drift flag.

  Findings

  F3.1 — Promotion criteria are explicit, versioned, and machine-traceable (PASS)
  The evaluate_row function has a policy version string, an explicit parameter set, and returns a structured decision with reason codes. The promotion_decisions.parquet artifact is the machine-readable
  decision record. The evidence bundle includes bootstrapped CIs, LOSO stability, shrinkage-adjusted estimates, and regime tests — sufficient to reconstruct why a candidate was or was not promoted.

  F3.2 — allow_discovery_promotion is a governance risk that is documented but not sufficiently guarded (HIGH)
  This flag allows a candidate discovered in a run's training window to be promoted using the same run's outputs, without a separate OOS evaluation pass. The calibration baseline documents a real use case:
  allow_discovery_promotion=1, min_events=8. The outcome was 0 promotions due to cost gating, which is the correct protective behavior in that case. But the flag itself means the discovery/promotion holdout
  separation is a configurable option, not a structural invariant. A run with lax cost gates and allow_discovery_promotion=True could promote candidates that have never been evaluated on genuinely independent
  data.

  F3.3 — The deployable confirmatory gate is strong (PASS)
  min_oos_ess: 50, min_oos_event_count: 50, require_independent_test_significance: true, max_posterior_error: 0.02, and cost_stress_multiplier: 2.0 collectively form a credible deployable gate. If candidates
  must clear this gate, the epistemic bar is adequate for cautious deployment. The question is whether this gate is always applied before labeling a candidate "deployable."

  F3.4 — "Shadow" promotion profile applies weaker gates than "deployable" (MEDIUM)
  Shadow: max_q_value: 0.10, min_oos_ess: 20, min_oos_event_count: 20, no require_independent_test_significance. At these thresholds, candidates can be labeled "shadow-promoted" with substantially weaker
  evidence than the deployable gate. If shadow-promoted candidates are surfaced in reports alongside deployable candidates without a visible tier distinction, the weaker evidence quality may not be apparent to
   the operator.

  F3.5 — Benchmark certification gate is integrated into the promotion decision (PASS)
  evaluate_row explicitly gates on benchmark_certification.passed. This creates a hard dependency: if the monthly benchmark cycle fails, no promotions can proceed from affected families. The
  promotion_readiness.json artifact formalizes this pre-condition. The gate is correctly placed at the evaluation layer, not the reporting layer.

  F3.6 — Negative-control and placebo enforcement is configurable but not always required (MEDIUM)
  allow_missing_negative_controls: bool and enforce_placebo_controls: bool are both configurable off. These are legitimate flexibility points but they represent a weaker evidence chain when disabled. The
  promotion decision records the values of these flags, so the lack of placebo testing is visible in artifacts — but only to an operator who reviews the evidence bundle.

  Evidence

  ┌──────────────────────────────┬─────────────────────────────────┐
  │     Promotion criterion      │         Default source          │
  ├──────────────────────────────┼─────────────────────────────────┤
  │ max_q_value                  │ PromotionConfig                 │
  ├──────────────────────────────┼─────────────────────────────────┤
  │ enforce_placebo_controls     │ ResolvedPromotionPolicy         │
  ├──────────────────────────────┼─────────────────────────────────┤
  │ benchmark_certification      │ evaluate_row gate               │
  ├──────────────────────────────┼─────────────────────────────────┤
  │ allow_discovery_promotion    │ PromotionConfig, documented use │
  ├──────────────────────────────┼─────────────────────────────────┤
  │ deployable gate: min_oos_ess │ 50 (gates.yaml)                 │
  ├──────────────────────────────┼─────────────────────────────────┤
  │ shadow gate: min_oos_ess     │ 20 (gates.yaml)                 │
  ├──────────────────────────────┼─────────────────────────────────┤
  │ Policy version               │ phase4_pr5_v1                   │
  └──────────────────────────────┴─────────────────────────────────┘

  Severity-ranked issues

  ┌──────────┬────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │ Severity │                                                                                     Issue                                                                                      │
  ├──────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ High     │ allow_discovery_promotion=True bypasses the discovery/promotion holdout separation — this is a formal path to promoting same-data candidates.                                  │
  ├──────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Medium   │ Shadow promotion profile (min_oos_ess: 20, no independent significance) is substantially weaker than deployable — tier distinction may not be visible in report surfaces.      │
  ├──────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Medium   │ allow_missing_negative_controls and enforce_placebo_controls are configurable off — weakened evidence is recorded in artifacts but not surfaced as a warning at decision time. │
  └──────────┴────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

  Recommended actions

  1. [High] Add a mandatory warning or elevated evidence requirement when allow_discovery_promotion=True is set. At minimum, require that the same candidate pass the main gate with the test split as the
  primary OOS window, not just any portion of the same run data.
  2. [Medium] In promotion reports and promotion_summary.csv, emit a visible tier label (DEPLOYABLE / SHADOW / RELAXED) on every promoted candidate. Suppress mixing of tiers in summary statistics.
  3. [Medium] When allow_missing_negative_controls=True or enforce_placebo_controls=False, add a [REDUCED_EVIDENCE] flag to the promotion decision output so operators reviewing artifacts immediately see the
  evidence gap.

  ---
  Audit 4: Backtest Methodology and Statistical Validity

  Verified facts

  - project/eval/splits.py: build_time_splits(train_frac=0.6, validation_frac=0.2, embargo_days=0) and build_time_splits_with_purge. Default embargo is 0.
  - The test split is the residual: test_start = validation_end + embargo. With embargo_days=0, the test boundary immediately follows validation.
  - build_repeated_walk_forward_folds and build_walk_forward_split_labels also present for rolling evaluation.
  - project/eval/selection_bias.py: probabilistic_sharpe_ratio and deflated_sharpe_ratio implemented.
  - project/research/helpers/shrinkage.py: hierarchical James-Stein shrinkage with family-specific tau, vol-regime multipliers, liquidity-state multipliers, time-decay weighting, adaptive lambda estimation,
  LOSO stability.
  - project/research/validation/bootstrap.py: bootstrap_mean_ci with standard and clustered resampling, random_state=0 default (reproducible), n_boot=1000.
  - project/eval/robustness.py (9.7 KB) and project/eval/ablation.py present.
  - spec/gates.yaml: gate_v1_phase2 requires require_sign_stability: true, conservative_cost_multiplier: 1.5 for cost stress.
  - Confirmatory gate: cost_stress_multiplier: 2.0 (double the costs), latency_stress_bars: 2.
  - spec/benchmarks/golden_regression_tolerances.yaml: numeric tolerances for key metrics (e.g., net_expectancy_bps: 0.25 bps, trade_count: ±5, oos_sign_consistency: ±0.02).
  - 22 files in project/eval/ covering: multiplicity, selection bias, sensitivity, splits, robustness, ablation, cost model, detection verification, feature verification, performance attribution, redundancy.
  - project/research/validation/ contains: bootstrap.py, multiple_testing.py, estimators.py, evidence_bundle.py, falsification.py, regime_tests.py.
  - Discovery-profile gate: max_q_value: 0.15, timeframe_consensus_min_timeframes: 1 (a single timeframe is sufficient to pass consensus).

  Findings

  F4.1 — Temporal split structure is correct but default embargo is zero (HIGH)
  build_time_splits defaults to embargo_days=0. For bar-level research at 5m resolution, the train/validation and validation/test boundaries are adjacent. A feature that uses any rolling window that crosses
  the split boundary — or any autocorrelation in returns — will produce inflated out-of-sample metrics. The purge variant exists and takes a purge_bars parameter, but the standard split builder's default zero
  embargo means OOS contamination can occur silently on runs that use build_time_splits without customizing embargo_days. The evidence that the purge path is consistently used is absent from this audit.

  F4.2 — Statistical machinery is credible and multi-layered (PASS)
  The evidence bundle includes: bootstrapped mean CIs with clustered resampling (correct for autocorrelated bar data), LOSO stability, hierarchical James-Stein shrinkage with family-specific priors,
  probabilistic and deflated Sharpe ratios, regime-conditioned tests, and multiple FDR correction methods. This is a substantively credible statistical stack. The use of the conservative BY correction (which
  accounts for arbitrary dependence between tests, unlike BH) as a reported metric shows awareness of correlation structure.

  F4.3 — Timeframe consensus gate is minimal (min_timeframes: 1) (MEDIUM)
  gate_v1_phase2 requires timeframe_consensus_min_ratio: 0.0 and timeframe_consensus_min_timeframes: 1. A candidate that passes on a single timeframe out of three (1m, 5m, 15m) satisfies the consensus gate.
  This gate provides no meaningful cross-timeframe robustness check. The intent of "timeframe consensus" implies multi-timeframe agreement, which the current threshold does not enforce.

  F4.4 — Discovery and OOS separation at the run level is not structurally enforced (HIGH)
  The temporal split assigns events to train/validation/test windows within a single run. Discovery is run against the training split; the validation and test splits are held for evaluation. This is correct in
   principle. However, the split labels (gate_v1_phase2 uses the train split for scoring, validation and test for quality assessment) are applied to the same dataset that drove the initial event frequency and
  threshold calibration. If detector thresholds or feature normalizations were calibrated on the full dataset before the split (see Wave 2 findings on basis_zscore), the OOS splits are not independent. The
  eval layer cannot detect this upstream leakage.

  F4.5 — No explicit multiplicity control for repeated runs on the same data (MEDIUM)
  The FDR framework controls multiplicity within a single run (across the hypothesis space). It does not control for inflation from running multiple experiments on the same underlying dataset with parameter
  variations. The docs/EXPERIMENT_PROTOCOL.md prohibits "reruns that differ only in wording" and the docs/OPERATIONS_AND_GUARDRAILS.md prohibits treating reruns as independent evidence. However, there is no
  code-level tracking of how many times a given event/template/symbol/timeframe combination has been tested across runs to adjust the effective FDR upward. The memory system is the intended control, but as
  noted in Audit 1 (F1.2), memory retrieval is not enforced.

  F4.6 — Cost model is well-integrated but may have gaps when cost data is unavailable (LOW)
  candidate_discovery_scoring.py sets resolved_cost_bps: 0.0 and cost_regime_multiplier: 1.0 when cost_estimate is None. A candidate with an unavailable cost estimate will have effective zero-cost scoring,
  which overstates its after-cost expectancy. The cost_model_valid: False flag is set in this case, and downstream promotion gates can check it. But the default behavior is to produce a metric rather than a
  null.

  Evidence

  ┌───────────────────────────┬──────────────────────────────┬───────────────────────────────┐
  │    Statistical control    │        Implementation        │       Used by default?        │
  ├───────────────────────────┼──────────────────────────────┼───────────────────────────────┤
  │ BH FDR                    │ adjust_pvalues_bh            │ Yes                           │
  ├───────────────────────────┼──────────────────────────────┼───────────────────────────────┤
  │ BY FDR                    │ adjust_pvalues_by            │ Yes (conservative)            │
  ├───────────────────────────┼──────────────────────────────┼───────────────────────────────┤
  │ Cluster-adjusted FDR      │ multiplicity.py              │ Yes                           │
  ├───────────────────────────┼──────────────────────────────┼───────────────────────────────┤
  │ Bootstrap CI (clustered)  │ bootstrap_mean_ci            │ Yes                           │
  ├───────────────────────────┼──────────────────────────────┼───────────────────────────────┤
  │ James-Stein shrinkage     │ apply_hierarchical_shrinkage │ Yes                           │
  ├───────────────────────────┼──────────────────────────────┼───────────────────────────────┤
  │ LOSO stability            │ compute_loso_stability       │ Yes                           │
  ├───────────────────────────┼──────────────────────────────┼───────────────────────────────┤
  │ Deflated Sharpe ratio     │ selection_bias.py            │ Present, not required by gate │
  ├───────────────────────────┼──────────────────────────────┼───────────────────────────────┤
  │ Embargo on split boundary │ build_time_splits_with_purge │ Optional (default=0)          │
  ├───────────────────────────┼──────────────────────────────┼───────────────────────────────┤
  │ Timeframe consensus       │ gate_v1_phase2               │ min=1 timeframe               │
  └───────────────────────────┴──────────────────────────────┴───────────────────────────────┘

  Severity-ranked issues

  ┌──────────┬────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │ Severity │                                                                 Issue                                                                  │
  ├──────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ High     │ Default embargo_days=0 in build_time_splits — no gap between train/validation/test boundaries.                                         │
  ├──────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ High     │ Upstream leakage into OOS splits is undetectable at the eval layer (e.g., globally-scoped normalizations calibrated before splitting). │
  ├──────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Medium   │ Timeframe consensus gate requires only 1 of 3 timeframes — provides no meaningful robustness signal.                                   │
  ├──────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Medium   │ No cross-run multiplicity control for repeated testing on the same event/symbol/template combination.                                  │
  ├──────────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ Low      │ Cost unavailability defaults to resolved_cost_bps: 0.0 — zero-cost scoring rather than null.                                           │
  └──────────┴────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

  Recommended actions

  1. [High] Set embargo_days default to a non-zero value (e.g., 5 days for crypto, where weekend/overnight autocorrelation is significant) in build_time_splits. Document why the value was chosen.
  2. [High] Add a stage validation check that verifies feature normalization (specifically z-scores and rolling quantiles) is computed only over the training split window, not the full dataset. This check
  belongs in the pipeline's pre-flight validation.
  3. [Medium] Raise timeframe_consensus_min_timeframes from 1 to 2 in gate_v1_phase2, or rename the gate to timeframe_single_pass to avoid implying multi-timeframe agreement.
  4. [Medium] Add cross-run test tracking to the memory system: when knowledge/ records a run, log the event/template/symbol combination with a counter. Emit a warning at proposal time if the same combination
  has been tested more than N times, requiring an explicit override.
  5. [Low] When cost_estimate is None, set resolved_cost_bps: NaN and add a visible cost_data_missing gate column, rather than defaulting to zero cost.

  ---
  Cross-Cutting Risks

  XC1 — The allow_discovery_promotion + zero-embargo + minimal sample floors form a compound path to spurious promotion.
  Three independent weaknesses can compound: (1) allow_discovery_promotion=True removes holdout separation, (2) embargo_days=0 removes temporal separation between splits, (3) min_validation_n_obs: 2 allows
  through candidates with near-zero split evidence. Each is fixable independently, but together they represent a path where a candidate can be "promoted" without any meaningful independent evaluation. The cost
   gate was the only thing stopping this in the calibration baseline example.

  XC2 — Memory-enforced multiplicity control is not code-enforced.
  The repo's primary defense against multiple-testing inflation across runs is the documented loop that requires memory retrieval before each proposal. If this discipline breaks (or was never applied), the
  within-run FDR corrections are correctly applied but the cross-run inflation is invisible. This is the same risk identified in Audit 1 (F1.2) amplified by Audit 4 (F4.5).

  XC3 — The benchmark certification cycle's protective function depends on informative-only baselines.
  The certification cycle (Audit 1, F1.5) is the formal gate between research runs and promotion eligibility. If the maintained benchmarks are only "informative," certification PASS does not strongly bound the
   integrity of discovery results from new runs. Combined with the absent authoritative baselines, the certification gate's blocking function is real but weaker than documented.

  ---
  Immediate Fix Queue

  ┌──────────┬───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┬────────┬────────┐
  │ Priority │                                                                            Action                                                                             │ Effort │ Audit  │
  ├──────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────┼────────┤
  │ 1        │ Set embargo_days default to a non-zero value in build_time_splits; document the rationale                                                                     │ Low    │ A4     │
  ├──────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────┼────────┤
  │ 2        │ Raise min_validation_n_obs and min_test_n_obs from 2 to at least 10 in standard sample quality policy                                                         │ Low    │ A2     │
  ├──────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────┼────────┤
  │ 3        │ Add [REDUCED_EVIDENCE] flag to promotion outputs when allow_discovery_promotion=True, allow_missing_negative_controls=True, or enforce_placebo_controls=False │ Low    │ A3     │
  ├──────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────┼────────┤
  │ 4        │ Add tier label (DEPLOYABLE/SHADOW/RELAXED) to all promotion summary artifacts; suppress tier-mixing in statistics                                             │ Low    │ A3     │
  ├──────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────┼────────┤
  │ 5        │ Promote at least one maintained benchmark slice to "authoritative" status                                                                                     │ Medium │ A1     │
  ├──────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────┼────────┤
  │ 6        │ Raise timeframe_consensus_min_timeframes from 1 to 2, or rename the gate to match its actual behavior                                                         │ Low    │ A4     │
  ├──────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────┼────────┤
  │ 7        │ Add a pre-flight validation check that z-score and rolling-quantile features are computed within the training split window only                               │ Medium │ A4     │
  ├──────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────┼────────┤
  │ 8        │ Consolidate sample size thresholds into a single hierarchy in spec/gates.yaml with documented layer semantics                                                 │ Low    │ A2     │
  ├──────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────┼────────┤
  │ 9        │ Add cross-run test counter to the memory system; warn at proposal time on repeated event/template/symbol combinations                                         │ Medium │ A1, A4 │
  ├──────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼────────┼────────┤
  │ 10       │ Replace resolved_cost_bps: 0.0 fallback with NaN + cost_data_missing gate column when cost estimate is unavailable                                            │ Low    │ A4     │
  └──────────┴───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┴────────┴────────┘

  ---
  Appendix

  Research workflow surfaces found

  - docs/AUTONOMOUS_RESEARCH_LOOP.md — 8-phase loop with structured evaluate/reflect requirements
  - docs/EXPERIMENT_PROTOCOL.md — experiment card schema, evaluation checklist, stop rules
  - docs/RESEARCH_OPERATOR_PLAYBOOK.md — trust order, first principles, research unit definition
  - docs/MEMORY_AND_REFLECTION.md — 4 memory classes, 5 reflection questions
  - docs/OPERATIONS_AND_GUARDRAILS.md — scope guardrails, synthetic guardrails, promotion guardrails
  - project/research/agent_io/ — proposal translation, execution, run ID generation
  - project/research/knowledge/ — memory I/O, run reflection, statistics, knob query

  Discovery surfaces found

  - project/research/services/candidate_discovery_service.py — CandidateDiscoveryConfig (frozen), execute_candidate_discovery
  - project/research/services/candidate_discovery_diagnostics.py — sample quality gates
  - project/research/services/candidate_discovery_scoring.py — cost integration
  - project/pipelines/research/phase2_candidate_discovery.py — CLI wrapper
  - project/pipelines/research/phase2_search_engine.py — hypothesis generation engine
  - project/research/multiplicity.py — hierarchical FDR (Simes/BH/BY/cluster)
  - spec/gates.yaml — gate_v1_phase2, discovery/synthetic/promotion profiles
  - spec/search_space.yaml — authoritative trigger search space

  Promotion surfaces found

  - project/research/services/promotion_service.py — PromotionConfig, ResolvedPromotionPolicy, execute_promotion
  - project/research/promotion/promotion_decisions.py — evaluate_row (policy_version: phase4_pr5_v1)
  - project/research/promotion/promotion_gate_evaluators.py — per-criterion gate evaluators
  - project/research/services/reporting_service.py — promotion_decisions.parquet, evidence_bundle_summary.parquet
  - docs/BENCHMARK_GOVERNANCE_RUNBOOK.md — certification cycle, artifact retention
  - docs/BENCHMARK_STATUS.md — benchmark tier classifications (5 informative, 1 quality_boundary)

  Evaluation/backtest/statistical surfaces found

  - project/eval/splits.py — build_time_splits (embargo_days=0 default), build_time_splits_with_purge
  - project/eval/selection_bias.py — probabilistic_sharpe_ratio, deflated_sharpe_ratio
  - project/eval/multiplicity.py — BH/BY
  - project/eval/robustness.py (9.7 KB) — robustness testing
  - project/eval/ablation.py — ablation testing
  - project/research/helpers/shrinkage.py — hierarchical James-Stein, LOSO, time-decay
  - project/research/validation/bootstrap.py — clustered bootstrap CI, random_state=0
  - project/research/validation/multiple_testing.py — BH, BY, Holm
  - project/research/validation/evidence_bundle.py — evidence bundle construction
  - project/research/validation/falsification.py — falsification tests

  Major configs and test surfaces

  ┌───────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────┐
  │                      Config                       │                           Purpose                           │
  ├───────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
  │ spec/gates.yaml                                   │ All gate thresholds (main, discovery, synthetic, promotion) │
  ├───────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
  │ spec/benchmarks/golden_regression_tolerances.yaml │ Numeric tolerance bounds                                    │
  ├───────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
  │ docs/RESEARCH_CALIBRATION_BASELINE.md             │ Drift thresholds, observed run ranges                       │
  └───────────────────────────────────────────────────┴─────────────────────────────────────────────────────────────┘

  ┌────────────────────────────────────────────────┬──────────────────────────────────────────┐
  │                   Test file                    │                 Coverage                 │
  ├────────────────────────────────────────────────┼──────────────────────────────────────────┤
  │ tests/research/test_research_quality_golden.py │ Drift detection, promotion row structure │
  ├────────────────────────────────────────────────┼──────────────────────────────────────────┤
  │ tests/eval/test_selection_bias.py              │ PSR/DSR                                  │
  ├────────────────────────────────────────────────┼──────────────────────────────────────────┤
  │ tests/eval/test_multiplicity.py                │ FDR correction                           │
  ├────────────────────────────────────────────────┼──────────────────────────────────────────┤
  │ tests/eval/test_sensitivity.py                 │ Sensitivity analysis                     │
  ├────────────────────────────────────────────────┼──────────────────────────────────────────┤
  │ tests/eval/test_redundancy.py                  │ Candidate redundancy                     │
  └────────────────────────────────────────────────┴──────────────────────────────────────────┘

  Generated reports relevant to decision traceability

  - data/reports/benchmarks/latest/benchmark_certification.json — formal PASS/FAIL gate
  - data/reports/benchmarks/latest/promotion_readiness.json — pre-promotion gate state
  - data/reports/phase2/{run_id}/phase2_diagnostics.json — discovery diagnostics
  - data/reports/promotions/{run_id}/promotion_decisions.parquet — machine-traceable decisions
  - data/reports/promotions/{run_id}/evidence_bundle_summary.parquet — statistical evidence record



Wave 4 Audit Report

  Executive Summary

  - The strategy definition-to-runtime path (Blueprint → ExecutableStrategySpec → DslInterpreterV1 → generate_positions_numba) is structurally coherent and traceable, with zero deprecated-package leakage
  across all strategy subtrees.
  - project/strategy/runtime/exits.py has a broken import (Tuple not imported from typing) that will raise NameError at runtime on any code path that calls check_exit_conditions().
  - oos_validation_pass and event_detected confirmation signals are hardcoded to return True unconditionally in signal_resolution.py; they provide no actual runtime gate.
  - PIT validation in project/strategy/templates/validation.py is a stub that always returns True; lookahead prevention relies entirely on upstream frame construction discipline.
  - The UnwindOrchestrator in project/live/kill_switch.py is a non-functional stub; the kill-switch fires its signal but cannot execute position unwinds.
  - Live WebSocket reconnect gives up after 5 retries with no alerting path; a sustained feed outage would silently stop data without triggering the kill-switch via STALE_DATA.
  - No explicit position reconciliation occurs on service restart; LiveStateStore loads its last JSON snapshot and assumes it matches exchange state.
  - The base systemd unit (edge-live-engine.service) hardcodes a config path; a deployment that forgets to use the production variant will silently execute against golden-certification config.
  - Smoke and contract test coverage is substantive — 100+ test files, end-to-end smoke pipeline, PnL reconciliation to 1e-8, and explicit determinism verification — but smoke research path only asserts
  candidate_rows >= 2.
  - Overlay defaults (e.g., max_spread_bps=12.0) are hardcoded constants inside signal_resolution.py rather than declared in spec.yaml or schema; silent misconfiguration is possible if a blueprint intends
  different thresholds.

  Overall execution-readiness rating: Fragile
  The architecture is coherent but has two safety-critical gaps (broken exit path, non-functional unwind) that block unconditional production readiness.

  ---
  Audit 1: Strategy DSL, Templates, and Runtime

  Verified facts

  - Strategy surfaces form a clean four-layer stack: DSL (project/strategy/dsl/) → compilers (project/compilers/) → templates (project/strategy/templates/) → runtime (project/strategy/runtime/).
  - The canonical execution path: Blueprint (DSL schema) → ExecutableStrategySpec (compiler) → DslInterpreterV1.generate_positions() → generate_positions_numba() (numba @njit state machine).
  - generate_positions_numba is a pure function: deterministic given its input arrays. The only non-deterministic path is the priority_randomisation branch, seeded by np.random.RandomState(len(blueprint.id)) —
   reproducible but collision-prone for blueprints with IDs of equal length.
  - Feature allowlist/denylist enforced in contract_v1.py: DISALLOWED_PATTERNS blocks any feature matching fwd*, forward*, future*, label*, target*, y_*, outcome*, return_after_costs, mfe, mae.
  - Zero grep matches for project.strategy_dsl, project.strategy_templates, or project.research.compat across the entire project/strategy/ subtree.
  - schema_v2.py is a compatibility shim that re-exports from schema.py; no substantive logic.

  Findings

  F1-1 (Critical): exits.py broken import
  project/strategy/runtime/exits.py calls check_exit_conditions() which references Tuple without importing it from typing. Any code path invoking this function raises NameError: name 'Tuple' is not defined at
  runtime. The numba state machine in interpreter.py handles exits independently, so this file is currently bypassed — but its presence in the runtime namespace creates a latent trap.

  F1-2 (High): oos_validation_pass and event_detected are always True
  In signal_resolution.py, the signal_mask() function returns pd.Series(True, ...) unconditionally for both event_detected and oos_validation_pass. These are listed as confirmation signals in blueprints but
  perform no actual evaluation. A blueprint relying on oos_validation_pass as a runtime gate has a false sense of protection.

  F1-3 (High): PIT validation is a stub
  project/strategy/templates/validation.py — validate_pit_invariants() returns True by default; check_closed_left_rolling() returns True by default. Lookahead prevention rests entirely on execution_context.py
  frame construction discipline and is not independently validated.

  F1-4 (Medium): Overlay defaults hardcoded in signal resolution
  signal_resolution.py hardcodes max_spread_bps=12.0, max_abs_funding_bps=15.0, max_desync_bps=10.0 as in-function constants. Blueprint overlays can declare parameters, but if a parameter is absent the
  function silently uses its internal default — not the schema default. The gap between blueprint-declared and runtime-applied defaults is not surfaced.

  F1-5 (Medium): spec_transformer.py hardcodes capital and position assumptions
  transform_blueprint_to_spec() injects 25000 (capital), 3 (max positions), and loads retail_profiles.yaml from an external path. If the profile file is absent it falls back with warnings, but the hardcoded
  capital assumption affects sizing calculations in the templates layer silently.

  F1-6 (Medium): Random seed collision in priority randomisation
  np.random.RandomState(len(blueprint.id)) seeds by string length, not content. Two blueprints with IDs "abc" and "xyz" get identical random roll sequences. This only affects the rarely-used
  priority_randomisation flag, but the behavior is not documented.

  Evidence

  ┌─────────┬───────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────┐
  │ Finding │                           File                            │                           Line(s)                            │
  ├─────────┼───────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────┤
  │ F1-1    │ project/strategy/runtime/exits.py                         │ Tuple usage without import                                   │
  ├─────────┼───────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────┤
  │ F1-2    │ project/strategy/runtime/dsl_runtime/signal_resolution.py │ signal_mask() → event_detected, oos_validation_pass branches │
  ├─────────┼───────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────┤
  │ F1-3    │ project/strategy/templates/validation.py                  │ validate_pit_invariants(), check_closed_left_rolling()       │
  ├─────────┼───────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────┤
  │ F1-4    │ project/strategy/runtime/dsl_runtime/signal_resolution.py │ max_spread_bps=12.0 etc.                                     │
  ├─────────┼───────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────┤
  │ F1-5    │ project/compilers/spec_transformer.py                     │ capital/position defaults, retail_profiles.yaml load         │
  ├─────────┼───────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────┤
  │ F1-6    │ project/strategy/runtime/dsl_runtime/interpreter.py       │ L221                                                         │
  └─────────┴───────────────────────────────────────────────────────────┴──────────────────────────────────────────────────────────────┘

  Severity-ranked issues

  1. Critical — exits.py broken import; latent NameError on any direct call path.
  2. High — oos_validation_pass/event_detected are no-ops; confirmations do not gate.
  3. High — PIT validation is a stub; lookahead protection is unverified at the templates layer.
  4. Medium — Overlay defaults silent in signal resolution; misconfiguration not surfaced.
  5. Medium — spec_transformer.py hardcoded capital assumptions affect sizing in templates.
  6. Medium — Random seed by ID length; same roll sequences for blueprints of equal ID length.

  Recommended actions

  1. Fix exits.py: add from typing import Tuple or convert to tuple[...] (Python 3.11+), then add a test that imports and calls check_exit_conditions.
  2. Either implement oos_validation_pass evaluation (query a stored OOS result) or rename it to always_true to make the semantic explicit. Document why event_detected is always true.
  3. Replace the stub PIT validators with real index-monotonicity and closed-left checks; gate template evaluation on pass.
  4. Move overlay defaults into blueprint schema with explicit None-propagation to signal resolution; remove inline hardcoded constants.
  5. Surface spec_transformer.py capital assumptions as named constants and test them.

  ---
  Audit 2: Reliability, Smoke, and Regression Tests

  Verified facts

  - project/reliability/cli_smoke.py supports five modes: engine, research, promotion, full, validate-artifacts.
  - project/reliability/contracts.py enforces PnL reconciliation to ±1e-8 (reconcile_portfolio_to_traces()), artifact ID consistency, and schema compliance per ArtifactSchemaSpec.
  - project/reliability/smoke_data.py uses np.random.default_rng(seed) for deterministic synthetic data; build_smoke_bars() and build_smoke_events() are fully seeded.
  - 100+ test files under tests/; coverage spans: DSL, engine execution, PnL aggregation, event detectors (PIT, signal-invariant), research pipeline, promotion artifacts, and live parsers.
  - test_determinism_verification.py explicitly asserts run-to-run reproducibility.
  - test_cross_artifact_reconciliation.py and test_artifact_contract.py validate artifact schema and cross-artifact consistency.

  Findings

  F2-1 (High): Research smoke asserts only candidate_rows >= 2
  run_research_smoke() validates that the discovery pipeline returned at least 2 candidates. This says nothing about correctness of the scoring, gate application, or statistical machinery. A regression in
  discovery logic that produces two plausible-looking rows would pass smoke.

  F2-2 (High): build_smoke_edge_candidates() is hardcoded to pass gates
  The smoke promotion path builds candidates by checking symbol=='BTCUSDT' and 'continuation' in template; those candidates receive robustness_score=0.85, gate-passing t-stats and effect sizes by construction.
   The smoke only tests the happy path. Failure paths (borderline candidates, gate rejections) are not exercised.

  F2-3 (Medium): No pytest configuration visible in pyproject.toml
  No [tool.pytest.ini_options] section is present. Test discovery relies on pytest defaults. This means no enforced markers, no timeout configuration, and no explicit filterwarnings. A noisy or slow test does
  not fail the suite.

  F2-4 (Medium): exits.py import error not caught by any test
  The broken Tuple import in exits.py would be caught only if a test imports or exercises that module. None of the identified test files explicitly target project.strategy.runtime.exits. The import error is a
  silent latent defect.

  F2-5 (Low): Smoke data builds a fixed synthetic regime profile
  build_smoke_bars() generates a simple trend-plus-noise series. No adverse regimes (gaps, zero-volume, extreme spread) are exercised by default. The smoke validates the happy path only.

  Evidence

  ┌─────────┬───────────────────────────────────────────────────────────────────┐
  │ Finding │                               File                                │
  ├─────────┼───────────────────────────────────────────────────────────────────┤
  │ F2-1    │ project/reliability/smoke_data.py — run_research_smoke()          │
  ├─────────┼───────────────────────────────────────────────────────────────────┤
  │ F2-2    │ project/reliability/smoke_data.py — build_smoke_edge_candidates() │
  ├─────────┼───────────────────────────────────────────────────────────────────┤
  │ F2-3    │ pyproject.toml — absence of [tool.pytest.ini_options]             │
  ├─────────┼───────────────────────────────────────────────────────────────────┤
  │ F2-4    │ project/strategy/runtime/exits.py, no test targeting it found     │
  ├─────────┼───────────────────────────────────────────────────────────────────┤
  │ F2-5    │ project/reliability/smoke_data.py — build_smoke_bars()            │
  └─────────┴───────────────────────────────────────────────────────────────────┘

  Severity-ranked issues

  1. High — Research smoke asserts row count only; scoring and gate regressions are invisible.
  2. High — Promotion smoke is gate-pass-only; no coverage of rejection paths or borderline candidates.
  3. Medium — No pytest configuration; no timeouts, markers, or warning filters.
  4. Medium — exits.py import error has no test coverage.
  5. Low — Smoke data is single-regime only.

  Recommended actions

  1. Add behavioral assertions to run_research_smoke(): validate at least one candidate has a non-trivial robustness score and that gates are actually applied (not bypassed).
  2. Add a rejection-path smoke: a candidate set where no candidate should pass, verifying the promotion gate correctly returns zero approvals.
  3. Add [tool.pytest.ini_options] to pyproject.toml with timeout, filterwarnings, and marker registration.
  4. Add a test that imports project.strategy.runtime.exits and calls check_exit_conditions to force the import error to surface.
  5. Add at least one adverse-regime smoke dataset (zero-volume bars, max-spread episode) to validate guard behavior under stress.

  ---
  Audit 3: Live Engine and Operational Risk

  Verified facts

  - Live-operation surfaces: project/live/ containing runner.py, kill_switch.py, health_checks.py, state.py, oms.py, drift.py, execution_attribution.py, ingest/manager.py, ingest/ws_client.py.
  - KillSwitchManager supports 8 reasons (FEATURE_DRIFT, EXECUTION_DRIFT, EXCESSIVE_DRAWDOWN, EXCHANGE_DISCONNECT, STALE_DATA, MICROSTRUCTURE_BREAKDOWN, ACCOUNT_SYNC_LOSS, MANUAL), persists status to JSON, and
   requires microstructure_recovery_streak=3 consecutive gate passes before reset.
  - LiveStateStore persists account state and kill-switch snapshot to a configurable JSON file path; loads on __init__ for crash recovery.
  - Execution degradation monitoring in LiveEngineRunner._assess_execution_degradation() blocks orders if avg_realized_net_edge_bps <= block_threshold and throttles if below warn threshold, grouped by (symbol,
   strategy, vol_regime, microstructure_regime).
  - Pre-trade microstructure gate in OrderManager.submit_order() calls kill_switch.check_microstructure(); raises OrderSubmissionBlocked if not tradable.
  - Paper and production environments are differentiated by separate env files (edge-live-engine-paper.env.example, edge-live-engine-production.env.example) pointing to different API base URLs
  (testnet.binancefuture.com vs fapi.binance.com).
  - No API secrets appear in any checked-in file; all credentials are environment-variable injected.

  Findings

  F3-1 (Critical): UnwindOrchestrator is a non-functional stub
  kill_switch.py defines UnwindOrchestrator with async unwind_all() that only logs "Unwinding all positions". There is no OMS integration, no order cancellation, and no position flattening logic. The
  kill-switch correctly blocks new orders but cannot close existing ones. Any live position at trigger time remains open until manually intervened.

  F3-2 (High): No position reconciliation on restart
  LiveStateStore.from_snapshot() loads the last-persisted account snapshot. There is no code path that reconciles this snapshot against the exchange's current open positions on startup. If the process crashed
  between submitting and acknowledging a fill, the loaded state and exchange state diverge silently.

  F3-3 (High): WebSocket reconnect exhaustion is silent
  BinanceWebSocketClient retries up to max_retries=5 with exponential backoff. After exhaustion it stops reconnecting. This does not automatically trigger EXCHANGE_DISCONNECT or STALE_DATA kill-switch reasons.
   The data queue goes empty, and DataHealthMonitor would eventually flag stale streams — but only if check_health() is being polled, and the connection between health check failure and kill-switch trigger is
  not explicitly wired.

  F3-4 (High): Data health checks freshness only, not correctness
  DataHealthMonitor.check_health() reports a stream as healthy if it received any event within stale_threshold_sec. A feed delivering stale or replayed prices would be declared healthy. There is no bid-ask
  consistency check, timestamp-monotonicity validation, or outlier detection.

  F3-5 (Medium): Base systemd unit hardcodes config path
  edge-live-engine.service executes --config /opt/edge/project/configs/golden_certification.yaml. The production unit (edge-live-engine-production.service) uses ${EDGE_LIVE_CONFIG} from EnvironmentFile. If the
   base unit is deployed instead of the production variant — a plausible operator error — the engine runs against the golden-certification research config, not the live production config.

  F3-6 (Medium): LiveStateStore has no distributed lock
  State is persisted to a JSON file with no file-locking mechanism. Running two engine instances pointing at the same snapshot path would produce corrupt state. The deployment assumes single-instance, but this
   is not enforced programmatically.

  F3-7 (Medium): STALE_DATA kill-switch not auto-triggered on feed loss
  The STALE_DATA reason exists in KillSwitchReason but there is no code in health_checks.py or runner.py that calls kill_switch.trigger(KillSwitchReason.STALE_DATA) when DataHealthMonitor.check_health()
  returns unhealthy. The trigger exists semantically but is not wired to the monitoring loop.

  F3-8 (Low): RestartSec=5 with Restart=on-failure could cause rapid restart loops
  If the process fails immediately on startup (e.g., bad config, missing snapshot path), systemd will restart it every 5 seconds. There is no StartLimitIntervalSec / StartLimitBurst guard in either service
  file. A misconfigured deployment could thrash indefinitely.

  Evidence

  ┌─────────┬────────────────────────────────────────────────────────────────────────────────────────────────┐
  │ Finding │                                              File                                              │
  ├─────────┼────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ F3-1    │ project/live/kill_switch.py — UnwindOrchestrator.unwind_all()                                  │
  ├─────────┼────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ F3-2    │ project/live/state.py — from_snapshot(), no reconcile call                                     │
  ├─────────┼────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ F3-3    │ project/live/ingest/ws_client.py — retry loop termination; health_checks.py — no wired trigger │
  ├─────────┼────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ F3-4    │ project/live/health_checks.py — check_health()                                                 │
  ├─────────┼────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ F3-5    │ deploy/systemd/edge-live-engine.service                                                        │
  ├─────────┼────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ F3-6    │ project/live/state.py — save_snapshot()                                                        │
  ├─────────┼────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ F3-7    │ project/live/health_checks.py — check_health(), kill_switch.py — STALE_DATA reason unused      │
  ├─────────┼────────────────────────────────────────────────────────────────────────────────────────────────┤
  │ F3-8    │ deploy/systemd/edge-live-engine.service, edge-live-engine-production.service                   │
  └─────────┴────────────────────────────────────────────────────────────────────────────────────────────────┘

  Severity-ranked issues

  1. Critical — UnwindOrchestrator is a stub; kill-switch cannot close positions.
  2. High — No exchange position reconciliation on restart; state divergence undetected.
  3. High — WebSocket reconnect exhaustion not wired to kill-switch trigger.
  4. High — Data health checks freshness only; corrupted/stale prices pass as healthy.
  5. Medium — Base systemd unit hardcodes config path; production variant not enforced.
  6. Medium — No file lock on LiveStateStore; multi-instance deployment would corrupt state.
  7. Medium — STALE_DATA kill-switch reason never triggered by monitoring code.
  8. Low — No systemd restart-loop guard (StartLimitIntervalSec/StartLimitBurst).

  Recommended actions

  1. Implement UnwindOrchestrator.unwind_all() with OMS integration (cancel all open orders, submit market close for each open position) before any production use of the kill-switch.
  2. Add a startup reconciliation path: on LiveStateStore load, query exchange open positions and reconcile against snapshot; log all discrepancies; block engine start if reconciliation fails.
  3. Wire BinanceWebSocketClient reconnect exhaustion to KillSwitchManager.trigger(EXCHANGE_DISCONNECT).
  4. Wire DataHealthMonitor.check_health() unhealthy result to KillSwitchManager.trigger(STALE_DATA) in the runner's monitoring loop.
  5. Add StartLimitIntervalSec=60 and StartLimitBurst=3 to both systemd unit files.
  6. Rename the base unit to edge-live-engine-dev.service or remove it; make the production unit the only deployable unit. Document the distinction explicitly.
  7. Add a file advisory lock (fcntl.flock) to LiveStateStore.save_snapshot() and load_snapshot().

  ---
  Cross-Cutting Risks

  XC-1: Kill-switch fires but does not close positions (F3-1 + F1-1)
  The strategy runtime can generate exit logic, and the kill-switch can block new orders, but the unwind path is a stub. Between them, a triggered kill-switch leaves existing positions alive and unmanaged.
  This is the highest cross-cutting risk in the system.

  XC-2: Confirmation signals as theatre (F1-2 + F2-1)
  oos_validation_pass and event_detected are unconditionally True at runtime. The smoke only asserts row count. A bug that corrupted confirmation signal evaluation would pass both the runtime and the smoke
  suite undetected. The system presents a validation surface that is not actually evaluating anything.

  XC-3: Exit path coverage gap (F1-1 + F2-4)
  exits.py has a broken import and no test coverage. The numba state machine handles exits for the primary execution path, but exits.py existing alongside it creates a maintenance trap: future refactors could
  inadvertently route to it, triggering a NameError in production with no prior warning from tests.

  XC-4: Freshness ≠ correctness (F3-4 + F3-7)
  Data health is declared by recency alone. STALE_DATA is never triggered. A degraded feed delivering corrupted prices would pass health monitoring, enter the signal frame, generate positions, and submit
  orders — with no automated kill-switch intervention.

  ---
  Immediate Fix Queue

  Ranked by impact × ease:

  ┌─────┬────────────────────────────────────────────────────────────────────────────────────┬──────────┬─────────┐
  │  #  │                                       Action                                       │ Severity │ Effort  │
  ├─────┼────────────────────────────────────────────────────────────────────────────────────┼──────────┼─────────┤
  │ 1   │ Add from typing import Tuple to exits.py; add a smoke test importing it            │ Critical │ Trivial │
  ├─────┼────────────────────────────────────────────────────────────────────────────────────┼──────────┼─────────┤
  │ 2   │ Wire DataHealthMonitor unhealthy → KillSwitchManager.trigger(STALE_DATA) in runner │ High     │ Low     │
  ├─────┼────────────────────────────────────────────────────────────────────────────────────┼──────────┼─────────┤
  │ 3   │ Wire WebSocket reconnect exhaustion → kill_switch.trigger(EXCHANGE_DISCONNECT)     │ High     │ Low     │
  ├─────┼────────────────────────────────────────────────────────────────────────────────────┼──────────┼─────────┤
  │ 4   │ Add systemd StartLimitIntervalSec=60 / StartLimitBurst=3 to both unit files        │ Low      │ Trivial │
  ├─────┼────────────────────────────────────────────────────────────────────────────────────┼──────────┼─────────┤
  │ 5   │ Rename oos_validation_pass and event_detected to always_true or document clearly   │ High     │ Low     │
  ├─────┼────────────────────────────────────────────────────────────────────────────────────┼──────────┼─────────┤
  │ 6   │ Replace stub validate_pit_invariants() with index-monotonicity check               │ High     │ Low     │
  ├─────┼────────────────────────────────────────────────────────────────────────────────────┼──────────┼─────────┤
  │ 7   │ Add promotion smoke rejection-path test (zero candidates should pass)              │ High     │ Low     │
  ├─────┼────────────────────────────────────────────────────────────────────────────────────┼──────────┼─────────┤
  │ 8   │ Add [tool.pytest.ini_options] with timeout and filterwarnings                      │ Medium   │ Low     │
  ├─────┼────────────────────────────────────────────────────────────────────────────────────┼──────────┼─────────┤
  │ 9   │ Implement UnwindOrchestrator.unwind_all() with real OMS cancellation               │ Critical │ High    │
  ├─────┼────────────────────────────────────────────────────────────────────────────────────┼──────────┼─────────┤
  │ 10  │ Add startup exchange reconciliation path to LiveStateStore load sequence           │ High     │ Medium  │
  └─────┴────────────────────────────────────────────────────────────────────────────────────┴──────────┴─────────┘

  ---
  Appendix

  Strategy surfaces found

  - project/strategy/dsl/ — 10 modules: schema.py, conditions.py, normalize.py, validate.py, contract_v1.py, policies.py, references.py, schema_v2.py (shim), templates.py, __init__.py
  - project/strategy/templates/ — spec.py, compiler.py, generator.py, evaluate.py, data_bundle.py, validation.py
  - project/strategy/runtime/ — base.py, exits.py (broken), event_strategy_utils.py, registry.py, dsl_interpreter_v1.py
  - project/strategy/runtime/dsl_runtime/ — execution_context.py, signal_resolution.py, evaluator.py, interpreter.py
  - project/strategy/models/blueprint.py — re-export façade

  Compiler/template/runtime surfaces found

  - project/compilers/executable_strategy_spec.py — ExecutableStrategySpec frozen model + to_blueprint_dict() / from_blueprint()
  - project/compilers/spec_transformer.py — transform_blueprint_to_spec() with hardcoded capital defaults

  Smoke/reliability surfaces found

  - project/reliability/cli_smoke.py — 5-mode orchestrator
  - project/reliability/contracts.py — schema validation, PnL reconciliation, artifact integrity
  - project/reliability/smoke_data.py — deterministic synthetic data + smoke pipeline runners
  - tests/ — 100+ test files; key: test_determinism_verification.py, test_cross_artifact_reconciliation.py, test_artifact_contract.py, test_event_pit_signal_invariant.py

  Live-engine and operational surfaces found

  - project/live/runner.py — LiveEngineRunner with degradation monitoring
  - project/live/kill_switch.py — KillSwitchManager (8 reasons, persistent), UnwindOrchestrator (stub)
  - project/live/health_checks.py — DataHealthMonitor, check_kill_switch_triggers(), build_runtime_certification_manifest()
  - project/live/state.py — LiveStateStore, AccountState, PositionState
  - project/live/oms.py — OrderManager, LiveOrder, OrderStatus
  - project/live/drift.py — calculate_feature_drift(), monitor_execution_drift()
  - project/live/execution_attribution.py — ExecutionAttributionRecord, build_execution_attribution_record()
  - project/live/ingest/manager.py — LiveDataManager (async WebSocket)
  - project/live/ingest/ws_client.py — BinanceWebSocketClient (exponential backoff, max 5 retries)
  - project/live/ingest/parsers.py — parse_kline_event(), parse_book_ticker_event()

  Deployment surfaces found

  - deploy/systemd/edge-live-engine.service — hardcoded config path, no restart loop guard
  - deploy/systemd/edge-live-engine-production.service — EnvironmentFile injection, same gap
  - deploy/env/edge-live-engine-production.env.example — blank API key/secret placeholders
  - deploy/env/edge-live-engine-paper.env.example — testnet base URL