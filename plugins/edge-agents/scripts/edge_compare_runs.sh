#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 2 ] || [ "$#" -gt 4 ]; then
  echo "usage: $0 BASELINE_RUN_ID CANDIDATE_RUN_ID [PROGRAM_ID] [DATA_ROOT]" >&2
  exit 2
fi

baseline_run_id="$1"
candidate_run_id="$2"
program_id="${3:-}"
data_root="${4:-}"

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "$script_dir/_edge_common.sh"

repo_root="$(edge_repo_root)"
ensure_edge_env "$repo_root"
cd "$repo_root"

cmd=(
  "$repo_root/.venv/bin/edge" operator compare
  --run_ids "${baseline_run_id},${candidate_run_id}"
)

if [ -n "$program_id" ]; then
  cmd+=(--program_id "$program_id")
fi

if [ -n "$data_root" ]; then
  cmd+=(--data_root "$data_root")
fi

"${cmd[@]}"
