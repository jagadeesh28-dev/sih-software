"""
Uniform Random Search Optimizer.
Unguided control baseline for evaluating metaheuristic search efficiency.
"""

from typing import Any, Callable, Dict, Optional
import numpy as np


class RandomSearchOptimizer:
    """
    Uniform Random Search baseline.
    Evaluates independently sampled random points within bounded continuous space [xl, xu].
    """

    def __init__(
        self,
        max_evaluations: int = 50000,
        seed: int = 42,
    ):
        self.max_evaluations = max_evaluations
        self.seed = seed

    def optimize(
        self,
        eval_fn: Callable[[np.ndarray], float],
        xl: np.ndarray,
        xu: np.ndarray,
        max_evaluations: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Execute Random Search on bounded space [xl, xu].
        """
        np.random.seed(self.seed)
        dim = len(xl)
        xl = np.asarray(xl, dtype=float)
        xu = np.asarray(xu, dtype=float)
        eval_cap = max_evaluations if max_evaluations is not None else self.max_evaluations

        best_score = float("inf")
        best_x = xl.copy()
        convergence_history = []

        for count in range(1, eval_cap + 1):
            sample = np.random.uniform(xl, xu, size=dim)
            score = float(eval_fn(sample))

            if score < best_score:
                best_score = score
                best_x = sample.copy()

            # Record history periodically (every 100 evaluations or at end)
            if count % 100 == 0 or count == eval_cap:
                convergence_history.append(float(best_score))

        return {
            "algorithm": "RandomSearch",
            "seed": self.seed,
            "best_x": best_x,
            "best_score": float(best_score),
            "total_evaluations": eval_cap,
            "convergence_history": convergence_history,
        }
