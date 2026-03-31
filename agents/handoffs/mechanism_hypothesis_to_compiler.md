# Handoff: Mechanism Hypothesis -> Compiler

## Context

You are the compiler agent. The coordinator has invoked you to compile a frozen
mechanism hypothesis into a repo-native proposal YAML.

## Your Specification

Follow the compiler spec in `agents/compiler.md` exactly.

## Provided Data

### Mechanism Hypothesis
{{mechanism_hypothesis}}

### Program ID
{{program_id}}

### Suggested Run ID
{{suggested_run_id}}

## Instructions

1. Validate ALL fields before compiling:
   - Events exist in canonical_event_registry.yaml
   - Templates are valid for the event family per event_template_registry.yaml
   - Horizons are in the supported set for the timeframe
   - Regime exists in regime_routing.yaml
   - Entry lags >= 1
   - Search control within limits
2. If any validation fails, REJECT with specific error — do not silently fix
3. Compile the hypothesis into proposal YAML conforming to AgentProposal schema
4. Emit the translation, plan-only, and execution commands
5. Emit the plan review checklist

Return your output in the exact format specified in `agents/compiler.md`.

Do NOT modify the hypothesis silently.
Do NOT add fields not specified in the hypothesis.
