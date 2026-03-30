from __future__ import annotations

from typing import Any, Dict, List, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ThesisEvidence(BaseModel):
    model_config = ConfigDict(frozen=True)

    sample_size: int = Field(ge=0)
    validation_samples: int = Field(default=0, ge=0)
    test_samples: int = Field(default=0, ge=0)
    estimate_bps: float | None = None
    net_expectancy_bps: float | None = None
    q_value: float | None = None
    stability_score: float | None = None
    cost_survival_ratio: float | None = None
    tob_coverage: float | None = None
    rank_score: float | None = None
    promotion_track: str = ""
    policy_version: str = ""
    bundle_version: str = ""


class ThesisLineage(BaseModel):
    model_config = ConfigDict(frozen=True)

    run_id: str = Field(min_length=1)
    candidate_id: str = Field(min_length=1)
    hypothesis_id: str = ""
    plan_row_id: str = ""
    blueprint_id: str = ""
    proposal_id: str = ""


class PromotedThesis(BaseModel):
    model_config = ConfigDict(frozen=True)

    thesis_id: str = Field(min_length=1)
    status: Literal["pending_blueprint", "active", "paused", "retired"] = "pending_blueprint"
    symbol_scope: Dict[str, Any] = Field(default_factory=dict)
    timeframe: str = Field(min_length=1)
    event_family: str = Field(min_length=1)
    event_side: Literal["long", "short", "both", "conditional", "unknown"] = "unknown"
    required_context: Dict[str, Any] = Field(default_factory=dict)
    supportive_context: Dict[str, Any] = Field(default_factory=dict)
    expected_response: Dict[str, Any] = Field(default_factory=dict)
    invalidation: Dict[str, Any] = Field(default_factory=dict)
    risk_notes: List[str] = Field(default_factory=list)
    evidence: ThesisEvidence
    lineage: ThesisLineage

    @field_validator("thesis_id", "timeframe", "event_family")
    @classmethod
    def _validate_non_empty(cls, value: str) -> str:
        if not str(value).strip():
            raise ValueError("field must be non-empty")
        return str(value).strip()
