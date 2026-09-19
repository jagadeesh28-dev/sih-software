"""
Common Evaluator for Phase 5 Benchmark.
Wraps Phase 4 Fleet Evaluator ensuring:
1. Strict evaluation budget accounting (counts only calls to evaluate_vector).
2. Independent evaluation for all algorithms (A0-A5, DE, PSO, GA, Random, NSGA-III).
3. Clear separation of hard constraints, soft objectives, and physical metrics.
4. Native Deb's feasibility-first comparison operator.
5. Standardized multi-objective vector extraction.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np

from optimization.fleet_evaluator_phase4 import Phase4FleetEvaluator, Phase4FleetEvaluationResult
from optimization.fleet_heterogeneous import (
    FLEET_VESSELS,
    OPERATIONAL_DEMANDS,
    WEATHER_SCENARIOS,
    DECISION_DIMS_PER_VESSEL,
    DEMAND_KEYS,
    FleetVesselProfile,
)


@dataclass
class EvaluationOutput:
    """Standardized output returned to all optimization algorithms."""
    fitness: float                     # Penalized scalar fitness (for standard/penalty optimizers)
    physical_fitness: float            # True unpenalized operational objective (robust expected loss + risk)
    penalty: float                     # Total penalty magnitude added to fitness
    is_feasible: bool                  # True if zero hard constraint violations
    hard_violations: List[str]         # List of violated hard constraints
    total_constraint_violation: float  # Quantitative constraint violation magnitude (for Deb's comparator)
    objectives: np.ndarray             # Multi-objective vector: [Fuel (t), OPEX ($), GHG (t), Delay (h), Risk ($)]
    evaluation_index: int              # Global 1-based index of this evaluation

    # Operational metrics
    fuel_tonnes: float
    opex_usd: float
    ghg_tonnes: float
    delay_hours: float
    risk_metric: float

    # Decoded decisions
    assigned_demands: Dict[str, str]
    fuel_decisions: Dict[str, str]
    speed_decisions: Dict[str, float]
    shore_decisions: Dict[str, bool]

    raw_result: Phase4FleetEvaluationResult


class CommonFleetEvaluator:
    """
    Unified evaluator interface for all algorithms in Phase 5.
    Every algorithm calls evaluator.evaluate(x) and receives an EvaluationOutput.
    """

    def __init__(
        self,
        base_evaluator: Phase4FleetEvaluator,
        max_budget: Optional[int] = 2500,
    ):
        self.base_evaluator = base_evaluator
        self.max_budget = max_budget
        self.evaluation_count = 0
        self.feasible_evaluations_count = 0

    def reset_budget(self) -> None:
        """Reset evaluation counter before a new run."""
        self.evaluation_count = 0
        self.feasible_evaluations_count = 0

    def get_bounds(self) -> Tuple[np.ndarray, np.ndarray]:
        """Returns lower and upper bounds of decision vector."""
        return self.base_evaluator.get_bounds()

    def evaluate(self, x: np.ndarray) -> EvaluationOutput:
        """
        Evaluates decision vector x. Strictly increments evaluation counter.
        """
        self.evaluation_count += 1
        res: Phase4FleetEvaluationResult = self.base_evaluator.evaluate_vector(x)

        is_f = bool(res.is_feasible)
        if is_f:
            self.feasible_evaluations_count += 1

        # Calculate Deb's constraint violation magnitude
        # If infeasible, sum hard violation penalties + soft violation amounts
        if is_f:
            total_viol = 0.0
        else:
            # Violation magnitude based on hard violation count and penalty values
            total_viol = float(res.total_penalty_value)
            if total_viol <= 0.0:
                total_viol = float(len(res.hard_violations) * 50000.0)

        # Multi-objective vector: [Fuel (t), OPEX ($), WtW GHG (t), Delay (h), CVaR Risk ($)]
        obj_vec = np.array([
            float(res.total_fuel_tonnes),
            float(res.total_opex_usd),
            float(res.total_wtw_ghg_tonnes),
            float(res.total_schedule_delay_hours),
            float(res.uncertainty_risk_metric),
        ], dtype=float)

        return EvaluationOutput(
            fitness=float(res.fitness),
            physical_fitness=float(res.physical_fitness),
            penalty=float(res.total_penalty_value),
            is_feasible=is_f,
            hard_violations=list(res.hard_violations),
            total_constraint_violation=total_viol,
            objectives=obj_vec,
            evaluation_index=self.evaluation_count,
            fuel_tonnes=float(res.total_fuel_tonnes),
            opex_usd=float(res.total_opex_usd),
            ghg_tonnes=float(res.total_wtw_ghg_tonnes),
            delay_hours=float(res.total_schedule_delay_hours),
            risk_metric=float(res.uncertainty_risk_metric),
            assigned_demands=dict(res.assigned_demands),
            fuel_decisions=dict(res.fuel_decisions),
            speed_decisions=dict(res.speed_decisions),
            shore_decisions=dict(res.shore_power_decisions),
            raw_result=res,
        )

    @staticmethod
    def deb_prefers(
        cand1: Union[EvaluationOutput, Dict[str, Any]],
        cand2: Union[EvaluationOutput, Dict[str, Any]],
    ) -> bool:
        """
        Deb's Feasibility-First Tournament Comparator:
        1. Feasible beats infeasible.
        2. Between two feasible solutions: lower objective/fitness wins.
        3. Between two infeasible solutions: lower total constraint violation wins.
        Returns True if cand1 is preferred over cand2, False otherwise.
        """
        f1 = cand1.fitness if isinstance(cand1, EvaluationOutput) else cand1["fitness"]
        is_f1 = cand1.is_feasible if isinstance(cand1, EvaluationOutput) else cand1["is_feasible"]
        v1 = cand1.total_constraint_violation if isinstance(cand1, EvaluationOutput) else cand1.get("total_constraint_violation", 1e9)

        f2 = cand2.fitness if isinstance(cand2, EvaluationOutput) else cand2["fitness"]
        is_f2 = cand2.is_feasible if isinstance(cand2, EvaluationOutput) else cand2["is_feasible"]
        v2 = cand2.total_constraint_violation if isinstance(cand2, EvaluationOutput) else cand2.get("total_constraint_violation", 1e9)

        if is_f1 and is_f2:
            return f1 < f2
        elif is_f1 and not is_f2:
            return True
        elif not is_f1 and is_f2:
            return False
        else:
            # Both infeasible: prefer candidate with lower constraint violation
            if abs(v1 - v2) > 1e-5:
                return v1 < v2
            return f1 < f2
