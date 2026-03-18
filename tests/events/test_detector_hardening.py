from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from project.events.families.oi import DeleveragingWaveDetector
from project.events.families.canonical_proxy import AbsorptionProxyDetector, DepthStressProxyDetector
from project.events.families.canonical_proxy import PriceVolImbalanceProxyDetector
from project.events.detectors.funding import (
    FundingFlipDetector,
    FundingNormalizationDetector,
    FundingPersistenceDetector,
)
from project.events.detectors.exhaustion import TrendExhaustionDetector, MomentumDivergenceDetector
from project.events.families.temporal import SpreadRegimeWideningDetector
from project.events.detectors.trend import SREventDetector, TrendAccelerationDetector
from project.events.policy import (
    LIVE_SAFE_EVENT_TYPES,
    RETROSPECTIVE_EVENT_TYPES,
    is_legacy_event_type,
)

def create_mock_data(n=2000):
    rng = np.random.default_rng(42)
    # Price with some trends and vol
    returns = rng.normal(0, 0.001, n)
    # Add a strong trend
    returns[1000:1100] += 0.005 
    close = 100 * np.exp(np.cumsum(returns))
    
    # OI and Vol for DeleveragingWave
    oi_delta_1h = rng.normal(0, 1.0, n)
    # Inject several sharp drops of varying magnitude
    oi_delta_1h[100] = -10.0
    oi_delta_1h[500] = -5.0
    oi_delta_1h[1500] = -8.0
    
    rv_96 = rng.uniform(0.001, 0.002, n)
    # Inject vol spikes
    rv_96[100] = 0.01
    rv_96[500] = 0.005
    rv_96[1500] = 0.008
    
    close_ser = pd.Series(close)
    df = pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=n, freq="5min", tz="UTC"),
        "close": close_ser,
        "oi_delta_1h": oi_delta_1h,
        "rv_96": rv_96,
        "open": close_ser.shift(1).fillna(close_ser[0]),
        "high": close_ser * 1.001,
        "low": close_ser * 0.999,
        "volume": 1000.0
    })
    return df

def test_deleveraging_wave_default_is_tight():
    df = create_mock_data()
    detector = DeleveragingWaveDetector()
    events = detector.detect(df, symbol="BTCUSDT")
    
    # Assert fewer than 3 events on this mock data.
    # The shock at 500 should be filtered out by tighter quantiles.
    assert len(events) <= 2

def test_trend_acceleration_default_is_tight():
    df = create_mock_data()
    detector = TrendAccelerationDetector()
    events = detector.detect(df, symbol="BTCUSDT")
    
    # Assert fewer than 5 events on 2000 bars.
    assert len(events) <= 5

def test_false_breakout_distance_filtering():
    from project.events.detectors.trend import FalseBreakoutDetector
    
    # Create data with an 11bps breakout and a 50bps breakout
    n = 200
    close = np.full(n, 100.0)
    
    close[49] = 100.11 # 11bps breakout
    close[50] = 100.00 # Back in
    
    close[150] = 100.50 # 50bps breakout
    close[151] = 100.00 # Back in
    
    df = pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=n, freq="5min", tz="UTC"),
        "close": pd.Series(close)
    })
    
    detector = FalseBreakoutDetector()
    # With default min_breakout_distance = 0.0025 (25bps), it should IGNORE the 11bps breakout
    # and ONLY detect the 50bps one.
    events = detector.detect(df, symbol="BTCUSDT", trend_window=40)
    
    assert len(events) == 1
    # Check detected_ts instead of timestamp because timestamp is signal_ts (next bar)
    assert events["detected_ts"].iloc[0] == df["timestamp"].iloc[151]


def test_proxy_detectors_fail_closed_when_depth_columns_are_missing():
    df = pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=32, freq="5min", tz="UTC"),
        "close": 100.0,
        "high": 100.1,
        "low": 99.9,
    })

    with pytest.raises(ValueError, match="ABSORPTION_PROXY requires columns"):
        AbsorptionProxyDetector().detect(df, symbol="BTCUSDT")

    with pytest.raises(ValueError, match="DEPTH_STRESS_PROXY requires columns"):
        DepthStressProxyDetector().detect(df, symbol="BTCUSDT")


def test_funding_flip_requires_meaningful_persistent_sign_change():
    n = 400
    funding = np.full(n, 0.0006, dtype=float)

    # Tiny oscillations around zero should not count as real flips.
    funding[290:294] = [0.00005, -0.00005, 0.00005, -0.00005]

    # One persistent and meaningful flip should count.
    funding[320:324] = [-0.0008, -0.0009, -0.00085, -0.00082]

    df = pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=n, freq="5min", tz="UTC"),
        "funding_rate_scaled": funding,
    })

    events = FundingFlipDetector().detect(df, symbol="BTCUSDT")

    assert len(events) == 1


def test_trend_exhaustion_default_is_tighter():
    df = create_mock_data()
    events = TrendExhaustionDetector().detect(df, symbol="BTCUSDT")

    assert len(events) <= 3


def test_momentum_divergence_default_is_tighter():
    df = create_mock_data()
    events = MomentumDivergenceDetector().detect(df, symbol="BTCUSDT")

    assert len(events) <= 2


def test_price_vol_imbalance_proxy_default_is_tighter():
    rng = np.random.default_rng(11)
    n = 2000
    close = pd.Series(100 * np.exp(np.cumsum(rng.normal(0, 0.0015, n))))
    rv_96 = pd.Series(rng.uniform(0.001, 0.003, n))
    volume = pd.Series(rng.uniform(800, 1200, n))

    close.iloc[1200:1204] *= [1.0, 1.015, 1.018, 1.017]
    rv_96.iloc[1200:1204] = [0.008, 0.009, 0.010, 0.009]
    volume.iloc[1200:1204] = [2500.0, 3200.0, 3600.0, 3000.0]

    df = pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=n, freq="5min", tz="UTC"),
        "close": close,
        "high": close * 1.001,
        "low": close * 0.999,
        "rv_96": rv_96,
        "volume": volume,
    })

    events = PriceVolImbalanceProxyDetector().detect(df, symbol="BTCUSDT")

    assert len(events) <= 2


def test_spread_regime_widening_requires_friction_not_just_spread():
    rng = np.random.default_rng(13)
    n = 2000
    spread_zscore = pd.Series(rng.normal(0.5, 0.3, n)).abs()
    volume = pd.Series(rng.uniform(900, 1200, n))

    spread_zscore.iloc[1500:1510] = np.linspace(2.5, 4.0, 10)
    volume.iloc[1500:1510] = np.linspace(500, 300, 10)

    df = pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=n, freq="5min", tz="UTC"),
        "volume": volume,
        "spread_zscore": spread_zscore,
    })

    events = SpreadRegimeWideningDetector().detect(df, symbol="BTCUSDT")

    assert len(events) <= 4


def test_funding_persistence_preserves_sign_and_subtype():
    n = 500
    funding_rate_scaled = np.full(n, 0.0003, dtype=float)
    funding_abs_pct = np.full(n, 10.0, dtype=float)
    funding_abs = np.full(n, 0.0003, dtype=float)
    funding_rate_scaled[320:333] = -0.0016
    funding_abs_pct[320:333] = 97.0
    funding_abs[320:333] = 0.0016

    df = pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=n, freq="5min", tz="UTC"),
        "funding_rate_scaled": funding_rate_scaled,
        "funding_abs_pct": funding_abs_pct,
        "funding_abs": funding_abs,
    })

    events = FundingPersistenceDetector().detect(df, symbol="BTCUSDT", persistence_pct=85.0, persistence_bars=8)

    assert not events.empty
    assert set(events["direction"]) == {"down"}
    assert "funding_subtype" in events.columns
    assert set(events["funding_subtype"]).issubset({"acceleration", "persistence"})
    assert (events["fr_sign"] == -1.0).all()


def test_funding_normalization_preserves_source_sign_and_semantic_intensity():
    n = 420
    funding_rate_scaled = np.full(n, 0.0002, dtype=float)
    funding_abs_pct = np.full(n, 20.0, dtype=float)
    funding_abs = np.full(n, 0.0002, dtype=float)
    funding_rate_scaled[260:320] = 0.0015
    funding_abs_pct[260:320] = 97.0
    funding_abs[260:320] = 0.0015
    funding_rate_scaled[320:] = 0.00025
    funding_abs_pct[320:] = 25.0
    funding_abs[320:] = 0.00025

    df = pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=n, freq="5min", tz="UTC"),
        "funding_rate_scaled": funding_rate_scaled,
        "funding_abs_pct": funding_abs_pct,
        "funding_abs": funding_abs,
    })

    events = FundingNormalizationDetector().detect(
        df,
        symbol="BTCUSDT",
        extreme_pct=95.0,
        normalization_pct=50.0,
        normalization_lookback=96,
    )

    assert not events.empty
    assert set(events["direction"]) == {"up"}
    assert set(events["funding_subtype"]) == {"normalization"}
    assert (events["prior_extreme_pct"] >= 95.0).all()
    assert (events["evt_signal_intensity"] > 0.0).all()


def test_support_resistance_break_is_implemented():
    n = 420
    close = np.full(n, 100.0, dtype=float)
    close[:360] += np.linspace(0.0, 1.0, 360)
    close[360:] = np.linspace(101.0, 106.0, n - 360)
    df = pd.DataFrame({
        "timestamp": pd.date_range("2024-01-01", periods=n, freq="5min", tz="UTC"),
        "close": close,
    })

    events = SREventDetector().detect(df, symbol="BTCUSDT", trend_window=96, breakout_z_threshold=1.0)

    assert not events.empty
    assert set(events["direction"]) == {"up"}
    assert (events["evt_signal_intensity"] > 0.0).all()


def test_detector_policy_sets_are_explicit():
    assert "SUPPORT_RESISTANCE_BREAK" in LIVE_SAFE_EVENT_TYPES
    assert "FUNDING_FLIP" in RETROSPECTIVE_EVENT_TYPES
    assert is_legacy_event_type("BASIS_SNAPBACK")
