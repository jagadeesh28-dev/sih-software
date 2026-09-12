"""
Quantum-Behaved Particle Swarm Optimization (QPSO) Algorithm.
Classical metaheuristic based on quantum delta-potential well dynamics (Sun et al. 2004).
Section 13: Strictly classical execution. QPSO is allowed to lose in benchmarks.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np


class QPSOOptimizer:
    """
    Quantum-behaved Particle Swarm Optimization for multi-objective / aggregate problems.
    Equations:
      p_i,d = phi * pbest_i,d + (1 - phi) * gbest_d, phi ~ U(0,1)
      mbest_d = 1/M * sum(pbest_k,d)
      x_i,d(t+1) = p_i,d +/- beta(t) * |mbest_d - x_i,d| * ln(1/u), u ~ U(0,1)
    """

    def __init__(
        self,
        n_particles: int = 100,
        max_iterations: int = 500,
        beta_start: float = 1.0,
        beta_end: float = 0.5,
        seed: int = 42,
    ):
        self.n_particles = n_particles
        self.max_iterations = max_iterations
        self.beta_start = beta_start
        self.beta_end = beta_end
        self.seed = seed

    def optimize(
        self,
        problem,
        weight_vector: Optional[np.ndarray] = None,
    ) -> Dict[str, Any]:
        """
        Execute QPSO on the given problem using a weighted Chebyshev / scalarized objective.

        Returns:
            Dict containing best position, objective values, history, and evaluations.
        """
        np.random.seed(self.seed)
        dim = problem.n_var
        xl, xu = problem.xl, problem.xu
        weights = weight_vector if weight_vector is not None else np.ones(problem.n_obj) / problem.n_obj

        def scalar_eval(x_vec):
            out = {}
            problem._evaluate(x_vec, out)
            f_vals = np.array(out["F"])
            g_vals = np.array(out["G"])
            # Penalize constraint violation
            penalty = np.sum(np.maximum(0.0, g_vals)) * 1e5
            return np.dot(weights, f_vals) + penalty, f_vals, g_vals

        # 1. Initialize swarm
        X = np.random.uniform(xl, xu, size=(self.n_particles, dim))
        P = X.copy()

        p_evals = [scalar_eval(x) for x in X]
        P_scores = np.array([e[0] for e in p_evals])
        P_f_vals = np.array([e[1] for e in p_evals])
        evaluations_count = self.n_particles

        gbest_idx = np.argmin(P_scores)
        gbest = P[gbest_idx].copy()
        gbest_score = P_scores[gbest_idx]
        gbest_f = P_f_vals[gbest_idx].copy()

        convergence_history = [float(gbest_score)]

        # 2. Optimization loop
        for t in range(self.max_iterations):
            # Beta contraction-expansion schedule
            beta = self.beta_start - (self.beta_start - self.beta_end) * (t / self.max_iterations)

            # Mean best position: mbest = 1/M * sum(pbest)
            mbest = np.mean(P, axis=0)

            for i in range(self.n_particles):
                phi = np.random.uniform(0.0, 1.0, size=dim)
                p_local = phi * P[i] + (1.0 - phi) * gbest
                u = np.random.uniform(0.0, 1.0, size=dim)
                sign = np.where(np.random.uniform(0.0, 1.0, size=dim) > 0.5, 1.0, -1.0)

                # QPSO position update
                X[i] = p_local + sign * beta * np.abs(mbest - X[i]) * np.log(1.0 / np.maximum(u, 1e-10))

                # Box boundary projection
                X[i] = np.clip(X[i], xl, xu)

                score, f_vals, g_vals = scalar_eval(X[i])
                evaluations_count += 1

                if score < P_scores[i]:
                    P[i] = X[i].copy()
                    P_scores[i] = score
                    P_f_vals[i] = f_vals.copy()

                    if score < gbest_score:
                        gbest = X[i].copy()
                        gbest_score = score
                        gbest_f = f_vals.copy()

            convergence_history.append(float(gbest_score))

        return {
            "algorithm": "QPSO",
            "seed": self.seed,
            "best_x": gbest,
            "best_score": float(gbest_score),
            "best_objectives": gbest_f,
            "total_evaluations": evaluations_count,
            "convergence_history": convergence_history,
        }
