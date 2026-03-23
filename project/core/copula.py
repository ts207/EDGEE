from __future__ import annotations

import numpy as np
import pandas as pd

try:
    from scipy import stats
except ModuleNotFoundError:  # pragma: no cover - environment-specific fallback
    from project.core.stats import stats


def fit_gaussian_copula(u1: np.ndarray, u2: np.ndarray) -> float:
    """
    Estimate the correlation parameter rho for a Gaussian copula.
    Transforms uniforms to standard normal and calculates Pearson correlation.
    """
    # Inverse probability transform
    z1 = stats.norm.ppf(np.clip(u1, 1e-6, 1 - 1e-6))
    z2 = stats.norm.ppf(np.clip(u2, 1e-6, 1 - 1e-6))

    rho = np.corrcoef(z1, z2)[0, 1]
    return float(rho)


def calculate_gaussian_conditional_prob(u1: float, u2: float, rho: float) -> float:
    """
    Calculate P(U1 <= u1 | U2 = u2) for a Gaussian copula with correlation rho.
    """
    z1 = stats.norm.ppf(np.clip(u1, 1e-6, 1 - 1e-6))
    z2 = stats.norm.ppf(np.clip(u2, 1e-6, 1 - 1e-6))

    num = z1 - rho * z2
    denom = np.sqrt(1 - rho**2)

    if denom < 1e-9:
        # If rho is ~1, U1 <= u1 | U2 = u2 is 1 if u1 >= u2 else 0 (roughly)
        # But this is conditional on Z. If rho=1, Z1=Z2. So P(Z1 <= z1 | Z2=z2) = 1 if z2 <= z1 else 0.
        return 1.0 if z2 <= z1 else 0.0

    prob = stats.norm.cdf(num / denom)
    return float(prob)


def get_empirical_uniforms(x: pd.Series) -> pd.Series:
    """
    Transform a series to empirical uniforms (ranks / (N+1)).
    """
    n = len(x)
    return x.rank(method="average") / (n + 1)
