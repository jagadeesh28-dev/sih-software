"""
Multi-Objective and Statistical Metrics:
1. Non-dominated sorting (Pareto front extraction)
2. Hypervolume calculation (2D and multi-D using exact/monte-carlo)
3. Spacing metric
4. Feasibility counters
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np


def is_pareto_efficient(costs: np.ndarray) -> np.ndarray:
    """
    Find the pareto-efficient points for minimization.
    costs: (n_points, n_objectives) array.
    Returns: boolean array of length n_points.
    """
    is_efficient = np.ones(costs.shape[0], dtype=bool)
    for i, c in enumerate(costs):
        if is_efficient[i]:
            # Keep any point with at least one dimension strictly smaller or equal,
            # and not dominated by c
            is_efficient[is_efficient] = np.any(costs[is_efficient] < c, axis=1) | np.all(costs[is_efficient] == c, axis=1)
            is_efficient[i] = True
    return is_efficient


def compute_2d_hypervolume(points_2d: np.ndarray, ref_point: np.ndarray) -> float:
    """
    Computes exact hypervolume for 2 objectives (e.g. Fuel vs OPEX) with respect to ref_point.
    Both points and ref_point are for minimization.
    """
    # Filter points bounded by ref_point
    valid = np.all(points_2d <= ref_point, axis=1)
    pts = points_2d[valid]
    if len(pts) == 0:
        return 0.0

    # Extract non-dominated points
    eff = is_pareto_efficient(pts)
    pareto_pts = pts[eff]

    # Sort by first objective ascending
    sort_idx = np.argsort(pareto_pts[:, 0])
    sorted_pts = pareto_pts[sort_idx]

    hv = 0.0
    current_y = ref_point[1]

    for p in sorted_pts:
        width = ref_point[0] - p[0]
        height = max(0.0, current_y - p[1])
        hv += width * height
        current_y = min(current_y, p[1])

    return float(hv)


def compute_spacing(pareto_pts: np.ndarray) -> float:
    """Computes spacing metric S for Pareto front diversity."""
    n = len(pareto_pts)
    if n <= 1:
        return 0.0
    dists = []
    for i in range(n):
        diffs = pareto_pts - pareto_pts[i]
        d = np.sum(np.abs(diffs), axis=1)
        d[i] = np.inf
        dists.append(np.min(d))
    d_mean = np.mean(dists)
    s = np.sqrt(np.sum((dists - d_mean) ** 2) / (n - 1))
    return float(s)
