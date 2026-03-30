from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Mapping

from project.core.coercion import safe_float


@dataclass(frozen=True)
class DetectedEvent:
    event_family: str
    event_side: str
    features: Dict[str, Any]


def detect_live_event(
    *,
    symbol: str,
    timeframe: str,
    current_close: float,
    previous_close: float | None,
    volume: float | None = None,
    supported_event_families: List[str] | None = None,
    detector_config: Mapping[str, Any] | None = None,
) -> DetectedEvent | None:
    supported = {str(item).strip().upper() for item in list(supported_event_families or []) if str(item).strip()}
    if supported and "VOL_SHOCK" not in supported:
        return None
    if previous_close is None or previous_close <= 0.0:
        return None

    config = dict(detector_config or {})
    move_bps = ((float(current_close) / float(previous_close)) - 1.0) * 10_000.0
    min_abs_move_bps = float(config.get("vol_shock_min_abs_move_bps", 35.0) or 35.0)
    if abs(move_bps) < min_abs_move_bps:
        return None

    event_side = "long" if move_bps > 0.0 else "short"
    return DetectedEvent(
        event_family="VOL_SHOCK",
        event_side=event_side,
        features={
            "symbol": str(symbol).upper(),
            "timeframe": str(timeframe),
            "move_bps": float(move_bps),
            "volume": safe_float(volume, 0.0),
        },
    )
