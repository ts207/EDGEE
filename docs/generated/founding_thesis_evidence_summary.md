# Founding thesis evidence summary

This artifact records the first raw-data empirical bundle generation pass against the founding thesis queue.

## Policy notes

- Generate canonical evidence bundles directly from raw perp market data.
- This archive does not include spot-perp basis inputs, so BASIS_DISLOC and FND_DISLOC are not part of the first supported empirical run.
- The first supported raw-data pass targets volatility, liquidity, and forced-flow theses.
- The next supported structural thesis is VOL_SHOCK + LIQUIDITY_VACUUM confirmation, which shares raw-data inputs with the first volatility/liquidity passes.
- A second supported structural thesis uses LIQUIDITY_VACUUM + LIQUIDATION_CASCADE co-occurrence to deepen the overlap graph around liquidity stress and forced-flow conditions.

- generated_theses: `5`
- unsupported_or_skipped: `0`

## Generated evidence bundles

| Candidate | Event | Symbols | Horizon | Bundles | Sample size | Mean net expectancy (bps) |
|---|---|---|---:|---:|---:|---:|
| THESIS_VOL_SHOCK | VOL_SHOCK | BTCUSDT|ETHUSDT | 24 | 2 | 3739 | 102.33 |
| THESIS_LIQUIDITY_VACUUM | LIQUIDITY_VACUUM | BTCUSDT|ETHUSDT | 24 | 2 | 1083 | 95.43 |
| THESIS_LIQUIDATION_CASCADE | LIQUIDATION_CASCADE | BTCUSDT|ETHUSDT | 24 | 2 | 329 | 121.45 |
| THESIS_VOL_SHOCK_LIQUIDITY_CONFIRM | VOL_SHOCK_LIQUIDITY_CONFIRM | BTCUSDT|ETHUSDT | 24 | 2 | 110 | 96.71 |
| THESIS_LIQUIDITY_VACUUM_CASCADE_CONFIRM | LIQUIDITY_VACUUM_CASCADE_CONFIRM | BTCUSDT|ETHUSDT | 48 | 1 | 39 | 145.95 |
