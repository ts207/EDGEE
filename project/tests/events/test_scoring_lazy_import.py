from __future__ import annotations

import builtins
import importlib
import sys

import pandas as pd
import pytest


def test_scoring_import_succeeds_without_sklearn(monkeypatch):
    original_import = builtins.__import__

    def _guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name.startswith("sklearn"):
            raise ModuleNotFoundError("No module named 'sklearn'")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", _guarded_import)
    sys.modules.pop("project.events.scoring", None)
    sys.modules.pop("project.events.scoring.confidence", None)

    scoring = importlib.import_module("project.events.scoring")

    assert callable(scoring.score_event_frame)
    assert "event_tradeability_score" in scoring.EventScoreColumns


def test_confidence_training_raises_clear_dependency_error_without_sklearn(monkeypatch):
    original_import = builtins.__import__

    def _guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name.startswith("sklearn"):
            raise ModuleNotFoundError("No module named 'sklearn'")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", _guarded_import)
    sys.modules.pop("project.events.scoring", None)
    sys.modules.pop("project.events.scoring.confidence", None)

    scoring = importlib.import_module("project.events.scoring")
    frame = pd.DataFrame(
        {
            "target": [0, 1],
            "timestamp": pd.date_range("2024-01-01", periods=2, freq="5min", tz="UTC"),
        }
    )

    with pytest.raises(ModuleNotFoundError, match="scikit-learn is required"):
        scoring.train_event_confidence_model(
            frame,
            candidate_feature_columns=["timestamp"],
            min_train_rows=1,
        )
