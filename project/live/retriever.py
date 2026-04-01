from __future__ import annotations

from dataclasses import dataclass
from typing import List

from project.live.contracts import PromotedThesis
from project.live.contracts.live_trade_context import LiveTradeContext
from project.live.thesis_store import ThesisStore
from project.research.meta_ranking import thesis_meta_quality_score


@dataclass(frozen=True)
class ThesisMatch:
    thesis: PromotedThesis
    eligibility_passed: bool
    support_score: float
    contradiction_penalty: float
    reasons_for: list[str]
    reasons_against: list[str]


def _context_events(context: LiveTradeContext) -> set[str]:
    out = {str(context.event_family).strip().upper()}
    out.update(str(item).strip().upper() for item in context.active_event_families if str(item).strip())
    return {item for item in out if item}


def _context_episodes(context: LiveTradeContext) -> set[str]:
    out = set(str(item).strip().upper() for item in context.active_episode_ids if str(item).strip())
    snapshot = context.episode_snapshot or {}
    out.update(str(item).strip().upper() for item in snapshot.get("episode_ids", []) if str(item).strip())
    return {item for item in out if item}


def _context_contradictions(context: LiveTradeContext) -> set[str]:
    return {
        str(item).strip().upper()
        for item in context.contradiction_event_families
        if str(item).strip()
    }


def _evaluate_invalidation(thesis: PromotedThesis, context: LiveTradeContext) -> bool:
    invalidation = thesis.invalidation or {}
    metric = str(invalidation.get("metric", "")).strip()
    operator = str(invalidation.get("operator", "")).strip()
    value = invalidation.get("value")
    if not metric or not operator:
        return False
    current = None
    if metric in context.live_features:
        current = context.live_features.get(metric)
    elif metric in context.regime_snapshot:
        current = context.regime_snapshot.get(metric)
    if current is None or value is None:
        return False
    try:
        left = float(current)
        right = float(value)
    except (TypeError, ValueError):
        return False
    if operator == ">":
        return left > right
    if operator == ">=":
        return left >= right
    if operator == "<":
        return left < right
    if operator == "<=":
        return left <= right
    return False


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
    candidates = thesis_store.filter(symbol=context.symbol, timeframe=context.timeframe)
    context_events = _context_events(context)
    context_episodes = _context_episodes(context)
    contradiction_events = _context_contradictions(context)
    current_regime = str((context.regime_snapshot or {}).get("canonical_regime", "")).strip().upper()

    results: list[ThesisMatch] = []
    for thesis in candidates:
        if thesis.status == "pending_blueprint" and not include_pending:
            continue
        if thesis.status in {"paused", "retired"}:
            continue

        reasons_for: list[str] = []
        reasons_against: list[str] = []
        support_score = 0.10
        contradiction_penalty = 0.0
        eligibility_passed = True

        governance_declared = any(
            [
                str(thesis.governance.tier).strip(),
                str(thesis.governance.operational_role).strip(),
                str(thesis.governance.deployment_disposition).strip(),
                str(thesis.governance.evidence_mode).strip(),
            ]
        )
        if governance_declared and not bool(thesis.governance.trade_trigger_eligible):
            reasons_against.append("thesis_not_trade_trigger_eligible")
            eligibility_passed = False

        requirements = thesis.requirements
        trigger_events = {str(item).strip().upper() for item in requirements.trigger_events if str(item).strip()}
        confirmation_events = {str(item).strip().upper() for item in requirements.confirmation_events if str(item).strip()}
        required_episodes = {str(item).strip().upper() for item in requirements.required_episodes if str(item).strip()}
        disallowed_regimes = {str(item).strip().upper() for item in requirements.disallowed_regimes if str(item).strip()}

        thesis_event_family = str(thesis.event_family).strip().upper()
        if thesis_event_family in context_events:
            support_score += 0.25
            reasons_for.append(f"event_family_match:{thesis_event_family}")
        elif trigger_events.intersection(context_events):
            support_score += 0.20
            reasons_for.append(f"trigger_event_match:{','.join(sorted(trigger_events.intersection(context_events)))}")
        else:
            reasons_against.append("no_trigger_event_match")
            eligibility_passed = False

        if trigger_events:
            matched_triggers = trigger_events.intersection(context_events)
            if not matched_triggers:
                reasons_against.append("required_trigger_missing")
                eligibility_passed = False
            else:
                support_score += min(0.10, 0.05 * len(matched_triggers))

        if confirmation_events:
            matched_confirmations = confirmation_events.intersection(context_events)
            if matched_confirmations:
                support_score += min(0.10, 0.05 * len(matched_confirmations))
                reasons_for.append(f"confirmation_match:{','.join(sorted(matched_confirmations))}")
            else:
                contradiction_penalty += 0.10
                reasons_against.append(f"confirmation_missing:{','.join(sorted(confirmation_events))}")

        if required_episodes:
            matched_episodes = required_episodes.intersection(context_episodes)
            if not matched_episodes:
                reasons_against.append(f"required_episode_missing:{','.join(sorted(required_episodes))}")
                eligibility_passed = False
            else:
                support_score += min(0.15, 0.08 * len(matched_episodes))
                reasons_for.append(f"episode_match:{','.join(sorted(matched_episodes))}")

        if current_regime and current_regime in disallowed_regimes:
            reasons_against.append(f"regime_disallowed:{current_regime}")
            eligibility_passed = False

        contradiction_overlap = contradiction_events.intersection(trigger_events | confirmation_events | {thesis_event_family})
        if contradiction_overlap:
            contradiction_penalty += 0.25
            reasons_against.append(f"contradiction_event:{','.join(sorted(contradiction_overlap))}")

        if _evaluate_invalidation(thesis, context):
            contradiction_penalty += 0.60
            reasons_against.append("invalidation_triggered")
            eligibility_passed = False

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

        meta_quality = thesis_meta_quality_score(thesis)
        if meta_quality > 0.0:
            support_score += min(0.10, 0.10 * float(meta_quality))
            reasons_for.append(f"meta_quality:{meta_quality:.2f}")

        results.append(
            ThesisMatch(
                thesis=thesis,
                eligibility_passed=eligibility_passed,
                support_score=min(1.0, max(0.0, support_score)),
                contradiction_penalty=min(1.0, max(0.0, contradiction_penalty)),
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
