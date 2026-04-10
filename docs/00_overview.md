# System Overview

Edge is a staged operating system for event-driven crypto research and runtime execution. The repo is designed to take a bounded research claim, evaluate it through persisted artifacts, and only allow runtime use after explicit packaging and deployment-state checks.

The high-level model is:

`discover → validate → promote → deploy`

That model is still correct, but it is not the whole repository. The current project also includes:

- compatibility `operator` commands
- planner-owned orchestration
- explicit export from promotion into runtime inventory
- thesis-state and live-approval contracts
- catalog and benchmark utilities
- plugin and ChatGPT app interface layers

This overview explains how those pieces fit together without confusing them with the canonical lifecycle.

## The Canonical Lifecycle

### 1. Discover

Discover takes a bounded proposal YAML and turns it into a candidate universe.

- Purpose: generate and rank candidate hypotheses
- Front doors: `edge discover plan`, `edge discover run`, `make discover`
- Main code surfaces: `project/cli.py`, `project/discover/`, `project/research/phase2_search_engine.py`, `project/research/services/candidate_discovery_service.py`
- Canonical artifacts: `data/reports/phase2/<run_id>/...`

The key input is a proposal file under `spec/proposals/`. Conceptually that proposal is the Structured Hypothesis: the frozen claim about which Anchor, Filter, template, and scope should be tested.

### 2. Validate

Validate takes discovery outputs and attempts to falsify them.

- Purpose: reject false positives, fragile effects, and non-tradable candidates
- Front doors: `edge validate run`, `edge validate report`, `edge validate diagnose`, `make validate`, `make review`
- Main code surfaces: `project/validate/`, `project/research/services/evaluation_service.py`, `project/research/validation/`
- Canonical artifacts: `data/reports/validation/<run_id>/...`

Validation is the stage that writes the canonical bundle promotion consumes.

### 3. Promote

Promote converts validated research results into governed thesis inventory.

- Purpose: decide which validated candidates are worth packaging for paper or live usage
- Front doors: `edge promote run`, `edge promote export`, `make promote`, `make export`
- Main code surfaces: `project/promote/`, `project/research/services/promotion_service.py`, `project/research/live_export.py`
- Canonical artifacts: `data/reports/promotions/<run_id>/...`

Important: promotion and export are not the same thing. Promotion writes research-facing promotion artifacts. Export writes the runtime-facing thesis batch under `data/live/theses/<run_id>/`.

### 4. Deploy

Deploy consumes exported thesis batches and runs the live engine.

- Purpose: launch paper or live runtime sessions using explicit thesis-state gating
- Front doors: `edge deploy list-theses`, `inspect-thesis`, `paper`, `live`, `status`
- Main code surfaces: `project/live/`, `project/scripts/run_live_engine.py`
- Runtime inventory: `data/live/theses/<run_id>/promoted_theses.json`

Deploy is intentionally downstream of export. A promoted candidate is not automatically a runtime-ready thesis.

## The Full Control Plane

The repo update that caused the old docs to drift is that Edge is no longer just a four-command pipeline. The operational control plane now includes:

### Canonical stage CLI

`project/cli.py` is the public command router for the lifecycle verbs.

### Compatibility operator lane

`edge operator ...` still exists for preflight, lint, explain, compare, regime-report, diagnose, and campaign operations. It is useful, but it is not the canonical story anymore.

### Planner/orchestration lane

`project/pipelines/run_all.py` and the `make` wrappers still provide planner-owned orchestration and smoke workflows. These support the lifecycle; they do not replace it conceptually.

### Runtime thesis lane

The runtime now loads thesis batches, enforces live approval contracts, and uses explicit deployment states, rather than treating promotion as enough for execution.

### App/plugin lane

`project/apps/chatgpt/` and `plugins/edge-agents/` are interface layers over canonical repo behavior. They should call the canonical services, not redefine promotion or runtime policy.

## Core Objects

### Proposal / Structured Hypothesis

The bounded research spec supplied to discovery. In the code and CLI it is usually called a proposal. In the conceptual model it is the Structured Hypothesis.

### Anchor

The event or transition that defines the onset of the opportunity.

### Filter

The contextual predicate that narrows the Anchor into a tradable context.

### Candidate

A concrete discovered research opportunity with measurable effect estimates, sample statistics, and ranking metadata.

### Validation Bundle

The persisted validation output written under `data/reports/validation/<run_id>/`. Promotion reads this bundle to determine which candidates survived the truth-testing boundary.

### Thesis

The runtime-facing packaged research artifact. A thesis contains lineage, evidence, governance metadata, deployment state, and runtime requirements.

## Artifact Lineage

The most important invariant in the repo is persisted stage lineage:

1. Proposal YAML under `spec/proposals/`
2. Discovery artifacts under `data/reports/phase2/<run_id>/`
3. Validation artifacts under `data/reports/validation/<run_id>/`
4. Promotion artifacts under `data/reports/promotions/<run_id>/`
5. Exported thesis inventory under `data/live/theses/<run_id>/`
6. Runtime load and execution by `project/live/`

This gives the repo:

- auditability
- resumability
- clear stage boundaries
- a place to enforce runtime gates without mutating research artifacts

## Runtime Safety Boundary

The runtime safety boundary is stronger than the older docs implied.

- `deploy live` is blocked unless the exported batch contains `live_enabled` theses
- live theses must satisfy `DeploymentGate`
- live approval metadata and cap profiles are part of the thesis contract
- thesis reconciliation can stop unsafe startup when batch state regresses
- kill switches and scoring floors are part of runtime control, not research ranking

## Adjacent Utility Surfaces

These exist, but they are not new stages:

- `edge ingest ...` for raw market data ingestion
- `edge catalog ...` for run inventory, comparison, and artifact audit
- `edge discover triggers ...` for advanced proposal-generating trigger discovery

## Recommended Reading Order

1. [01_discover.md](01_discover.md)
2. [02_validate.md](02_validate.md)
3. [03_promote.md](03_promote.md)
4. [04_deploy.md](04_deploy.md)
5. [02_REPOSITORY_MAP.md](02_REPOSITORY_MAP.md)
6. [90_architecture.md](90_architecture.md)
