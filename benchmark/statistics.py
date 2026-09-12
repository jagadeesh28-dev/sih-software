"""
Rigorous statistical testing for multi-seed algorithm comparisons.
Section 27: Paired Wilcoxon signed-rank test (alpha = 0.05), Vargha-Delaney A effect size,
and objective WIN / TIE / LOSS outcome determination.
"""

from typing import Dict, Any, List
import numpy as np
from scipy import stats


def compute_vargha_delaney_a(sample_a: np.ndarray, sample_b: np.ndarray) -> float:
    """
    Compute Vargha-Delaney A effect size (probability that algorithm A yields better performance than B).
    A > 0.5 favors sample_a, A < 0.5 favors sample_b.
    Standard thresholds: |A - 0.5| > 0.06 (small), > 0.14 (medium), > 0.21 (large).
    """
    m = len(sample_a)
    n = len(sample_b)
    if m == 0 or n == 0:
        return 0.5

    r = stats.rankdata(np.concatenate([sample_a, sample_b]))
    r_a = np.sum(r[:m])
    a_stat = (r_a / m - (m + 1) / 2.0) / n
    return float(a_stat)


def perform_wilcoxon_test(
    sample_qpso: np.ndarray,
    sample_baseline: np.ndarray,
    alpha: float = 0.05,
    higher_is_better: bool = True,
) -> Dict[str, Any]:
    """
    Perform paired Wilcoxon signed-rank test across independent seed runs.
    """
    diffs = sample_qpso - sample_baseline if higher_is_better else sample_baseline - sample_qpso

    # If all differences are zero
    if np.all(np.abs(diffs) < 1e-12):
        return {
            "statistic": 0.0,
            "p_value": 1.0,
            "effect_size_a": 0.5,
            "significant": False,
            "outcome": "TIE",
        }

    try:
        w_res = stats.wilcoxon(diffs, alternative="two-sided")
        p_val = float(w_res.pvalue)
        stat = float(w_res.statistic)
    except Exception:
        p_val = 1.0
        stat = 0.0

    a_stat = compute_vargha_delaney_a(sample_qpso, sample_baseline)
    is_sig = p_val < alpha

    outcome = classify_outcome(is_sig, np.median(diffs))

    return {
        "statistic": stat,
        "p_value": p_val,
        "effect_size_a": a_stat,
        "median_difference": float(np.median(diffs)),
        "significant": is_sig,
        "outcome": outcome,
    }


def classify_outcome(is_significant: bool, median_difference: float) -> str:
    """
    Classify benchmark outcome for QPSO vs baseline.
    Returns: 'WIN', 'TIE', or 'LOSS'.
    """
    if not is_significant:
        return "TIE"
    if median_difference > 0:
        return "WIN"
    return "LOSS"
