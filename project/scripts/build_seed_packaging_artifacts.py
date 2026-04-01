from __future__ import annotations

from pathlib import Path

from project.research.seed_package import package_seed_promoted_theses

DOCS = Path("docs/generated")


def main() -> None:
    package_seed_promoted_theses(docs_dir=DOCS)


if __name__ == "__main__":
    main()
