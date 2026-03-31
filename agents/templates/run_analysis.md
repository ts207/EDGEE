# Run Analysis Template

Use this template to structure a complete analysis cycle for a finished run.

## 1. Run Identity

| Field | Value |
|-------|-------|
| run_id | |
| program_id | |
| proposal_path | |
| date_analyzed | |

## 2. Analyst Phase

### Invoke Analyst

```
Agent prompt:
  Read agents/analyst.md.
  Analyze run <run_id> for program <program_id>.
  Proposal: <path>
  [paste gathered artifacts]
```

### Analyst Report

<paste analyst report here>

### Coordinator Review of Analyst Report
- Pipeline healthy? yes/no
- Candidates found? yes/no
- If empty, upstream cause identified? yes/no
- Primary rejection mechanism: <gate>
- Recommendation: keep / modify / kill

## 3. Mechanism Hypothesis Phase

(Skip if analyst recommends kill)

### Invoke Mechanism Hypothesis

```
Agent prompt:
  Read agents/mechanism_hypothesis.md.
  Analyst report: [paste]
  Original proposal: [paste]
```

### Mechanism Hypotheses

<paste hypotheses here>

### Coordinator Scope Drift Check
- [ ] Events in canonical registry
- [ ] Templates valid for event family
- [ ] Horizons supported
- [ ] Regime unchanged or narrower
- [ ] No symbol/date expansion
- [ ] Direction justified

## 4. Compiler Phase

### Invoke Compiler (per hypothesis)

```
Agent prompt:
  Read agents/compiler.md.
  Hypothesis: [paste one hypothesis]
  Program ID: <program_id>
  Suggested run ID: <run_id>
```

### Compiled Proposals

<paste compiled outputs here>

## 5. Execution Phase

### Pre-Execution
- [ ] Translation command succeeded
- [ ] Plan-only command succeeded
- [ ] Plan review checklist passed
- [ ] User approved execution

### Execution
- Run ID: <new_run_id>
- Command: <execution command>
- Status: pending / running / completed / failed

## 6. Decision

| Field | Value |
|-------|-------|
| Decision | keep / modify / kill |
| Evidence strength | weak / moderate / strong |
| Next action | |
| Stop condition | |
