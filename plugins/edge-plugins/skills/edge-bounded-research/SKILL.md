---
name: edge-bounded-research
description: Use when planning or executing a bounded Edge research run through the proposal and experiment workflow.
---

# Edge Bounded Research

## Purpose

Use this skill for proposal-driven research work in Edge.

## Core Discipline

Edge research is bounded, not open-ended. A valid run should stay inside one:

- regime
- mechanism
- tradable expression
- primary trigger family
- template family

## Canonical Workflow

1. Query knowledge and prior memory first.
2. Translate the proposal to repo-native config.
3. Plan before executing.
4. Execute one bounded run.
5. Review artifacts in strict order.
6. End with exactly one decision: `keep`, `modify`, or `kill`.

## Useful Commands

Plan a proposal:

```bash
plugins/edge-plugins/scripts/edge_plan_proposal.sh /abs/path/to/proposal.yaml planned_run_id
```

Run contract verification after code or config changes:

```bash
plugins/edge-plugins/scripts/edge_verify_contracts.sh
```

Run experiment verification after a completed run:

```bash
.venv/bin/python -m project.scripts.run_researcher_verification --mode experiment --run-id <run_id>
```

## Stop Conditions

Stop if:

- the plan widens beyond one regime or mechanism
- artifacts are missing or contradictory
- schema validation fails
- the result only survives after weakening costs or gates
