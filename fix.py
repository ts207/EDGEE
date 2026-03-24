import sys

path = r"c:\Users\tuvsh\Downloads\Edge\Edge\spec\states\state_registry.yaml"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

# Priority 1
text = text.replace(
"""- state_id: POST_ABSORPTION_STATE
  family: LIQUIDITY_DISLOCATION
  source_event_type: ABSORPTION_EVENT""",
"""- state_id: POST_ABSORPTION_STATE
  family: LIQUIDITY_DISLOCATION
  source_event_type: ABSORPTION_PROXY"""
)

text = text.replace(
"""- state_id: MS_FUNDING_STATE
  family: MICROSTRUCTURE_CONTEXT
  source_event_type: FUNDING_RATE_EXTREME""",
"""- state_id: MS_FUNDING_STATE
  family: MICROSTRUCTURE_CONTEXT
  source_event_type: FUNDING_EXTREME_ONSET"""
)

text = text.replace(
"""- state_id: MS_OI_STATE
  family: MICROSTRUCTURE_CONTEXT
  source_event_type: OI_SURGE""",
"""- state_id: MS_OI_STATE
  family: MICROSTRUCTURE_CONTEXT
  source_event_type: OI_SPIKE_POSITIVE"""
)

text = text.replace(
"""  allowed_templates:
  - continuation
  - reversal
  - breakout""",
"""  allowed_templates:
  - continuation"""
)

# Priority 2 & 3: Append new states
new_states = """
- state_id: FEE_REGIME_STATE
  family: EXECUTION_FRICTION
  source_event_type: FEE_REGIME_CHANGE_EVENT
  activation_rule: fee regime transition detected
  decay_rule: fee regime normalizes
  features_required:
  - fee_bps
  allowed_templates:
  - tail_risk_avoid
  - slippage_aware_filter

- state_id: OI_CONTRACTION_STATE
  family: POSITIONING_EXTREMES
  source_event_type: OI_SPIKE_NEGATIVE
  activation_rule: oi contraction detected
  decay_rule: oi normalizes
  features_required:
  - oi_notional
  - rv_96
  allowed_templates:
  - momentum_fade
  - mean_reversion

- state_id: POST_CASCADE_RECOVERY_STATE
  family: POSITIONING_EXTREMES
  source_event_type: LIQUIDATION_EXHAUSTION_REVERSAL
  activation_rule: post cascade recovery detected
  decay_rule: recovery normalizes
  features_required:
  - liquidation_notional
  - spread_bps
  allowed_templates:
  - mean_reversion
  - continuation

- state_id: FUNDING_FLIP_STATE
  family: POSITIONING_EXTREMES
  source_event_type: FUNDING_FLIP
  activation_rule: funding rate sign flip
  decay_rule: funding persistence achieved
  features_required:
  - funding_rate_scaled
  allowed_templates:
  - reversal_or_squeeze
  - trend_continuation

- state_id: BETA_SPIKE_STATE
  family: REGIME_TRANSITION
  source_event_type: BETA_SPIKE_EVENT
  activation_rule: beta spike detected
  decay_rule: beta normalizes
  features_required:
  - beta
  allowed_templates:
  - only_if_regime
  - tail_risk_avoid
"""

if "state_id: FEE_REGIME_STATE" not in text:
    text += new_states

with open(path, "w", encoding="utf-8") as f:
    f.write(text)
print("done")
