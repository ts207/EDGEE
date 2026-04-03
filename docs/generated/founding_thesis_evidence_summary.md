# Founding thesis evidence summary

This artifact records the first raw-data empirical bundle generation pass against the founding thesis queue.

## Policy notes

- Generate canonical evidence bundles directly from raw perp market data.
- The first founding batch is intentionally narrow: five standalone event theses.
- Basis and funding dislocation bundles may use canonical feature-schema inputs when dedicated paired raw archives are absent.
- Liquidation cascade bundles may fall back to a feature-schema forced-flow proxy when liquidation and open-interest archives are unavailable in the founding batch.
- Confirmation and episode theses remain in the registry, but they are not part of the first empirical packaging batch.

- generated_theses: `3`
- unsupported_or_skipped: `2`

## Generated evidence bundles

| Candidate | Event | Symbols | Horizon | Bundles | Sample size | Mean net expectancy (bps) |
|---|---|---|---:|---:|---:|---:|
| THESIS_VOL_SHOCK | VOL_SHOCK | BTCUSDT|ETHUSDT | 24 | 2 | 3739 | 102.33 |
| THESIS_LIQUIDITY_VACUUM | LIQUIDITY_VACUUM | BTCUSDT|ETHUSDT | 24 | 2 | 1083 | 95.43 |
| THESIS_LIQUIDATION_CASCADE | LIQUIDATION_CASCADE | BTCUSDT|ETHUSDT | 24 | 2 | 375 | 119.74 |

## Unsupported or skipped

- `THESIS_BASIS_DISLOC` — required_input_dataset_missing
- `THESIS_FND_DISLOC` — required_input_dataset_missing
