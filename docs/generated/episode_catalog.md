# Episode catalog

## EP_VOLATILITY_BREAKOUT
- title: `Volatility breakout episode`
- tier: `B`
- role: `trigger`
- disposition: `secondary_trigger_candidate`
- required_events: `RANGE_COMPRESSION_END, VOL_SHOCK`
- optional_confirmation_events: `VOL_SPIKE`
- runtime_hint: `transition_or_volatility_move`
- description: Compression gives way to a directional volatility release and follow-through.

## EP_LIQUIDITY_SHOCK
- title: `Liquidity shock episode`
- tier: `B`
- role: `trigger`
- disposition: `secondary_trigger_candidate`
- required_events: `LIQUIDITY_VACUUM, VOL_SHOCK`
- optional_confirmation_events: `VOL_SPIKE`
- runtime_hint: `wide_spread_and_thin_depth`
- description: Microstructure thins, spreads widen, and a price shock emerges into unstable conditions.

## EP_DISLOCATION_REPAIR
- title: `Dislocation repair episode`
- tier: `C`
- role: `context`
- disposition: `context_only`
- required_events: `CROSS_VENUE_DESYNC, ABSORPTION_EVENT`
- optional_confirmation_events: `VOL_SHOCK`
- runtime_hint: `desync_reversion`
- description: A venue or basis dislocation normalizes as absorption and repair liquidity emerge.
