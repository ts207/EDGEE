# Developer Onboarding

This is the first doc to read as an engineer working in this codebase.

---

## Repo Layout

```
project/           Core source code
  pipelines/       Orchestration and stage entrypoints
  events/          Detector logic, family logic, registry-facing event behavior
  features/        Shared feature and regime helpers
  research/        Discovery, evaluation, promotion, diagnostics
  contracts/       Artifact and stage contracts
  strategy/        DSL, templates, runtime
  spec_registry/   Read-only YAML spec loaders
  spec_validation/ Ontology, grammar, loader, and search-spec validation
  scripts/         Operator and maintenance entrypoints
  tests/           Regression and contract coverage

spec/              YAML specs: events, features, states, grammar, search, strategies
docs/              Maintained operator and reference docs (you are here)
data/              Runtime outputs — not source files unless maintained as fixtures
deploy/            Systemd units and env templates for live engine
```

---

## Install

```bash
pip install -e .
# With Nautilus Trader runtime:
pip install -e ".[nautilus]"
```

**Requirements:** Python 3.11+

---

## Common Build Commands

```bash
make test           # Full test suite
make test-fast      # Excludes @pytest.mark.slow tests
make lint           # Ruff lint check
make format-check   # Ruff format check (no changes)
make format         # Apply formatting
make discover-edges # Broad edge discovery
```

Plan-only run (verify a run is scoped correctly before executing):

```bash
edge-run-all --run_id demo --symbols BTCUSDT --start 2024-01-01 --end 2024-01-31 --plan_only 1
```

---

## CLI Entry Points

All registered in `pyproject.toml`:

| Command | Module |
|---|---|
| `edge-run-all` | `project.pipelines.run_all:main` |
| `edge-live-engine` | `project.scripts.run_live_engine:main` |
| `edge-phase2-discovery` | `project.pipelines.research.phase2_candidate_discovery:main` |
| `edge-promote` | `project.pipelines.research.promote_candidates:main` |
| `edge-smoke` | `project.reliability.cli_smoke:main` ⚠️ |
| `compile-strategy-blueprints` | `project.pipelines.research.compile_strategy_blueprints:main` |
| `build-strategy-candidates` | `project.pipelines.research.build_strategy_candidates:main` |
| `ontology-consistency-audit` | `project.scripts.ontology_consistency_audit:main` |

> ⚠️ **Known issue:** `project/reliability/cli_smoke.py` does not currently define a top-level `def main()`. The `edge-smoke` command will fail with `AttributeError` until this is resolved. Use `PYTHONPATH=. python3 -m project.reliability.cli_smoke --mode research` as a workaround.

---

## Coding Style

- Python 3.11 target
- 4-space indentation
- Ruff defaults, line length 100
- `snake_case` for functions, variables, file names
- `UPPER_SNAKE_CASE` for constants and spec identifiers
- Explicit, domain-specific names over vague generic names
- Keep CLI entrypoints and stage boundaries explicit — do not hide orchestration behind ambiguous helper layers

---

## Testing Rules

Test file locations follow the owned surface:

| Surface | Test location |
|---|---|
| Event logic | `project/tests/events/` |
| Pipeline behavior | `project/tests/pipelines/` |
| Architecture and contract rules | `project/tests/architecture/`, `project/tests/contracts/` |
| Research behavior | `project/tests/research/` |

Mark long-running tests with `@pytest.mark.slow` so `make test-fast` stays fast.

---

## Change Discipline

Before any broad refactor:
1. Identify the contract you are changing.
2. Identify the tests that pin it.
3. Keep the write set focused.

If a change affects detector semantics, pipeline contracts, feature definitions, or search/promotion behavior — update or add tests.

**When editing docs:**
- Keep `CLAUDE.md`, `AGENTS.md`, and `GEMINI.md` aligned on core policy.
- Do not describe repo behavior that is not actually implemented.

---

## Next Docs

After this one:

1. [ARCHITECTURE.md](./ARCHITECTURE.md) — package surfaces, canonical imports, removed packages
2. [MAINTENANCE_CHECKLIST.md](./MAINTENANCE_CHECKLIST.md) — what to update when changing contracts or surfaces
3. [TECH_STACK.md](./TECH_STACK.md) — dependencies and versions
