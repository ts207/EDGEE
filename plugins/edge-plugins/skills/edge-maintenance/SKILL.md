---
name: edge-maintenance
description: Use when validating Edge changes against the maintained verification and maintenance commands.
---

# Edge Maintenance

## Purpose

Use this skill for verification, stabilization, and maintenance work in Edge.

## Fastest Useful Checks

Use these first:

```bash
make test-fast
.venv/bin/python -m project.reliability.cli_smoke --mode full --root /tmp/edge_smoke
```

## Stronger Baseline

When you need broader confidence:

```bash
make minimum-green-gate
```

## Change Guidance

- Detector or gate changes:
  run `make test-fast`, relevant targeted tests, and smoke if artifacts or stage wiring changed.
- Pipeline or contract changes:
  run `make test-fast`, full smoke, and artifact reconciliation on a bounded run.
- After any code or config change:
  run `plugins/edge-plugins/scripts/edge_verify_contracts.sh`.

## Recording Rule

Always leave behind:

- what changed
- what command was run
- whether artifacts reconciled
- whether the result was mechanical, statistical, or both
