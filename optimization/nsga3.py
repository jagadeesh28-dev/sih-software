"""
NSGA-III Optimizer wrapper using pymoo.
Uses reference directions for structured multi-objective Pareto front approximation.
"""

from typing import Any, Dict, Optional
import numpy as np
from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.util.ref_dirs import get_reference_directions
from pymoo.optimize import minimize


class NSGA3Optimizer:
    """Wrapper around pymoo NSGA-III algorithm for equal-budget benchmarking."""

    def __init__(
        self,
        n_partitions: int = 12,
        pop_size: int = 100,
        n_gen: int = 500,
        seed: int = 42,
    ):
        self.n_partitions = n_partitions
        self.pop_size = pop_size
        self.n_gen = n_gen
        self.seed = seed

    def optimize(self, problem) -> Dict[str, Any]:
        """Execute NSGA-III optimization."""
        ref_dirs = get_reference_directions("das-dennis", problem.n_obj, n_partitions=self.n_partitions)
        algorithm = NSGA3(
            ref_dirs=ref_dirs,
            pop_size=len(ref_dirs),
            eliminate_duplicates=True,
        )

        res = minimize(
            problem,
            algorithm,
            ("n_gen", self.n_gen),
            seed=self.seed,
            verbose=False,
        )

        return {
            "algorithm": "NSGA-III",
            "seed": self.seed,
            "pareto_X": res.X,
            "pareto_F": res.F,
            "total_evaluations": algorithm.evaluator.n_eval,
            "runtime_seconds": res.exec_time,
        }
