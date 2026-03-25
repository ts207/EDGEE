from __future__ import annotations
import pytest
import pandas as pd
from project.strategy.dsl.validate import validate_signal_columns, validate_overlay_columns
from project.strategy.dsl.schema import OverlaySpec
from unittest.mock import patch

def test_validate_signal_columns_success():
    df = pd.DataFrame({
        "close": [100.0, 101.0],
        "spread_bps": [1.0, 2.0],
        "funding_rate_scaled": [0.01, 0.02],
        "quote_volume": [1000.0, 2000.0],
        "range_96": [10.0, 11.0]
    })
    signals = ["spread_guard_pass", "funding_extreme_event", "liquidity_vacuum_event", "vol_aftershock_event"]
    # Mock REGISTRY_SIGNAL_COLUMNS to be empty so it doesn't look for 'liquidity_vacuum_event' as a column
    with patch("project.strategy.dsl.validate.REGISTRY_SIGNAL_COLUMNS", set()):
        # Should not raise
        validate_signal_columns(df, signals, "bp_test")

def test_validate_signal_columns_missing():
    df = pd.DataFrame({
        "close": [100.0, 101.0]
    })
    signals = ["spread_guard_pass"]
    with patch("project.strategy.dsl.validate.REGISTRY_SIGNAL_COLUMNS", set()):
        with pytest.raises(ValueError, match="missing required columns for entry signals"):
            validate_signal_columns(df, signals, "bp_test")

def test_validate_signal_columns_registry_success():
    df = pd.DataFrame({
        "high": [100.0, 101.0],
        "low": [99.0, 100.0]
    })
    with patch("project.strategy.dsl.validate.REGISTRY_SIGNAL_COLUMNS", {"high"}):
        # 'high' is in REGISTRY_SIGNAL_COLUMNS
        validate_signal_columns(df, ["high"], "bp_test")

def test_validate_overlay_columns_success():
    df = pd.DataFrame({
        "spread_bps": [1.0, 2.0],
        "quote_volume": [1000.0, 2000.0]
    })
    overlays = [
        OverlaySpec(name="spread_guard", params={}),
        OverlaySpec(name="liquidity_guard", params={})
    ]
    # Should not raise
    validate_overlay_columns(df, overlays, "bp_test")

def test_validate_overlay_columns_missing():
    df = pd.DataFrame({
        "close": [100.0, 101.0]
    })
    overlays = [OverlaySpec(name="spread_guard", params={})]
    with pytest.raises(ValueError, match="missing required columns for overlays"):
        validate_overlay_columns(df, overlays, "bp_test")

def test_has_numeric_values_check():
    # Test internal _has_numeric_values via validate calls
    df = pd.DataFrame({
        "spread_bps": ["none", "none"] # strings that can't be numeric
    })
    overlays = [OverlaySpec(name="spread_guard", params={})]
    with pytest.raises(ValueError, match="missing required columns"):
        validate_overlay_columns(df, overlays, "bp_test")
