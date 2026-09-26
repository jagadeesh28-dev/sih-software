"""
Classical Multi-Objective Baseline: NSGA-III (pymoo 0.6).

Minimises [Fuel (t), OPEX ($), WtW GHG (t)] with Das-Dennis reference directions and
constraint-domination on one inequality constraint g = total penalty (hard + soft) <= 0, so a
candidate is feasible in the multi-objective sense only if it is hard-feasible AND penalty-free
(on time, actual speed within the vessel band, inside the model domain).

The previous implementation bred every generation from the initial random population and never
applied non-dominated sorting or survivor selection (random search, mislabelled as NSGA-III).

`best_output` keeps the scalar Deb-preferred solution so the algorithm can still be benchmarked
against DE / GA / QPSO on penalized fitness; `pareto_archive` holds every feasible, penalty-free
evaluation, which is what the operator Pareto front is built from.
"""

import time
from typing import List, Optional, Tuple

import numpy as np
from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.core.problem import ElementwiseProblem
from pymoo.optimize import minimize
from pymoo.util.ref_dirs import get_reference_directions

from src.algorithms.base import BaseFleetOptimizer, OptimizationResult
from src.benchmark.metrics import compute_2d_hypervolume, is_pareto_efficient
from src.evaluator.common_evaluator import CommonFleetEvaluator, EvaluationOutput

N_OBJ = 3  # fuel, OPEX, WtW GHG


def is_pareto_feasible(out: EvaluationOutput) -> bool:
    """Hard-feasible and free of every soft penalty (speed band, schedule delay)."""
    return bool(out.is_feasible and out.penalty <= 0.0)


class _FleetProblem(ElementwiseProblem):
    def __init__(self, evaluator: CommonFleetEvaluator, xl: np.ndarray, xu: np.ndarray, on_eval):
        super().__init__(n_var=len(xl), n_obj=N_OBJ, n_ieq_constr=1, xl=xl, xu=xu)
        self.evaluator = evaluator
        self.on_eval = on_eval

    def _evaluate(self, x, out, *args, **kwargs):
        res = self.evaluator.evaluate(np.asarray(x, dtype=float))
        self.on_eval(np.asarray(x, dtype=float), res)
        out["F"] = res.objectives[:N_OBJ]
        out["G"] = [res.penalty]


def structured_initial_population(vessels, n: int, xl: np.ndarray, xu: np.ndarray, rng) -> np.ndarray:
    """
    Initial vectors whose categorical genes are individually valid: each vessel gets a demand it is
    compatible with, a compatible fuel and an under-way mode (transit / maneuvering); speed, cargo and
    shore power are uniform in their bounds. Validity is judged by the evaluator's own decoder, and
    fleet-level rules (exactly-once demands, deadlines, domain) are NOT pre-satisfied: every candidate
    is still scored by the full evaluator under constraint-domination.
    """
    from optimization.fleet_heterogeneous import DECISION_DIMS_PER_VESSEL as D, DEMAND_KEYS, decode_fleet_vector
    from optimization.variables import FUEL_MAP, REV_MODE_MAP

    options = []
    for i, v in enumerate(vessels):
        fuels = [k for k, f in FUEL_MAP.items() if f in v.compatible_fuels]
        probe = lambda dem: np.array([dem, 0.0, v.min_speed_knots, fuels[0], REV_MODE_MAP["transit"], 0.0])
        demands = [d for d in range(1, len(DEMAND_KEYS)) if decode_fleet_vector(probe(d), [v])[0].is_compatible]
        options.append((demands or [0], fuels))
    X = rng.uniform(xl, xu, size=(n, len(xl)))
    for i, (demands, fuels) in enumerate(options):
        X[:, i * D + 0] = rng.choice(demands, size=n)
        X[:, i * D + 3] = rng.choice(fuels, size=n)
        X[:, i * D + 4] = rng.choice([REV_MODE_MAP["transit"], REV_MODE_MAP["maneuvering"]], size=n)
    return X


class NSGA3Optimizer(BaseFleetOptimizer):
    """NSGA-III with reference directions and constraint-domination (pymoo)."""

    def __init__(
        self,
        seed: int = 42,
        population_size: int = 50,
        max_generations: int = 50,
        n_partitions: int = 8,
        ref_point: Optional[np.ndarray] = None,
        init: str = "random",
    ):
        super().__init__(name="NSGA3", seed=seed)
        self.population_size = population_size
        self.max_generations = max_generations
        self.n_partitions = n_partitions  # 45 reference directions for 3 objectives
        # "random": uniform in the box (equal footing with DE/GA/QPSO in the benchmark);
        # "structured": structured_initial_population (used for the operator Pareto search).
        self.init = init
        self.ref_point = ref_point if ref_point is not None else np.array([500.0, 500000.0])
        self.pareto_archive: List[Tuple[np.ndarray, np.ndarray, EvaluationOutput]] = []

    def optimize(
        self,
        evaluator: CommonFleetEvaluator,
        xl: np.ndarray,
        xu: np.ndarray,
        budget: int = 2500,
    ) -> OptimizationResult:
        t0 = time.perf_counter()
        state = {"best": None, "best_x": None, "feas": 0, "first_eval": -1}
        archive: List[Tuple[np.ndarray, np.ndarray, EvaluationOutput]] = []
        unique: set = set()
        conv: List[float] = []
        evals: List[int] = []

        def on_eval(x: np.ndarray, out: EvaluationOutput) -> None:
            unique.add(tuple(np.round(x, 3)))
            if out.is_feasible:
                state["feas"] += 1
                if state["first_eval"] == -1:
                    state["first_eval"] = out.evaluation_index
            if is_pareto_feasible(out):
                archive.append((out.objectives[:N_OBJ].copy(), x.copy(), out))
            if state["best"] is None or CommonFleetEvaluator.deb_prefers(out, state["best"]):
                state["best"], state["best_x"] = out, x.copy()
            if evaluator.evaluation_count % self.population_size == 0:
                conv.append(state["best"].fitness)
                evals.append(evaluator.evaluation_count)

        ref_dirs = get_reference_directions("das-dennis", N_OBJ, n_partitions=self.n_partitions)
        kwargs = {}
        if self.init == "structured":
            vessels = evaluator.base_evaluator.vessels
            kwargs["sampling"] = structured_initial_population(
                vessels, self.population_size, np.asarray(xl, float), np.asarray(xu, float), np.random.default_rng(self.seed))
        algorithm = NSGA3(ref_dirs=ref_dirs, pop_size=self.population_size, eliminate_duplicates=True, **kwargs)
        problem = _FleetProblem(evaluator, np.asarray(xl, float), np.asarray(xu, float), on_eval)
        n_gen = max(1, min(self.max_generations, budget // self.population_size))
        minimize(problem, algorithm, ("n_gen", n_gen), seed=self.seed, verbose=False)
        t1 = time.perf_counter()

        self.pareto_archive = archive
        best: Optional[EvaluationOutput] = state["best"]
        if archive:
            costs = np.array([a[0] for a in archive])
            front = costs[is_pareto_efficient(costs)]
            archive_size = len(np.unique(front, axis=0))
            hv = compute_2d_hypervolume(front[:, :2], self.ref_point)
        else:
            archive_size, hv = 0, 0.0

        return OptimizationResult(
            algorithm="NSGA3",
            seed=self.seed,
            run_id=f"NSGA3_seed_{self.seed}",
            runtime_seconds=round(t1 - t0, 4),
            objective_evaluations=evaluator.evaluation_count,
            iterations=n_gen,
            best_x=state["best_x"],
            best_fitness=float(best.fitness) if best else float("inf"),
            best_physical_objective=float(best.physical_fitness) if best else float("inf"),
            best_penalty=float(best.penalty) if best else 0.0,
            feasible_at_end=bool(best.is_feasible) if best else False,
            best_output=best,
            first_feasible_evaluation=state["first_eval"],
            first_feasible_iteration=-1 if state["first_eval"] == -1 else (state["first_eval"] - 1) // self.population_size,
            number_of_feasible_evaluations=state["feas"],
            candidate_level_feasibility_rate=float(state["feas"] / max(1, evaluator.evaluation_count)),
            constraint_violation_total=float(best.total_constraint_violation) if best else 0.0,
            hard_violations=list(best.hard_violations) if best else [],
            convergence_trajectory=conv,
            eval_trajectory=evals,
            unique_solution_count=len(unique),
            pareto_archive_size=archive_size,
            pareto_hypervolume=round(hv, 2),
            assigned_demands=dict(best.assigned_demands) if best else {},
            fuel_decisions=dict(best.fuel_decisions) if best else {},
            speed_decisions=dict(best.speed_decisions) if best else {},
        )
