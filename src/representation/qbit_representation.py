"""
Quantum-Inspired Probabilistic Representations:
1. Two-state Q-bit: |psi> = cos(theta)|0> + sin(theta)|1>, |alpha|^2 + |beta|^2 = 1.
2. Dirichlet-Q Categorical Vector: Multi-state quantum probability amplitude for K fuel/mode choices.
3. Conditional Observation Operator: Exact bijection guaranteeing sum_v d_{v,k} = 1 by construction.
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np


class QBit:
    """
    Standard 2-state Quantum Bit parameterized by phase angle theta.
    Amplitudes: alpha = cos(theta), beta = sin(theta).
    State: |psi> = alpha|0> + beta|1>.
    Probability of state 1: P(1) = |beta|^2 = sin^2(theta).
    """

    def __init__(self, theta: Optional[float] = None):
        if theta is None:
            self.theta = np.pi / 4.0  # Equal superposition: |alpha|^2 = |beta|^2 = 0.5
        else:
            self.theta = float(theta)

    @property
    def alpha(self) -> float:
        return float(np.cos(self.theta))

    @property
    def beta(self) -> float:
        return float(np.sin(self.theta))

    @property
    def prob_one(self) -> float:
        return float(np.sin(self.theta) ** 2)

    def measure(self, rng: Optional[np.random.Generator] = None) -> int:
        """Projective measurement in computational basis {|0>, |1>}."""
        u = rng.uniform(0.0, 1.0) if rng is not None else np.random.uniform(0.0, 1.0)
        return 1 if u < self.prob_one else 0

    def rotate(self, delta_theta: float) -> None:
        """Unitary quantum rotation gate R(delta_theta)."""
        self.theta = (self.theta + delta_theta) % (2.0 * np.pi)

    def rotate_toward(self, target_bit: int, step_size: float = 0.05 * np.pi) -> None:
        """
        Updates theta toward target_bit (0 or 1) using standard QIEA rotation lookup.
        If target is 1, increase prob_one (move theta toward pi/2).
        If target is 0, decrease prob_one (move theta toward 0).
        """
        current_p1 = self.prob_one
        if target_bit == 1 and current_p1 < 0.99:
            self.rotate(step_size)
        elif target_bit == 0 and current_p1 > 0.01:
            self.rotate(-step_size)


class DirichletQVector:
    """
    Categorical Quantum Probability Vector for multi-state decisions (e.g. K fuel types).
    q = [q_0, q_1, ..., q_{K-1}], sum(q_k) = 1, q_k >= epsilon.
    """

    def __init__(self, n_categories: int, epsilon: float = 0.01):
        self.n_categories = n_categories
        self.epsilon = epsilon
        # Initialize to uniform superposition
        self.probs = np.full(n_categories, 1.0 / n_categories, dtype=float)

    def measure(self, allowed_mask: Optional[np.ndarray] = None, rng: Optional[np.random.Generator] = None) -> int:
        """Sample a category according to probability amplitudes."""
        p = self.probs.copy()
        if allowed_mask is not None:
            p = p * allowed_mask
            if np.sum(p) < 1e-9:
                p = allowed_mask.astype(float)
        p_norm = p / np.sum(p)
        if rng is not None:
            return int(rng.choice(self.n_categories, p=p_norm))
        return int(np.random.choice(self.n_categories, p=p_norm))

    def update(self, best_category: int, eta: float = 0.05, lambda_reg: float = 0.01) -> None:
        """
        Dirichlet-Q rotation update: increase amplitude of best category,
        apply regularization to prevent premature collapse.
        """
        q_new = self.probs.copy()
        q_new[best_category] += eta
        q_new -= lambda_reg * self.probs
        q_new = np.maximum(q_new, self.epsilon)
        self.probs = q_new / np.sum(q_new)


class ConditionalDemandObservation:
    """
    Quantum-inspired conditional observation operator for combinatorial fleet assignment.
    Guarantees sum_v d_{v,k} = 1 for all mandatory demands k by construction.
    """

    def __init__(self, n_vessels: int = 3, n_demands: int = 3):
        self.n_vessels = n_vessels
        self.n_demands = n_demands
        # Q-amplitude matrix: theta[v, k] initialized to equal superposition
        self.thetas = np.full((n_vessels, n_demands), np.pi / 4.0, dtype=float)

    def observe(self, compatibility_matrix: np.ndarray, rng: Optional[np.random.Generator] = None) -> np.ndarray:
        """
        Observes a valid assignment matrix D of shape (n_vessels, n_demands).
        compatibility_matrix[v, k] is 1 if vessel v can fulfill demand k, 0 otherwise.
        Returns:
            assignment_indices: array of length n_vessels, where entry v is assigned demand index (1-based), or 0.
        """
        # P[v, k] = sin^2(theta[v, k])
        probs = np.sin(self.thetas) ** 2
        assigned_vessels = set()
        vessel_assignments = np.zeros(self.n_vessels, dtype=int)

        # For each demand, select a compatible available vessel
        for k in range(self.n_demands):
            p_k = probs[:, k].copy()
            # Mask out incompatible vessels and already assigned vessels
            mask = compatibility_matrix[:, k].copy()
            for v_used in assigned_vessels:
                mask[v_used] = 0.0

            p_k = p_k * mask
            if np.sum(p_k) < 1e-9:
                # Fallback to any unassigned compatible vessel
                p_k = mask.astype(float)
            if np.sum(p_k) < 1e-9:
                # If completely constrained, allow any unassigned vessel
                unassigned_mask = np.ones(self.n_vessels)
                for v_used in assigned_vessels:
                    unassigned_mask[v_used] = 0.0
                p_k = unassigned_mask

            if np.sum(p_k) > 0:
                p_norm = p_k / np.sum(p_k)
                if rng is not None:
                    chosen_v = int(rng.choice(self.n_vessels, p=p_norm))
                else:
                    chosen_v = int(np.random.choice(self.n_vessels, p=p_norm))
                vessel_assignments[chosen_v] = k + 1  # 1-based demand index
                assigned_vessels.add(chosen_v)

        return vessel_assignments

    def update_toward(self, best_assignments: np.ndarray, step_size: float = 0.05 * np.pi) -> None:
        """
        Rotates Q-amplitudes toward best known assignment.
        best_assignments: array of length n_vessels with demand index (1-based) or 0.
        """
        for v in range(self.n_vessels):
            target_k_1based = best_assignments[v]
            for k in range(self.n_demands):
                if target_k_1based == (k + 1):
                    # Rotate toward 1
                    self.thetas[v, k] = min(self.thetas[v, k] + step_size, 0.48 * np.pi)
                else:
                    # Rotate toward 0
                    self.thetas[v, k] = max(self.thetas[v, k] - step_size, 0.02 * np.pi)
