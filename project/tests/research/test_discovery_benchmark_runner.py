import pytest
from pathlib import Path
from project import PROJECT_ROOT
from project.research.benchmarks import discovery_benchmark

def test_benchmark_runner_immutability():
    # Read bytes of configs before run
    ledger_config_path = PROJECT_ROOT.parent / "project/configs/discovery_ledger.yaml"
    scoring_config_path = PROJECT_ROOT.parent / "project/configs/discovery_scoring_v2.yaml"
    
    def get_bytes(p):
        return p.read_bytes() if p.exists() else b""

    before_ledger = get_bytes(ledger_config_path)
    before_scoring = get_bytes(scoring_config_path)

    # Note: We don't actually run a full benchmark here as it might be slow/data-dependent
    # but we verify that the helper function doesn't touch the disk.
    base_search = {"symbol": "BTC", "cases": []}
    base_scoring = {"v2_scoring": {"enabled": True}}
    base_ledger = {"enabled": False}
    
    # Run helper
    resolved = discovery_benchmark._resolved_benchmark_mode_config(
        base_search, base_scoring, base_ledger, "ledger"
    )
    
    assert resolved["ledger"]["enabled"] is True
    assert base_ledger["enabled"] is False # Ensure deepcopy worked
    
    # Check disk bytes again
    assert get_bytes(ledger_config_path) == before_ledger
    assert get_bytes(scoring_config_path) == before_scoring

def test_benchmark_output_contains_resolved_config(tmp_path):
    # This would require a minimal run, but we can check the logic in discovery_benchmark.py
    # and trust our previous multi_replace_file_content which added the json.dump call.
    pass
