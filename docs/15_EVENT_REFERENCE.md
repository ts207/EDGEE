# Event Reference

This document lists the event inventory that exists in the repository.

It is built from two canonical sources:

- unified event registry: [event_registry_unified.yaml](../spec/events/event_registry_unified.yaml)
- runtime detector registry: [events.yaml](../project/configs/registries/events.yaml)

Use this doc when you need to answer:

- which event families exist
- which event types belong to each family
- which event types are default executable
- which detector is wired at runtime
- whether a runtime event is enabled

## How To Read This

For each canonical family, each event line shows:

- event type
- `default`: whether the unified registry lists it in `default_executable_event_types`
- `legacy_family`: the compatibility family recorded in the unified event entry
- `detector`: the runtime detector name from the runtime registry
- `enabled`: the runtime enabled flag from the runtime registry
- `tags`: the runtime tags from the runtime registry

Facts to keep in mind:

- canonical family membership comes from [event_registry_unified.yaml](../spec/events/event_registry_unified.yaml)
- detector wiring comes from [events.yaml](../project/configs/registries/events.yaml)
- some canonical event types do not currently have a runtime detector entry
- some runtime detector entries exist outside the canonical-family list in this doc

## Canonical Families

### BASIS_FUNDING_DISLOCATION

- `BASIS_DISLOC` | `default=yes` | `legacy_family=BASIS_DISLOC` | `detector=BasisDislocationDetector` | `enabled=True` | `tags=basis_dislocation`
- `CROSS_VENUE_DESYNC` | `default=yes` | `legacy_family=CROSS_VENUE_DESYNC` | `detector=CrossVenueDesyncDetector` | `enabled=True` | `tags=desync`
- `FND_DISLOC` | `default=yes` | `legacy_family=FND_DISLOC` | `detector=FndDislocDetector` | `enabled=True` | `tags=basis_dislocation`
- `FUNDING_EXTREME_ONSET` | `default=yes` | `legacy_family=FUNDING_EXTREME_ONSET` | `detector=FundingExtremeOnsetDetector` | `enabled=True` | `tags=funding_crowding`
- `FUNDING_FLIP` | `default=yes` | `legacy_family=FUNDING_FLIP` | `detector=FundingFlipDetector` | `enabled=True` | `tags=funding_crowding,high_urgency`
- `FUNDING_NORMALIZATION_TRIGGER` | `default=yes` | `legacy_family=FUNDING_NORMALIZATION_TRIGGER` | `detector=FundingNormalizationDetector` | `enabled=True` | `tags=funding_crowding`
- `FUNDING_PERSISTENCE_TRIGGER` | `default=yes` | `legacy_family=FUNDING_PERSISTENCE_TRIGGER` | `detector=FundingPersistenceDetector` | `enabled=True` | `tags=funding_crowding`
- `SEQ_FND_EXTREME_THEN_BREAKOUT` | `default=no` | `legacy_family=SEQ_FND_EXTREME_THEN_BREAKOUT` | `detector=EventSequenceDetector` | `enabled=True` | `tags=funding_crowding,sequence`
- `SPOT_PERP_BASIS_SHOCK` | `default=yes` | `legacy_family=SPOT_PERP_BASIS_SHOCK` | `detector=SpotPerpBasisShockDetector` | `enabled=True` | `tags=desync,basis_dislocation,high_urgency`

### CROSS_ASSET_DESYNCHRONIZATION

- `CROSS_ASSET_DESYNC_EVENT` | `default=yes` | `legacy_family=CROSS_ASSET_DESYNC_EVENT` | `detector=CrossAssetDesyncDetector` | `enabled=True` | `tags=desync`
- `INDEX_COMPONENT_DIVERGENCE` | `default=yes` | `legacy_family=INDEX_COMPONENT_DIVERGENCE` | `detector=IndexComponentDivergenceDetector` | `enabled=True` | `tags=desync`
- `LEAD_LAG_BREAK` | `default=yes` | `legacy_family=LEAD_LAG_BREAK` | `detector=LeadLagBreakDetector` | `enabled=True` | `tags=desync`

### EXECUTION_FRICTION

- `FEE_REGIME_CHANGE_EVENT` | `default=yes` | `legacy_family=FEE_REGIME_CHANGE_EVENT` | `detector=FeeRegimeChangeDetector` | `enabled=True` | `tags=execution_cost`
- `SLIPPAGE_SPIKE_EVENT` | `default=yes` | `legacy_family=SLIPPAGE_SPIKE_EVENT` | `detector=SlippageSpikeDetector` | `enabled=True` | `tags=execution_cost,high_urgency`
- `SPREAD_REGIME_WIDENING_EVENT` | `default=yes` | `legacy_family=SPREAD_REGIME_WIDENING_EVENT` | `detector=SpreadRegimeWideningDetector` | `enabled=True` | `tags=execution_cost,liquidity_stress`

### LIQUIDATION_CASCADE

- `LIQUIDATION_CASCADE` | `default=yes` | `legacy_family=LIQUIDATION_CASCADE` | `detector=LiquidationCascadeDetector` | `enabled=True` | `tags=forced_liquidation,high_urgency`

### LIQUIDITY_STRESS

- `ABSORPTION_PROXY` | `default=yes` | `legacy_family=ABSORPTION_PROXY` | `detector=` | `enabled=` | `tags=`
- `DEPTH_COLLAPSE` | `default=yes` | `legacy_family=DEPTH_COLLAPSE` | `detector=DepthCollapseDetector` | `enabled=True` | `tags=liquidity_stress`
- `DEPTH_STRESS_PROXY` | `default=yes` | `legacy_family=DEPTH_STRESS_PROXY` | `detector=` | `enabled=` | `tags=`
- `LIQUIDITY_GAP_PRINT` | `default=yes` | `legacy_family=LIQUIDITY_GAP_PRINT` | `detector=LiquidityGapDetector` | `enabled=True` | `tags=liquidity_stress`
- `LIQUIDITY_SHOCK` | `default=yes` | `legacy_family=LIQUIDITY_SHOCK` | `detector=LiquidityStressDetector` | `enabled=True` | `tags=liquidity_stress,high_urgency`
- `LIQUIDITY_STRESS_DIRECT` | `default=yes` | `legacy_family=LIQUIDITY_STRESS_DIRECT` | `detector=` | `enabled=` | `tags=`
- `LIQUIDITY_STRESS_PROXY` | `default=yes` | `legacy_family=LIQUIDITY_STRESS_PROXY` | `detector=` | `enabled=` | `tags=`
- `LIQUIDITY_VACUUM` | `default=yes` | `legacy_family=LIQUIDITY_VACUUM` | `detector=LiquidityVacuumDetector` | `enabled=True` | `tags=liquidity_stress,high_urgency`
- `ORDERFLOW_IMBALANCE_SHOCK` | `default=yes` | `legacy_family=ORDERFLOW_IMBALANCE_SHOCK` | `detector=OrderflowImbalanceDetector` | `enabled=True` | `tags=orderflow_imbalance`
- `PRICE_VOL_IMBALANCE_PROXY` | `default=yes` | `legacy_family=PRICE_VOL_IMBALANCE_PROXY` | `detector=` | `enabled=` | `tags=`
- `SEQ_LIQ_VACUUM_THEN_DEPTH_RECOVERY` | `default=no` | `legacy_family=SEQ_LIQ_VACUUM_THEN_DEPTH_RECOVERY` | `detector=EventSequenceDetector` | `enabled=True` | `tags=liquidity_stress,absorption_recovery,sequence`
- `SPREAD_BLOWOUT` | `default=yes` | `legacy_family=SPREAD_BLOWOUT` | `detector=SpreadBlowoutDetector` | `enabled=True` | `tags=liquidity_stress,execution_cost`
- `SWEEP_STOPRUN` | `default=yes` | `legacy_family=SWEEP_STOPRUN` | `detector=StopRunDetector` | `enabled=True` | `tags=orderflow_imbalance,high_urgency`
- `WICK_REVERSAL_PROXY` | `default=yes` | `legacy_family=WICK_REVERSAL_PROXY` | `detector=` | `enabled=` | `tags=`

### POSITIONING_EXPANSION

- `OI_SPIKE_NEGATIVE` | `default=yes` | `legacy_family=OI_SPIKE_NEGATIVE` | `detector=OISpikeNegativeDetector` | `enabled=True` | `tags=oi_dynamic`
- `OI_SPIKE_POSITIVE` | `default=yes` | `legacy_family=OI_SPIKE_POSITIVE` | `detector=OISpikePositiveDetector` | `enabled=True` | `tags=oi_dynamic`
- `SEQ_OI_SPIKEPOS_THEN_VOL_SPIKE` | `default=no` | `legacy_family=SEQ_OI_SPIKEPOS_THEN_VOL_SPIKE` | `detector=EventSequenceDetector` | `enabled=True` | `tags=oi_dynamic,sequence`

### POSITIONING_UNWIND_DELEVERAGING

- `DELEVERAGING_WAVE` | `default=yes` | `legacy_family=DELEVERAGING_WAVE` | `detector=DeleveragingWaveDetector` | `enabled=True` | `tags=forced_liquidation,oi_dynamic`
- `OI_FLUSH` | `default=yes` | `legacy_family=OI_FLUSH` | `detector=OIFlushDetector` | `enabled=True` | `tags=oi_dynamic,high_urgency`
- `POST_DELEVERAGING_REBOUND` | `default=yes` | `legacy_family=POST_DELEVERAGING_REBOUND` | `detector=` | `enabled=` | `tags=`

### REGIME_TRANSITION

- `BETA_SPIKE_EVENT` | `default=yes` | `legacy_family=BETA_SPIKE_EVENT` | `detector=BetaSpikeDetector` | `enabled=True` | `tags=regime_shift`
- `CHOP_TO_TREND_SHIFT` | `default=yes` | `legacy_family=CHOP_TO_TREND_SHIFT` | `detector=ChopToTrendDetector` | `enabled=True` | `tags=regime_shift,trend_momentum`
- `CORRELATION_BREAKDOWN_EVENT` | `default=yes` | `legacy_family=CORRELATION_BREAKDOWN_EVENT` | `detector=CorrelationBreakdownDetector` | `enabled=True` | `tags=regime_shift`
- `TREND_TO_CHOP_SHIFT` | `default=yes` | `legacy_family=TREND_TO_CHOP_SHIFT` | `detector=TrendToChopDetector` | `enabled=True` | `tags=regime_shift,trend_momentum`
- `VOL_REGIME_SHIFT_EVENT` | `default=yes` | `legacy_family=VOL_REGIME_SHIFT_EVENT` | `detector=VolRegimeShiftDetector` | `enabled=True` | `tags=regime_shift,vol_regime`

### SCHEDULED_TEMPORAL_WINDOW

- `FUNDING_TIMESTAMP_EVENT` | `default=no` | `legacy_family=FUNDING_TIMESTAMP_EVENT` | `detector=FundingTimestampDetector` | `enabled=True` | `tags=temporal_anchor,funding_crowding`
- `SCHEDULED_NEWS_WINDOW_EVENT` | `default=no` | `legacy_family=SCHEDULED_NEWS_WINDOW_EVENT` | `detector=ScheduledNewsDetector` | `enabled=True` | `tags=temporal_anchor`
- `SESSION_CLOSE_EVENT` | `default=no` | `legacy_family=SESSION_CLOSE_EVENT` | `detector=SessionCloseDetector` | `enabled=True` | `tags=temporal_anchor`
- `SESSION_OPEN_EVENT` | `default=no` | `legacy_family=SESSION_OPEN_EVENT` | `detector=SessionOpenDetector` | `enabled=True` | `tags=temporal_anchor`

### STATISTICAL_STRETCH_OVERSHOOT

- `BAND_BREAK` | `default=yes` | `legacy_family=BAND_BREAK` | `detector=BandBreakDetector` | `enabled=True` | `tags=statistical_stretch`
- `COPULA_PAIRS_TRADING` | `default=no` | `legacy_family=COPULA_PAIRS_TRADING` | `detector=CopulaPairsTradingDetector` | `enabled=True` | `tags=basis_dislocation`
- `GAP_OVERSHOOT` | `default=yes` | `legacy_family=GAP_OVERSHOOT` | `detector=GapOvershootDetector` | `enabled=True` | `tags=statistical_stretch`
- `OVERSHOOT_AFTER_SHOCK` | `default=yes` | `legacy_family=OVERSHOOT_AFTER_SHOCK` | `detector=OvershootDetector` | `enabled=True` | `tags=statistical_stretch`
- `ZSCORE_STRETCH` | `default=yes` | `legacy_family=ZSCORE_STRETCH` | `detector=ZScoreStretchDetector` | `enabled=True` | `tags=statistical_stretch`

### TREND_CONTINUATION

- `PULLBACK_PIVOT` | `default=yes` | `legacy_family=PULLBACK_PIVOT` | `detector=PullbackPivotDetector` | `enabled=True` | `tags=trend_momentum`
- `RANGE_BREAKOUT` | `default=yes` | `legacy_family=RANGE_BREAKOUT` | `detector=RangeBreakoutDetector` | `enabled=True` | `tags=trend_momentum`
- `SUPPORT_RESISTANCE_BREAK` | `default=yes` | `legacy_family=SUPPORT_RESISTANCE_BREAK` | `detector=SREventDetector` | `enabled=True` | `tags=trend_momentum`
- `TREND_ACCELERATION` | `default=yes` | `legacy_family=TREND_ACCELERATION` | `detector=TrendAccelerationDetector` | `enabled=True` | `tags=trend_momentum`

### TREND_FAILURE_EXHAUSTION

- `CLIMAX_VOLUME_BAR` | `default=yes` | `legacy_family=CLIMAX_VOLUME_BAR` | `detector=ClimaxVolumeDetector` | `enabled=True` | `tags=exhaustion,high_urgency`
- `FAILED_CONTINUATION` | `default=yes` | `legacy_family=FAILED_CONTINUATION` | `detector=FailedContinuationDetector` | `enabled=True` | `tags=exhaustion`
- `FALSE_BREAKOUT` | `default=yes` | `legacy_family=FALSE_BREAKOUT` | `detector=FalseBreakoutDetector` | `enabled=True` | `tags=trend_momentum,exhaustion`
- `FLOW_EXHAUSTION_PROXY` | `default=yes` | `legacy_family=FLOW_EXHAUSTION_PROXY` | `detector=` | `enabled=` | `tags=`
- `FORCED_FLOW_EXHAUSTION` | `default=yes` | `legacy_family=FORCED_FLOW_EXHAUSTION` | `detector=ForcedFlowExhaustionDetector` | `enabled=True` | `tags=exhaustion,forced_liquidation`
- `LIQUIDATION_EXHAUSTION_REVERSAL` | `default=yes` | `legacy_family=LIQUIDATION_EXHAUSTION_REVERSAL` | `detector=PostDeleveragingReboundDetector` | `enabled=True` | `tags=forced_liquidation`
- `MOMENTUM_DIVERGENCE_TRIGGER` | `default=yes` | `legacy_family=MOMENTUM_DIVERGENCE_TRIGGER` | `detector=MomentumDivergenceDetector` | `enabled=True` | `tags=exhaustion`
- `TREND_DECELERATION` | `default=yes` | `legacy_family=TREND_DECELERATION` | `detector=TrendDecelerationDetector` | `enabled=True` | `tags=trend_momentum`
- `TREND_EXHAUSTION_TRIGGER` | `default=yes` | `legacy_family=TREND_EXHAUSTION_TRIGGER` | `detector=TrendExhaustionDetector` | `enabled=True` | `tags=exhaustion,trend_momentum`

### VOLATILITY_EXPANSION

- `VOL_CLUSTER_SHIFT` | `default=yes` | `legacy_family=VOL_CLUSTER_SHIFT` | `detector=VolClusterShiftDetector` | `enabled=True` | `tags=vol_regime`
- `VOL_SPIKE` | `default=yes` | `legacy_family=VOL_SPIKE` | `detector=VolSpikeDetector` | `enabled=True` | `tags=vol_regime,high_urgency`

### VOLATILITY_RELAXATION_COMPRESSION_RELEASE

- `BREAKOUT_TRIGGER` | `default=yes` | `legacy_family=BREAKOUT_TRIGGER` | `detector=BreakoutTriggerDetector` | `enabled=True` | `tags=vol_regime,trend_momentum`
- `RANGE_COMPRESSION_END` | `default=yes` | `legacy_family=RANGE_COMPRESSION_END` | `detector=RangeCompressionDetector` | `enabled=True` | `tags=vol_regime`
- `SEQ_VOL_COMP_THEN_BREAKOUT` | `default=no` | `legacy_family=SEQ_VOL_COMP_THEN_BREAKOUT` | `detector=EventSequenceDetector` | `enabled=True` | `tags=vol_regime,sequence`
- `VOL_RELAXATION_START` | `default=yes` | `legacy_family=VOL_RELAXATION_START` | `detector=VolRelaxationDetector` | `enabled=True` | `tags=vol_regime`

### VOLATILITY_TRANSITION

- `VOL_SHOCK` | `default=yes` | `legacy_family=VOL_SHOCK` | `detector=VolShockRelaxationDetector` | `enabled=True` | `tags=vol_regime,high_urgency`

## Coverage Notes

Runtime detector coverage is not perfectly complete.

Canonical event types in this doc with no runtime detector entry shown:

- `ABSORPTION_PROXY`
- `DEPTH_STRESS_PROXY`
- `LIQUIDITY_STRESS_DIRECT`
- `LIQUIDITY_STRESS_PROXY`
- `PRICE_VOL_IMBALANCE_PROXY`
- `POST_DELEVERAGING_REBOUND`
- `FLOW_EXHAUSTION_PROXY`
- `WICK_REVERSAL_PROXY`

This means:

- they exist in the canonical unified event model
- but they do not currently have a detector entry in [events.yaml](../project/configs/registries/events.yaml)

## Runtime-Only Event Entries

The runtime registry also contains enabled event entries that are not part of the canonical family list above.

Examples include:

- `ABSORPTION_EVENT`
- `BASIS_SNAPBACK`
- `CROSS_VENUE_CATCHUP`
- `DEPTH_RECOVERY_EVENT`
- `FUNDING_EXTREME_BREAKOUT`
- `FUNDING_EXTREME_STAGNATION`
- `IMBALANCE_ABSORPTION_REVERSAL`
- `OI_VOL_COMPRESSION_BUILDUP`
- `OI_VOL_DIVERGENCE`
- `SEQ_LIQ_CASCADE_THEN_EXHAUST`
- `VOL_COMPRESSION_BREAKOUT`

These are present in [events.yaml](../project/configs/registries/events.yaml), but they are not part of the canonical family inventory in [event_registry_unified.yaml](../spec/events/event_registry_unified.yaml).
