"""
Empirical Conditional Value-at-Risk (CVaR) for voyage schedule delay.
Section 17: Evaluates Z(omega) = max(0, T_actual(omega) - deadline) across common scenarios.
"""

from typing import Dict, List
import numpy as np


def compute_schedule_delay_cvar(
    transit_times_hours: np.ndarray,
    deadline_hours: float,
    alpha: float = 0.95,
) -> Dict[str, float]:
    """
    Compute empirical VaR and CVaR for transit schedule delays.

    Inputs:
        transit_times_hours: 1D array of simulated transit times across scenarios (hours)
        deadline_hours: Target contractual delivery window (hours)
        alpha: Confidence level (default 0.95)

    Returns:
        Dict containing:
            mean_delay_hours: Average delay over all scenarios
            var_alpha_hours: Value at Risk at level alpha
            cvar_alpha_hours: Conditional Value at Risk at level alpha (expected shortfall)
            prob_delay: Empirical probability of deadline breach P(delay > 0)
    """
    delays = np.maximum(0.0, transit_times_hours - deadline_hours)

    prob_delay = float(np.mean(delays > 0.0))
    mean_delay = float(np.mean(delays))

    # Empirical VaR at level alpha
    var_alpha = float(np.percentile(delays, alpha * 100.0))

    # Tail condition: scenarios exceeding or equal to VaR
    tail_delays = delays[delays >= var_alpha]
    if len(tail_delays) > 0:
        cvar_alpha = float(np.mean(tail_delays))
    else:
        cvar_alpha = var_alpha

    return {
        "mean_delay_hours": mean_delay,
        "var_alpha_hours": var_alpha,
        "cvar_alpha_hours": cvar_alpha,
        "probability_of_delay": prob_delay,
    }
