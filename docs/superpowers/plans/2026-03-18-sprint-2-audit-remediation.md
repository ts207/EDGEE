# Sprint 2 Audit Remediation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Close 6 high-priority audit findings related to dependency management, promotion evidence, live health monitoring, and defensive startup reconciliation.

**Architecture:** 
1. **Hardened Registry**: Add `is_reduced_evidence` column to promotion schemas and logic.
2. **Safety-First Live Execution**: Wire data health into the kill-switch, implement real Binance unwind/flattening, and enforce strict startup reconciliation.
3. **Environment Isolation**: Harden `systemd` units and lock down dependencies.

**Tech Stack:** Python 3.11+, pytest, pandas, aiohttp, systemd, pip-tools

---

## Task 1: TICKET-003 — Dependency Lock and Pyright Pinning

**Files:**
- Modify: `pyproject.toml`
- Create: `requirements.txt` (via tool)

**Step 1: Add pyright to dev dependencies**
Modify `pyproject.toml` to include `pyright==1.1.350` (or current stable) in a new `[project.optional-dependencies] dev` section or similar.

**Step 2: Generate full lockfile**
Run: `pip-compile --extra dev -o requirements.txt pyproject.toml`
*If pip-compile is missing, use `pip install pip-tools` first.*

**Step 3: Verify lockfile**
Expected: `requirements.txt` contains pinned versions for all dependencies.

**Step 4: Commit**
```bash
git add pyproject.toml requirements.txt
git commit -m "chore: pin pyright and generate full dependency lockfile (TICKET-003)"
```

---

## Task 2: TICKET-006 — Mark Reduced-Evidence Promotions

**Files:**
- Modify: `project/reliability/schemas.py`
- Modify: `project/research/services/promotion_service.py`
- Modify: `project/reliability/contracts.py`

**Step 1: Update Schemas**
Add `is_reduced_evidence: bool = False` to `PROMOTION_AUDIT_SCHEMA` and `PROMOTION_DECISION_SCHEMA`.

**Step 2: Update Promotion Logic**
In `PromotionService._process_candidate`, set `is_reduced_evidence=True` if `allow_discovery_promotion` was used to pass the statistical gate.

**Step 3: Update Contract Validation**
Update `contracts.py` to ensure the new column is validated in artifact bundles.

**Step 4: Verify**
Run: `pytest tests/reliability/test_contracts.py` (ensure existing tests pass or are updated).

**Step 5: Commit**
```bash
git add project/reliability/schemas.py project/research/services/promotion_service.py project/reliability/contracts.py
git commit -m "feat: add is_reduced_evidence flag to promotion artifacts (TICKET-006)"
```

---

## Task 3: TICKET-010 — Wire Data Health into Kill-Switch

**Files:**
- Modify: `project/live/runner.py`

**Step 1: Add health-check loop**
In `LiveEngineRunner.start()`, add an `asyncio.create_task(self._monitor_data_health())`.

**Step 2: Implement monitoring logic**
```python
async def _monitor_data_health(self):
    while self._running:
        report = self.data_manager.health_monitor.check_health()
        if not report["is_healthy"]:
            self.kill_switch.trigger(
                KillSwitchReason.STALE_DATA, 
                f"Stale feeds: {report['stale_count']}"
            )
        await asyncio.sleep(5)
```

**Step 3: Verify**
Run: `pytest tests/live/test_runner_health.py` (create if missing, mocking `data_manager.health_monitor`).

**Step 4: Commit**
```bash
git add project/live/runner.py
git commit -m "fix: trigger STALE_DATA kill-switch on health degradation (TICKET-010)"
```

---

## Task 4: TICKET-011 — Real Binance Unwind Implementation

**Files:**
- Modify: `project/live/oms.py`
- Modify: `project/live/kill_switch.py`

**Step 1: Add OMS primitives**
Add `async def cancel_all_orders()` and `async def flatten_all_positions()` to `OrderManager`.
Implement using `Binance` signed request helpers (reusing logic from `run_live_engine.py`).

**Step 2: Implement UnwindOrchestrator**
Update `unwind_all()` in `kill_switch.py` to call the new OMS primitives.

**Step 3: Verify**
Run: `pytest tests/live/test_unwind.py` with `respx` or `aioresponses` mocking Binance API.

**Step 4: Commit**
```bash
git add project/live/oms.py project/live/kill_switch.py
git commit -m "feat: implement real Binance order cancellation and position flattening (TICKET-011)"
```

---

## Task 5: TICKET-012 — Startup Position Reconciliation

**Files:**
- Modify: `project/live/runner.py`

**Step 1: Add reconciliation logic**
In `LiveEngineRunner.start()`, call `await self.reconcile_positions()`.

**Step 2: Implement check**
Fetch Binance positions via `account_snapshot_fetcher`. Compare with `self.state_store.account.positions`.
If any mismatch > 1e-8:
`raise RuntimeError("Startup reconciliation failed: position mismatch")`.

**Step 3: Verify**
Run: `pytest tests/live/test_reconciliation.py`.

**Step 4: Commit**
```bash
git add project/live/runner.py
git commit -m "feat: add strict exchange position reconciliation at startup (TICKET-012)"
```

---

## Task 6: TICKET-013 — Systemd Unit Hardening

**Files:**
- Modify/Rename: `deploy/systemd/edge-live-engine.service`

**Step 1: Add Restart Limits**
Add `StartLimitIntervalSec=60` and `StartLimitBurst=5` to the `[Unit]` or `[Service]` section.

**Step 2: Specific Labeling**
Rename `edge-live-engine.service` to `edge-live-engine-paper.service`. Update `ExecStart` to explicitly point to paper env vars if needed.

**Step 3: Commit**
```bash
git add deploy/systemd/
git commit -m "chore: harden systemd units with restart limits and paper-trading labels (TICKET-013)"
```
