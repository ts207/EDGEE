# Research Loop

## Default Loop

The default autonomous loop is:

1. Pick one canonical regime.
2. Write one mechanism sheet.
3. Define one tradable expression.
4. Translate that into one bounded proposal.
5. Plan the run.
6. Execute the run.
7. Inspect manifests, diagnostics, and reports in artifact order.
8. Produce one keep/modify/kill decision.
9. Log the result into the edge registry.

## Exact Operating Sequence

### 1. Retrieve existing memory and static context

Run:

```bash
.venv/bin/python -m project.research.knowledge.query knobs
.venv/bin/python -m project.research.knowledge.query memory --program_id <program_id>
.venv/bin/python -m project.research.knowledge.query static --event <event_type>
```

Use this to avoid repeating already-tested regions and to verify the candidate mechanism is grounded in an existing event/regime family.

### 2. Write the mechanism and hypothesis

Fill in:

- `hypothesis_template.md`
- the mechanism section of `experiment_review_template.md` before running anything

Hard scope rule:

- one regime,
- one mechanism,
- one tradable expression,
- one template family,
- one primary event family.

### 3. Draft the proposal

Create a proposal YAML that stays inside `project.research.agent_io.proposal_schema.AgentProposal`.

Required proposal characteristics:

- `trigger_space.canonical_regimes` contains exactly one regime,
- `templates` contains only the intended template family,
- `symbols`, `timeframe`, `start`, `end`, `horizons_bars`, `directions`, and `entry_lags` are explicit,
- any knob overrides are proposal-settable only.

### 4. Plan before executing

Plan the run first:

```bash
.venv/bin/python -m project.research.agent_io.issue_proposal \
  --proposal /abs/path/to/proposal.yaml \
  --registry_root project/configs/registries \
  --plan_only 1
```

Review:

- validated hypothesis count,
- required detectors,
- required features,
- required states,
- whether the plan still matches the intended bounded mechanism.

Stop if the validated plan widens beyond the intended mechanism or regime.

### 5. Execute the bounded run

Execute only after the plan remains bounded:

```bash
.venv/bin/python -m project.research.agent_io.issue_proposal \
  --proposal /abs/path/to/proposal.yaml \
  --registry_root project/configs/registries \
  --run_id <planned_run_id> \
  --plan_only 0
```

### 6. Review artifacts in strict order

Read in this order:

1. `data/runs/<run_id>/run_manifest.json`
2. `data/reports/phase2/<run_id>/phase2_diagnostics.json`
3. `data/reports/phase2/<run_id>/phase2_candidates.parquet`
4. `data/reports/promotions/<run_id>/promotion_diagnostics.json`
5. promotion tables and evidence bundles
6. blueprint/spec artifacts if any candidate was promoted
7. comparison report if there is a directly relevant baseline run

Do not jump directly to headline metrics.

### 7. Produce the decision

Use `experiment_review_template.md` and end with exactly one:

- `keep`
- `modify`
- `kill`

The next step must remain bounded. No open-ended follow-on search.

### 8. Update the edge registry

Write one new or updated row using `edge_registry_template.md`.

Required fields:

- hypothesis id,
- regime,
- status,
- evidence strength,
- latest run id,
- cost survivability,
- execution realism,
- drift sensitivity,
- next action.

## Comparison Rule

Run comparison is allowed only when the baseline is directly comparable:

- same regime,
- same mechanism family,
- same tradable expression,
- only one intentional change.

Use:

```bash
.venv/bin/python project/scripts/compare_research_runs.py \
  --baseline_run_id <baseline_run_id> \
  --candidate_run_id <candidate_run_id>
```

Self-comparison is not a substantive review.

## Stop Conditions

Stop immediately if:

- the plan widened beyond one regime/mechanism/expression,
- artifacts are missing or contradictory,
- schema validation fails,
- the result only survives after rationalizing away costs,
- the next proposed step is broader rather than sharper.
