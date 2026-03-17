"""Tests for detector_audit_module shared measurement logic."""
import math
import pandas as pd
import pytest


def _make_df(n: int = 5000) -> pd.DataFrame:
    """Build a minimal rich DataFrame for testing."""
    import numpy as np
    ts = pd.date_range("2023-01-01", periods=n, freq="5min", tz="UTC")
    close = pd.Series(30000.0 + np.cumsum(np.random.randn(n) * 50), name="close")
    df = pd.DataFrame({
        "timestamp": ts,
        "open": close,
        "high": close * 1.001,
        "low": close * 0.999,
        "close": close,
        "close_perp": close,
        "close_spot": close * 0.9998,
        "volume": 1000.0,
        "quote_volume": close * 1000.0,
        "trade_count": 500,
        "taker_buy_volume": 500.0,
        "taker_buy_quote_volume": close * 500.0,
        "spread_bps": 2.5,
        "depth_usd": 5_000_000.0,
        "funding_rate_scaled": 0.0001,
        "symbol": "BTCUSDT",
    })
    log_ret = np.log(close / close.shift(1))
    df["rv_96"] = log_ret.rolling(96, min_periods=12).std()
    return df


def test_measure_detector_returns_metrics_dict():
    from project.events.detectors.registry import load_all_detectors, get_detector
    from project.scripts.detector_audit_module import measure_detector

    load_all_detectors()
    detector = get_detector("VOL_SPIKE")
    assert detector is not None, "VOL_SPIKE detector must be registered"

    df = _make_df()
    segments = []  # no truth windows → uncovered

    metrics = measure_detector(detector, df, "BTCUSDT", segments, "test_run")

    assert metrics["event_type"] == "VOL_SPIKE"
    assert metrics["symbol"] == "BTCUSDT"
    assert metrics["classification"] == "uncovered"
    assert metrics["error"] is None
    assert isinstance(metrics["total_events"], int)
    assert isinstance(metrics["precision"], float)


def test_measure_detector_handles_missing_required_column():
    from project.events.detectors.registry import load_all_detectors, get_detector
    from project.scripts.detector_audit_module import measure_detector

    load_all_detectors()
    detector = get_detector("BASIS_DISLOC")
    assert detector is not None

    df = _make_df()
    df = df.drop(columns=["close_spot"])  # BASIS_DISLOC requires close_spot
    segments = []

    metrics = measure_detector(detector, df, "BTCUSDT", segments, "test_run")
    assert metrics["classification"] == "error"
    assert metrics["error"] is not None


def test_classify_noisy():
    from project.scripts.detector_audit_module import _classify
    assert _classify(precision=0.30, recall=0.60, expected_windows=5) == "noisy"


def test_classify_silent():
    from project.scripts.detector_audit_module import _classify
    assert _classify(precision=0.70, recall=0.10, expected_windows=5) == "silent"


def test_classify_broken():
    from project.scripts.detector_audit_module import _classify
    assert _classify(precision=0.20, recall=0.10, expected_windows=5) == "broken"


def test_classify_stable():
    from project.scripts.detector_audit_module import _classify
    assert _classify(precision=0.60, recall=0.50, expected_windows=5) == "stable"


def test_classify_uncovered():
    from project.scripts.detector_audit_module import _classify
    assert _classify(precision=0.0, recall=0.0, expected_windows=0) == "uncovered"
