#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ] || [ "$#" -gt 5 ]; then
  echo "usage: $0 PROPOSAL_PATH [RUN_ID] [REGISTRY_ROOT] [OUT_DIR] [CHECK]" >&2
  exit 2
fi

proposal_path="$1"
run_id="${2:-}"
registry_root="${3:-project/configs/registries}"
out_dir="${4:-}"
check="${5:-}"

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "$script_dir/_edge_common.sh"

repo_root="$(edge_repo_root)"
ensure_edge_env "$repo_root"
cd "$repo_root"

cmd=(
  "$repo_root/.venv/bin/edge" operator lint
  --proposal "$proposal_path"
  --registry_root "$registry_root"
)

if [ -n "$run_id" ]; then
  cmd+=(--run_id "$run_id")
fi

if [ -n "$out_dir" ]; then
  cmd+=(--out_dir "$out_dir")
fi

if [ -n "$check" ]; then
  cmd+=(--check "$check")
fi

"${cmd[@]}"
