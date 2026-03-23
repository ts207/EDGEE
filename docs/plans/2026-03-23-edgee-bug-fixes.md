# EDGEE Bug Fixes Implementation Plan

> **For Gemini:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix critical and statistical issues in the EDGEE codebase to ensure reliability and quantitative correctness.

**Architecture:** Surgical fixes to specific files identified in the audit.

**Tech Stack:** Python, NumPy, Pandas, Asyncio.

---

### Task 1: Fix Funding PnL Overcounting

**Files:**
- Modify: `project/engine/pnl.py`
- Test: `project/tests/engine/test_pnl_funding.py` (Create)

**Step 1: Write the failing test**

```python
import pandas as pd
import numpy as np
from project.engine.pnl import compute_pnl_ledger

def test_funding_overcounting_default():
    # 5-minute bars for 1 day = 288 bars
    idx = pd.date_range("2025-01-01", periods=288, freq="5min")
    pos = pd.Series(1.0, index=idx)
    close = pd.Series(100.0, index=idx)
    # Funding rate of 0.01% (0.0001) every 8 hours
    funding_rate = pd.Series(0.0001, index=idx)
    
    # Current behavior: False by default, overcounts
    ledger = compute_pnl_ledger(pos, close, funding_rate=funding_rate, use_event_aligned_funding=False)
    
    # Expected: 0.0001 * 288 bars = 0.0288 (Wrong)
    # Correct (event-aligned): 0.0001 * 3 events = 0.0003
    
    # We want to change the default or normalize. 
    # Let's test that the default now matches event-aligned or is normalized.
    
    ledger_default = compute_pnl_ledger(pos, close, funding_rate=funding_rate)
    assert abs(ledger_default["funding_pnl"].sum()) < 0.001
```

**Step 2: Run test to verify it fails**

Run: `pytest project/tests/engine/test_pnl_funding.py`
Expected: FAIL (sum will be ~0.0288)

**Step 3: Write minimal implementation**

Change default `use_event_aligned_funding=True` in `compute_pnl_ledger` signature.

```python
def compute_pnl_ledger(
    ...,
    use_event_aligned_funding: bool = True, # Change from False
) -> pd.DataFrame:
```

**Step 4: Run test to verify it passes**

Run: `pytest project/tests/engine/test_pnl_funding.py`
Expected: PASS

**Step 5: Commit**

```bash
git add project/engine/pnl.py
git commit -m "fix: set use_event_aligned_funding=True by default to avoid overcounting"
```

---

### Task 2: Remove Dead Code in `_kurtosis`

**Files:**
- Modify: `project/core/stats.py`

**Step 1: Write the failing test**
(No functional change, so no failing test needed, but can verify correctness with existing tests)

**Step 2: Write minimal implementation**

Remove lines 267-277 in `project/core/stats.py` and clean up.

```python
def _kurtosis(values: Iterable[float], fisher: bool = True) -> float:
    # ...
    # Remove:
    # s4 = np.sum(centered**4)
    # s2 = np.sum(centered**2)
    # ...
```

**Step 3: Run existing tests**

Run: `pytest project/tests/core/test_stats.py`
Expected: PASS

**Step 4: Commit**

```bash
git add project/core/stats.py
git commit -m "refactor: remove dead code in _kurtosis"
```

---

### Task 3: Use Newey-West t-stat in `calculate_expectancy_stats`

**Files:**
- Modify: `project/research/gating.py`

**Step 1: Write the failing test**

Verify that `calculate_expectancy_stats` returns a t-stat consistent with Newey-West when there is autocorrelation.

**Step 2: Write minimal implementation**

Update `calculate_expectancy_stats` to use `newey_west_t_stat_for_mean`.

**Step 3: Run tests**

**Step 4: Commit**

```bash
git add project/research/gating.py
git commit -m "fix: use Newey-West t-stat in calculate_expectancy_stats"
```

---

### Task 4: Fix Vol/Units Ambiguity in Kelly Sizing

**Files:**
- Modify: `project/portfolio/sizing.py`

**Step 1: Write the failing test**

```python
from project.portfolio.sizing import calculate_target_notional

def test_kelly_sizing_vol_ambiguity():
    # Test with bps-like vol (250) vs decimal (0.025)
    # Current behavior allows both, resulting in wildly different sizes.
    ...
```

**Step 2: Write minimal implementation**

Normalize `vol_regime` at the top of `calculate_target_notional`.

```python
def calculate_target_notional(...):
    vol_regime = _to_decimal_return(vol_regime)
    # ...
```

**Step 3: Run tests**

**Step 4: Commit**

```bash
git add project/portfolio/sizing.py
git commit -m "fix: normalize vol_regime in calculate_target_notional"
```

---

### Task 5: Verify Critical Issues (1, 2, 3)

Since these seem to be already addressed, I will verify they are correct.

**Step 1: Check `kill_switch.py` for `asyncio`**
**Step 2: Check `sizing.py` for `_to_decimal_return`**
**Step 3: Check `gating_statistics.py` for stub**

If they are indeed fixed, I will just report it.
If I find any subtle issues, I'll add them to the plan.
