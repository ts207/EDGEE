# EDGEE Bug Fixes Batch 2 Implementation Plan

> **For Gemini:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix advanced quantitative, statistical, and architectural issues in the EDGEE codebase.

**Architecture:** Targeted improvements to core calculation engines and research tools.

**Tech Stack:** Python, NumPy, Pandas, SciPy.

---

### Task 1: Rolling Correlation in Risk Allocator (Issue 8)

**Files:**
- Modify: `project/engine/risk_allocator.py`
- Test: `project/tests/engine/test_risk_allocator_rolling_corr.py`

**Step 1: Write failing test**
Verify that the correlation constraint adapts to time-varying correlation.

**Step 2: Implement rolling correlation**
Update the pairwise correlation logic (lines 498-542) to use a rolling window correlation.

```python
# Instead of static tail correlation
# corr_mat = df_alloc.tail(corr_window).corr().abs().fillna(0.0)

# Use rolling correlation
# This requires calculating the correlation at each bar t using a window [t-W, t]
# To avoid O(N*W) complexity, we can use pd.DataFrame.rolling(W).corr()
```
Actually, the `allocate_position_details` function seems to process the entire history at once.

**Step 3: Run tests**

---

### Task 2: Correct ADF p-values in Cointegration Fallback (Issue 9)

**Files:**
- Modify: `project/core/stats.py`

**Step 1: Implement MacKinnon critical value lookup**
Add a helper to provide approximate ADF p-values based on MacKinnon (1994) tables instead of the standard t-distribution.

**Step 2: Run tests**

---

### Task 3: Improve PSR/DSR Small-Sample Accuracy (Issue 10)

**Files:**
- Modify: `project/eval/selection_bias.py`

**Step 1: Implement expected maximum lookup**
For `n_trials < 20`, use hardcoded expected maximums of $n$ IID standard normals instead of the Euler-Mascheroni approximation.

---

### Task 4: Log Swallowed Exceptions in Campaign Controller (Issue 11)

**Files:**
- Modify: `project/pipelines/research/campaign_controller.py`

**Step 1: Replace bare `except: pass`**
Update all instances of silent exception swallowing to include at least a `_LOG.warning(..., exc_info=True)`.

---

### Task 5: Cap Vol Scaling (Issue 12)

**Files:**
- Modify: `project/engine/risk_allocator.py`

**Step 1: Update RiskLimits**
Add `allow_lever_up: bool = False`.

**Step 2: Update Vol Scaling**
Clip `vol_scale` upper bound to 1.0 if `allow_lever_up` is False.

---

### Task 6: Fix PnL Component Consistency and Flip Trades (Issue 13, 17)

**Files:**
- Modify: `project/engine/pnl.py`

**Step 1: Update `compute_pnl_components`**
Ensure flip trades (long to short) use the new position for the intrabar leg of the return, matching `build_execution_state`.

---

### Task 7: Add Student-t Copula (Issue 14)

**Files:**
- Modify: `project/core/copula.py`

**Step 1: Implement Student-t Copula**
Add `fit_t_copula` and `calculate_t_conditional_prob`.

---

### Task 8: Add Kendall's τ Scalability Guard (Issue 15)

**Files:**
- Modify: `project/core/stats.py`

**Step 1: Add length check to `_kendalltau`**
Raise `ImportError` if $n > 1000$ and `scipy` is not available.

---

### Task 9: Consolidate BH-FDR Implementations (Issue 16)

**Files:**
- Modify: `project/research/validation/multiple_testing.py`

**Step 1: Redirect to `core/stats.py::bh_adjust`**
Deprecate the local implementation and use the one in `core/stats`.

---

### Task 10: Add Budget Protection to Discovery (Issue 18)

**Files:**
- Modify: `project/research/discovery.py`

**Step 1: Add `max_hypotheses` pruning**
In `_synthesize_registry_candidates` and similar, ensure the number of generated hypotheses does not exceed a configured budget.
