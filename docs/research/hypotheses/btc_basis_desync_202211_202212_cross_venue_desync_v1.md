# Hypothesis

## Identity

- Hypothesis ID: `btc_basis_desync_202211_202212_cross_venue_desync_v1`
- Program ID: `btc_basis_disloc_campaign`
- Date: `2026-03-30`
- Author: `Codex`

## Scope

- Canonical regime: `BASIS_FUNDING_DISLOCATION`
- Event or state family: `CROSS_VENUE_DESYNC`
- Template family: `desync_repair`
- Symbol scope: `BTCUSDT`
- Timeframe: `5m`
- Start: `2022-11-01`
- End: `2022-12-31`

## Mechanism

- Mechanism statement: Temporary cross-venue price discovery desynchronization inside a basis-funding dislocation should compress once routing friction and inventory imbalance normalize.
- Forced actor: Perp-led short-horizon participants and venue-local inventory that temporarily move one venue faster than another.
- Constraint: Cross-venue basis cannot stay materially extreme for long without arbitrage, hedging, or inventory rotation compressing it.
- Distortion: One venue leads price discovery while the lagging venue underreacts, creating a temporary information-desync shock.
- Why this distortion should exist in this regime: `BASIS_FUNDING_DISLOCATION` explicitly includes crowding, basis instability, and venue-specific price discovery stress where transient desync is plausible.
- Why the market should unwind rather than continue: Once the lag is visible and the dislocation is large enough, arbitrage and cross-venue re-hedging should compress the spread before the same shock can extend linearly.
- Unwind path: Cross-venue desync onset -> routing and hedge adjustment -> basis compression -> lagging-venue spot catch-up.

## Tradable Expression

- Execution venue: `Binance spot`
- Instrument expression: Long `BTCUSDT` spot one bar after `CROSS_VENUE_DESYNC`.
- Spot expression if futures state is only informational: Use the venue-desync event only as informational state and express the trade in spot.
- Why this expression is simpler than the full mechanism: It avoids direct venue-spread execution and asks only whether the lagging spot leg shows a usable catch-up response.

## Entry / Exit

- Entry logic: Enter long one bar after `CROSS_VENUE_DESYNC` in the bounded November to December 2022 window.
- Entry lag: `1`
- Exit logic: Fixed horizon exit at `12` bars.
- Invalidation: Continued downside or persistent venue desynchronization without visible compression.
- Expected horizon: `12` bars (`60m`)

## Cost And Execution Assumptions

- Fee assumption: Default retail profile taker fees.
- Slippage assumption: Default retail profile baseline slippage.
- Funding assumption: Funding and perp basis remain informational rather than directly monetized.
- Liquidity assumption: BTC spot liquidity is sufficient for the repository retail profile in this window.
- Execution realism risk: The signal may only be real in spread form, and the spot-only catch-up proxy may be too weak or too symmetric to survive costs.

## Success Criteria

- Required artifact outputs: Canonical proposal/config artifacts, run manifest, phase-2 diagnostics, phase-2 candidates, promotion bundle, and verification output.
- Minimum cost-aware evidence: Positive after-cost expectancy with no artifact contradictions and no purely mechanical rejection.
- Required holdout or promotion evidence: Any surviving candidate must clear sample-quality gates and remain coherent after promotion review.
- What would count as mechanism confirmation: A clean long-side candidate survives phase-2 and remains directionally coherent after cost and stress review.

## Kill Criteria

- What result would disconfirm the mechanism: No coherent long-side spot catch-up appears for this bounded desync expression.
- What cost result would kill the idea: Negative after-cost expectancy or failure to survive promotion-quality evidence review.
- What artifact inconsistency would invalidate the run: Manifest, diagnostics, and candidate outputs disagree on scope, event family, or hypothesis count.
- What would force escalation instead of another run: Detector, routing, or artifact-contract failure unrelated to the bounded mechanism.

## Negative Controls

- Required placebo or negative-control expectation: Opposite-template or multi-event rescue should not be necessary for this one desync mechanism.
- What should not work if the mechanism is real: Broadening to unrelated templates or unrelated event families should not be required to find the effect.

## Bounded Next Step

- If `keep`: Widen only the date window while keeping the same event, expression, and template family.
- If `modify`: Keep the same regime and event but adjust only the horizon or date window.
- If `kill`: Stop this desync spot-proxy mechanism and move to the next backlog item without broadening the search.
