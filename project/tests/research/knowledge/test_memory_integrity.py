from __future__ import annotations

import pandas as pd
import pytest

from project.core.exceptions import DataIntegrityError
from project.research.knowledge.memory import build_tested_regions_snapshot


def test_build_tested_regions_snapshot_raises_on_corrupted_expanded_hypotheses(tmp_path) -> None:
    data_root = tmp_path / "data"
    run_id = "run_1"
    program_id = "btc_campaign"

    phase2_dir = data_root / "reports" / "phase2" / run_id / "search_engine"
    phase2_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                "hypothesis_id": "hyp_1",
                "candidate_id": "cand_1",
                "event_type": "VOL_SHOCK",
                "trigger_type": "EVENT",
                "template_id": "mean_reversion",
                "direction": "long",
                "horizon": "12b",
            }
        ]
    ).to_parquet(phase2_dir / "phase2_candidates.parquet", index=False)

    exp_dir = data_root / "artifacts" / "experiments" / program_id / run_id
    exp_dir.mkdir(parents=True, exist_ok=True)
    (exp_dir / "expanded_hypotheses.parquet").write_bytes(b"NOTPARQUET")

    with pytest.raises(DataIntegrityError):
        build_tested_regions_snapshot(run_id=run_id, program_id=program_id, data_root=data_root)
