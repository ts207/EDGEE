# Design Doc: Portfolio Overlap Unification

## 1. Objective
Unify the fragmented overlap-group handling logic across the `Edge` codebase into a single, deterministic, and test-backed Portfolio Admission Policy. This ensures the system behaves as a governed portfolio rather than a set of isolated theses.

## 2. Architecture
Introduce a new `PortfolioAdmissionPolicy` component that acts as the authoritative source for overlap-group admission decisions.

### 2.1 Component: `PortfolioAdmissionPolicy`
- **Location:** `project/live/portfolio_policy.py`
- **Responsibility:** Enforce the "Exclusive Overlap Group" invariant.
- **Invariants:**
  - **Incumbent Dominance:** If an overlap group already has an active thesis, any new challenger from the same group is blocked.
  - **Deterministic Selection:** For multiple new candidates in an empty group, exactly one is selected based on a deterministic ranking:
    1. Higher `support_score - contradiction_penalty`.
    2. Higher `sample_size`.
    3. `thesis_id` ascending (tie-breaker).

### 2.2 Integration Points
- **Retriever (`project/live/retriever.py`):** Replaces internal suppression with calls to `PortfolioAdmissionPolicy.resolve_overlap_winners`.
- **RiskEnforcer (`project/live/risk.py`):** Adds a new check in `check_and_apply_caps` that rejects orders if the thesis belongs to an overlap group occupied by a *different* active thesis.
- **LiveEngineRunner (`project/live/runner.py`):** Provides the set of currently active overlap group IDs from the `ThesisStateManager`.

## 3. Data Flow
1. **Event Detection:** Retriever finds potential thesis matches.
2. **Admission Control:** Retriever calls `PortfolioAdmissionPolicy` with matches and current active groups.
3. **Selection:** Policy identifies the winner per group; others are marked with `blocked_by_active_group_member` or `lost_overlap_ranking`.
4. **Order Submission:** `RiskEnforcer` performs a final safety check against the current portfolio state before allowing live orders.

## 4. Error Handling
- Invalid or missing `overlap_group_id` will default to the `thesis_id` (treating it as an "orphaned" group of one).
- Admission failures are recorded in the matching reasons or risk breach history.

## 5. Testing
- **Selection Tests:** Verify ranking and suppression during retrieval.
- **Enforcement Tests:** Verify order rejection when a different group member is active.
- **Tie-Breaker Tests:** Verify deterministic `thesis_id` sorting.

## 6. Status
- [x] Design Approved
- [ ] Implementation Plan Ready
- [ ] Verification Complete
