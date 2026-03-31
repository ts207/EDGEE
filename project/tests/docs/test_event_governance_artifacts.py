from __future__ import annotations

import json
from pathlib import Path

from project.scripts.build_event_contract_artifacts import build_artifacts
from project.scripts.build_event_ontology_artifacts import build_outputs
from project.scripts.event_ontology_audit import render_markdown, run_audit


def test_event_governance_artifacts_are_current() -> None:
    contract_outputs = build_artifacts()["outputs"]
    for path, content in contract_outputs.items():
        assert Path(path).read_text(encoding="utf-8") == content

    ontology_outputs = build_outputs()
    for path, content in ontology_outputs.items():
        assert Path(path).read_text(encoding="utf-8") == content

    audit_report = run_audit()
    assert Path("docs/generated/event_ontology_audit.json").read_text(encoding="utf-8") == (
        json.dumps(audit_report, indent=2, sort_keys=True) + "\n"
    )
    assert Path("docs/generated/event_ontology_audit.md").read_text(encoding="utf-8") == render_markdown(audit_report)
