"""
Classical Baseline: Unguided Uniform Random Search.
Matches Phase 4 Random Search baseline.
Crucially reports BOTH:
1. Candidate-level feasibility rate (fraction of all evaluated candidates that are feasible)
2. Run-level success (whether the run found at least one feasible candidate)
"""

import time
from typing import Any, Dict, List, Optional
import numpy as np

from src.algorithms.base import BaseFleetOptimizer, OptimizationResult
from src.evaluator.common_evaluator import CommonFleetEvaluator, EvaluationOutput


class RandomSearchOptimizer(BaseFleetOptimizer):
    """Unguided Uniform Random Search Baseline."""

    def __init__(self, seed: int = 42):
        super().__init__(name="Random", seed=seed)

    def optimize(
        self,
        evaluator: CommonFleetEvaluator,
        xl: np.ndarray,
        xu: np.ndarray,
        budget: int = 2500,
    ) -> OptimizationResult:
        t0 = time.perf_counter()
        rng = np.random.default_rng(self.seed)
        np.random.seed(self.seed)

        dim = len(xl)
        best_score = np.inf
        best_x = np.zeros(dim)
        best_output: Optional[EvaluationOutput] = None

        first_feas_eval = -1
        first_feas_iter = -1
        feas_count = 0
        convergence_traj: List[float] = []
        eval_traj: List[int] = []
        unique_solutions: set = set()

        for idx in range(budget):
            if evaluator.evaluation_count >= budget:
                break

            x = rng.uniform(xl, xu)
            out = evaluator.evaluate(x)
            unique_solutions.add(tuple(np.round(x, 3)))

            if out.is_feasible:
                feas_count += 1
                if first_feas_eval == -1:
                    first_feas_eval = out.evaluation_index
                    first_feas_iter = idx + 1

            if out.fitness < best_score:
                best_score = out.fitness
                best_x = x.copy()
                best_output = out

            if (idx + 1) % 50 == 0 or idx == budget - 1:
                convergence_traj.append(best_score)
                eval_traj.append(evaluator.evaluation_count)

        t1 = time.perf_counter()

        return OptimizationResult(
            algorithm="Random",
            seed=self.seed,
            run_id=f"Random_seed_{self.seed}",
            runtime_seconds=round(t1 - t0, 4),
            objective_evaluations=evaluator.evaluation_count,
            iterations=budget,
            best_x=best_x,
            best_fitness=float(best_score),
            best_physical_objective=float(best_output.physical_fitness) if best_output else float(best_score),
            best_penalty=float(best_output.penalty) if best_output else 0.0,
            feasible_at_end=bool(best_output.is_feasible) if best_output else False,
            best_output=best_output,
            first_feasible_evaluation=first_feas_eval,
            first_feasible_iteration=first_feas_iter,
            number_of_feasible_evaluations=feas_count,
            candidate_level_feasibility_rate=float(feas_count / max(1, evaluator.evaluation_count)),
            constraint_violation_total=float(best_output.total_constraint_violation) if best_output else 0.0,
            hard_violations=list(best_output.hard_violations) if best_output else [],
            convergence_trajectory=convergence_traj,
            eval_trajectory=eval_traj,
            population_diversity=[],
            categorical_entropy=[],
            repair_count=0,
            repair_rate=0.0,
            unique_solution_count=len(unique_solutions),
            assigned_demands=dict(best_output.assigned_demands) if best_output else {},
            fuel_decisions=dict(best_output.fuel_decisions) if best_output else {},
            speed_decisions=dict(best_output.speed_decisions) if best_output else {},
        )
