"""
A3: QPSO + Discrete Update Operators + Diversity Preservation.
Applies principled discrete operators to discrete/categorical variables:
- Continuous variables (speed, cargo) update via quantum delta-well dynamics
- Discrete categorical variables (demand, fuel, mode) update via stochastic crossover
  with pbest and gbest, plus uniform mutation to prevent plateau stagnation
- Binary variables (shore power) update via sigmoid/logistic probabilistic mapping
- Standard scalar fitness comparison (NO Deb rules, NO QIEA Q-bits)
- Measures categorical entropy, unique solutions, and diversity
"""

import time
from typing import Any, Dict, List, Optional
import numpy as np

from src.algorithms.base import BaseFleetOptimizer, OptimizationResult
from src.evaluator.common_evaluator import CommonFleetEvaluator, EvaluationOutput
from src.representation.variable_types import get_heterogeneous_fleet_partitions, VariableType


class DiscreteQPSOOptimizer(BaseFleetOptimizer):
    """A3: Hybrid Continuous-Discrete QPSO with Diversity Preservation."""

    def __init__(
        self,
        seed: int = 42,
        n_particles: int = 50,
        max_iterations: int = 50,
        beta_start: float = 1.0,
        beta_end: float = 0.5,
        p_crossover: float = 0.7,
        p_mutation: float = 0.1,
    ):
        super().__init__(name="A3_Discrete_QPSO", seed=seed)
        self.n_particles = n_particles
        self.max_iterations = max_iterations
        self.beta_start = beta_start
        self.beta_end = beta_end
        self.p_crossover = p_crossover
        self.p_mutation = p_mutation
        self.partitions = get_heterogeneous_fleet_partitions(n_vessels=3)

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

        continuous_dims = [p.index for p in self.partitions if p.var_type == VariableType.CONTINUOUS]
        discrete_dims = [p.index for p in self.partitions if p.var_type in (VariableType.CATEGORICAL, VariableType.INTEGER)]
        binary_dims = [p.index for p in self.partitions if p.var_type == VariableType.BINARY]

        # 1. Initialize swarm
        X = rng.uniform(xl, xu, size=(self.n_particles, dim))
        # Discretize initial categorical and binary dimensions
        for d in discrete_dims:
            X[:, d] = np.round(X[:, d])
        for d in binary_dims:
            X[:, d] = np.where(X[:, d] >= 0.5, 1.0, 0.0)

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
            beta = self.beta_start - (self.beta_start - self.beta_end) * (t / max(1, self.max_iterations))
            mbest = np.mean(P, axis=0)

            # Diagnostics
            diversity_traj.append(float(np.mean(np.std(X, axis=0))))
            cat_vals = np.round(X[:, discrete_dims]).astype(int)
            entropies = []
            for col in range(len(discrete_dims)):
                _, counts = np.unique(cat_vals[:, col], return_counts=True)
                p_c = counts / np.sum(counts)
                entropies.append(-float(np.sum(p_c * np.log2(p_c + 1e-12))))
            entropy_traj.append(float(np.mean(entropies)))

            for i in range(self.n_particles):
                if evaluator.evaluation_count >= eval_cap:
                    break

                # --- 2A. Continuous Update (Speed & Cargo) ---
                for d in continuous_dims:
                    phi = rng.uniform(0.0, 1.0)
                    p_local = phi * P[i, d] + (1.0 - phi) * gbest[d]
                    u = max(1e-10, rng.uniform(0.0, 1.0))
                    sign = 1.0 if rng.uniform(0.0, 1.0) > 0.5 else -1.0
                    X[i, d] = p_local + sign * beta * abs(mbest[d] - X[i, d]) * np.log(1.0 / u)
                    X[i, d] = np.clip(X[i, d], xl[d], xu[d])

                # --- 2B. Discrete Categorical Update (Demand, Fuel, Mode) ---
                for d in discrete_dims:
                    r_op = rng.uniform(0.0, 1.0)
                    if r_op < 0.40:
                        # Inherit from personal best
                        X[i, d] = P[i, d]
                    elif r_op < 0.80:
                        # Inherit from global best
                        X[i, d] = gbest[d]
                    elif r_op < 0.80 + self.p_mutation:
                        # Random exploration within bounds
                        X[i, d] = float(rng.integers(int(xl[d]), int(xu[d]) + 1))
                    else:
                        # Keep current
                        pass

                # --- 2C. Binary Update (Shore Power) ---
                for d in binary_dims:
                    r_b = rng.uniform(0.0, 1.0)
                    if r_b < 0.50:
                        X[i, d] = gbest[d]
                    elif r_b < 0.85:
                        X[i, d] = P[i, d]
                    else:
                        X[i, d] = 1.0 - X[i, d]  # Bit-flip mutation

                out = evaluator.evaluate(X[i])
                score = out.fitness
                unique_solutions.add(tuple(np.round(X[i], 3)))

                if out.is_feasible:
                    feas_count += 1
                    if first_feas_eval == -1:
                        first_feas_eval = out.evaluation_index
                        first_feas_iter = t + 1

                # Standard scalar fitness comparison
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
            algorithm="A3_Discrete_QPSO",
            seed=self.seed,
            run_id=f"A3_seed_{self.seed}",
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
