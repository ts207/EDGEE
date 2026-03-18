#!/bin/bash
set -e

echo "Running smoke test for show_benchmark_review.py --compare-history..."

# This should FAIL because --compare-history doesn't exist yet
PYTHONPATH=. python3 project/scripts/show_benchmark_review.py --compare-history 3
