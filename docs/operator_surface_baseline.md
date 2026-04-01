# Operator Surface Baseline

This document records the current operator-facing execution surfaces after Sprint 1.

## Canonical

Use one command family for normal research issuance:

- `edge operator preflight`
- `edge operator plan`
- `edge operator run`

`edge` and `edge-backtest` point to the same CLI surface. `backtest` remains an alias.

## Transitional

These remain valid, but they are no longer the recommended front door for normal operator work:

- `python -m project.research.agent_io.proposal_to_experiment`
- `python -m project.research.agent_io.execute_proposal`
- `python -m project.research.agent_io.issue_proposal`
- `python -m project.pipelines.run_all`

Use them when you need direct inspection of internal boundaries or already know the exact bounded slice.

## Deprecated As Primary Operator Entry

These are still maintained for compatibility or specialized workflows, but should not be the first command an operator reaches for:

- broad `make` orchestration targets for routine bounded research
- direct `run_all` invocation for proposal-shaped work
- ad hoc shell wrappers around proposal compilation and run issuance

## Sprint 1 Decision

The repo keeps its existing engines and wrappers, but the preferred workflow is now:

`preflight -> plan -> run`

That is the stable operator contract for local research work.
