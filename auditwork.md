# Patch plan with tickets

This is the shortest ticket set that closes the highest-risk findings first while preserving dependency order from the audit. The plan is arranged as:

* **Phase 0**: establish a clean, reproducible baseline
* **Phase 1**: close critical runtime and promotion-path failures
* **Phase 2**: make live operation safe
* **Phase 3**: restore detector / semantic trust
* **Phase 4**: harden governance and regression coverage

The plan below assumes GitHub issues, but it also maps cleanly to Jira epics/tasks.

---

## Phase 0 — Stabilize the baseline

### TICKET-001 — Clean working tree and commit semantic surface changes

**Priority:** P0
**Why:** The audit found uncommitted changes in `feature_schema_v2.json`, `template_verb_lexicon.yaml`, and the phase-2 feature-serving path, which degrades reproducibility and audit fidelity.
**Scope:**

* Commit or revert:

  * `feature_schema_v2.json`
  * `template_verb_lexicon.yaml`
  * `project/pipelines/research/phase2_search_engine.py`
  * deletion/refactor around `search_feature_frame.py`
* Make the change atomic
* Add or update a behavioral-equivalence test for the phase-2 feature-serving path

**Acceptance criteria:**

* `git status` is clean
* phase-2 path has an equivalence or contract test
* regenerated artifacts are based on the committed tree

**Depends on:** none

---

### TICKET-002 — Regenerate machine-owned artifacts from clean baseline

**Priority:** P0
**Why:** Generated artifacts were stale relative to the audited working tree.
**Scope:**

* Run `scripts/regenerate_artifacts.sh`
* Refresh `docs/generated/**`
* Verify architecture, ontology, and detector coverage artifacts align with committed code

**Acceptance criteria:**

* artifact regeneration succeeds from clean tree
* generated files are committed
* no stale generated outputs remain in diff

**Depends on:** TICKET-001

---

### TICKET-003 — Add full dependency lock and pin dev toolchain

**Priority:** P1
**Why:** Only a partial set of dependencies is pinned; `pyright` is unpinned, weakening reproducibility.
**Scope:**

* Generate full lockfile
* Pin `pyright`
* Add pytest config into `pyproject.toml` or equivalent
* Standardize install/test commands against lockfile

**Acceptance criteria:**

* new environment can be recreated deterministically
* CI and local workflow use same lock source
* pyright version is explicit

**Depends on:** TICKET-001

---

## Phase 1 — Close critical promotion and runtime failures

### TICKET-004 — Enforce non-zero embargo in time splits

**Priority:** P0
**Why:** `embargo_days=0` was identified as part of the compound spurious promotion path.
**Scope:**

* Set default `embargo_days >= 5` in `build_time_splits`
* Document rationale
* Update tests and affected docs

**Acceptance criteria:**

* default split builder uses non-zero embargo
* tests fail if zero embargo is reintroduced as default

**Depends on:** none

---

### TICKET-005 — Raise minimum validation/test sample floors

**Priority:** P0
**Why:** `min_validation_n_obs: 2` and `min_test_n_obs: 2` make split-level evidence effectively meaningless.
**Scope:**

* Raise standard policy minimums to at least 10/10
* Update `spec/gates.yaml`
* Review downstream configs overriding weak floors

**Acceptance criteria:**

* standard gate profile enforces updated minimums
* promotion-path tests reject candidates below new floors

**Depends on:** none

---

### TICKET-006 — Mark reduced-evidence promotions explicitly

**Priority:** P0
**Why:** `allow_discovery_promotion=True` is a real reachable path and needs explicit evidence labeling.
**Scope:**

* Add `[REDUCED_EVIDENCE]` flag to promotion artifacts and reports
* Make test split the primary OOS window in this path
* Distinguish shadow vs deployable / reduced-evidence outputs visually and structurally

**Acceptance criteria:**

* every same-lineage promotion artifact is flagged
* report surfaces clearly distinguish reduced-evidence results

**Depends on:** TICKET-004, TICKET-005

---

### TICKET-007 — Replace or rename inert `oos_validation_pass`

**Priority:** P0
**Why:** `oos_validation_pass` is currently unconditionally `True`, creating a phantom safety surface.
**Scope:**

* Either implement real OOS validation lookup
* Or rename it to an explicit placeholder and block it from production-path blueprints
* Update blueprint validation and examples

**Acceptance criteria:**

* no misleading always-true OOS signal remains on production path
* tests prove runtime behavior is not silently unconditional

**Depends on:** none

---

### TICKET-008 — Fix `exits.py` direct invocation failure

**Priority:** P0
**Why:** `project/strategy/runtime/exits.py` raises `NameError` due to missing `Tuple` import.
**Scope:**

* Add missing import
* Add direct-call test for `check_exit_conditions()`

**Acceptance criteria:**

* module imports cleanly
* direct invocation test passes

**Depends on:** none

---

### TICKET-009 — Replace PIT template validation stubs with real checks

**Priority:** P0
**Why:** `validate_pit_invariants()` and `check_closed_left_rolling()` currently always return `True`. 
**Scope:**

* Implement monotonic-index and closed-left-window checks
* Fail template evaluation on PIT validation failure
* Add adversarial tests

**Acceptance criteria:**

* invalid PIT fixture fails
* valid PIT fixture passes
* template execution is blocked on PIT failure

**Depends on:** none

---

## Phase 2 — Make live operation safe

### TICKET-010 — Wire data health failures into kill-switch

**Priority:** P0
**Why:** `STALE_DATA` exists but is not triggered by the health loop; reconnect exhaustion also does not trigger `EXCHANGE_DISCONNECT`.
**Scope:**

* Trigger `STALE_DATA` from unhealthy health-check result
* Trigger `EXCHANGE_DISCONNECT` on reconnect exhaustion
* Add minimum integrity checks beyond freshness:

  * timestamp monotonicity
  * basic price anomaly guard

**Acceptance criteria:**

* stale/corrupt feed activates kill-switch
* reconnect exhaustion activates kill-switch
* tests cover both paths

**Depends on:** none

---

### TICKET-011 — Implement real `UnwindOrchestrator.unwind_all()`

**Priority:** P0
**Why:** The kill-switch blocks new orders but cannot close existing positions because unwind is a stub.
**Scope:**

* Cancel open orders
* Flatten open positions via OMS/exchange adapter
* Persist unwind state/results
* Register and verify callback path from kill-switch trigger

**Acceptance criteria:**

* kill-switch activation attempts actual flattening
* callback registration exists at startup
* unwind behavior is covered by integration test/mocks

**Depends on:** TICKET-010

---

### TICKET-012 — Add startup exchange position reconciliation

**Priority:** P0
**Why:** Live state is restored from JSON snapshot without reconciliation to exchange truth.
**Scope:**

* Fetch exchange account/position snapshot at startup
* Diff against persisted local state
* Block trading startup on unreconciled mismatch

**Acceptance criteria:**

* startup reconciliation occurs before trading activation
* mismatch causes startup failure or safe block
* discrepancy logging is explicit

**Depends on:** none

---

### TICKET-013 — Harden systemd units and config-path safety

**Priority:** P1
**Why:** Base service can silently point to research config; restart burst limiting is absent.
**Scope:**

* Add `StartLimitIntervalSec` / `StartLimitBurst`
* Rename base unit to clearly non-production form
* Document production-only service unit path

**Acceptance criteria:**

* deployment units cannot be confused silently
* restart storm protection is present
* operator docs reflect the correct unit

**Depends on:** TICKET-012

---

## Phase 3 — Restore detector and semantic trust

### TICKET-014 — Resolve canonical events that map to proxy detectors

**Priority:** P1
**Why:** Four canonical events currently resolve to proxy-tier detectors without point-of-use disclosure. 
**Scope:**

* For each of:

  * `ABSORPTION_EVENT`
  * `DEPTH_COLLAPSE`
  * `ORDERFLOW_IMBALANCE_SHOCK`
  * `SWEEP_STOPRUN`
* Either implement dedicated canonical detectors or demote/disclose them as proxy in validation and registry surfaces

**Acceptance criteria:**

* no canonical event silently resolves to proxy maturity
* proposal validation surfaces maturity tier
* registry/docs agree

**Depends on:** none

---

### TICKET-015 — Tighten synthetic truth validation thresholds

**Priority:** P1
**Why:** Current synthetic validation can pass with 75% off-regime firing and is not precision-informative. 
**Scope:**

* Lower `max_off_regime_rate` to meaningful threshold
* Add `min_in_regime_fraction` or equivalent precision-style gate
* Make tolerance regime-specific

**Acceptance criteria:**

* noisy detector cases fail
* validation output reports hit + precision-style measures
* updated thresholds are documented

**Depends on:** none

---

### TICKET-016 — Classify uncovered and synthetic-unvalidatable event types

**Priority:** P1
**Why:** Most implemented event types have no synthetic truth windows, so synthetic “pass” can be vacuous. 
**Scope:**

* Mark event types as:

  * covered
  * uncovered
  * synthetic-unvalidatable
* Enforce profile/manifest freeze integrity in validation flow

**Acceptance criteria:**

* coverage docs distinguish all three states
* validation aborts on manifest/profile mismatch

**Depends on:** TICKET-015

---

### TICKET-017 — Register or deprecate undocumented materialized states

**Priority:** P1
**Why:** Ten materialized states lack formal registry entries and policy semantics. 
**Scope:**

* Register all materialized-but-unregistered states with rules
* Or formally deprecate them
* Remove dead registry entries that never materialize

**Acceptance criteria:**

* every materialized state is formally accounted for
* ontology audit treats unregistered live states as failure/warning with explicit policy

**Depends on:** none

---

### TICKET-018 — Remove orphan detectors and parameterize hardcoded detector thresholds

**Priority:** P2
**Why:** Three legacy alias detectors have no active event spec, and `TREND_EXHAUSTION_TRIGGER` has hardcoded thresholds. 
**Scope:**

* Remove orphan registrations or add valid active specs
* Move hardcoded thresholds into config/default parameter surface

**Acceptance criteria:**

* no spec-less detectors appear in active enumeration
* detector thresholds are externally configurable

**Depends on:** TICKET-014, TICKET-017

---

## Phase 4 — Structural hardening and governance

### TICKET-019 — Refactor `project.spec_registry` into policy-compliant surface

**Priority:** P1
**Why:** `project.spec_registry/__init__.py` is a boundary violation and is not properly represented in the architecture inventory.
**Scope:**

* Move YAML loaders into `loaders.py`
* Move policy/constants into `policy.py`
* Reduce `__init__.py` to thin re-exports
* Add `project.spec_registry` to architecture inventory

**Acceptance criteria:**

* `__init__.py` is thin
* architecture inventory formally declares the surface
* import-boundary tests remain green

**Depends on:** TICKET-002

---

### TICKET-020 — Promote at least one authoritative benchmark

**Priority:** P1
**Why:** Certification gate exists but relies on informative-only benchmarks, which weakens the decision boundary. 
**Scope:**

* Select stable benchmark slice
* Define authoritative maintenance policy
* Run benchmark certification against it

**Acceptance criteria:**

* at least one authoritative benchmark exists in maintained set
* certification artifacts include authoritative pass/fail

**Depends on:** TICKET-004, TICKET-005, TICKET-006

---

### TICKET-021 — Strengthen smoke tests to catch gate bypass and rejection paths

**Priority:** P1
**Why:** Smoke coverage is substantive, but research smoke asserts row count only and promotion smoke lacks rejection-path coverage. 
**Scope:**

* Add behavioral assertions to research smoke
* Add rejection-path promotion smoke
* Add adverse-regime smoke dataset
* Add pytest timeout/marker/warning config if not already covered by TICKET-003

**Acceptance criteria:**

* smoke suite fails when gates are bypassed
* rejection-path test exists
* adverse-regime dataset is exercised

**Depends on:** TICKET-003, TICKET-008, TICKET-009

---

## Dependency order

### Immediate start

* TICKET-001
* TICKET-004
* TICKET-005
* TICKET-007
* TICKET-008
* TICKET-009
* TICKET-010
* TICKET-012

### Start after first merges

* TICKET-002 after TICKET-001
* TICKET-006 after TICKET-004 and TICKET-005
* TICKET-011 after TICKET-010
* TICKET-013 after TICKET-012
* TICKET-003 after TICKET-001

### Start after platform stabilization

* TICKET-014
* TICKET-015
* TICKET-017
* TICKET-019
* TICKET-021

### Final hardening

* TICKET-016 after TICKET-015
* TICKET-018 after TICKET-014 and TICKET-017
* TICKET-020 after TICKET-004, TICKET-005, TICKET-006

---

## Recommended sprint split

### Sprint 1

* TICKET-001, 002, 004, 005, 007, 008, 009

### Sprint 2
* [Plan: 2026-03-18-sprint-2-audit-remediation.md](file:///home/tstuv/workspace/trading/EDGEE/docs/superpowers/plans/2026-03-18-sprint-2-audit-remediation.md)
* TICKET-006, 010, 011, 012, 013, 003

### Sprint 3

* TICKET-014, 015, 017, 019, 021

### Sprint 4

* TICKET-016, 018, 020

---

