"""
Statistical Significance and Diversity Engine.
SIH26138 - Phase 6

Implements:
1. Paired Wilcoxon signed-rank test across matched seeds.
2. Holm-Bonferroni multiple testing correction.
3. Rank-biserial correlation (r) effect size.
4. Hodges-Lehmann estimator for median paired difference.
5. Bootstrap 95% Confidence Intervals.
6. Feature Selection Stability (Pairwise Jaccard Similarity).
7. Population Diversity (Pairwise Hamming Distance & Shannon Entropy).
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from scipy import stats


class PredictionStatisticsEngine:
    """Rigorous statistical testing and diversity analysis for prediction benchmarks."""

    @staticmethod
    def paired_wilcoxon_test(
        baseline_scores: np.ndarray,
        candidate_scores: np.ndarray,
    ) -> Dict[str, float]:
        """
        Computes two-sided paired Wilcoxon signed-rank test between matched seed results.
        Returns p-value, rank-biserial correlation, and Hodges-Lehmann median difference.
        """
        diffs = candidate_scores - baseline_scores
        # Filter out exact zero differences for Wilcoxon
        non_zero_diffs = diffs[diffs != 0]

        if len(non_zero_diffs) < 5:
            return {
                "p_value": 1.0,
                "rank_biserial_r": 0.0,
                "hodges_lehmann": float(np.median(diffs)),
                "stat": 0.0,
            }

        res = stats.wilcoxon(diffs, alternative="two-sided")
        w_stat = float(res.statistic)
        p_val = float(res.pvalue)

        # Rank-biserial correlation
        ranks = stats.rankdata(np.abs(non_zero_diffs))
        w_pos = np.sum(ranks[non_zero_diffs > 0])
        w_neg = np.sum(ranks[non_zero_diffs < 0])
        total_w = w_pos + w_neg
        r_biserial = float((w_pos - w_neg) / total_w) if total_w > 0 else 0.0

        # Hodges-Lehmann estimator: median of pairwise Walsh averages
        walsh_averages = []
        n = len(diffs)
        for i in range(n):
            for j in range(i, n):
                walsh_averages.append(0.5 * (diffs[i] + diffs[j]))
        hl_diff = float(np.median(walsh_averages))

        return {
            "p_value": p_val,
            "rank_biserial_r": r_biserial,
            "hodges_lehmann": hl_diff,
            "stat": w_stat,
        }

    @staticmethod
    def holm_bonferroni_correction(p_values: List[float]) -> List[float]:
        """
        Applies step-down Holm-Bonferroni correction to a list of p-values.
        Preserves family-wise error rate (FWER) at alpha = 0.05.
        """
        m = len(p_values)
        indexed_p = sorted(enumerate(p_values), key=lambda x: x[1])
        adjusted_p = [0.0] * m

        running_max = 0.0
        for rank, (orig_idx, p_val) in enumerate(indexed_p):
            # Adjusted p = min(1.0, (m - rank) * p)
            adj = (m - rank) * p_val
            adj = max(running_max, min(1.0, adj))
            running_max = adj
            adjusted_p[orig_idx] = adj

        return adjusted_p

    @staticmethod
    def bootstrap_ci(
        values: np.ndarray,
        n_boot: int = 1000,
        alpha: float = 0.05,
        seed: int = 42,
    ) -> Tuple[float, float]:
        """Calculates 95% bootstrap confidence interval of the mean."""
        rng = np.random.default_rng(seed)
        n = len(values)
        boot_means = [np.mean(rng.choice(values, size=n, replace=True)) for _ in range(n_boot)]
        ci_low = float(np.percentile(boot_means, 100 * (alpha / 2)))
        ci_high = float(np.percentile(boot_means, 100 * (1 - alpha / 2)))
        return ci_low, ci_high

    @staticmethod
    def jaccard_feature_stability(feature_masks: List[np.ndarray]) -> Dict[str, float]:
        """
        Computes pairwise Jaccard similarity across feature selection runs:
        J(A, B) = |A cap B| / |A cup B|.
        Measures stability of selected feature subsets across independent seeds.
        """
        n_runs = len(feature_masks)
        if n_runs < 2:
            return {"mean_jaccard": 1.0, "std_jaccard": 0.0}

        jaccards = []
        for i in range(n_runs):
            for j in range(i + 1, n_runs):
                set_i = set(np.where(feature_masks[i] == 1)[0])
                set_j = set(np.where(feature_masks[j] == 1)[0])
                union = set_i | set_j
                inter = set_i & set_j
                if len(union) > 0:
                    jaccards.append(len(inter) / len(union))
                else:
                    jaccards.append(1.0)

        return {
            "mean_jaccard": float(np.mean(jaccards)),
            "std_jaccard": float(np.std(jaccards)),
            "min_jaccard": float(np.min(jaccards)),
            "max_jaccard": float(np.max(jaccards)),
        }

    @staticmethod
    def population_hamming_diversity(binary_masks: List[np.ndarray]) -> float:
        """Computes mean normalized Hamming distance between binary configurations."""
        n = len(binary_masks)
        if n < 2:
            return 0.0
        dists = []
        m = len(binary_masks[0])
        for i in range(n):
            for j in range(i + 1, n):
                dists.append(np.sum(binary_masks[i] != binary_masks[j]) / m)
        return float(np.mean(dists))
