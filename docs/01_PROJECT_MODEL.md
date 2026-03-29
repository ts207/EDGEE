# Project Model

This repository is built around explicit research objects. Most confusion comes from mixing them up.

## Core Objects

### Event

An event is a discrete trigger at a timestamp.

Examples:

- `VOL_SHOCK`
- `BASIS_DISLOC`
- `LIQUIDATION_CASCADE`

Question it answers:
"What happened now?"

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

## Example: `VOL_SHOCK`

`VOL_SHOCK` is a good anchor example.

- object type: event
- family: `VOLATILITY_TRANSITION`
- detector meaning: realized-volatility shock onset
- later tested with templates like `mean_reversion`, `continuation`, `only_if_regime`
- evaluated across state-derived regime buckets

So `VOL_SHOCK` is not a family and not a state. It is an event inside a family.

## What The Pipeline Actually Tests

A narrow research claim usually looks like:

"When event X occurs, does template Y in direction Z over horizon H produce post-cost expectancy that survives robustness and bridge gating?"

That means the repo is not merely checking whether an event exists. It is checking whether a trade idea around that event survives:

- sample size thresholds
- `t_stat` thresholds
- multiple-testing control
- cost adjustments
- regime robustness
- stress scenarios
- bridge tradability

## Searchable Universe

Current compiled counts in this workspace:

- `70` event types
- `72` state IDs
- `10` searchable event families
- `8` searchable state families

Those counts come from the compiled domain registry exposed through [project/domain/](/home/irene/Edge/project/domain).

## Family And Template Compatibility

Family compatibility is maintained in:

- [spec/templates/event_template_registry.yaml](/home/irene/Edge/spec/templates/event_template_registry.yaml)
- [spec/events/event_registry_unified.yaml](/home/irene/Edge/spec/events/event_registry_unified.yaml)

This matters because not every template is legal for every family. A clean search run should avoid generating obviously incompatible combinations.

## Practical Rule

When you read a result, ask in this order:

1. what event or state triggered the candidate
2. what family constrained the template set
3. what template generated the trade idea
4. what states and regimes qualified or disqualified the idea
5. whether the candidate died in search, bridge, or promotion
