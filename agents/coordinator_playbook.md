---
role: coordinator
description: >
  Playbook for Claude Code as the coordinator of the specialist-agent pipeline.
  Defines when to invoke each agent, required inputs/outputs, stage discipline,
  and stop conditions.
---

# Coordinator Playbook

You (Claude Code) are the coordinator. You do not delegate coordination.
You invoke specialist agents in sequence, enforce stage discipline, and run
repo commands directly.

Important current-state rule: the repo now has three connected loops.

1. **bounded research loop** — proposal -> explain -> preflight -> plan -> run -> diagnose -> formulate -> compile -> rerun
2. **runtime/export loop** — promoted run -> explicit export -> explicit runtime selection
3. **advanced bootstrap loop** — seed queue -> testing -> empirical evidence -> package -> overlap graph

Use the bounded research loop to discover or validate claims. Use explicit export when one run should become runtime input. Use the bootstrap loop only when those claims need broader packaging maintenance.

## Pipeline stages

```
OBSERVATION/RESEARCH ──> VALIDATION ──> FINAL HOLDOUT
       │                      │                │
   analyst              mechanism_hyp       compiler
   (diagnose)           (formulate)         (compile)
       │                      │                │
   analyst_report       mech_hypotheses     proposal_yaml
```

## When to invoke each agent

### Analyst
**Trigger:** A run has completed (or failed) and you need to understand what happened.

**Required inputs:**
- `run_id` — the completed run
- `program_id` — the experiment program
- `proposal_yaml_path` — path to the proposal that generated the run

**How to invoke:**
1. Read `agents/analyst.md` for the full spec
2. Gather the required files yourself:
   - `data/runs/<run_id>/run_manifest.json`
   - `data/reports/phase2/<run_id>/phase2_diagnostics.json`
   - `data/reports/phase2/<run_id>/phase2_candidates.parquet` (use pandas to inspect)
   - If candidates empty: `data/reports/phase2/<run_id>/hypotheses/<SYMBOL>/evaluated_hypotheses.parquet`
   - If candidates empty: `data/reports/phase2/<run_id>/hypotheses/<SYMBOL>/gate_failures.parquet`
3. Launch an Agent (subagent_type: general-purpose) with:
   - The analyst spec from `agents/analyst.md`
   - The file contents you gathered
   - The handoff template from `agents/handoffs/coordinator_to_analyst.md`
4. Receive the analyst_report

**Required output:** Structured analyst report per the analyst spec.

**Stop condition:** If the run failed before phase2, stop the research loop and
report the pipeline failure. Do not proceed to mechanism_hypothesis.

### Mechanism Hypothesis
**Trigger:** You have a completed analyst report with at least one recommended
next experiment that is not "kill".

**Required inputs:**
- `analyst_report` — the structured report from the analyst agent
- `original_proposal_yaml_path` — the proposal that generated the analyzed run

**How to invoke:**
1. Read `agents/mechanism_hypothesis.md` for the full spec
2. Launch an Agent (subagent_type: general-purpose) with:
   - The mechanism_hypothesis spec
   - The analyst report
   - The original proposal YAML content
   - The handoff template from `agents/handoffs/analyst_to_mechanism_hypothesis.md`
3. Receive 1-3 mechanism hypotheses

**Required output:** 1-3 structured mechanism hypotheses per the spec.

**Stop condition:** If the analyst report recommends "kill" for all lines, do NOT
invoke mechanism_hypothesis. Instead, record the kill decision and stop.

### Compiler
**Trigger:** You have one or more frozen mechanism hypotheses to compile.

**Required inputs:**
- `mechanism_hypothesis` — one hypothesis (invoke once per hypothesis)
- `program_id` — the program this belongs to

**How to invoke:**
1. Read `agents/compiler.md` for the full spec
2. Verify the hypothesis references valid events, templates, horizons BEFORE
   invoking (pre-screen using your own knowledge of the repo specs)
3. Launch an Agent (subagent_type: general-purpose) with:
   - The compiler spec
   - The mechanism hypothesis
   - The handoff template from `agents/handoffs/mechanism_hypothesis_to_compiler.md`
4. Receive the compiled proposal + commands

**Required output:** Proposal YAML, explain/preflight/plan/execution commands, review checklist.

**Stop condition:** If the compiler rejects the hypothesis (unsupported horizon,
invalid template, nonexistent event), route the rejection back to
mechanism_hypothesis for revision. Maximum 2 revision cycles before escalating
to the user.

## Thesis bootstrap loop

When one specific run deserves runtime-readable thesis input, do this first:

1. `python -m project.research.export_promoted_theses --run_id <run_id>`
2. optionally record runtime registration or deployment-state overrides on that export surface

When the thesis store is empty or sparse, or when recent runs need broader packaging maintenance, use this sequence after the bounded research loop:

1. `python -m project.scripts.build_seed_bootstrap_artifacts`
2. `python -m project.scripts.build_seed_testing_artifacts`
3. `python -m project.scripts.build_seed_empirical_artifacts`
4. `python -m project.scripts.build_founding_thesis_evidence` for selected high-priority theses
5. `python -m project.scripts.build_seed_packaging_artifacts`
6. `python -m project.scripts.build_structural_confirmation_artifacts` only when conservative bridge packaging is intended
7. `python -m project.scripts.build_thesis_overlap_artifacts --run_id <run_id>`

Use this loop to answer:

- which theses are still only candidates
- which are tested but under-evidenced
- which can be `seed_promoted`
- which can be `paper_promoted`
- whether the packaged thesis set is structurally disconnected or overlap-aware
- not “what runtime will use by default” — runtime selection is explicit now

## Stage discipline

### Observation / Research stage
- Run the experiment via `edge operator run`
- Invoke analyst on the completed run
- This is read-only diagnosis — no hypothesis formulation here

### Validation stage
- Invoke mechanism_hypothesis on the analyst report
- Review the hypotheses yourself for scope drift:
  - Are the events in the canonical registry?
  - Are the templates valid for the event family?
  - Is the regime the same as (or narrower than) the original?
  - Are horizons supported?
- If anything drifts, reject back to mechanism_hypothesis

### Final holdout stage
- Invoke compiler on each validated hypothesis
- Review the compiled proposal against the plan review checklist
- Run the explain command yourself to validate normalization
- Run preflight and plan to verify the plan
- Only after plan review: execute

### Export stage
- Export a run explicitly when the result should become runtime-readable input
- Do not confuse export with live trading permission
- Inspect `deployment_state` before answering “can this trade?”

### Packaging stage
- Do not package a thesis until testing and empirical evidence are both reviewed
- Do not allow `seed_promoted` or bridge-derived confirmation theses to be described as production-ready
- Regenerate overlap artifacts after any packaging change

## Scope drift prevention

You MUST check for and prevent:

| Drift Type | Check |
|------------|-------|
| Symbol drift | New symbols not in original proposal |
| Date drift | Window expanded beyond original |
| Template drift | Templates not valid for event family |
| Trigger family drift | Events from different family than intended |
| Horizon drift | Horizons not in supported set |
| Regime drift | Regime changed without new hypothesis version |
| Conditioning axis drift | New context dimensions added without justification |

If any drift is detected, REJECT the output back to the originating agent with
the specific drift identified.
