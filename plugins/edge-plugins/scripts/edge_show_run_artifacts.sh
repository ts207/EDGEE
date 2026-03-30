#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "usage: $0 RUN_ID" >&2
  exit 2
fi

run_id="$1"

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$repo_root"

paths=(
  "data/runs/$run_id/run_manifest.json"
  "data/reports/phase2/$run_id/phase2_diagnostics.json"
  "data/reports/phase2/$run_id/phase2_candidates.parquet"
  "data/reports/promotions/$run_id"
)

for path in "${paths[@]}"; do
  abs_path="$repo_root/$path"
  if [ -e "$abs_path" ]; then
    echo "FOUND $path"
    if [ -d "$abs_path" ]; then
      find "$abs_path" -maxdepth 2 -type f | sort
    fi
  else
    echo "MISSING $path"
  fi
done
