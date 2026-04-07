import json
import shutil
from pathlib import Path
from project.research.validation.contracts import (
    ValidationBundle,
    ValidatedCandidateRecord,
    ValidationDecision,
    ValidationMetrics,
)
from project.research.validation.result_writer import (
    write_validation_bundle,
    load_validation_bundle,
)

def test_round_trip():
    print("Testing round-trip...")
    run_id = "test_run_round_trip"
    base_dir = Path("tmp/test_validation") / run_id
    if base_dir.exists():
        shutil.rmtree(base_dir)
    
    bundle = ValidationBundle(
        run_id=run_id,
        created_at="2026-04-07T12:00:00",
        effect_stability_report={"metric_a": 0.95},
        summary_stats={"total": 1}
    )
    
    write_validation_bundle(bundle, base_dir=base_dir)
    
    loaded = load_validation_bundle(run_id, base_dir=base_dir)
    
    assert loaded is not None
    assert loaded.effect_stability_report == bundle.effect_stability_report
    assert loaded.to_dict() == bundle.to_dict()
    print("Round-trip SUCCESS")

def test_backward_compat():
    print("Testing backward-compat...")
    run_id = "test_run_compat"
    base_dir = Path("tmp/test_validation") / run_id
    if base_dir.exists():
        shutil.rmtree(base_dir)
    base_dir.mkdir(parents=True)
    
    # 1. validation_bundle.json lacks the field
    bundle_data = {
        "run_id": run_id,
        "created_at": "2026-04-07T12:00:00",
        "validated_candidates": [],
        "rejected_candidates": [],
        "inconclusive_candidates": [],
        "summary_stats": {}
    }
    with (base_dir / "validation_bundle.json").open("w") as f:
        json.dump(bundle_data, f)
        
    # 2. effect_stability_report.json exists
    stability_data = {"legacy_metric": 0.88}
    with (base_dir / "effect_stability_report.json").open("w") as f:
        json.dump(stability_data, f)
        
    loaded = load_validation_bundle(run_id, base_dir=base_dir)
    
    assert loaded is not None
    assert loaded.effect_stability_report == stability_data
    print("Backward-compat SUCCESS")

if __name__ == "__main__":
    try:
        test_round_trip()
        test_backward_compat()
    except Exception as e:
        print(f"Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
