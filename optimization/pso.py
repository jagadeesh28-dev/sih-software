"""
Canonical Particle Swarm Optimization (PSO) Algorithm.
Standard Clerc-constricted PSO baseline for fair metaheuristic comparison.
"""

from typing import Any, Callable, Dict, List, Optional
import numpy as np


class CanonicalPSOOptimizer:
    """
    Standard velocity-position Particle Swarm Optimization.
    Velocity: v = chi * [v + c1*r1*(pbest - x) + c2*r2*(gbest - x)]
    Position: x = x + v
    Constriction factor: chi = 0.7298, c1 = c2 = 2.05
    """

    def __init__(
        self,
        n_particles: int = 100,
        max_iterations: int = 500,
        chi: float = 0.7298,
        c1: float = 2.05,
        c2: float = 2.05,
        seed: int = 42,
    ):
        self.n_particles = n_particles
        self.max_iterations = max_iterations
        self.chi = chi
        self.c1 = c1
        self.c2 = c2
        self.seed = seed

    def optimize(
        self,
        eval_fn: Callable[[np.ndarray], float],
        xl: np.ndarray,
        xu: np.ndarray,
        max_evaluations: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Execute Canonical PSO on bounded continuous decision space [xl, xu].
        """
        np.random.seed(self.seed)
        dim = len(xl)
        xl = np.asarray(xl, dtype=float)
        xu = np.asarray(xu, dtype=float)
        eval_cap = max_evaluations if max_evaluations is not None else (self.n_particles * self.max_iterations)

        # 1. Initialize swarm and velocities
        X = np.random.uniform(xl, xu, size=(self.n_particles, dim))
        span = xu - xl
        V = np.random.uniform(-span * 0.1, span * 0.1, size=(self.n_particles, dim))
        P = X.copy()

        P_scores = np.zeros(self.n_particles)
        evaluations_count = 0

        for i in range(self.n_particles):
            P_scores[i] = eval_fn(X[i])
            evaluations_count += 1
            if evaluations_count >= eval_cap:
                break

        gbest_idx = np.argmin(P_scores)
        gbest = P[gbest_idx].copy()
        gbest_score = float(P_scores[gbest_idx])

        convergence_history = [float(gbest_score)]

        # 2. Velocity-position loop
        t = 0
        while t < self.max_iterations and evaluations_count < eval_cap:
            for i in range(self.n_particles):
                if evaluations_count >= eval_cap:
                    break

                r1 = np.random.uniform(0.0, 1.0, size=dim)
                r2 = np.random.uniform(0.0, 1.0, size=dim)

                # Velocity update
                V[i] = self.chi * (
                    V[i]
                    + self.c1 * r1 * (P[i] - X[i])
                    + self.c2 * r2 * (gbest - X[i])
                )

                # Position update & box projection
                X[i] = np.clip(X[i] + V[i], xl, xu)

                score = float(eval_fn(X[i]))
                evaluations_count += 1

                if score < P_scores[i]:
                    P[i] = X[i].copy()
                    P_scores[i] = score

                    if score < gbest_score:
                        gbest = X[i].copy()
                        gbest_score = score

            convergence_history.append(float(gbest_score))
            t += 1

        return {
            "algorithm": "PSO",
            "seed": self.seed,
            "best_x": gbest,
            "best_score": float(gbest_score),
            "total_evaluations": evaluations_count,
            "convergence_history": convergence_history,
        }
