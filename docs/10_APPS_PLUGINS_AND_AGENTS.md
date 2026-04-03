# Apps, plugins, and agents

This document explains the repo surfaces that sit beside the core operator and pipeline path.

## ChatGPT app surface

Location:

- `project/apps/chatgpt/`

What it contains:

- `handlers.py` — wraps operator, reporting, dashboard, and related repo actions
- `tool_catalog.py` — tool definitions and intent metadata
- `server.py` — MCP/server blueprint surface
- `resources.py` — widget/resource payloads
- `cli.py` — inspection and serve helpers
- `ui/operator_dashboard.html` — lightweight dashboard UI surface

Console entrypoint:

```bash
edge-chatgpt-app backlog
edge-chatgpt-app blueprint
edge-chatgpt-app widget
edge-chatgpt-app serve --host 127.0.0.1 --port 8000 --path /mcp
```

Use this surface when you are integrating the repo with a ChatGPT-app or MCP-style operator experience. It is not the main research runtime.

## Repo-local plugins

### `plugins/edge-agents/`

This is a repo-local Codex/plugin surface aligned with the repo's bounded workflow.

It contains:

- skill folders for repo orientation, coordinator flow, analyst review, compiler flow, and thesis bootstrap
- shell wrappers for preflight, plan, run, compare, verify, and bootstrap actions
- local hooks that warn on contract-sensitive edits and recent runs

This is an interface layer around the canonical repo flow, not an alternate architecture.

### `plugins/edge-plugins/`

This holds plugin metadata for the plugin package surface.

## Agent playbooks

Location:

- `agents/`

What is there:

- `analyst.md`
- `compiler.md`
- `mechanism_hypothesis.md`
- `coordinator_playbook.md`
- example and template documents for campaign ledgers, proposal compilation, and run analysis

These files are human-oriented playbooks that sit above the core code path. Use them to structure work, not as code truth.

## Relationship to the core repo

These surfaces are important, but they are secondary to the operator and service layers.

Correct dependency direction:

- app/plugin/agent surfaces should wrap or call the canonical operator path
- they should not invent a parallel research lifecycle
- policy should still live in canonical code and specs

## When to use these surfaces

Use them when you need:

- a guided operator interface
- repo-local automation helpers
- a human-readable playbook for recurring tasks
- a compact dashboard for current operator state

Do not use them as the primary source of truth for:

- proposal schema
- stage contracts
- promotion policy
- packaged thesis contract

Those remain owned by code, specs, and generated inventories.
