# Project Model

This repository is built around explicit research and packaging objects. Most confusion comes from mixing them up.

## Core objects

### Event

An event is a discrete trigger at a timestamp.

Examples:

- `VOL_SHOCK`
- `BASIS_DISLOC`
- `LIQUIDATION_CASCADE`

Question it answers:
"What happened now?"

### Episode

An episode is a higher-order stateful sequence composed of one or more events with onset, persistence, and expiry semantics.

Examples:

- compression -> breakout
- liquidity vacuum -> vol shock
- dislocation -> repair

Question it answers:
"What multi-step process is unfolding, not just what happened on one bar?"

### Family

A family is the higher-level category an event or state belongs to. Families constrain compatible templates and organize search.

Examples:

- `VOLATILITY_TRANSITION`
- `LIQUIDITY_DISLOCATION`
- `TREND_STRUCTURE`

Question it answers:
"What class of phenomenon is this?"

### Template

A template is the hypothesis shape tested around a trigger.

Examples:

- `mean_reversion`
- `continuation`
- `trend_continuation`
- `only_if_regime`

Question it answers:
"How are we trying to extract edge from this trigger?"

### State

A state is a market-condition label on bars.

Examples:

- `TRENDING_STATE`
- `CHOP_STATE`
- `HIGH_VOL_REGIME`
- `LOW_LIQUIDITY_STATE`

Question it answers:
"What condition is the market in around the trigger?"

### Regime

Regime is used in two distinct ways in this repo:

1. canonical grouping on an event row, such as `VOLATILITY_TRANSITION`
2. composite evaluation buckets built from states, such as `high_vol.funding_pos.trend.wide`

Question it answers:
"Does this candidate survive across environments?"

### Thesis

A thesis is the governed operational claim that downstream live and allocation systems consume.

A thesis binds together:

- event or episode contracts
- trigger requirements
- optional confirmations
- invalidation requirements
- bounded horizon
- expected path or direction
- allowed/disallowed regimes
- promotion class
- deployment state

Question it answers:
"What exactly are we willing to claim, package, retrieve, and potentially act on?"

### Promotion class

Promotion class is the repo’s maturity staging for theses.

Current classes:

- `candidate` — structured idea or queue entry, not yet tested enough
- `tested` — bounded claim with testing artifacts, not yet packaged
- `seed_promoted` — packaged and usable for monitor-only / bootstrap surfaces
- `paper_promoted` — packaged and eligible for paper-style live retrieval
- `production_promoted` — rare, highest bar

Question it answers:
"How much evidence and operational trust does this thesis have?"

### Overlap group

An overlap group is the allocator-facing cluster of theses that share enough mechanism, event structure, episode structure, or invalidation logic that they should not be treated as independent.

Question it answers:
"Which packaged theses are too similar to size as if they were unrelated?"

## Example: `VOL_SHOCK`

`VOL_SHOCK` is a good anchor example.

- object type: event
- family: `VOLATILITY_TRANSITION`
- detector meaning: realized-volatility shock onset
- later tested with templates like `mean_reversion`, `continuation`, `only_if_regime`
- evaluated across state-derived regime buckets
- can also appear inside a packaged thesis such as a standalone `VOL_SHOCK` thesis or a confirmation-aware thesis like `VOL_SHOCK_LIQUIDITY_CONFIRM`

So `VOL_SHOCK` is not a family and not a thesis. It is one contract input that can later support one or more theses.

## Practical distinction

Do not confuse these layers:

- event detection answers **what happened**
- proposal/run artifacts answer **what was tested**
- evidence bundles answer **how much support exists**
- packaged theses answer **what downstream systems are allowed to retrieve**
- overlap graph answers **which packaged theses are structurally related**
