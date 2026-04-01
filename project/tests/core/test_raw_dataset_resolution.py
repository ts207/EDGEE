from __future__ import annotations

from project.io.utils import raw_dataset_dir_candidates


def test_raw_dataset_dir_candidates_include_vendorless_fallback(tmp_path) -> None:
    candidates = raw_dataset_dir_candidates(
        tmp_path,
        market="perp",
        symbol="BTCUSDT",
        dataset="ohlcv_5m",
        run_id="run123",
    )
    rendered = [str(path) for path in candidates]
    assert rendered[0].endswith("lake/runs/run123/raw/binance/perp/BTCUSDT/ohlcv_5m")
    assert rendered[1].endswith("lake/raw/binance/perp/BTCUSDT/ohlcv_5m")
    assert rendered[2].endswith("lake/runs/run123/raw/perp/BTCUSDT/ohlcv_5m")
    assert rendered[3].endswith("lake/raw/perp/BTCUSDT/ohlcv_5m")
