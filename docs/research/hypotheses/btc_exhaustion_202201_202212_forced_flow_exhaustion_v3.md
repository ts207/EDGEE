# Hypothesis

## Identity

- Hypothesis ID: `btc_exhaustion_202201_202212_forced_flow_exhaustion_v3`
- Program ID: `btc_exhaustion_campaign`
- Date: `2026-03-30`
- Author: `Codex`

## Scope

- Canonical regime: `TREND_FAILURE_EXHAUSTION`
- Event or state family: `FORCED_FLOW_EXHAUSTION`
- Template family: `exhaustion_reversal`
- Symbol scope: `BTCUSDT`
- Timeframe: `5m`
- Start: `2022-01-01`
- End: `2022-12-31`

## Mechanism

- Mechanism statement: late forced flow should produce short-horizon exhaustion, followed by reversal once aggressive participation is spent.
- Forced actor: liquidating or late-chasing participants pushing the move into local exhaustion.
- Constraint: once the forced actor’s marginal flow is exhausted, continuation should weaken rather than accelerate cleanly.
- Distortion: the event marks a locally stretched move whose next leg is more likely to mean-revert than extend.
- Why this distortion should exist in this regime: `TREND_FAILURE_EXHAUSTION` explicitly models unsustainable continuation and post-exhaustion reversal.
- Why this run exists: the repaired November to December slice showed clean zero-event semantics, so the next justified move is to widen only the window and test whether the branch is genuinely event-sparse or merely too narrow.

## Tradable Expression

- Execution venue: `Binance spot`
- Instrument expression: Long `BTCUSDT` spot after `FORCED_FLOW_EXHAUSTION`.
- Spot expression if futures state is only informational: Use the forced-flow event as the informational state and express the trade in spot.
- Why this expression is simpler than the full mechanism: It avoids directly modeling liquidation plumbing while testing whether exhaustion is strong enough to show up in the spot leg.

## Entry / Exit

- Entry logic: Enter long one bar after `FORCED_FLOW_EXHAUSTION`.
- Entry lag: `1`
- Exit logic: Fixed horizon exit at `12` bars.
- Invalidation: immediate continuation through the exhaustion trigger or renewed forced selling.
- Expected horizon: `12` bars (`60m`)

## Success Criteria

- Required artifact outputs: canonical proposal/config artifacts, run manifest, phase-2 diagnostics, promotion diagnostics, and conditional expectancy.
- Minimum cost-aware evidence: positive after-cost expectancy with no artifact contradictions and no trivial sample-quality failure.
- What would count as mechanism confirmation: a long-side exhaustion-reversal candidate survives phase 2 and remains coherent after cost and stress review.
