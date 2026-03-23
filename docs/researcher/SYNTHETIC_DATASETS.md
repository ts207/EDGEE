# Synthetic Datasets

## What synthetic data is for

Synthetic data exists to calibrate detectors, validate truth recovery, and test pipeline behavior in controlled conditions.

## Maintained profiles

The repository includes maintained synthetic workflows for:

- broad discovery calibration,
- fast certification,
- and detector-truth validation.

## What gets written

Synthetic workflows should produce artifacts that let you answer:

- what was injected,
- what was recovered,
- what was missed,
- and whether the pipeline handled the case as expected.

## Main workflows

Use the maintained scripts rather than inventing a one-off flow.

```bash
python3 -m project.scripts.run_golden_synthetic_discovery
python3 -m project.scripts.run_fast_synthetic_certification
python3 -m project.scripts.validate_synthetic_detector_truth --run_id <run_id>
```

## Truth validation

After a synthetic run, confirm that the detector truth matches the maintained expectation for that profile.

## Known limitations

Synthetic calibration is narrower than live market evidence.

It should be used to verify mechanics, not to claim market alpha.

## Recommended workflow

1. Run the maintained synthetic scenario.
2. Inspect the produced artifacts.
3. Confirm truth recovery.
4. Update docs if the calibration contract changed.
