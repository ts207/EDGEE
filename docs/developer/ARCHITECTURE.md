# Architecture

This document records the current package-surface decisions and import boundaries. It exists to prevent surface sprawl and to make the correct import path obvious for new code.

---

## Canonical Surfaces

These are the primary public surfaces. Prefer these for all new cross-domain imports.

| Surface | Purpose |
|---|---|
| `project.pipelines.run_all` | Canonical orchestration entrypoint |
| `project.research.services.candidate_discovery_service` | Canonical discovery service surface |
| `project.research.services.promotion_service` | Canonical promotion service surface |
| `project.research.services.reporting_service` | Canonical reporting surface |
| `project.pipelines.research.phase2_candidate_discovery` | Pipeline entrypoint only — helper/policy code belongs in research service/spec modules |
| `project.pipelines.research.promote_candidates` | Pipeline entrypoint only — promotion policy belongs in research service/promotion modules |
| `project.strategy.dsl` | Canonical public Strategy DSL import surface |
| `project.strategy.templates` | Canonical public strategy-template import surface |
| `project.strategy.runtime` | Canonical public runtime-facing strategy surface |

---

## Explicit Package-Root Surfaces

These package roots exist as deliberate import surfaces, not implicit namespace folders. Import from the package root only.

| Package | Purpose | Import rule |
|---|---|---|
| `project.artifacts` | Artifact path and payload helpers for run- and report-scoped outputs | Import from package root |
| `project.compilers` | Executable strategy-spec and blueprint transformation | Import from package root |
| `project.eval` | Multiplicity and split-building helpers | Import from package root |
| `project.experiments` | Experiment config loading and registry helpers | Import from package root |
| `project.live` | Live runner, kill-switch, and runtime health helpers | Import from package root |
| `project.portfolio` | Allocation, sizing, and risk-budget helpers | Import from package root |
| `project.spec_registry` | Read-only YAML spec loaders and blueprint policy defaults | Import from package root only — not from `.loaders` or `.policy` directly |
| `project.spec_validation` | Ontology, grammar, loader, and search-spec validation helpers | Import from package root |

---

## Explicit Subpackage Roots

These are package roots for active subdomains. Keep them thin. They should not absorb business logic.

- `project.pipelines.clean`
- `project.pipelines.features`
- `project.pipelines.ingest`
- `project.pipelines.smoke`
- `project.research.clustering`
- `project.research.reports`
- `project.research.utils`

For `project.pipelines.clean`, `project.pipelines.features`, and `project.pipelines.ingest`, the package roots are lazy import shims over concrete stage entrypoints. Keep `__getattr__`-based dispatch minimal and deterministic.

---

## Compatibility Facades

These surfaces are still allowed, but only as pure re-export wrappers.

- `project.apps.*`
- `project.execution.*`
- `project.infra.*`

**Compatibility wrappers must:**
- Include the `# COMPAT WRAPPER` marker at the top.
- Import from canonical `project.*` modules.
- Contain no local `def` or `class` logic.

If a facade needs new behavior, add it to the canonical source module and re-export it — do not implement it inside the wrapper.

---

## Strategy Namespace Boundary Policy

| Package | Status | Rule |
|---|---|---|
| `project.strategy` | **Canonical** | All new models, DSL definitions, and template logic must be added here. |
| `project.strategy.runtime` | **Legacy implementation tree** | Currently hosts concrete runtime logic (e.g. `dsl_runtime`). Still heavily used — 16 importers. Do not add new business logic here. |
| `project.strategy._runtime` | **Target consolidation destination** | When the public surface is fully decoupled, move concrete implementation here or into `project.strategy.runtime` internals. |

---

## Removed Surfaces

These packages have been deleted. Do not re-create them.

| Package | Replacement |
|---|---|
| `project.research.compat` | Canonical research service/spec modules |
| `project.strategy_dsl` | `project.strategy.dsl` |
| `project.strategy_templates` | `project.strategy.templates` |

If any of these reappear, treat it as a regression and remove immediately.

---

## Support Module Pattern

Large policy or orchestration modules should split into focused support modules before architecture thresholds are relaxed. Current examples:

- `project/pipelines/execution_engine_support.py`
- `project/research/services/candidate_discovery_diagnostics.py`
- `project/research/services/candidate_discovery_scoring.py`
- `project/research/promotion/promotion_decision_support.py`
- `project/research/promotion/promotion_result_support.py`
- `project/research/promotion/promotion_reporting_support.py`

---

## Current Policy Summary

New public or cross-domain code should:
- Prefer explicit package-root surfaces where they exist.
- Use `project.strategy.dsl`, `project.strategy.templates`, `project.strategy.runtime` for strategy-related imports.
- Use research service modules instead of removed compatibility packages.

Transitional imports are only allowed from the currently documented importer set, enforced in architecture tests (`project/tests/test_architectural_integrity.py`).

When migrating call sites: update tests and scripts before deleting compatibility modules.

---

## Keeping This Doc Current

After any package-surface migration:
1. Recompute architecture metrics: `python3 -m project.scripts.build_system_map --check`
2. Update `docs/generated/architecture_metrics.json`.
3. Update the transitional importer counts in this doc if they changed.
4. Update `project/tests/test_architectural_integrity.py` to match.
