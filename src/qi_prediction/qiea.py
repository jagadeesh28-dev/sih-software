"""
Quantum-Inspired Evolutionary Algorithm (QIEA) for Feature Selection.
SIH26138 - Phase 6

Implements the canonical Q-bit representation and rotation gate dynamics
of Han & Kim (2002) adapted for maritime telemetry feature subset selection.

Key Mathematical Mechanisms:
1. Q-Bit State: q_i = [alpha_i, beta_i]^T with |alpha_i|^2 + |beta_i|^2 = 1.0.
2. Superposition Initialization: alpha_i = beta_i = 1/sqrt(2), P(select) = |beta_i|^2 = 0.5.
3. Measurement Collapse: Binary observation x_i in {0, 1} where P(x_i = 1) = |beta_i|^2.
4. Quantum Rotation Gate: U(Delta theta) = [[cos(theta), -sin(theta)], [sin(theta), cos(theta)]].
5. Update Lookup Table: Standard Han & Kim quadrant sign matrix.
6. Quantum Entropy: H(Q) = - (1/m) sum(alpha^2 log2(alpha^2) + beta^2 log2(beta^2)).
"""

from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np


class QBitChromosome:
    """
    Represents a population of Q-bits where each Q-bit encodes the probability
    amplitude of a feature being excluded (|0>) or included (|1>).
    """

    def __init__(self, n_features: int, seed: Optional[int] = None):
        self.n_features = n_features
        self.rng = np.random.default_rng(seed)

        # Initialize to equal superposition |psi> = 1/sqrt(2)|0> + 1/sqrt(2)|1>
        self.alpha = np.full(n_features, 1.0 / np.sqrt(2.0), dtype=float)
        self.beta = np.full(n_features, 1.0 / np.sqrt(2.0), dtype=float)

    def normalize(self) -> None:
        """Enforce quantum probability normalization: |alpha|^2 + |beta|^2 = 1.0."""
        norm = np.sqrt(self.alpha**2 + self.beta**2)
        norm = np.where(norm < 1e-12, 1.0, norm)
        self.alpha /= norm
        self.beta /= norm

    def measure(self) -> np.ndarray:
        """
        Collapse Q-bit superpositions into a classical binary selection vector.
        P(select_i = 1) = |beta_i|^2.
        Safety guard: Ensures at least 1 feature is selected.
        """
        prob_one = self.beta**2
        random_draws = self.rng.uniform(0.0, 1.0, size=self.n_features)
        binary_solution = (random_draws < prob_one).astype(int)

        # If zero features were selected, include the feature with highest beta^2
        if np.sum(binary_solution) == 0:
            best_feat = int(np.argmax(prob_one))
            binary_solution[best_feat] = 1

        return binary_solution

    def apply_rotation_gate(
        self,
        current_x: np.ndarray,
        best_b: np.ndarray,
        is_better: bool,
        theta_step: float = 0.05 * np.pi,
    ) -> None:
        """
        Update Q-bit amplitudes using quantum rotation gates:
        [alpha', beta']^T = R(Delta theta) * [alpha, beta]^T
        Rotation direction is determined via the Han & Kim (2002) sign table.
        """
        for i in range(self.n_features):
            xi = current_x[i]
            bi = best_b[i]

            # Han & Kim Lookup Table for rotation angle sign
            delta_theta = 0.0
            if not is_better:  # Current is worse than best; rotate toward best
                if xi == 0 and bi == 1:
                    # Move toward |1>: increase |beta|
                    if self.alpha[i] * self.beta[i] > 0:
                        delta_theta = theta_step
                    elif self.alpha[i] * self.beta[i] < 0:
                        delta_theta = -theta_step
                    elif self.alpha[i] == 0:
                        delta_theta = 0.0
                    elif self.beta[i] == 0:
                        delta_theta = theta_step
                elif xi == 1 and bi == 0:
                    # Move toward |0>: increase |alpha|
                    if self.alpha[i] * self.beta[i] > 0:
                        delta_theta = -theta_step
                    elif self.alpha[i] * self.beta[i] < 0:
                        delta_theta = theta_step
                    elif self.alpha[i] == 0:
                        delta_theta = -theta_step
                    elif self.beta[i] == 0:
                        delta_theta = 0.0

            if delta_theta != 0.0:
                cos_t = np.cos(delta_theta)
                sin_t = np.sin(delta_theta)
                new_alpha = cos_t * self.alpha[i] - sin_t * self.beta[i]
                new_beta = sin_t * self.alpha[i] + cos_t * self.beta[i]
                self.alpha[i] = new_alpha
                self.beta[i] = new_beta

        self.normalize()

    def get_selection_probabilities(self) -> np.ndarray:
        """Return the vector of feature selection probabilities |beta_i|^2."""
        return self.beta**2

    def get_shannon_entropy(self) -> float:
        """
        Compute mean quantum state entropy across features:
        H = - (1/m) sum(alpha^2 log2(alpha^2) + beta^2 log2(beta^2))
        H = 1.0 represents complete superposition (exploration).
        H -> 0 represents complete collapse to deterministic state (exploitation).
        """
        p0 = np.clip(self.alpha**2, 1e-12, 1.0)
        p1 = np.clip(self.beta**2, 1e-12, 1.0)
        ent = -(p0 * np.log2(p0) + p1 * np.log2(p1))
        return float(np.mean(ent))


class QIEAFeatureSelector:
    """
    Quantum-Inspired Evolutionary Algorithm for Feature Selection.
    Optimizes a population of Q-bit individuals under strict evaluation budget.
    """

    def __init__(
        self,
        population_size: int = 10,
        max_generations: int = 15,
        theta_step: float = 0.05 * np.pi,
        seed: int = 42,
    ):
        self.pop_size = population_size
        self.max_generations = max_generations
        self.total_budget = population_size * max_generations
        self.theta_step = theta_step
        self.seed = seed
        self.rng = np.random.default_rng(seed)

    def search(
        self,
        n_features: int,
        eval_fn: Callable[[np.ndarray], float],
    ) -> Dict[str, Any]:
        """
        Execute QIEA feature search.
        eval_fn: Function taking binary feature mask (np.ndarray of 0s and 1s)
                 and returning validation error (lower is better).
        """
        # 1. Initialize population of Q-bit chromosomes
        population = [
            QBitChromosome(n_features, seed=int(self.rng.integers(1, 1000000)))
            for _ in range(self.pop_size)
        ]

        gbest_mask: Optional[np.ndarray] = None
        gbest_fitness = float("inf")
        eval_count = 0

        convergence_curve: List[float] = []
        entropy_history: List[float] = []
        unique_masks_evaluated: set = set()

        # Initial evaluation (Gen 0)
        p_masks = [chrom.measure() for chrom in population]
        p_scores = []
        for mask in p_masks:
            score = eval_fn(mask)
            eval_count += 1
            p_scores.append(score)
            unique_masks_evaluated.add(tuple(mask.tolist()))

            if score < gbest_fitness:
                gbest_fitness = score
                gbest_mask = mask.copy()

        mean_ent = float(np.mean([chrom.get_shannon_entropy() for chrom in population]))
        convergence_curve.append(gbest_fitness)
        entropy_history.append(mean_ent)

        # Generational loop
        for gen in range(1, self.max_generations):
            # 1. Measurement
            curr_masks = [chrom.measure() for chrom in population]

            # 2. Evaluation
            curr_scores = []
            for i, mask in enumerate(curr_masks):
                score = eval_fn(mask)
                eval_count += 1
                curr_scores.append(score)
                unique_masks_evaluated.add(tuple(mask.tolist()))

                if score < gbest_fitness:
                    gbest_fitness = score
                    gbest_mask = mask.copy()

            # 3. Update via Quantum Rotation Gate
            for i, chrom in enumerate(population):
                is_better = curr_scores[i] < gbest_fitness
                chrom.apply_rotation_gate(
                    current_x=curr_masks[i],
                    best_b=gbest_mask,
                    is_better=is_better,
                    theta_step=self.theta_step,
                )

            mean_ent = float(np.mean([chrom.get_shannon_entropy() for chrom in population]))
            convergence_curve.append(gbest_fitness)
            entropy_history.append(mean_ent)

        # Average selection probabilities across population
        pop_probs = np.mean([chrom.get_selection_probabilities() for chrom in population], axis=0)

        return {
            "algorithm": "QIEA-FS",
            "best_mask": gbest_mask,
            "best_score": gbest_fitness,
            "selected_indices": np.where(gbest_mask == 1)[0].tolist(),
            "n_selected": int(np.sum(gbest_mask)),
            "total_evaluations": eval_count,
            "unique_configurations": len(unique_masks_evaluated),
            "convergence_history": convergence_curve,
            "entropy_history": entropy_history,
            "final_population_probabilities": pop_probs.tolist(),
        }
