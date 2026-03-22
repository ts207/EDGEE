# Experiment Protocol

This document defines how to turn one research question into one bounded, replayable experiment.

An experiment should answer a specific question with the smallest trustworthy run. It does not exist to generate output volume.

---

## What a Good Experiment Specifies

Before running, you should be able to fill in all of these:

| Field | Description |
|---|---|
| `objective` | The belief being tested, in one sentence. |
| `run_scope` | Symbol(s), date range. |
| `trigger_space` | Event name(s) or family name(s). |
| `templates` | Template(s) from the family's allowed set. |
| `contexts` | Market-state filters to apply. |
| `directions` | `long`, `short`, or both — with justification for both. |
| `horizons_bars` | One to three horizon values. |
| `entry_lags` | Entry lag bars. |
| `expected_artifacts` | What outputs you expect to exist after the run. |
| `success_condition` | What a passing result looks like. |
| `failure_condition` | What a failing result looks like, and what it means. |

If you cannot specify `success_condition` and `failure_condition` in advance, the question is not ready to run.

---

## Scope Rules

Start narrow. Every broadening must be justified.

- **One family** before many families.
- **One template family** before many.
- **One context family** before many.
- **One symbol** before many, unless cross-sectional behavior is the explicit question.
- **One primary objective per run.** Do not append unrelated families "just in case."

Broaden only after the narrow path is mechanically clean and statistically interpretable.

---

## Batch Design

When running more than one slice:

- **Primary slice** — the main question.
- **Comparison slice** — one specific question such as: does context help? Is an adjacent legal template better? Is the effect robust to one small design variation?
- **Optional adjacent slice** — only if it tests a genuinely distinct sub-question.

Do not add unrelated objectives to the same batch.

---

## Planning Rule

Use `plan_only` before every material run.

```bash
edge-run-all \
  --run_id <your_run_id> \
  --symbols BTCUSDT \
  --start 2024-01-01 \
  --end 2024-03-31 \
  --plan_only 1
```

Planning verifies:
- the run is actually narrow
- the event and template set are correct
- the stages in scope are what you intended

If the plan is broader than your objective, fix the proposal before running.

---

## Execution Order

Default sequence:

1. **Repair replay** if a code or contract change needs verification first.
2. **Narrow discovery slice** — the primary question.
3. **Broader expansion** only after the narrow slice reconciles.
4. **Confirmatory or promotion path** only after discovery justifies it.

Do not skip to promotion before discovery output supports it.

---

## Evaluation Checklist

Every experiment should be checked on all of these before being called meaningful:

**Mechanical**
- [ ] All intended stages completed
- [ ] Manifests and logs agree
- [ ] Required artifacts are present
- [ ] Warning noise is not hiding real failures

**Statistical**
- [ ] Non-zero validation and test split counts
- [ ] Metrics survive multiplicity correction
- [ ] Post-cost quality is non-negative
- [ ] Stressed quality is checked

**Deployment Relevance**
- [ ] Costs still allow meaningful expectancy
- [ ] Context claim is plausible
- [ ] Candidate contract is valid if heading toward promotion

---

## Stop Rules

Stop broadening an experiment when any of these apply:

- The path is mechanically broken and unrepaired.
- The idea fails cleanly on holdout.
- Context adds no value over the base case.
- Promotion rejection is clearly explained and no new material condition exists.
- The next run would only restate the same failed question.

---

## Promotion Discipline

Discovery and promotion are different surfaces. A result does not become promotion-ready because it looks attractive.

Promotion should only be trusted when:
- the candidate contract is valid
- split support exists (non-zero validation and test counts)
- costs and stressed quality survive
- the claim is narrow enough to understand and explain

---

## Synthetic Discipline

When the experiment uses synthetic data:
- Truth validation comes before interpretation of misses.
- Short windows are calibration evidence unless holdout support exists.
- Cross-profile survival matters more than one strong synthetic world.
- Store the generator profile, noise scale, and truth-map path with the run record.
