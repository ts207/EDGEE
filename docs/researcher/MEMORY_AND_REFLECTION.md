# Memory and Reflection

## Purpose

Memory is how the research loop compounds across runs.

It stores what happened, what failed, what looked promising, and what should be tried next.

## Memory classes

### Structural memory
Facts about the system and its supported surfaces.

### Experimental memory
What happened in prior runs, including outcomes and conditions.

### Negative memory
Regions or combinations that should not be retried blindly.

### Action memory
Repairs, adjacent explorations, exploit follow-ups, and holds.

## Reflection schema

A useful reflection should capture:

- mechanical outcome,
- statistical outcome,
- confidence,
- failure class,
- sample size,
- and the recommended next action.

## What should be written back

At minimum, the loop should preserve:

- reflections,
- belief state,
- tested regions,
- next-action queues,
- and any supersession tracking for repaired failures.

## Retrieval rule

The controller should read memory before proposing new work.

If the memory says to repair a broken pipeline, that takes priority over frontier expansion.

## What older docs missed

The code already supports more than a simple pass/fail memory model.

The missing documentation gap is not whether memory exists. The gap is how the controller is supposed to consume it.

## Related code

- `project/research/knowledge/memory.py`
- `project/research/knowledge/reflection.py`
- `project/pipelines/research/update_campaign_memory.py`
- `project/pipelines/research/campaign_controller.py`
