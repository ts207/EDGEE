from __future__ import annotations

from pathlib import Path

import yaml


def test_search_space_includes_vol_shock_event_trigger():
    search_space_path = Path("/home/irene/Edge/spec/search_space.yaml")
    payload = yaml.safe_load(search_space_path.read_text(encoding="utf-8"))

    assert "VOL_SHOCK" in payload["triggers"]["events"]
