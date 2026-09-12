"""
Quantum-Inspired Multi-Objective Evolutionary Algorithm based on Decomposition (Q-MOEA/D).
Decomposes the 3-objective problem into scalar subproblems solved via QPSO operators.
"""

from typing import Any, Dict, List, Optional
import numpy as np
from pymoo.util.ref_dirs import get_reference_directions
from .qpso import QPSOOptimizer


class QMOEADOptimizer:
    """Multi-objective QPSO using subproblem decomposition weights."""

    def __init__(
        self,
        n_subproblems: int = 20,
        iterations_per_subproblem: int = 50,
        seed: int = 42,
    ):
        self.n_subproblems = n_subproblems
        self.iterations_per_subproblem = iterations_per_subproblem
        self.seed = seed

    def optimize(self, problem) -> Dict[str, Any]:
        """Execute Q-MOEA/D across decomposition weight vectors."""
        ref_dirs = get_reference_directions("das-dennis", problem.n_obj, n_partitions=4)
        pareto_X = []
        pareto_F = []
        total_evals = 0

        for i, weight in enumerate(ref_dirs):
            qpso = QPSOOptimizer(
                n_particles=20,
                max_iterations=self.iterations_per_subproblem,
                seed=self.seed + i,
            )
            res = qpso.optimize(problem, weight_vector=weight)
            pareto_X.append(res["best_x"])
            pareto_F.append(res["best_objectives"])
            total_evals += res["total_evaluations"]

        return {
            "algorithm": "Q-MOEA/D",
            "seed": self.seed,
            "pareto_X": np.array(pareto_X),
            "pareto_F": np.array(pareto_F),
            "total_evaluations": total_evals,
        }
