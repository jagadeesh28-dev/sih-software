"""
Classical Baseline: Differential Evolution (DE/rand/1/bin).
Wrapped to conform to BaseFleetOptimizer interface.
Matches Phase 4 DE implementation exactly.
"""

import time
from typing import Any, Dict, List, Optional
import numpy as np

from src.algorithms.base import BaseFleetOptimizer, OptimizationResult
from src.evaluator.common_evaluator import CommonFleetEvaluator, EvaluationOutput


class DEOptimizer(BaseFleetOptimizer):
    """Differential Evolution (DE/rand/1/bin) Baseline."""

    def __init__(
        self,
        seed: int = 42,
        population_size: int = 50,
        max_generations: int = 50,
        f_mut: float = 0.8,
        cr: float = 0.9,
    ):
        super().__init__(name="DE", seed=seed)
        self.population_size = population_size
        self.max_generations = max_generations
        self.f_mut = f_mut
        self.cr = cr

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
        eval_cap = budget

        # 1. Initialize population
        pop = rng.uniform(xl, xu, size=(self.population_size, dim))
        fitness = np.zeros(self.population_size)
        pop_outputs: List[Optional[EvaluationOutput]] = [None] * self.population_size

        first_feas_eval = -1
        first_feas_iter = -1
        feas_count = 0
        convergence_traj: List[float] = []
        eval_traj: List[int] = []
        diversity_traj: List[float] = []
        entropy_traj: List[float] = []
        unique_solutions: set = set()

        for i in range(self.population_size):
            if evaluator.evaluation_count >= eval_cap:
                break
            out = evaluator.evaluate(pop[i])
            fitness[i] = out.fitness
            pop_outputs[i] = out
            unique_solutions.add(tuple(np.round(pop[i], 3)))

            if out.is_feasible:
                feas_count += 1
                if first_feas_eval == -1:
                    first_feas_eval = out.evaluation_index
                    first_feas_iter = 0

        best_idx = int(np.argmin(fitness))
        best_x = pop[best_idx].copy()
        best_score = float(fitness[best_idx])
        best_output = pop_outputs[best_idx]

        convergence_traj.append(best_score)
        eval_traj.append(evaluator.evaluation_count)

        # 2. Generational mutation-crossover loop
        gen = 0
        while gen < self.max_generations and evaluator.evaluation_count < eval_cap:
            diversity_traj.append(float(np.mean(np.std(pop, axis=0))))
            cat_dims = [0, 3, 4, 6, 9, 10, 12, 15, 16]
            cat_vals = np.round(pop[:, cat_dims]).astype(int)
            entropies = []
            for col in range(len(cat_dims)):
                _, counts = np.unique(cat_vals[:, col], return_counts=True)
                p_c = counts / np.sum(counts)
                entropies.append(-float(np.sum(p_c * np.log2(p_c + 1e-12))))
            entropy_traj.append(float(np.mean(entropies)))

            for i in range(self.population_size):
                if evaluator.evaluation_count >= eval_cap:
                    break

                candidates = [idx for idx in range(self.population_size) if idx != i]
                r1, r2, r3 = rng.choice(candidates, size=3, replace=False)

                # Mutation
                v = pop[r1] + self.f_mut * (pop[r2] - pop[r3])
                v = np.clip(v, xl, xu)

                # Binomial Crossover
                j_rand = rng.integers(0, dim)
                u = pop[i].copy()
                for d in range(dim):
                    if rng.uniform(0.0, 1.0) <= self.cr or d == j_rand:
                        u[d] = v[d]

                out_u = evaluator.evaluate(u)
                score_u = out_u.fitness
                unique_solutions.add(tuple(np.round(u, 3)))

                if out_u.is_feasible:
                    feas_count += 1
                    if first_feas_eval == -1:
                        first_feas_eval = out_u.evaluation_index
                        first_feas_iter = gen + 1

                # Greedy selection
                if score_u < fitness[i]:
                    pop[i] = u.copy()
                    fitness[i] = score_u
                    pop_outputs[i] = out_u

                    if score_u < best_score:
                        best_x = u.copy()
                        best_score = score_u
                        best_output = out_u

            convergence_traj.append(best_score)
            eval_traj.append(evaluator.evaluation_count)
            gen += 1

        t1 = time.perf_counter()

        return OptimizationResult(
            algorithm="DE",
            seed=self.seed,
            run_id=f"DE_seed_{self.seed}",
            runtime_seconds=round(t1 - t0, 4),
            objective_evaluations=evaluator.evaluation_count,
            iterations=gen,
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
            population_diversity=diversity_traj,
            categorical_entropy=entropy_traj,
            repair_count=0,
            repair_rate=0.0,
            unique_solution_count=len(unique_solutions),
            assigned_demands=dict(best_output.assigned_demands) if best_output else {},
            fuel_decisions=dict(best_output.fuel_decisions) if best_output else {},
            speed_decisions=dict(best_output.speed_decisions) if best_output else {},
        )
