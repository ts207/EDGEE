from __future__ import annotations

import sys
import types

import pandas as pd

import project.core.stats as core_stats


def test_cointegration_uses_statsmodels_pvalue_when_available(monkeypatch):
    statsmodels_mod = types.ModuleType("statsmodels")
    tsa_mod = types.ModuleType("statsmodels.tsa")
    stattools_mod = types.ModuleType("statsmodels.tsa.stattools")

    def fake_coint(x, y):
        return -2.0, 0.5553, [-3.9, -3.3, -3.0]

    stattools_mod.coint = fake_coint
    tsa_mod.stattools = stattools_mod
    statsmodels_mod.tsa = tsa_mod

    monkeypatch.setitem(sys.modules, "statsmodels", statsmodels_mod)
    monkeypatch.setitem(sys.modules, "statsmodels.tsa", tsa_mod)
    monkeypatch.setitem(sys.modules, "statsmodels.tsa.stattools", stattools_mod)

    x = pd.Series(range(100), dtype=float)
    y = x + 0.5

    assert core_stats.test_cointegration(x, y) == 0.5553
