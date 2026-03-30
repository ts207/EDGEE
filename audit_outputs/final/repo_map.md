# Repo Map

Required path map, traced from code rather than prose:

## 1. Proposal

- `project/research/agent_io/issue_proposal.py:57`
  - `issue_proposal()` loads the proposal, materializes a proposal copy under memory storage, and delegates execution.
- `project/research/agent_io/execute_proposal.py:77`
  - `execute_proposal()` translates the proposal into `experiment.yaml` plus `run_all_overrides.json`, then shells into `project.pipelines.run_all`.

## 2. Search

- `project/pipelines/run_all.py:126`
  - `_run_all_impl()` resolves config, preflight, and the executable stage plan.
- `project/contracts/pipeline_registry.py:182`
  - `phase1_analysis` owns event analysis and clustering surfaces.
- `project/contracts/pipeline_registry.py:190`
  - `phase2_event_registry` owns event-registry and episode canonicalization surfaces.
- `project/contracts/pipeline_registry.py:198`
  - `phase2_discovery` owns `phase2_search_engine`, discovery summarization, and experiment finalization.

## 3. Validation

- `project/contracts/pipeline_registry.py:167`
  - `runtime_invariants` stages materialize replay, causal lanes, determinism replay, and OMS replay validation.
- `project/pipelines/run_all_finalize.py:99`
  - `finalize_successful_run()` reconciles the run manifest from stage manifests before allowing terminal success.
- Validation consequence confirmed locally:
  - `pytest -q project/tests/regressions/test_run_success_requires_outputs.py -q` passed and refused success finalization when required outputs were missing.

## 4. Promotion

- `project/contracts/pipeline_registry.py:215`
  - `promotion` owns `evaluate_naive_entry`, `generate_negative_control_summary`, `promote_candidates`, `update_edge_registry`, `update_campaign_memory`, and `export_edge_candidates`.

## 5. Blueprint / Spec

- `project/pipelines/stages/evaluation.py:5`
  - `build_evaluation_stages()` wires `compile_strategy_blueprints`, `build_strategy_candidates`, and `select_profitable_strategies`.
- `project/engine/runner.py:55`
  - `_spec_metadata_payload()` carries proposal/run/hypothesis/candidate/blueprint lineage into engine execution.
- `project/engine/runner.py:86`
  - `run_engine_for_specs()` consumes executable strategy specs and turns them into engine-run strategies.

## 6. Engine / Live

- `project/engine/runner.py:86`
  - strategy specs become executable backtest/engine runs.
- `project/scripts/run_live_engine.py:384`
  - `build_live_runner()` resolves runtime config, environment, and live OMS wiring.
- `project/live/runner.py:27`
  - `LiveEngineRunner` is the live runtime surface handling state, kill-switching, order submission, and incubation gating.

## Audit Notes

- The proposal -> search -> validation -> promotion -> blueprint/spec -> engine/live chain is real in code.
- The strongest verified breaks in this audit are repository hygiene, contract provenance drift for objective/profile resolution, and the live incubation ledger path bug.
