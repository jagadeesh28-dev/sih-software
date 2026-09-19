"""
Quantum-Behaved Particle Swarm Optimization (QPSO) and Classical HPO Controls.
SIH26138 - Phase 6

Implements the standard delta-potential well QPSO metaheuristic (Sun, Feng & Xu, 2004)
along with direct, budget-matched classical controls (Classical PSO and Random Search).

Key Mathematical Equations:
1. Mean Best Position (mbest):
   mbest_j = (1 / N) * sum_{i=1}^N P_{ij}
2. Local Attractor:
   p_{ij} = phi_j * P_{ij} + (1 - phi_j) * gbest_j,  where phi_j ~ U(0, 1)
3. Quantum Wave Equation Position Step:
   X_{ij}(t+1) = p_{ij} +- beta(t) * |mbest_j - X_{ij}(t)| * ln(1 / u_{ij}),  where u_{ij} ~ U(0, 1)
4. Contraction-Expansion Coefficient (beta):
   beta(t) = beta_start - (beta_start - beta_end) * (t / T_max)
"""

import time
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np


class HyperparameterSearchSpace:
    """Defines search bounds and mapping to LightGBM + Hybrid parameters."""

    BOUNDS = [
        ("learning_rate", 0.01, 0.20, "float"),
        ("num_leaves", 15, 63, "int"),
        ("max_depth", 3, 8, "int"),
        ("min_child_samples", 10, 50, "int"),
        ("colsample_bytree", 0.6, 1.0, "float"),
        ("reg_alpha", 0.001, 5.0, "log_float"),
        ("reg_lambda", 0.001, 5.0, "log_float"),
        ("alpha_residual", 0.5, 1.0, "float"),
    ]

    @classmethod
    def get_dim(cls) -> int:
        return len(cls.BOUNDS)

    @classmethod
    def vector_to_params(cls, vec: np.ndarray) -> Dict[str, Any]:
        """Convert continuous vector in [0, 1]^d to concrete model parameters."""
        params = {}
        for i, (name, low, high, p_type) in enumerate(cls.BOUNDS):
            val = float(vec[i])
            val = max(0.0, min(1.0, val))

            if p_type == "int":
                params[name] = int(round(low + val * (high - low)))
            elif p_type == "float":
                params[name] = float(low + val * (high - low))
            elif p_type == "log_float":
                log_low = np.log10(low)
                log_high = np.log10(high)
                params[name] = float(10.0 ** (log_low + val * (log_high - log_low)))

        return params


class QPSOOptimizer:
    """
    Quantum-Behaved Particle Swarm Optimization (QPSO).
    Searches continuous hyperparameter space using delta-potential quantum mechanics.
    """

    def __init__(
        self,
        n_particles: int = 15,
        max_iterations: int = 10,
        beta_start: float = 1.0,
        beta_end: float = 0.5,
        seed: int = 42,
    ):
        self.n_particles = n_particles
        self.max_iterations = max_iterations
        self.total_budget = n_particles * max_iterations
        self.beta_start = beta_start
        self.beta_end = beta_end
        self.seed = seed
        self.dim = HyperparameterSearchSpace.get_dim()
        self.rng = np.random.default_rng(seed)

    def optimize(
        self,
        eval_fn: Callable[[Dict[str, Any]], float],
    ) -> Dict[str, Any]:
        """
        Execute QPSO search.
        eval_fn: Function mapping concrete hyperparameter dict to validation MAE.
        """
        t0 = time.perf_counter()
        eval_count = 0

        # Initialize particles uniformly in [0, 1]^d
        X = self.rng.uniform(0.0, 1.0, size=(self.n_particles, self.dim))
        P = X.copy()
        P_scores = np.zeros(self.n_particles)

        for i in range(self.n_particles):
            params = HyperparameterSearchSpace.vector_to_params(X[i])
            P_scores[i] = eval_fn(params)
            eval_count += 1

        gbest_idx = int(np.argmin(P_scores))
        gbest = P[gbest_idx].copy()
        gbest_score = float(P_scores[gbest_idx])
        convergence = [gbest_score]

        # QPSO Main Loop
        for t in range(1, self.max_iterations):
            beta = self.beta_start - (self.beta_start - self.beta_end) * (t / self.max_iterations)
            mbest = np.mean(P, axis=0)

            for i in range(self.n_particles):
                phi = self.rng.uniform(0.0, 1.0, size=self.dim)
                p_local = phi * P[i] + (1.0 - phi) * gbest
                u = self.rng.uniform(0.0, 1.0, size=self.dim)
                sign = np.where(self.rng.uniform(0.0, 1.0, size=self.dim) > 0.5, 1.0, -1.0)

                # Quantum position update equation
                X[i] = p_local + sign * beta * np.abs(mbest - X[i]) * np.log(1.0 / np.maximum(u, 1e-10))
                # Bound handling (box constraints in [0, 1])
                X[i] = np.clip(X[i], 0.0, 1.0)

                params = HyperparameterSearchSpace.vector_to_params(X[i])
                score = eval_fn(params)
                eval_count += 1

                if score < P_scores[i]:
                    P[i] = X[i].copy()
                    P_scores[i] = score
                    if score < gbest_score:
                        gbest = X[i].copy()
                        gbest_score = score

            convergence.append(gbest_score)

        elapsed = time.perf_counter() - t0
        best_params = HyperparameterSearchSpace.vector_to_params(gbest)

        return {
            "algorithm": "QPSO-HPO",
            "evaluations": eval_count,
            "runtime_s": round(elapsed, 2),
            "best_score": gbest_score,
            "best_params": best_params,
            "convergence_history": convergence,
            "best_vector": gbest.tolist(),
        }


class ClassicalPSOOptimizer:
    """
    Classical Velocity-Based Particle Swarm Optimization (CPSO).
    Provides a fair, budget-matched classical control for QPSO.
    """

    def __init__(
        self,
        n_particles: int = 15,
        max_iterations: int = 10,
        inertia_w: float = 0.7,
        c1: float = 1.5,
        c2: float = 1.5,
        seed: int = 42,
    ):
        self.n_particles = n_particles
        self.max_iterations = max_iterations
        self.total_budget = n_particles * max_iterations
        self.w = inertia_w
        self.c1 = c1
        self.c2 = c2
        self.seed = seed
        self.dim = HyperparameterSearchSpace.get_dim()
        self.rng = np.random.default_rng(seed)

    def optimize(
        self,
        eval_fn: Callable[[Dict[str, Any]], float],
    ) -> Dict[str, Any]:
        """Execute classical PSO search."""
        t0 = time.perf_counter()
        eval_count = 0

        X = self.rng.uniform(0.0, 1.0, size=(self.n_particles, self.dim))
        V = self.rng.uniform(-0.1, 0.1, size=(self.n_particles, self.dim))
        P = X.copy()
        P_scores = np.zeros(self.n_particles)

        for i in range(self.n_particles):
            params = HyperparameterSearchSpace.vector_to_params(X[i])
            P_scores[i] = eval_fn(params)
            eval_count += 1

        gbest_idx = int(np.argmin(P_scores))
        gbest = P[gbest_idx].copy()
        gbest_score = float(P_scores[gbest_idx])
        convergence = [gbest_score]

        for t in range(1, self.max_iterations):
            for i in range(self.n_particles):
                r1 = self.rng.uniform(0.0, 1.0, size=self.dim)
                r2 = self.rng.uniform(0.0, 1.0, size=self.dim)

                V[i] = (
                    self.w * V[i]
                    + self.c1 * r1 * (P[i] - X[i])
                    + self.c2 * r2 * (gbest - X[i])
                )
                V[i] = np.clip(V[i], -0.2, 0.2)
                X[i] = np.clip(X[i] + V[i], 0.0, 1.0)

                params = HyperparameterSearchSpace.vector_to_params(X[i])
                score = eval_fn(params)
                eval_count += 1

                if score < P_scores[i]:
                    P[i] = X[i].copy()
                    P_scores[i] = score
                    if score < gbest_score:
                        gbest = X[i].copy()
                        gbest_score = score

            convergence.append(gbest_score)

        elapsed = time.perf_counter() - t0
        best_params = HyperparameterSearchSpace.vector_to_params(gbest)

        return {
            "algorithm": "CPSO-HPO",
            "evaluations": eval_count,
            "runtime_s": round(elapsed, 2),
            "best_score": gbest_score,
            "best_params": best_params,
            "convergence_history": convergence,
            "best_vector": gbest.tolist(),
        }


class RandomSearchOptimizer:
    """Uniform Random Search over hyperparameter space under identical budget."""

    def __init__(self, total_budget: int = 150, seed: int = 42):
        self.total_budget = total_budget
        self.seed = seed
        self.dim = HyperparameterSearchSpace.get_dim()
        self.rng = np.random.default_rng(seed)

    def optimize(
        self,
        eval_fn: Callable[[Dict[str, Any]], float],
    ) -> Dict[str, Any]:
        t0 = time.perf_counter()
        best_score = float("inf")
        best_vec = None
        convergence = []

        for i in range(self.total_budget):
            vec = self.rng.uniform(0.0, 1.0, size=self.dim)
            params = HyperparameterSearchSpace.vector_to_params(vec)
            score = eval_fn(params)
            if score < best_score:
                best_score = score
                best_vec = vec.copy()
            convergence.append(best_score)

        elapsed = time.perf_counter() - t0
        best_params = HyperparameterSearchSpace.vector_to_params(best_vec)

        return {
            "algorithm": "RS-HPO",
            "evaluations": self.total_budget,
            "runtime_s": round(elapsed, 2),
            "best_score": best_score,
            "best_params": best_params,
            "convergence_history": convergence,
            "best_vector": best_vec.tolist(),
        }
