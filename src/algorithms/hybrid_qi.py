"""
A4 & A5: Heterogeneous Quantum-Inspired Fleet Optimization Engines.

A4: Heterogeneous Q-bit + QPSO (Penalty-Only Selection)
- Q-bit / QIEA probabilistic representation for discrete/binary/categorical variables
- QPSO continuous delta-potential well optimizer for speed and cargo
- Standard scalar fitness comparison (NO Deb rules, NO repair)
- Measures the standalone contribution of heterogeneous QI representation

A5: Complete Hybrid QI Framework (Hybrid QI-HFO)
- Q-bit / QIEA discrete search
- QPSO continuous search
- Principled Decoder / Repair
- Deb's Feasibility-First Selection
- Multi-Objective Pareto Archive (Fuel, OPEX, GHG, Delay, CVaR Risk)
- Hypervolume tracking
"""

import time
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from src.algorithms.base import BaseFleetOptimizer, OptimizationResult
from src.evaluator.common_evaluator import CommonFleetEvaluator, EvaluationOutput
from src.representation.qbit_representation import QBit, DirichletQVector, ConditionalDemandObservation
from src.representation.repair import FleetSolutionRepairer
from src.representation.variable_types import get_heterogeneous_fleet_partitions, VariableType
from src.benchmark.metrics import is_pareto_efficient, compute_2d_hypervolume


class A4HeterogeneousQIOptimizer(BaseFleetOptimizer):
    """A4: Heterogeneous Q-bit + QPSO Representation with Penalty-Only Selection."""

    def __init__(
        self,
        seed: int = 42,
        n_particles: int = 50,
        max_iterations: int = 50,
        beta_start: float = 1.0,
        beta_end: float = 0.5,
        rotation_step: float = 0.05 * np.pi,
    ):
        super().__init__(name="A4_Heterogeneous_QBit_QPSO", seed=seed)
        self.n_particles = n_particles
        self.max_iterations = max_iterations
        self.beta_start = beta_start
        self.beta_end = beta_end
        self.rotation_step = rotation_step
        self.n_vessels = 3

    def optimize(
        self,
        evaluator: CommonFleetEvaluator,
        xl: np.ndarray,
        xu: np.ndarray,
        budget: int = 2500,
    ) -> OptimizationResult:
        t0 = time.perf_counter()
        rng = np.random.default_rng(self.seed)
        np.random.seed(self.seed)

        dim = len(xl)
        eval_cap = budget

        # 1. Initialize Quantum Representations per individual
        # Binary shore power Q-bits: (n_particles, n_vessels)
        shore_qbits = [[QBit() for _ in range(self.n_vessels)] for _ in range(self.n_particles)]
        # Dirichlet-Q vectors for fuel (5 options): (n_particles, n_vessels)
        fuel_qvectors = [[DirichletQVector(n_categories=5) for _ in range(self.n_vessels)] for _ in range(self.n_particles)]
        # Dirichlet-Q vectors for operating mode (4 options)
        mode_qvectors = [[DirichletQVector(n_categories=4) for _ in range(self.n_vessels)] for _ in range(self.n_particles)]
        # Conditional demand observation operators
        demand_q_obs = [ConditionalDemandObservation(n_vessels=self.n_vessels, n_demands=3) for _ in range(self.n_particles)]

        # Continuous speed & cargo positions
        X = np.zeros((self.n_particles, dim), dtype=float)
        # Compatibility matrix for demands (Poseidon:Dem-A, Triton:Dem-B, Ceto:Dem-C)
        comp_matrix = np.array([
            [1.0, 0.0, 0.0],  # Poseidon
            [0.0, 1.0, 0.0],  # Triton
            [0.0, 0.0, 1.0],  # Ceto
        ])

        # Sample initial positions
        for i in range(self.n_particles):
            # Observe demands
            dem_assigns = demand_q_obs[i].observe(comp_matrix, rng=rng)
            for v in range(self.n_vessels):
                v_offset = v * 6
                X[i, v_offset] = float(dem_assigns[v])
                X[i, v_offset + 1] = float(rng.uniform(xl[v_offset + 1], xu[v_offset + 1]))  # Cargo
                X[i, v_offset + 2] = float(rng.uniform(xl[v_offset + 2], xu[v_offset + 2]))  # Speed
                X[i, v_offset + 3] = float(fuel_qvectors[i][v].measure(rng=rng))             # Fuel
                X[i, v_offset + 4] = float(mode_qvectors[i][v].measure(rng=rng))             # Mode
                X[i, v_offset + 5] = float(shore_qbits[i][v].measure(rng=rng))               # Shore

        P = X.copy()
        P_scores = np.full(self.n_particles, np.inf)
        P_outputs: List[Optional[EvaluationOutput]] = [None] * self.n_particles

        first_feas_eval = -1
        first_feas_iter = -1
        feas_count = 0
        convergence_traj: List[float] = []
        eval_traj: List[int] = []
        diversity_traj: List[float] = []
        entropy_traj: List[float] = []
        unique_solutions: set = set()

        for i in range(self.n_particles):
            if evaluator.evaluation_count >= eval_cap:
                break
            out = evaluator.evaluate(X[i])
            P_scores[i] = out.fitness
            P_outputs[i] = out
            unique_solutions.add(tuple(np.round(X[i], 3)))

            if out.is_feasible:
                feas_count += 1
                if first_feas_eval == -1:
                    first_feas_eval = out.evaluation_index
                    first_feas_iter = 0

        gbest_idx = int(np.argmin(P_scores))
        gbest = P[gbest_idx].copy()
        gbest_score = float(P_scores[gbest_idx])
        gbest_output = P_outputs[gbest_idx]

        convergence_traj.append(gbest_score)
        eval_traj.append(evaluator.evaluation_count)

        # 2. Main Generation Loop
        t = 0
        while t < self.max_iterations and evaluator.evaluation_count < eval_cap:
            beta = self.beta_start - (self.beta_start - self.beta_end) * (t / max(1, self.max_iterations))
            mbest = np.mean(P, axis=0)

            # Diagnostics
            diversity_traj.append(float(np.mean(np.std(X, axis=0))))
            cat_dims = [0, 3, 4, 6, 9, 10, 12, 15, 16]
            cat_vals = np.round(X[:, cat_dims]).astype(int)
            entropies = []
            for col in range(len(cat_dims)):
                _, counts = np.unique(cat_vals[:, col], return_counts=True)
                p_c = counts / np.sum(counts)
                entropies.append(-float(np.sum(p_c * np.log2(p_c + 1e-12))))
            entropy_traj.append(float(np.mean(entropies)))

            for i in range(self.n_particles):
                if evaluator.evaluation_count >= eval_cap:
                    break

                # 2A. Q-bit Observations for Discrete Variables
                dem_assigns = demand_q_obs[i].observe(comp_matrix, rng=rng)
                for v in range(self.n_vessels):
                    v_offset = v * 6
                    X[i, v_offset] = float(dem_assigns[v])
                    X[i, v_offset + 3] = float(fuel_qvectors[i][v].measure(rng=rng))
                    X[i, v_offset + 4] = float(mode_qvectors[i][v].measure(rng=rng))
                    X[i, v_offset + 5] = float(shore_qbits[i][v].measure(rng=rng))

                    # 2B. QPSO Update for Continuous Dimensions (Speed & Cargo)
                    for d_cont in [v_offset + 1, v_offset + 2]:
                        phi = rng.uniform(0.0, 1.0)
                        p_local = phi * P[i, d_cont] + (1.0 - phi) * gbest[d_cont]
                        u = max(1e-10, rng.uniform(0.0, 1.0))
                        sign = 1.0 if rng.uniform(0.0, 1.0) > 0.5 else -1.0
                        X[i, d_cont] = p_local + sign * beta * abs(mbest[d_cont] - X[i, d_cont]) * np.log(1.0 / u)
                        X[i, d_cont] = np.clip(X[i, d_cont], xl[d_cont], xu[d_cont])

                out = evaluator.evaluate(X[i])
                score = out.fitness
                unique_solutions.add(tuple(np.round(X[i], 3)))

                if out.is_feasible:
                    feas_count += 1
                    if first_feas_eval == -1:
                        first_feas_eval = out.evaluation_index
                        first_feas_iter = t + 1

                # Standard scalar fitness comparison
                if score < P_scores[i]:
                    P[i] = X[i].copy()
                    P_scores[i] = score
                    P_outputs[i] = out

                    # Rotate Q-bits toward better solution
                    target_dems = np.array([int(round(X[i, v * 6])) for v in range(self.n_vessels)])
                    demand_q_obs[i].update_toward(target_dems, step_size=self.rotation_step)
                    for v in range(self.n_vessels):
                        fuel_qvectors[i][v].update(int(round(X[i, v * 6 + 3])))
                        shore_qbits[i][v].rotate_toward(int(round(X[i, v * 6 + 5])), step_size=self.rotation_step)

                    if score < gbest_score:
                        gbest = X[i].copy()
                        gbest_score = score
                        gbest_output = out

            convergence_traj.append(gbest_score)
            eval_traj.append(evaluator.evaluation_count)
            t += 1

        t1 = time.perf_counter()

        return OptimizationResult(
            algorithm="A4_Heterogeneous_QBit_QPSO",
            seed=self.seed,
            run_id=f"A4_seed_{self.seed}",
            runtime_seconds=round(t1 - t0, 4),
            objective_evaluations=evaluator.evaluation_count,
            iterations=t,
            best_x=gbest,
            best_fitness=float(gbest_score),
            best_physical_objective=float(gbest_output.physical_fitness) if gbest_output else float(gbest_score),
            best_penalty=float(gbest_output.penalty) if gbest_output else 0.0,
            feasible_at_end=bool(gbest_output.is_feasible) if gbest_output else False,
            best_output=gbest_output,
            first_feasible_evaluation=first_feas_eval,
            first_feasible_iteration=first_feas_iter,
            number_of_feasible_evaluations=feas_count,
            candidate_level_feasibility_rate=float(feas_count / max(1, evaluator.evaluation_count)),
            constraint_violation_total=float(gbest_output.total_constraint_violation) if gbest_output else 0.0,
            hard_violations=list(gbest_output.hard_violations) if gbest_output else [],
            convergence_trajectory=convergence_traj,
            eval_trajectory=eval_traj,
            population_diversity=diversity_traj,
            categorical_entropy=entropy_traj,
            repair_count=0,
            repair_rate=0.0,
            unique_solution_count=len(unique_solutions),
            assigned_demands=dict(gbest_output.assigned_demands) if gbest_output else {},
            fuel_decisions=dict(gbest_output.fuel_decisions) if gbest_output else {},
            speed_decisions=dict(gbest_output.speed_decisions) if gbest_output else {},
        )


class A5CompleteHybridQIOptimizer(BaseFleetOptimizer):
    """
    A5: Complete Hybrid QI Framework (Hybrid QI-HFO).
    Integrates:
    1. Q-bit / QIEA probabilistic discrete representation (Dirichlet-Q & Conditional observation)
    2. QPSO continuous speed and cargo optimization
    3. Principled Decoder & Repair operator
    4. Deb's Feasibility-First Selection rule
    5. Multi-Objective Pareto Archive & Hypervolume computation
    6. Uncertainty-aware CVaR evaluation
    """

    def __init__(
        self,
        seed: int = 42,
        n_particles: int = 50,
        max_iterations: int = 50,
        beta_start: float = 1.0,
        beta_end: float = 0.5,
        rotation_step: float = 0.05 * np.pi,
        pareto_ref_point: Optional[np.ndarray] = None,
    ):
        super().__init__(name="A5_Complete_Hybrid_QI", seed=seed)
        self.n_particles = n_particles
        self.max_iterations = max_iterations
        self.beta_start = beta_start
        self.beta_end = beta_end
        self.rotation_step = rotation_step
        self.repairer = FleetSolutionRepairer()
        self.n_vessels = 3
        # Reference point for Fuel (t) vs OPEX ($)
        self.ref_point = pareto_ref_point if pareto_ref_point is not None else np.array([500.0, 500000.0])

    def optimize(
        self,
        evaluator: CommonFleetEvaluator,
        xl: np.ndarray,
        xu: np.ndarray,
        budget: int = 2500,
    ) -> OptimizationResult:
        t0 = time.perf_counter()
        rng = np.random.default_rng(self.seed)
        np.random.seed(self.seed)

        dim = len(xl)
        eval_cap = budget

        # 1. Quantum Representations
        shore_qbits = [[QBit() for _ in range(self.n_vessels)] for _ in range(self.n_particles)]
        fuel_qvectors = [[DirichletQVector(n_categories=5) for _ in range(self.n_vessels)] for _ in range(self.n_particles)]
        mode_qvectors = [[DirichletQVector(n_categories=4) for _ in range(self.n_vessels)] for _ in range(self.n_particles)]
        demand_q_obs = [ConditionalDemandObservation(n_vessels=self.n_vessels, n_demands=3) for _ in range(self.n_particles)]

        comp_matrix = np.array([
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ])

        X = np.zeros((self.n_particles, dim), dtype=float)

        # External Pareto Archive: stores (objectives, candidate_x, EvaluationOutput)
        pareto_archive: List[Tuple[np.ndarray, np.ndarray, EvaluationOutput]] = []

        # Sample initial population
        for i in range(self.n_particles):
            dem_assigns = demand_q_obs[i].observe(comp_matrix, rng=rng)
            for v in range(self.n_vessels):
                v_offset = v * 6
                X[i, v_offset] = float(dem_assigns[v])
                X[i, v_offset + 1] = float(rng.uniform(xl[v_offset + 1], xu[v_offset + 1]))
                X[i, v_offset + 2] = float(rng.uniform(xl[v_offset + 2], xu[v_offset + 2]))
                X[i, v_offset + 3] = float(fuel_qvectors[i][v].measure(rng=rng))
                X[i, v_offset + 4] = float(mode_qvectors[i][v].measure(rng=rng))
                X[i, v_offset + 5] = float(shore_qbits[i][v].measure(rng=rng))

            # Apply principled repair before evaluation
            repaired_x, _, _ = self.repairer.repair_vector(X[i])
            X[i] = repaired_x

        P = X.copy()
        P_outputs: List[Optional[EvaluationOutput]] = [None] * self.n_particles

        first_feas_eval = -1
        first_feas_iter = -1
        feas_count = 0
        convergence_traj: List[float] = []
        eval_traj: List[int] = []
        diversity_traj: List[float] = []
        entropy_traj: List[float] = []
        unique_solutions: set = set()

        for i in range(self.n_particles):
            if evaluator.evaluation_count >= eval_cap:
                break
            out = evaluator.evaluate(X[i])
            P_outputs[i] = out
            unique_solutions.add(tuple(np.round(X[i], 3)))

            if out.is_feasible:
                feas_count += 1
                if first_feas_eval == -1:
                    first_feas_eval = out.evaluation_index
                    first_feas_iter = 0
                if out.penalty <= 0.0:  # penalty-free only (speed band, schedule)
                    pareto_archive.append((out.objectives[:2].copy(), X[i].copy(), out))

        # Initial gbest via Deb's selection
        gbest_idx = 0
        for i in range(1, self.n_particles):
            if P_outputs[i] is not None and CommonFleetEvaluator.deb_prefers(P_outputs[i], P_outputs[gbest_idx]):
                gbest_idx = i

        gbest = P[gbest_idx].copy()
        gbest_output = P_outputs[gbest_idx]
        gbest_score = gbest_output.fitness if gbest_output else np.inf

        convergence_traj.append(gbest_score)
        eval_traj.append(evaluator.evaluation_count)

        # 2. Main Generation Loop
        t = 0
        while t < self.max_iterations and evaluator.evaluation_count < eval_cap:
            beta = self.beta_start - (self.beta_start - self.beta_end) * (t / max(1, self.max_iterations))
            mbest = np.mean(P, axis=0)

            # Diagnostics
            diversity_traj.append(float(np.mean(np.std(X, axis=0))))
            cat_dims = [0, 3, 4, 6, 9, 10, 12, 15, 16]
            cat_vals = np.round(X[:, cat_dims]).astype(int)
            entropies = []
            for col in range(len(cat_dims)):
                _, counts = np.unique(cat_vals[:, col], return_counts=True)
                p_c = counts / np.sum(counts)
                entropies.append(-float(np.sum(p_c * np.log2(p_c + 1e-12))))
            entropy_traj.append(float(np.mean(entropies)))

            for i in range(self.n_particles):
                if evaluator.evaluation_count >= eval_cap:
                    break

                # 2A. Quantum Observation for Discrete Dimensions
                dem_assigns = demand_q_obs[i].observe(comp_matrix, rng=rng)
                for v in range(self.n_vessels):
                    v_offset = v * 6
                    X[i, v_offset] = float(dem_assigns[v])
                    X[i, v_offset + 3] = float(fuel_qvectors[i][v].measure(rng=rng))
                    X[i, v_offset + 4] = float(mode_qvectors[i][v].measure(rng=rng))
                    X[i, v_offset + 5] = float(shore_qbits[i][v].measure(rng=rng))

                    # 2B. QPSO Delta-Well Update for Speed & Cargo
                    for d_cont in [v_offset + 1, v_offset + 2]:
                        phi = rng.uniform(0.0, 1.0)
                        p_local = phi * P[i, d_cont] + (1.0 - phi) * gbest[d_cont]
                        u = max(1e-10, rng.uniform(0.0, 1.0))
                        sign = 1.0 if rng.uniform(0.0, 1.0) > 0.5 else -1.0
                        X[i, d_cont] = p_local + sign * beta * abs(mbest[d_cont] - X[i, d_cont]) * np.log(1.0 / u)
                        X[i, d_cont] = np.clip(X[i, d_cont], xl[d_cont], xu[d_cont])

                # 2C. Principled Repair
                repaired_x, was_rep, _ = self.repairer.repair_vector(X[i])
                X[i] = repaired_x

                out = evaluator.evaluate(X[i])
                unique_solutions.add(tuple(np.round(X[i], 3)))

                if out.is_feasible:
                    feas_count += 1
                    if first_feas_eval == -1:
                        first_feas_eval = out.evaluation_index
                        first_feas_iter = t + 1
                    if out.penalty <= 0.0:  # penalty-free only (speed band, schedule)
                        pareto_archive.append((out.objectives[:2].copy(), X[i].copy(), out))

                # 2D. Deb's Feasibility-First Selection for pbest and gbest
                if CommonFleetEvaluator.deb_prefers(out, P_outputs[i]):
                    P[i] = X[i].copy()
                    P_outputs[i] = out

                    # Rotate quantum amplitudes toward improved personal best
                    target_dems = np.array([int(round(X[i, v * 6])) for v in range(self.n_vessels)])
                    demand_q_obs[i].update_toward(target_dems, step_size=self.rotation_step)
                    for v in range(self.n_vessels):
                        fuel_qvectors[i][v].update(int(round(X[i, v * 6 + 3])))
                        shore_qbits[i][v].rotate_toward(int(round(X[i, v * 6 + 5])), step_size=self.rotation_step)

                    if CommonFleetEvaluator.deb_prefers(out, gbest_output):
                        gbest = X[i].copy()
                        gbest_output = out
                        gbest_score = out.fitness

            convergence_traj.append(gbest_score)
            eval_traj.append(evaluator.evaluation_count)
            t += 1

        t1 = time.perf_counter()

        # Prune Pareto archive to non-dominated points
        if len(pareto_archive) > 0:
            archive_costs = np.array([item[0] for item in pareto_archive])
            eff_mask = is_pareto_efficient(archive_costs)
            pareto_pts = archive_costs[eff_mask]
            archive_size = len(pareto_pts)
            hv = compute_2d_hypervolume(pareto_pts, self.ref_point)
        else:
            archive_size = 0
            hv = 0.0

        return OptimizationResult(
            algorithm="A5_Complete_Hybrid_QI",
            seed=self.seed,
            run_id=f"A5_seed_{self.seed}",
            runtime_seconds=round(t1 - t0, 4),
            objective_evaluations=evaluator.evaluation_count,
            iterations=t,
            best_x=gbest,
            best_fitness=float(gbest_output.fitness) if gbest_output else float(gbest_score),
            best_physical_objective=float(gbest_output.physical_fitness) if gbest_output else float(gbest_score),
            best_penalty=float(gbest_output.penalty) if gbest_output else 0.0,
            feasible_at_end=bool(gbest_output.is_feasible) if gbest_output else False,
            best_output=gbest_output,
            first_feasible_evaluation=first_feas_eval,
            first_feasible_iteration=first_feas_iter,
            number_of_feasible_evaluations=feas_count,
            candidate_level_feasibility_rate=float(feas_count / max(1, evaluator.evaluation_count)),
            constraint_violation_total=float(gbest_output.total_constraint_violation) if gbest_output else 0.0,
            hard_violations=list(gbest_output.hard_violations) if gbest_output else [],
            convergence_trajectory=convergence_traj,
            eval_trajectory=eval_traj,
            population_diversity=diversity_traj,
            categorical_entropy=entropy_traj,
            repair_count=self.repairer.total_repairs_count,
            repair_rate=self.repairer.get_repair_rate(),
            unique_solution_count=len(unique_solutions),
            pareto_archive_size=archive_size,
            pareto_hypervolume=round(hv, 2),
            assigned_demands=dict(gbest_output.assigned_demands) if gbest_output else {},
            fuel_decisions=dict(gbest_output.fuel_decisions) if gbest_output else {},
            speed_decisions=dict(gbest_output.speed_decisions) if gbest_output else {},
        )
