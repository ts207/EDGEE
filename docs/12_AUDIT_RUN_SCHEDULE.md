# Audit and run schedule

This reference captures the order in which audit-oriented run review should happen.

## Recommended sequence

1. inspect `data/runs/<run_id>/run_manifest.json`
2. inspect phase-2 artifacts under `data/reports/phase2/<run_id>/`
3. inspect promotion artifacts under `data/reports/promotions/<run_id>/`
4. inspect operator summary under `data/reports/operator/<run_id>/`
5. run formal verification from `docs/VERIFICATION.md`

## Purpose

Use this file only as a supporting reference for templates that need a stable link target. The main workflow ownership remains in `docs/03_OPERATOR_WORKFLOW.md` and `docs/05_ARTIFACTS_AND_INTERPRETATION.md`.
