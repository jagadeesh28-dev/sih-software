"""
Offline Hyperparameter and Model Selection Engine.
Sections 11, 12, 13:
- Classical Quantum-behaved Particle Swarm Optimization (QPSO) metaheuristic (Sun et al. 2004)
- Baseline: Random Search Optimizer
- Evaluates strictly on VALIDATION data under equal evaluation budgets.
- Search space: learning_rate, num_leaves, max_depth, min_child_samples, feature_fraction,
  reg_alpha, reg_lambda, alpha (in [0.0, 1.0]).
- Classical CPU metaheuristic: NO quantum computing, QPU, supremacy, or tunneling claimed.
"""

import time
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error

from .residual_model import HybridResidualPredictor


class HyperparameterSearchSpace:
    """Defines search bounds and mapping to LightGBM + Hybrid parameters."""

    BOUNDS = [
        ("learning_rate", 0.01, 0.25, "float"),
        ("num_leaves", 15, 127, "int"),
        ("max_depth", 3, 10, "int"),
        ("min_child_samples", 5, 50, "int"),
        ("feature_fraction", 0.6, 1.0, "float"),
        ("reg_alpha", 0.001, 10.0, "log_float"),
        ("reg_lambda", 0.001, 10.0, "log_float"),
        ("alpha_residual", 0.0, 1.0, "float"),  # Section 13: primary alpha range [0, 1]
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


class QPSOModelSelector:
    """
    Classical offline metaheuristic using quantum-behaved delta-potential dynamics.
    Tuning objective: VALIDATION MAE under strict evaluation budget.
    """

    def __init__(
        self,
        n_particles: int = 15,
        max_iterations: int = 15,  # 15 * 15 = 225 evaluations total
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

    def search(
        self,
        train_df: pd.DataFrame,
        val_df: pd.DataFrame,
        target_col: str = "fuel_mass_flow_kg_h",
        feature_cols: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Execute QPSO search over validation performance.
        TEST set is strictly forbidden and must never be passed into this method.
        """
        t0 = time.perf_counter()
        rng = np.random.default_rng(self.seed)

        eval_count = 0
        y_val = val_df[target_col].values

        def evaluate_vector(vec: np.ndarray) -> float:
            nonlocal eval_count
            eval_count += 1
            p = HyperparameterSearchSpace.vector_to_params(vec)
            lgb_params = {
                "n_estimators": 100,
                "learning_rate": p["learning_rate"],
                "num_leaves": p["num_leaves"],
                "max_depth": p["max_depth"],
                "min_child_samples": p["min_child_samples"],
                "colsample_bytree": p["feature_fraction"],
                "reg_alpha": p["reg_alpha"],
                "reg_lambda": p["reg_lambda"],
                "random_state": self.seed,
                "n_jobs": -1,
                "verbose": -1,
            }
            try:
                model = HybridResidualPredictor(
                    feature_cols=feature_cols,
                    hyperparameters=lgb_params,
                    alpha=p["alpha_residual"],
                    seed=self.seed,
                )
                model.fit(train_df, target_col=target_col)
                preds = model.predict(val_df)
                score = float(mean_absolute_error(y_val, preds))
            except Exception:
                score = 1e6
            return score

        # 1. Initialize swarm in unit hypercube [0, 1]^d
        X = rng.uniform(0.0, 1.0, size=(self.n_particles, self.dim))
        P = X.copy()
        P_scores = np.array([evaluate_vector(x) for x in X])

        gbest_idx = np.argmin(P_scores)
        gbest = P[gbest_idx].copy()
        gbest_score = float(P_scores[gbest_idx])

        convergence = [gbest_score]

        # 2. QPSO Iteration Loop
        for t in range(self.max_iterations - 1):
            beta = self.beta_start - (self.beta_start - self.beta_end) * (t / self.max_iterations)
            mbest = np.mean(P, axis=0)

            for i in range(self.n_particles):
                phi = rng.uniform(0.0, 1.0, size=self.dim)
                p_local = phi * P[i] + (1.0 - phi) * gbest
                u = rng.uniform(0.0, 1.0, size=self.dim)
                sign = np.where(rng.uniform(0.0, 1.0, size=self.dim) > 0.5, 1.0, -1.0)

                # QPSO position update
                X[i] = p_local + sign * beta * np.abs(mbest - X[i]) * np.log(1.0 / np.maximum(u, 1e-10))
                # Bound handling (box constraints in [0, 1])
                X[i] = np.clip(X[i], 0.0, 1.0)

                score = evaluate_vector(X[i])
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
            "algorithm": "QPSO",
            "evaluations": eval_count,
            "wall_clock_runtime_s": round(elapsed, 2),
            "best_validation_mae": gbest_score,
            "best_params": best_params,
            "convergence_history": convergence,
            "best_vector": gbest.tolist(),
        }


class RandomSearchModelSelector:
    """
    Classical random search optimizer.
    Provides identical search space, identical evaluation budget, and identical objective.
    """

    def __init__(self, total_budget: int = 225, seed: int = 42):
        self.total_budget = total_budget
        self.seed = seed
        self.dim = HyperparameterSearchSpace.get_dim()

    def search(
        self,
        train_df: pd.DataFrame,
        val_df: pd.DataFrame,
        target_col: str = "fuel_mass_flow_kg_h",
        feature_cols: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        t0 = time.perf_counter()
        rng = np.random.default_rng(self.seed)
        y_val = val_df[target_col].values

        best_score = float("inf")
        best_vec = None
        convergence = []

        for i in range(self.total_budget):
            vec = rng.uniform(0.0, 1.0, size=self.dim)
            p = HyperparameterSearchSpace.vector_to_params(vec)
            lgb_params = {
                "n_estimators": 100,
                "learning_rate": p["learning_rate"],
                "num_leaves": p["num_leaves"],
                "max_depth": p["max_depth"],
                "min_child_samples": p["min_child_samples"],
                "colsample_bytree": p["feature_fraction"],
                "reg_alpha": p["reg_alpha"],
                "reg_lambda": p["reg_lambda"],
                "random_state": self.seed,
                "n_jobs": -1,
                "verbose": -1,
            }
            try:
                model = HybridResidualPredictor(
                    feature_cols=feature_cols,
                    hyperparameters=lgb_params,
                    alpha=p["alpha_residual"],
                    seed=self.seed,
                )
                model.fit(train_df, target_col=target_col)
                preds = model.predict(val_df)
                score = float(mean_absolute_error(y_val, preds))
            except Exception:
                score = 1e6

            if score < best_score:
                best_score = score
                best_vec = vec.copy()

            convergence.append(best_score)

        elapsed = time.perf_counter() - t0
        best_params = HyperparameterSearchSpace.vector_to_params(best_vec) if best_vec is not None else {}

        return {
            "algorithm": "RandomSearch",
            "evaluations": self.total_budget,
            "wall_clock_runtime_s": round(elapsed, 2),
            "best_validation_mae": best_score,
            "best_params": best_params,
            "convergence_history": convergence,
            "best_vector": best_vec.tolist() if best_vec is not None else [],
        }
