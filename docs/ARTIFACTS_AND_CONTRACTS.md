# Artifacts And Contracts

## Principle

Artifacts are contracts, not incidental files.

Do not trust a run because the command exited successfully.
Trust it only when the expected artifacts exist and reconcile.

## Artifact Layers

### Run Layer

Located under `data/runs/<run_id>/`.

Use for:

- overall run status
- planned stage list
- stage manifests
- stage logs
- reconciliation checks

### Research Report Layer

Located under `data/reports/`.

Use for:

- phase-2 candidate outputs
- discovery summaries
- edge candidate exports
- promotion audits
- registry updates

### Event Layer

Located under `data/events/<run_id>/`.

Use for:

- event materialization
- registry manifests
- event-level troubleshooting

### Lake Layer

Located under `data/lake/runs/<run_id>/`.

Use for:

- cleaned bars
- feature tables
- context features
- market-state features

## Contract Expectations

The normal expectation is:

- manifests match actual stage terminal status
- zero-candidate bridge stages end as successful no-op stages, not runner failures
- exported candidates carry required downstream fields
- promotion fallbacks emit the same normalized candidate contract as the canonical export path
- split-aware metrics survive into promotion-facing artifacts
- durable writes go through shared IO helpers instead of ad hoc parquet writes
- generated diagnostics agree with the registry and contract sources that produced them

## Failure Classes

### Mechanical Contract Failure

Examples:

- missing input artifact
- stale manifest after replay
- stage success with no outputs
- logs disagree with manifests
- detector registry metadata disagrees with runnable detector inventory

### Semantic Contract Failure

Examples:

- field exists but means the wrong thing
- units drift from their canonical meaning
- train metrics are computed on all rows
- regime-conditioned outputs duplicate unconditional rows

### Statistical Contract Failure

Examples:

- zero validation or test support
- invalid multiplicity interpretation
- no cost-surviving expectancy

## Trust Order

When investigating a run, inspect in this order:

1. top-level run manifest
2. stage manifests
3. stage logs
4. report artifacts
5. generated diagnostics

If those disagree, the disagreement is a first-class finding.

## Required Checks Before Trusting A Run

- top-level run status matches stage outcomes
- candidate counts reconcile across summary, export, and promotion
- feature-stage declared inputs match what the implementation actually reads
- split counts exist where required
- artifacts exist where manifests say they do
- detector ownership, registry, and generated coverage diagnostics agree
- warning noise does not hide runtime faults

## Response To Contract Breakage

When contracts break:

1. stop broad experimentation
2. isolate the broken path
3. repair propagation or bookkeeping
4. replay the smallest affected chain
5. resume research interpretation only after reconciliation
