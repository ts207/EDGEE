# Stage 1: Discover

Discover is the bounded research issuance stage. It takes a proposal YAML, resolves its search space against the registry, runs the canonical phase-2 discovery engine, and writes the candidate artifacts that the rest of the lifecycle depends on.

## What Discover Means In Edge

Discover is not "run arbitrary strategy search." In the current repo it means:

- freeze a proposal
- anchor the proposal to explicit event and context semantics
- execute the planner-owned discovery path
- write candidates and diagnostics as persisted artifacts

The main research objects here are:

- Proposal / Structured Hypothesis
- Anchor
- Filter
- Sampling Policy
- Candidate

## Canonical Commands

### Plan without executing

```bash
python -m project.cli discover plan --proposal spec/proposals/<proposal>.yaml
```

or:

```bash
make discover PROPOSAL=spec/proposals/<proposal>.yaml DISCOVER_ACTION=plan
```

### Execute a discovery run

```bash
python -m project.cli discover run --proposal spec/proposals/<proposal>.yaml
```

or:

```bash
make discover PROPOSAL=spec/proposals/<proposal>.yaml DISCOVER_ACTION=run
```

### List discovery artifacts

```bash
python -m project.cli discover list-artifacts --run_id <run_id>
```

## Main Inputs

### Proposal YAML

The proposal is the bounded experiment contract. In practical terms it tells discovery:

- which Anchor family to test
- which Filters or regime predicates must be true
- which scope, horizon, and search dimensions are allowed
- where the registry root is
- how to name or persist the run

### Registry Surfaces

Discovery depends on the event / domain registry lineage:

- authored event specs in `spec/events/*.yaml`
- compiled event registry in `spec/events/event_registry_unified.yaml`
- projected domain graph in `spec/domain/domain_graph.yaml`

If those drift, discovery semantics drift too.

### Data Root

Most users let the repo default the data root, but discovery can be pointed at another root with `--data_root`.

## Main Code Surfaces

- `project/cli.py`
- `project/discover/`
- `project/research/phase2_search_engine.py`
- `project/research/services/candidate_discovery_service.py`
- `project/research/agent_io/`
- `project/operator/preflight.py` and `project/operator/proposal_tools.py` for compatibility helpers

## Main Outputs

The canonical helper path for candidate output is:

- `data/reports/phase2/<run_id>/phase2_candidates.parquet`

Other discovery-adjacent outputs commonly include:

- `data/reports/phase2/<run_id>/phase2_diagnostics.json`
- `data/reports/edge_candidates/<run_id>/...`
- run manifests under `data/runs/<run_id>/`

The canonical artifact helper paths point only at the flat phase-2 layout. Older runs that still use nested legacy layouts should be inspected through explicit compatibility helpers rather than through the default catalog path.

## Stable Default Behavior

The stable default discovery path currently assumes:

- a bounded proposal, not open-ended search
- planner-owned phase-2 discovery
- flat search expansion
- discovery v2 scoring
- persisted diagnostics and rejection reason counts
- downstream validation as the next required boundary

Current ranking logic considers, at a high level:

- statistical strength
- support and sample quality
- precheck failures
- tradability constraints
- overlap and novelty pressure
- fold and split stability

## What Discover Does Not Do

Discover does not:

- validate a claim for deployment on its own
- create a runtime-ready thesis batch
- bypass promotion because a candidate looks good
- turn trigger mining outputs directly into production registry definitions

## Advanced Trigger Discovery Lane

The repo now has an internal trigger-discovery lane under:

```bash
python -m project.cli discover triggers ...
```

This lane is proposal-generating research, not the default lifecycle path.

Supported commands include:

- `parameter-sweep`
- `feature-cluster`
- `report`
- `emit-registry-payload`
- `list`
- `inspect`
- `review`
- `approve`
- `reject`
- `mark-adopted`

The important operational boundary is:

- trigger discovery can suggest registry payloads
- it does not automatically alter the registry
- it does not bypass validation or promotion
- manual review and governance still apply

## Compatibility Surfaces

The older `operator` lane still exists for:

- `operator preflight`
- `operator plan`
- `operator run`
- `operator lint`
- `operator explain`

Those commands wrap the same bounded-research model. New docs should teach `discover` first.

## Common Failure Modes

### Proposal or registry mismatch

The proposal resolves to invalid anchors, invalid fields, or a stale registry assumption.

### Data coverage failure

Required symbols, features, or time windows are missing under the active data root.

### Thin event support

The Anchor exists, but not often enough to support credible discovery statistics.

### No surviving candidates

Discovery runs successfully, but all candidates fail minimum filters or ranking thresholds.

### Legacy path confusion

Older runs may have artifacts in fallback locations. Use explicit compatibility helpers or `discover list-artifacts` rather than guessing directory layouts by hand.
