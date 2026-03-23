# Research Loop

This is the operational loop for one campaign cycle.

## 1. Observe

Load the current artifact state, market context, and prior campaign memory.

Inputs typically come from:

- cleaned bars,
- features,
- context labels,
- regime labels,
- prior reflections,
- tested regions,
- and next-action queues.

## 2. Retrieve memory

Before proposing new work, read the most recent:

- reflection,
- belief state,
- avoid list,
- promising regions,
- open repairs,
- and queued next actions.

This prevents the controller from behaving like a blind frontier popper.

## 3. Define the objective

Choose one of three operating modes:

- `scan` for breadth within the allowed frontier,
- `explore` for adjacent variation and family expansion,
- `exploit` for follow-up on a promising region.

The mode should match what the memory says, not what is easiest to enumerate.

## 4. Propose

A proposal must be fully specified and plan-ready.

That means it should define:

- symbol scope,
- event or trigger family,
- template,
- direction,
- horizon,
- entry lag,
- and context.

## 5. Plan

The plan step should catch contract failures early.

If a proposal is invalid at plan time, do not push it downstream and hope evaluation will sort it out.

## 6. Execute

Run the approved experiment and keep the run id stable across produced artifacts.

## 7. Evaluate

Review:

- mechanical failures,
- sample size,
- regime behavior,
- stress and placebo results,
- promotion readiness,
- and any clustering or deduplication signals.

## 8. Write back

Update memory, reflections, belief state, and next-action queues.

The next run should be conditioned on what happened in this one.

## Where this loop lives in code

- `project/pipelines/research/campaign_controller.py`
- `project/pipelines/research/update_campaign_memory.py`
- `project/pipelines/research/search_intelligence.py`
- `project/research/knowledge/`
- `project/research/services/`
