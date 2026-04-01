# Direct paired-event study — THESIS_LIQUIDITY_VACUUM_CASCADE_CONFIRM

- thesis_id: `THESIS_LIQUIDITY_VACUUM_CASCADE_CONFIRM`
- selected_horizon_bars: `48`
- symbols: `BTCUSDT, ETHUSDT`
- trigger_component: `LIQUIDITY VACUUM`
- confirm_component: `LIQUIDATION CASCADE`
- split: `2021 validation / 2022 test`

## Aggregate selected-horizon comparison

| Cohort | Events | Validation mean (bps) | Test mean (bps) | Total mean (bps) | Stability | Q-value |
|---|---:|---:|---:|---:|---:|---:|
| liquidity_vacuum_only | 1028 | 155.90 | 117.22 | 138.93 | 0.929 | 0.000000 |
| liquidation_cascade_only | 260 | 175.06 | 145.70 | 154.62 | 0.954 | 0.000000 |
| joint_trigger | 55 | 192.59 | 136.77 | 161.13 | 0.915 | 0.000005 |

## Pair advantage diagnostics

- joint_minus_trigger_only_bps: `22.197104377651016`
- joint_minus_confirmation_only_bps: `6.513005163510144`
- joint_test_advantage_vs_trigger_only_bps: `19.547045153118944`
- joint_test_advantage_vs_confirmation_only_bps: `-8.924703445941276`

## Interpretation

This study closes the missing direct paired-event evidence gap for the packaged confirmation thesis.
Use the pair-vs-component comparison to decide whether the thesis should stay confirmation-scoped or be granted broader paper-grade use.
