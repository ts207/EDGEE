
# Sprint 2 operator additions

The operator surface now supports bounded confirmation semantics through proposal metadata.

## Bounded proposal block

```yaml
bounded:
  baseline_run_id: my_prior_run
  experiment_type: confirmation
  allowed_change_field: end
  change_reason: narrow to 2022 only
  compare_to_baseline: true
```

Bounded proposals are validated against the baseline proposal stored in program memory.
The current proposal must differ from the baseline on exactly one tracked field, and that field must match `allowed_change_field`.

## Run terminal states

Run manifests now include `terminal_status` in addition to the existing `status` field.

Current values:
- `completed`
- `completed_with_contract_warnings`
- `failed_mechanical`
- `failed_statistical`
- `failed_runtime_invariants`
- `failed_data_quality`

`resume_recommended` is also written into the run manifest when the failure looks resumable.
