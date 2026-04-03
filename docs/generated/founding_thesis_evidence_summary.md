# Founding thesis evidence summary

This artifact records the first raw-data empirical bundle generation pass against the founding thesis queue.

## Policy notes

- Generate canonical evidence bundles directly from raw perp market data.
- The first founding batch is intentionally narrow: five standalone event theses.
- Basis and funding dislocation bundles may use canonical feature-schema inputs when dedicated paired raw archives are absent.
- Liquidation cascade bundles may fall back to a feature-schema forced-flow proxy when liquidation and open-interest archives are unavailable in the founding batch.
- Confirmation and episode theses remain in the registry, but they are not part of the first empirical packaging batch.

- generated_theses: `4`
- unsupported_or_skipped: `1`

## Generated evidence bundles

| Candidate | Event | Symbols | Horizon | Bundles | Sample size | Mean net expectancy (bps) |
|---|---|---|---:|---:|---:|---:|
| THESIS_BASIS_DISLOC | BASIS_DISLOC | BTCUSDT | 24 | 1 | 47 | 123.49 |
| THESIS_FND_DISLOC | FND_DISLOC | BTCUSDT | 8 | 1 | 35 | 102.72 |
| THESIS_VOL_SHOCK | VOL_SHOCK | BTCUSDT|ETHUSDT | 24 | 2 | 6618 | 84.25 |
| THESIS_LIQUIDITY_VACUUM | LIQUIDITY_VACUUM | BTCUSDT|ETHUSDT | 24 | 2 | 2192 | 71.85 |

## Unsupported or skipped

- `THESIS_LIQUIDATION_CASCADE` — insufficient_event_count_after_detection
