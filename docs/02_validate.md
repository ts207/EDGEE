# Stage 2: Validate

Validate is the truth-testing boundary between discovery and promotion. A discovered Candidate is only a research lead. Validation is where the repo decides whether that lead survives enough falsification pressure to be packaged further.

## What Validate Does

Validation turns discovery artifacts into a canonical validation bundle by checking:

- effect stability across time and regimes
- cost survival and expectancy robustness
- sample adequacy and support quality
- rejection reasons and failure auditability

This stage is the main anti-noise boundary. Promotion should consume validation outputs, not raw discovery enthusiasm.

## Canonical Commands

### Run validation

```bash
python -m project.cli validate run --run_id <run_id>
```

or:

```bash
make validate RUN_ID=<run_id>
```

### Build regime/stability reports

```bash
python -m project.cli validate report --run_id <run_id>
```

### Write negative-result diagnostics

```bash
python -m project.cli validate diagnose --run_id <run_id>
```

### List validation artifacts

```bash
python -m project.cli validate list-artifacts --run_id <run_id>
```

## Main Code Surfaces

- `project/validate/`
- `project/research/services/evaluation_service.py`
- `project/research/validation/`
- `project/research/validation/result_writer.py`
- compatibility reporting in `project/operator/stability.py`

## Canonical Outputs

Validation writes under:

- `data/reports/validation/<run_id>/`

The important files are:

- `validation_bundle.json`
- `validated_candidates.parquet`
- `rejection_reasons.parquet`
- `validation_report.json`
- `effect_stability_report.json`

Promotion logic loads the validation bundle from this directory. That file is the boundary object that says "these candidates survived stage 2."

## What The Validation Bundle Means

The bundle contains:

- validated candidates
- rejected candidates
- inconclusive candidates where applicable
- summary metrics
- effect stability report payload

That lets downstream logic distinguish between:

- nothing was discovered
- candidates existed but validation rejected them
- candidates survived but were downgraded by later gates

## Typical Rejection Reasons

Common reasons exposed by validation or downstream reporting include:

- `failed_stability`
- `failed_cost_survival`
- `insufficient_sample_support`
- `loso_unstable`
- `setup_match_below_floor`

The exact mix depends on the validation path and evidence bundle contents, but the important point is that rejection is explicit and persisted, not inferred later from missing outputs.

## Statistical Gate Defaults

The main thresholds live in `spec/gates.yaml`.

Current defaults documented by the codebase include:

| Gate | Value |
|------|-------|
| Minimum t-statistic | 2.0 |
| Maximum BH-adjusted q-value | 0.05 |
| Minimum after-cost expectancy | 0.1 bps |
| Minimum regime ESS coverage | 3 regimes |
| Conditioned bucket floor | 75 observations |
| Minimum sample size | 50 events |

Important current invariant:

- gate p-values are computed on train plus validation observations
- held-out test observations are reported separately and are not used for gate decisions

## Report And Diagnose Boundaries

The validation stage has two report-like surfaces that older docs blurred together:

### `validate report`

Builds regime/stability reporting for an existing run.

### `validate diagnose`

Writes structured negative-result diagnostics for an existing run.

These correspond conceptually to the old `operator regime-report` and `operator diagnose` commands, but the canonical doc path is the `validate` command family.

## Behavior When Nothing Survives

Validation can complete successfully and still yield zero validated candidates.

That is not the same as a crashed run. It means:

- discovery artifacts existed
- validation executed
- nothing survived the gate

Promotion should treat that as "no promotable candidates," not as a missing artifact boundary.

## Why This Stage Matters Operationally

Without stage-2 discipline, the repo loses:

- a durable falsification boundary
- an auditable explanation for why candidates failed
- a stable handoff into promotion
- protection against promoting discovery noise directly into runtime-facing artifacts
