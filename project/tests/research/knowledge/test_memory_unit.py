from __future__ import annotations
import pytest
import pandas as pd
import json
from pathlib import Path
from project.research.knowledge.memory import classify_failure_cause, ensure_memory_store, read_memory_table, write_memory_table

def test_classify_failure_cause_mechanical():
    assert classify_failure_cause("stage_failed_v1", 100) == "mechanical"
    assert classify_failure_cause("missing_event_column_X", 100) == "mechanical"
    assert classify_failure_cause("", 0) == "mechanical"

def test_classify_failure_cause_insufficient_sample():
    assert classify_failure_cause("gate_promo_stability_gate", 20) == "insufficient_sample"
    # Even if it's a cost gate, if sample is small, it's insufficient_sample
    assert classify_failure_cause("gate_promo_retail_cost_budget", 5) == "insufficient_sample"

def test_classify_failure_cause_cost():
    assert classify_failure_cause("gate_promo_retail_cost_budget", 100) == "cost"
    assert classify_failure_cause("gate_promo_stressed_cost_survival", 50) == "cost"

def test_classify_failure_cause_market():
    assert classify_failure_cause("gate_promo_stability_gate", 100) == "market"
    assert classify_failure_cause("gate_promo_oos_validation", 100) == "market"
    assert classify_failure_cause("", 100) == "market"
    assert classify_failure_cause("unknown_gate", 100) == "market"

def test_classify_failure_cause_overfitting():
    assert classify_failure_cause("gate_promo_multiplicity_diagnostics", 100) == "overfitting"
    assert classify_failure_cause("gate_promo_negative_control_missing", 100) == "overfitting"

def test_ensure_memory_store_initializes_files(tmp_path):
    # Mock data_root
    program_id = "test_prog"
    paths = ensure_memory_store(program_id, data_root=tmp_path)
    
    assert paths.root.exists()
    assert (paths.root / "belief_state.json").exists()
    assert (paths.root / "next_actions.json").exists()
    
    # Check content of belief_state
    belief = json.loads((paths.root / "belief_state.json").read_text())
    assert "current_focus" in belief

def test_write_and_read_memory_table(tmp_path):
    program_id = "test_prog"
    df = pd.DataFrame({"event_type": ["E1"], "split_label": ["train"], "expectancy": [0.1]})
    
    # We need to use a table name that exists in _TABLES, e.g. 'tested_regions'
    write_memory_table(program_id, "tested_regions", df, data_root=tmp_path)
    
    read_df = read_memory_table(program_id, "tested_regions", data_root=tmp_path)
    assert len(read_df) == 1
    assert read_df.iloc[0]["event_type"] == "E1"
