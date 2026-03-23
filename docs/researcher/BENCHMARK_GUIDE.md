# Benchmark Guide

## Purpose

Benchmarks are maintenance and calibration tools.

They are used to detect drift, validate maintained slices, and keep the platform honest.

## Quick terminal review

Use the maintained scripts and Makefile targets rather than ad hoc commands when possible.

Typical checks:

```bash
make benchmark-maintenance
PYTHONPATH=. python3 project/scripts/show_benchmark_review.py
```

## When to run benchmark maintenance

Run it when:

- detector coverage changes,
- synthetic calibration changes,
- benchmark slices are updated,
- or core orchestration logic changes.

## Reading the output

Check whether the maintained slices still:

- complete successfully,
- preserve expected truth labels,
- and remain comparable to previous runs.

## Status definitions

- Pass: maintained slice still behaves as expected.
- Drift: output changed in a way that needs explanation.
- Failure: the maintained slice no longer meets the contract.

## What this guide is not

It is not a live alpha performance report.

It is a maintenance and verification guide.
