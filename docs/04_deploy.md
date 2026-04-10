# Stage 4: Deploy

Deploy is the runtime execution boundary. It is the first stage that actually interacts with runtime thesis batches, approval contracts, and live-engine controls.

The most important current rule is simple:

- discovery does not deploy
- validation does not deploy
- promotion does not deploy
- export prepares the thesis batch
- deploy consumes that exported batch under explicit gating

## Canonical Commands

### List exported thesis batches

```bash
python -m project.cli deploy list-theses
```

### Inspect a thesis batch

```bash
python -m project.cli deploy inspect-thesis --run_id <run_id>
```

### Launch paper mode

```bash
python -m project.cli deploy paper --run_id <run_id> --config project/configs/live_paper.yaml
```

### Launch live mode

```bash
python -m project.cli deploy live --run_id <run_id> --config project/configs/live_production.yaml
```

### Status

```bash
python -m project.cli deploy status
```

## What Deploy Reads

Deploy does not read raw promotion tables directly. It reads:

- `data/live/theses/<run_id>/promoted_theses.json`

That file is produced by `promote export`.

If the thesis batch does not exist, deploy fails with the correct boundary message: the promote stage was not completed into runtime inventory.

## Deployment States

The thesis contract now supports richer deployment lifecycle states than the older docs reflected:

- `monitor_only`
- `paper_only`
- `promoted`
- `paper_enabled`
- `paper_approved`
- `live_eligible`
- `live_enabled`
- `live_paused`
- `live_disabled`
- `retired`

Current runtime rule:

- only `live_enabled` is tradeable for real live order submission

That is enforced by `LIVE_TRADEABLE_STATES` in `project/live/contracts/promoted_thesis.py`.

## Current CLI Gate Behavior

The launcher behavior in `project/cli.py` is intentionally conservative:

### `deploy paper`

The current CLI blocks paper launch unless the batch contains at least one thesis whose `deployment_state` is:

- `paper_only`, or
- `live_enabled`

### `deploy live`

The current CLI blocks live launch unless the batch contains at least one `live_enabled` thesis.

This means the runtime contract knows about richer lifecycle states, but the launcher still uses a strict eligibility check at startup.

## DeploymentGate

`project/live/deployment.py` enforces the live approval contract.

For theses in `live_eligible` or `live_enabled`, the gate checks:

- `live_approval.live_approval_status == "approved"`
- `approved_by` is populated
- `approved_at` is populated
- `risk_profile_id` is populated
- paper duration requirements are satisfied if configured

For `live_enabled` theses specifically, the gate also checks:

- cap profile is configured with hard caps
- `deployment_mode_allowed` is `live_eligible` or `live_enabled`

This is the repo’s hard guard against treating promotion class alone as enough for live trading.

## Thesis Reconciliation

The current runtime also includes startup reconciliation logic in `project/live/thesis_reconciliation.py`.

This exists to catch batch drift such as:

- removed theses
- downgraded theses
- superseded theses
- state regressions

That matters because a new export can be written between runtime restarts. Reconciliation prevents the engine from silently treating changed inventory as if nothing happened.

## Runtime Modes

The live engine runtime modes are:

- `monitor_only`
- `trading`

The older `paper_trading` runtime mode is not the current model. Paper trading is now represented by configuration and thesis-state usage, not a third runtime-mode string.

## Config Paths

If `--config` is omitted, `project/cli.py` defaults to:

- paper: `project/configs/live_paper.yaml`
- live: `project/configs/live_production.yaml`

Passing `--config` is still useful when you want an explicit environment, policy, or OMS configuration.

## Risk And Runtime Controls

Deployment is not just a launcher. The runtime includes several explicit safeguards.

### Kill switch

`project/live/kill_switch.py` uses:

| Parameter | Value |
|-----------|-------|
| `PSI_ERROR_THRESHOLD` | 0.25 |
| `PSI_WARN_THRESHOLD` | 0.10 |

Tier-1 monitored features currently include:

- `vol_regime`
- `ms_spread_state`
- `funding_abs_pct`
- `basis_zscore`
- `oi_delta_1h`
- `spread_bps`

The runtime also checks KS statistics alongside PSI for drift sensitivity.

### Decay defaults

`project/live/decay.py` activates conservative default rules when no explicit decay rules are supplied:

| Rule | Metric | Threshold | Window | Action |
|------|--------|-----------|--------|--------|
| `edge_decay_default` | edge ratio | 0.50 of expected | 10 samples | downsize 50% |
| `slippage_spike_default` | slippage bps | 20 bps | 5 samples | downsize 50% |
| `hit_rate_decay_default` | hit rate | 0.40 | 10 samples | warn |

### Decision score floor

`project/live/scoring.py` enforces:

- `MIN_SETUP_MATCH = 0.20`

If setup match falls below that floor, the additive score is forced to zero before a trade decision proceeds.

### Allocation policy

`project/engine/risk_allocator.py` defaults to:

- `AllocationPolicy.mode = "deterministic_optimizer"`

That default exists to keep allocation decisions reproducible and auditable.

## Funding And Venue Nuance

Carry calculations are venue-sensitive. `project/engine/pnl.py` includes explicit funding schedules such as:

- `FUNDING_HOURS_BINANCE`
- `FUNDING_HOURS_BYBIT_4H`

Using the wrong schedule can materially understate carry for venues with 4-hour funding cadence.

## What Deploy Does Not Do

Deploy does not:

- auto-generate theses from discovery outputs
- bypass approval metadata because a thesis was production-promoted
- reinterpret a missing export batch as a recoverable warning
- treat generated research artifacts as a substitute for the thesis store
