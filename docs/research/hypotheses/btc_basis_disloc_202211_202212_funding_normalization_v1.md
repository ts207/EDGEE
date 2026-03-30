# Hypothesis

## Identity

- Hypothesis ID: `btc_basis_disloc_202211_202212_funding_normalization_v1`
- Program ID: `btc_basis_disloc_campaign`
- Date: `2026-03-30`
- Author: `Codex`

## Scope

- Canonical regime: `BASIS_FUNDING_DISLOCATION`
- Event or state family: `FUNDING_NORMALIZATION_TRIGGER`
- Template family: `basis_repair`
- Symbol scope: `BTCUSDT`
- Timeframe: `5m`
- Start: `2022-11-01`
- End: `2022-12-31`

## Mechanism

- Mechanism statement: Extreme funding and basis crowding should partially unwind after normalization, leaving a tradable spot-side rebound or basis compression window.
- Forced actor: Leveraged perp participants paying elevated funding into a crowded positioning episode.
- Constraint: Cross-venue basis and funding stress cannot persist indefinitely without capital rotation, liquidation, or inventory rebalancing.
- Distortion: Perp-led crowding dislocates price discovery and overstates near-term downside or short-pressure relative to spot.
- Why this distortion should exist in this regime: `BASIS_FUNDING_DISLOCATION` explicitly models funding and basis stress as trade-generating dislocations rather than generic trend continuation.
- Why the market should unwind rather than continue: Once funding normalizes, the crowding signal weakens and the marginal forced seller or payer should exhaust before a fresh dislocation forms.
- Unwind path: Funding normalization -> basis compression -> spot/perp resynchronization -> short-horizon spot rebound.

## Tradable Expression

- Execution venue: `Binance spot`
- Instrument expression: Long `BTCUSDT` spot after `FUNDING_NORMALIZATION_TRIGGER`.
- Spot expression if futures state is only informational: Use perp funding/basis only as regime information and express the trade in spot.
- Why this expression is simpler than the full mechanism: It avoids modeling spread capture directly and tests whether the futures-state unwind is strong enough to appear in the simpler spot leg.

## Entry / Exit

- Entry logic: Enter long one bar after `FUNDING_NORMALIZATION_TRIGGER` in the bounded regime slice.
- Entry lag: `1`
- Exit logic: Fixed horizon exit at `12` bars.
- Invalidation: Continued downside after normalization without basis compression or evidence of renewed crowding.
- Expected horizon: `12` bars (`60m`)

## Cost And Execution Assumptions

- Fee assumption: Default retail profile taker fees.
- Slippage assumption: Default retail profile baseline slippage.
- Funding assumption: Funding is informational, not part of spot carry.
- Liquidity assumption: BTC spot liquidity is sufficient for the repository retail profile in this window.
- Execution realism risk: The signal may be visible statistically while failing bridge robustness if the unwind expresses mainly in perp basis rather than spot.

## Success Criteria

- Required artifact outputs: Canonical proposal/config artifacts, run manifest, phase-2 diagnostics, phase-2 candidates, promotion bundle, and verification output.
- Minimum cost-aware evidence: Positive after-cost expectancy with no artifact contradictions and no immediate bridge rejection for purely mechanical reasons.
- Required holdout or promotion evidence: Promotion bundle must be present and any survivor must not fail on trivial sample-quality defects.
- What would count as mechanism confirmation: A clean long-side candidate survives phase-2 and remains coherent after cost and stress review in the intended regime.

## Kill Criteria

- What result would disconfirm the mechanism: No coherent long-side edge appears after normalization, or the best rows point to the opposite direction.
- What cost result would kill the idea: Negative after-cost expectancy or zero stressed survivability on the intended expression.
- What artifact inconsistency would invalidate the run: Manifest, diagnostics, and candidate outputs disagree on scope or hypothesis count.
- What would force escalation instead of another run: Template/event incompatibility in the planner, missing canonical artifacts, or a contract failure unrelated to the bounded hypothesis.

## Negative Controls

- Required placebo or negative-control expectation: Unrelated template families or opposite-direction expressions should not be needed to rescue the claim.
- What should not work if the mechanism is real: Broad multi-template or multi-event search should not be necessary for this one-slice funding-normalization claim.

## Bounded Next Step

- If `keep`: Re-run the same regime and expression with one bounded horizon adjustment or one confirmatory companion event.
- If `modify`: Keep the same regime and symbol, but switch to `SPOT_PERP_BASIS_SHOCK` or adjust only the horizon.
- If `kill`: Stop this mechanism and move to the next backlog regime-scoped idea without broadening the search.
