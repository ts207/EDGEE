Use this as the coding-agent work order for Discovery v2 stabilization.
Mission
Stabilize the current discovery stack.
Do not add new discovery features.
Do not change runtime, export, thesis lineage, proposal schema, or deploy semantics.
This pass is only for:

evidence
interpretability
mode classification
default freeze
regression protection

The repo already contains:

v2 discovery scoring
repeated walk-forward support
concept-ledger scaffolding
hierarchical search scaffolding
diversification scaffolding
trigger-discovery lane

This pass must determine whether those changes are:

helping
understandable
safe to keep as defaults
clearly separated into stable vs experimental


Non-negotiable boundaries
Must not change

runtime thesis selection behavior
deployment-state permission model
export/runtime registration flow
proposal front door
single-hypothesis loader/adapter
public CLI stage model
thesis artifact format

Must not add

new scoring factors
new trigger types
new hierarchical stages
new ledger concepts
new diversification logic
new runtime/deploy features

Allowed changes

diagnostics
benchmark harness
report generation
documentation classification
config comments/default assertions
tests


Deliverables
The coding agent must deliver all 5 of these.
Deliverable 1 — Benchmark harness
A reproducible benchmark script + benchmark spec that compares:

legacy ranking
v2 ranking
optional ledger-adjusted ranking

on a fixed set of historical discovery slices.
Deliverable 2 — Score decomposition artifact
Every candidate must expose the components that produced its rank.
Deliverable 3 — Diagnostics summaries
Human-readable run-level diagnostics showing:

rank movers
penalty categories
promotion density by rank bucket
overlap concentration
placebo/tradability effects

Deliverable 4 — Stable vs experimental classification
Docs and config comments must clearly mark:

stable
experimental / opt-in
compatibility-only

Deliverable 5 — Regression tests
Tests must protect:

mode defaults
presence of decomposition artifacts
benchmark harness output contract
public/stable vs experimental separation


Task units
Task Unit 1 — Map the current discovery stack
Objective
Produce a short internal map before changing anything.
Read first

project/research/phase2_search_engine.py
project/research/services/candidate_discovery_scoring.py
project/research/services/candidate_discovery_diagnostics.py
project/research/validation/splits.py
project/research/benchmarks/ if present
spec/search_space.yaml
project/configs/discovery_scoring_v2.yaml
project/configs/discovery_ledger.yaml
project/configs/discovery_validation.yaml

Must answer

where ranking mode is selected
where candidate component scores are computed
where diagnostics are persisted
which fields already exist for decomposition
which discovery features are default-on vs opt-in

Stop condition
A one-page internal map exists and no code has been changed yet.
Rollback boundary
None. Read-only.

Task Unit 2 — Add benchmark harness
Objective
Create a fixed, reproducible benchmark runner for discovery ranking comparison.
Files to add
Suggested:

project/research/benchmarks/discovery_benchmark.py
project/scripts/run_discovery_benchmark.py

Expected inputs
A committed benchmark spec containing a fixed set of benchmark runs/proposals.
Suggested file:

project/research/benchmarks/discovery_benchmark_spec.yaml

Benchmark set requirements
Include 3–5 cases:

one simple event-driven case
one medium-complexity case
one noisy/high-candidate case
one historically promotable case
one historically weak case

Required modes
Support at least:

legacy ranking
v2 ranking
optional ledger ranking if flag exists

Required outputs
Write to something like:
data/reports/discovery_benchmarks/<benchmark_id>/

Artifacts:

rank_comparison.parquet
rank_comparison.csv
rank_movers.csv
promotion_outcome_comparison.csv
benchmark_summary.json
benchmark_summary.md

Stop condition
Benchmark harness runs end-to-end on a tiny internal benchmark spec and emits all required files.
Rollback boundary
If harness requires changing core scoring logic, stop and report scope breach.
Only reporting/driver code is allowed here.

Task Unit 3 — Complete per-candidate score decomposition
Objective
Make every discovery rank explainable.
Files to edit

project/research/services/candidate_discovery_scoring.py
project/research/phase2_search_engine.py

Required candidate columns
Ensure candidate artifacts include these fields if applicable:

significance_component
support_component
falsification_component
tradability_component
novelty_component
overlap_penalty
fragility_penalty
fold_stability_component
ledger_penalty
discovery_quality_score

Required comparison columns
When relevant:

legacy_rank
v2_rank
ledger_rank
rank_delta_legacy_to_v2
rank_delta_v2_to_ledger

Rule
Do not change score formulas in this pass unless a field is missing and impossible to surface otherwise.
This is exposure, not retuning.
Stop condition
A single candidate row can be fully explained from artifact columns alone.
Rollback boundary
If adding decomposition columns changes ranking behavior, revert that part and keep only additive artifact fields.

Task Unit 4 — Upgrade diagnostics summaries
Objective
Make discovery runs interpretable at run level, not just candidate level.
Files to edit

project/research/services/candidate_discovery_diagnostics.py

Required outputs
Add summaries for:

top positive rank movers
top negative rank movers
count demoted by placebo
count demoted by tradability
count demoted by overlap
count demoted by fold stability
count demoted by ledger penalty if enabled
promotion density by rank bucket
overlap concentration in top-N
number of unique event/template families in top-N

Human-readable reason outputs
Include:

rank_primary_reason
demotion_reason_codes
falsification_reason
tradability_reason
overlap_reason
fold_reason
ledger_reason

Stop condition
A reviewer can explain why the top-N changed between legacy and v2 without reading code.
Rollback boundary
If diagnostics require changing candidate generation or scoring formulas, stop and report scope breach.

Task Unit 5 — Classify stable vs experimental modes
Objective
Prevent future confusion about what is canonical.
Files to edit

docs/01_discover.md
docs/90_architecture.md
docs/91_advanced_research.md
docs/93_trigger_discovery.md
maybe docs/README.md

Config files to annotate

spec/search_space.yaml
project/configs/discovery_scoring_v2.yaml
project/configs/discovery_ledger.yaml
project/configs/discovery_validation.yaml

Required classification
Mark features as:
Stable

flat search
v2 scoring
current canonical discovery path
standard diagnostics

Experimental / opt-in

hierarchical search
concept-ledger scoring
diversified shortlist
trigger-discovery lane

Compatibility-only

legacy proposal shape
deprecated operator/pipeline surfaces if referenced here

Stop condition
A maintainer can tell in under 10 seconds whether a feature is stable or experimental.
Rollback boundary
No structural code changes allowed in this task. Docs/comments/tests only.

Task Unit 6 — Freeze defaults with tests
Objective
Make current discovery defaults explicit and hard to regress.
Files to inspect/edit

spec/search_space.yaml
project/configs/discovery_scoring_v2.yaml
project/configs/discovery_ledger.yaml
project/configs/discovery_validation.yaml

Default posture to preserve
Unless code proves otherwise, freeze this posture:
Default on

v2 discovery scoring
current standard validation path
standard diagnostics

Default off

hierarchical search
ledger-adjusted ranking
diversified shortlist
trigger-discovery as canonical path

Tests to add
Suggested:

project/tests/research/test_discovery_modes.py

Assertions:

hierarchical mode default is off
ledger scoring default is off
diversified shortlist default is off
v2 scoring default matches intended current baseline

Stop condition
If someone changes a discovery default later, tests fail loudly.
Rollback boundary
Do not change defaults in this pass unless current docs and config are provably contradictory.
If contradictory, fix the docs first and report the inconsistency.

Task Unit 7 — Add benchmark and artifact contract tests
Objective
Protect the stabilization outputs themselves.
Tests to add
Suggested:

project/tests/research/test_discovery_benchmark.py
extend project/tests/research/test_candidate_discovery_diagnostics.py

Benchmark harness smoke test
Verify:

benchmark script runs on a tiny fixture
emits required files
summary JSON/MD exist
rank comparison artifact contains required columns

Decomposition contract test
Verify candidate outputs include:

component fields
score field
rank comparison fields when applicable

Diagnostics contract test
Verify diagnostics artifact includes:

rank movers
penalty counts
stable summary keys

Stop condition
The benchmark and diagnostics surfaces are test-protected.
Rollback boundary
If the test fixture requires deep runtime/export interactions, stop and replace with a smaller research-only fixture.

Required artifact contracts
Candidate artifact must expose
At minimum:

raw score / rank fields
component score fields
reason-code fields
comparison rank fields where applicable

Diagnostics artifact must expose
At minimum:

benchmark identifier
scoring mode
top rank movers
penalty counts
promotion density summary
overlap concentration summary

Benchmark summary must expose
At minimum:

benchmark case id
mode compared
top-N promotion density delta
placebo-like candidate reduction
overlap concentration delta
recommendation / conclusion field


Review checklist for coding agent
Before reporting completion, answer these explicitly:

Which file now runs the discovery benchmark?
Where are benchmark cases specified?
Which artifact contains per-candidate decomposition?
Which artifact contains run-level rank mover summaries?
Which discovery features are now labeled stable?
Which discovery features are now labeled experimental?
What defaults are now protected by tests?
Did any runtime/export/proposal behavior change?
What historical benchmark cases were used?
Did v2 improve promotion density or only rearrange candidates?


Hard stop conditions
Stop immediately and report instead of continuing if any task requires:

changing runtime thesis behavior
changing export/runtime registration
changing proposal loading/normalization
changing deploy permission semantics
changing thesis artifacts
adding new scoring factors
retuning discovery weights
turning on experimental modes by default

That would be a scope breach.

Rollback strategy
Safe rollback unit A
Benchmark harness only

can be reverted independently

Safe rollback unit B
Diagnostics enrichment only

can be reverted independently

Safe rollback unit C
Docs/config comments/test coverage only

can be reverted independently

Safe rollback unit D
Additive candidate decomposition columns

can be reverted independently if they accidentally alter ranking

Never mix ranking formula changes into this stabilization pass.
If they happened accidentally, revert those first.

Execution order
Do these in exactly this order:

map current discovery stack
add benchmark harness
expose full score decomposition
enrich diagnostics
classify stable vs experimental in docs/config
freeze defaults with tests
add benchmark/diagnostic contract tests
run benchmark report
summarize findings

This order keeps the pass additive and observable.

Test commands
Focused research tests first:
TMPDIR=/home/irene/Edge/tmp .venv/bin/pytest -s -q \
  project/tests/research

If benchmark tests are separate:
TMPDIR=/home/irene/Edge/tmp .venv/bin/pytest -s -q \
  project/tests/research/test_discovery_benchmark.py \
  project/tests/research/test_candidate_discovery_diagnostics.py \
  project/tests/research/test_discovery_modes.py

Then contract verification:
TMPDIR=/home/irene/Edge/tmp .venv/bin/python -m project.scripts.run_researcher_verification --mode contracts

If a benchmark runner exists after implementation:
TMPDIR=/home/irene/Edge/tmp .venv/bin/python -m project.scripts.run_discovery_benchmark


Completion criteria
This stabilization pass is complete when:

benchmark harness exists and runs
benchmark artifacts are emitted
candidate score decomposition is fully visible
diagnostics explain rank changes
stable vs experimental discovery modes are documented
defaults are frozen and test-protected
no runtime/export/proposal/deploy behavior changed
a short benchmark conclusion exists stating whether v2 appears better, worse, or inconclusive


Best final deliverable
The most valuable final output is a short report with:

benchmark cases used
old vs new top-N behavior
rank mover examples
promotion density change
placebo/tradability/overlap effects
recommendation:

keep v2 as default
keep experimental modes off
do or do not enable ledger mode next



