# Shadow live thesis summary

- run_id: `block_h_shadow_live_v1`
- contexts_evaluated: `88`
- window: `2022-12-17 23:55:00+00:00` -> `2022-12-31 23:55:00+00:00`
- symbols: `BTCUSDT, ETHUSDT`
- trace_path: `/mnt/data/work_next/Edge-irene/data/reports/shadow_live/block_h_shadow_live_v1/shadow_live_thesis_trace.jsonl`

## Action counts

- `trade_normal`: `63`
- `trade_small`: `25`

## Confirmation thesis diagnostics

- retrieved_cycles: `176`
- eligible_cycles: `88`
- confirmation_match_cycles: `32`
- confirmation_missing_cycles: `144`
- top_ranked_cycles: `1`

## Confirmation thesis breakdown

- `THESIS_LIQUIDITY_VACUUM_CASCADE_CONFIRM` — retrieved `88`, matches `13`, missing `75`, top-ranked `0`
- `THESIS_VOL_SHOCK_LIQUIDITY_CONFIRM` — retrieved `88`, matches `19`, missing `69`, top-ranked `1`

## Quality checks

- no_silent_thesis_matches: `True`
- no_unexplained_holds: `True`
- overlap_metadata_visible_consistently: `True`
