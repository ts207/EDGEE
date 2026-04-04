Assuming Sprint 4 exits with a hardened **validate → promote** boundary, Sprint 5 should be the **surface-area consolidation sprint**: make the repo legible and operable through the four-stage model without changing core research semantics. That matches the original execution order in .

# Sprint 5 — Surface Area Consolidation

Make the repo present and behave as:
**discover → validate → promote → deploy**
for both humans and tooling, while preserving one migration cycle of backward compatibility.

## Sprint 5 objective
Collapse the public interface onto the four-stage model and establish canonical terminology for the entire public surface.

## Known deferred items

### 1. Deferred runtime integration
`edge deploy` is interface-complete in Sprint 5, but execution integration with the live session runner is deferred to Sprint 6 runtime hardening. Commands like `edge deploy paper` will operate as dry-run/eligibility checks.

### 2. Deferred internal terminology cleanup
Sprint 5 guarantees canonical public terminology (README, docs, CLI, schemas). Internal legacy comments and private variable names may persist temporarily where they do not affect external semantics.

## Definition of done
* `edge discover`, `edge validate`, `edge promote`, `edge deploy` are the canonical top-level verbs.
* README and top-level docs explain the four-stage model consistently.
* Public vocabulary is canonical (`anchor`, `filter`, `sampling_policy`, `candidate`, `thesis`).
* Compatibility aliases exist and warn clearly.
* `edge deploy` exposes a truthful deploy interface (inspect/dry-run/status).
* deploy commands reject raw research candidates and accept only promoted theses.
* Internal legacy terminology is allowed only where private and non-contradictory.

---

# Sprint 5 workstreams

## Workstream 1 — Public CLI redesign

### Goal

Expose four first-class verbs exactly as planned:

* `edge discover`
* `edge validate`
* `edge promote`
* `edge deploy`

This is explicitly called out in the overhaul plan. 

### Deliverables

* top-level CLI command group with the four verbs
* stable help text for each verb
* compatibility aliases for old commands
* deprecation warnings with migration guidance
* command examples in help output

### Design rules

Each verb must map to one stage only.

* `discover` produces candidate artifacts only
* `validate` produces validation artifacts only
* `promote` consumes validated candidates only
* `deploy` consumes promoted theses only

No command should blur boundaries.

### Recommended subcommands

#### `edge discover`

* `run`
* `resume`
* `inspect`
* `list-artifacts`

#### `edge validate`

* `run`
* `inspect`
* `report`
* `list-artifacts`

#### `edge promote`

* `run`
* `inspect`
* `export`
* `list-artifacts`

#### `edge deploy`

* `paper`
* `live`
* `status`
* `disable`
* `list-theses`

### Compatibility aliases

Map old commands for one migration cycle:

* old research/discovery/search commands → `edge discover ...`
* old evaluation/preflight/diagnostic commands → `edge validate ...`
* old export/promote commands → `edge promote ...`
* old live runtime selectors/launchers → `edge deploy ...`

### Required behavior

Every alias must:

* still work
* print the new canonical command
* identify sunset version/date
* not silently change semantics

### Exit criteria

* a new user can discover the four verbs from `edge --help`
* each verb has stage-specific help with examples
* aliases are tested and logged

---

## Workstream 2 — README rewrite

### Goal

Replace the repo’s front page identity with the four-stage operating model.

The roadmap explicitly says to overhaul README and demote internal mechanics from front-page identity. 

### Recommended README structure

## 1. One-sentence definition

Example:
“This repo discovers crypto alpha candidates, validates them, promotes the few robust ideas into theses, and deploys approved theses in paper/live mode.”

## 2. Core workflow diagram

Use a compact diagram:

`discover → validate → promote → deploy`

with one-line descriptions.

## 3. What each stage does

* Discover: broad candidate generation
* Validate: falsification and robustness testing
* Promote: inventory/readiness decision
* Deploy: explicit runtime execution of promoted theses

## 4. Core concepts

* anchor
* filters
* sampling_policy
* template
* validated candidate
* promoted thesis

## 5. Quickstart

Minimal end-to-end example:

* run discover
* run validate
* run promote
* run deploy paper

## 6. Repo map

High-level pointers only:

* docs/
* project/research/
* project/live/
* tests/

## 7. Compatibility note

Explain old commands/specs are still supported temporarily.

## 8. What this repo is not

Useful for preventing confusion:

* not auto-trading every research idea
* not promotion-by-backtest
* not portfolio optimizer first
* not on-chain execution framework first

### README anti-patterns to remove

* long theory before workflow
* operator internals near top
* proposal grammar as front-door identity
* benchmarking/certification dominating overview
* mixed terminology for trigger/state/transition/anchor

### Exit criteria

* README first screen explains the system without referencing internals
* quickstart uses only the new verbs
* terminology is consistent with the new schema

---

## Workstream 3 — Full docs rewrite

### Goal

Rebuild docs around the planned documentation surface. The roadmap already specifies the desired docs set. 

### Target docs tree

* `docs/00_overview.md`
* `docs/01_discover.md`
* `docs/02_validate.md`
* `docs/03_promote.md`
* `docs/04_deploy.md`
* `docs/05_data_foundation.md`
* `docs/06_core_concepts.md`
* `docs/90_architecture.md`
* `docs/91_advanced_research.md`
* `docs/92_assurance_and_benchmarks.md`

### What each doc should cover

#### `00_overview.md`

Purpose:

* explain the repo as a staged system
* define lifecycle and artifact lineage
* link to all stage docs

Must include:

* stage diagram
* artifact flow
* minimal end-to-end lifecycle
* boundaries between stages

#### `01_discover.md`

Purpose:

* explain discovery as candidate generation, not promotion

Must include:

* discovery inputs
* candidate outputs
* ranking and metadata
* anchor/filter/sampling usage in discovery
* common failure modes

Must not imply:

* discovery equals truth
* top candidate equals deployable

#### `02_validate.md`

Purpose:

* position validation as the truth-testing stage

Must include:

* required validation checks
* validation artifacts
* rejection reasons
* robustness/falsification/stability interpretation
* what qualifies a candidate for promotion

#### `03_promote.md`

Purpose:

* explain promotion as packaging/governance/inventory

Must include:

* validated input requirement
* readiness classes
* maturity classes
* promotion audit outputs
* promoted thesis structure

Must explicitly say:

* promotion is not major re-validation

#### `04_deploy.md`

Purpose:

* explain explicit deployment of promoted theses only

Must include:

* paper vs live
* thesis selection
* deployment state
* minimal caps and controls
* runtime monitoring/decay handling if already present

#### `05_data_foundation.md`

Purpose:

* explain datasets, feature pipelines, artifacts, storage, lineage

Must include:

* source datasets
* artifact naming
* lineage expectations across stages
* retention and reproducibility rules

#### `06_core_concepts.md`

Purpose:

* become the canonical semantic glossary

Must include:

* anchor
* event
* transition
* sequence
* feature_crossing
* filter
* regime
* state
* sampling_policy
* template
* hypothesis/candidate/thesis
* validation vs promotion

This is the most important semantics doc.

#### `90_architecture.md`

Purpose:

* explain package structure and internal flow for maintainers

Must include:

* module map
* stage wrapper vs internal implementation
* artifact boundaries
* adapters/normalizers
* compatibility layer

#### `91_advanced_research.md`

Purpose:

* deeper material that should not dominate the front door

Examples:

* search generation internals
* ontology/grammar
* synthetic truth tools
* advanced diagnostics

#### `92_assurance_and_benchmarks.md`

Purpose:

* keep assurance content, but demoted

Examples:

* benchmark methodology
* certification-like checks
* regression suites
* audit philosophy

### Documentation rules

* every page starts with stage purpose
* every page has “inputs / outputs / artifacts / failure modes”
* every page uses the new terms only
* old terms appear only in migration notes

### Exit criteria

* docs navigation mirrors the four-stage model
* no top-level doc contradicts the contract model
* internal/advanced material is moved out of front-door flow

---

## Workstream 4 — Canonical glossary and terminology migration

### Goal

Eliminate mixed vocabulary across code comments, docs, CLI help, and artifacts.

This is necessary because the overhaul explicitly centers semantic clarity around `anchor`, `filter`, and `sampling_policy`. 

### Canonical terms

Use these as source of truth:

* **anchor**: event, transition, sequence, feature_crossing
* **filters**: state/regime/context predicates
* **sampling_policy**: episodic/once_per_episode/every_n_bars/etc.
* **candidate**: output of discovery
* **validated candidate**: output of validation
* **promoted thesis**: output of promotion
* **deployment**: runtime use of promoted theses

### Terms to demote

* `trigger` as public master abstraction
* `state` as anchor
* overloaded `proposal` where `candidate` or `thesis` is more accurate
* promotion as “certification” unless that is a strict formal subsystem

### Concrete tasks

* grep repo for old public-facing terms
* update CLI help
* update README/docs/examples
* update comments/docstrings in public modules
* add migration glossary section:

  * trigger → anchor + filters + sampling_policy
  * legacy proposal → structured hypothesis
  * promoted strategy → promoted thesis, if that is the intended term

### Exit criteria

* public docs no longer depend on legacy terminology
* help text and examples are semantically consistent
* migration table exists for old users

---

## Workstream 5 — Example flows and artifact lineage

### Goal

Give users executable examples that match the new product model.

### Required examples

#### Example A — minimal research loop

* discover one candidate set
* validate top candidate(s)
* promote one validated candidate
* deploy in paper mode

#### Example B — validation failure path

* show candidate rejection reasons
* demonstrate no promotion possible

#### Example C — compatibility path

* run old alias
* show mapped canonical command
* show resulting equivalent artifacts

### Artifact lineage spec

Every example should show:

* discovery run ID
* validation run ID
* promotion run ID
* deploy session / thesis selection

### Deliverables

* `examples/` directory or `docs/examples/`
* shell snippets
* expected output samples
* artifact tree samples

### Exit criteria

* a user can follow one example without inspecting internals
* every example reflects true artifact boundaries

---

## Workstream 6 — Compatibility and deprecation framework

### Goal

Preserve stability while pushing users to the new surface.

The roadmap explicitly calls for compatibility aliases for one migration cycle. 

### Required compatibility behavior

For commands:

* old command works
* warning prints once per invocation
* warning includes canonical replacement
* warning includes deprecation phase

For specs:

* old spec still normalizes
* normalization warnings are human-readable
* docs explain when support ends

### Recommended deprecation phases

* **Phase 1**: supported + warned
* **Phase 2**: supported + noisy warning + docs marked legacy
* **Phase 3**: disabled by default behind compatibility flag
* **Phase 4**: removed

### Suggested output format

Use structured deprecation messages:

* legacy command/spec used
* replacement
* current support level
* target removal version

### Exit criteria

* users are never surprised by silently remapped behavior
* all compatibility paths are explicit and test-covered

---

## Workstream 7 — Package façade and navigation cleanup

### Goal

Make the repository navigable according to stages even if internal modules remain where they are.

This follows the roadmap guidance to use façade packages before deeper file migration. 

### Recommended façades

Conceptually expose:

* `project/discover/`
* `project/validate/`
* `project/promote/`
* `project/deploy/`

These can initially re-export existing internals.

### What façades should contain

* stable service entrypoints
* thin adapters
* public data models if appropriate
* minimal docstrings
* no deep logic duplication

### Why this matters

It aligns:

* CLI verbs
* docs
* architecture docs
* import surface

without forcing a large code move.

### Exit criteria

* maintainers can identify stage entrypoints quickly
* docs and imports point to consistent top-level stage packages

---

## Workstream 8 — Test plan for Sprint 5

### Goal

Test the product surface, not just internal logic.

### Test groups

#### 1. CLI contract tests

Verify:

* `edge --help` shows four canonical verbs
* each verb has valid help text
* each alias maps correctly
* deprecation messages appear correctly

#### 2. Documentation consistency tests

Optional but high value:

* link check
* artifact-name consistency scan
* forbidden-term scan for front-door docs
* example command smoke validation

#### 3. Compatibility tests

Verify:

* old commands still produce equivalent results
* old specs normalize with explicit warnings
* compatibility flag behavior is correct

#### 4. Stage-boundary smoke tests

Run:

* discover example
* validate example
* promote example
* deploy paper example

using the new command surface

### Exit criteria

* user-facing surface is test-covered
* migration paths are test-covered
* docs examples do not rot immediately

---

# Sprint 5 structure by week or tranche

## Tranche 1 — vocabulary and interface lock

Do first:

* freeze canonical terms
* define CLI verbs/subcommands/options
* define docs outline
* define alias/deprecation rules

Output:

* Sprint 5 interface spec

## Tranche 2 — CLI implementation

Do next:

* implement top-level command groups
* wire aliases
* standardize help text
* add smoke tests

Output:

* usable new command surface

## Tranche 3 — README and stage docs

Do next:

* rewrite README
* add `00`–`06` docs
* move advanced material to `90+` docs
* add migration glossary

Output:

* coherent documentation portal

## Tranche 4 — examples and compatibility docs

Do next:

* add end-to-end examples
* add old→new migration pages
* add artifact lineage examples

Output:

* adoption support

## Tranche 5 — cleanup and hardening

Do last:

* terminology sweep
* docstring/help consistency
* link check
* example smoke tests
* release notes / changelog entry

Output:

* stable release candidate

---

# Concrete tickets

## CLI

* create top-level stage command groups
* add subcommands per stage
* centralize common run/artifact options
* add deprecation alias registry
* standardize help formatter
* add stage-specific examples to `--help`

## Docs

* rewrite README
* add overview doc
* add discover/validate/promote/deploy docs
* add data foundation doc
* add core concepts doc
* add architecture doc
* add advanced research doc
* add assurance/benchmarks doc
* add migration guide

## Examples

* minimal full pipeline example
* rejected candidate example
* compatibility alias example

## Terminology

* replace public `trigger` master usage
* replace ambiguous `proposal` usage where needed
* add glossary
* add old→new term mapping table

## Tests

* CLI help tests
* alias/deprecation tests
* docs link checks
* example smoke tests
* terminology lint checks for front-door docs

---

# Risks and how to control them

## Risk 1 — Sprint 5 turns into a hidden architecture rewrite

Control:

* use façades and aliases
* do not move deep internals unless required

## Risk 2 — docs get ahead of actual behavior

Control:

* every example must be executable
* write docs from real command outputs
* add smoke tests for examples

## Risk 3 — compatibility layer becomes permanent

Control:

* attach explicit deprecation phases
* mark all legacy docs as temporary
* add removal target in changelog

## Risk 4 — terminology drift persists

Control:

* create one canonical glossary first
* run terminology sweep after README/docs rewrite
* add simple lint/search checks

## Risk 5 — help text and artifacts still expose old mental models

Control:

* use stage-specific nouns everywhere
* forbid mixed terms in CLI templates
* review generated example outputs

---

# Definition of done

Sprint 5 is done when all of the following are true:

* README presents the repo through the four-stage model
* `edge discover|validate|promote|deploy` are the canonical top-level verbs
* stage docs exist and match real behavior
* old commands still work through a documented compatibility layer
* migration guidance from old terms/commands exists
* examples run through the new surface
* docs/help/examples use consistent concepts:

  * anchor
  * filters
  * sampling_policy
  * candidate
  * validated candidate
  * promoted thesis
  * deploy

---

# Strongest recommendation on sequencing

Start Sprint 5 with a short **interface specification document** before touching code:

1. canonical CLI verbs and subcommands
2. canonical terminology table
3. canonical docs tree
4. alias/deprecation policy
5. example artifact lineage

Then implement CLI first, README/docs second, compatibility/tests third.

That sequence minimizes rework because Sprint 5 is primarily a **surface contract sprint**, not a logic sprint.
