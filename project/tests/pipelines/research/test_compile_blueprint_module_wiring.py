from __future__ import annotations

import json
import sys

import pandas as pd

from project.pipelines.research import compile_strategy_blueprints as compiler
from project.strategy.dsl.schema import (
    Blueprint,
    EntrySpec,
    EvaluationSpec,
    ExitSpec,
    LineageSpec,
    SizingSpec,
    SymbolScopeSpec,
)


def _make_blueprint(*, bp_id: str, candidate_id: str) -> Blueprint:
    return Blueprint(
        id=bp_id,
        run_id="run_test",
        event_type="VOL_SHOCK",
        candidate_id=candidate_id,
        symbol_scope=SymbolScopeSpec(
            mode="single_symbol",
            symbols=["BTCUSDT"],
            candidate_symbol="BTCUSDT",
        ),
        direction="long",
        entry=EntrySpec(
            triggers=["entry_trigger"],
            conditions=[],
            confirmations=[],
            delay_bars=0,
            cooldown_bars=0,
        ),
        exit=ExitSpec(
            time_stop_bars=5,
            invalidation={"metric": "ret_1m", "operator": "<", "value": -1.0},
            stop_type="percent",
            stop_value=0.01,
            target_type="percent",
            target_value=0.02,
        ),
        sizing=SizingSpec(
            mode="fixed_risk",
            risk_per_trade=0.01,
            max_gross_leverage=1.0,
        ),
        overlays=[],
        evaluation=EvaluationSpec(
            min_trades=10,
            cost_model={"fees_bps": 2.0, "slippage_bps": 4.0, "funding_included": False},
            robustness_flags={
                "oos_required": True,
                "multiplicity_required": True,
                "regime_stability_required": True,
            },
        ),
        lineage=LineageSpec(
            source_path="source.csv",
            compiler_version="strategy_dsl_v1",
            generated_at_utc="1970-01-01T00:00:00Z",
        ),
    )


def test_choose_event_rows_delegates_to_selection_module(monkeypatch):
    captured: dict[str, object] = {}
    sentinel_rows = [{"candidate_id": "c1"}]
    sentinel_diag = {"reason": "sentinel"}
    sentinel_df = pd.DataFrame([{"candidate_id": "c1"}])

    def _fake_choose_event_rows(**kwargs):
        captured.update(kwargs)
        return sentinel_rows, sentinel_diag, sentinel_df

    monkeypatch.setattr(compiler, "_selection_choose_event_rows", _fake_choose_event_rows)

    rows, diag, selection_df = compiler._choose_event_rows(
        run_id="run_test",
        event_type="VOL_SHOCK",
        edge_rows=[],
        phase2_df=pd.DataFrame(),
        max_per_event=1,
        allow_fallback_blueprints=True,
        strict_cost_fields=True,
        min_events=25,
    )

    assert rows == sentinel_rows
    assert diag == sentinel_diag
    assert selection_df is sentinel_df
    assert captured["data_root"] == compiler.DATA_ROOT
    assert captured["candidate_id_fn"] is compiler._candidate_id
    assert captured["load_gates_spec_fn"] is compiler._load_gates_spec
    assert captured["passes_quality_floor_fn"] is compiler._passes_quality_floor
    assert captured["rank_key_fn"] is compiler._rank_key
    assert captured["passes_fallback_gate_fn"] is compiler._passes_fallback_gate
    assert captured["as_bool_fn"] is compiler._as_bool
    assert captured["safe_float_fn"] is compiler._safe_float


def test_annotate_blueprints_external_validation_supports_pydantic_models(monkeypatch):
    bp = _make_blueprint(bp_id="bp_1", candidate_id="c_1")
    monkeypatch.setattr(
        compiler,
        "_load_external_validation_strategy_metrics",
        lambda run_id: ({}, "sha256:ignored", "unused_source"),
    )

    annotated, stats = compiler._annotate_blueprints_with_external_validation_evidence(
        blueprints=[bp],
        run_id="run_test",
        evidence_hash="sha256:test_hash",
    )

    assert len(annotated) == 1
    assert annotated[0].lineage.wf_status == "pass"
    assert annotated[0].lineage.wf_evidence_hash == "sha256:test_hash"
    assert bp.lineage.wf_evidence_hash == ""
    assert stats["wf_evidence_used"] is False


def test_main_compilation_loop_accepts_record_dicts(monkeypatch, tmp_path):
    data_root = tmp_path
    run_id = "compile_loop_dicts"
    promo_dir = data_root / "reports" / "promotions" / run_id
    promo_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                "candidate_id": "cand_1",
                "event_type": "VOL_SHOCK",
                "status": "PROMOTED",
                "pnl_series": json.dumps([1.0, -0.5, 0.75, 1.25]),
            }
        ]
    ).to_parquet(promo_dir / "promoted_candidates.parquet", index=False)
    historical_dir = data_root / "reports" / "promotions" / "prior_run"
    historical_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                "candidate_id": "prior_cand",
                "event_type": "VOL_SHOCK",
                "status": "PROMOTED",
                "pnl_series": json.dumps([1.0, -0.5, 0.75, 1.25]),
            }
        ]
    ).to_parquet(historical_dir / "promoted_candidates.parquet", index=False)
    portfolio_state_path = data_root / "live_state.json"
    portfolio_state_path.write_text(
        json.dumps(
            {
                "account": {
                    "wallet_balance": 1_000.0,
                    "available_balance": 600.0,
                    "positions": [
                        {
                            "symbol": "BTCUSDT",
                            "quantity": 0.01,
                            "mark_price": 30_000.0,
                        }
                    ],
                },
                "current_vol": 0.30,
                "target_vol": 0.15,
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(compiler, "DATA_ROOT", data_root)
    monkeypatch.setattr(compiler, "_checklist_decision", lambda _run_id: "PROMOTE")
    monkeypatch.setattr(compiler, "_load_run_mode", lambda _run_id: "research")
    monkeypatch.setattr(compiler, "ontology_spec_hash", lambda _root: "sha256:test")
    monkeypatch.setattr(compiler, "_load_operator_registry", lambda: {})
    monkeypatch.setattr(
        compiler,
        "resolve_objective_profile_contract",
        lambda **_: type(
            "Contract",
            (),
            {
                "retail_profile_name": "capital_constrained",
                "require_low_capital_contract": False,
                "max_concurrent_positions": 2,
                "effective_per_position_notional_cap_usd": 5_000.0,
                "low_capital_contract": {"fee_tier": "taker", "max_position_notional_usd": 5_000.0},
            },
        )(),
    )
    monkeypatch.setattr(compiler, "start_manifest", lambda *args, **kwargs: {})
    monkeypatch.setattr(compiler, "finalize_manifest", lambda *args, **kwargs: None)

    def _fake_compile_blueprint(**kwargs):
        row = kwargs["merged_row"]
        blueprint = _make_blueprint(bp_id="bp_1", candidate_id=str(row["candidate_id"]))
        return (
            blueprint.model_copy(
                update={
                    "lineage": blueprint.lineage.model_copy(
                        update={
                            "constraints": {
                                "expected_return_bps": 12.0,
                                "expected_adverse_bps": 4.5,
                            }
                        }
                    )
                }
            ),
            0,
        )

    monkeypatch.setattr(compiler, "compile_blueprint", _fake_compile_blueprint)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "compile_strategy_blueprints.py",
            "--run_id",
            run_id,
            "--symbols",
            "BTCUSDT",
            "--ignore_checklist",
            "1",
            "--portfolio_state_path",
            str(portfolio_state_path),
        ],
    )

    rc = compiler.main()
    assert rc == 0
    out_path = data_root / "reports" / "strategy_blueprints" / run_id / "blueprints.jsonl"
    assert out_path.exists()
    payload = json.loads(out_path.read_text(encoding="utf-8").splitlines()[0])
    assert payload["candidate_id"] == "cand_1"
    assert payload["sizing"]["risk_per_trade"] < 0.01
    assert payload["lineage"]["constraints"]["portfolio_state_path"] == str(portfolio_state_path)
    assert payload["lineage"]["constraints"]["max_promoted_pnl_correlation"] >= 0.99
    allocation_path = (
        data_root
        / "reports"
        / "strategy_blueprints"
        / run_id
        / "allocation_specs"
        / "bp_1.allocation_spec.json"
    )
    assert allocation_path.exists()
    allocation_payload = json.loads(allocation_path.read_text(encoding="utf-8"))
    assert allocation_payload["sizing_policy"]["expected_return_bps"] == 12.0
    assert allocation_payload["sizing_policy"]["expected_adverse_bps"] == 4.5
