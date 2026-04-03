#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -gt 1 ]; then
  echo "usage: $0 [THESIS_RUN_ID]" >&2
  exit 2
fi

thesis_run_id="${1:-}"

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "$script_dir/_edge_common.sh"

repo_root="$(edge_repo_root)"
ensure_edge_env "$repo_root"
cd "$repo_root"

if [ -n "$thesis_run_id" ]; then
  THESIS_RUN_ID="$thesis_run_id" make package
else
  make package
fi
