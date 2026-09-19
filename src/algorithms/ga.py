"""
Classical Baseline: Genetic Algorithm (GA).
Matches Phase 4 GA implementation (tournament selection, simulated binary crossover SBX, polynomial mutation).
"""

import time
from typing import Any, Dict, List, Optional
import numpy as np

from src.algorithms.base import BaseFleetOptimizer, OptimizationResult
from src.evaluator.common_evaluator import CommonFleetEvaluator, EvaluationOutput


class GeneticAlgorithmOptimizer(BaseFleetOptimizer):
    """Genetic Algorithm Baseline."""

    def __init__(
        self,
        seed: int = 42,
        population_size: int = 50,
        max_generations: int = 50,
        crossover_rate: float = 0.9,
        mutation_rate: float = 0.1,
        eta_c: float = 15.0,
        eta_m: float = 20.0,
    ):
        super().__init__(name="GA", seed=seed)
        self.population_size = population_size
        self.max_generations = max_generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.eta_c = eta_c
        self.eta_m = eta_m

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

        # 2. Generational loop
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

            # Selection via 2-tournament
            selected = np.zeros_like(pop)
            for i in range(self.population_size):
                i1, i2 = rng.integers(0, self.population_size, size=2)
                winner = i1 if fitness[i1] < fitness[i2] else i2
                selected[i] = pop[winner].copy()

            # SBX Crossover & Polynomial Mutation
            next_pop = np.zeros_like(pop)
            for i in range(0, self.population_size, 2):
                p1 = selected[i]
                p2 = selected[(i + 1) % self.population_size]
                c1, c2 = p1.copy(), p2.copy()

                if rng.uniform(0.0, 1.0) < self.crossover_rate:
                    # SBX
                    for d in range(dim):
                        if rng.uniform(0.0, 1.0) <= 0.5:
                            if abs(p1[d] - p2[d]) > 1e-9:
                                y1 = min(p1[d], p2[d])
                                y2 = max(p1[d], p2[d])
                                rand_val = rng.uniform(0.0, 1.0)
                                beta = 1.0 + (2.0 * (y1 - xl[d]) / (y2 - y1))
                                alpha = 2.0 - beta ** -(self.eta_c + 1.0)
                                if rand_val <= (1.0 / alpha):
                                    beta_q = (rand_val * alpha) ** (1.0 / (self.eta_c + 1.0))
                                else:
                                    beta_q = (1.0 / (2.0 - rand_val * alpha)) ** (1.0 / (self.eta_c + 1.0))
                                c1[d] = 0.5 * ((y1 + y2) - beta_q * (y2 - y1))
                                beta = 1.0 + (2.0 * (xu[d] - y2) / (y2 - y1))
                                alpha = 2.0 - beta ** -(self.eta_c + 1.0)
                                if rand_val <= (1.0 / alpha):
                                    beta_q = (rand_val * alpha) ** (1.0 / (self.eta_c + 1.0))
                                else:
                                    beta_q = (1.0 / (2.0 - rand_val * alpha)) ** (1.0 / (self.eta_c + 1.0))
                                c2[d] = 0.5 * ((y1 + y2) + beta_q * (y2 - y1))

                # Polynomial mutation
                for child in [c1, c2]:
                    for d in range(dim):
                        if rng.uniform(0.0, 1.0) < self.mutation_rate:
                            y = child[d]
                            delta_1 = (y - xl[d]) / (xu[d] - xl[d])
                            delta_2 = (xu[d] - y) / (xu[d] - xl[d])
                            rand_m = rng.uniform(0.0, 1.0)
                            mut_pow = 1.0 / (self.eta_m + 1.0)
                            if rand_m < 0.5:
                                xy = 1.0 - delta_1
                                val = 2.0 * rand_m + (1.0 - 2.0 * rand_m) * (xy ** (self.eta_m + 1.0))
                                delta_q = val ** mut_pow - 1.0
                            else:
                                xy = 1.0 - delta_2
                                val = 2.0 * (1.0 - rand_m) + 2.0 * (rand_m - 0.5) * (xy ** (self.eta_m + 1.0))
                                delta_q = 1.0 - val ** mut_pow
                            child[d] = np.clip(y + delta_q * (xu[d] - xl[d]), xl[d], xu[d])

                next_pop[i] = c1
                if i + 1 < self.population_size:
                    next_pop[i + 1] = c2

            pop = next_pop
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
                        first_feas_iter = gen + 1

                if out.fitness < best_score:
                    best_score = out.fitness
                    best_x = pop[i].copy()
                    best_output = out

            convergence_traj.append(best_score)
            eval_traj.append(evaluator.evaluation_count)
            gen += 1

        t1 = time.perf_counter()

        return OptimizationResult(
            algorithm="GA",
            seed=self.seed,
            run_id=f"GA_seed_{self.seed}",
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
