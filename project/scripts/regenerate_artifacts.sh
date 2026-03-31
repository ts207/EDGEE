#!/usr/bin/env bash
set -euo pipefail

# Scripts directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "Regenerating repository artifacts..."

# 0. Event Governance Artifacts
echo "[0/6] Regenerating Event Governance Artifacts..."
PYTHONPATH="$REPO_ROOT" python3 "$REPO_ROOT/project/scripts/build_event_contract_artifacts.py"
PYTHONPATH="$REPO_ROOT" python3 "$REPO_ROOT/project/scripts/event_ontology_audit.py"
PYTHONPATH="$REPO_ROOT" python3 "$REPO_ROOT/project/scripts/build_event_ontology_artifacts.py"
PYTHONPATH="$REPO_ROOT" python3 "$REPO_ROOT/project/scripts/build_event_deep_analysis_suite.py"

# 1. System Map
echo "[1/6] Regenerating System Map..."
PYTHONPATH="$REPO_ROOT" python3 "$REPO_ROOT/project/scripts/build_system_map.py"

# 2. Detector Coverage Report
echo "[2/6] Regenerating Detector Coverage Report..."
PYTHONPATH="$REPO_ROOT" python3 "$REPO_ROOT/project/scripts/detector_coverage_audit.py" \
    --md-out "$REPO_ROOT/docs/generated/detector_coverage.md" \
    --json-out "$REPO_ROOT/docs/generated/detector_coverage.json"

# 3. Ontology Consistency Audit
echo "[3/6] Regenerating Ontology Audit..."
PYTHONPATH="$REPO_ROOT" python3 "$REPO_ROOT/project/scripts/ontology_consistency_audit.py" \
    --output "$REPO_ROOT/docs/generated/ontology_audit.json"

echo "Artifact regeneration complete."
echo "Please review changes and commit them."
