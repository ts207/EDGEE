#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "usage: $0 EVENT SYMBOLS [RUN_ID] [START] [END]" >&2
  exit 2
fi

event="$1"
symbols="$2"
run_id="${3:-discovery_target}"
start_date="${4:-2020-06-01}"
end_date="${5:-2025-07-10}"

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$repo_root"

make discover-target EVENT="$event" SYMBOLS="$symbols" RUN_ID="$run_id" START="$start_date" END="$end_date"
