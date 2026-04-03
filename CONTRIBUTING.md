# Contributing

## Development setup

Install the package in editable mode:

```bash
pip install -e .
```

Use the repo virtualenv if present. The codebase assumes Python 3.11+.

## Working rules

1. Make changes in the canonical path, not compatibility wrappers.
2. Keep pipeline names, contracts, docs, and tests aligned.
3. Add or update regression coverage for behavior changes.
4. Prefer service-owned workflow changes over wrapper-owned policy changes.

## Useful commands

Plan or inspect a bounded proposal:

```bash
edge operator plan --proposal <proposal.yaml>
edge operator explain --proposal <proposal.yaml>
```

Run the canonical daily validation surface:

```bash
make validate
```

Run the deeper researcher verification block:

```bash
python -m project.scripts.run_researcher_verification --mode contracts
```

Run tests:

```bash
pytest -q
```

Lint:

```bash
python -m ruff check .
```

Format:

```bash
python -m ruff format .
```

## Documentation rule

If you change commands, contracts, workflows, stage ownership, or packaging semantics, update the canonical docs that own those concepts:

- `README.md`
- `docs/00_START_HERE.md`
- `docs/02_REPOSITORY_MAP.md`
- `docs/03_OPERATOR_WORKFLOW.md`
- `docs/04_COMMANDS_AND_ENTRY_POINTS.md`
- `docs/05_ARTIFACTS_AND_INTERPRETATION.md`
- `docs/06_QUALITY_GATES_AND_PROMOTION.md`
- `docs/09_THESIS_BOOTSTRAP_AND_PROMOTION.md`
- `docs/11_LIVE_THESIS_STORE_AND_OVERLAP.md`

Regenerate generated inventories when needed instead of editing them by hand.
