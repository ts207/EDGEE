# Maintenance Checklist

Use this checklist whenever a change touches contracts, generated docs, orchestration, or service/package ownership. It defines what must be updated to keep the codebase and docs consistent.

---

## Contracts and Generated Docs

When you change `project/contracts/pipeline_registry.py` or `project/contracts/system_map.py`:

- [ ] Regenerate the system map artifacts in `docs/generated/`:
  ```bash
  python3 -m project.scripts.build_system_map --check
  ```
- [ ] Run the contract and generated-artifact tests.
- [ ] Do not leave generated docs as stale snapshots.

When you change detector coverage or the ontology:

- [ ] Regenerate detector coverage docs:
  ```bash
  python3 -m project.scripts.detector_coverage_audit \
    --md-out docs/generated/detector_coverage.md \
    --json-out docs/generated/detector_coverage.json \
    --check
  ```

---

## Research Services and Wrappers

- Keep research pipeline wrappers entrypoint-only. Reusable helper logic belongs in `project.research.services.*`, `project.research.promotion.*`, or `project.specs.*`.
- If a test needs a helper, import the canonical service/spec module — not a pipeline wrapper.
- When adding a new helper to discovery or promotion, decide whether it is service-owned or private before exporting it.
- If `candidate_discovery_service.py`, `promotion_decisions.py`, or `promotion_reporting.py` grows large again, split focused helpers into support modules instead of loosening the file-size threshold.

---

## Strategy Surfaces

- Prefer `project.strategy.dsl` and `project.strategy.templates` for all new public or cross-domain imports.
- If you touch `project.strategy.__init__`, avoid eager imports that can reintroduce circular-import chains.
- `project.strategy_dsl` and `project.strategy_templates` are removed packages. If they reappear, that is a regression.

---

## Compatibility Facades

- `project.apps.*`, `project.execution.*`, and `project.infra.*` are compatibility facades.
- Keep wrapper modules as pure re-exports with the `# COMPAT WRAPPER` marker and no local `def` or `class` logic.
- If a facade needs new behavior, add it to the canonical source module and re-export it rather than implementing it inside the wrapper.

---

## Package Roots

- Keep package-root `__init__.py` files intentionally small. They should re-export stable symbols, not own heavy logic.
- For lazy pipeline package roots (`project.pipelines.clean`, `project.pipelines.features`, `project.pipelines.ingest`), keep `__getattr__`-based dispatch minimal and deterministic.
- Prefer explicit package-root surfaces where they exist: `project.artifacts`, `project.compilers`, `project.eval`, `project.experiments`, `project.live`, `project.portfolio`, `project.spec_validation`.

---

## Orchestration

- Keep `project/pipelines/run_all.py` as a coordinator over focused helpers. If it grows materially, split logic into `run_all_support`, `run_all_bootstrap`, or `run_all_finalize`.
- Keep `project/pipelines/execution_engine.py` coordinator-oriented. Shared helper logic belongs in `project/pipelines/execution_engine_support.py`.
- Add or keep characterization tests before moving planning, bootstrap, or terminalization logic in the orchestrator.

---

## Architecture Tests and Metrics

After any package-surface migration:

- [ ] Recompute architecture metrics and refresh `docs/generated/architecture_metrics.json`.
- [ ] Update `docs/developer/ARCHITECTURE.md` when transitional importer counts or dispositions change.
- [ ] Keep `project/tests/test_architectural_integrity.py` aligned with the current canonical package model.

---

## Research Calibration

When retuning research defaults:

- [ ] Keep drift thresholds in `project/research/services/run_comparison_service.py` aligned with CLI defaults in `project/pipelines/pipeline_planning.py`.
- [ ] Keep sample-quality policies in `project/research/services/candidate_discovery_service.py` aligned with the current research profiles.
- [ ] Update `docs/researcher/RESEARCH_CALIBRATION_BASELINE.md` (if present) to reflect the new defaults.
- [ ] Update pinned tests in `tests/research/services/` and `tests/pipelines/`.

---

## Benchmark Maintenance

When modifying core event detectors or feature schemas:

- [ ] Run the benchmark maintenance cycle to verify the change does not degrade maintained slices:
  ```bash
  make benchmark-maintenance
  ```
- [ ] If a maintained benchmark slice degrades, follow the escalation path in `docs/researcher/BENCHMARK_GUIDE.md`.

---

## Docs Alignment

When behavior changes in any of the following areas, check that these docs are still accurate:

| Area changed | Docs to review |
|---|---|
| CLI entry points | `developer/ONBOARDING.md` |
| Package surfaces or import rules | `developer/ARCHITECTURE.md` |
| Feature registry additions | `researcher/FEATURE_CATALOG.md` |
| Event families or templates | `researcher/ONTOLOGY.md` |
| Calibration defaults | `researcher/RESEARCH_CALIBRATION_BASELINE.md` |
| Benchmark status or slice list | `researcher/BENCHMARK_GUIDE.md` |
| Synthetic profiles or truth validation | `researcher/SYNTHETIC_DATASETS.md` |
