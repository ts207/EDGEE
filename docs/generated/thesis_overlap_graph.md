# Thesis Overlap Graph

- Schema version: `thesis_overlap_graph_v1`
- Thesis count: 4
- Overlap groups: 4

## Groups

- `LIQUIDATION_CASCADE::NO_EPISODE::FORCED_FLOW::trigger` — 1 member(s): THESIS_LIQUIDATION_CASCADE
- `LIQUIDITY_VACUUM::NO_EPISODE::LIQUIDITY_STRESS::trigger` — 1 member(s): THESIS_LIQUIDITY_VACUUM
- `VOL_SHOCK::NO_EPISODE::VOLATILITY_TRANSITION::confirm` — 1 member(s): THESIS_VOL_SHOCK_LIQUIDITY_CONFIRM
- `VOL_SHOCK::NO_EPISODE::VOLATILITY_TRANSITION::trigger` — 1 member(s): THESIS_VOL_SHOCK

## Highest-overlap edges

- `THESIS_VOL_SHOCK` ↔ `THESIS_VOL_SHOCK_LIQUIDITY_CONFIRM` — score 0.70; primary_event_id:VOL_SHOCK, event_contract_ids:VOL_SHOCK, canonical_regime:VOLATILITY_TRANSITION
- `THESIS_LIQUIDITY_VACUUM` ↔ `THESIS_VOL_SHOCK_LIQUIDITY_CONFIRM` — score 0.25; event_contract_ids:LIQUIDITY_VACUUM
