# Guardrails

## Operating priorities

1. Correctness
2. Attribution
3. Reproducibility
4. Only then breadth

## Scope guardrails

- Do not broaden a run just because the narrow version failed.
- Do not reuse stale outputs as evidence for a different hypothesis.
- Do not treat a plan-only approval as a success signal.

## Contract guardrails

- Every hypothesis must be fully specified.
- Every evaluation must preserve enough metadata to explain the result.
- Every promotion should distinguish evaluated from not-evaluated conditions.

## Synthetic guardrails

Synthetic workflows calibrate detectors and pipelines.

They do not prove live alpha.

## Promotion guardrails

- Reject ambiguous OOS states.
- Reject fragile results that only survive in narrow, high-dimensional contexts without explicit justification.
- Check overlap with existing promoted strategies before assigning capital.

## Memory guardrails

- High-confidence failures should block.
- Low-confidence mechanical issues should route to repair.
- Don’t let one noisy failure region poison an entire family without cause.

## Shrinkage Persistence

Adaptive shrinkage $\lambda$ estimates are persisted across research sessions to stabilize pooling. To prevent stale estimates from anchoring current research:
1.  **Lambda Decay:** Previous $\lambda$ estimates are discounted by a `lambda_decay_factor` (default 5%) at the start of each session.
2.  **Smoothing:** Decayed estimates are combined with current raw estimates via an exponential moving average (`lambda_smoothing_alpha`).
3.  **Shock Cap:** Updates to $\lambda$ are capped by `lambda_shock_cap_pct` to prevent localized noise from destabilizing the global pooling structure.

## Pre-run checklist

- Proposal fully specified
- Plan validated
- Frontier choice justified
- Memory read completed
- OOS expectation understood

## Post-run checklist

- Reflection written
- Next actions updated
- Belief state updated
- Promotion status checked
- Docs updated if the behavior changed
