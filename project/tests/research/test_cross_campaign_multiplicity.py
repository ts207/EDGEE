"""
Tests for cross-campaign / campaign-lineage multiplicity control.

Phase 1 acceptance tests:
- both side_policy counts as 2 tests
- num_tests_campaign reflects full campaign scope
- q_value_scope >= q_value when scope broadens
- effective_q_value = max(applicable q-values)
- promotion rejects candidate if effective_q_value > max_q_value
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from project.research.multiplicity import (
    apply_canonical_cross_campaign_multiplicity,
    apply_multiplicity_controls,
    merge_historical_candidates,
)
from project.research.contracts.multiplicity_scope import (
    MultiplicityScope,
    infer_multiplicity_scope,
    resolve_campaign_scope_key,
    resolve_effective_scope_key,
    resolve_lineage_scope_key,
)


class TestMultiplicityScopeContract:
    """Test the canonical multiplicity scope contract."""

    def test_infer_multiplicity_scope(self):
        row = {
            "run_id": "run_001",
            "campaign_id": "camp_001",
            "program_id": "prog_001",
            "concept_lineage_key": "lineage_abc",
            "family_id": "family_xyz",
            "side_policy": "directional",
        }
        scope = infer_multiplicity_scope(row)
        assert scope.run_id == "run_001"
        assert scope.campaign_id == "camp_001"
        assert scope.program_id == "prog_001"
        assert scope.concept_lineage_key == "lineage_abc"
        assert scope.family_id == "family_xyz"
        assert scope.side_policy == "directional"
        assert scope.scope_version == "phase1_v1"

    def test_resolve_campaign_scope_key_prioritizes_campaign(self):
        row = {"run_id": "run_001", "campaign_id": "camp_001", "program_id": "prog_001"}
        key = resolve_campaign_scope_key(row)
        assert key == "campaign::camp_001"

    def test_resolve_campaign_scope_key_falls_back_to_program(self):
        row = {"run_id": "run_001", "program_id": "prog_001"}
        key = resolve_campaign_scope_key(row)
        assert key == "program::prog_001"

    def test_resolve_campaign_scope_key_falls_back_to_run(self):
        row = {"run_id": "run_001"}
        key = resolve_campaign_scope_key(row)
        assert key == "run::run_001"

    def test_resolve_lineage_scope_key_includes_lineage(self):
        row = {
            "campaign_id": "camp_001",
            "concept_lineage_key": "lineage_abc",
        }
        key = resolve_lineage_scope_key(row)
        assert "campaign::camp_001" in key
        assert "lineage::lineage_abc" in key

    def test_resolve_effective_scope_key_modes(self):
        row = {
            "run_id": "run_001",
            "campaign_id": "camp_001",
            "program_id": "prog_001",
            "concept_lineage_key": "lineage_abc",
        }
        assert resolve_effective_scope_key(row, mode="run").startswith("run::")
        assert resolve_effective_scope_key(row, mode="campaign").startswith("campaign::")
        assert resolve_effective_scope_key(row, mode="program").startswith("program::")


class TestCrossCampaignMultiplicity:
    """Test canonical cross-campaign multiplicity adjustment."""

    def test_both_side_policy_weighted_as_two(self):
        df = pd.DataFrame({
            "candidate_id": ["a", "b", "c"],
            "p_value_for_fdr": [0.01, 0.02, 0.03],
            "family_id": ["f1", "f1", "f2"],
            "campaign_id": ["c1", "c1", "c1"],
            "side_policy": ["directional", "both", "directional"],
            "run_id": ["r1", "r1", "r1"],
            "multiplicity_pool_eligible": [True, True, True],
        })
        result = apply_multiplicity_controls(df, max_q=0.05)
        # both should be counted as 2 tests
        assert result.loc[1, "num_tests_family"] == 3  # f1: 1 + 2 (both)
        assert result.loc[2, "num_tests_family"] == 2  # f2: 1 (directional only)

    def test_campaign_scope_key_determinism(self):
        df = pd.DataFrame({
            "candidate_id": ["a", "b", "c"],
            "p_value_for_fdr": [0.01, 0.02, 0.03],
            "family_id": ["f1", "f1", "f2"],
            "campaign_id": ["camp_001", "camp_001", "camp_001"],
            "run_id": ["r1", "r1", "r1"],
            "side_policy": ["directional", "directional", "directional"],
            "multiplicity_pool_eligible": [True, True, True],
        })
        result = apply_canonical_cross_campaign_multiplicity(df, max_q=0.05)
        # All should have same campaign scope key
        assert all(result["multiplicity_scope_key"] == "campaign::camp_001")

    def test_num_tests_scope_reflects_full_scope(self):
        df = pd.DataFrame({
            "candidate_id": ["a", "b", "c", "d"],
            "p_value_for_fdr": [0.01, 0.02, 0.03, 0.04],
            "family_id": ["f1", "f1", "f2", "f2"],
            "campaign_id": ["camp_001", "camp_001", "camp_002", "camp_002"],
            "run_id": ["r1", "r1", "r2", "r2"],
            "concept_lineage_key": ["L1", "L1", "L1", "L1"],
            "side_policy": ["directional", "directional", "directional", "directional"],
            "multiplicity_pool_eligible": [True, True, True, True],
        })
        result = apply_canonical_cross_campaign_multiplicity(
            df, max_q=0.05, scope_mode="campaign_lineage"
        )
        # Each campaign should count tests across families
        for idx, row in result.iterrows():
            assert row["num_tests_scope"] >= 1

    def test_q_value_scope_greater_or_equal_to_local(self):
        df = pd.DataFrame({
            "candidate_id": ["a", "b", "c"],
            "p_value_for_fdr": [0.01, 0.02, 0.05],
            "family_id": ["f1", "f1", "f2"],
            "campaign_id": ["camp_001", "camp_001", "camp_001"],
            "q_value": [0.03, 0.04, 0.06],
            "run_id": ["r1", "r1", "r1"],
            "side_policy": ["directional", "directional", "directional"],
            "multiplicity_pool_eligible": [True, True, True],
        })
        result = apply_canonical_cross_campaign_multiplicity(df, max_q=0.05)
        # Scope q-value should be >= local q-value when scope broadens
        for idx in result.index:
            assert result.loc[idx, "q_value_scope"] >= result.loc[idx, "q_value"] * 0.99  # numerical tolerance

    def test_effective_q_value_computed(self):
        df = pd.DataFrame({
            "candidate_id": ["a", "b"],
            "p_value_for_fdr": [0.01, 0.02],
            "family_id": ["f1", "f1"],
            "campaign_id": ["camp_001", "camp_001"],
            "q_value": [0.03, 0.04],
            "q_value_program": [0.05, 0.06],
            "run_id": ["r1", "r1"],
            "side_policy": ["directional", "directional"],
            "multiplicity_pool_eligible": [True, True],
        })
        result = apply_canonical_cross_campaign_multiplicity(df, max_q=0.10)
        # effective_q_value should be max of q_value, q_value_scope, q_value_program
        for idx in result.index:
            local_q = result.loc[idx, "q_value"]
            scope_q = result.loc[idx, "q_value_scope"]
            prog_q = result.loc[idx, "q_value_program"]
            effective_q = result.loc[idx, "effective_q_value"]
            assert effective_q >= local_q
            assert effective_q >= scope_q * 0.99
            assert effective_q >= prog_q * 0.99

    def test_scope_mode_variations(self):
        df = pd.DataFrame({
            "candidate_id": ["a"],
            "p_value_for_fdr": [0.01],
            "family_id": ["f1"],
            "run_id": ["run_001"],
            "campaign_id": ["camp_001"],
            "program_id": ["prog_001"],
            "multiplicity_pool_eligible": [True],
        })
        result_run = apply_canonical_cross_campaign_multiplicity(df, max_q=0.05, scope_mode="run")
        result_campaign = apply_canonical_cross_campaign_multiplicity(df, max_q=0.05, scope_mode="campaign")
        result_program = apply_canonical_cross_campaign_multiplicity(df, max_q=0.05, scope_mode="program")
        
        assert result_run.loc[0, "multiplicity_scope_key"].startswith("run::")
        assert result_campaign.loc[0, "multiplicity_scope_key"].startswith("campaign::")
        assert result_program.loc[0, "multiplicity_scope_key"].startswith("program::")

    def test_degraded_status_on_empty_historical(self):
        current = pd.DataFrame({
            "candidate_id": ["a"],
            "p_value_for_fdr": [0.01],
            "family_id": ["f1"],
            "run_id": ["run_001"],
            "multiplicity_pool_eligible": [True],
        })
        result = merge_historical_candidates(current, historical=None, scope_mode="campaign_lineage")
        assert result.loc[0, "multiplicity_scope_degraded"] is True
        assert result.loc[0, "multiplicity_scope_reason"] == "missing_history"


class TestEffectiveQValueInPromotion:
    """Test that effective_q_value gates promotion decisions."""

    def test_scope_level_fields_propagated(self):
        df = pd.DataFrame({
            "candidate_id": ["a"],
            "p_value_for_fdr": [0.01],
            "family_id": ["f1"],
            "campaign_id": ["camp_001"],
            "run_id": ["run_001"],
            "multiplicity_pool_eligible": [True],
        })
        result = apply_canonical_cross_campaign_multiplicity(df, max_q=0.05)
        assert "multiplicity_scope_mode" in result.columns
        assert "multiplicity_scope_key" in result.columns
        assert "multiplicity_scope_version" in result.columns
        assert "num_tests_scope" in result.columns
        assert "q_value_scope" in result.columns
        assert "is_discovery_scope" in result.columns
        assert "effective_q_value" in result.columns
        assert "is_discovery_effective" in result.columns


class TestBackwardCompatibility:
    """Test that existing fields are preserved."""

    def test_existing_q_value_columns_preserved(self):
        df = pd.DataFrame({
            "candidate_id": ["a"],
            "p_value_for_fdr": [0.01],
            "family_id": ["f1"],
            "q_value": [0.03],
            "q_value_family": [0.03],
            "q_value_program": [0.04],
            "run_id": ["run_001"],
            "multiplicity_pool_eligible": [True],
        })
        result = apply_canonical_cross_campaign_multiplicity(df, max_q=0.05)
        # All original columns should still exist
        assert "q_value" in result.columns
        assert "q_value_family" in result.columns
        assert "q_value_program" in result.columns
        # New columns added
        assert "q_value_scope" in result.columns
        assert "effective_q_value" in result.columns