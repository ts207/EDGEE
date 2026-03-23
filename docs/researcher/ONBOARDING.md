# Researcher Onboarding

This is the first doc to read as a research operator.

It tells you what this system is for, what the fundamental rules are, and how to run your first experiment safely.

---

## What This System Is

EDGEE is a research operating system for market studies. It is designed to:

- turn observations into explicit, falsifiable hypotheses
- run bounded, replayable experiments
- evaluate output against contract, statistical, and deployment gates
- store reusable memory across runs
- gate promotion only after evidence survives required checks

It is **not** a strategy toybox. It is **not** a place to run broad searches because more output seems valuable. Detector firings alone are not evidence.

---

## Five First Principles

Keep these in mind at all times.

1. **Artifacts are the source of truth.** A run is only as trustworthy as its reconciled outputs.
2. **Contracts define trust.** A run that exits `0` but has missing or mismatched artifacts is not a good run.
3. **Synthetic evidence is calibration evidence.** Do not present synthetic profitability as live-market evidence.
4. **Confidence-aware context is the default.** Hard regime labels exist for compatibility, not as the authoritative filter.
5. **Promotion is a gate, not a reward.** Attractive discovery output does not imply promotion readiness.

---

## The Research Unit

The correct unit of research is a **hypothesis**, not a detector, not a strategy.

A hypothesis specifies:

| Field | Example |
|---|---|
| `event` | `FND_DISLOC` |
| `canonical_family` | `STATISTICAL_DISLOCATION` |
| `template` | `mean_reversion` |
| `context` | high volatility, non-hostile spread state |
| `side` | `short` |
| `horizon` | 12 bars |
| `entry_lag` | 1 bar |
| `symbol_scope` | `BTCUSDT` |

That is the unit you compare across runs, store in memory, and interpret in promotion. If you cannot write it in this form, the question is not ready to run.

---

## Translating a Question Into Repo-Native Terms

Before running anything, convert your plain-language question.

**Plain language:** "Funding dislocation may revert quickly in high volatility if spreads are still acceptable."

**Repo-native:**
- event: `FND_DISLOC`
- family: `STATISTICAL_DISLOCATION`
- template: `mean_reversion`
- context: `ms_vol_state = HIGH`, `ms_spread_state` non-hostile
- horizons: 12–24 bars (short intraday)

If the translation is not possible, the question needs more specificity first.

---

## The Minimum Safe Run Pattern

Default to this sequence for every material run:

1. Inspect memory for the same event, template, context, and symbol region.
2. Inspect static event knowledge and prior benchmark status.
3. Write a compact proposal in repo-native terms.
4. Run `plan_only` and review the plan.
5. Execute the narrow slice.
6. Inspect artifacts in trust order (manifest → stage manifests → logs → reports → diagnostics).

Do not skip `plan_only` for material runs.

**Plan-only command:**
```bash
edge-run-all --run_id demo --symbols BTCUSDT --start 2024-01-01 --end 2024-01-31 --plan_only 1
```

---

## Smoke Verification

Before any material run, verify the platform is in a working state.

```bash
edge-smoke --mode research
```

---

## Reading Order After This Doc

Follow this sequence:

1. [RESEARCH_LOOP.md](./RESEARCH_LOOP.md) — the full observe → reflect cycle
2. [EXPERIMENT_PROTOCOL.md](./EXPERIMENT_PROTOCOL.md) — how to design and scope a single run
3. [GUARDRAILS.md](./GUARDRAILS.md) — operating rules and stop conditions
4. [ARTIFACTS_AND_CONTRACTS.md](./ARTIFACTS_AND_CONTRACTS.md) — how to trust output
5. [BENCHMARK_GUIDE.md](./BENCHMARK_GUIDE.md) — current benchmark status and maintenance
