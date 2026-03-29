# Testing And Maintenance

This repository has a research-quality bar, not just a syntax bar. A run can be mechanically executable while still failing the maintained quality gate.

## Fastest Useful Checks

Use these first:

```bash
make test-fast
.venv/bin/python -m project.reliability.cli_smoke --mode full --root /tmp/edge_smoke
```

`test-fast` is the maintained quick regression gate. The full smoke path is useful after pipeline or artifact-contract changes.

## Stronger Baseline

Use this when you want the repo's stricter stabilization baseline:

```bash
make minimum-green-gate
```

This is the best single command when you need confidence that the repository is in a generally acceptable state.

## Other Important Maintenance Targets

From the maintained `make` surface:

- `golden-workflow`
- `golden-certification`
- `governance`
- `benchmark-maintenance-smoke`
- `benchmark-maintenance`
- `lint`
- `format-check`
- `style`

## When To Run Which Check

### Docs-only changes

Usually:

- structural spot-check
- stale-link check if relevant

### Detector, search, robustness, or gate changes

At minimum:

- `make test-fast`
- relevant targeted tests
- smoke if the change touches stage wiring or artifacts

### Pipeline orchestration or contract changes

At minimum:

- `make test-fast`
- full smoke
- artifact reconciliation on one bounded real or synthetic run

## Maintenance Rules

- do not rely on exit code alone
- inspect artifacts after any material pipeline change
- prefer bounded reruns over broad reruns
- leave behind the exact command and run id used for verification

## What To Record After Verification

For every meaningful change, record:

- what was changed
- what command was run
- whether artifacts reconciled
- whether the result was a mechanical pass, statistical pass, or both

That keeps maintenance evidence aligned with the repo's research discipline.
