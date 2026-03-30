#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "usage: $0 RUN_ID [BASELINE_RUN_ID]" >&2
  exit 2
fi

run_id="$1"
baseline_run_id="${2:-}"

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$repo_root"

if [ -n "$baseline_run_id" ]; then
  .venv/bin/python -m project.scripts.run_researcher_verification \
    --mode experiment \
    --run-id "$run_id" \
    --baseline-run-id "$baseline_run_id"
else
  .venv/bin/python -m project.scripts.run_researcher_verification \
    --mode experiment \
    --run-id "$run_id"
fi
