"""
Classical Baseline: Canonical Particle Swarm Optimization (PSO).
Matches Phase 4 PSO implementation (inertia weight + cognitive/social attraction).
"""

import time
from typing import Any, Dict, List, Optional
import numpy as np

from src.algorithms.base import BaseFleetOptimizer, OptimizationResult
from src.evaluator.common_evaluator import CommonFleetEvaluator, EvaluationOutput


class CanonicalPSOOptimizer(BaseFleetOptimizer):
    """Canonical Particle Swarm Optimization Baseline."""

    def __init__(
        self,
        seed: int = 42,
        n_particles: int = 50,
        max_iterations: int = 50,
        w: float = 0.7298,
        c1: float = 1.496,
        c2: float = 1.496,
    ):
        super().__init__(name="PSO", seed=seed)
        self.n_particles = n_particles
        self.max_iterations = max_iterations
        self.w = w
        self.c1 = c1
        self.c2 = c2

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

        # 1. Initialize swarm and velocities
        X = rng.uniform(xl, xu, size=(self.n_particles, dim))
        V = rng.uniform(-(xu - xl) * 0.1, (xu - xl) * 0.1, size=(self.n_particles, dim))
        P = X.copy()
        P_scores = np.full(self.n_particles, np.inf)
        P_outputs: List[Optional[EvaluationOutput]] = [None] * self.n_particles

        first_feas_eval = -1
        first_feas_iter = -1
        feas_count = 0
        convergence_traj: List[float] = []
        eval_traj: List[int] = []
        diversity_traj: List[float] = []
        entropy_traj: List[float] = []
        unique_solutions: set = set()

        for i in range(self.n_particles):
            if evaluator.evaluation_count >= eval_cap:
                break
            out = evaluator.evaluate(X[i])
            P_scores[i] = out.fitness
            P_outputs[i] = out
            unique_solutions.add(tuple(np.round(X[i], 3)))

            if out.is_feasible:
                feas_count += 1
                if first_feas_eval == -1:
                    first_feas_eval = out.evaluation_index
                    first_feas_iter = 0

        gbest_idx = int(np.argmin(P_scores))
        gbest = P[gbest_idx].copy()
        gbest_score = float(P_scores[gbest_idx])
        gbest_output = P_outputs[gbest_idx]

        convergence_traj.append(gbest_score)
        eval_traj.append(evaluator.evaluation_count)

        # 2. Main generation loop
        t = 0
        while t < self.max_iterations and evaluator.evaluation_count < eval_cap:
            diversity_traj.append(float(np.mean(np.std(X, axis=0))))
            cat_dims = [0, 3, 4, 6, 9, 10, 12, 15, 16]
            cat_vals = np.round(X[:, cat_dims]).astype(int)
            entropies = []
            for col in range(len(cat_dims)):
                _, counts = np.unique(cat_vals[:, col], return_counts=True)
                p_c = counts / np.sum(counts)
                entropies.append(-float(np.sum(p_c * np.log2(p_c + 1e-12))))
            entropy_traj.append(float(np.mean(entropies)))

            for i in range(self.n_particles):
                if evaluator.evaluation_count >= eval_cap:
                    break

                r1 = rng.uniform(0.0, 1.0, size=dim)
                r2 = rng.uniform(0.0, 1.0, size=dim)

                V[i] = self.w * V[i] + self.c1 * r1 * (P[i] - X[i]) + self.c2 * r2 * (gbest - X[i])
                X[i] = np.clip(X[i] + V[i], xl, xu)

                out = evaluator.evaluate(X[i])
                score = out.fitness
                unique_solutions.add(tuple(np.round(X[i], 3)))

                if out.is_feasible:
                    feas_count += 1
                    if first_feas_eval == -1:
                        first_feas_eval = out.evaluation_index
                        first_feas_iter = t + 1

                if score < P_scores[i]:
                    P[i] = X[i].copy()
                    P_scores[i] = score
                    P_outputs[i] = out

                    if score < gbest_score:
                        gbest = X[i].copy()
                        gbest_score = score
                        gbest_output = out

            convergence_traj.append(gbest_score)
            eval_traj.append(evaluator.evaluation_count)
            t += 1

        t1 = time.perf_counter()

        return OptimizationResult(
            algorithm="PSO",
            seed=self.seed,
            run_id=f"PSO_seed_{self.seed}",
            runtime_seconds=round(t1 - t0, 4),
            objective_evaluations=evaluator.evaluation_count,
            iterations=t,
            best_x=gbest,
            best_fitness=float(gbest_score),
            best_physical_objective=float(gbest_output.physical_fitness) if gbest_output else float(gbest_score),
            best_penalty=float(gbest_output.penalty) if gbest_output else 0.0,
            feasible_at_end=bool(gbest_output.is_feasible) if gbest_output else False,
            best_output=gbest_output,
            first_feasible_evaluation=first_feas_eval,
            first_feasible_iteration=first_feas_iter,
            number_of_feasible_evaluations=feas_count,
            candidate_level_feasibility_rate=float(feas_count / max(1, evaluator.evaluation_count)),
            constraint_violation_total=float(gbest_output.total_constraint_violation) if gbest_output else 0.0,
            hard_violations=list(gbest_output.hard_violations) if gbest_output else [],
            convergence_trajectory=convergence_traj,
            eval_trajectory=eval_traj,
            population_diversity=diversity_traj,
            categorical_entropy=entropy_traj,
            repair_count=0,
            repair_rate=0.0,
            unique_solution_count=len(unique_solutions),
            assigned_demands=dict(gbest_output.assigned_demands) if gbest_output else {},
            fuel_decisions=dict(gbest_output.fuel_decisions) if gbest_output else {},
            speed_decisions=dict(gbest_output.speed_decisions) if gbest_output else {},
        )
