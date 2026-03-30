from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from project.core.exceptions import DataIntegrityError
from project.research.live_export import export_promoted_theses_for_run


def _bundle() -> dict:
    return {
        "candidate_id": "cand_1",
        "event_family": "VOL_SHOCK",
        "event_type": "VOL_SHOCK",
        "run_id": "run_1",
        "sample_definition": {
            "n_events": 120,
            "validation_samples": 60,
            "test_samples": 60,
            "symbol": "BTCUSDT",
        },
        "split_definition": {
            "split_scheme_id": "confirmatory",
            "purge_bars": 1,
            "embargo_bars": 1,
            "bar_duration_minutes": 5,
        },
        "effect_estimates": {"estimate": 0.12, "estimate_bps": 12.0},
        "uncertainty_estimates": {"q_value": 0.01},
        "stability_tests": {"stability_score": 0.9},
        "falsification_results": {"passes_control": True},
        "cost_robustness": {
            "cost_survival_ratio": 1.0,
            "net_expectancy_bps": 9.0,
            "tob_coverage": 0.95,
            "retail_net_expectancy_pass": True,
        },
        "multiplicity_adjustment": {"q_value_program": 0.01},
        "metadata": {
            "hypothesis_id": "hyp_1",
            "plan_row_id": "plan_1",
            "has_realized_oos_path": True,
        },
        "promotion_decision": {
            "promotion_status": "promoted",
            "promotion_track": "deploy",
            "rank_score": 1.0,
        },
        "policy_version": "v1",
        "bundle_version": "b1",
    }


def test_export_promoted_theses_pending_then_active_with_blueprint(tmp_path: Path) -> None:
    promoted_df = pd.DataFrame(
        [
            {
                "candidate_id": "cand_1",
                "event_type": "VOL_SHOCK",
                "status": "PROMOTED",
                "canonical_regime": "VOLATILITY",
                "routing_profile_id": "routing_v1",
            }
        ]
    )

    first = export_promoted_theses_for_run(
        "run_1",
        data_root=tmp_path,
        bundles=[_bundle()],
        promoted_df=promoted_df,
    )
    payload = json.loads(first.output_path.read_text(encoding="utf-8"))
    assert first.thesis_count == 1
    assert first.pending_count == 1
    assert payload["theses"][0]["status"] == "pending_blueprint"
    assert payload["theses"][0]["invalidation"] == {}

    second = export_promoted_theses_for_run(
        "run_1",
        data_root=tmp_path,
        bundles=[_bundle()],
        promoted_df=promoted_df,
        blueprints=[
            {
                "id": "bp_1",
                "candidate_id": "cand_1",
                "direction": "long",
                "symbol_scope": {
                    "mode": "single_symbol",
                    "symbols": ["BTCUSDT"],
                    "candidate_symbol": "BTCUSDT",
                },
                "exit": {
                    "time_stop_bars": 8,
                    "stop_type": "range_pct",
                    "stop_value": 0.02,
                    "target_type": "range_pct",
                    "target_value": 0.03,
                    "invalidation": {
                        "metric": "adverse_proxy",
                        "operator": ">",
                        "value": 0.02,
                    },
                },
                "lineage": {"proposal_id": "proposal_1"},
            }
        ],
    )

    updated = json.loads(second.output_path.read_text(encoding="utf-8"))
    thesis = updated["theses"][0]
    assert second.active_count == 1
    assert thesis["status"] == "active"
    assert thesis["lineage"]["blueprint_id"] == "bp_1"
    assert thesis["invalidation"]["metric"] == "adverse_proxy"


def test_export_promoted_theses_fails_on_corrupted_existing_index(tmp_path: Path) -> None:
    promoted_df = pd.DataFrame(
        [
            {
                "candidate_id": "cand_1",
                "event_type": "VOL_SHOCK",
                "status": "PROMOTED",
            }
        ]
    )
    index_path = tmp_path / "live" / "theses" / "index.json"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text("{not-json", encoding="utf-8")

    with pytest.raises(DataIntegrityError):
        export_promoted_theses_for_run(
            "run_1",
            data_root=tmp_path,
            bundles=[_bundle()],
            promoted_df=promoted_df,
        )
