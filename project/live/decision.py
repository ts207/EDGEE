from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from project.live.contracts.live_trade_context import LiveTradeContext
from project.live.contracts.trade_intent import TradeIntent
from project.live.policy import score_to_action, thresholds_from_config
from project.live.retriever import ThesisMatch, retrieve_ranked_theses
from project.live.scoring import DecisionScore, build_decision_score
from project.live.thesis_store import ThesisStore


@dataclass(frozen=True)
class DecisionOutcome:
    context: LiveTradeContext
    ranked_matches: List[ThesisMatch]
    top_score: DecisionScore | None
    trade_intent: TradeIntent


def decide_trade_intent(
    *,
    context: LiveTradeContext,
    thesis_store: ThesisStore,
    policy_config: Dict[str, Any] | None = None,
    include_pending: bool = True,
) -> DecisionOutcome:
    matches = retrieve_ranked_theses(
        thesis_store=thesis_store,
        context=context,
        include_pending=include_pending,
    )
    if not matches:
        reject = TradeIntent(
            action="reject",
            symbol=context.symbol,
            side="flat",
            thesis_id="",
            support_score=0.0,
            contradiction_penalty=0.0,
            confidence_band="none",
            size_fraction=0.0,
            reasons_for=[],
            reasons_against=["no_matching_thesis"],
        )
        return DecisionOutcome(
            context=context,
            ranked_matches=[],
            top_score=None,
            trade_intent=reject,
        )

    top_match = matches[0]
    score = build_decision_score(top_match, context)
    side = "flat"
    if top_match.thesis.event_side == "long":
        side = "buy"
    elif top_match.thesis.event_side == "short":
        side = "sell"
    elif context.event_side == "long":
        side = "buy"
    elif context.event_side == "short":
        side = "sell"

    intent = score_to_action(
        score=score,
        symbol=context.symbol,
        side=side,
        thesis_id=top_match.thesis.thesis_id,
        invalidation=top_match.thesis.invalidation,
        thresholds=thresholds_from_config(policy_config),
    )
    return DecisionOutcome(
        context=context,
        ranked_matches=matches,
        top_score=score,
        trade_intent=intent,
    )
