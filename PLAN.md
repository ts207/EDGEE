Thought for 14s

Complete overhaul plan:

0. Objective

Transform the repo into a personal crypto quant platform with one clean loop:

discover → validate → promote → deploy

Everything else becomes either:

data foundation,
shared infrastructure,
or advanced tooling.

This is an architectural refactor, not a full rewrite.
Keep the working engine, artifact system, runtime gating, and data stack.
Overhaul the surface model, contracts, and stage boundaries.

1. What changes fundamentally
Current problem

The repo is structurally capable, but the visible and internal model is too mixed:

trigger mixes anchor, filter, and policy
state and regime are overloaded
discovery is underexposed
validation is fragmented
promotion partly re-runs validation
operator mechanics dominate user intent
Target state

The repo should behave like this:

Discover

Generate broad candidate alpha.

Validate

Determine whether candidate alpha is real, robust, and tradable enough to keep.

Promote

Carry forward a small validated subset into thesis inventory.

Deploy

Run only explicit approved theses in paper/live with basic risk controls.

2. Non-negotiable design rules
Rule 1

Event / transition / sequence are anchors.

Rule 2

State and regime are usually filters, not anchors.

Rule 3

Persistent conditions require sampling policy.

Rule 4

Promotion is not another vague validation layer.

Rule 5

Nothing trades directly from research candidates.

Rule 6

The main user verbs are:

discover
validate
promote
deploy
3. New core research contract

Replace the current hypothesis contract centered on trigger with this:

anchor:
  type: event | transition | sequence | feature_crossing
  ...

filters:
  states: [...]
  regimes: [...]
  feature_predicates: [...]
  context: {...}

sampling_policy:
  mode: episodic | onset_only | once_per_episode | every_n_bars | continuous
  entry_lag: 0|1|...
  overlap_policy: suppress | allow | capped

template:
  id: mean_reversion | continuation | convergence | ...
  params: {...}

direction: long | short
horizon_bars: N
symbol_scope: ...
Why this matters

This fixes the worst conceptual bug in the repo:

STATE stops pretending to be the same kind of object as EVENT
persistent conditions get explicit entry semantics
discovery and validation become interpretable
runtime contracts align with research contracts
4. Semantic cleanup
4.1 Trigger taxonomy

Deprecate generic trigger.type as the main abstraction.

Keep as valid anchors
EVENT
TRANSITION
SEQUENCE
FEATURE_CROSSING only when onset/crossing is explicit
Demote to filters
STATE
static feature predicates
most interaction conditions
4.2 State vs regime

Introduce explicit typed concepts:

market_regime

Broad environment class.
Examples:

high vol
low vol
trend
chop
liquidity stress
state

Operational condition active now.
Examples:

aftershock window
close window
high friction
depth recovery
transition

A change from one state/regime to another.

This should be reflected in spec metadata and validation.

4.3 Typed state subclasses

Split the current mixed state registry into:

regime_state
episode_state
execution_state
context_code

Do not let all of them participate in search the same way.

5. New top-level product structure
5.1 Repo surface

Reframe the repo around these stage directories conceptually:

project/discover/
project/validate/
project/promote/
project/deploy/

You do not have to physically move everything at once.
Start with façade packages that re-export existing modules.

Example
project/discover/__init__.py wraps current discovery/search services
project/validate/__init__.py wraps proposal/preflight/eval/diagnostics
etc.

This lets you change the user model before a deep file migration.

5.2 New docs surface

Replace current top-level documentation narrative with:

docs/00_overview.md
docs/01_discover.md
docs/02_validate.md
docs/03_promote.md
docs/04_deploy.md
docs/05_data_foundation.md
docs/06_core_concepts.md
docs/90_architecture.md
docs/91_advanced_research.md
docs/92_assurance_and_benchmarks.md
5.3 New CLI surface

Expose four first-class commands:

edge discover ...
edge validate ...
edge promote ...
edge deploy ...

Map current commands internally.

Internal mapping
edge discover → broad discovery / phase2 search / workbench / concept search
edge validate → preflight + bounded run + diagnostics + robustness
edge promote → promotion service + thesis packaging/export
edge deploy → thesis loading + paper/live runtime

Keep old commands as compatibility aliases for one migration cycle.

6. Stage-by-stage overhaul
Phase A — Discover
Goal

Make broad discovery the explicit upstream lane.

Keep
search generator
phase2 search engine
candidate discovery services
broad discovery tooling
strategy workbench
concept/search specs
Change
stop centering proposal-first workflow here
require discovery outputs to be candidate-centric, not proposal-centric
attach candidate metadata:
anchor class
filter set
sampling policy
effective sample size
overlap rate
regime coverage
New outputs
candidate_table.parquet
candidate_metadata.json
discovery_summary.json
Acceptance criteria
user can run one discovery command and get ranked candidate sets
state-filtered and event-anchored candidates are clearly distinguished
discovery results no longer imply promotion or deployability
Phase B — Validate
Goal

Centralize truth-testing here.

Move into validation stage logically
preflight
bounded proposal execution
confirmatory reruns
multiplicity/FDR
cost/slippage stress
robustness
time/regime splits
negative controls
diagnostics
Key refactor

Promotion must stop owning core truth-testing.

Validation outputs
validated_candidates.parquet
validation_report.json
rejection_reasons.parquet
effect_stability_report.json
Required checks

Every candidate reaching promotion should already have:

clear anchor semantics
clear sampling policy
effective sample size estimate
overlap/dependence accounting
cost sensitivity
regime/time-slice stability
falsification status
Acceptance criteria
“Is this real enough?” can be answered without invoking promotion
identical candidate semantics across all validation paths
transitions mean the same thing everywhere
Phase C — Promote
Goal

Make promotion a narrow carry-forward decision.

Promotion should do
readiness decision
maturity class assignment
thesis packaging
blueprint packaging
governance metadata
deployment-state defaulting
Promotion should not do
major new truth-testing
hidden re-interpretation of candidate semantics
fallback redefinition of anchors or transitions
Outputs
promoted_candidates.parquet
promotion_audit.json
promoted_theses.json
strategy_blueprints/
Acceptance criteria
every promoted thesis has already passed validation
promotion is explainable as a business/research inventory decision
promotion failure reasons are separate from validation failure reasons
Phase D — Deploy
Goal

Keep runtime simple, explicit, and safe.

Keep
thesis store
retriever
explicit thesis selection
deployment state
paper/live modes
overlap checks
runtime logging
Add early
decay monitor
simple global caps:
max gross exposure
per-symbol cap
per-family cap
max active theses
Do not prioritize yet
full portfolio orchestrator
complex correlation optimizer
multi-venue routing
on-chain integration
Acceptance criteria
paper deployment works from promoted thesis batch only
live deployment requires explicit opt-in and risk caps
runtime can auto-flag decay and downsize/disable
7. Compatibility and migration strategy

Do this as a two-track migration.

Track 1 — façade first

Create:

new docs
new CLI aliases
new stage wrappers
new schema adapters

without breaking existing workflows.

Track 2 — internal cleanup

Then refactor internals gradually:

replace trigger in schemas
harden transition semantics
split state taxonomy
centralize validation
narrow promotion
Compatibility adapter

Support both old and new hypothesis specs during migration:

old trigger specs are normalized into:
anchor
filters
sampling_policy

Warn on:

STATE as anchor
static feature predicate as anchor
ambiguous transition fallback
8. Concrete file-level priorities
Priority 1

Schema and semantics

Touch first:

project/research/agent_io/proposal_schema.py
project/research/agent_io/proposal_to_experiment.py
project/research/search/generator.py
project/research/search/evaluator_utils.py
project/research/discovery.py

Tasks:

add new schema
add old→new normalization
ban ambiguous state-anchor behavior
make transition evaluation strict
add sampling policy contract
Priority 2

Validation boundary

Touch:

project/research/validation/*
project/eval/*
project/operator/stability.py
promotion gating code

Tasks:

centralize validation outputs
move truth-testing out of promotion where possible
make validation artifact bundle canonical
Priority 3

Promotion narrowing

Touch:

project/research/promotion/*
project/research/live_export.py
project/research/export_promoted_theses.py

Tasks:

treat validated candidates as input
assign maturity / readiness
emit thesis packaging cleanly
Priority 4

CLI/docs overhaul

Touch:

project/cli.py
README.md
docs/*

Tasks:

expose four verbs
demote operator internals
publish concept glossary
Priority 5

Deploy hardening

Touch:

project/live/*
project/portfolio/*
live configs

Tasks:

add minimal decay monitor
add simple caps
keep runtime explicit and basic
9. What to delete, demote, or freeze
Freeze immediately

Do not add new major feature families until the semantic overhaul is done:

cross-venue execution
on-chain integration
regime forecasting
self-calibration
institutional reporting
capacity optimizer

These are second-order.

Demote from front-page identity
proposal mechanics
certification flows
benchmark maintenance
ontology grammar internals
synthetic truth tooling
advanced runtime assurance

Keep them, but do not let them define the repo.

10. Testing strategy

You need three test layers.

1. Semantic contract tests

Verify:

event anchor != state filter
transition is strict everywhere
old specs normalize deterministically
sampling policy is required for persistent conditions
2. Stage boundary tests

Verify:

discover emits candidates only
validate emits validated candidates and rejection reasons
promote cannot accept unvalidated candidates
deploy cannot accept raw research candidates
3. End-to-end golden tests

Run:

discover
validate
promote
deploy (paper mode)

and confirm artifact lineage and stage transitions.

11. Success criteria

The overhaul is complete when these are true:

Product clarity

A new user can explain the repo in one sentence:
discover alpha, validate it, promote the few real ideas, deploy them carefully

Semantic clarity

There is no ambiguity between:

anchor
filter
sampling policy
template
Stage clarity

You can answer separately:

discovered?
validated?
promoted?
deployed?
Statistical clarity

State persistence and overlap are explicitly handled.

Runtime clarity

Only promoted theses can reach deployment.

12. Recommended execution order
Sprint 1
freeze feature expansion
write new concept spec
add anchor + filters + sampling_policy
old→new schema normalizer
Sprint 2
strict transition semantics
demote STATE to filter by default
add sampling policy enforcement
semantic tests
Sprint 3
centralize validation artifacts
move validation logic out of promotion where needed
define validation output contract
Sprint 4
narrow promotion contract
clean thesis export handoff
stage-boundary tests
Sprint 5
new CLI verbs
docs rewrite
README overhaul
compatibility aliases
Sprint 6
paper deploy hardening
decay monitor
simple caps
end-to-end golden runs
13. Final recommendation

Do not rebuild the engine.
Do not start with dashboards or new alpha families.
Do not start with portfolio sophistication.

Start with the semantic overhaul:

trigger → anchor + filters + sampling_policy
centralize validation
narrow promotion
expose discover / validate / promote / deploy

That is the highest-leverage path because it fixes:

research correctness,
repo clarity,
false discovery risk,
and live deployment semantics
all at once.

Start with Sprint 1 and freeze all new feature work until the new hypothesis contract is in place