# Hypothesis

## Identity

- Hypothesis ID: `btc_exhaustion_202211_202212_forced_flow_exhaustion_v1`
- Program ID: `btc_exhaustion_campaign`
- Date: `2026-03-30`
- Author: `Codex`

## Scope

- Canonical regime: `TREND_FAILURE_EXHAUSTION`
- Event or state family: `FORCED_FLOW_EXHAUSTION`
- Template family: `exhaustion_reversal`
- Symbol scope: `BTCUSDT`
- Timeframe: `5m`
- Start: `2022-11-01`
- End: `2022-12-31`

## Mechanism

- Mechanism statement: late forced flow should produce short-horizon exhaustion, followed by a reversal once aggressive participation is spent.
- Forced actor: liquidating or late-chasing participants pushing the move into local exhaustion.
- Constraint: once the forced actor’s marginal flow is exhausted, continuation should weaken rather than accelerate cleanly.
- Distortion: the event marks a locally stretched move whose next leg is more likely to mean-revert than extend.
- Why this distortion should exist in this regime: `TREND_FAILURE_EXHAUSTION` is already framed around unsustainable continuation and post-exhaustion reversal.
- Why the market should unwind rather than continue: the detector specifically targets exhausted forced flow rather than generic trend persistence.
- Unwind path: aggressive flow extension -> forced flow exhaustion trigger -> short-horizon reversal or repair.

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

## Cost And Execution Assumptions

- Fee assumption: Default retail profile taker fees.
- Slippage assumption: Default retail profile baseline slippage.
- Funding assumption: Not part of the realized spot leg.
- Liquidity assumption: BTC spot liquidity remains adequate for the repository retail profile in this window.
- Execution realism risk: the reversal may be too brief or too futures-localized to survive spot execution after costs.

## Success Criteria

- Required artifact outputs: Canonical proposal/config artifacts, run manifest, phase-2 diagnostics, phase-2 candidates, promotion bundle, and verification output.
- Minimum cost-aware evidence: Positive after-cost expectancy with no artifact contradictions and no trivial phase-2 sample-quality failure.
- Required holdout or promotion evidence: Any survivor must clear phase-2 statistical gates and produce promotion-relevant evidence.
- What would count as mechanism confirmation: A long-side exhaustion-reversal candidate survives phase 2 and remains coherent after cost and stress review.

## Kill Criteria

- What result would disconfirm the mechanism: No coherent long-side edge appears on the forced-flow exhaustion trigger in the bounded slice.
- What cost result would kill the idea: Negative after-cost expectancy or no promoted evidence after a valid sample.
- What artifact inconsistency would invalidate the run: Manifest, diagnostics, and candidate outputs disagree on scope or hypothesis count.
- What would force escalation instead of another run: Missing canonical artifacts, detector absence, or a contract failure unrelated to the bounded hypothesis.

## Negative Controls

- Required placebo or negative-control expectation: The edge should not require unrelated events or unrelated templates to appear.
- What should not work if the mechanism is real: broad multi-template rescue should not be needed for this one slice.

## Bounded Next Step

- If `keep`: Keep the same event and expression and widen only the date window or switch only to the optional companion `LIQUIDATION_EXHAUSTION_REVERSAL`.
- If `modify`: Keep the same regime and template and widen only the date window.
- If `kill`: Stop this mechanism family and end the current backlog sweep.
