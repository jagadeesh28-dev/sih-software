"""
Multi-objective benchmark metrics: Hypervolume (HV) and Inverted Generational Distance (IGD).
"""

from typing import Optional
import numpy as np
from pymoo.indicators.hv import HV
from pymoo.indicators.igd import IGD


def compute_hypervolume(
    pareto_front: np.ndarray,
    reference_point: np.ndarray,
) -> float:
    """
    Compute Hypervolume indicator.
    Higher is better.
    """
    if len(pareto_front) == 0:
        return 0.0
    hv_calc = HV(ref_point=reference_point)
    return float(hv_calc(pareto_front))


def compute_igd(
    approx_front: np.ndarray,
    true_front: np.ndarray,
) -> float:
    """
    Compute Inverted Generational Distance (IGD).
    Lower is better.
    """
    if len(approx_front) == 0 or len(true_front) == 0:
        return float("inf")
    igd_calc = IGD(true_front)
    return float(igd_calc(approx_front))
