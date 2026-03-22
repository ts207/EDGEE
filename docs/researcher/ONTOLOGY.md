# Ontology Reference

This document explains the research ontology used throughout the repository. Understanding this hierarchy prevents common research mistakes.

---

## The Hierarchy

```
regime
  └── market state / context
        └── event
              └── canonical family
                    └── template
                          └── hypothesis
```

Each layer has a distinct job. Confusing them leads to bad research decisions.

---

## Layer Definitions

### Regime

The underlying market environment inferred from features or injected by a synthetic generator.

Examples:
- synthetic `liquidity_stress`
- synthetic `funding_dislocation`
- inferred: high-vol, low-vol, trending, choppy, crowded, deleveraging

Regimes describe the world the market is in. They are not directly tradeable signals.

### Market State

A normalized label derived from features by the context pipeline stage.

Examples:
- `ms_vol_state` — canonical volatility state
- `ms_liq_state` — canonical liquidity state
- `ms_trend_state` — canonical trend/chop state
- `ms_spread_state` — canonical spread state
- `ms_funding_state` — canonical funding state
- `ms_oi_state` — canonical open-interest state
- `ms_context_state_code` — encoded composite state

States are context surfaces, not detector outputs. Use them to filter rows, not as events.

### Context

The actual filter applied to an event-template combination in research.

Examples:
- Only high-volatility rows (`ms_vol_state = HIGH`)
- Only acceptable-spread rows (`ms_spread_state` non-hostile)
- Only high-confidence trend rows (`ms_trend_confidence` above threshold)

Context is where a broad event claim becomes a narrower, defensible research claim. Confidence-aware context is the default; hard labels are a comparison baseline.

### Event

A concrete detector output: a specific market condition detected at a specific time for a specific symbol.

Examples:
- `FND_DISLOC` — funding dislocation
- `BASIS_DISLOC` — basis dislocation
- `VOL_SHOCK` — volatility shock
- `FALSE_BREAKOUT` — failed breakout
- `ZSCORE_STRETCH` — statistical z-score extreme

An event is evidence of a condition. It is not a strategy.

### Canonical Family

The semantic class assigned to an event in the registry. Families constrain which templates are legal.

| Family | Description | Example events |
|---|---|---|
| `LIQUIDITY_DISLOCATION` | Discrete shocks to order book depth and spread | `DEPTH_COLLAPSE`, `SPREAD_BLOWOUT` |
| `VOLATILITY_TRANSITION` | Shifts in realized volatility and range compression | `VOL_SHOCK`, `VOL_SPIKE`, `BAND_BREAK` |
| `POSITIONING_EXTREMES` | Extreme funding rates and open interest flushes | `FND_DISLOC`, `OI_FLUSH` |
| `FORCED_FLOW_AND_EXHAUSTION` | Exhaustion of trend momentum and climax volume | `TREND_EXHAUSTION_TRIGGER`, `CLIMAX_VOLUME_BAR` |
| `TREND_STRUCTURE` | Breakouts and trend accelerations | `BREAKOUT_TRIGGER`, `FALSE_BREAKOUT` |
| `STATISTICAL_DISLOCATION` | Mean reversion from statistical z-score extremes | `ZSCORE_STRETCH`, `BASIS_DISLOC` |
| `REGIME_TRANSITION` | Long-term shifts in market regime | `VOL_REGIME_SHIFT_EVENT` |
| `INFORMATION_DESYNC` | Arbitrage opportunities from cross-venue desync | `CROSS_VENUE_DESYNC`, `LEAD_LAG_BREAK` |
| `TEMPORAL_STRUCTURE` | Time-based market structures | `SESSION_OPEN_EVENT` |

### Template

A trade or evaluation shape applied to an event. Templates describe *how* an event should be tested, not *whether* it fires.

Common templates:
- `mean_reversion`
- `continuation`
- `pullback_entry`
- `trend_continuation`
- `exhaustion_reversal`
- `false_breakout_reversal`
- `breakout_followthrough`
- `overshoot_repair`
- `momentum_fade`

The family registry enforces which templates are legal for each family. An event cannot be paired with an arbitrary template.

### Hypothesis

The explicit research unit evaluated in discovery. The correct comparison and memory unit.

A hypothesis combines:

| Field | Description |
|---|---|
| `event` | The detector event name |
| `canonical_family` | The family from the registry |
| `template` | A template from the family's allowed set |
| `context` | The market-state filter applied |
| `side` | `long` or `short` |
| `horizon` | Bar count for evaluation |
| `entry_lag` | Bars after event detection before entry |
| `symbol_scope` | Symbol(s) the hypothesis covers |

---

## How the Stack Uses the Ontology

### Pipelines Build Context

The feature and context stages build cleaned bars, feature tables, context features, and market-state features. These outputs create the context surface used by detectors and research.

### Detectors Emit Events

Detectors consume bars and features and emit event rows. Every maintained event type is tied to:
- a canonical family
- parameter defaults
- report paths
- template eligibility

### Families Constrain Templates

The template registry prevents invalid pairings. Without this constraint, search would cross events with semantically invalid templates, promotion would compare unlike things, and memory would store shallow name matches instead of ontology-native claims.

### Search Expands to Hypotheses

Phase 2 evaluates explicit hypotheses built from event + template + context + horizon. The hypothesis, not the detector firing, is the unit that gets scored, stored, and promoted.

---

## Registry Files

| Surface | Path |
|---|---|
| Family registry (event families + allowed templates) | `spec/grammar/family_registry.yaml` |
| Canonical event registry | `spec/events/canonical_event_registry.yaml` |
| State registry | `spec/grammar/state_registry.yaml` |
| Template registry | `spec/ontology/templates/template_registry.yaml` |
