# Operations And Guardrails

## Operating Priorities

Optimize in this order:

1. correctness
2. comparability
3. narrow attribution
4. operational cleanliness
5. iteration speed

## Scope Rules

- use targeted stage execution for repair verification
- use narrow search specs for isolated hypothesis testing
- use full runs only after recent path stability is confirmed
- do not broaden immediately after a mechanical fix

## Safety Rules

- do not overwrite broad production artifacts when a narrow output path will do
- do not treat a repaired tail replay as equivalent to the original full DAG run
- do not call warning-heavy output clean without inspection
- do not interpret synthetic profitability as live-market proof

## Logging Rules

Warnings should help triage, not flood the operator.

The agent should:

- suppress low-signal coercion noise where safe
- preserve warnings that indicate real contract or data issues
- call out stale or contradictory logs explicitly

## Promotion Guardrails

Promotion is conservative by design.

Do not bypass:

- multiplicity controls
- cost-survival checks
- validation and test sample requirements
- confirmatory locking rules
- retail and capital viability filters

## Memory Guardrails

Memory should guide action without hard-coding bias.

Still allow:

- materially different contexts
- repaired code paths
- cleaner reruns that invalidate old conclusions

## Review Checklist

When a run looks abnormal, inspect:

- manifests
- logs
- row counts across artifact boundaries
- duplicate hypotheses
- stale replay traces
- missing split metadata
- generated diagnostics when the issue may be architectural

## Operationally Clean End State

A run is operationally clean when:

- stage and top-level manifests agree
- downstream artifacts are populated as expected
- warning noise is controlled
- the next action is obvious from the evidence

## Synthetic Guardrails

- freeze `volatility_profile`, symbol set, and time window before review
- prefer cross-profile survival over single-profile maximization
- rerun truth validation after detector or generator edits
- treat short certification windows as detector-and-pipeline calibration unless holdout support exists
- do not keep tuning directly against one synthetic world
