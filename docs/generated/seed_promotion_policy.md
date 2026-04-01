# Seed promotion policy

- schema_version: `seed_promotion_policy_v1`
- lifecycle_classes: `candidate_thesis, tested_thesis, seed_promoted, paper_eligible, production_eligible`
- candidate_statuses: `test_now, needs_repair, needs_more_evidence, reject, ready_for_seed_packaging`

## Minimum requirements
- governed_source_required: `True`
- clear_trigger_definition: `True`
- clear_expected_response: `True`
- bounded_horizon_required: `True`
- explicit_invalidation_required: `True`
- holdout_check_required: `True`
- confounder_sanity_check_required: `True`
- detector_spec_fidelity_required: `True`
- role_and_disposition_compatible: `True`

## Seed promotion usage
- allowed_live_usage: `live_retrieval, overlap_graph, monitor_only_shadow, operator_review`
- blocked_default_usage: `production_sizing, default_live_sizing`
- allowed_deployment_states: `monitor_only, paper_only`
- required_evidence_gaps_field: `True`

## Governance defaults
- blocked_operational_roles: `context, filter, research_only, sequence_component`
- blocked_dispositions: `context_only, research_only, repair_before_promotion, inactive, deprecated, alias_only`
- preferred_seed_event_ids: `VOL_SHOCK, LIQUIDITY_VACUUM, LIQUIDITY_STRESS_DIRECT, BASIS_DISLOC, FND_DISLOC, LIQUIDATION_CASCADE, VOL_SPIKE`
- preferred_seed_episode_ids: `EP_VOLATILITY_BREAKOUT, EP_LIQUIDITY_SHOCK, EP_DISLOCATION_REPAIR`
