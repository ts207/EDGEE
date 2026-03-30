---
name: edge-artifact-triage
description: Use when Edge run manifests, reports, or promotion bundles are missing, contradictory, or need path-level inspection.
---

# Edge Artifact Triage

## Purpose

Use this skill when a run appears mechanically wrong even before statistical interpretation.

Typical symptoms:

- missing `run_manifest.json`
- missing phase-2 diagnostics or candidates
- missing promotion bundle
- path mismatches between expected and actual outputs
- artifact contradictions across stages

## First Actions

1. Inspect canonical artifact paths for the run.
2. Verify whether the files exist.
3. Run contract verification if the issue followed a code or config change.

Useful commands:

```bash
plugins/edge-plugins/scripts/edge_show_run_artifacts.sh <run_id>
plugins/edge-plugins/scripts/edge_verify_contracts.sh
plugins/edge-plugins/scripts/edge_verify_run.sh <run_id>
```

## Escalation Rule

Escalate instead of patching blindly if the issue touches:

- ontology meaning
- routing semantics
- stage/artifact contracts
- schema surfaces listed as forbidden in `docs/AGENT_CONTRACT.md`
