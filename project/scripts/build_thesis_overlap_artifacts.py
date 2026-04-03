from __future__ import annotations

from pathlib import Path

from project.live.thesis_store import ThesisStore
from project.portfolio.thesis_overlap import write_thesis_overlap_artifacts

DOCS = Path("docs/generated")


def main() -> None:
    run_id = "thesis_overlap_artifacts"
    try:
        store = ThesisStore.latest()
        theses = store.all()
        run_id = store.run_id or run_id
    except Exception:
        theses = []
    write_thesis_overlap_artifacts(theses, DOCS, source_run_id=run_id)


if __name__ == "__main__":
    main()
