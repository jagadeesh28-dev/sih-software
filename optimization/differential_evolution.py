"""
Differential Evolution (DE) Algorithm.
Standard DE/rand/1/bin evolutionary baseline for fair metaheuristic comparison.
"""

from typing import Any, Callable, Dict, List, Optional
import numpy as np


class DifferentialEvolutionOptimizer:
    """
    Differential Evolution (DE/rand/1/bin) with binomial crossover.
    Donor vector: v = x_r1 + F * (x_r2 - x_r3)
    Trial vector: u_d = v_d if rand <= CR or d == d_rand else x_d
    """

    def __init__(
        self,
        population_size: int = 100,
        max_generations: int = 500,
        f_mut: float = 0.8,
        cr: float = 0.9,
        seed: int = 42,
    ):
        self.population_size = population_size
        self.max_generations = max_generations
        self.f_mut = f_mut
        self.cr = cr
        self.seed = seed

    def optimize(
        self,
        eval_fn: Callable[[np.ndarray], float],
        xl: np.ndarray,
        xu: np.ndarray,
        max_evaluations: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Execute Differential Evolution on bounded continuous decision space [xl, xu].
        """
        np.random.seed(self.seed)
        dim = len(xl)
        xl = np.asarray(xl, dtype=float)
        xu = np.asarray(xu, dtype=float)
        eval_cap = max_evaluations if max_evaluations is not None else (self.population_size * self.max_generations)

        # 1. Initialize population
        pop = np.random.uniform(xl, xu, size=(self.population_size, dim))
        fitness = np.zeros(self.population_size)
        evaluations_count = 0

        for i in range(self.population_size):
            fitness[i] = eval_fn(pop[i])
            evaluations_count += 1
            if evaluations_count >= eval_cap:
                break

        best_idx = np.argmin(fitness)
        best_x = pop[best_idx].copy()
        best_score = float(fitness[best_idx])

        convergence_history = [float(best_score)]

        # 2. Generational mutation-crossover loop
        gen = 0
        while gen < self.max_generations and evaluations_count < eval_cap:
            for i in range(self.population_size):
                if evaluations_count >= eval_cap:
                    break

                # Select 3 distinct random donors
                candidates = [idx for idx in range(self.population_size) if idx != i]
                r1, r2, r3 = np.random.choice(candidates, size=3, replace=False)

                # Mutation
                v = pop[r1] + self.f_mut * (pop[r2] - pop[r3])
                v = np.clip(v, xl, xu)

                # Binomial Crossover
                j_rand = np.random.randint(0, dim)
                u = pop[i].copy()
                for d in range(dim):
                    if np.random.uniform(0.0, 1.0) <= self.cr or d == j_rand:
                        u[d] = v[d]

                score_u = float(eval_fn(u))
                evaluations_count += 1

                # Greedy selection
                if score_u < fitness[i]:
                    pop[i] = u.copy()
                    fitness[i] = score_u

                    if score_u < best_score:
                        best_score = score_u
                        best_x = u.copy()

            convergence_history.append(float(best_score))
            gen += 1

        return {
            "algorithm": "DE",
            "seed": self.seed,
            "best_x": best_x,
            "best_score": float(best_score),
            "total_evaluations": evaluations_count,
            "convergence_history": convergence_history,
        }
