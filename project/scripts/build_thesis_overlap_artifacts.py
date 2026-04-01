from __future__ import annotations

from pathlib import Path

from project.live.thesis_store import ThesisStore
from project.portfolio.thesis_overlap import write_thesis_overlap_artifacts

DOCS = Path("docs/generated")


def main() -> None:
    try:
        store = ThesisStore.latest()
        theses = store.all()
    except Exception:
        theses = []
    write_thesis_overlap_artifacts(theses, DOCS)


if __name__ == "__main__":
    main()
