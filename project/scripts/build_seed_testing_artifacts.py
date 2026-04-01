from __future__ import annotations

from pathlib import Path

from project.research.seed_testing import score_seed_candidates
from project.spec_registry.loaders import repo_root

DOCS = repo_root() / "docs" / "generated"


if __name__ == "__main__":
    score_seed_candidates(docs_dir=DOCS)
