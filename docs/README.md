# EDGEE Documentation

This docs set is split into two tracks plus one cross-role audit.

## Tracks

### Researcher
For operators running experiments, evaluating runs, and making promotion decisions.

| Doc | Purpose |
|---|---|
| [researcher/ONBOARDING.md](./researcher/ONBOARDING.md) | Start here. Role, principles, first run. |
| [researcher/RESEARCH_LOOP.md](./researcher/RESEARCH_LOOP.md) | Observe -> retrieve -> propose -> execute -> evaluate. |
| [researcher/EXPERIMENT_PROTOCOL.md](./researcher/EXPERIMENT_PROTOCOL.md) | How to scope and run one experiment. |
| [researcher/GUARDRAILS.md](./researcher/GUARDRAILS.md) | Operating rules, stop conditions, scope limits. |
| [researcher/ARTIFACTS_AND_CONTRACTS.md](./researcher/ARTIFACTS_AND_CONTRACTS.md) | How to read and trust run output. |
| [researcher/BENCHMARK_GUIDE.md](./researcher/BENCHMARK_GUIDE.md) | Benchmark status and maintenance cycle. |
| [researcher/SYNTHETIC_DATASETS.md](./researcher/SYNTHETIC_DATASETS.md) | Synthetic profiles, truth validation, guardrails. |
| [researcher/ONTOLOGY.md](./researcher/ONTOLOGY.md) | Regimes, states, events, families, templates, hypotheses. |
| [researcher/FEATURE_CATALOG.md](./researcher/FEATURE_CATALOG.md) | Canonical features and their ownership. |
| [researcher/MEMORY_AND_REFLECTION.md](./researcher/MEMORY_AND_REFLECTION.md) | Memory schema, reflection questions, retrieval rules. |

### Developer
For engineers modifying the codebase, adding detectors, changing contracts, or maintaining the platform.

| Doc | Purpose |
|---|---|
| [developer/ONBOARDING.md](./developer/ONBOARDING.md) | Repo layout, build commands, coding rules. |
| [developer/ARCHITECTURE.md](./developer/ARCHITECTURE.md) | Package surfaces, canonical imports, removed packages. |
| [developer/MAINTENANCE_CHECKLIST.md](./developer/MAINTENANCE_CHECKLIST.md) | What to update when changing contracts, surfaces, or docs. |
| [developer/TECH_STACK.md](./developer/TECH_STACK.md) | Dependencies, versions, and tooling. |

## Cross-role audit

| Doc | Purpose |
|---|---|
| [CURRENT_STATE_AND_GAPS.md](./CURRENT_STATE_AND_GAPS.md) | What the code already does, what older docs understate, and what remains undocumented. |

## Ownership rules

| Location | Status | Policy |
|---|---|---|
| `docs/` (this tree) | Authored | Edit to keep current. |
| `docs/generated/` | Not present in this snapshot | Do not assume it exists. |
| `docs/EDGE_Vision.docx` | Roadmap archive | Treat as historical vision material. |

When a policy doc and a planning note disagree, the policy doc wins.
