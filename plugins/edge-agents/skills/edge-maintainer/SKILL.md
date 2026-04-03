---
name: edge-maintainer
description: Route repo changes through the correct validation, generated-doc regeneration, plugin sync, and maintenance commands. Use when the task is developer upkeep, doc drift, plugin upkeep, app-surface maintenance, or figuring out the smallest correct verification loop.
---

# Edge Maintainer

Use this skill for developer maintenance and repo-upkeep work in `/home/irene/Edge`.

## Read first

1. `docs/08_TESTING_AND_MAINTENANCE.md`
2. `docs/04_COMMANDS_AND_ENTRY_POINTS.md`
3. `docs/10_APPS_PLUGINS_AND_AGENTS.md`
4. `Makefile`

## Role

- Route the current change through the smallest correct maintenance loop.
- Prefer canonical repo entrypoints over ad hoc script sequences.
- Regenerate generated docs instead of editing them by hand.
- Keep plugin maintenance thin and repo-aligned.

## Primary routing table

### Proposal or operator-surface change

Use:

```bash
make validate
PYTHONPATH=. ./.venv/bin/python -m project.scripts.generate_operator_surface_inventory
```

Then inspect:

- `README.md`
- `docs/00_START_HERE.md`
- `docs/03_OPERATOR_WORKFLOW.md`
- `docs/04_COMMANDS_AND_ENTRY_POINTS.md`

### Event, ontology, or registry change

Use:

```bash
make validate
PYTHONPATH=. ./.venv/bin/python -m project.scripts.build_event_contract_artifacts
PYTHONPATH=. ./.venv/bin/python -m project.scripts.build_system_map
```

Then inspect:

- `docs/generated/event_contract_reference.md`
- `docs/02_REPOSITORY_MAP.md`
- `docs/05_ARTIFACTS_AND_INTERPRETATION.md`

### Thesis packaging or overlap change

Use:

```bash
make package
PYTHONPATH=. ./.venv/bin/python -m project.scripts.build_thesis_overlap_artifacts
```

Then inspect:

- `data/live/theses/index.json`
- `docs/generated/seed_thesis_catalog.md`
- `docs/generated/seed_thesis_packaging_summary.md`
- `docs/generated/thesis_overlap_graph.md`
- `docs/09_THESIS_BOOTSTRAP_AND_PROMOTION.md`
- `docs/11_LIVE_THESIS_STORE_AND_OVERLAP.md`

### Architectural boundary change

Use:

```bash
make validate
PYTHONPATH=. ./.venv/bin/python -m project.scripts.build_system_map
```

Then inspect:

- `docs/ARCHITECTURE_SURFACE_INVENTORY.md`
- `docs/ARCHITECTURE_MAINTENANCE_CHECKLIST.md`
- `docs/generated/system_map.md`

### Plugin change

Use:

```bash
./plugins/edge-agents/scripts/edge_sync_plugin.sh check
./plugins/edge-agents/scripts/edge_sync_plugin.sh sync
```

### Repo-level validation or governance work

Use:

```bash
./plugins/edge-agents/scripts/edge_validate_repo.sh
./plugins/edge-agents/scripts/edge_governance.sh
```

## ChatGPT app surface

When the task touches `project/apps/chatgpt/`, use:

```bash
./plugins/edge-agents/scripts/edge_chatgpt_app.sh backlog
./plugins/edge-agents/scripts/edge_chatgpt_app.sh blueprint
./plugins/edge-agents/scripts/edge_chatgpt_app.sh widget
./plugins/edge-agents/scripts/edge_chatgpt_app.sh serve --host 127.0.0.1 --port 8000 --path /mcp
```

Treat this as an interface layer around canonical operator surfaces, not a separate runtime.

## Hard rules

- Do not teach wrappers as if they own repo policy.
- Do not manually edit `docs/generated/*` when a generator exists.
- Do not stop at `make validate` if the change type implies additional regeneration.
- If plugin source changes, remember that the installed plugin cache may still be stale until synced.
