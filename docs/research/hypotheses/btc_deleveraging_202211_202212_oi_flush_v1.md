# Hypothesis

## Identity

- Hypothesis ID: `btc_deleveraging_202211_202212_oi_flush_v1`
- Program ID: `btc_deleveraging_campaign`
- Date: `2026-03-30`
- Author: `Codex`

## Scope

- Canonical regime: `POSITIONING_UNWIND_DELEVERAGING`
- Event or state family: `OI_FLUSH`
- Template family: `exhaustion_reversal`
- Symbol scope: `BTCUSDT`
- Timeframe: `5m`
- Start: `2022-11-01`
- End: `2022-12-31`

## Mechanism

- Mechanism statement: A sharp open-interest flush during forced unwind should mark exhaustion of aggressive positioning and create a rebound window in spot.
- Forced actor: Leveraged futures participants being forced out after a rapid unwind.
- Constraint: Open interest cannot keep collapsing at the same pace once the most fragile positioning has already been cleared.
- Distortion: Forced unwind flow overshoots near-term spot discovery and leaves a short-horizon reversal opportunity.
- Why this distortion should exist in this regime: `POSITIONING_UNWIND_DELEVERAGING` explicitly captures unwind pressure and recovery conditions.
- Why the market should unwind rather than continue: After the OI flush, the marginal forced seller should be weaker and the market can mean-revert from the overshoot.
- Unwind path: OI flush -> liquidation pressure exhausts -> rebound bid returns -> short-horizon spot recovery.

## Tradable Expression

- Execution venue: `Binance spot`
- Instrument expression: Long `BTCUSDT` spot after `OI_FLUSH`.
- Spot expression if futures state is only informational: Use futures unwind state as the regime filter and express the trade in spot.
- Why this expression is simpler than the full mechanism: It avoids modeling futures positioning directly while testing whether the unwind signal survives in spot.

## Entry / Exit

- Entry logic: Enter long one bar after `OI_FLUSH`.
- Entry lag: `1`
- Exit logic: Fixed horizon exit at `12` bars.
- Invalidation: Continued downside after the flush or renewed open-interest expansion against the reversal.
- Expected horizon: `12` bars (`60m`)

## Cost And Execution Assumptions

- Fee assumption: Default retail profile taker fees.
- Slippage assumption: Default retail profile baseline slippage.
- Funding assumption: Funding is informational, not part of spot carry.
- Liquidity assumption: BTC spot liquidity is sufficient for the repository retail profile in this window.
- Execution realism risk: The flush may be only a local futures-positioning event with too little spot follow-through after costs.

## Success Criteria

- Required artifact outputs: Canonical proposal/config artifacts, run manifest, phase-2 diagnostics, phase-2 candidates, promotion bundle, and verification output.
- Minimum cost-aware evidence: Positive after-cost expectancy with no artifact contradictions and no immediate bridge rejection for purely mechanical reasons.
- Required holdout or promotion evidence: Promotion bundle must be present and any survivor must clear trivial sample-quality defects.
- What would count as mechanism confirmation: A long-side exhaustion-reversal candidate survives phase 2 and remains coherent after cost and stress review.

## Kill Criteria

- What result would disconfirm the mechanism: No coherent long-side edge appears on the OI flush trigger in the bounded slice.
- What cost result would kill the idea: Negative after-cost expectancy or zero stressed survivability on the intended expression.
- What artifact inconsistency would invalidate the run: Manifest, diagnostics, and candidate outputs disagree on scope or hypothesis count.
- What would force escalation instead of another run: Missing canonical artifacts, detector absence, or a contract failure unrelated to the bounded hypothesis.

## Negative Controls

- Required placebo or negative-control expectation: The edge should not require unrelated templates or unrelated events to appear.
- What should not work if the mechanism is real: Broad multi-template or multi-event rescue should not be necessary for this one slice.

## Bounded Next Step

- If `keep`: Keep the same event and expression and widen only the date window or tighten only the horizon.
- If `modify`: Keep the same regime and expression and escalate the registry mismatch for `POST_DELEVERAGING_REBOUND` as a separate change-management task.
- If `kill`: Stop this mechanism family and move to the next backlog item without broadening the search.
