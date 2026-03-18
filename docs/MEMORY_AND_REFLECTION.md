# Memory And Reflection

## Purpose

Memory stops the agent from:

- repeating failed slices
- forgetting fragile system facts
- overstating weak evidence

Reflection converts one run into reusable decision support for the next run.

## Memory Classes

### Structural Memory

Facts about how the repository behaves.

Examples:

- export requires normalized edge-candidate artifacts
- explicit contexts should not create unconditional duplicates
- top-level manifests may need reconciliation after manual tail replay

### Experimental Memory

Facts about what was tested and what happened.

Examples:

- low-liquidity basis continuation on BTC 15m survived cost in one January slice
- search-engine candidates were once orphaned from promotion

### Negative Memory

Facts about what should be avoided.

Examples:

- broad noisy runs with stale manifests are low-trust
- a region repeatedly fails retail net expectancy despite acceptable raw `q_value`

### Action Memory

Facts about what to do next.

Examples:

- rerun a narrow slice after a generator contract change
- escalate only after validation and test counts survive export

## Reflection Questions

After each meaningful run, answer:

1. what prior belief did this test
2. what evidence increased or decreased that belief
3. was the outcome market-driven or system-driven
4. what reusable rule should be remembered
5. what exact next experiment is justified

## Write Rules

- store facts, not impressions
- include run ids, scope, and failure class
- separate system issues from market conclusions
- record both positive and negative results
- prefer short, high-signal entries over narrative dumps
- reference exact artifact families when that fact will matter later

## Retrieval Heuristics

Before any new experiment, retrieve memory for:

- the same trigger or event family
- the same template
- the same symbol and timeframe
- the same context
- the same fail gate

If prior memory shows repeated failure with no material new condition, do not rerun by default.

## Reinforcement Rules

Increase priority for experiments that:

- resolve a known ambiguity
- build on positive post-cost evidence
- reduce uncertainty with a small run
- validate a recent code-path fix

Decrease priority for experiments that:

- duplicate prior unsuccessful slices
- broaden scope without adding information
- depend on known-broken contracts
- create warning-heavy output without changing the decision

## Reflection Schema

Each reflection should minimally include:

- `objective`
- `run_scope`
- `mechanical_status`
- `statistical_status`
- `primary_findings`
- `primary_failures`
- `belief_update`
- `next_action`

## Memory Hygiene

Downgrade or supersede memories that are:

- invalidated by code changes
- contradicted by cleaner reruns
- too vague to guide future selection

Do not silently delete history when a superseded record would be more informative.

## Synthetic Memory

Synthetic runs should also store:

- generator profile
- noise scale
- truth-map path
- whether the result survived another profile or only one world

If a synthetic result fails to survive a profile change, store it as simulator-specific rather than as a general
market belief.
