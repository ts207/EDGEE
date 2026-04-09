## Current state (2026-04-09)

### What has run

**Infrastructure (pipeline bugs fixed — all working)**
- 9 pipeline bugs fixed (dependency races, zero-output rejections, exit code handling, search engine event type routing, filter template mis-classification, DataFrame.attrs concat crash)
- Pipeline runs end-to-end, exit 0, all stages succeed or warn

**Shared lake cache populated**
- BTC+ETH 2021–2024 cleaned bars, features, market context written to shared lake
- Re-use `--run_id funding_extreme_combined` for same date range to skip data building (fastest cache)

---

### LIQUIDATION_CASCADE_PROXY — STOPPED

Run: `liq_proxy_combined` (BTC+ETH, 2021–2024)

| Symbol | Events | Best horizon | t_stat | mean bps |
|--------|--------|-------------|--------|----------|
| BTCUSDT | ~1000 | 60m long | 1.73 | 10.1 |
| ETHUSDT | ~930 | 60m long | 1.79 | 12.5 |

**Decision: STOP.** t ceiling ~1.8 (gate=2.0). Proxy fires on OI+volume coincidences including false positives. Best config locked: `oi_drop_quantile=0.98`, `vol_surge_quantile=0.90`.

---

### FUNDING_EXTREME_ONSET — ACTIVE, NEEDS REGIME CONDITIONING

Run: `funding_extreme_combined` (BTC+ETH, 2021–2024, 5m timeframe)

| Symbol | Horizon | Direction | t_stat | mean bps | n | robustness |
|--------|---------|-----------|--------|----------|---|------------|
| BTCUSDT | 60m | long | 3.27 | 14.97 | 684 | 0.4747 |
| ETHUSDT | — | — | <2.0 | — | — | — |

**Status: regime-conditional signal.** Signal is statistically real (t=3.27, q=0.001, passes FDR). Fails promotion because:
- `robustness_score=0.4747 < gate 0.6` → `gate_c_regime_stable=False`
- Signal works in ~7/11 market regimes (`regime_support_ratio=0.636`), fails in ~4
- `falsification_component=0.0` → `discovery_quality_score=-0.36`
- ETH: no signal at any horizon

**Root cause:** The unconditional search averages over all market regimes. In ~4 regimes (likely low-vol chop or deleveraging), funding extremes do not predict 60m reversals.

---

### Next step: regime-conditioned re-run

**Plan:** Add `only_if_regime` to FUNDING_EXTREME_ONSET's filter templates in `spec/templates/registry.yaml`. This adds hypotheses conditioned on `rv_pct_17280 > 0.7` (realized vol in top 30%), which should isolate the regime where the signal is strong.

**Step 1 — Edit `spec/templates/registry.yaml`** (the FUNDING_EXTREME_ONSET block):
```yaml
FUNDING_EXTREME_ONSET:
  ...
  templates:
  - reversal_or_squeeze
  - mean_reversion
  - continuation
  - exhaustion_reversal
  - convexity_capture
  - only_if_funding
  - only_if_oi
  - only_if_regime      # ← ADD THIS (rv_pct_17280 > 0.7 = high-vol conditioning)
  - tail_risk_avoid
```

**Step 2 — Re-run** (cache hits from `funding_extreme_combined`):
```
python3 -m project.pipelines.run_all \
  --run_id funding_extreme_highvol \
  --symbols BTCUSDT,ETHUSDT \
  --start 2021-01-01 \
  --end 2024-12-31 \
  --events FUNDING_EXTREME_ONSET \
  --timeframe 5m
```

**What to look for:** A new candidate with `filter_template_id=only_if_regime` at 60m long with `robustness_score >= 0.6`. If found, check whether it also passes `gate_oos_validation` (≥0.7).

**Alternative conditioning:** If `only_if_regime` doesn't help, try `only_if_trend` (logret_1 > 0.001, trending market). Available columns in features also include `high_vol_regime`, `bull_trend_regime`, `chop_regime` for manual slicing.

**Filter template definitions** (from `spec/templates/registry.yaml` `filter_templates:` section):
- `only_if_regime`: `rv_pct_17280 > 0.7` (high realized vol)
- `only_if_trend`: `logret_1 > 0.001` (recent positive momentum)
- `only_if_funding`: `funding_rate > 0.0` (positive funding)

---

### Infrastructure facts

- `spec/events/LIQUIDATION_CASCADE_PROXY.yaml` — `oi_drop_quantile: 0.98` is best calibration (do not change)
- `spec/templates/registry.yaml` — LIQUIDATION_CASCADE_PROXY added; FUNDING_EXTREME_ONSET has funding+oi filter templates
- `project/events/phase2.py` — LIQUIDATION_CASCADE_PROXY added to PHASE2_EVENT_CHAIN
- `--events EVENTNAME` correctly pins `phase2_event_type` in the planner
- Filter templates are correctly separated from expression templates in resolved search specs
- `promote_candidates` exits 1 + warns (not fails) for missing validation bundle — expected in discovery runs
- Lake cache at `data/lake/runs/funding_extreme_combined/` covers BTC+ETH 2021–2024 fully
