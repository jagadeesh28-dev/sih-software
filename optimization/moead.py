"""
MOEA/D Optimizer wrapper using pymoo.
Multi-Objective Evolutionary Algorithm based on Decomposition.
"""

from typing import Any, Dict, Optional
import numpy as np
from pymoo.algorithms.moo.moead import MOEAD
from pymoo.util.ref_dirs import get_reference_directions
from pymoo.optimize import minimize


class MOEADOptimizer:
    """Wrapper around pymoo MOEA/D algorithm for equal-budget benchmarking."""

    def __init__(
        self,
        n_partitions: int = 12,
        n_neighbors: int = 15,
        n_gen: int = 500,
        seed: int = 42,
    ):
        self.n_partitions = n_partitions
        self.n_neighbors = n_neighbors
        self.n_gen = n_gen
        self.seed = seed

    def optimize(self, problem) -> Dict[str, Any]:
        """Execute MOEA/D optimization."""
        ref_dirs = get_reference_directions("das-dennis", problem.n_obj, n_partitions=self.n_partitions)
        algorithm = MOEAD(
            ref_dirs=ref_dirs,
            n_neighbors=self.n_neighbors,
            prob_neighbor_mating=0.9,
        )

        res = minimize(
            problem,
            algorithm,
            ("n_gen", self.n_gen),
            seed=self.seed,
            verbose=False,
        )

        return {
            "algorithm": "MOEA/D",
            "seed": self.seed,
            "pareto_X": res.X,
            "pareto_F": res.F,
            "total_evaluations": algorithm.evaluator.n_eval,
            "runtime_seconds": res.exec_time,
        }
