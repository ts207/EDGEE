# Research Loop

The research loop is the standard operating cycle for every experiment in this system.

```
observe → retrieve memory → define objective → propose → plan → execute → evaluate → reflect → adapt
```

A complete loop leaves behind: a bounded objective, a reconciled artifact set, an evaluation, a reflection, and an explicit next action. If any of these are missing, the loop is incomplete.

---

## Phase 1 — Observe

Collect the smallest evidence set that describes the current state:

- latest run manifest and relevant stage manifests
- stage logs where failures or warnings occurred
- discovery and promotion summaries
- generated diagnostics when ownership or registry questions are relevant

**Key questions to answer at this phase:**
- What was previously tried in this region?
- What failed mechanically?
- What looked statistically interesting?
- What remains ambiguous?

---

## Phase 2 — Retrieve Memory

Before proposing a new run, check memory for prior work on:

- the same event or family
- the same template
- the same symbol or timeframe
- the same context
- the same fail gate

If prior memory shows repeated clean failure with no material new condition, do not rerun by default. See [MEMORY_AND_REFLECTION.md](./MEMORY_AND_REFLECTION.md) for retrieval rules.

---

## Phase 3 — Define Objective

The objective must be explicit and falsifiable before any run is planned.

**Good objectives:**
- "Test whether a basis dislocation continuation survives costs in low-liquidity windows."
- "Verify whether the promotion rejection came from missing holdout support rather than weak economics."
- "Isolate whether high-confidence trend context improves this specific template."

**Bad objectives:**
- "Find alpha."
- "Try more experiments."
- "Search more broadly."

---

## Phase 4 — Propose

Translate the objective into repo-native terms:

| Field | Options |
|---|---|
| `trigger` | event name or family name |
| `templates` | from the family's allowed template set |
| `context` | market-state filters (`ms_vol_state`, `ms_spread_state`, etc.) |
| `directions` | `long`, `short`, or both |
| `horizons` | bar counts |
| `entry_lags` | bar offsets |
| `date_scope` | start / end |
| `symbol_scope` | one symbol before many |

Use the ontology-native surfaces. Do not invent free-form categories when the registry has a canonical form.

---

## Phase 5 — Plan

Use `plan_only` before every material run. Planning verifies:

- the requested stages are actually in scope
- the event and template set are what you intended
- the run is still narrow
- unnecessary downstream work is not being pulled in

If the plan is broader than the objective, fix the proposal before running.

```bash
edge-run-all --run_id <id> --symbols BTCUSDT --start 2024-01-01 --end 2024-01-31 --plan_only 1
```

---

## Phase 6 — Execute

Default execution order:

1. Targeted replay if a code or contract change must be verified first.
2. Narrow discovery slice.
3. Broader expansion only after the narrow path reconciles.

The repository should answer one question per run whenever possible.

---

## Phase 7 — Evaluate

Evaluate every run on three layers.

### Mechanical
- Did all intended stages complete?
- Do manifests and outputs reconcile?
- Are required artifacts present?
- Are warnings hiding runtime faults?

### Statistical
- Are there non-zero validation and test counts?
- Do metrics survive multiplicity correction and cost deduction?
- Are results stable across splits?

### Deployment Relevance
- Is the idea tradeable after friction costs?
- Is the result narrow and attributable?
- Is the context stable enough to matter live?

**Trust order when reading evidence:**

1. Top-level run manifest
2. Stage manifests
3. Stage logs
4. Report artifacts
5. Generated diagnostics

If those sources disagree, the disagreement is itself a finding — not a detail to explain away.

---

## Phase 8 — Reflect

After every meaningful run, answer these five questions:

1. What belief was being tested?
2. What evidence increased or decreased that belief?
3. Was the result market-driven or system-driven?
4. What reusable rule should be remembered?
5. What exact next action is justified?

Store the reflection using the schema in [MEMORY_AND_REFLECTION.md](./MEMORY_AND_REFLECTION.md).

---

## Phase 9 — Adapt

Choose one of these next actions:

| Action | When to use |
|---|---|
| `exploit` | Narrow positive evidence justifies a confirmatory or adjacent strengthening run. |
| `explore` | The result was informative but the next move should test a nearby region. |
| `repair` | System or contract issues dominate and must be fixed before more research. |
| `hold` | Evidence is too weak or ambiguous to justify more work now. |
| `stop` | The idea or path is not worth continuing under current evidence. |

If the loop does not end in one of these decisions, it is incomplete.

---

## Escalation and De-escalation

**Escalate from narrow to broad only when:**
- the narrow path is mechanically clean
- the target claim is still coherent after the narrow run
- there is enough statistical support to justify wider scope

**De-escalate to repair mode when:**
- manifests and logs disagree
- required artifacts are missing
- candidate contracts are malformed
- warnings are obscuring real failures

---

## Synthetic Branch

When running on synthetic data, the loop changes at phases 6–8:

1. Freeze the generator profile before evaluating outcomes.
2. Keep the manifest and truth map with the run.
3. Validate detector truth before interpreting misses.
4. Compare across at least one additional profile before strengthening belief.
5. Separate detector recovery claims from profitability claims explicitly.

---

## Definition of Done

The loop is complete only when:

- artifacts reconcile
- the result is interpreted at the correct layer (mechanical / statistical / deployment)
- the next action is explicit
- memory is updated with enough information to prevent repeated rediscovery
