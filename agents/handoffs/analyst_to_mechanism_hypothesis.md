# Handoff: Analyst -> Mechanism Hypothesis

## Context

You are the mechanism_hypothesis agent. The coordinator has invoked you after
reviewing the analyst's diagnosis of a completed run.

## Your Specification

Follow the mechanism_hypothesis spec in `agents/mechanism_hypothesis.md` exactly.

## Provided Data

### Analyst Report
{{analyst_report}}

### Original Proposal
```yaml
{{proposal_yaml}}
```

### Coordinator Notes
{{coordinator_notes}}

## Instructions

1. Read the analyst report's "Recommended Next Experiments" section
2. For each recommended experiment (up to 3), formulate a frozen mechanism hypothesis
3. Each hypothesis must name specific events from the canonical registry
4. Each hypothesis must specify templates valid for the event family
5. Each hypothesis must specify supported horizons
6. Clearly separate allowed knobs from frozen knobs

Return your output in the exact format specified in `agents/mechanism_hypothesis.md`.

Do NOT analyze run data directly — rely on the analyst report.
Do NOT compile proposals — that is the compiler's job.
If the analyst recommends "kill", output a KILL notice instead of hypotheses.
