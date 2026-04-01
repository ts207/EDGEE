from __future__ import annotations

import json
from pathlib import Path

from project.core.config import get_data_root
from project.live.shadow_live_validation import run_shadow_live_thesis_validation
from project.research.paired_event_study import build_direct_paired_event_study
from project.research.seed_empirical import run_empirical_seed_pass
from project.research.seed_package import package_seed_promoted_theses
from project.research.thesis_evidence_runner import build_founding_thesis_evidence

PACKAGE_RUN_ID = "block_g_empirical_paired_v1"
SHADOW_RUN_ID = "block_g_shadow_live_v1"


def main() -> int:
    build_founding_thesis_evidence()
    build_direct_paired_event_study()
    run_empirical_seed_pass()
    package_outputs = package_seed_promoted_theses(package_run_id=PACKAGE_RUN_ID)
    run_shadow_live_thesis_validation(
        thesis_store_path=package_outputs["thesis_store"],
        run_id=SHADOW_RUN_ID,
    )
    summary = {
        "package_run_id": PACKAGE_RUN_ID,
        "shadow_run_id": SHADOW_RUN_ID,
        "data_root": str(Path(get_data_root())),
        "thesis_store": str(package_outputs["thesis_store"]),
    }
    Path("docs/generated/block_g_run_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
