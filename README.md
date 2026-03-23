# EDGEE

A research platform for event-driven alpha discovery in crypto markets.

EDGEE turns market observations into explicit, testable hypotheses, runs them through a structured pipeline, and gates any result on mechanical, statistical, and deployment-readiness checks before promotion. The system now includes memory-aware campaign control, MI-based candidate generation, hypothesis clustering, promotion scoring, blueprint compilation, and live-state-aware sizing.

---

## What it does now

The platform is organized around these surfaces:

- Ingest, clean, and feature pipelines for market data
- Market context and regime labeling
- Research orchestration through the campaign controller
- Memory, reflection, and next-action persistence
- Hypothesis evaluation, stress testing, and promotion gating
- Candidate clustering and PnL similarity filtering
- Strategy blueprint compilation and allocation sizing
- Live runner state, health, drift, and kill-switch handling

The important distinction is this: the system is no longer just a detector stack. The research loop already reads and writes state across runs.

---

## Install

Requires Python 3.11+.

```bash
pip install -e .
```

With Nautilus Trader live execution support:

```bash
pip install -e ".[nautilus]"
```

---

## Quickstart

Plan a run before executing it:

```bash
edge-run-all \
  --run_id demo \
  --symbols BTCUSDT \
  --start 2024-01-01 \
  --end 2024-03-31 \
  --plan_only 1
```

Remove `--plan_only 1` to execute. Use plan-only mode first for any material run.

---

## Common commands

### Pipeline

```bash
edge-run-all --run_id <id> --symbols BTCUSDT --start 2024-01-01 --end 2024-03-31 --plan_only 1
edge-phase2-discovery --run_id <id> --symbols BTCUSDT
edge-promote --run_id <id>
edge-smoke --mode research
compile-strategy-blueprints --run_id <id>
```

### Research and memory

```bash
python3 -m project.research.knowledge.query knobs
python3 -m project.research.knowledge.query memory --program_id btc_campaign
python3 -m project.research.knowledge.query static --event BASIS_DISLOC
```

### Synthetic validation

```bash
python3 -m project.scripts.run_golden_synthetic_discovery
python3 -m project.scripts.run_fast_synthetic_certification
python3 -m project.scripts.validate_synthetic_detector_truth --run_id <run_id>
```

### Benchmarks and maintenance

```bash
make benchmark-maintenance
PYTHONPATH=. python3 project/scripts/show_benchmark_review.py
python3 -m project.scripts.build_system_map --check
python3 -m project.scripts.detector_coverage_audit --md-out docs/generated/detector_coverage.md --json-out docs/generated/detector_coverage.json --check
```

---

## Repository layout

```text
project/           Application code
  pipelines/       Stage entrypoints and orchestration
  research/        Discovery, promotion, evaluation, knowledge, services
  live/            Live runner, OMS, drift, health, kill switch
  portfolio/       Allocation, risk budget, and sizing
  contracts/       Stage, artifact, and temporal contracts
  spec_registry/   Search-space and registry loaders
  strategy/        Strategy DSL and templates
  tests/           Regression, contract, smoke, and architecture tests

spec/              Events, features, hypotheses, objectives, and search space
docs/              Role docs and maintained references
  researcher/      Research operator docs
  developer/       Developer docs
  CURRENT_STATE_AND_GAPS.md  Cross-role audit and doc-gap index
deploy/            Systemd units and environment templates
data/              Local runtime outputs and run artifacts
```

---

## Key surfaces

| Surface | Path |
|---|---|
| End-to-end orchestrator | `project/pipelines/run_all.py` |
| Phase 2 discovery | `project/pipelines/research/phase2_candidate_discovery.py` |
| Campaign controller | `project/pipelines/research/campaign_controller.py` |
| Memory update | `project/pipelines/research/update_campaign_memory.py` |
| MI scan | `project/pipelines/research/feature_mi_scan.py` |
| Search intelligence | `project/pipelines/research/search_intelligence.py` |
| Promotion services | `project/research/services/promotion_service.py` |
| Candidate discovery services | `project/research/services/candidate_discovery_service.py` |
| Clustering | `project/research/clustering/alpha_clustering.py` |
| Promotion gating | `project/research/promotion/promotion_gate_evaluators.py` |
| Blueprint compilation | `project/pipelines/research/compile_strategy_blueprints.py` |
| Allocation spec | `project/portfolio/allocation_spec.py` |
| Live runner | `project/live/runner.py` |
| Stage and artifact contracts | `project/contracts/` |
| Ontology and memory | `project/research/knowledge/` |

---

## Research unit

The platform is built around hypotheses, not loose detector output.

A hypothesis specifies the event or trigger family, template, direction, horizon, entry lag, and context. That tuple is what gets evaluated, stored in memory, and gated for promotion.

The canonical event families remain the contract boundary for template eligibility and direction semantics. The docs should describe those families as a stable ontology, not as a casual taxonomy.

---

## Documentation map

- Researchers start with `docs/researcher/ONBOARDING.md`
- Developers start with `docs/developer/ONBOARDING.md`
- The role map lives in `docs/README.md`
- The cross-role audit lives in `docs/CURRENT_STATE_AND_GAPS.md`

`docs/EDGE_Vision.docx` is a roadmap archive and should be read as a vision note, not as the active operational manual.

---

## Core rules

- Artifacts are the source of truth.
- Plan before material runs.
- Synthetic results are calibration, not proof.
- Promotion is a gate, not a label.
- Narrow before broad unless the run is explicitly a breadth scan.
