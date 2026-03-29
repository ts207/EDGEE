# Final Recommendations

## Current Project State After Implementation

The implementation materially improved the architecture in the intended direction. In the bounded post-review run, canonical phase-2 storage, distinct `candidate_id` vs `hypothesis_id`, canonical regime-routing metadata, and proposal-driven promotion semantics all held after fixing three local boundary defects in the smoke replay/export path. The core repository state is stronger than the original audit described, but the bounded experiment still does not fully prove the end-to-end blueprint-to-engine bridge on run-scoped artifacts.

## What The Bounded Run Proved Or Disproved

Proved:

- The proposal-issued narrow run can be replayed onto one canonical phase-2 tree.
- Phase-2 artifacts can carry explicit, non-collapsed lineage.
- Promotion outputs can preserve proposal semantics and hypothesis lineage.
- Canonical event/regime metadata can be present from phase-2 through promotion.

Disproved or not yet proven:

- This bounded fixture does not produce a promotable candidate under current thresholds.
- Because no candidate is promoted, the run does not prove blueprint compilation or typed-engine execution from the run’s own artifacts.

## Remaining Risks

- The maintained bounded smoke fixture is still too weak for Phase 5 verification.
- Promotion gate naming remains slightly misleading in diagnostics (`deploy_confirmatory` appears even under `research` profile), which can confuse postmortems even if behavior is correct.
- Self-comparison via `compare_run_ids(run_id, run_id)` is mechanically valid but analytically low-signal.

## Highest-Value Next Improvements

- Create one deterministic bounded fixture or tiny proposal slice that yields exactly one promoted candidate under `promotion_profile=research`.
- Add a regression test that `promotion_decisions.parquet` retains `hypothesis_id`.
- Add a regression test that smoke phase-2 outputs retain `canonical_regime` and `routing_profile_id`.
- Add a narrow assertion that promotion smoke uses the proposal’s `promotion_profile` rather than the CLI default.

## Recommended Next Experiment

Run the same narrow `VOL_SHOCK` replay shape, but seed or fixture it so one candidate clears the research-profile statistical gates while the other still fails. That preserves the bounded scope while finally exercising:

- `promoted_candidates.parquet`
- `blueprints.jsonl`
- `executable_strategy_spec_index.json`
- `run_engine_for_specs(...)` on run-scoped specs

The success condition should be exactly one promoted candidate and at least one executable strategy spec, not a broad search or threshold relaxation.

## Exact Tests And Verification To Protect The New Changes

```bash
.venv/bin/pytest project/tests/smoke/test_promotion_smoke.py -q
```

Add next:

- `project/tests/smoke/test_promotion_smoke.py`
  Assert `promotion_diagnostics.json["promotion_profile"] == "research"` for the bounded replay.
- `project/tests/smoke/test_promotion_smoke.py`
  Assert `promotion_decisions.parquet["hypothesis_id"]` is populated and matches the upstream phase-2 lineage.
- A narrow smoke or service test around [`/home/irene/Edge/project/reliability/smoke_data.py`](/home/irene/Edge/project/reliability/smoke_data.py)
  Assert `phase2_candidates.parquet` contains populated `canonical_regime` and `routing_profile_id`.
- A bounded blueprint smoke
  Assert one promoted candidate produces one executable spec and that `run_engine_for_specs` preserves `run_id`, `candidate_id`, `hypothesis_id`, and `blueprint_id`.

The next logical step is to add that one promotable bounded fixture and rerun the same postmortem template without widening scope.
