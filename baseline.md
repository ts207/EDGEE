# Baseline

Date: `2026-04-03`
Branch workspace: `/home/irene/Edge`

## Baseline command results

### `make minimum-green-gate`

- Status: failing before any edits
- Log: `tmp/baseline_minimum_green_gate.log`
- Failure:
  - `project/scripts/detector_coverage_audit.py --check`
  - drift reported in:
    - `docs/generated/detector_coverage.json`
    - `docs/generated/detector_coverage.md`

### `pytest -q project/tests/live project/tests/research project/tests/scripts`

- Status: failing before any edits
- Log: `tmp/baseline_pytest_live_research_scripts.log`
- Failure:
  - test collection error in `project/tests/scripts/test_baseline_snapshot_scripts.py`
  - `ModuleNotFoundError: No module named 'scripts.baseline'`

## Snapshots captured

- Generated docs snapshot:
  - `tmp/baseline_snapshots/docs_generated/`
- Domain graph snapshot:
  - `tmp/baseline_snapshots/spec_domain/domain_graph.yaml`

Current generated files present:

- `docs/generated/event_deep_analysis_suite.md`
- `docs/generated/regime_routing_audit.md`
- `spec/domain/domain_graph.yaml`

## Current symptoms

- Shadow live retrieval count: unavailable in current workspace
  - `docs/generated/shadow_live_thesis_summary.json` is absent
  - `data/live/theses/` is absent, so there is no packaged thesis store to validate against
- Eligible cycle count: unavailable in current workspace for the same reason
- Overlap metadata visible boolean: unavailable in current workspace for the same reason
- Number of packaged theses: `0`
  - `data/live/theses/` does not exist
- Current template kinds in `spec/templates/registry.yaml`:
  - the file does not expose per-template `kind`
  - it currently stores operator metadata under `operators.*.template_kind`
  - selected current values:
    - `mean_reversion`: `execution_template`
    - `continuation`: `execution_template`
    - `trend_continuation`: `execution_template`
    - `pullback_entry`: `execution_template`
    - `exhaustion_reversal`: `filter_template`
    - `momentum_fade`: `filter_template`
    - `overshoot_repair`: `filter_template`
    - `only_if_regime`: `filter_template`
    - `only_if_liquidity`: `filter_template`
    - `only_if_funding`: `filter_template`
    - `only_if_oi`: `filter_template`
    - `slippage_aware_filter`: `filter_template`
    - `tail_risk_avoid`: `filter_template`

## Runtime mismatch to fix

- `project/live/retriever.py` still prefers mixed id/family token matching in `_context_events()` and `_requirements_for_matching()`
- `project/live/thesis_store.py` still merges `event_id` and `event_family` into one filter branch
- `project/live/contracts/promoted_thesis.py` and `project/live/contracts/live_trade_context.py` still backfill `primary_event_id` and `event_family` symmetrically

## Target outcomes

- Runtime retrieval is thesis-clause-first and id-centric
- Family matching remains compatibility-only
- Retrieval reasons are clause-based rather than generic family-match language
- `ThesisStore.filter(event_id=...)` and `filter(event_family=...)` behave distinctly
- Live contract normalization becomes one-way compatibility, not symmetric interchangeability
