# Artifacts And Interpretation

Artifacts are the source of truth. Logs and summaries only matter when they reconcile with artifacts.

## Read order

For every meaningful run, read in this order:

1. top-level run manifest
2. stage manifests
3. stage logs
4. report artifacts
5. diagnostics

If these disagree, the disagreement is a first-class finding.

## Core artifact paths

### Run and search artifacts

- run manifest: `data/runs/<run_id>/run_manifest.json`
- stage logs: `data/runs/<run_id>/*.log`
- phase-2 search outputs: `data/reports/phase2/<run_id>/search_engine/`
- edge candidates: `data/reports/edge_candidates/<run_id>/`
- event outputs: `data/reports/<detector_reports_dir>/<run_id>/`

### Thesis bootstrap and promotion artifacts

- founding queue: `docs/generated/promotion_seed_inventory.csv`
- thesis testing scorecards: `docs/generated/thesis_testing_scorecards.csv`
- thesis empirical scorecards: `docs/generated/thesis_empirical_scorecards.csv`
- founding evidence bundles: `data/reports/promotions/<thesis_id>/evidence_bundles.jsonl`
- packaging summary: `docs/generated/seed_thesis_packaging_summary.json`
- seed thesis cards: `docs/generated/seed_thesis_cards/<THESIS_ID>.md`
- thesis catalog: `docs/generated/seed_thesis_catalog.md`
- thesis store index: `data/live/theses/index.json`
- packaged thesis batch: `data/live/theses/<batch>/promoted_theses.json`
- overlap graph: `docs/generated/thesis_overlap_graph.json`

## High-value files

Inspect these first for bounded experiment work:

- `run_manifest.json`
- `phase2_candidates.parquet`
- `phase2_diagnostics.json`
- `discovery_quality_summary.json`
- `funnel_summary.json`
- detector event parquet outputs

Inspect these first for thesis bootstrap work:

- `promotion_seed_inventory.md`
- `thesis_testing_summary.md`
- `thesis_empirical_summary.md`
- `founding_thesis_evidence_summary.md`
- `seed_thesis_packaging_summary.md`
- `seed_thesis_catalog.md`
- `thesis_overlap_graph.md`

## The four required conclusions

### Mechanical integrity

Questions:

- Did the required stages run?
- Did expected artifacts exist?
- Did postflight pass?
- Were there fallbacks, sequential degradations, or drift warnings?

Mechanical success means the system executed correctly. It does not prove edge.

### Statistical quality

Questions:

- How many events were detected?
- How many hypotheses were generated?
- How many were feasible?
- How many died on sample size, invalid metrics, or `t_stat`?
- What are `q_value`, after-cost expectancy, and stressed expectancy?

Statistical success means there is evidence. It does not prove packagability.

### Promotion or thesis-class relevance

Questions:

- Did bridge tradability pass?
- Did robustness clear threshold?
- Did stress survival clear threshold?
- Does the evidence support only `candidate`/`tested`, or does it clear `seed_promoted` or `paper_promoted`?

Promotion success means the candidate survived a stricter filter than discovery.

### Packaging relevance

Questions:

- Does a canonical thesis object exist under `data/live/theses/`?
- Does the thesis card explain trigger, invalidation, regimes, and gaps?
- Does the overlap graph now include the thesis in a meaningful node or edge?

Packaging success means downstream live and allocator surfaces can consume the result.

## Typical failure shapes

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

### Promotion failure

Examples:

- poor robustness across regimes
- poor stress survival
- missing holdout or confounder checks
- candidate never became bridge-tradable

### Packaging failure

Examples:

- evidence exists but no canonical thesis object was created
- thesis class is overstated relative to evidence
- overlap graph stays disconnected because the thesis lacks structurally related packaged peers
- live retrieval cannot load the thesis due to missing contract fields

## Example interpretation pattern

Use a structure like this after every run or thesis bootstrap cycle:

- mechanical: "Run completed, artifacts reconciled, postflight passed."
- statistical: "Detector produced 128 events; 80 hypotheses were evaluated; 10 candidates survived phase 2."
- promotion: "One thesis cleared the seed gate but not the paper gate because direct paired-event evidence is still missing."
- packaging: "The thesis store was refreshed and the overlap graph gained two edges."

That format forces you to separate pipeline health from research quality from packaging truth.
