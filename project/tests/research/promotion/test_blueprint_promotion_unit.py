from __future__ import annotations
import pytest
import pandas as pd
import numpy as np
from project.research.promotion.blueprint_promotion import (
    calculate_stressed_pnl,
    calculate_realized_cost_ratio,
    get_loss_cluster_lengths,
    calculate_drawdown_metrics,
    fragility_gate
)
from unittest.mock import patch

def test_calculate_stressed_pnl():
    df = pd.DataFrame({
        "split_label": ["train", "validation", "test"],
        "gross_pnl": [100.0, 50.0, 20.0],
        "trading_cost": [5.0, 2.0, 1.0],
        "funding_pnl": [1.0, 0.5, 0.2],
        "borrow_cost": [0.5, 0.2, 0.1]
    })
    # stressed = gross - 2*cost + funding - borrow
    # train: 100 - 10 + 1 - 0.5 = 90.5
    # val: 50 - 4 + 0.5 - 0.2 = 46.3
    # test: 20 - 2 + 0.2 - 0.1 = 18.1
    res = calculate_stressed_pnl(df)
    assert pytest.approx(res["train"]) == 90.5
    assert pytest.approx(res["validation"]) == 46.3
    assert pytest.approx(res["test"]) == 18.1

def test_calculate_stressed_pnl_empty():
    res = calculate_stressed_pnl(pd.DataFrame())
    assert res == {"train": 0.0, "validation": 0.0, "test": 0.0}

def test_calculate_realized_cost_ratio():
    df = pd.DataFrame({
        "split_label": ["train"],
        "gross_pnl": [100.0],
        "trading_cost": [10.0]
    })
    # ratio = cost / (abs(gross) + cost)
    # train: 10 / (100 + 10) = 10 / 110 = 0.090909
    res = calculate_realized_cost_ratio(df)
    assert pytest.approx(res["train"]["realized_cost_ratio"]) == 10.0 / 110.0

def test_get_loss_cluster_lengths():
    pnl = pd.Series([1, -1, -2, 1, -1, 1, 1, -1, -1, -1])
    # clusters: [-1, -2] (len 2), [-1] (len 1), [-1, -1, -1] (len 3)
    res = get_loss_cluster_lengths(pnl)
    assert res == [2, 1, 3]

def test_calculate_drawdown_metrics():
    ts = pd.date_range("2024-01-01", periods=10, freq="1h")
    df = pd.DataFrame({
        "timestamp": ts,
        "split_label": ["train"] * 10,
        "pnl": [0.1, -0.05, -0.05, 0.1, -0.1, 0.1, 0.1, -0.05, -0.05, -0.05]
    })
    res = calculate_drawdown_metrics(df, "train")
    assert res["max_loss_cluster_len"] == 3.0
    assert "cluster_loss_concentration" in res
    assert "tail_conditional_drawdown_95" in res

def test_fragility_gate():
    pnl = pd.Series([0.01] * 100)
    with patch("project.research.promotion.blueprint_promotion.simulate_parameter_perturbation", return_value={"fraction_positive": 0.8}):
        assert fragility_gate(pnl, min_pass_rate=0.6) == True
        assert fragility_gate(pnl, min_pass_rate=0.9) == False

def test_fragility_gate_empty():
    assert fragility_gate(pd.Series()) == False
