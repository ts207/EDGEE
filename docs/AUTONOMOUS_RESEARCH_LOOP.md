# Autonomous Research Loop

## Purpose

The research loop exists to turn market observations into bounded experiments, convert results into reusable
evidence, and decide the next action without drifting outside repository contracts.

This system is not a chat bot with occasional analysis. It is an iterative research worker with:

- explicit objectives
- explicit hypotheses
- bounded execution
- artifact-based evaluation
- memory-backed adaptation

## The Loop

The canonical loop is:

1. observe the current state
2. retrieve relevant memory
3. define the objective
4. generate hypotheses
5. choose the smallest useful batch
6. execute
7. evaluate
8. reflect
9. choose the next action

If the loop does not leave behind a durable decision trail, it did not happen.

## Required Outputs

Every completed loop should leave behind:

- a run or replay artifact set
- an evaluation
- a written reflection
- a next-action decision
- an updated memory record

## Phase Guide

### 1. Observe

Inspect the current local evidence before proposing new work.

Minimum inputs:

- run manifest
- stage manifests
- stage logs
- discovery or promotion summaries
- generated audits when relevant
- prior reflections or memory for the same region

Questions to answer:

- what was run
- what completed
- what failed
- what is still ambiguous
- what was mechanical versus statistical

### 2. Retrieve Memory

Look up prior work before rerunning a similar slice.

Retrieve memory for:

- the same symbol
- the same event or trigger family
- the same template
- the same context
- the same primary failure mode

Bias toward memory-backed iteration, not repeated rediscovery of already-rejected regions.

### 3. Define The Objective

The objective must be explicit and falsifiable.

Good objectives:

- test whether basis-dislocation continuation under low liquidity survives costs
- verify whether a promotion failure came from missing split counts or weak economics
- isolate one regime-conditioned trigger with enough holdout support to justify follow-up

Bad objectives:

- find alpha
- run more experiments
- explore broadly

### 4. Generate Hypotheses

Hypotheses must be stated in repo-native terms:

- trigger or event
- direction
- horizon
- template
- context
- entry lag

Favor hypotheses that are:

- explainable from artifacts
- comparable to prior runs
- narrow enough to falsify
- directly representable by registry and search specs

### 5. Choose The Batch

Default batch logic:

- one exploit slice
- one adjacent exploration slice
- one repair or verification slice if code or contracts changed

Do not mix unrelated objectives in one batch.

Prefer the smallest batch that can answer the actual question.

### 6. Execute

Use repository entrypoints that preserve manifests and downstream contracts.

Preferred order:

- targeted replay for repair verification
- narrow search-engine slice for hypothesis isolation
- full `run_all` only after the path is mechanically stable

### 7. Evaluate

Evaluate on three axes:

- statistical quality
- execution quality
- contract integrity

Statistical quality includes:

- split counts
- `q_value`
- post-cost expectancy
- stressed expectancy
- regime stability

Execution quality includes:

- stage completion
- manifest reconciliation
- warning surface
- absence of stale replay traces

Contract integrity includes:

- required inputs and outputs exist
- fields propagate correctly
- top-level and stage manifests agree

### 8. Reflect

Reflection is mandatory after material runs, fixes, or surprising failures.

Reflection should answer:

- what belief was tested
- what changed in that belief
- what was learned about the market
- what was learned about the system
- what should be tried next
- what should stop

### 9. Choose The Next Action

Every loop must end with exactly one explicit next action:

- exploit
- explore
- repair
- hold
- stop

That choice should come from evidence and memory, not intuition alone.

## Reinforcement Rules

Increase priority for work that consistently leads to:

- reproducible post-cost signal
- validation and test support
- low operational friction
- clear explanatory structure

Decrease priority for work that repeatedly leads to:

- contract breakage
- stale bookkeeping
- duplicated search regions
- high operational cost with weak evidence
- warning-heavy runs that do not change the decision

## Escalation Rules

Escalate from narrow to broad only when:

- the narrow path produced coherent outputs
- the target has enough support to justify broader spend
- the mechanical path is stable

De-escalate to repair mode when:

- manifests and logs disagree
- downstream artifacts are malformed
- split counts are missing or suspect
- warning floods hide the true failure

## Synthetic Branch

Synthetic work uses the same loop, but with extra discipline.

When the active dataset is synthetic:

1. freeze the generator profile and slice before looking at results
2. preserve the generation manifest and truth map with the run
3. validate detector truth before interpreting misses
4. compare across at least one additional profile before strengthening belief
5. separate detector recovery from profitability claims

Synthetic research should optimize for:

- mechanism recovery
- falsification
- contract verification
- promotion robustness

It should not be treated as direct evidence of live profitability.
