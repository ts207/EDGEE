# Primary Audit Notes

No delegated subagents were used in this audit turn.

Primary evidence collected locally:

- `pytest -q project/tests/contracts/test_repository_hygiene.py -q`
- `pytest -q project/tests/regressions/test_run_success_requires_outputs.py -q`
- `pytest -q project/tests/pipelines/test_run_all_smoke.py -q`
- direct artifact inspection under `data/runs/` and `data/artifacts/experiments/`
- direct path and contract reproductions with `.venv/bin/python -c ...`

Key verified outcomes:

- repository hygiene is currently broken by Windows ADS sidecar files
- objective/profile contract provenance can diverge from the file actually loaded
- live incubation gating persists to a duplicated `project/project/...` path by default
