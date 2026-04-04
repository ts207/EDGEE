from __future__ import annotations
from pathlib import Path
from project.research.services.promotion_service import execute_promotion, PromotionConfig
from project.research.live_export import export_promoted_theses_for_run as export

def run(
    run_id: str, 
    symbols: str, 
    retail_profile: str = "capital_constrained", 
    out_dir: Path | None = None,
    use_compatibility_bridge: bool = False
):
    config = PromotionConfig(
        run_id=run_id,
        symbols=symbols,
        out_dir=out_dir,
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
        program_id="",
        retail_profile=retail_profile,
        objective_name="",
        objective_spec=None,
        retail_profiles_spec=None,
        use_compatibility_bridge=use_compatibility_bridge
    )
    return execute_promotion(config)
