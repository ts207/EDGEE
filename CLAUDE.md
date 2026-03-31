# Tailored Workflow for Edge Repo

## What this repo already has

Edge already contains the core control surfaces for a disciplined research loop:

- operator contracts in  `docs/03_OPERATOR_WORKFLOW.md`, `docs/AGENT_CONTRACT.md`
- proposal translation and issuance in `project/research/agent_io/proposal_to_experiment.py`, `issue_proposal.py`, `execute_proposal.py`
- memory/query surfaces in `project/research/knowledge/query.py`
- autonomous planning in `project/research/agent_io/campaign_planner.py`
- a full closed loop in `project/research/agent_io/closed_loop.py`
- review templates in `docs/templates/`
- agents in /agents
Because those pieces already exist, the right workflow is **not** to invent a second orchestration system. The right workflow is to use Claude Code as the control plane and wrap the repo’s native proposal / plan / run / artifact-review path.

---

## Recommended control model

### Claude Code
Claude Code is:
- coordinator
- manager
- executor

Claude Code should:
- decide the current stage
- choose which specialist agent to invoke
- run translation / plan / execution commands
- collect artifacts
- enforce observation / validation / final separation
- prevent silent scope drift
- stop when the issue is a repo defect rather than a research defect

### Specialist agents
Use only three specialist agents:

1. `analyst`
2. `mechanism_hypothesis`
3. `compiler`

Do **not** create a separate coordinator agent. The repo already has a strong top-level operator model, and Claude Code should occupy that role.

---

## Repo-native research stages

Use these explicit stages.

### Stage 1: Observation / research
Purpose:
- mechanism discovery
- context concentration
- early rejection

Allowed:
- narrow proposals
- promotion disabled
- one symbol or tiny symbol set
- one event family or one narrow cluster
- one template family
- one new conditioning axis at a time

Not allowed:
- final conclusions
- broad multi-family search
- many symbols / dates / templates at once

### Stage 2: Validation
Purpose:
- test frozen hypotheses on a separate period
- evaluate robustness, cost survival, sensitivity, regime dependence

Allowed:
- mild neighboring perturbations
- same mechanism family
- same tradable expression

Not allowed:
- broad mechanism rewrite
- silent widening of the search surface

### Stage 3: Final holdout
Purpose:
- single final decision

Allowed:
- one final run of surviving validated hypotheses

Not allowed:
- iterative retuning after seeing final results

---

## Tailored workflow loop

### Step 0: Query memory first
Always start with:

```bash
.venv/bin/python -m project.research.knowledge.query knobs
.venv/bin/python -m project.research.knowledge.query memory --program_id <program_id>
.venv/bin/python -m project.research.knowledge.query static --event <EVENT>
```

This repo expects memory-first research. Do not skip it.

### Step 1: Write a bounded hypothesis
Use:
- `docs/templates/hypothesis_template.md`
- `docs/templates/bounded_experiment_template.md`

A valid bounded hypothesis in this repo must state exactly:
- one regime
- one mechanism
- one tradable expression
- one primary trigger family
- one template family
- one symbol set
- one timeframe
- one date window
- one horizon set
- one direction set
- one entry-lag set
- one success test
- one kill condition

### Step 2: Compiler produces proposal YAML
The compiler should create a proposal under `spec/proposals/`.

It must validate against the repo’s executable surfaces before emitting commands.



### Step 3: Translate proposal
```bash
.venv/bin/python -m project.research.agent_io.proposal_to_experiment \
  --proposal <PROPOSAL_PATH> \
  --registry_root project/configs/registries
```

Review:
- dates
- symbols
- templates
- trigger space
- promotion profile
- horizons / directions / entry lags

### Step 4: Plan before execution
Use `issue_proposal`, not direct `run_all`, for the main loop because `issue_proposal` also records proposal artifacts and memory bookkeeping.

```bash
.venv/bin/python -m project.research.agent_io.issue_proposal \
  --proposal <PROPOSAL_PATH> \
  --registry_root project/configs/registries \
  --plan_only 1
```

Review:
- `run_id`
- validated hypothesis count
- required detectors
- required states / features
- whether the plan widened beyond the intended mechanism

### Step 5: Execute one bounded run
```bash
.venv/bin/python -m project.research.agent_io.issue_proposal \
  --proposal <PROPOSAL_PATH> \
  --registry_root project/configs/registries \
  --run_id <RUN_ID> \
  --plan_only 0
```

### Step 6: Analyst inspects artifacts in strict order
Read in this order:

1. `data/runs/<run_id>/run_manifest.json`
2. stage manifests / stage logs
3. `data/reports/phase2/<run_id>/phase2_diagnostics.json`
4. `data/reports/phase2/<run_id>/phase2_candidates.parquet`
5. if candidates are empty: upstream `evaluated_hypotheses.parquet` and `gate_failures.parquet`
6. `research_checklist/checklist.json`
7. promotion artifacts only if promotion was enabled

This is especially important in Edge because empty candidate output is often **not** enough to explain a run.

### Step 7: Mechanism hypothesis agent writes the next idea
Only after the analyst diagnoses the run.

Output 1–3 mechanism hypotheses, each with:
- trigger family
- direction
- horizon
- likely context filter
- invalidation
- likely failure mode
- allowed knobs only
- frozen knobs

### Step 8: Either refine, validate, or stop
Use this rule:

- if the run exposed a repo / contract / data defect: patch first
- if the run was mechanically clean but all hypotheses failed weakly: refine with one context axis
- if the mechanism survives cleanly on observation data: move to validation
- if validation survives: move once to final holdout
- if final fails: stop

---



## When to use built-in autonomous planner surfaces

The repo already includes:
- `project/research/agent_io/campaign_planner.py`
- `project/research/agent_io/closed_loop.py`
- `.github/commands/research-planner.toml`

Use them only after the manual / semi-autonomous loop is stable.

### Recommended adoption order

#### Phase A: manual bounded loop
Use:
- memory query
- proposal compile
- plan only
- execute
- artifact diagnosis



#### Phase B: built-in planner / closed loop
Only after:
- proposal contracts are stable
- artifact diagnosis is reliable
- compiler rejects bad horizons / bad contract values up front
- memory tables are accumulating usable frontier history

Reason:
The built-in planner is useful for ranking the next region, but it should not be the first layer you trust while the campaign design and analysis workflow are still being hardened.

---

## Tailored state machine for this repo

### State: `needs_diagnosis`
Invoke analyst.

Transition to:
- `repair_repo`
- `repair_proposal`
- `refine_mechanism`
- `advance_to_validation`
- `advance_to_final`
- `stop`

### State: `repair_repo`
Only for local, contract-preserving repairs.
If the fix touches forbidden surfaces from `docs/AGENT_CONTRACT.md`, escalate to human.

### State: `repair_proposal`
Compiler rewrites the proposal narrowly and reruns translate + plan.

### State: `refine_mechanism`
Mechanism Hypothesis produces a narrower conditional version.
Compiler creates a new observation-refinement proposal.

### State: `advance_to_validation`
Compiler creates a validation proposal on the held-out validation period.

### State: `advance_to_final`
Compiler creates a final-holdout proposal.
Run once.

### State: `stop`
Write review, update memory, and stop the loop.

---

## Tailored stop conditions

Stop immediately when:
- an unsupported horizon/template/event is detected
- the required fix touches canonical ontology, routing, or contract surfaces listed as forbidden in `docs/AGENT_CONTRACT.md`
- data coverage is materially incomplete
- artifact layers disagree in business meaning
- the same hypothesis version has already consumed final holdout
- the next proposed run changes more than one major axis

For this repo, these are more important than “keep running until something works.”

---

## Default run shapes

### First observation run
- one symbol
- one timeframe
- one event family or narrow event cluster
- promotion disabled
- bounded date range
- one template family

### First refinement run
- keep the strongest family only
- keep strongest direction only
- keep strongest horizon only
- add one context axis only

### Validation run
- one frozen hypothesis version
- separate dates
- same mechanism family
- no broad search widening

### Final run
- surviving validated hypothesis only
- one final held-out period

---

## Exact tailored command policy

### Preferred main loop commands

Memory query:
```bash
.venv/bin/python -m project.research.knowledge.query knobs
.venv/bin/python -m project.research.knowledge.query memory --program_id <program_id>
.venv/bin/python -m project.research.knowledge.query static --event <EVENT>
```

Translate proposal:
```bash
.venv/bin/python -m project.research.agent_io.proposal_to_experiment \
  --proposal <PROPOSAL_PATH> \
  --registry_root project/configs/registries
```

Plan only:
```bash
.venv/bin/python -m project.research.agent_io.issue_proposal \
  --proposal <PROPOSAL_PATH> \
  --registry_root project/configs/registries \
  --plan_only 1
```

Execute:
```bash
.venv/bin/python -m project.research.agent_io.issue_proposal \
  --proposal <PROPOSAL_PATH> \
  --registry_root project/configs/registries \
  --run_id <RUN_ID> \
  --plan_only 0
```

### When to use direct `run_all`
Only when you already know the exact slice and do not need proposal memory bookkeeping.

### When to use `campaign_planner`
Only when you want repo-native autonomous frontier ranking after several runs already exist for the `program_id`.

---

## Best initial autonomous loop for this repo

1. Claude Code queries memory.
2. Claude Code asks compiler for a bounded proposal.
3. Claude Code translates the proposal.
4. Claude Code runs `plan_only`.
5. Claude Code executes.
6. Claude Code asks analyst for diagnosis.a
7. If mechanically clean but weak, Claude Code asks mechanism_hypothesis for a narrower conditional mechanism.
8. Claude Code asks compiler for the next proposal.
9. Repeat until either:
   - validation-worthy hypothesis exists,
   - a repo defect must be patched,
   - or the mechanism is killed.

This fits the repo’s actual design far better than a generic planner/executor/critic loop.
