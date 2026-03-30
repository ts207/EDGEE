#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "usage: $0 /abs/path/to/proposal.yaml run_id [registry_root]" >&2
  exit 2
fi

proposal_path="$1"
run_id="$2"
registry_root="${3:-project/configs/registries}"

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$repo_root"

.venv/bin/python -m project.research.agent_io.issue_proposal \
  --proposal "$proposal_path" \
  --registry_root "$registry_root" \
  --run_id "$run_id" \
  --plan_only 1
