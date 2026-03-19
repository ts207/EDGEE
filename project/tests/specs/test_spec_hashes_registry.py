from __future__ import annotations

from pathlib import Path

from project import PROJECT_ROOT
from project.specs.utils import get_spec_hashes


def test_get_spec_hashes_uses_canonical_registry_paths():
    hashes = get_spec_hashes(PROJECT_ROOT.parent)
    assert isinstance(hashes, dict)
    assert "gates.yaml" in hashes
    assert all(".yaml" in k for k in hashes)
