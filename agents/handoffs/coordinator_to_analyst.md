# Handoff: Coordinator -> Analyst

## Context

You are the analyst agent. The coordinator has invoked you to diagnose a completed
experiment run.

## Your Specification

Follow the analyst spec in `agents/analyst.md` exactly.

## Provided Data

### Run Identity
- run_id: {{run_id}}
- program_id: {{program_id}}
- proposal_path: {{proposal_yaml_path}}

### Run Manifest
```json
{{run_manifest_json}}
```

### Phase2 Diagnostics
```json
{{phase2_diagnostics_json}}
```

### Phase2 Candidates Summary
{{phase2_candidates_summary}}

### Upstream Artifacts (if candidates empty)
{{evaluated_hypotheses_summary}}
{{gate_failures_summary}}

### Original Proposal
```yaml
{{proposal_yaml}}
```

## Instructions

1. Diagnose run health from the manifest
2. Trace the funnel from generation through gating
3. Identify the primary rejection mechanism
4. Find the strongest near-misses
5. Read the asymmetry (long/short, horizon, event type)
6. Interpret the mechanistic meaning
7. Recommend 1-3 bounded next experiments

Return your output in the exact format specified in `agents/analyst.md`.

Do NOT propose mechanism hypotheses or compile proposals.
Do NOT recommend broadening scope unless structurally necessary.
