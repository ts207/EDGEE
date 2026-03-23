# Feature Catalog

## Core feature groups

### Price and basis features
- Cleaned price returns
- Spread, basis, and relative movement features
- Alignment and lag-aware basis state features

### Funding and microstructure features
- Funding-related measures
- Order book and tick-derived aggregates
- Liquidity and spread diagnostics

### Canonical market-state features
- Volatility regime probabilities
- Liquidity regime probabilities
- Open-interest regime probabilities
- Funding regime probabilities
- Trend regime probabilities

### Confidence and entropy features
- Regime confidence
- Label entropy
- Cross-state uncertainty indicators

## Why this matters

The MI scan and candidate generator work from the feature table.

That means the catalog is not just a descriptive list. It is a search substrate.

## What the older docs did not fully reflect

The code already uses feature structure to support:

- regime-aware discovery,
- context-conditioned hypotheses,
- and candidate predicate generation.

The docs should not treat features as a passive analytics layer only.

## Maintenance rule

If a feature column is added, renamed, or removed, update:

- the feature pipeline,
- any consumer that reads the column,
- the catalog doc,
- and the relevant tests.
