from __future__ import annotations

from pathlib import Path

from project.research.seed_bootstrap import (
    build_promotion_seed_inventory,
    build_thesis_bootstrap_baseline,
    write_seed_promotion_policy_artifacts,
)

DOCS = Path("docs/generated")


def main() -> None:
    build_thesis_bootstrap_baseline(docs_dir=DOCS)
    build_promotion_seed_inventory(docs_dir=DOCS)
    write_seed_promotion_policy_artifacts(docs_dir=DOCS)


if __name__ == "__main__":
    main()
