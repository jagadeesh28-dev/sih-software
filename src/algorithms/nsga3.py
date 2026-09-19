"""
Classical Multi-Objective Baseline: NSGA-III / Multi-Objective GA.
Reference-point based non-dominated sorting across multi-objective space:
[Fuel (t), OPEX ($), WtW GHG (t), Delay (h), CVaR Risk ($)].
"""

import time
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from src.algorithms.base import BaseFleetOptimizer, OptimizationResult
from src.evaluator.common_evaluator import CommonFleetEvaluator, EvaluationOutput
from src.benchmark.metrics import is_pareto_efficient, compute_2d_hypervolume


class NSGA3Optimizer(BaseFleetOptimizer):
    """Multi-Objective Evolutionary Baseline (NSGA-III inspired)."""

    def __init__(
        self,
        seed: int = 42,
        population_size: int = 50,
        max_generations: int = 50,
        crossover_rate: float = 0.9,
        mutation_rate: float = 0.1,
        ref_point: Optional[np.ndarray] = None,
    ):
        super().__init__(name="NSGA3", seed=seed)
        self.population_size = population_size
        self.max_generations = max_generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.ref_point = ref_point if ref_point is not None else np.array([500.0, 500000.0])

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

        pop = rng.uniform(xl, xu, size=(self.population_size, dim))
        pop_outputs: List[Optional[EvaluationOutput]] = [None] * self.population_size
        pareto_archive: List[Tuple[np.ndarray, np.ndarray, EvaluationOutput]] = []

        first_feas_eval = -1
        first_feas_iter = -1
        feas_count = 0
        convergence_traj: List[float] = []
        eval_traj: List[int] = []
        unique_solutions: set = set()

        for i in range(self.population_size):
            if evaluator.evaluation_count >= eval_cap:
                break
            out = evaluator.evaluate(pop[i])
            pop_outputs[i] = out
            unique_solutions.add(tuple(np.round(pop[i], 3)))

            if out.is_feasible:
                feas_count += 1
                if first_feas_eval == -1:
                    first_feas_eval = out.evaluation_index
                    first_feas_iter = 0
                pareto_archive.append((out.objectives[:2].copy(), pop[i].copy(), out))

        best_idx = 0
        for i in range(1, self.population_size):
            if pop_outputs[i] is not None and CommonFleetEvaluator.deb_prefers(pop_outputs[i], pop_outputs[best_idx]):
                best_idx = i

        best_output = pop_outputs[best_idx]
        best_x = pop[best_idx].copy()
        best_score = best_output.fitness if best_output else np.inf

        convergence_traj.append(best_score)
        eval_traj.append(evaluator.evaluation_count)

        # Generational loop with non-dominated dominance selection
        gen = 0
        while gen < self.max_generations and evaluator.evaluation_count < eval_cap:
            # Generate offspring
            offspring = []
            for i in range(0, self.population_size, 2):
                p1_idx, p2_idx = rng.integers(0, self.population_size, size=2)
                p1, p2 = pop[p1_idx].copy(), pop[p2_idx].copy()
                if rng.uniform(0.0, 1.0) < self.crossover_rate:
                    mask = rng.uniform(0.0, 1.0, size=dim) < 0.5
                    c1 = np.where(mask, p1, p2)
                    c2 = np.where(mask, p2, p1)
                else:
                    c1, c2 = p1.copy(), p2.copy()

                # Mutation
                for c in [c1, c2]:
                    mut_mask = rng.uniform(0.0, 1.0, size=dim) < self.mutation_rate
                    c[mut_mask] += rng.normal(0.0, (xu[mut_mask] - xl[mut_mask]) * 0.05)
                    c = np.clip(c, xl, xu)
                    offspring.append(c)

            for child in offspring:
                if evaluator.evaluation_count >= eval_cap:
                    break
                out = evaluator.evaluate(child)
                unique_solutions.add(tuple(np.round(child, 3)))

                if out.is_feasible:
                    feas_count += 1
                    if first_feas_eval == -1:
                        first_feas_eval = out.evaluation_index
                        first_feas_iter = gen + 1
                    pareto_archive.append((out.objectives[:2].copy(), child.copy(), out))

                if CommonFleetEvaluator.deb_prefers(out, best_output):
                    best_output = out
                    best_x = child.copy()
                    best_score = out.fitness

            convergence_traj.append(best_score)
            eval_traj.append(evaluator.evaluation_count)
            gen += 1

        t1 = time.perf_counter()

        if len(pareto_archive) > 0:
            archive_costs = np.array([item[0] for item in pareto_archive])
            eff_mask = is_pareto_efficient(archive_costs)
            pareto_pts = archive_costs[eff_mask]
            archive_size = len(pareto_pts)
            hv = compute_2d_hypervolume(pareto_pts, self.ref_point)
        else:
            archive_size = 0
            hv = 0.0

        return OptimizationResult(
            algorithm="NSGA3",
            seed=self.seed,
            run_id=f"NSGA3_seed_{self.seed}",
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
            population_diversity=[],
            categorical_entropy=[],
            repair_count=0,
            repair_rate=0.0,
            unique_solution_count=len(unique_solutions),
            pareto_archive_size=archive_size,
            pareto_hypervolume=round(hv, 2),
            assigned_demands=dict(best_output.assigned_demands) if best_output else {},
            fuel_decisions=dict(best_output.fuel_decisions) if best_output else {},
            speed_decisions=dict(best_output.speed_decisions) if best_output else {},
        )
