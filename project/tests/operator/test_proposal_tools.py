from __future__ import annotations

import yaml

import project.operator.proposal_tools as proposal_tools


def test_explain_and_lint_proposal(monkeypatch, tmp_path):
    proposal_path = tmp_path / "proposal.yaml"
    proposal_path.write_text(
        yaml.safe_dump(
            {
                "program_id": "btc_campaign",
                "start": "2021-01-01",
                "end": "2021-12-31",
                "symbols": ["BTCUSDT"],
                "trigger_space": {"allowed_trigger_types": ["EVENT"], "events": {"include": ["VOL_SHOCK"]}},
                "templates": ["mean_reversion"],
                "timeframe": "5m",
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        proposal_tools,
        "translate_and_validate_proposal",
        lambda *args, **kwargs: {
            "validated_plan": {
                "estimated_hypothesis_count": 3,
                "required_detectors": ["VolShockDetector"],
                "required_features": ["ret_5m"],
                "required_states": [],
            },
            "run_all_overrides": {"program_id": "btc_campaign"},
        },
    )
    monkeypatch.setattr(proposal_tools, "validate_bounded_proposal", lambda *args, **kwargs: None)

    explained = proposal_tools.explain_proposal(proposal_path=proposal_path)
    linted = proposal_tools.lint_proposal(proposal_path=proposal_path)

    assert explained["estimated_hypothesis_count"] == 3
    assert explained["required_detectors"] == ["VolShockDetector"]
    assert linted["status"] == "pass"
