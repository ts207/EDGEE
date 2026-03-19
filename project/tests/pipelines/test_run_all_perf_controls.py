from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace

from project import PROJECT_ROOT

import project.pipelines.run_all as run_all
import project.pipelines.pipeline_planning as pipeline_planning
from project.pipelines.stages.evaluation import build_evaluation_stages


def _load_manifest(tmp_path: Path, run_id: str) -> dict:
    path = tmp_path / "data" / "runs" / run_id / "run_manifest.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_run_all_performance_mode_sets_manifest_fields(monkeypatch, tmp_path):
    captured: list[str] = []

    def fake_run_stage(stage, script, base_args, run_id, **kwargs) -> bool:
        captured.append(stage)
        return False

    monkeypatch.setattr(run_all, "DATA_ROOT", tmp_path / "data")
    monkeypatch.setattr(run_all, "_git_commit", lambda _project_root: "test-sha")
    monkeypatch.setattr(run_all, "_run_stage", fake_run_stage)
    monkeypatch.delenv("BACKTEST_STAGE_CACHE", raising=False)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_all.py",
            "--run_id",
            "perf_mode_run",
            "--symbols",
            "BTCUSDT",
            "--start",
            "2024-01-01",
            "--end",
            "2024-01-02",
            "--performance_mode",
            "1",
        ],
    )

    rc = run_all.main()
    assert rc == 1
    assert captured
    manifest = _load_manifest(tmp_path, "perf_mode_run")
    assert manifest["performance_mode"] is True
    assert manifest["stage_cache_enabled_global"] is True
    assert int(manifest["phase2_parallel_workers"]) >= 1
    assert manifest["objective_name"] == "retail_profitability"
    assert manifest["objective_id"] == "retail_profitability"
    assert isinstance(manifest["objective_spec_hash"], str) and manifest["objective_spec_hash"]
    assert int(manifest["objective_hard_gates"]["min_trade_count"]) == 150
    assert manifest["retail_profile_name"] == "capital_constrained"
    assert (
        isinstance(manifest["retail_profile_spec_hash"], str)
        and manifest["retail_profile_spec_hash"]
    )
    assert float(manifest["retail_profile_config"]["max_leverage"]) == 3.0
    assert manifest["runtime_invariants_mode"] == "off"
    assert manifest["runtime_invariants_status"] == "disabled"
    assert manifest["emit_run_hash"] is False
    assert manifest["run_hash_status"] == "disabled"
    assert manifest["effective_config_schema_version"] == "effective_run_config_v1"
    assert str(manifest["effective_config_path"]).endswith("/effective_config.json")
    assert str(manifest["effective_config_hash"]).startswith("sha256:")
    effective_config = json.loads(
        Path(manifest["effective_config_path"]).read_text(encoding="utf-8")
    )
    assert effective_config["run_id"] == "perf_mode_run"
    assert effective_config["config_resolution"]["normalized_symbols"] == ["BTCUSDT"]


def test_run_all_disables_expectancy_chain_when_checklist_dependency_is_missing(
    monkeypatch, tmp_path
):
    captured: list[str] = []

    def fake_run_stage(stage, script, base_args, run_id, **kwargs) -> bool:
        captured.append(stage)
        return False

    monkeypatch.setattr(run_all, "DATA_ROOT", tmp_path / "data")
    monkeypatch.setattr(run_all, "_git_commit", lambda _project_root: "test-sha")
    monkeypatch.setattr(run_all, "_run_stage", fake_run_stage)
    real_exists = Path.exists

    def fake_exists(path: Path) -> bool:
        if str(path).endswith("project/pipelines/research/analyze_conditional_expectancy.py"):
            return False
        return real_exists(path)

    monkeypatch.setattr(pipeline_planning.Path, "exists", fake_exists)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_all.py",
            "--run_id",
            "checklist_expectancy_auto",
            "--symbols",
            "BTCUSDT",
            "--start",
            "2024-01-01",
            "--end",
            "2024-01-02",
            "--run_phase2_conditional",
            "0",
            "--run_candidate_promotion",
            "0",
            "--run_edge_registry_update",
            "0",
            "--run_strategy_blueprint_compiler",
            "0",
            "--run_strategy_builder",
            "0",
            "--run_profitable_selector",
            "0",
            "--run_interaction_lift",
            "0",
            "--run_recommendations_checklist",
            "1",
        ],
    )

    rc = run_all.main()
    assert rc == 1
    manifest = _load_manifest(tmp_path, "checklist_expectancy_auto")
    planned = manifest.get("planned_stages", [])
    assert "analyze_conditional_expectancy" not in planned
    assert "validate_expectancy_traps" not in planned
    assert "generate_recommendations_checklist" not in planned


def test_run_all_production_auto_enables_phase2_when_not_explicit(monkeypatch, tmp_path):
    captured: list[str] = []

    def fake_run_stage(stage, script, base_args, run_id, **kwargs) -> bool:
        captured.append(stage)
        return False

    monkeypatch.setattr(run_all, "DATA_ROOT", tmp_path / "data")
    monkeypatch.setattr(run_all, "_git_commit", lambda _project_root: "test-sha")
    monkeypatch.setattr(run_all, "_run_stage", fake_run_stage)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_all.py",
            "--run_id",
            "prod_auto_phase2",
            "--symbols",
            "BTCUSDT",
            "--start",
            "2024-01-01",
            "--end",
            "2024-01-02",
            "--mode",
            "production",
            "--run_recommendations_checklist",
            "0",
            "--run_expectancy_analysis",
            "0",
            "--run_expectancy_robustness",
            "0",
        ],
    )

    rc = run_all.main()
    assert rc == 1
    assert captured
    manifest = _load_manifest(tmp_path, "prod_auto_phase2")
    planned = manifest.get("planned_stages", [])
    assert "phase2_search_engine" in planned
    assert "promote_candidates" in planned


def test_run_all_auto_promotion_q_matches_phase2_profile(monkeypatch, tmp_path):
    promote_args: dict[str, list[str]] = {}

    def fake_run_stage(stage, script, base_args, run_id, **kwargs) -> bool:
        if stage == "promote_candidates":
            promote_args["base_args"] = list(base_args)
            return False
        return True

    monkeypatch.setattr(run_all, "DATA_ROOT", tmp_path / "data")
    monkeypatch.setattr(run_all, "_git_commit", lambda _project_root: "test-sha")
    monkeypatch.setattr(run_all, "_run_stage", fake_run_stage)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_all.py",
            "--run_id",
            "promo_q_auto",
            "--symbols",
            "BTCUSDT",
            "--start",
            "2024-01-01",
            "--end",
            "2024-01-02",
            "--skip_ingest_ohlcv",
            "1",
            "--skip_ingest_funding",
            "1",
            "--skip_ingest_spot_ohlcv",
            "1",
            "--run_phase2_conditional",
            "1",
            "--phase2_event_type",
            "LIQUIDITY_VACUUM",
            "--run_bridge_eval_phase2",
            "0",
            "--run_naive_entry_eval",
            "0",
            "--run_edge_registry_update",
            "0",
            "--run_edge_candidate_universe",
            "0",
            "--run_strategy_blueprint_compiler",
            "0",
            "--run_strategy_builder",
            "0",
            "--run_profitable_selector",
            "0",
            "--run_expectancy_analysis",
            "0",
            "--run_expectancy_robustness",
            "0",
            "--run_recommendations_checklist",
            "0",
            "--run_interaction_lift",
            "0",
        ],
    )

    rc = run_all.main()
    assert rc == 1
    args = promote_args.get("base_args", [])
    assert "--promotion_profile" in args
    profile_idx = args.index("--promotion_profile")
    assert args[profile_idx + 1] == "research"
    assert "--max_q_value" in args
    idx = args.index("--max_q_value")
    assert float(args[idx + 1]) == 0.15
    assert int(args[args.index("--min_events") + 1]) == 50
    assert float(args[args.index("--min_stability_score") + 1]) == 0.50
    assert float(args[args.index("--min_sign_consistency") + 1]) == 0.55
    assert float(args[args.index("--min_cost_survival_ratio") + 1]) == 0.50
    assert float(args[args.index("--min_tob_coverage") + 1]) == 0.50
    assert float(args[args.index("--max_negative_control_pass_rate") + 1]) == 0.10


def test_run_all_explicit_promotion_q_with_equals_syntax_is_respected(monkeypatch, tmp_path):
    promote_args: dict[str, list[str]] = {}

    def fake_run_stage(stage, script, base_args, run_id, **kwargs) -> bool:
        if stage == "promote_candidates":
            promote_args["base_args"] = list(base_args)
            return False
        return True

    monkeypatch.setattr(run_all, "DATA_ROOT", tmp_path / "data")
    monkeypatch.setattr(run_all, "_git_commit", lambda _project_root: "test-sha")
    monkeypatch.setattr(run_all, "_run_stage", fake_run_stage)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_all.py",
            "--run_id",
            "promo_q_explicit_equals",
            "--symbols",
            "BTCUSDT",
            "--start",
            "2024-01-01",
            "--end",
            "2024-01-02",
            "--skip_ingest_ohlcv",
            "1",
            "--skip_ingest_funding",
            "1",
            "--skip_ingest_spot_ohlcv",
            "1",
            "--run_phase2_conditional",
            "1",
            "--phase2_event_type",
            "LIQUIDITY_VACUUM",
            "--run_bridge_eval_phase2",
            "0",
            "--run_naive_entry_eval",
            "0",
            "--run_edge_registry_update",
            "0",
            "--run_edge_candidate_universe",
            "0",
            "--run_strategy_blueprint_compiler",
            "0",
            "--run_strategy_builder",
            "0",
            "--run_profitable_selector",
            "0",
            "--run_expectancy_analysis",
            "0",
            "--run_expectancy_robustness",
            "0",
            "--run_recommendations_checklist",
            "0",
            "--run_interaction_lift",
            "0",
            "--candidate_promotion_max_q_value=0.12",
        ],
    )

    rc = run_all.main()
    assert rc == 1
    args = promote_args.get("base_args", [])
    assert "--max_q_value" in args
    idx = args.index("--max_q_value")
    assert float(args[idx + 1]) == 0.12


def test_run_all_threads_candidate_promotion_profile_into_stage_args(monkeypatch, tmp_path):
    promote_args: dict[str, list[str]] = {}

    def fake_run_stage(stage, script, base_args, run_id, **kwargs) -> bool:
        if stage == "promote_candidates":
            promote_args["base_args"] = list(base_args)
            return False
        return True

    monkeypatch.setattr(run_all, "DATA_ROOT", tmp_path / "data")
    monkeypatch.setattr(run_all, "_git_commit", lambda _project_root: "test-sha")
    monkeypatch.setattr(run_all, "_run_stage", fake_run_stage)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_all.py",
            "--run_id",
            "promo_profile_wiring",
            "--symbols",
            "BTCUSDT",
            "--start",
            "2024-01-01",
            "--end",
            "2024-01-02",
            "--skip_ingest_ohlcv",
            "1",
            "--skip_ingest_funding",
            "1",
            "--skip_ingest_spot_ohlcv",
            "1",
            "--run_phase2_conditional",
            "1",
            "--run_bridge_eval_phase2",
            "0",
            "--run_naive_entry_eval",
            "0",
            "--run_edge_registry_update",
            "0",
            "--run_edge_candidate_universe",
            "0",
            "--run_strategy_blueprint_compiler",
            "0",
            "--run_strategy_builder",
            "0",
            "--run_profitable_selector",
            "0",
            "--run_expectancy_analysis",
            "0",
            "--run_expectancy_robustness",
            "0",
            "--run_recommendations_checklist",
            "0",
            "--run_interaction_lift",
            "0",
            "--candidate_promotion_profile",
            "research",
        ],
    )

    rc = run_all.main()
    assert rc == 1
    args = promote_args.get("base_args", [])
    assert "--promotion_profile" in args
    idx = args.index("--promotion_profile")
    assert args[idx + 1] == "research"


def test_run_all_production_auto_uses_deploy_promotion_defaults(monkeypatch, tmp_path):
    promote_args: dict[str, list[str]] = {}

    def fake_run_stage(stage, script, base_args, run_id, **kwargs) -> bool:
        if stage == "promote_candidates":
            promote_args["base_args"] = list(base_args)
            return False
        return True

    monkeypatch.setattr(run_all, "DATA_ROOT", tmp_path / "data")
    monkeypatch.setattr(run_all, "_git_commit", lambda _project_root: "test-sha")
    monkeypatch.setattr(run_all, "_run_stage", fake_run_stage)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_all.py",
            "--run_id",
            "promo_profile_auto_deploy",
            "--symbols",
            "BTCUSDT",
            "--start",
            "2024-01-01",
            "--end",
            "2024-01-02",
            "--mode",
            "production",
            "--skip_ingest_ohlcv",
            "1",
            "--skip_ingest_funding",
            "1",
            "--skip_ingest_spot_ohlcv",
            "1",
            "--run_phase2_conditional",
            "1",
            "--run_bridge_eval_phase2",
            "0",
            "--run_naive_entry_eval",
            "0",
            "--run_edge_registry_update",
            "0",
            "--run_edge_candidate_universe",
            "0",
            "--run_strategy_blueprint_compiler",
            "0",
            "--run_strategy_builder",
            "0",
            "--run_profitable_selector",
            "0",
            "--run_expectancy_analysis",
            "0",
            "--run_expectancy_robustness",
            "0",
            "--run_recommendations_checklist",
            "0",
            "--run_interaction_lift",
            "0",
        ],
    )

    rc = run_all.main()
    assert rc == 1
    args = promote_args.get("base_args", [])
    assert args[args.index("--promotion_profile") + 1] == "deploy"
    assert float(args[args.index("--max_q_value") + 1]) == 0.10
    assert int(args[args.index("--min_events") + 1]) == 100
    assert float(args[args.index("--min_stability_score") + 1]) == 0.60
    assert float(args[args.index("--min_sign_consistency") + 1]) == 0.67
    assert float(args[args.index("--min_cost_survival_ratio") + 1]) == 0.75
    assert float(args[args.index("--min_tob_coverage") + 1]) == 0.60
    assert float(args[args.index("--max_negative_control_pass_rate") + 1]) == 0.01


def test_run_all_program_scoped_run_wires_update_campaign_memory(monkeypatch, tmp_path):
    captured: dict[str, list[str]] = {}

    def fake_run_stage(stage, script, base_args, run_id, **kwargs) -> bool:
        captured[stage] = list(base_args)
        return stage != "update_campaign_memory"

    monkeypatch.setattr(run_all, "DATA_ROOT", tmp_path / "data")
    monkeypatch.setattr(run_all, "_git_commit", lambda _project_root: "test-sha")
    monkeypatch.setattr(run_all, "_run_stage", fake_run_stage)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_all.py",
            "--run_id",
            "campaign_memory_wiring",
            "--symbols",
            "BTCUSDT",
            "--start",
            "2024-01-01",
            "--end",
            "2024-01-02",
            "--skip_ingest_ohlcv",
            "1",
            "--skip_ingest_funding",
            "1",
            "--skip_ingest_spot_ohlcv",
            "1",
            "--run_phase2_conditional",
            "1",
            "--run_bridge_eval_phase2",
            "0",
            "--run_naive_entry_eval",
            "0",
            "--run_candidate_promotion",
            "0",
            "--run_edge_registry_update",
            "0",
            "--run_expectancy_analysis",
            "0",
            "--run_expectancy_robustness",
            "0",
            "--run_recommendations_checklist",
            "0",
            "--run_interaction_lift",
            "0",
            "--program_id",
            "btc_campaign",
        ],
    )

    rc = run_all.main()
    assert rc == 1
    assert "export_edge_candidates" in captured
    assert "update_campaign_memory" in captured
    args = captured["update_campaign_memory"]
    assert args[args.index("--data_root") + 1] == str(tmp_path / "data")
    assert args[args.index("--registry_root") + 1] == "project/configs/registries"
    assert "--promising_top_k" in args
    assert args[args.index("--promising_top_k") + 1] == "5"
    assert args[args.index("--frontier_untested_top_k") + 1] == "3"


def test_run_all_wires_strategy_builder_fractional_allocation_flag(monkeypatch, tmp_path):
    args = SimpleNamespace(
        experiment_config=None,
        run_strategy_blueprint_compiler=0,
        run_strategy_builder=1,
        strategy_builder_top_k_per_event=2,
        strategy_builder_max_candidates=20,
        strategy_builder_include_alpha_bundle=1,
        strategy_builder_ignore_checklist=0,
        strategy_builder_allow_non_promoted=0,
        strategy_builder_allow_missing_candidate_detail=0,
        strategy_builder_enable_fractional_allocation=0,
        run_profitable_selector=1,
    )

    stages = build_evaluation_stages(
        args=args,
        run_id="strategy_builder_fractional_wiring",
        symbols="BTCUSDT",
        start="2024-01-01",
        end="2024-01-02",
        force_flag="0",
        project_root=PROJECT_ROOT,
        data_root=tmp_path / "data",
    )

    strategy_stage = next(stage for stage in stages if stage[0] == "build_strategy_candidates")
    args = strategy_stage[2]
    assert "--blueprints_file" in args
    assert args[args.index("--blueprints_file") + 1].endswith(
        "/reports/strategy_blueprints/strategy_builder_fractional_wiring/blueprints.jsonl"
    )
    assert "--enable_fractional_allocation" in args
    assert args[args.index("--enable_fractional_allocation") + 1] == "0"
    profitable_stage = next(stage for stage in stages if stage[0] == "select_profitable_strategies")
    profitable_args = profitable_stage[2]
    assert "--candidates_path" in profitable_args
    assert profitable_args[profitable_args.index("--candidates_path") + 1].endswith(
        "/reports/strategy_builder/strategy_builder_fractional_wiring/strategy_candidates.parquet"
    )


def test_run_all_runtime_invariants_enforce_fails_preflight(monkeypatch, tmp_path):
    executed: list[str] = []

    def fake_run_stage(stage, script, base_args, run_id, **kwargs) -> bool:
        executed.append(stage)
        return True

    monkeypatch.setattr(run_all, "DATA_ROOT", tmp_path / "data")
    monkeypatch.setattr(run_all, "_git_commit", lambda _project_root: "test-sha")
    monkeypatch.setattr(run_all, "_run_stage", fake_run_stage)
    monkeypatch.setattr(
        run_all,
        "validate_runtime_invariants_specs",
        lambda _repo_root: ["runtime lanes spec: duplicate lane_id 'alpha_5s'"],
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_all.py",
            "--run_id",
            "runtime_enforce_fail",
            "--symbols",
            "BTCUSDT",
            "--start",
            "2024-01-01",
            "--end",
            "2024-01-02",
            "--runtime_invariants_mode",
            "enforce",
            "--run_phase2_conditional",
            "0",
            "--run_strategy_blueprint_compiler",
            "0",
            "--run_strategy_builder",
            "0",
            "--run_candidate_promotion",
            "0",
            "--run_edge_registry_update",
            "0",
            "--run_edge_candidate_universe",
            "0",
            "--run_naive_entry_eval",
            "0",
            "--run_expectancy_analysis",
            "0",
            "--run_expectancy_robustness",
            "0",
            "--run_recommendations_checklist",
            "0",
            "--run_interaction_lift",
            "0",
        ],
    )

    rc = run_all.main()
    assert rc == 1
    assert executed == []
    manifest = _load_manifest(tmp_path, "runtime_enforce_fail")
    assert manifest["runtime_invariants_mode"] == "enforce"
    assert manifest["runtime_invariants_validation_ok"] is False
    assert manifest["failed_stage"] == "runtime_invariants_preflight"
    assert manifest["status"] == "failed"


def test_run_all_runtime_invariants_audit_records_issues_and_continues(monkeypatch, tmp_path):
    executed: list[str] = []

    def fake_run_stage(stage, script, base_args, run_id, **kwargs) -> bool:
        executed.append(stage)
        return False

    monkeypatch.setattr(run_all, "DATA_ROOT", tmp_path / "data")
    monkeypatch.setattr(run_all, "_git_commit", lambda _project_root: "test-sha")
    monkeypatch.setattr(run_all, "_run_stage", fake_run_stage)
    monkeypatch.setattr(
        run_all,
        "validate_runtime_invariants_specs",
        lambda _repo_root: ["runtime hashing spec: domains must be a non-empty list"],
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_all.py",
            "--run_id",
            "runtime_audit_continue",
            "--symbols",
            "BTCUSDT",
            "--start",
            "2024-01-01",
            "--end",
            "2024-01-02",
            "--runtime_invariants_mode",
            "audit",
        ],
    )

    rc = run_all.main()
    assert rc == 1
    assert executed
    manifest = _load_manifest(tmp_path, "runtime_audit_continue")
    assert manifest["runtime_invariants_mode"] == "audit"
    assert manifest["runtime_invariants_validation_ok"] is False
    assert manifest["runtime_invariants_status"] == "invalid_spec"
    assert manifest["failed_stage"] != "runtime_invariants_preflight"


