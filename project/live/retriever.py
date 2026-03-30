from __future__ import annotations

from dataclasses import dataclass
from typing import List

from project.live.contracts import PromotedThesis
from project.live.contracts.live_trade_context import LiveTradeContext
from project.live.thesis_store import ThesisStore


@dataclass(frozen=True)
class ThesisMatch:
    thesis: PromotedThesis
    eligibility_passed: bool
    support_score: float
    contradiction_penalty: float
    reasons_for: list[str]
    reasons_against: list[str]


def _score_supportive_context(thesis: PromotedThesis, context: LiveTradeContext) -> tuple[float, list[str], list[str]]:
    reasons_for: list[str] = []
    reasons_against: list[str] = []
    score = 0.0
    support = thesis.supportive_context or {}
    regime = context.regime_snapshot or {}

    canonical_regime = str(support.get("canonical_regime", "")).strip().upper()
    current_regime = str(regime.get("canonical_regime", "")).strip().upper()
    if canonical_regime:
        if canonical_regime == current_regime:
            score += 0.15
            reasons_for.append(f"regime_match:{canonical_regime}")
        else:
            reasons_against.append(f"regime_mismatch:{canonical_regime}->{current_regime or 'unknown'}")

    bridge_certified = bool(support.get("bridge_certified", False))
    if bridge_certified:
        score += 0.05
        reasons_for.append("bridge_certified")

    if bool(support.get("has_realized_oos_path", False)):
        score += 0.05
        reasons_for.append("realized_oos_path")
    else:
        reasons_against.append("limited_realized_oos_path")

    return score, reasons_for, reasons_against


def retrieve_ranked_theses(
    *,
    thesis_store: ThesisStore,
    context: LiveTradeContext,
    include_pending: bool = True,
    limit: int = 5,
) -> List[ThesisMatch]:
    candidates = thesis_store.filter(
        symbol=context.symbol,
        timeframe=context.timeframe,
        event_family=context.event_family,
    )
    results: list[ThesisMatch] = []
    for thesis in candidates:
        if thesis.status == "pending_blueprint" and not include_pending:
            continue
        if thesis.status in {"paused", "retired"}:
            continue
        reasons_for = ["exact_symbol_timeframe_event_match"]
        reasons_against: list[str] = []
        support_score = 0.45
        contradiction_penalty = 0.0

        required = thesis.required_context or {}
        required_event_type = str(required.get("event_type", "")).strip().upper()
        if required_event_type and required_event_type != context.event_family.strip().upper():
            reasons_against.append("required_event_type_mismatch")
            results.append(
                ThesisMatch(
                    thesis=thesis,
                    eligibility_passed=False,
                    support_score=0.0,
                    contradiction_penalty=1.0,
                    reasons_for=[],
                    reasons_against=reasons_against,
                )
            )
            continue

        if thesis.event_side != "unknown" and thesis.event_side not in {"both", "conditional"}:
            if thesis.event_side == context.event_side:
                support_score += 0.10
                reasons_for.append(f"event_side_match:{context.event_side}")
            else:
                contradiction_penalty += 0.20
                reasons_against.append(
                    f"event_side_mismatch:{thesis.event_side}->{context.event_side}"
                )

        extra_score, extra_for, extra_against = _score_supportive_context(thesis, context)
        support_score += extra_score
        reasons_for.extend(extra_for)
        reasons_against.extend(extra_against)

        if thesis.status == "active":
            support_score += 0.10
            reasons_for.append("blueprint_invalidation_available")
        elif thesis.status == "pending_blueprint":
            contradiction_penalty += 0.05
            reasons_against.append("pending_blueprint")

        results.append(
            ThesisMatch(
                thesis=thesis,
                eligibility_passed=True,
                support_score=min(1.0, support_score),
                contradiction_penalty=min(1.0, contradiction_penalty),
                reasons_for=reasons_for,
                reasons_against=reasons_against,
            )
        )

    results.sort(
        key=lambda match: (
            int(match.eligibility_passed),
            match.support_score - match.contradiction_penalty,
            match.thesis.evidence.sample_size,
        ),
        reverse=True,
    )
    return results[: max(1, int(limit))]
