from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field, field_validator


class LiveTradeContext(BaseModel):
    model_config = ConfigDict(frozen=True)

    timestamp: str = Field(min_length=1)
    symbol: str = Field(min_length=1)
    timeframe: str = Field(min_length=1)
    event_family: str = Field(min_length=1)
    event_side: str = Field(min_length=1)
    live_features: Dict[str, Any] = Field(default_factory=dict)
    regime_snapshot: Dict[str, Any] = Field(default_factory=dict)
    execution_env: Dict[str, Any] = Field(default_factory=dict)
    portfolio_state: Dict[str, Any] = Field(default_factory=dict)
    active_event_families: List[str] = Field(default_factory=list)
    active_episode_ids: List[str] = Field(default_factory=list)
    contradiction_event_families: List[str] = Field(default_factory=list)
    episode_snapshot: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("timestamp", "symbol", "timeframe", "event_family", "event_side")
    @classmethod
    def _validate_non_empty(cls, value: str) -> str:
        token = str(value).strip()
        if not token:
            raise ValueError("field must be non-empty")
        return token
