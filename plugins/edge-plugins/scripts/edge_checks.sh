#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$repo_root"

pytest -q tests/param_integrity/test_no_hardcoded_constants.py -q
pytest -q project/tests/events/test_detector_hardening.py -q
pytest -q project/tests/test_event_hardening_verification.py -q
