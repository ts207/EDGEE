# Artifacts And Interpretation

Artifacts are the source of truth. Logs and summaries only matter when they reconcile with artifacts.

## Read Order

For every meaningful run, read in this order:

1. top-level run manifest
2. stage manifests
3. stage logs
4. report artifacts
5. diagnostics

If these disagree, the disagreement is a first-class finding.

## Core Artifact Paths

- run manifest: `data/runs/<run_id>/run_manifest.json`
- stage logs: `data/runs/<run_id>/*.log`
- phase-2 search outputs: `data/reports/phase2/<run_id>/search_engine/`
- edge candidates: `data/reports/edge_candidates/<run_id>/`
- event outputs: `data/reports/<detector_reports_dir>/<run_id>/`

## High-Value Files

Inspect these first:

- `run_manifest.json`
- `phase2_candidates.parquet`
- `phase2_diagnostics.json`
- `discovery_quality_summary.json`
- `funnel_summary.json`
- detector event parquet outputs

## The Three Required Conclusions

### Mechanical Integrity

Questions:

- Did the required stages run?
- Did expected artifacts exist?
- Did postflight pass?
- Were there fallbacks, sequential degradations, or drift warnings?

Mechanical success means the system executed correctly. It does not prove edge.

### Statistical Quality

Questions:

- How many events were detected?
- How many hypotheses were generated?
- How many were feasible?
- How many died on sample size, invalid metrics, or `t_stat`?
- What are `q_value`, after-cost expectancy, and stressed expectancy?

Statistical success means there is evidence. It does not prove deployability.

### Deployment Relevance

Questions:

- Did bridge tradability pass?
- Did robustness clear threshold?
- Did stress survival clear threshold?
- Is the candidate stable enough for promotion-oriented follow-up?

Deployment success means the candidate survived a stricter filter than discovery.

## Typical Failure Shapes

### Mechanical failure

Examples:

- missing artifacts
- stale path assumptions
- postflight causality violations
- failed stage contracts

### Statistical failure

Examples:

- low `n`
- weak `t_stat`
- failed FDR control
- positive in one bucket but unsupported broadly

### Deployment failure

Examples:

- poor robustness across regimes
- poor stress survival
- microstructure risk controls failed
- candidate never became bridge-tradable

## Example Interpretation Pattern

Use a structure like this after every run:

- mechanical: "Run completed, artifacts reconciled, postflight passed."
- statistical: "Detector produced 128 events; 80 hypotheses were evaluated; 10 candidates survived phase 2."
- deployment: "No candidates passed bridge because robustness and stress survival were below threshold."

That format forces you to separate pipeline health from research quality.
