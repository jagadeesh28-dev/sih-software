"""
Statistical Analysis Pipeline for Multi-Algorithm Benchmarking.
Implements:
1. Friedman omnibus test for repeated measures
2. Robust paired Wilcoxon signed-rank test with zero-difference handling (|Delta J| <= 1e-5)
3. Holm-Bonferroni Family-Wise Error Rate (FWER) correction
4. Exact/Monte-Carlo paired permutation test (100,000 resamples)
5. Rank-biserial effect size r
6. Hodges-Lehmann median difference estimator
7. Paired percentile bootstrap 95% confidence intervals
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from scipy import stats


def robust_wilcoxon_paired(diff: np.ndarray, threshold: float = 1e-5) -> Dict[str, Any]:
    """
    Robust paired Wilcoxon test handling ties below tolerance threshold.
    """
    diff = np.asarray(diff, dtype=float)
    n_total = len(diff)
    diff_thresh = np.where(np.abs(diff) <= threshold, 0.0, diff)
    non_zero = diff_thresh[diff_thresh != 0.0]
    n_nonzero = len(non_zero)
    n_zero = n_total - n_nonzero

    if n_nonzero == 0:
        return {
            "statistic": np.nan,
            "p_value": 1.0,
            "is_significant": False,
            "status": "ALL_TIES",
            "n_nonzero": 0,
            "n_zero": n_zero,
            "rank_biserial": 0.0,
        }

    res = stats.wilcoxon(diff_thresh, zero_method="wilcox", alternative="two-sided")
    pos_ranks = diff_thresh[diff_thresh > 0]
    neg_ranks = diff_thresh[diff_thresh < 0]
    w_plus = float(np.sum(np.abs(pos_ranks)))
    w_minus = float(np.sum(np.abs(neg_ranks)))
    w_tot = w_plus + w_minus
    r_biserial = float((w_minus - w_plus) / max(w_tot, 1e-12)) if w_tot > 0 else 0.0

    return {
        "statistic": float(res.statistic),
        "p_value": float(res.pvalue),
        "is_significant": bool(res.pvalue < 0.05),
        "status": "COMPUTED",
        "n_nonzero": n_nonzero,
        "n_zero": n_zero,
        "rank_biserial": round(r_biserial, 4),
    }


def permutation_test_paired(diff: np.ndarray, n_permutations: int = 100000, seed: int = 42) -> float:
    """Paired sign-flip permutation test."""
    rng = np.random.default_rng(seed)
    diff = np.asarray(diff, dtype=float)
    obs_mean = float(np.mean(diff))
    if abs(obs_mean) < 1e-9:
        return 1.0
    signs = rng.choice([-1.0, 1.0], size=(n_permutations, len(diff)))
    perm_means = np.mean(diff * signs, axis=1)
    p_val = float(np.mean(np.abs(perm_means) >= np.abs(obs_mean)))
    return max(p_val, 1.0 / n_permutations)


def hodges_lehmann_median_diff(diff: np.ndarray) -> float:
    """Computes Hodges-Lehmann pseudo-median difference via Walsh averages."""
    diff = np.asarray(diff, dtype=float)
    walsh = []
    n = len(diff)
    for i in range(n):
        for j in range(i, n):
            walsh.append((diff[i] + diff[j]) / 2.0)
    return float(np.median(walsh))


def bootstrap_mean_diff_ci(diff: np.ndarray, n_boot: int = 10000, ci: float = 0.95, seed: int = 42) -> Tuple[float, float]:
    """Paired bootstrap confidence interval for mean difference."""
    rng = np.random.default_rng(seed)
    diff = np.asarray(diff, dtype=float)
    boot_means = [float(np.mean(rng.choice(diff, size=len(diff), replace=True))) for _ in range(n_boot)]
    alpha = (1.0 - ci) / 2.0
    lower = float(np.percentile(boot_means, alpha * 100.0))
    upper = float(np.percentile(boot_means, (1.0 - alpha) * 100.0))
    return lower, upper


def holm_bonferroni_correction(p_values: List[float]) -> List[float]:
    """Applies step-down Holm-Bonferroni correction to a list of p-values."""
    m = len(p_values)
    indices = np.argsort(p_values)
    adjusted = np.zeros(m)
    current_max = 0.0

    for rank, idx in enumerate(indices):
        p = p_values[idx]
        adj = p * (m - rank)
        current_max = max(current_max, adj)
        adjusted[idx] = min(1.0, current_max)

    return list(adjusted)


def run_omnibus_friedman(df_matrix: pd.DataFrame) -> Tuple[float, float]:
    """
    Executes Friedman test across multiple algorithms (columns) over matched seeds (rows).
    Returns (chi2_stat, p_value).
    """
    args = [df_matrix[col].to_numpy() for col in df_matrix.columns]
    res = stats.friedmanchisquare(*args)
    return float(res.statistic), float(res.pvalue)
