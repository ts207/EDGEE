# EDGEE Documentation

This docs set is split into two tracks. Choose the one that matches your role.

---

## Tracks

### Researcher
For operators running experiments, evaluating runs, and making promotion decisions.

| Doc | Purpose |
|---|---|
| [researcher/ONBOARDING.md](./researcher/ONBOARDING.md) | Start here. Role, principles, first run. |
| [researcher/RESEARCH_LOOP.md](./researcher/RESEARCH_LOOP.md) | The full observe → reflect cycle. |
| [researcher/EXPERIMENT_PROTOCOL.md](./researcher/EXPERIMENT_PROTOCOL.md) | How to design, scope, and execute one experiment. |
| [researcher/GUARDRAILS.md](./researcher/GUARDRAILS.md) | Operating rules, stop conditions, scope limits. |
| [researcher/ARTIFACTS_AND_CONTRACTS.md](./researcher/ARTIFACTS_AND_CONTRACTS.md) | How to read and trust run output. |
| [researcher/BENCHMARK_GUIDE.md](./researcher/BENCHMARK_GUIDE.md) | Benchmark status, maintenance cycle, promotion gating. |
| [researcher/SYNTHETIC_DATASETS.md](./researcher/SYNTHETIC_DATASETS.md) | Synthetic profiles, truth validation, guardrails. |
| [researcher/ONTOLOGY.md](./researcher/ONTOLOGY.md) | Regimes, states, events, families, templates, hypotheses. |
| [researcher/FEATURE_CATALOG.md](./researcher/FEATURE_CATALOG.md) | All canonical features and their owning stages. |
| [researcher/MEMORY_AND_REFLECTION.md](./researcher/MEMORY_AND_REFLECTION.md) | Memory schema, reflection questions, retrieval rules. |

### Developer
For engineers modifying the codebase, adding detectors, changing contracts, or maintaining the platform.

| Doc | Purpose |
|---|---|
| [developer/ONBOARDING.md](./developer/ONBOARDING.md) | Start here. Repo layout, build commands, coding rules. |
| [developer/ARCHITECTURE.md](./developer/ARCHITECTURE.md) | Package surfaces, canonical imports, removed packages. |
| [developer/MAINTENANCE_CHECKLIST.md](./developer/MAINTENANCE_CHECKLIST.md) | What to do when changing contracts, surfaces, or generated docs. |
| [developer/TECH_STACK.md](./developer/TECH_STACK.md) | Dependencies, versions, and tooling. |

---

## Ownership Rules

| Location | Status | Policy |
|---|---|---|
| `docs/` (this tree) | Authored | Edit to keep current. |
| `docs/generated/` | Machine-owned | Do not hand-edit. Regenerate with maintenance scripts. |
| `docs/plans/` | Planning history | Do not treat as current policy unless adopted by a maintained doc. |

When a policy doc and a planning note disagree, the policy doc wins.
