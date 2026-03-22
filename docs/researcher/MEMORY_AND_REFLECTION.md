# Memory and Reflection

Memory prevents the system from repeating avoidable work. Reflection turns one run into reusable decision support for the next.

---

## Purpose

Use memory to:
- Avoid rerunning failed regions under new wording.
- Retain fragile system facts that are not obvious from the code.
- Distinguish market conclusions from system conclusions.
- Prioritize the next best experiment.

---

## Memory Classes

### Structural Memory
Facts about how the repository behaves.

Examples:
- A stage contract requires normalized candidates before promotion.
- A quality report is emitted at a specific path after phase 2.
- A promotion fallback uses the same normalized contract as the canonical path.

### Experimental Memory
Facts about what was tested and what happened.

Examples:
- A specific family-template-context region survived costs on a given symbol in a given period.
- A narrow slice failed in validation despite attractive train metrics.

### Negative Memory
Facts about what to avoid.

Examples:
- A broad noisy run pattern repeatedly produces low-trust output.
- A region repeatedly fails retail net expectancy after costs regardless of template.

### Action Memory
Facts about what the next justified move should be.

Examples:
- Rerun a narrow slice after a generator change that may have affected that region.
- Stop re-testing a family-template region until live data coverage improves.

---

## Reflection Schema

Every meaningful run should produce a reflection that minimally covers:

| Field | Description |
|---|---|
| `objective` | What belief was being tested |
| `run_scope` | Symbol(s), date range, run ID |
| `mechanical_status` | Did the pipeline run cleanly |
| `statistical_status` | Did quality checks pass |
| `primary_findings` | What the evidence showed |
| `primary_failures` | What failed and why |
| `belief_update` | How the finding changes the prior belief |
| `next_action` | One of: `exploit`, `explore`, `repair`, `hold`, `stop` |

For synthetic runs, also include:
- Generator profile and noise scale
- Truth-map path
- Whether the result survived a second profile or only one synthetic world

---

## Reflection Questions

After each meaningful run, answer:

1. What prior belief did this run test?
2. What evidence increased or decreased that belief?
3. Was the result market-driven or system-driven?
4. What reusable rule should be remembered?
5. What exact next action is justified?

---

## Write Rules

- Store facts, not impressions.
- Include run IDs and scope so the record is traceable.
- Separate system issues from market conclusions explicitly.
- Record both positive and negative findings.
- Prefer short, high-signal entries over narrative.
- Reference exact artifact families when that fact will matter later.

---

## Retrieval Rules

Before any new experiment, retrieve memory for:
- The same event or family
- The same template
- The same symbol or timeframe
- The same context
- The same fail gate

If prior memory shows repeated clean failure with no material new condition, do not rerun by default.

---

## Priority Rules

**Increase priority for experiments that:**
- Resolve a known ambiguity.
- Build on positive post-cost evidence.
- Reduce uncertainty with a small run.
- Validate a recent code or contract fix.

**Decrease priority for experiments that:**
- Duplicate prior unsuccessful slices.
- Broaden scope without adding information.
- Depend on known-broken contracts.
- Produce warning-heavy output without changing the decision.

---

## Memory Hygiene

Supersede or downgrade memories that are:
- Invalidated by code changes
- Contradicted by cleaner reruns
- Too vague to guide future selection

Do not silently erase history when a superseded record is still more informative than no record. Mark it superseded with a note explaining what replaced it.
