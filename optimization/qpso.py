"""
Quantum-Behaved Particle Swarm Optimization (QPSO) Algorithm.
Classical metaheuristic based on quantum delta-potential well dynamics (Sun et al. 2004).
Section 16 & 17: Strictly classical execution on CPU cores. QPSO is allowed to lose in benchmarks.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import numpy as np


class QPSOOptimizer:
    """
    Quantum-behaved Particle Swarm Optimization for constrained operational optimization.
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
        problem_or_fn: Union[Callable[[np.ndarray], float], Any],
        xl: Optional[np.ndarray] = None,
        xu: Optional[np.ndarray] = None,
        max_evaluations: Optional[int] = None,
        weight_vector: Optional[np.ndarray] = None,
    ) -> Dict[str, Any]:
        """
        Execute QPSO on either:
        1. Problem object with ._evaluate(x, out), .xl, .xu, .n_var
        2. Scalar evaluation function eval_fn(x) with explicit bounds xl, xu
        """
        np.random.seed(self.seed)

        if hasattr(problem_or_fn, "_evaluate") or hasattr(problem_or_fn, "xl"):
            problem = problem_or_fn
            xl_arr = np.asarray(problem.xl, dtype=float)
            xu_arr = np.asarray(problem.xu, dtype=float)
            dim = len(xl_arr)
            n_obj = getattr(problem, "n_obj", 1)
            weights = weight_vector if weight_vector is not None else np.ones(n_obj) / max(1, n_obj)

            def eval_wrapper(x_vec: np.ndarray) -> Tuple[float, np.ndarray]:
                out: Dict[str, Any] = {}
                problem._evaluate(x_vec, out)
                f_vals = np.array(out.get("F", [0.0]))
                g_vals = np.array(out.get("G", [0.0]))
                penalty = np.sum(np.maximum(0.0, g_vals)) * 1e5
                return float(np.dot(weights, f_vals) + penalty), f_vals
        else:
            eval_fn = problem_or_fn
            if xl is None or xu is None:
                raise ValueError("xl and xu must be provided when passing a callable eval_fn")
            xl_arr = np.asarray(xl, dtype=float)
            xu_arr = np.asarray(xu, dtype=float)
            dim = len(xl_arr)

            def eval_wrapper(x_vec: np.ndarray) -> Tuple[float, np.ndarray]:
                score = float(eval_fn(x_vec))
                return score, np.array([score])

        eval_cap = max_evaluations if max_evaluations is not None else (self.n_particles * self.max_iterations)

        # 1. Initialize swarm uniformly across bounded space
        X = np.random.uniform(xl_arr, xu_arr, size=(self.n_particles, dim))
        P = X.copy()

        P_scores = np.zeros(self.n_particles)
        P_f_vals = []
        evaluations_count = 0

        for i in range(self.n_particles):
            score, f_val = eval_wrapper(X[i])
            P_scores[i] = score
            P_f_vals.append(f_val)
            evaluations_count += 1
            if evaluations_count >= eval_cap:
                break

        gbest_idx = np.argmin(P_scores)
        gbest = P[gbest_idx].copy()
        gbest_score = float(P_scores[gbest_idx])
        gbest_f = P_f_vals[gbest_idx].copy()

        convergence_history = [float(gbest_score)]

        # 2. Optimization loop
        t = 0
        while t < self.max_iterations and evaluations_count < eval_cap:
            # Beta contraction-expansion schedule
            beta = self.beta_start - (self.beta_start - self.beta_end) * (t / max(1, self.max_iterations))

            # Mean best position: mbest = 1/M * sum(pbest)
            mbest = np.mean(P, axis=0)

            for i in range(self.n_particles):
                if evaluations_count >= eval_cap:
                    break

                phi = np.random.uniform(0.0, 1.0, size=dim)
                p_local = phi * P[i] + (1.0 - phi) * gbest
                u = np.random.uniform(0.0, 1.0, size=dim)
                sign = np.where(np.random.uniform(0.0, 1.0, size=dim) > 0.5, 1.0, -1.0)

                # QPSO quantum delta-potential update
                X[i] = p_local + sign * beta * np.abs(mbest - X[i]) * np.log(1.0 / np.maximum(u, 1e-10))

                # Box boundary projection
                X[i] = np.clip(X[i], xl_arr, xu_arr)

                score, f_val = eval_wrapper(X[i])
                evaluations_count += 1

                if score < P_scores[i]:
                    P[i] = X[i].copy()
                    P_scores[i] = score
                    P_f_vals[i] = f_val.copy()

                    if score < gbest_score:
                        gbest = X[i].copy()
                        gbest_score = score
                        gbest_f = f_val.copy()

            convergence_history.append(float(gbest_score))
            t += 1

        return {
            "algorithm": "QPSO",
            "seed": self.seed,
            "best_x": gbest,
            "best_score": float(gbest_score),
            "best_objectives": gbest_f,
            "total_evaluations": evaluations_count,
            "convergence_history": convergence_history,
        }

