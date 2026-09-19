"""
Multi-Objective Pareto Analysis & Decision-Support Engine.
Implements non-dominated sorting, Hypervolume, Generational Distance, IGD, Spacing,
and operational compromise selection presets (Fuel, Cost, Green, Balanced).
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np


def dominates(p: np.ndarray, q: np.ndarray) -> bool:
    """True if vector p dominates vector q (minimization sense)."""
    return bool(np.all(p <= q) and np.any(p < q))


def non_dominated_sort(points: np.ndarray) -> List[List[int]]:
    """
    Fast non-dominated sorting (Deb et al. 2002).
    Returns list of fronts, where fronts[0] is the non-dominated Pareto front.
    """
    n = len(points)
    domination_counts = np.zeros(n, dtype=int)
    dominated_sets = [[] for _ in range(n)]
    fronts = [[]]

    for i in range(n):
        for j in range(i + 1, n):
            if dominates(points[i], points[j]):
                dominated_sets[i].append(j)
                domination_counts[j] += 1
            elif dominates(points[j], points[i]):
                dominated_sets[j].append(i)
                domination_counts[i] += 1

        if domination_counts[i] == 0:
            fronts[0].append(i)

    curr_idx = 0
    while len(fronts[curr_idx]) > 0:
        next_front = []
        for i in fronts[curr_idx]:
            for j in dominated_sets[i]:
                domination_counts[j] -= 1
                if domination_counts[j] == 0:
                    next_front.append(j)
        curr_idx += 1
        fronts.append(next_front)

    if not fronts[-1]:
        fronts.pop()
    return fronts


def compute_hypervolume_2d(front_2d: np.ndarray, ref_point: np.ndarray) -> float:
    """
    Exact Hypervolume calculation for 2D objective vectors.
    front_2d: (N, 2) array of non-dominated objective points (to minimize).
    ref_point: 2D upper bounding reference point.
    """
    if len(front_2d) == 0:
        return 0.0

    # Sort by first objective ascending
    sorted_idx = np.argsort(front_2d[:, 0])
    pts = front_2d[sorted_idx]

    # Filter points strictly dominated by ref_point
    valid = (pts[:, 0] <= ref_point[0]) & (pts[:, 1] <= ref_point[1])
    pts = pts[valid]
    if len(pts) == 0:
        return 0.0

    hv = 0.0
    current_y = ref_point[1]

    for i in range(len(pts)):
        width = ref_point[0] - pts[i, 0]
        height = max(0.0, current_y - pts[i, 1])
        hv += width * height
        current_y = min(current_y, pts[i, 1])

    return float(hv)


def compute_generational_distance(front: np.ndarray, reference_front: np.ndarray) -> float:
    """Generational Distance (GD) measuring convergence to reference front."""
    if len(front) == 0 or len(reference_front) == 0:
        return float("nan")
    dists = []
    for p in front:
        d = np.min(np.linalg.norm(reference_front - p, axis=1))
        dists.append(d ** 2)
    return float(np.sqrt(np.mean(dists)))


def compute_inverted_generational_distance(front: np.ndarray, reference_front: np.ndarray) -> float:
    """Inverted Generational Distance (IGD) measuring diversity and convergence."""
    if len(front) == 0 or len(reference_front) == 0:
        return float("nan")
    dists = []
    for r in reference_front:
        d = np.min(np.linalg.norm(front - r, axis=1))
        dists.append(d)
    return float(np.mean(dists))


def compute_spacing_metric(front: np.ndarray) -> float:
    """Spacing metric (S) measuring uniformity of Pareto solution distribution."""
    if len(front) <= 1:
        return 0.0
    dists = []
    for i in range(len(front)):
        d_min = float("inf")
        for j in range(len(front)):
            if i != j:
                d = np.sum(np.abs(front[i] - front[j]))
                if d < d_min:
                    d_min = d
        dists.append(d_min)
    d_mean = np.mean(dists)
    return float(np.sqrt(np.sum((dists - d_mean) ** 2) / (len(front) - 1)))


def select_compromise_presets(
    front_solutions: List[Dict[str, Any]],
    norm_scales: Optional[np.ndarray] = None,
) -> Dict[str, Dict[str, Any]]:
    """
    Select operational compromise policies from a Pareto front:
    - fuel_priority: Solution with lowest fuel consumption
    - cost_priority: Solution with lowest total OPEX
    - green_priority: Solution with lowest Well-to-Wake GHG emissions
    - balanced_decision: Knee point (closest to ideal in normalized objective space)
    """
    if not front_solutions:
        return {}

    fuel_vals = [s["total_fuel_tonnes"] for s in front_solutions]
    cost_vals = [s["total_opex_usd"] for s in front_solutions]
    ghg_vals = [s["total_wtw_ghg_tonnes"] for s in front_solutions]

    # Extreme Presets
    idx_fuel = int(np.argmin(fuel_vals))
    idx_cost = int(np.argmin(cost_vals))
    idx_green = int(np.argmin(ghg_vals))

    # Balanced Decision (Knee Point)
    scales = norm_scales if norm_scales is not None else np.array([50.0, 50000.0, 150.0])
    norm_pts = np.array([
        [s["total_fuel_tonnes"], s["total_opex_usd"], s["total_wtw_ghg_tonnes"]]
        for s in front_solutions
    ]) / scales[:3]

    ideal_point = np.min(norm_pts, axis=0)
    dists_to_ideal = np.linalg.norm(norm_pts - ideal_point, axis=1)
    idx_balanced = int(np.argmin(dists_to_ideal))

    return {
        "fuel_priority": front_solutions[idx_fuel],
        "cost_priority": front_solutions[idx_cost],
        "green_priority": front_solutions[idx_green],
        "balanced_decision": front_solutions[idx_balanced],
    }
