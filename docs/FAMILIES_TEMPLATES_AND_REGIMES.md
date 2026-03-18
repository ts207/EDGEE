# Event Families, Templates, Contexts, And Regimes

## Purpose

This note explains how the research ontology fits together.

The important hierarchy is:

`regime -> market state/context -> event -> canonical family -> allowed template -> hypothesis`

Each layer means something different. Do not collapse them into one concept.

## Definitions

### Regime

The underlying market environment.

Examples:

- synthetic `liquidity_stress`
- synthetic `funding_dislocation`
- synthetic `breakout_failure`
- inferred live volatility, carry, trend, and spread environments

### Market State And Context

Normalized labels or feature conditions used to condition hypotheses.

Common examples in this repo:

- `vol_regime`
- `carry_state`
- `ms_trend_state`
- `ms_spread_state`
- `severity_bucket`

Context is the actual filter applied during search or evaluation, for example "only high vol" or "only positive
carry".

### Event

A concrete detector output at a specific time for a specific symbol.

Examples:

- `FND_DISLOC`
- `BASIS_DISLOC`
- `VOL_SHOCK`
- `FALSE_BREAKOUT`
- `DELEVERAGING_WAVE`

### Canonical Family

The semantic class assigned to an event in the event registry.

The family controls how the event should be interpreted and which templates are legal.

### Template

A trade or evaluation shape applied to an event.

Examples:

- `mean_reversion`
- `continuation`
- `pullback_entry`
- `exhaustion_reversal`
- `tail_risk_avoid`
- `slippage_aware_filter`

An event is not a template.

### Hypothesis

The explicit research unit tested in discovery.

In repo-native terms it combines:

- event type
- family
- side
- horizon
- template
- state filter
- symbol scope

## How The Stack Uses Them

### 1. Pipelines Build Features And States

The pipelines layer creates:

- cleaned bars
- feature tables
- context features
- market-state features
- microstructure rollups

Those outputs provide the state surface used by both detectors and research.

### 2. Detectors Emit Events

Detectors consume bars and features and emit event rows.

Each event type is tied to a registry entry and therefore to a canonical family.

### 3. The Registry Constrains Interpretation

The event registry maps each event type to:

- `canonical_family`
- `reports_dir`
- parameter defaults
- allowed templates

That prevents search from treating all events as interchangeable.

### 4. Templates Are Chosen By Family

The template registry defines which templates are legal for each family.

This is a real constraint, not just documentation.

### 5. Research Expands Hypotheses

The research layer crosses:

- event
- family
- template
- horizon
- side
- optional context

That produces the explicit hypothesis registry scored in phase 2.

## Family Map

| Family | Meaning | Typical examples | Typical template style | Usual interpretation |
| --- | --- | --- | --- | --- |
| `EXECUTION_FRICTION` | Market is expensive or mechanically unattractive to trade | spread and fee widening style events | defensive filters, slippage-aware gating | often says "do not trade this other idea now" |
| `TEMPORAL_STRUCTURE` | Time-window or schedule effect | session and scheduled-window events | simple continuation or mean reversion | defines validity windows more than alpha |
| `VOLATILITY_TRANSITION` | Volatility regime changed | `VOL_SHOCK` and vol-regime shifts | continuation, trend continuation, regime filters | changes horizon and sizing before entry logic |
| `LIQUIDITY_DISLOCATION` | Liquidity is impaired, stressed, or recovering | `LIQUIDITY_STRESS_DIRECT`, `LIQUIDITY_STRESS_PROXY` | repair, replenishment, selective continuation | must pass execution feasibility first |
| `POSITIONING_EXTREMES` | Funding, OI, or liquidation crowding | `DELEVERAGING_WAVE`, `OI_FLUSH` | squeeze, reversal, convexity, continuation with caution | high conviction only if liquidity allows execution |
| `FORCED_FLOW_AND_EXHAUSTION` | Move is driven by forced flow or late-stage exhaustion | climax-volume and exhaustion-style events | exhaustion reversal, mean reversion, momentum fade | usually depends on vol and liquidity checks |
| `INFORMATION_DESYNC` | Markets or venues temporarily disagree | `CROSS_VENUE_DESYNC`, lead-lag breaks | convergence, repair, lead-lag follow | fast decay, execution-sensitive |
| `TREND_STRUCTURE` | Breakout, pullback, or structural failure | `FALSE_BREAKOUT`, `PULLBACK_PIVOT` | breakout followthrough, pullback, continuation, reversal | slower-decay directional family |
| `STATISTICAL_DISLOCATION` | Basis, z-score, or correlation relationship is displaced | `BASIS_DISLOC`, `FND_DISLOC` | mean reversion, repair, tail-risk avoidance | usually wants confirmation from higher-precedence families |
| `REGIME_TRANSITION` | Broader market mode is changing | trend-to-chop and structural shift events | structural regime shift, continuation, defensive filters | context setter, not usually the fastest intraday trigger |

## Precedence

Families are not peers when they conflict.

The precedence model is:

1. `EXECUTION_FRICTION`
2. `TEMPORAL_STRUCTURE`
3. `VOLATILITY_TRANSITION`
4. `LIQUIDITY_DISLOCATION`
5. `POSITIONING_EXTREMES`
6. `FORCED_FLOW_AND_EXHAUSTION`
7. `INFORMATION_DESYNC`
8. `TREND_STRUCTURE`
9. `STATISTICAL_DISLOCATION`
10. `REGIME_TRANSITION`

Practical meaning:

- friction can block an otherwise attractive setup
- temporal windows can invalidate slower structural ideas
- statistical dislocations should not override higher-precedence execution or liquidity constraints

Per-event overrides can change priority for specific event types.

## Search And Discovery

Search specs decide:

- which event types are in scope
- which contexts are expanded
- which templates are tested
- which horizons and entry lags are used

The template registry then removes illegal family-template combinations.

The hypothesis registry converts the result into explicit research units with:

- `event_family`
- `event_type`
- `side`
- `horizon`
- `condition_template`
- `state_filter`

Those are the units discovery, bridge evaluation, and promotion reason about.

## Synthetic Interpretation

Synthetic regimes are useful because they let the repo test:

- detector recovery
- contract plumbing
- search behavior under controlled worlds

But synthetic regime labels are still not the same thing as tradable hypotheses.

Keep the boundary clear:

- a planted regime is not the final state label
- a state label is not the detector event
- a detector event is not the trading template
- a trading template is not a promoted edge

## Working Rules

- use the family to understand what class of phenomenon an event belongs to
- use the template to understand how that event is being turned into a testable trade shape
- use context to understand when the event-template pair is valid
- use precedence to arbitrate conflicts
- do not interpret a detector hit without understanding family, template, and context
