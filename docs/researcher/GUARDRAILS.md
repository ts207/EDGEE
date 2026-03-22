# Guardrails

This document defines the operating rules for running research safely and efficiently. These rules exist to prevent expensive, low-trust experimentation.

---

## Operating Priorities

When in doubt, prefer in this order:

1. **Narrow attribution** — know what caused a result before widening
2. **Artifact cleanliness** — reconciled manifests over raw output volume
3. **Post-cost relevance** — expectancy after friction, not before
4. **Reproducibility** — replayable runs over one-off results
5. **Operator clarity** — explicit next actions over vague interpretations

Do not trade any of these away for output volume.

---

## Scope Guardrails

**Default to narrow.** Every dimension you widen costs attribution clarity.

- One event family before many families.
- One template family before many.
- One primary context family before many.
- One objective per run.

Broadening is only justified after the narrow path is mechanically clean and still decision-relevant.

---

## Contract Guardrails

**Do not interpret results when:**

- Manifests and logs disagree.
- Expected artifacts are missing.
- Generated diagnostics disagree with the owning code or registry surface.
- Warning noise is hiding runtime faults.

Repair the path first. A run that exited `0` is not a good run if its artifacts do not reconcile.

---

## Synthetic Guardrails

Synthetic runs are for:
- Detector truth recovery and validation
- Contract and artifact plumbing checks
- Negative-control testing
- Controlled regime stress

They are **not** direct proof of live profitability.

Rules:
- Freeze the generator profile before evaluating outcomes.
- Keep the manifest and truth map with the run.
- Validate truth before interpreting misses.
- Prefer cross-profile survival over one strong synthetic world.
- Treat short windows as calibration unless real holdout support exists.

---

## Promotion Guardrails

Promotion is a hard gate, not a reward for attractive discovery output.

**Only trust a promotion result when:**
- The candidate contract is valid.
- Split support exists (non-zero validation and test).
- Cost and stress quality survive.
- The claim is narrow enough to explain.

If a promotion decision requires you to ignore any of those, stop.

---

## Context Guardrails

Confidence-aware context is the default for production research.

- Hard regime labels exist for compatibility and baseline comparison only.
- Low-confidence or high-entropy regime rows should not be treated as fully trustworthy context.
- Hard-label mode should be used as a comparison baseline, not as the primary research context.

---

## Memory Guardrails

Do not keep rerunning a region because the wording of the question changed.

Before repeating a similar slice, verify that at least one of these changed:
- The event or family
- The template
- The context
- The fail gate
- The code or data it depends on

If nothing material changed, do not rerun by default.

---

## Pre-Run Review Checklist

Before calling a run ready to execute, ask:

- [ ] Is the question explicit and falsifiable?
- [ ] Is the path narrow enough to attribute results?
- [ ] Has memory been checked for prior runs in this region?
- [ ] Is `plan_only` confirming the expected stages?
- [ ] Are the success and failure conditions defined in advance?

---

## Post-Run Review Checklist

Before calling a run meaningful, ask:

- [ ] Do artifacts reconcile?
- [ ] Are split counts real (non-zero validation and test)?
- [ ] Do costs still allow relevance?
- [ ] Is the next action explicit?

---

## Stop Conditions

Stop and reassess when any of these apply:

- A path remains mechanically unstable after a repair attempt.
- A clean rerun still fails on holdout.
- Promotion rejection is clear and has been repeated under the same conditions.
- The next run would only restate the same failed claim.
- The evidence is too weak to justify more scope.
