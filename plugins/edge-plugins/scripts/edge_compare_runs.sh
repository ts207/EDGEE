#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "usage: $0 BASELINE_RUN_ID CANDIDATE_RUN_ID" >&2
  exit 2
fi

baseline_run_id="$1"
candidate_run_id="$2"

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$repo_root"

.venv/bin/python project/scripts/compare_research_runs.py \
  --baseline_run_id "$baseline_run_id" \
  --candidate_run_id "$candidate_run_id"
