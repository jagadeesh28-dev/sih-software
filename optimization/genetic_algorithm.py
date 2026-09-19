"""
Real-Coded Genetic Algorithm (GA) Optimization Engine.
Standard evolutionary baseline using Simulated Binary Crossover (SBX) and Polynomial Mutation.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np


class GeneticAlgorithmOptimizer:
    """
    Real-coded Genetic Algorithm for constrained continuous/mixed optimization.
    - Selection: Tournament Selection (k=3)
    - Crossover: Simulated Binary Crossover (SBX, eta_c=15, p_c=0.9)
    - Mutation: Polynomial Mutation (eta_m=20, p_m=0.1)
    - Elitism: Preserves top individual across generations
    """

    def __init__(
        self,
        population_size: int = 100,
        max_generations: int = 500,
        crossover_rate: float = 0.9,
        mutation_rate: float = 0.1,
        eta_c: float = 15.0,
        eta_m: float = 20.0,
        tournament_size: int = 3,
        seed: int = 42,
    ):
        self.population_size = population_size
        self.max_generations = max_generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.eta_c = eta_c
        self.eta_m = eta_m
        self.tournament_size = tournament_size
        self.seed = seed

    def _sbx_crossover(
        self,
        p1: np.ndarray,
        p2: np.ndarray,
        xl: np.ndarray,
        xu: np.ndarray,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Simulated Binary Crossover (SBX)."""
        dim = len(p1)
        c1 = p1.copy()
        c2 = p2.copy()

        if np.random.uniform(0.0, 1.0) > self.crossover_rate:
            return c1, c2

        for d in range(dim):
            if np.random.uniform(0.0, 1.0) <= 0.5:
                if abs(p1[d] - p2[d]) > 1e-10:
                    y1 = min(p1[d], p2[d])
                    y2 = max(p1[d], p2[d])
                    rand = np.random.uniform(0.0, 1.0)

                    # Beta formulation
                    beta = 1.0 + (2.0 * (y1 - xl[d]) / (y2 - y1))
                    alpha = 2.0 - (beta ** -(self.eta_c + 1.0))
                    if rand <= (1.0 / alpha):
                        beta_q = (rand * alpha) ** (1.0 / (self.eta_c + 1.0))
                    else:
                        beta_q = (1.0 / (2.0 - rand * alpha)) ** (1.0 / (self.eta_c + 1.0))

                    c1[d] = 0.5 * ((y1 + y2) - beta_q * (y2 - y1))
                    c2[d] = 0.5 * ((y1 + y2) + beta_q * (y2 - y1))
                    c1[d] = np.clip(c1[d], xl[d], xu[d])
                    c2[d] = np.clip(c2[d], xl[d], xu[d])
        return c1, c2

    def _polynomial_mutation(
        self,
        ind: np.ndarray,
        xl: np.ndarray,
        xu: np.ndarray,
    ) -> np.ndarray:
        """Polynomial Mutation."""
        dim = len(ind)
        mut = ind.copy()
        for d in range(dim):
            if np.random.uniform(0.0, 1.0) <= self.mutation_rate:
                y = ind[d]
                delta1 = (y - xl[d]) / (xu[d] - xl[d])
                delta2 = (xu[d] - y) / (xu[d] - xl[d])
                rand = np.random.uniform(0.0, 1.0)
                mut_pow = 1.0 / (self.eta_m + 1.0)

                if rand < 0.5:
                    xy = 1.0 - delta1
                    val = 2.0 * rand + (1.0 - 2.0 * rand) * (xy ** (self.eta_m + 1.0))
                    delta_q = (val ** mut_pow) - 1.0
                else:
                    xy = 1.0 - delta2
                    val = 2.0 * (1.0 - rand) + 2.0 * (rand - 0.5) * (xy ** (self.eta_m + 1.0))
                    delta_q = 1.0 - (val ** mut_pow)

                mut[d] = np.clip(y + delta_q * (xu[d] - xl[d]), xl[d], xu[d])
        return mut

    def optimize(
        self,
        eval_fn: Callable[[np.ndarray], float],
        xl: np.ndarray,
        xu: np.ndarray,
        max_evaluations: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Execute Real-Coded Genetic Algorithm on bounded space [xl, xu].
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

        # 2. Generational evolution loop
        gen = 0
        while gen < self.max_generations and evaluations_count < eval_cap:
            new_pop = []

            # Elitism: retain best individual
            new_pop.append(best_x.copy())

            while len(new_pop) < self.population_size:
                if evaluations_count >= eval_cap:
                    break

                # Tournament selection
                i1, i2 = np.random.choice(self.population_size, size=2, replace=False)
                t1 = i1 if fitness[i1] < fitness[i2] else i2
                i3, i4 = np.random.choice(self.population_size, size=2, replace=False)
                t2 = i3 if fitness[i3] < fitness[i4] else i4

                p1, p2 = pop[t1], pop[t2]
                c1, c2 = self._sbx_crossover(p1, p2, xl, xu)
                c1 = self._polynomial_mutation(c1, xl, xu)
                c2 = self._polynomial_mutation(c2, xl, xu)

                new_pop.append(c1)
                if len(new_pop) < self.population_size:
                    new_pop.append(c2)

            # Evaluate new population
            pop = np.array(new_pop[:self.population_size])
            fitness[0] = best_score  # Elitist preserves its score

            for i in range(1, len(pop)):
                if evaluations_count >= eval_cap:
                    break
                fitness[i] = eval_fn(pop[i])
                evaluations_count += 1

                if fitness[i] < best_score:
                    best_score = float(fitness[i])
                    best_x = pop[i].copy()

            convergence_history.append(float(best_score))
            gen += 1

        return {
            "algorithm": "GA",
            "seed": self.seed,
            "best_x": best_x,
            "best_score": float(best_score),
            "total_evaluations": evaluations_count,
            "convergence_history": convergence_history,
        }
