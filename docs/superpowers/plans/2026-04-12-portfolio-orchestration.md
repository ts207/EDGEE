# Portfolio Orchestration Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the centralized portfolio orchestration layer using a dynamic constraint-weighted greedy arbitration policy.

**Architecture:** A stateless target-state generator that takes a snapshot of thesis intents and current portfolio constraints, ranks them by marginal utility, and greedily allocates capital while dynamically penalizing correlated clusters to ensure structural diversification.

**Tech Stack:** Python 3, Pydantic, Pandas, Pytest.

---

### Task 1: Define Schemas for Orchestration

**Files:**
- Create: `project/portfolio/orchestration.py`
- Test: `project/tests/portfolio/test_orchestration.py`

- [ ] **Step 1: Write the failing test**

```python
# project/tests/portfolio/test_orchestration.py
import pytest
from project.portfolio.orchestration import ThesisIntent, PortfolioContext, TargetPortfolioState

def test_schemas_instantiate():
    intent = ThesisIntent(
        strategy_id="strat_1",
        family_id="momentum",
        symbol="BTC",
        requested_notional=10000.0,
        setup_match=0.9,
        thesis_strength=0.8,
        freshness=1.0,
        execution_quality=0.95,
        capital_efficiency=1.2
    )
    context = PortfolioContext(
        max_portfolio_notional=100000.0,
        family_caps={"momentum": 20000.0},
        symbol_caps={"BTC": 30000.0}
    )
    state = TargetPortfolioState(allocations={"strat_1": 5000.0})
    
    assert intent.strategy_id == "strat_1"
    assert context.max_portfolio_notional == 100000.0
    assert state.allocations["strat_1"] == 5000.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest project/tests/portfolio/test_orchestration.py::test_schemas_instantiate -v`
Expected: FAIL with ImportError (module not found).

- [ ] **Step 3: Write minimal implementation**

```python
# project/portfolio/orchestration.py
from pydantic import BaseModel, Field
from typing import Dict, Optional

class ThesisIntent(BaseModel):
    strategy_id: str
    family_id: str
    symbol: str
    requested_notional: float
    setup_match: float
    thesis_strength: float
    freshness: float
    execution_quality: float
    capital_efficiency: float

class PortfolioContext(BaseModel):
    max_portfolio_notional: float
    family_caps: Dict[str, float] = Field(default_factory=dict)
    symbol_caps: Dict[str, float] = Field(default_factory=dict)

class TargetPortfolioState(BaseModel):
    allocations: Dict[str, float]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest project/tests/portfolio/test_orchestration.py::test_schemas_instantiate -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add project/portfolio/orchestration.py project/tests/portfolio/test_orchestration.py
git commit -m "feat: add schemas for portfolio orchestration"
```

---

### Task 2: Implement Dynamic Utility Scoring

**Files:**
- Modify: `project/portfolio/orchestration.py`
- Modify: `project/tests/portfolio/test_orchestration.py`

- [ ] **Step 1: Write the failing test**

```python
# project/tests/portfolio/test_orchestration.py
from project.portfolio.orchestration import calculate_priority_score

def test_calculate_priority_score():
    intent = ThesisIntent(
        strategy_id="strat_1",
        family_id="momentum",
        symbol="BTC",
        requested_notional=10000.0,
        setup_match=0.9,
        thesis_strength=0.8,
        freshness=1.0,
        execution_quality=0.95,
        capital_efficiency=1.2
    )
    # score = 0.9 * 0.8 * 1.0 * 0.95 * 1.2 * 1.0 (diversification mult) = 0.8208
    score = calculate_priority_score(intent, diversification_multiplier=1.0)
    assert abs(score - 0.8208) < 1e-6
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest project/tests/portfolio/test_orchestration.py::test_calculate_priority_score -v`
Expected: FAIL with ImportError for `calculate_priority_score`.

- [ ] **Step 3: Write minimal implementation**

```python
# project/portfolio/orchestration.py (append)

def calculate_priority_score(intent: ThesisIntent, diversification_multiplier: float) -> float:
    return (
        intent.setup_match *
        intent.thesis_strength *
        intent.freshness *
        intent.execution_quality *
        intent.capital_efficiency *
        diversification_multiplier
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest project/tests/portfolio/test_orchestration.py::test_calculate_priority_score -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add project/portfolio/orchestration.py project/tests/portfolio/test_orchestration.py
git commit -m "feat: implement dynamic priority scoring"
```

---

### Task 3: Implement Greedy Allocation Loop

**Files:**
- Modify: `project/portfolio/orchestration.py`
- Modify: `project/tests/portfolio/test_orchestration.py`

- [ ] **Step 1: Write the failing test**

```python
# project/tests/portfolio/test_orchestration.py
from project.portfolio.orchestration import generate_target_portfolio

def test_generate_target_portfolio_greedy_with_dynamic_penalty():
    intent1 = ThesisIntent(strategy_id="strat_1", family_id="momentum", symbol="BTC", requested_notional=10000.0, setup_match=1.0, thesis_strength=1.0, freshness=1.0, execution_quality=1.0, capital_efficiency=1.0)
    # intent2 has lower setup match, but same family
    intent2 = ThesisIntent(strategy_id="strat_2", family_id="momentum", symbol="ETH", requested_notional=10000.0, setup_match=0.9, thesis_strength=1.0, freshness=1.0, execution_quality=1.0, capital_efficiency=1.0)
    # intent3 is a different family, slightly lower setup match than intent1 but higher than intent2
    intent3 = ThesisIntent(strategy_id="strat_3", family_id="mean_reversion", symbol="BTC", requested_notional=10000.0, setup_match=0.95, thesis_strength=1.0, freshness=1.0, execution_quality=1.0, capital_efficiency=1.0)
    
    context = PortfolioContext(
        max_portfolio_notional=15000.0, # Only enough capital for 1.5 intents
        family_caps={"momentum": 12000.0}, # Momentum is capped
        symbol_caps={"BTC": 20000.0}
    )
    
    state = generate_target_portfolio([intent1, intent2, intent3], context)
    
    # strat_1 should get 10000 (highest score, first to allocate)
    assert state.allocations["strat_1"] == 10000.0
    
    # Remaining capital = 5000.
    # strat_3 (score 0.95) vs strat_2 (score 0.9). 
    # Because strat_1 allocated 10k to momentum, strat_2's diversification multiplier drops, making strat_3 win the rest.
    assert state.allocations["strat_3"] == 5000.0
    
    # strat_2 gets nothing because capital is exhausted.
    assert state.allocations.get("strat_2", 0.0) == 0.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest project/tests/portfolio/test_orchestration.py::test_generate_target_portfolio_greedy_with_dynamic_penalty -v`
Expected: FAIL (generate_target_portfolio not defined).

- [ ] **Step 3: Write minimal implementation**

```python
# project/portfolio/orchestration.py (append)
from typing import List

def generate_target_portfolio(intents: List[ThesisIntent], context: PortfolioContext) -> TargetPortfolioState:
    allocations = {}
    current_portfolio_notional = 0.0
    current_family_exposure = {k: 0.0 for k in context.family_caps.keys()}
    current_symbol_exposure = {k: 0.0 for k in context.symbol_caps.keys()}
    
    # Track remaining intents
    remaining_intents = intents.copy()
    
    while remaining_intents and current_portfolio_notional < context.max_portfolio_notional:
        best_intent = None
        best_score = -1.0
        
        for intent in remaining_intents:
            # Calculate dynamic diversification multiplier.
            # Simple heuristic: penalty scales with how close the family is to its cap.
            family_cap = context.family_caps.get(intent.family_id, context.max_portfolio_notional)
            current_family = current_family_exposure.get(intent.family_id, 0.0)
            
            if current_family >= family_cap:
                div_multiplier = 0.0
            else:
                # E.g., if 0% used -> 1.0. If 50% used -> 0.5
                div_multiplier = 1.0 - (current_family / family_cap)
            
            score = calculate_priority_score(intent, div_multiplier)
            if score > best_score:
                best_score = score
                best_intent = intent
                
        if not best_intent or best_score <= 0.0:
            break # No valid intents left or caps hit
            
        remaining_intents.remove(best_intent)
        
        # Determine max allocatable
        available_portfolio = context.max_portfolio_notional - current_portfolio_notional
        family_cap = context.family_caps.get(best_intent.family_id, context.max_portfolio_notional)
        available_family = family_cap - current_family_exposure.get(best_intent.family_id, 0.0)
        
        symbol_cap = context.symbol_caps.get(best_intent.symbol, context.max_portfolio_notional)
        available_symbol = symbol_cap - current_symbol_exposure.get(best_intent.symbol, 0.0)
        
        max_allocatable = min(best_intent.requested_notional, available_portfolio, available_family, available_symbol)
        
        if max_allocatable > 0:
            allocations[best_intent.strategy_id] = max_allocatable
            current_portfolio_notional += max_allocatable
            current_family_exposure[best_intent.family_id] = current_family_exposure.get(best_intent.family_id, 0.0) + max_allocatable
            current_symbol_exposure[best_intent.symbol] = current_symbol_exposure.get(best_intent.symbol, 0.0) + max_allocatable

    # Ensure all missing intents have 0.0
    for intent in intents:
        if intent.strategy_id not in allocations:
            allocations[intent.strategy_id] = 0.0
            
    return TargetPortfolioState(allocations=allocations)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest project/tests/portfolio/test_orchestration.py::test_generate_target_portfolio_greedy_with_dynamic_penalty -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add project/portfolio/orchestration.py project/tests/portfolio/test_orchestration.py
git commit -m "feat: implement dynamic constraint-weighted greedy allocation loop"
```
