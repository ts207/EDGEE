# Operator Preflight

`edge operator preflight` validates the front-door conditions for a proposal before a run starts.

## What it checks

- proposal schema validity
- validated plan generation
- search spec existence
- local raw data resolution for requested symbols
- coverage window overlap for the requested date range
- artifact output writability

## Status model

- `pass`: ready on this check
- `warn`: usable but incomplete or partial
- `block`: do not start the run

## Canonical usage

```bash
edge operator preflight \
  --proposal spec/proposals/my_slice.yaml \
  --registry_root project/configs/registries \
  --json_output data/reports/operator_preflight/my_slice.json
```

## Local data resolution

Sprint 1 adds explicit support for both layouts below:

- canonical vendor-qualified archive
  - `data/lake/raw/binance/perp/<SYMBOL>/<DATASET>`
- vendorless local archive
  - `data/lake/raw/perp/<SYMBOL>/<DATASET>`

Resolution order is:

1. run-scoped vendor-qualified
2. global vendor-qualified
3. run-scoped vendorless
4. global vendorless

This keeps the canonical path primary while making local archive drops visible to the operator.

## Interpretation rule

Block the run when OHLCV coverage is missing or absent for the requested interval.
Treat missing funding or open interest as a warning unless the specific workflow later hard-requires those inputs.
