from __future__ import annotations

from pathlib import Path

from project.scripts.generate_operator_surface_inventory import build_inventory, render_markdown


def test_operator_inventory_covers_new_commands():
    inventory = build_inventory()
    commands = set(inventory["canonical_operator_commands"])
    assert "edge operator compare" in commands
    assert "edge operator regime-report" in commands
    assert "edge operator diagnose" in commands


def test_operator_inventory_doc_is_in_sync():
    inventory = build_inventory()
    expected = render_markdown(inventory)
    doc_path = Path("docs/operator_command_inventory.md")
    assert doc_path.read_text(encoding="utf-8") == expected


def test_readme_and_start_here_anchor_canonical_operator_flow():
    readme = Path("README.md").read_text(encoding="utf-8")
    start_here = Path("docs/00_START_HERE.md").read_text(encoding="utf-8")
    assert "edge operator preflight" in readme
    assert "edge operator diagnose" in start_here
    assert "edge operator compare" in start_here
