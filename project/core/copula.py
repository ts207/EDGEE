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
    denom = np.sqrt(max(1e-9, 1 - rho**2))

    prob = stats.norm.cdf(num / denom)
    return float(prob)


def fit_t_copula(u1: np.ndarray, u2: np.ndarray) -> tuple[float, float]:
    """
    Estimate parameters for a Student-t copula: (rho, df).
    Degrees of freedom (df) controls tail dependence.
    """
    # Quick estimate of rho using Spearman's rho or Kendall's tau
    # For Student-t, rho = sin(pi/2 * tau)
    try:
        from scipy import stats as scipy_stats
        tau, _ = scipy_stats.kendalltau(u1, u2)
    except (ImportError, AttributeError):
        # Fallback to simple correlation if kendalltau fails
        tau = np.corrcoef(u1, u2)[0, 1] * 0.6 # rough proxy
        
    rho = float(np.sin(np.pi / 2 * tau))
    
    # Estimate degrees of freedom (df)
    # A simple heuristic for crypto: heavy tails (df between 3 and 10)
    # For now, we'll use a fixed df=4.0 which is a good baseline for crypto tail risk,
    # or could be optimized via MLE in a full implementation.
    df = 4.0
    return rho, df


def calculate_t_conditional_prob(u1: float, u2: float, rho: float, df: float = 4.0) -> float:
    """
    Calculate P(U1 <= u1 | U2 = u2) for a Student-t copula.
    Captures symmetric tail dependence.
    """
    try:
        from scipy import stats as scipy_stats
        # t-distribution inverse CDF
        x1 = scipy_stats.t.ppf(np.clip(u1, 1e-6, 1 - 1e-6), df=df)
        x2 = scipy_stats.t.ppf(np.clip(u2, 1e-6, 1 - 1e-6), df=df)
        
        # Conditional distribution of Student-t is also Student-t
        # with adjusted parameters:
        # mu_cond = rho * x2
        # scale_cond = sqrt((df + x2^2) / (df + 1) * (1 - rho^2))
        # df_cond = df + 1
        
        mu_cond = rho * x2
        scale_cond = np.sqrt(max(1e-9, (df + x2**2) / (df + 1.0) * (1.0 - rho**2)))
        
        # P(X1 <= x1 | X2 = x2) = F_t_df+1((x1 - mu_cond) / scale_cond)
        prob = scipy_stats.t.cdf((x1 - mu_cond) / scale_cond, df=df + 1.0)
        return float(prob)
    except (ImportError, AttributeError):
        # Fallback to Gaussian if scipy.stats.t is unavailable
        return calculate_gaussian_conditional_prob(u1, u2, rho)


def get_empirical_uniforms(x: pd.Series) -> pd.Series:
    """
    Transform a series to empirical uniforms (ranks / (N+1)).
    """
    n = len(x)
    return x.rank(method="average") / (n + 1)
