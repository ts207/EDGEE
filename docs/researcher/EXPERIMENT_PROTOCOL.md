# Experiment Protocol

## What a good experiment specifies

- one clear hypothesis family,
- one template shape,
- one direction,
- one horizon,
- one entry-lag policy,
- one context policy,
- and one evaluation target.

## Scope rules

Start narrow.

Broaden only when the current result is interpretable and the memory says to expand.

## Batch design

Prefer batches that are comparable within the same family or the same frontier slice.

Do not mix unrelated surfaces unless the run is explicitly a breadth scan.

## Planning rule

A proposal is not ready until it can be validated without hidden assumptions.

If the controller or validator cannot infer what the proposal means, the experiment is not yet specified enough.

## Execution order

1. Read memory
2. Build proposal
3. Validate plan
4. Execute
5. Evaluate
6. Write back

## Evaluation checklist

- Was the run mechanically valid?
- Was the sample size sufficient?
- Was OOS actually evaluated?
- Did any regime stand out?
- Did stress and placebo checks change the conclusion?
- Is the candidate redundant with prior promoted work?

## Stop rules

Stop a branch when:

- the region is repeatedly blocked for valid reasons,
- the result is too sample-poor to trust,
- or the next action is repair rather than expansion.

## Promotion discipline

Promotion should follow evidence, not excitement.

A result that passes promotion should still be explainable in the artifact trail.

## Synthetic discipline

Use synthetic runs for calibration and truth checks.

Do not use them as a substitute for market evidence.
