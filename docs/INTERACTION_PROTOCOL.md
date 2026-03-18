# Interaction Protocol

## Role

The agent interacts with three things:

- the operator
- repository artifacts
- prior memory

The operator supplies goals and constraints.
Artifacts supply the current source of truth.
Memory supplies prior lessons and prior failure boundaries.

## Communication Rules

The agent should always make the following clear:

- the working objective
- the immediate next action
- important assumptions
- abnormal findings
- why the next step is justified

Never hide uncertainty.

If a run is:

- partial
- replayed
- manually reconciled
- generated from synthetic data

say so explicitly.

## Default Interaction Pattern

1. restate the objective
2. inspect local evidence
3. narrow the request into repo-native terms
4. run the smallest informative action
5. summarize findings and the next decision

## Artifact-First Rule

Artifacts are the primary source of truth.

Read in this order:

1. top-level run manifest
2. stage manifests
3. stage logs
4. report artifacts
5. generated diagnostics

If those sources disagree, the disagreement is itself a finding.

## Memory Use

Before proposing a materially similar run, retrieve memory for:

- the same event or trigger
- the same template
- the same symbol
- the same context
- the same fail gate

If memory shows repeated failure with no material new condition:

- explain what is different now
- or do not rerun

## Operator Escalation

Ask the operator for input only when:

- the decision changes risk materially
- a destructive action is required
- the repo evidence is insufficient to make a defensible choice

Otherwise, prefer making the best evidence-backed choice and proceeding.

## Run Summary Contract

After each meaningful run, summarize:

- what was run
- what passed
- what failed
- what is suspicious
- what the next best move is

The operator should not need to reconstruct the decision from raw logs.

## Synthetic Interaction Rules

When synthetic data is involved, state:

- the active profile
- the truth-validation status
- whether the conclusion is about detector recovery, pipeline mechanics, or synthetic profitability only

Do not present synthetic profitability as live-market evidence.
