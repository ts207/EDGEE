# Hypothesis: Basis Normalization After Forced Payer Flow

## Identity

- Hypothesis ID: H_BASIS_NORM_001
- Program ID: basis_normalization_campaign
- Date: 2026-03-31
- Author: Gemini CLI

## Scope

- Canonical regime: BASIS_FUNDING_DISLOCATION
- Event or state family: FUNDING_NORMALIZATION_TRIGGER, SPOT_PERP_BASIS_SHOCK
- Template family: mean_reversion, basis_repair
- Symbol scope: BTCUSDT
- Timeframe: 5m
- Start: 2021-01-01
- End: 2022-12-31

## Mechanism

- Mechanism statement: Extreme perp premium and funding are a crowding artifact that mean-revert after the payer imbalance exhausts.
- Forced actor: Leveraged long perp positions.
- Constraint: Liquidity on the short side or spot-perp arbitrage friction.
- Distortion: Perp price trades at a significant premium to spot, reflected in high funding rates and positive basis.
- Why this distortion should exist in this regime: Aggressive directional flow in perps outpaces the ability of arbitrageurs to keep prices in line due to risk limits or capital constraints.
- Why the market should unwind rather than continue: The high cost of carrying the long position (funding) and the exhaustion of aggressive buyers eventually lead to a normalization of the basis.
- Unwind path: Perp price reverts toward spot price as long positions are closed or arbitrageurs enter.

## Tradable Expression

- Execution venue: Binance UM (Perp) or Spot
- Instrument expression: Short Perp or Long Spot (if basis is positive)
- Spot expression if futures state is only informational: Long Spot to capture the relative cheapness compared to perp.
- Why this expression is simpler than the full mechanism: Avoids complex delta-neutral arbitrage if the directional edge from basis normalization is sufficient.

## Entry / Exit

- Entry logic: FUNDING_NORMALIZATION_TRIGGER or SPOT_PERP_BASIS_SHOCK (extreme positive)
- Entry lag: 1 bar
- Exit logic: Fixed horizon or basis reversion to mean.
- Invalidation: Basis continues to expand beyond extreme levels.
- Expected horizon: 12-48 bars (1h to 4h at 5m timeframe)

## Cost And Execution Assumptions

- Fee assumption: 5bps (taker)
- Slippage assumption: 2bps
- Funding assumption: High positive funding paid by longs (earned by shorts)
- Liquidity assumption: Standard BTCUSDT liquidity
- Execution realism risk: High volatility during normalization might increase slippage.

## Success Criteria

- Required artifact outputs: Phase 2 candidates, promotion diagnostics.
- Minimum cost-aware evidence: Positive after-cost expectancy.
- Required holdout or promotion evidence: Survival of bridge gates.
- What would count as mechanism confirmation: Significant alpha from shorting perps or longing spot when basis is extremely positive and starts normalizing.

## Kill Criteria

- What result would disconfirm the mechanism: Basis stays elevated or expands further without mean reversion.
- What cost result would kill the idea: Fees and slippage eat more than 70% of the gross alpha.
- What artifact inconsistency would invalidate the run: Missing funding data or mismatched spot/perp timestamps.
- What would force escalation instead of another run: Systematic failure of basis detectors.

## Negative Controls

- Required placebo or negative-control expectation: No edge when basis is near zero.
- What should not work if the mechanism is real: Trend continuation (longing perps) at extreme basis.

## Bounded Next Step

- If `keep`: Sharpen horizons and entry lags.
- If `modify`: Test different threshold quantiles for basis shock.
- If `kill`: Abandon basis-driven mean reversion for this period.
