# Best Practices And Failure Modes

This file is the shortest practical answer to "How should I use this repo well?"

## Best Usage

### Start narrow

Default to:

- one event or one tight family
- one symbol
- one timeframe
- one bounded date range
- one main template family

Narrow runs leave behind clear attribution. Broad runs mostly leave confusion.

### Plan first

Use plan-only before expensive execution. Verify:

- symbols
- date range
- trigger scope
- templates
- horizons
- output locations

### Prefer maintained entry points

Use:

- `knowledge.query`
- `proposal_to_experiment`
- `execute_proposal`
- `issue_proposal`
- `run_all`
- `make` targets

Avoid ad hoc shell pipelines when a maintained entry point already captures the workflow.

### Separate conclusions

Always end with:

- mechanical conclusion
- statistical conclusion
- deployment conclusion
- next action

### Trust artifacts over impressions

If a run "felt successful" but artifacts disagree, the artifacts win.

## Common Failure Modes

### Broad search when the question is narrow

This wastes compute and destroys attribution.

Fix:

- scope search to the event or family you actually care about
- avoid unrelated states, sequences, and interactions in the same run unless they are the question

### Treating detector output as strategy proof

An event detector producing rows is not evidence of deployable edge.

Fix:

- inspect phase-2 and bridge outputs separately

### Reading only winners

Ignoring rejected hypotheses hides the real reason a run failed.

Fix:

- inspect diagnostics and gate-failure surfaces, not just surviving candidates

### Blending live and synthetic conclusions

Synthetic is for calibration and truth recovery, not direct live edge proof.

Fix:

- keep synthetic and historical-live conclusions separate

### Exit-code trust

Commands can return success while the research result is still invalid or weak.

Fix:

- reconcile manifests, artifacts, and logs every time

## Strong Default Recommendation

If you are unsure how to proceed, do this:

1. query memory and knobs
2. define one explicit claim
3. plan the run
4. run a narrow slice
5. read the manifest, diagnostics, and funnel
6. record one next action

That path prevents most self-inflicted errors.
