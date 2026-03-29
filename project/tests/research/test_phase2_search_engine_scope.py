from __future__ import annotations

from pathlib import Path

import yaml

from project.research.phase2_search_engine import _write_event_scoped_search_spec


def test_write_event_scoped_search_spec_narrows_default_broad_spec(tmp_path: Path) -> None:
    out_dir = tmp_path / "search_engine"

    resolved = _write_event_scoped_search_spec(
        search_spec="spec/search_space.yaml",
        phase2_event_type="VOL_SHOCK",
        out_dir=out_dir,
    )

    resolved_path = Path(resolved)
    assert resolved_path.exists()
    payload = yaml.safe_load(resolved_path.read_text(encoding="utf-8"))
    assert payload["events"] == ["VOL_SHOCK"]
    assert payload["triggers"]["events"] == ["VOL_SHOCK"]
    assert payload["templates"] == [
        "mean_reversion",
        "continuation",
        "trend_continuation",
    ]
    assert payload["horizons"] == ["60m"]
    assert payload["include_sequences"] is False
    assert payload["include_interactions"] is False
    assert "states" not in payload
    assert "transitions" not in payload
    assert payload["metadata"]["auto_scope"] == "event:VOL_SHOCK"


def test_write_event_scoped_search_spec_preserves_explicit_nondefault_spec(tmp_path: Path) -> None:
    out_dir = tmp_path / "search_engine"

    resolved = _write_event_scoped_search_spec(
        search_spec="spec/search/search_benchmark_vol_shock.yaml",
        phase2_event_type="VOL_SHOCK",
        out_dir=out_dir,
    )

    assert resolved == "spec/search/search_benchmark_vol_shock.yaml"
    assert not out_dir.exists()
