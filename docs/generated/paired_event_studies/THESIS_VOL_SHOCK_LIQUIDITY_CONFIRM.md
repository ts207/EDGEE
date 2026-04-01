# Direct paired-event study — THESIS_VOL_SHOCK_LIQUIDITY_CONFIRM

- thesis_id: `THESIS_VOL_SHOCK_LIQUIDITY_CONFIRM`
- selected_horizon_bars: `24`
- symbols: `BTCUSDT, ETHUSDT`
- trigger_component: `VOL SHOCK`
- confirm_component: `LIQUIDITY VACUUM`
- split: `2021 validation / 2022 test`

## Aggregate selected-horizon comparison

| Cohort | Events | Validation mean (bps) | Test mean (bps) | Total mean (bps) | Stability | Q-value |
|---|---:|---:|---:|---:|---:|---:|
| vol_shock_only | 3629 | 118.59 | 96.58 | 108.75 | 0.949 | 0.000000 |
| liquidity_vacuum_only | 977 | 113.86 | 85.44 | 101.29 | 0.929 | 0.000000 |
| joint_trigger | 110 | 130.65 | 71.95 | 103.43 | 0.855 | 0.000000 |

## Pair advantage diagnostics

- joint_minus_trigger_only_bps: `-5.321910999684334`
- joint_minus_confirmation_only_bps: `2.140565929691732`
- joint_test_advantage_vs_trigger_only_bps: `-24.629703644553203`
- joint_test_advantage_vs_confirmation_only_bps: `-13.491398405575765`

## Interpretation

This study closes the missing direct paired-event evidence gap for the packaged confirmation thesis.
Use the pair-vs-component comparison to decide whether the thesis should stay confirmation-scoped or be granted broader paper-grade use.
