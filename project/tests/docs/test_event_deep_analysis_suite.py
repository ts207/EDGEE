from __future__ import annotations

from pathlib import Path

from project.scripts.build_event_deep_analysis_suite import build_outputs


def test_event_deep_analysis_artifacts_are_current() -> None:
    outputs = build_outputs()
    for path, content in outputs.items():
        assert Path(path).read_text(encoding="utf-8") == content
