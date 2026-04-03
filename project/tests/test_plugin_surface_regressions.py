from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).parents[2]


def test_edge_agents_plugin_readme_tracks_canonical_export_surface() -> None:
    path = _repo_root() / "plugins" / "edge-agents" / "README.md"
    text = path.read_text(encoding="utf-8")
    assert "make discover|review|export|validate" in text
    assert "edge_export_theses.sh" in text
    assert "advanced bootstrap" in text


def test_edge_agents_export_wrapper_exists_and_targets_run_export_module() -> None:
    path = _repo_root() / "plugins" / "edge-agents" / "scripts" / "edge_export_theses.sh"
    text = path.read_text(encoding="utf-8")
    assert "--run_id" in text
    assert "project.research.export_promoted_theses" in text


def test_edge_agents_bootstrap_wrapper_requires_explicit_overlap_source() -> None:
    path = _repo_root() / "plugins" / "edge-agents" / "scripts" / "edge_bootstrap_theses.sh"
    text = path.read_text(encoding="utf-8")
    assert "thesis-overlap requires an explicit thesis source" in text
    assert "--thesis_run_id" in text
    assert "--thesis_path" in text
    assert "--run_id" in text
