# Research Docs

This docs set is organized around operator workflows.

Use it to answer four questions quickly:

1. What should I read first?
2. Which docs are policy versus reference?
3. Which path should I use for real research versus synthetic calibration?
4. Which files are authored docs versus generated evidence or planning history?

## Start Paths

Choose one start path instead of reading the whole tree.

### New operator

Read in this order:

1. [Root Operator Guide](../CLAUDE.md)
2. [Research Operator Playbook](./RESEARCH_OPERATOR_PLAYBOOK.md)
3. [Autonomous Research Loop](./AUTONOMOUS_RESEARCH_LOOP.md)
4. [Experiment Protocol](./EXPERIMENT_PROTOCOL.md)
5. [Operations And Guardrails](./OPERATIONS_AND_GUARDRAILS.md)

### Real historical research

Read in this order:

1. [Research Operator Playbook](./RESEARCH_OPERATOR_PLAYBOOK.md)
2. [Experiment Protocol](./EXPERIMENT_PROTOCOL.md)
3. [Artifacts And Contracts](./ARTIFACTS_AND_CONTRACTS.md)
4. [Operations And Guardrails](./OPERATIONS_AND_GUARDRAILS.md)
5. [Research Workflow Example](./RESEARCH_WORKFLOW_EXAMPLE.md)

### Synthetic calibration and detector validation

Read in this order:

1. [Synthetic Datasets](./SYNTHETIC_DATASETS.md)
2. [Research Calibration Baseline](./RESEARCH_CALIBRATION_BASELINE.md)
3. [Experiment Protocol](./EXPERIMENT_PROTOCOL.md)
4. [Artifacts And Contracts](./ARTIFACTS_AND_CONTRACTS.md)

### Benchmark and certification work

Read in this order:

1. [Benchmark Status](./BENCHMARK_STATUS.md)
2. [Benchmark Governance Runbook](./BENCHMARK_GOVERNANCE_RUNBOOK.md)
3. [Benchmark Triage Guide](./BENCHMARK_TRIAGE.md)
4. [Operations And Guardrails](./OPERATIONS_AND_GUARDRAILS.md)

### Architecture and maintenance work

Read in this order:

1. [Architecture Surface Inventory](./ARCHITECTURE_SURFACE_INVENTORY.md)
2. [Architecture Maintenance Checklist](./ARCHITECTURE_MAINTENANCE_CHECKLIST.md)
3. [Artifacts And Contracts](./ARTIFACTS_AND_CONTRACTS.md)

## Docs Sets

These are the maintained documentation sets in this repo.

### 1. Operator Policy

These docs define how a human or external controller should behave.

- [Root Operator Guide](../CLAUDE.md)
- [Research Operator Playbook](./RESEARCH_OPERATOR_PLAYBOOK.md)
- [Autonomous Research Loop](./AUTONOMOUS_RESEARCH_LOOP.md)
- [Interaction Protocol](./INTERACTION_PROTOCOL.md)
- [Memory And Reflection](./MEMORY_AND_REFLECTION.md)
- [Operations And Guardrails](./OPERATIONS_AND_GUARDRAILS.md)

### 2. Experiment Execution

These docs explain how to scope, run, inspect, and interpret research.

- [Experiment Protocol](./EXPERIMENT_PROTOCOL.md)
- [Artifacts And Contracts](./ARTIFACTS_AND_CONTRACTS.md)
- [Research Workflow Example](./RESEARCH_WORKFLOW_EXAMPLE.md)
- [Research Operator Playbook](./RESEARCH_OPERATOR_PLAYBOOK.md)

### 3. Synthetic and Calibration

These docs cover synthetic datasets, detector truth, and calibration expectations.

- [Synthetic Datasets](./SYNTHETIC_DATASETS.md)
- [Research Calibration Baseline](./RESEARCH_CALIBRATION_BASELINE.md)

### 4. Benchmarks and Certification

These docs define the maintained benchmark and certification posture.

- [Benchmark Status](./BENCHMARK_STATUS.md)
- [Benchmark Governance Runbook](./BENCHMARK_GOVERNANCE_RUNBOOK.md)
- [Benchmark Triage Guide](./BENCHMARK_TRIAGE.md)

Current maintained review artifact:

- `data/reports/benchmarks/latest/benchmark_review.json` when the benchmark maintenance cycle has populated local artifacts

### 5. Reference Surfaces

These docs explain ontology, features, families, and long-term direction.

- [Event Families, Templates, Contexts, And Regimes](./FAMILIES_TEMPLATES_AND_REGIMES.md)
- [Feature Catalog](./FEATURE_CATALOG.md)
- [Future Milestones](./FUTURE_MILESTONES.md)
- [tech-stack.md](./tech-stack.md)

### 6. Architecture and Maintenance

These docs are for repo maintenance and package-surface discipline.

- [Architecture Surface Inventory](./ARCHITECTURE_SURFACE_INVENTORY.md)
- [Architecture Maintenance Checklist](./ARCHITECTURE_MAINTENANCE_CHECKLIST.md)

## Read By Question

Use this section when you already know the task.

### I need to start a real research run safely

- [Research Operator Playbook](./RESEARCH_OPERATOR_PLAYBOOK.md)
- [Experiment Protocol](./EXPERIMENT_PROTOCOL.md)
- [Operations And Guardrails](./OPERATIONS_AND_GUARDRAILS.md)

### I need to inspect whether a run is trustworthy

- [Artifacts And Contracts](./ARTIFACTS_AND_CONTRACTS.md)
- [Operations And Guardrails](./OPERATIONS_AND_GUARDRAILS.md)
- [Research Workflow Example](./RESEARCH_WORKFLOW_EXAMPLE.md)

### I need to work with synthetic data

- [Synthetic Datasets](./SYNTHETIC_DATASETS.md)
- [Research Calibration Baseline](./RESEARCH_CALIBRATION_BASELINE.md)

### I need to understand event families, templates, or feature surfaces

- [Event Families, Templates, Contexts, And Regimes](./FAMILIES_TEMPLATES_AND_REGIMES.md)
- [Feature Catalog](./FEATURE_CATALOG.md)

### I need maintained benchmark status or promotion gating context

- [Benchmark Status](./BENCHMARK_STATUS.md)
- [Benchmark Governance Runbook](./BENCHMARK_GOVERNANCE_RUNBOOK.md)
- [Benchmark Triage Guide](./BENCHMARK_TRIAGE.md)

### I need architecture boundaries or maintenance guidance

- [Architecture Surface Inventory](./ARCHITECTURE_SURFACE_INVENTORY.md)
- [Architecture Maintenance Checklist](./ARCHITECTURE_MAINTENANCE_CHECKLIST.md)

## Ownership Rules

Treat the docs tree in these categories:

- Authored policy and reference:
  files directly under `docs/` except `generated/` and `plans/`
- Machine-owned diagnostics:
  `docs/generated/`
- Planning history:
  `docs/plans/` and `docs/superpowers/plans/`

Interpretation rules:

- Do not hand-edit `docs/generated/*`.
- Do not treat `docs/plans/*` as current policy unless another maintained doc adopts the same rule.
- If a policy doc and a planning note disagree, the policy doc wins.

## Maintained Commands

These are the repo-level commands most commonly referenced by the docs set.

### Real pipeline planning or execution

```bash
edge-run-all --run_id demo_run --symbols BTCUSDT --start 2024-01-01 --end 2024-01-31 --plan_only 1
```

### Smoke verification

```bash
edge-smoke --mode research
```

### Broad synthetic discovery

```bash
python3 -m project.scripts.run_golden_synthetic_discovery
```

### Detector truth validation

```bash
python3 -m project.scripts.validate_synthetic_detector_truth --run_id golden_synthetic_discovery
```

### Benchmark review

```bash
PYTHONPATH=. python3 project/scripts/show_benchmark_review.py
```

## When Updating Docs

When adding or editing docs:

- update this file if the reading path changes
- keep policy docs short and directive
- keep reference docs explanatory
- prefer linking to the owning doc instead of duplicating policy
- mark generated or historical material clearly
