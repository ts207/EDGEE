from __future__ import annotations
import pytest
import pandas as pd
import numpy as np
from project.research.services.candidate_discovery_scoring import (
    _split_labels,
    _evaluation_mask,
    _float_mean,
    _t_stat,
    _regime_labels
)

def test_split_labels():
    df = pd.DataFrame({"split_label": ["Train ", " Validation", "test"]})
    res = _split_labels(df)
    assert res.tolist() == ["train", "validation", "test"]
    
    df_no_label = pd.DataFrame({"a": [1, 2]})
    res = _split_labels(df_no_label)
    assert res.tolist() == ["train", "train"]

def test_evaluation_mask():
    labels = pd.Series(["train", "validation", "test"])
    mask = _evaluation_mask(labels)
    assert mask.tolist() == [False, True, True]
    
    labels_only_train = pd.Series(["train", "train"])
    mask = _evaluation_mask(labels_only_train)
    assert mask.all() # Fallback to all if no val/test

def test_float_mean():
    df = pd.DataFrame({"a": [1.0, 2.0, "nan", 3.0]})
    assert _float_mean(df, "a") == 2.0
    assert _float_mean(df, "missing") == 0.0

def test_t_stat():
    df = pd.DataFrame({"a": [1.0, 2.0, 3.0]})
    # mean=2.0, std=1.0, n=3. t = 2 / (1 / sqrt(3)) = 2 * sqrt(3) = 3.464
    assert pytest.approx(_t_stat(df, "a")) == 3.4641016

def test_regime_labels():
    df = pd.DataFrame({"vol_regime": ["low", "high", np.nan]})
    res = _regime_labels(df)
    assert res.tolist() == ["low", "high", "unknown"]
    
    df_no_regime = pd.DataFrame({"a": [1]})
    res = _regime_labels(df_no_regime)
    assert res.tolist() == ["unknown"]
