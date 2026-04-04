import pandas as pd
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from project.research.validation.contracts import (
    ValidationBundle,
    ValidatedCandidateRecord,
    ValidationDecision,
    ValidationMetrics,
    PromotionReasonCodes,
)
from project.research.services.evaluation_service import ValidationService
from project.research.services.promotion_service import execute_promotion, PromotionConfig


@pytest.fixture
def mock_data_root(tmp_path):
    data_root = tmp_path / "data"
    data_root.mkdir()
    (data_root / "reports" / "validation").mkdir(parents=True)
    (data_root / "reports" / "promotions").mkdir(parents=True)
    (data_root / "runs" / "test_run").mkdir(parents=True)
    (data_root / "runs" / "test_run" / "run_manifest.json").write_text('{"run_mode": "confirmatory"}')
    return data_root


def test_promotion_rejects_unvalidated_candidates(mock_data_root):
    run_id = "test_run"
    
    # Create a validation bundle with ONLY rejected candidates
    decision = ValidationDecision(
        status="rejected",
        candidate_id="cand_1",
        run_id=run_id,
        reason_codes=["failed_stability"]
    )
    candidate = ValidatedCandidateRecord(
        candidate_id="cand_1",
        decision=decision,
        metrics=ValidationMetrics()
    )
    bundle = ValidationBundle(
        run_id=run_id,
        created_at="2026-01-01",
        rejected_candidates=[candidate]
    )
    
    from project.research.validation.result_writer import write_validation_bundle
    write_validation_bundle(bundle, base_dir=mock_data_root / "reports" / "validation" / run_id)
    
    # Mock candidates table
    (mock_data_root / "reports" / "edge_candidates" / run_id).mkdir(parents=True)
    pd.DataFrame([{"candidate_id": "cand_1"}]).to_parquet(
        mock_data_root / "reports" / "edge_candidates" / run_id / "edge_candidates_normalized.parquet"
    )
    
    config = PromotionConfig(
        run_id=run_id,
        symbols="BTC",
        out_dir=mock_data_root / "reports" / "promotions" / run_id,
        max_q_value=0.05,
        min_events=20,
        min_stability_score=0.5,
        min_sign_consistency=0.5,
        min_cost_survival_ratio=0.5,
        max_negative_control_pass_rate=0.05,
        min_tob_coverage=0.5,
        require_hypothesis_audit=False,
        allow_missing_negative_controls=True,
        require_multiplicity_diagnostics=False,
        min_dsr=0.0,
        max_overlap_ratio=1.0,
        max_profile_correlation=1.0,
        allow_discovery_promotion=True,
        program_id="test_program",
        retail_profile="default",
        objective_name="default",
        objective_spec=None,
        retail_profiles_spec=None
    )
    
    with patch("project.research.services.promotion_service.get_data_root", return_value=mock_data_root):
        with patch("project.research.services.promotion_service.load_run_manifest", return_value={"run_mode": "confirmatory"}):
            with patch("project.research.services.promotion_service.resolve_objective_profile_contract") as mock_contract:
                mock_contract.return_value = MagicMock()
                # execute_promotion should only consider VALIDATED candidates from the bundle
                result = execute_promotion(config)
                # Since cand_1 was rejected in validation, candidates_df will be empty
                assert len(result.promoted_df) == 0


def test_promotion_accepts_validated_candidates(mock_data_root):
    run_id = "test_run"
    
    # Create a validation bundle with a VALIDATED candidate
    decision = ValidationDecision(
        status="validated",
        candidate_id="cand_1",
        run_id=run_id
    )
    candidate = ValidatedCandidateRecord(
        candidate_id="cand_1",
        decision=decision,
        metrics=ValidationMetrics(sample_count=100, expectancy=0.1, q_value=0.01)
    )
    bundle = ValidationBundle(
        run_id=run_id,
        created_at="2026-01-01",
        validated_candidates=[candidate]
    )
    
    from project.research.validation.result_writer import write_validation_bundle
    write_validation_bundle(bundle, base_dir=mock_data_root / "reports" / "validation" / run_id)
    
    # Mock candidates table with all required columns for promote_candidates
    from project.specs.ontology import ontology_spec_hash
    from project import PROJECT_ROOT
    curr_hash = ontology_spec_hash(PROJECT_ROOT.parent)

    (mock_data_root / "reports" / "edge_candidates" / run_id).mkdir(parents=True)
    pd.DataFrame([{
        "candidate_id": "cand_1",
        "event_type": "VOL_SHOCK",
        "rule_template": "tpl1",
        "direction": "long",
        "horizon": 12,
        "n_obs": 100,
        "expectancy": 0.1,
        "q_value": 0.01,
        "p_value": 0.01,
        "stability_score": 0.8,
        "sign_consistency": 0.9,
        "cost_survival_ratio": 0.8,
        "tob_coverage": 0.9,
        "selection_score": 0.8,
        "confirmatory_locked": True,
        "frozen_spec_hash": curr_hash,
    }]).to_parquet(
        mock_data_root / "reports" / "edge_candidates" / run_id / "edge_candidates_normalized.parquet"
    )
    
    config = PromotionConfig(
        run_id=run_id,
        symbols="BTC",
        out_dir=mock_data_root / "reports" / "promotions" / run_id,
        max_q_value=0.05,
        min_events=20,
        min_stability_score=0.5,
        min_sign_consistency=0.5,
        min_cost_survival_ratio=0.5,
        max_negative_control_pass_rate=0.05,
        min_tob_coverage=0.5,
        require_hypothesis_audit=False,
        allow_missing_negative_controls=True,
        require_multiplicity_diagnostics=False,
        min_dsr=0.0,
        max_overlap_ratio=1.0,
        max_profile_correlation=1.0,
        allow_discovery_promotion=True,
        program_id="test_program",
        retail_profile="default",
        objective_name="default",
        objective_spec=None,
        retail_profiles_spec=None
    )
    
    with patch("project.research.services.promotion_service.get_data_root", return_value=mock_data_root):
        with patch("project.research.services.promotion_service.load_run_manifest", return_value={"run_mode": "confirmatory"}):
            with patch("project.research.services.promotion_service.resolve_objective_profile_contract") as mock_contract:
                mock_contract.return_value = MagicMock()
                with patch("project.research.services.promotion_service.promote_candidates") as mock_promote:
                    mock_promote.return_value = (pd.DataFrame([{"candidate_id": "cand_1"}]), pd.DataFrame([{"candidate_id": "cand_1"}]), {})
                    result = execute_promotion(config)
                    assert len(result.promoted_df) == 1


def test_promotion_compatibility_bridge(mock_data_root):
    run_id = "legacy_run"
    
    # Mock candidates table but NO validation bundle
    (mock_data_root / "reports" / "edge_candidates" / run_id).mkdir(parents=True)
    pd.DataFrame([{
        "candidate_id": "cand_1",
        "event_type": "VOL_SHOCK",
        "rule_template": "tpl1",
        "direction": "long",
        "horizon": 12,
        "n_obs": 100,
        "expectancy": 0.1,
        "q_value": 0.01,
        "p_value": 0.01,
        "stability_score": 0.8,
        "sign_consistency": 0.9,
        "cost_survival_ratio": 0.8,
        "tob_coverage": 0.9,
        "selection_score": 0.8,
        "confirmatory_locked": True,
        "frozen_spec_hash": "some_hash",
    }]).to_parquet(
        mock_data_root / "reports" / "edge_candidates" / run_id / "edge_candidates_normalized.parquet"
    )
    
    config = PromotionConfig(
        run_id=run_id,
        symbols="BTC",
        out_dir=mock_data_root / "reports" / "promotions" / run_id,
        max_q_value=0.05,
        min_events=20,
        min_stability_score=0.5,
        min_sign_consistency=0.5,
        min_cost_survival_ratio=0.5,
        max_negative_control_pass_rate=0.05,
        min_tob_coverage=0.5,
        require_hypothesis_audit=False,
        allow_missing_negative_controls=True,
        require_multiplicity_diagnostics=False,
        min_dsr=0.0,
        max_overlap_ratio=1.0,
        max_profile_correlation=1.0,
        allow_discovery_promotion=True,
        program_id="test_program",
        retail_profile="default",
        objective_name="default",
        objective_spec=None,
        retail_profiles_spec=None
    )
    
    with patch("project.research.services.promotion_service.get_data_root", return_value=mock_data_root):
        # Mock load_run_manifest to avoid spec hash check if needed, 
        # but let's just mock resolve_objective_profile_contract
        with patch("project.research.services.promotion_service.load_run_manifest", return_value={"run_mode": "confirmatory"}):
            with patch("project.research.services.promotion_service.resolve_objective_profile_contract") as mock_contract:
                mock_contract.return_value = MagicMock()
                with patch("project.research.services.promotion_service.ontology_spec_hash", return_value="some_hash"):
                    with patch("project.research.services.promotion_service.promote_candidates") as mock_promote:
                        mock_promote.return_value = (pd.DataFrame([{"candidate_id": "cand_1"}]), pd.DataFrame([{"candidate_id": "cand_1"}]), {})
                        
                        # execute_promotion should use the compatibility bridge to create a bundle
                        result = execute_promotion(config)
                        assert len(result.promoted_df) == 1
                        
                        # Verify validation bundle was created in the background
                        from project.research.validation.result_writer import load_validation_bundle
                        val_bundle = load_validation_bundle(run_id, base_dir=mock_data_root / "reports" / "validation" / run_id)
                        assert val_bundle is not None
                        assert val_bundle.summary_stats.get("validation_stage_version") == "compat_legacy_bridge_v1"
