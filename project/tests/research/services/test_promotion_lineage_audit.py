from pathlib import Path

import pandas as pd

from project.research.services.promotion_service import _write_promotion_lineage_audit


def test_write_promotion_lineage_audit(tmp_path: Path) -> None:
    out = _write_promotion_lineage_audit(
        out_dir=tmp_path,
        run_id="run_1",
        evidence_bundles=[
            {
                "candidate_id": "cand_1",
                "event_type": "VOL_SHOCK",
                "promotion_decision": {"promotion_status": "promoted", "promotion_track": "standard"},
                "bundle_version": "v1",
                "policy_version": "p1",
                "metadata": {"program_id": "prog_1", "campaign_id": "camp_1"},
            }
        ],
        promoted_df=pd.DataFrame([{"candidate_id": "cand_1"}]),
        live_export_diagnostics={"thesis_count": 1},
    )
    assert Path(out["json_path"]).exists()
    assert Path(out["md_path"]).exists()
    assert 'camp_1' in Path(out["md_path"]).read_text(encoding='utf-8')
