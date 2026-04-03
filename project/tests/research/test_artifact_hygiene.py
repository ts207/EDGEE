from __future__ import annotations

from pathlib import Path

from project.live.contracts import (
    PromotedThesis,
    ThesisEvidence,
    ThesisGovernance,
    ThesisLineage,
    ThesisRequirements,
    ThesisSource,
)
from project.portfolio.thesis_overlap import write_thesis_overlap_artifacts
from project.research.artifact_hygiene import build_artifact_refs, build_summary_metadata


def _thesis(thesis_id: str) -> PromotedThesis:
    return PromotedThesis(
        thesis_id=thesis_id,
        status="active",
        symbol_scope={"mode": "symbol_set", "symbols": ["BTCUSDT"], "candidate_symbol": "BTCUSDT"},
        timeframe="5m",
        primary_event_id="VOL_SHOCK",
        event_family="VOL_SHOCK",
        event_side="both",
        required_context={},
        supportive_context={"canonical_regime": "VOLATILITY"},
        expected_response={},
        invalidation={"metric": "adverse_proxy"},
        risk_notes=[],
        evidence=ThesisEvidence(sample_size=12, rank_score=1.0, stability_score=0.8),
        lineage=ThesisLineage(run_id="run-1", candidate_id=thesis_id),
        governance=ThesisGovernance(tier="A", operational_role="trigger", trade_trigger_eligible=True),
        requirements=ThesisRequirements(trigger_events=["VOL_SHOCK"], required_episodes=["EP_VOL_BREAKOUT"]),
        source=ThesisSource(event_contract_ids=["VOL_SHOCK"], episode_contract_ids=["EP_VOL_BREAKOUT"]),
    )


def test_build_artifact_refs_marks_dead_reference(tmp_path: Path) -> None:
    workspace_root = tmp_path
    existing = tmp_path / "docs" / "generated" / "artifact.md"
    existing.parent.mkdir(parents=True, exist_ok=True)
    existing.write_text("ok\n", encoding="utf-8")
    refs, invalid = build_artifact_refs({"existing": existing, "missing": tmp_path / "missing.json"}, workspace_root=workspace_root)
    metadata = build_summary_metadata(
        schema_version="artifact_test_v1",
        artifact_root=existing.parent,
        source_run_id="artifact-test",
        workspace_root=workspace_root,
        invalid_artifact_refs=invalid,
    )
    assert refs["existing"]["path"] == "docs/generated/artifact.md"
    assert "missing" in invalid
    assert metadata["all_referenced_files_exist"] is False
    assert metadata["artifact_root"] == "docs/generated"


def test_write_thesis_overlap_artifacts_records_workspace_local_metadata(tmp_path: Path) -> None:
    out_dir = tmp_path / "docs" / "generated"
    payload = write_thesis_overlap_artifacts([_thesis("thesis::1"), _thesis("thesis::2")], out_dir, source_run_id="overlap-test", workspace_root=tmp_path)
    assert payload["schema_version"] == "thesis_overlap_graph_v1"
    assert payload["workspace_root"] == "."
    assert payload["artifact_root"] == "docs/generated"
    assert payload["source_run_id"] == "overlap-test"
    assert payload["all_referenced_files_exist"] is True
    assert payload["invalid_artifact_refs"] == []
    assert payload["artifact_refs"]["overlap_json"]["path"] == "docs/generated/thesis_overlap_graph.json"
    md_text = (out_dir / "thesis_overlap_graph.md").read_text(encoding="utf-8")
    assert "## Artifact metadata" in md_text
    assert "/home/irene/" not in md_text
