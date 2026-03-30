from __future__ import annotations

from typing import Any, Dict, Mapping

from project.live.contracts.live_trade_context import LiveTradeContext
from project.live.event_detector import DetectedEvent


def _canonical_regime_from_move(move_bps: float) -> str:
    if abs(move_bps) >= 80.0:
        return "VOLATILITY"
    if abs(move_bps) >= 35.0:
        return "TRANSITION"
    return "CALM"


def build_live_trade_context(
    *,
    timestamp: str,
    symbol: str,
    timeframe: str,
    detected_event: DetectedEvent,
    market_features: Mapping[str, Any],
    portfolio_state: Mapping[str, Any],
    execution_env: Mapping[str, Any],
) -> LiveTradeContext:
    move_bps = float(detected_event.features.get("move_bps", 0.0) or 0.0)
    regime_snapshot: Dict[str, Any] = {
        "canonical_regime": _canonical_regime_from_move(move_bps),
        "move_bps": move_bps,
    }
    if "spread_bps" in market_features and float(market_features.get("spread_bps", 0.0) or 0.0) <= 5.0:
        regime_snapshot["microstructure_regime"] = "healthy"
    else:
        regime_snapshot["microstructure_regime"] = "degraded"
    return LiveTradeContext(
        timestamp=str(timestamp),
        symbol=str(symbol).upper(),
        timeframe=str(timeframe),
        event_family=str(detected_event.event_family).upper(),
        event_side=str(detected_event.event_side).lower(),
        live_features=dict(market_features),
        regime_snapshot=regime_snapshot,
        execution_env=dict(execution_env),
        portfolio_state=dict(portfolio_state),
    )
