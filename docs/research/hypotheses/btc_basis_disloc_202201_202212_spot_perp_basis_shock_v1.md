# Hypothesis

## Identity

- Hypothesis ID: `btc_basis_disloc_202201_202212_spot_perp_basis_shock_v1`
- Program ID: `btc_basis_disloc_campaign`
- Date: `2026-03-30`
- Author: `Codex`

## Scope

- Canonical regime: `BASIS_FUNDING_DISLOCATION`
- Event or state family: `SPOT_PERP_BASIS_SHOCK`
- Template family: `basis_repair`
- Symbol scope: `BTCUSDT`
- Timeframe: `5m`
- Start: `2022-01-01`
- End: `2022-12-31`

## Mechanism

- Mechanism statement: Acute spot-perp basis desynchronization during a funding dislocation should mean-revert as inventory and arbitrage capital rebalance the spread.
- Forced actor: Leveraged perp participants and short-horizon basis traders leaning too far into the perp-led dislocation.
- Constraint: Spot and perp cannot stay materially desynced once inventory rotation and arbitrage participation react to the spread.
- Distortion: Perp price leads spot too aggressively, creating a temporary futures-state information shock that should compress.
- Why this distortion should exist in this regime: `BASIS_FUNDING_DISLOCATION` explicitly captures crowded funding and basis conditions where cross-venue price discovery can become temporarily unstable.
- Why the market should unwind rather than continue: Once the spread shock is visible and funding stress is elevated, arbitrage and re-hedging pressure should compress the basis before a fresh dislocation forms.
- Unwind path: Spot-perp basis shock -> convergence pressure -> spread compression -> short-horizon spot rebound or reduced downside pressure.

## Tradable Expression

- Execution venue: `Binance spot`
- Instrument expression: Long `BTCUSDT` spot after `SPOT_PERP_BASIS_SHOCK`.
- Spot expression if futures state is only informational: Use the basis shock only as regime information and express the trade in spot.
- Why this expression is simpler than the full mechanism: It avoids directly trading the spread while still testing whether the dislocation has enough power to show up in the spot leg.

## Entry / Exit

- Entry logic: Enter long one bar after `SPOT_PERP_BASIS_SHOCK` in the bounded regime slice.
- Entry lag: `1`
- Exit logic: Fixed horizon exit at `12` bars.
- Invalidation: Continued downside after the basis shock without visible convergence pressure.
- Expected horizon: `12` bars (`60m`)

## Cost And Execution Assumptions

- Fee assumption: Default retail profile taker fees.
- Slippage assumption: Default retail profile baseline slippage.
- Funding assumption: Funding remains informational, not part of spot carry.
- Liquidity assumption: BTC spot liquidity is sufficient for the repository retail profile in this wider window.
- Execution realism risk: The shock may be tradable only in spread form, not in the spot-only expression.

## Success Criteria

- Required artifact outputs: Canonical proposal/config artifacts, run manifest, phase-2 diagnostics, phase-2 candidates, promotion bundle, and verification output.
- Minimum cost-aware evidence: Positive after-cost expectancy with no artifact contradictions and no immediate bridge rejection for purely mechanical reasons.
- Required holdout or promotion evidence: Promotion bundle must be present and any survivor must clear trivial sample-quality defects.
- What would count as mechanism confirmation: A clean long-side candidate survives phase-2 on the compatible event in the wider 2022 slice and remains coherent after cost and stress review.

## Kill Criteria

- What result would disconfirm the mechanism: No coherent long-side edge appears even after widening the compatible event to a full-year 2022 window.
- What cost result would kill the idea: Negative after-cost expectancy or zero stressed survivability on the intended expression.
- What artifact inconsistency would invalidate the run: Manifest, diagnostics, and candidate outputs disagree on scope or hypothesis count.
- What would force escalation instead of another run: Detector absence, missing canonical artifacts, or a contract failure unrelated to the bounded hypothesis.

## Negative Controls

- Required placebo or negative-control expectation: Opposite-direction or unrelated-template rescue should not be necessary for this one mechanism.
- What should not work if the mechanism is real: Broad multi-template or multi-event search should not be needed to find the effect in this bounded full-year slice.

## Bounded Next Step

- If `keep`: Keep the same event and expression and tighten only one evaluation dimension such as horizon.
- If `modify`: Keep the same regime and expression but adjust only the horizon or entry lag.
- If `kill`: Stop this mechanism family and move to the next backlog regime-scoped idea without broadening the search.
