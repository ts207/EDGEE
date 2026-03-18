#!/bin/bash
set -e

echo "Running smoke test for show_benchmark_review.py --compare-history..."

# This verifies side-by-side historical row count comparison
PYTHONPATH=. python3 project/scripts/show_benchmark_review.py --compare-history 3
