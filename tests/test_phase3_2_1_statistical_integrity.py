"""
Phase 3.2.1 Statistical Integrity and Zero-Difference Handling Regression Tests.
Guarantees:
1. When all paired differences are zero or within numerical tolerance (<= 1e-5),
   hypothesis test reports n_nonzero = 0, p-value = 1.0 (or NOT_APPLICABLE), and
   is_significant = False.
2. The system NEVER reports 'statistically significant = True' when all pairs tie.
3. True differences (such as QPSO vs Random Search) retain statistical significance.
4. Objective decomposition J = sum(w_k * f_k / s_k) + penalties holds within numerical tolerance.
"""

import numpy as np
import pytest
from scipy import stats


def robust_paired_wilcoxon(
    diff: np.ndarray,
    zero_tolerance: float = 1e-5,
    zero_method: str = "wilcox",
) -> dict:
    """
    Independent robust paired Wilcoxon evaluator with explicit zero-difference handling.
    Prevents floating-point discretization micro-noise from producing false-positive p-values.
    """
    diff = np.asarray(diff, dtype=float)
    n_total = len(diff)
    
    # Apply numerical tolerance threshold
    diff_thresh = np.where(np.abs(diff) <= zero_tolerance, 0.0, diff)
    non_zero = diff_thresh[diff_thresh != 0.0]
    n_nonzero = len(non_zero)
    n_zero = n_total - n_nonzero

    if n_nonzero == 0:
        return {
            "n_total": n_total,
            "n_nonzero": 0,
            "n_zero": n_zero,
            "statistic": np.nan,
            "p_value": 1.0,
            "is_significant": False,
            "status": "NOT_APPLICABLE_ALL_TIES",
            "effect_size": 0.0,
        }

    res = stats.wilcoxon(diff_thresh, zero_method=zero_method, alternative="two-sided")
    
    # Rank-biserial effect size
    pos_ranks = diff_thresh[diff_thresh > 0]
    neg_ranks = diff_thresh[diff_thresh < 0]
    w_plus = np.sum(np.abs(pos_ranks))
    w_minus = np.sum(np.abs(neg_ranks))
    w_tot = w_plus + w_minus
    r_biserial = float((w_minus - w_plus) / max(w_tot, 1e-12)) if w_tot > 0 else 0.0

    return {
        "n_total": n_total,
        "n_nonzero": n_nonzero,
        "n_zero": n_zero,
        "statistic": float(res.statistic),
        "p_value": float(res.pvalue),
        "is_significant": bool(res.pvalue < 0.05),
        "status": "VALID",
        "effect_size": r_biserial,
    }


def test_zero_difference_handling_all_exact_zeros():
    """All paired differences are exact 0.0: must yield p=1.0 and is_significant=False."""
    diff = np.zeros(30)
    result = robust_paired_wilcoxon(diff)
    
    assert result["n_nonzero"] == 0
    assert result["n_zero"] == 30
    assert result["p_value"] == 1.0
    assert not result["is_significant"]
    assert result["status"] == "NOT_APPLICABLE_ALL_TIES"
    assert result["effect_size"] == 0.0


def test_zero_difference_handling_floating_point_micro_noise():
    """
    Floating-point micro-noise (~1e-7 to 1e-9) must NOT trigger artificial significance.
    This was the exact defect discovered in Phase 3.2.
    """
    np.random.seed(42)
    # Simulated 1e-7 noise where signs happen to be skewed (e.g. 25 positive, 5 negative)
    diff = np.array([2.8e-7] * 25 + [-1.2e-7] * 5)
    
    # Without thresholding, raw scipy.stats.wilcoxon gives p < 0.01!
    raw_p = stats.wilcoxon(diff).pvalue
    assert raw_p < 0.05  # Proves raw Wilcoxon is vulnerable to micro-noise

    # With robust thresholding, it must be recognized as all ties
    result = robust_paired_wilcoxon(diff, zero_tolerance=1e-5)
    assert result["n_nonzero"] == 0
    assert result["n_zero"] == 30
    assert result["p_value"] == 1.0
    assert not result["is_significant"]
    assert result["status"] == "NOT_APPLICABLE_ALL_TIES"


def test_de_vs_qpso_empirical_data_tied():
    """Verify that empirical DE and QPSO vectors from SCEN-01 benchmark are evaluated as tied."""
    import pandas as pd
    from pathlib import Path

    csv_path = Path("results/experiments/optimization_phase3_2/optimizer_summary.csv")
    if not csv_path.exists():
        pytest.skip("optimizer_summary.csv not found")

    df = pd.read_csv(csv_path)
    qpso = df[df["optimizer"] == "QPSO"].sort_values("seed")["best_loss"].values
    de = df[df["optimizer"] == "DE"].sort_values("seed")["best_loss"].values
    diff = qpso - de

    result = robust_paired_wilcoxon(diff, zero_tolerance=1e-5)
    assert result["n_zero"] == 30
    assert result["n_nonzero"] == 0
    assert not result["is_significant"]
    assert result["p_value"] == 1.0


def test_true_difference_preserves_significance():
    """Verify that genuinely different distributions (e.g. QPSO vs Random Search) are significant."""
    import pandas as pd
    from pathlib import Path

    csv_path = Path("results/experiments/optimization_phase3_2/optimizer_summary.csv")
    if not csv_path.exists():
        pytest.skip("optimizer_summary.csv not found")

    df = pd.read_csv(csv_path)
    qpso = df[df["optimizer"] == "QPSO"].sort_values("seed")["best_loss"].values
    rnd = df[df["optimizer"] == "Random_Search"].sort_values("seed")["best_loss"].values
    diff = qpso - rnd  # negative because QPSO is better

    result = robust_paired_wilcoxon(diff, zero_tolerance=1e-5)
    assert result["n_nonzero"] == 30
    assert result["p_value"] < 0.001
    assert result["is_significant"]
    assert result["effect_size"] == 1.0  # 100% wins for QPSO


def test_objective_reconstruction_fidelity():
    """Verify J = sum(w_k * f_k / s_k) + penalty holds within numerical tolerance."""
    import pandas as pd
    from pathlib import Path

    csv_path = Path("results/experiments/optimization_phase3_2/optimizer_summary.csv")
    if not csv_path.exists():
        pytest.skip("optimizer_summary.csv not found")

    df = pd.read_csv(csv_path)
    weights = np.array([0.35, 0.30, 0.25, 0.05, 0.05])
    scales = np.array([50.0, 50000.0, 150.0, 10.0, 15.0])

    max_err = 0.0
    for _, row in df.iterrows():
        f_vec = np.array([
            row["total_fuel_tonnes"],
            row["total_opex_usd"],
            row["total_wtw_ghg_tonnes"],
            row["schedule_delay_hours"],
            row["uncertainty_risk_tonnes"],
        ])
        j_calc = float(np.sum(weights * (f_vec / scales)) + row["penalty"])
        err = abs(j_calc - row["best_loss"])
        max_err = max(max_err, err)

    assert max_err < 1e-4, f"Reconstruction error {max_err} exceeds 1e-4 tolerance."
