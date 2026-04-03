# Worked Example: BTC 2021-2022 Observation Campaign

This example walks through the full specialist-agent pipeline using the
`btc_obs_2021_2022_campaign` program as the reference pattern.

## Background

The BTC 2021-2022 campaign is an observation-only run focused on volatility
expansion, breakout continuation, and breakout failure in BTCUSDT across the
2021-01-01 to 2022-12-31 window. Promotion is disabled — the goal is hypothesis
formation, not deployment.

Original proposal: `spec/proposals/btcvolexp2122.yaml`

---

## Step 1: Execute the Original Run

The coordinator runs the existing proposal:

```bash
# Explain normalization first
edge operator explain --proposal $(pwd)/spec/proposals/btcvolexp2122.yaml

# Preflight and plan
edge operator preflight --proposal $(pwd)/spec/proposals/btcvolexp2122.yaml
edge operator plan --proposal $(pwd)/spec/proposals/btcvolexp2122.yaml \
  --run_id btc_obs_2021_2022_campai_20260330_obs

# Execute (after plan review)
edge operator run --proposal $(pwd)/spec/proposals/btcvolexp2122.yaml \
  --run_id btc_obs_2021_2022_campai_20260330_obs
```

---

## Step 2: Invoke Analyst

After the run completes, the coordinator gathers artifacts and invokes the analyst.

### Coordinator gathers:
```bash
# Check run manifest
cat data/runs/btc_obs_2021_2022_campai_20260330_obs/run_manifest.json | python -m json.tool

# Check phase2 diagnostics
cat data/reports/phase2/btc_obs_2021_2022_campai_20260330_obs/phase2_diagnostics.json | python -m json.tool

# Inspect candidates
python -c "
import pandas as pd
df = pd.read_parquet('data/reports/phase2/btc_obs_2021_2022_campai_20260330_obs/phase2_candidates.parquet')
print(f'Candidates: {len(df)}')
if len(df) > 0:
    print(df[['event_type','template_verb','horizon','direction','effect_raw','p_value','q_value','selection_score','fail_gate_primary']].head(10))
else:
    print('EMPTY - must inspect upstream')
"
```

### Hypothetical Analyst Report

```markdown
# Analyst Report: btc_obs_2021_2022_campai_20260330_obs

## Run Health
- pipeline_status: success
- failed_stage: none
- stages_completed: 8 / 8
- data_quality_flags: []

## Funnel Summary
- hypotheses_generated: 148
- feasible: 112
- evaluated: 112
- passed_phase2_gate: 3
- bridge_candidates: 0
- promoted: 0 (promotion disabled)

## Primary Rejection Mechanism
- gate: gate_phase2_final
- reason: min_after_cost_expectancy_bps
- fraction_rejected_here: 62%
- interpretation: Most hypotheses show raw signal but fail cost survival

## Strongest Near-Misses (top 3)
1. VOL_SHOCK / continuation / 24 bars / short
   - effect_raw: -18.2 bps, p_value: 0.008, q_value: 0.06
   - fail: min_after_cost_expectancy_bps (after-cost: -0.3 bps)
   - how close: cost assumptions would need ~1 bps reduction

2. RANGE_BREAKOUT / continuation / 72 bars / long
   - effect_raw: 22.5 bps, p_value: 0.012, q_value: 0.08
   - fail: min_after_cost_expectancy_bps (after-cost: 0.05 bps)
   - how close: barely below threshold, longer horizon helps

3. FALSE_BREAKOUT / continuation / 12 bars / short
   - effect_raw: -12.1 bps, p_value: 0.03, q_value: 0.12
   - fail: require_sign_stability
   - how close: sign flips in 2 of 5 sub-windows

## Asymmetry Read
- long_vs_short: short side shows more consistent signal for VOL_SHOCK events
- horizon_pattern: 24-bar and 72-bar horizons show clearer signal than 12-bar
- event_type_pattern: VOL_SHOCK strongest; BREAKOUT_TRIGGER weakest

## Mechanistic Meaning
- what_the_data_says: Vol shocks in BTC 2021-2022 created short-lived dislocations
  that continuation templates partially capture, but the effect is marginal after costs
  at short horizons. Longer horizons (72 bars) show better cost survival for breakouts.
- what_the_data_does_not_say: The data does not confirm a tradable edge at the
  current cost model. The near-misses could be noise survivors.
- regime_interpretation: The VOLATILITY_EXPANSION regime during 2021-2022 was
  characterized by frequent vol shocks with rapid mean-reversion, making continuation
  templates an imperfect fit.

## Recommended Next Experiments (1-3)
1. rationale: VOL_SHOCK 24-bar short near-miss suggests testing mean_reversion
   template instead of continuation, since the mechanism appears to be vol-shock
   followed by reversion rather than continuation
   change_type: shift
   what_to_change: templates from [continuation] to [mean_reversion]
   what_to_freeze: events, symbols, dates, horizons, directions
   expected_information_gain: confirms whether the signal is reversion not continuation
   stop_condition: kill if mean_reversion also fails cost gate

2. rationale: RANGE_BREAKOUT 72-bar long near-miss suggests longer horizons
   improve cost survival; test with horizons [48, 72, 288] to find the sweet spot
   change_type: narrow
   what_to_change: horizons_bars from [12, 24, 72] to [48, 72, 288]
   what_to_freeze: events [RANGE_BREAKOUT], templates, symbols, dates, direction [long]
   expected_information_gain: identifies optimal horizon for breakout cost survival
   stop_condition: kill if no horizon passes cost gate
```

---

## Step 3: Invoke Mechanism Hypothesis

The coordinator reviews the analyst report, confirms no pipeline failure and
no kill recommendation, then invokes mechanism_hypothesis.

### Hypothetical Mechanism Hypothesis Output

```markdown
# Mechanism Hypothesis: btc_obs_2021_2022_campaign_h1_v1

## Version
- version: 1
- parent_hypothesis: none
- parent_run_id: btc_obs_2021_2022_campai_20260330_obs

## Mechanism Statement
During BTC's volatile 2021-2022 period, sudden volatility shocks create transient
dislocations where price overshoots fair value. Forced liquidations and stop-runs
during these shocks push price beyond equilibrium, and the market mean-reverts over
the next 1-2 hours (12-24 bars at 5m). This reversion, not continuation, is the
tradable pattern.

## Trigger / Event Family
- primary_event_family: VOLATILITY_TRANSITION
- events_include: [VOL_SHOCK]
- canonical_regime: VOLATILITY_EXPANSION

## Direction
- direction: [short]
- rationale: Analyst report shows short side more consistent for VOL_SHOCK;
  mechanism expects price overshoot then reversion downward after upside shocks

## Horizon
- horizons_bars: [12, 24]
- rationale: Near-miss was at 24 bars; include 12 as lower bound to bracket
  the reversion window. 72+ bars likely too long for mean-reversion.

## Context Filter
- contexts: {}
- rationale: No context conditioning in first version; add only if this version
  shows regime-dependent performance

## Template
- templates: [mean_reversion]
- rationale: Analyst report suggests reversion not continuation; mean_reversion
  is valid for VOLATILITY_TRANSITION family

## Invalidation
- kill_if: mean_reversion template also fails min_after_cost_expectancy_bps gate
- example: effect_raw < 10 bps or q_value > 0.10 across all horizons

## Likely Failure Mode
- expected_failure: Cost gate still binding — the reversion exists but is too
  small to survive spread + slippage
- diagnostic: Check after-cost expectancy in analyst report; if raw effect is
  strong but after-cost fails, the mechanism is real but not tradable

## Allowed Knobs
- symbols: [BTCUSDT]
- start / end: 2021-01-01 / 2022-12-31
- horizons_bars: [12, 24]
- entry_lags: [1, 2]
- search_control: max_hypotheses_total <= 150

## Frozen Knobs
- trigger_space.events.include: [VOL_SHOCK]
- trigger_space.canonical_regimes: [VOLATILITY_EXPANSION]
- templates: [mean_reversion]
- direction: [short]
- timeframe: 5m
- promotion_profile: disabled
- objective_name: retail_profitability
```

---

## Step 4: Coordinator Validates (Scope Drift Check)

The coordinator checks:
- [x] VOL_SHOCK exists in canonical_event_registry.yaml
- [x] mean_reversion is valid for VOLATILITY_TRANSITION family
- [x] Horizons 12, 24 are supported bar counts
- [x] VOLATILITY_EXPANSION exists in regime_routing.yaml
- [x] No symbol expansion (still [BTCUSDT])
- [x] No date expansion (still 2021-2022)
- [x] Direction justified by analyst asymmetry read

No drift detected. Proceed to compiler.

---

## Step 5: Invoke Compiler

### Hypothetical Compiler Output

```markdown
# Compiled Proposal: btc_obs_2021_2022_campaign_h1_v1

## Proposal Path
`spec/proposals/btc_obs_2021_2022_campaign_h1_v1.yaml`

## Proposal YAML
```yaml
program_id: btc_obs_2021_2022_campaign
description: >
  Hypothesis h1_v1: VOL_SHOCK mean-reversion in BTC 2021-2022.
  Tests whether vol shocks create tradable reversion on the short side
  at 12-24 bar horizons, using mean_reversion template instead of
  continuation (which failed cost gate in parent run).
objective_name: retail_profitability
promotion_profile: disabled
run_mode: research

symbols: [BTCUSDT]
timeframe: 5m
start: "2021-01-01"
end: "2022-12-31"

trigger_space:
  allowed_trigger_types: [EVENT]
  events:
    include: [VOL_SHOCK]
  canonical_regimes: [VOLATILITY_EXPANSION]

templates: [mean_reversion]
horizons_bars: [12, 24]
directions: [short]
entry_lags: [1, 2]

search_control:
  max_hypotheses_total: 150
  max_hypotheses_per_template: 80
  max_hypotheses_per_event_family: 100
```

## Explain Command
```bash
edge operator explain --proposal $(pwd)/spec/proposals/btc_obs_2021_2022_campaign_h1_v1.yaml
```

## Preflight Command
```bash
edge operator preflight --proposal $(pwd)/spec/proposals/btc_obs_2021_2022_campaign_h1_v1.yaml
```

## Plan Command
```bash
edge operator plan --proposal $(pwd)/spec/proposals/btc_obs_2021_2022_campaign_h1_v1.yaml \
  --run_id btc_obs_2021_2022_campai_h1v1_20260331
```

## Execution Command
```bash
edge operator run --proposal $(pwd)/spec/proposals/btc_obs_2021_2022_campaign_h1_v1.yaml \
  --run_id btc_obs_2021_2022_campai_h1v1_20260331
```

## Plan Review Checklist
- [x] program_id: btc_obs_2021_2022_campaign
- [x] symbols: BTCUSDT (valid)
- [x] dates: 2021-01-01 to 2022-12-31 (valid)
- [x] timeframe: 5m (supported)
- [x] horizons_bars: [12, 24] (supported)
- [x] templates: [mean_reversion] (valid for VOLATILITY_TRANSITION)
- [x] events: [VOL_SHOCK] (in canonical registry)
- [x] regime: VOLATILITY_EXPANSION (in routing table)
- [x] directions: [short] (valid)
- [x] entry_lags: [1, 2] (all >= 1)
- [x] promotion_profile: disabled (valid)
- [x] search_control: within limits
- [x] no forbidden knobs
- [x] YAML parses cleanly
```

---

## Step 6: Coordinator Executes

The coordinator:
1. Writes the proposal YAML to `spec/proposals/btc_obs_2021_2022_campaign_h1_v1.yaml`
2. Runs the explain command — verifies normalization and search surface
3. Runs preflight and plan — verifies the plan looks correct
4. Presents to the user for approval
5. On approval, runs the execution command
6. After completion, returns to Step 2 with the new run_id

---

## Decision After Hypothetical h1_v1 Run

If the analyst finds mean_reversion still fails cost gate:
- **Kill** the VOL_SHOCK reversion line — the mechanism may be real but is not
  tradable under current cost assumptions

If the analyst finds mean_reversion passes cost gate at 24 bars:
- **Keep** — proceed to RANGE_BREAKOUT hypothesis (h2_v1) from the second
  analyst recommendation
- Record h1_v1 as evidence for the VOLATILITY_EXPANSION regime

If the analyst finds mixed results:
- **Modify** — create h1_v2 with context conditioning (e.g., vol_regime: high)
  to test whether the signal is regime-dependent
