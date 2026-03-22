# Artifacts and Contracts

Artifacts are contracts, not incidental files. A run is trustworthy only when expected artifacts exist and reconcile with the manifests and logs that describe them.

---

## Artifact Layers

The output of any run is organized across four layers. Read them in trust order.

### 1. Run Layer — `data/runs/<run_id>/`

The top-level record of what was planned and what happened.

Contains:
- Overall run status
- Planned stages
- Per-stage manifests
- Stage logs
- Reconciliation checks

### 2. Research Report Layer — `data/reports/`

The research output produced by phase 2 and promotion.

Contains:
- Phase 2 outputs and candidate exports
- Discovery summaries
- Promotion audits
- Benchmark and comparison reports

### 3. Event Layer — `data/events/<run_id>/`

Per-run detector output.

Contains:
- Event materializations
- Event-level debugging artifacts
- Detector registry and event report verification

### 4. Lake Layer — `data/lake/runs/<run_id>/`

The cleaned and feature-enriched input data consumed by research.

Contains:
- Cleaned bars
- Feature tables
- Context and market-state features
- Rollups used downstream

---

## Trust Order

When inspecting a run, read evidence in this order and stop at the first disagreement:

1. Top-level run manifest
2. Stage manifests
3. Stage logs
4. Report artifacts
5. Generated diagnostics

**If any of those sources disagree, the disagreement is a first-class finding.** Do not explain it away. Stop and investigate.

---

## Core Contract Expectations

A healthy run satisfies all of these:

- Manifests match actual stage outcomes.
- Stage success implies the expected outputs exist on disk.
- Zero-candidate no-op stages are still successful if that is the intended behavior.
- Exported candidates carry all required downstream fields.
- Split-aware metrics survive into promotion-facing artifacts.
- Generated diagnostics agree with the code and registry surfaces that produced them.

---

## Failure Classes

### Mechanical Contract Failure

The most common and easiest to detect:
- Missing input artifact
- Stale manifest after a replay
- Success status with missing outputs
- Logs that disagree with manifests

### Semantic Contract Failure

Harder to catch, more damaging:
- A field exists but means the wrong thing
- Units have drifted from the canonical definition
- Train metrics were computed over all rows (lookahead)
- Regime-conditioned outputs contain duplicate unconditional rows

### Statistical Contract Failure

Requires explicit checks:
- Zero validation or test support
- Invalid multiplicity interpretation
- No cost-surviving expectancy despite positive raw metrics

---

## Required Checks Before Trusting a Run

- [ ] Top-level run status matches stage outcomes.
- [ ] Candidate counts reconcile across summaries and exports.
- [ ] Declared feature-stage inputs match what the implementation actually reads.
- [ ] Split counts exist where required (non-zero validation and test).
- [ ] Expected artifacts exist where manifests say they do.
- [ ] Detector ownership, registry, and coverage diagnostics agree.
- [ ] Warning noise does not hide runtime faults.

---

## Response to Contract Breakage

When contracts break:

1. Stop broad experimentation.
2. Isolate the broken path.
3. Repair the propagation or bookkeeping issue.
4. Replay the smallest affected chain.
5. Resume interpretation only after reconciliation.

**Do not call a run good because the command exited with code `0`.** Call it good only when artifacts exist, reconcile, and are being interpreted at the correct layer.
