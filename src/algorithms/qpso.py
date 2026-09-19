"""
A0: Plain Quantum-Behaved Particle Swarm Optimization (QPSO).
Reproduces the Phase 4 QPSO baseline verbatim:
- Continuous delta-potential well dynamics (Sun et al. 2004)
- Scalar penalized fitness comparison
- Naive float rounding for categorical variables
- No repair, no Deb rules, no discrete operators
"""

import time
from typing import Any, Dict, List, Optional
import numpy as np

from src.algorithms.base import BaseFleetOptimizer, OptimizationResult
from src.evaluator.common_evaluator import CommonFleetEvaluator, EvaluationOutput


class PlainQPSOOptimizer(BaseFleetOptimizer):
    """A0: Verbatim Phase 4 QPSO implementation."""

    def __init__(
        self,
        seed: int = 42,
        n_particles: int = 50,
        max_iterations: int = 50,
        beta_start: float = 1.0,
        beta_end: float = 0.5,
    ):
        super().__init__(name="A0_Plain_QPSO", seed=seed)
        self.n_particles = n_particles
        self.max_iterations = max_iterations
        self.beta_start = beta_start
        self.beta_end = beta_end

    def optimize(
        self,
        evaluator: CommonFleetEvaluator,
        xl: np.ndarray,
        xu: np.ndarray,
        budget: int = 2500,
    ) -> OptimizationResult:
        t0 = time.perf_counter()
        np.random.seed(self.seed)

        dim = len(xl)
        eval_cap = budget

        # 1. Initialize swarm uniformly across bounded space
        X = np.random.uniform(xl, xu, size=(self.n_particles, dim))
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

        # 2. Main QPSO generation loop
        t = 0
        while t < self.max_iterations and evaluator.evaluation_count < eval_cap:
            beta = self.beta_start - (self.beta_start - self.beta_end) * (t / max(1, self.max_iterations))
            mbest = np.mean(P, axis=0)

            # Track population diversity & categorical entropy
            std_dim = np.std(X, axis=0)
            diversity_traj.append(float(np.mean(std_dim)))
            cat_dims = [0, 3, 4, 6, 9, 10, 12, 15, 16]
            cat_vals = np.round(X[:, cat_dims]).astype(int)
            # Categorical entropy
            entropies = []
            for col in range(len(cat_dims)):
                _, counts = np.unique(cat_vals[:, col], return_counts=True)
                p_c = counts / np.sum(counts)
                entropies.append(-float(np.sum(p_c * np.log2(p_c + 1e-12))))
            entropy_traj.append(float(np.mean(entropies)))

            for i in range(self.n_particles):
                if evaluator.evaluation_count >= eval_cap:
                    break

                phi = np.random.uniform(0.0, 1.0, size=dim)
                p_local = phi * P[i] + (1.0 - phi) * gbest
                u = np.random.uniform(0.0, 1.0, size=dim)
                sign = np.where(np.random.uniform(0.0, 1.0, size=dim) > 0.5, 1.0, -1.0)

                # QPSO quantum delta-potential update
                X[i] = p_local + sign * beta * np.abs(mbest - X[i]) * np.log(1.0 / np.maximum(u, 1e-10))
                X[i] = np.clip(X[i], xl, xu)

                out = evaluator.evaluate(X[i])
                score = out.fitness
                unique_solutions.add(tuple(np.round(X[i], 3)))

                if out.is_feasible:
                    feas_count += 1
                    if first_feas_eval == -1:
                        first_feas_eval = out.evaluation_index
                        first_feas_iter = t + 1

                # Standard scalar fitness comparison (vulnerable to penalty inversion)
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
            algorithm="A0_Plain_QPSO",
            seed=self.seed,
            run_id=f"A0_seed_{self.seed}",
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
