from __future__ import annotations

from pathlib import Path

import yaml


def test_search_space_includes_vol_shock_event_trigger():
    repo_root = Path(__file__).resolve().parents[3]
    search_space_path = repo_root / "spec" / "search_space.yaml"
    payload = yaml.safe_load(search_space_path.read_text(encoding="utf-8"))

    assert "VOL_SHOCK" in payload["triggers"]["events"]
