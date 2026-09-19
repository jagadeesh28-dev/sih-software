"""
Feature Selection Framework: Quantum-Inspired vs Matched Classical Controls.
SIH26138 - Phase 6

Provides fair, budget-matched feature selection algorithms:
1. QIEAFeatureSelector: Q-bit rotation search (Han & Kim 2002).
2. ClassicalGAFeatureSelector: Standard binary Genetic Algorithm with tournament selection,
   two-point crossover, bit-flip mutation, and elite preservation.
3. LassoFeatureSelector: L1-regularized linear baseline.

All algorithms evaluate candidate feature subsets strictly against VALIDATION MAE
using identical training subsets and identical evaluation budgets.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.linear_model import LassoCV

from .qiea import QIEAFeatureSelector


class ClassicalGAFeatureSelector:
    """
    Classical Binary Genetic Algorithm for Feature Selection.
    Acts as the direct, fair classical control for QIEA-FS.
    Matched population size, generations, and evaluation budget.
    """

    def __init__(
        self,
        population_size: int = 10,
        max_generations: int = 15,
        crossover_rate: float = 0.8,
        mutation_rate: float = 0.1,
        tournament_size: int = 2,
        seed: int = 42,
    ):
        self.pop_size = population_size
        self.max_generations = max_generations
        self.total_budget = population_size * max_generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.tournament_size = tournament_size
        self.seed = seed
        self.rng = np.random.default_rng(seed)

    def search(
        self,
        n_features: int,
        eval_fn: Callable[[np.ndarray], float],
    ) -> Dict[str, Any]:
        """Execute Classical Binary GA feature search."""
        # 1. Initialize random binary population
        population = self.rng.integers(0, 2, size=(self.pop_size, n_features))
        # Ensure each individual has at least one feature
        for i in range(self.pop_size):
            if np.sum(population[i]) == 0:
                population[i, self.rng.integers(0, n_features)] = 1

        eval_count = 0
        unique_masks_evaluated = set()
        convergence_curve: List[float] = []

        scores = np.zeros(self.pop_size)
        for i in range(self.pop_size):
            scores[i] = eval_fn(population[i])
            eval_count += 1
            unique_masks_evaluated.add(tuple(population[i].tolist()))

        gbest_idx = int(np.argmin(scores))
        gbest_mask = population[gbest_idx].copy()
        gbest_score = float(scores[gbest_idx])
        convergence_curve.append(gbest_score)

        # Generational loop
        for gen in range(1, self.max_generations):
            new_pop = [gbest_mask.copy()]  # Elite preservation

            while len(new_pop) < self.pop_size:
                # Tournament Selection
                p1_idx = self._tournament(scores)
                p2_idx = self._tournament(scores)
                parent1 = population[p1_idx]
                parent2 = population[p2_idx]

                # Two-point Crossover
                if self.rng.uniform(0.0, 1.0) < self.crossover_rate and n_features > 2:
                    pt1, pt2 = sorted(self.rng.choice(n_features, size=2, replace=False))
                    child = parent1.copy()
                    child[pt1:pt2] = parent2[pt1:pt2]
                else:
                    child = parent1.copy()

                # Bit-flip Mutation
                for j in range(n_features):
                    if self.rng.uniform(0.0, 1.0) < self.mutation_rate:
                        child[j] = 1 - child[j]

                # Safety guard
                if np.sum(child) == 0:
                    child[self.rng.integers(0, n_features)] = 1

                new_pop.append(child)

            population = np.array(new_pop[: self.pop_size])

            # Evaluate new population
            for i in range(self.pop_size):
                scores[i] = eval_fn(population[i])
                eval_count += 1
                unique_masks_evaluated.add(tuple(population[i].tolist()))

                if scores[i] < gbest_score:
                    gbest_score = float(scores[i])
                    gbest_mask = population[i].copy()

            convergence_curve.append(gbest_score)

        return {
            "algorithm": "CGA-FS",
            "best_mask": gbest_mask,
            "best_score": gbest_score,
            "selected_indices": np.where(gbest_mask == 1)[0].tolist(),
            "n_selected": int(np.sum(gbest_mask)),
            "total_evaluations": eval_count,
            "unique_configurations": len(unique_masks_evaluated),
            "convergence_history": convergence_curve,
        }

    def _tournament(self, scores: np.ndarray) -> int:
        candidates = self.rng.choice(len(scores), size=self.tournament_size, replace=False)
        return int(candidates[np.argmin(scores[candidates])])


class FeatureSelectionBenchmark:
    """
    Coordinates feature selection experiments on maritime telemetry residuals.
    Compares QIEA-FS against Classical GA-FS under matched conditions.
    """

    def __init__(
        self,
        feature_names: List[str],
        population_size: int = 10,
        max_generations: int = 15,
        seed: int = 42,
    ):
        self.feature_names = list(feature_names)
        self.n_features = len(self.feature_names)
        self.pop_size = population_size
        self.max_generations = max_generations
        self.seed = seed

    def build_eval_function(
        self,
        X_train: pd.DataFrame,
        r_train: np.ndarray,
        X_val: pd.DataFrame,
        r_val: np.ndarray,
        f_phys_val: np.ndarray,
        y_val: np.ndarray,
        alpha: float = 1.0,
    ) -> Tuple[Callable[[np.ndarray], float], Dict[str, Any]]:
        """
        Constructs an evaluation closure that trains a LightGBM regressor on the selected
        residual feature subset and returns the validation MAE of the full hybrid prediction.
        """
        import lightgbm as lgb
        from sklearn.metrics import mean_absolute_error

        eval_cache: Dict[tuple, float] = {}

        def eval_fn(mask: np.ndarray) -> float:
            mask_tuple = tuple(mask.tolist())
            if mask_tuple in eval_cache:
                return eval_cache[mask_tuple]

            selected_cols = [self.feature_names[i] for i, val in enumerate(mask) if val == 1]
            if not selected_cols:
                return float("inf")

            X_tr = X_train[selected_cols]
            X_va = X_val[selected_cols]

            model = lgb.LGBMRegressor(
                n_estimators=100,
                learning_rate=0.05,
                num_leaves=31,
                max_depth=6,
                min_child_samples=20,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=self.seed,
                n_jobs=-1,
                verbose=-1,
            )
            try:
                model.fit(X_tr, r_train)
                r_hat_val = model.predict(X_va)
                y_pred_val = np.maximum(0.0, f_phys_val + alpha * r_hat_val)
                mae = float(mean_absolute_error(y_val, y_pred_val))
            except Exception:
                mae = 1e6

            eval_cache[mask_tuple] = mae
            return mae

        return eval_fn, eval_cache
