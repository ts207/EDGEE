# Operator memory and proposal authoring

Sprint 3 adds compact operator memory outputs and a tighter proposal surface.

## New outputs per run

Successful finalized runs now emit:

- `data/reports/operator/<run_id>/operator_summary.json`
- `data/reports/operator/<run_id>/operator_summary.md`

The summary captures:

- what was tested
- what changed from baseline
- strongest candidate or near-miss
- terminal and statistical outcome
- next bounded action

Program memory now also maintains:

- `data/artifacts/experiments/<program_id>/memory/evidence_ledger.parquet`

Each ledger row is one run-level evidence record. It is intended to support bounded follow-up work without re-reading dispersed notes.

## New operator commands

### Explain a proposal

```bash
python -m project.cli operator explain --proposal spec/proposals/example.yaml
```

This resolves the proposal into:

- estimated hypothesis count
- required detectors
- required features
- required states
- effective run overrides

### Lint a proposal

```bash
python -m project.cli operator lint --proposal spec/proposals/example.yaml
```

This validates the proposal and emits bounded-scope warnings for unusually broad surfaces.

## Proposal templates

Example templates are available under:

- `spec/proposals/templates/discovery.yaml`
- `spec/proposals/templates/confirmation.yaml`
- `spec/proposals/templates/regime_split.yaml`
- `spec/proposals/templates/template_fit_test.yaml`

They are starting points for common operator intents rather than full production specs.
