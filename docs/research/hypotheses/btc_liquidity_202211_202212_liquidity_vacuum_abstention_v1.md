# Hypothesis

## Summary

- Hypothesis ID: `btc_liquidity_202211_202212_liquidity_vacuum_abstention_v1`
- Program ID: `btc_liquidity_campaign`
- Canonical regime: `LIQUIDITY_STRESS`
- Primary event family: `LIQUIDITY_VACUUM`
- Template family: `tail_risk_avoid`
- Symbol: `BTCUSDT`
- Timeframe: `5m`
- Date range: `2022-11-01` to `2022-12-31`

## Mechanism

After an impulsive move followed by thin-book, wide-range bars, short-horizon execution quality and path stability should deteriorate. The useful claim is not immediate rebound; it is that this window should be avoided because forward path quality is materially worse than normal.

## Tradable Expression

Use `LIQUIDITY_VACUUM` as the event trigger and test `tail_risk_avoid` on `BTCUSDT` spot over a `12`-bar horizon with a `1`-bar entry lag.

- Intended operational interpretation: abstain from fresh spot exposure during the post-vacuum window.
- Why this expression is simpler than the full mechanism: it tests whether the detector identifies materially worse forward path quality without bundling in a separate rebound thesis.

## Bounded Scope

- One event family: `LIQUIDITY_VACUUM`
- One template family: `tail_risk_avoid`
- One symbol: `BTCUSDT`
- One timeframe: `5m`
- One horizon: `12` bars
- One lag: `1` bar
- One date window: `2022-11-01` to `2022-12-31`

## Acceptance Standard

Keep only if the abstention claim survives the repo’s mechanical checks, produces adequate sample count, and yields promotion-relevant evidence that forward path risk is materially worse after the event. If the template-event path is incompatible or the edge vanishes in promotion review, stop rather than broadening into a rebound claim.
