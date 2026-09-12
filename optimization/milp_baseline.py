"""
Mixed-Integer Linear Programming (MILP) Baseline for Small Fleet Instances.
Uses PuLP solver for exact comparison against heuristic approximations on small fleets (<= 5 vessels).
"""

from typing import Any, Dict, List
import pulp
import numpy as np


class SmallInstanceMILPBaseline:
    """Exact MILP solver for linear approximation of fleet assignment and speed discretizations."""

    def __init__(self, time_limit_seconds: int = 60):
        self.time_limit = time_limit_seconds

    def solve(
        self,
        vessel_ids: List[str],
        discrete_speeds: List[float],
        fuel_costs: Dict[float, float],
        cargo_capacities: Dict[str, float],
        total_demand: float,
    ) -> Dict[str, Any]:
        """Solve small linearized fleet allocation problem."""
        prob = pulp.LpProblem("Fleet_Assignment_MILP", pulp.LpMinimize)

        # Decision variable: x[v, s] binary indicator of vessel v at speed s
        x = {}
        for v in vessel_ids:
            for s in discrete_speeds:
                x[(v, s)] = pulp.LpVariable(f"x_{v}_{s}", cat=pulp.LpBinary)

        # Objective: minimize fuel/cost
        prob += pulp.lpSum(x[(v, s)] * fuel_costs.get(s, 1000.0) for v in vessel_ids for s in discrete_speeds)

        # Constraint 1: Each vessel assigned at most one speed
        for v in vessel_ids:
            prob += pulp.lpSum(x[(v, s)] for s in discrete_speeds) <= 1

        # Constraint 2: Total cargo served meets demand
        prob += pulp.lpSum(
            x[(v, s)] * cargo_capacities.get(v, 800.0) for v in vessel_ids for s in discrete_speeds
        ) >= total_demand

        solver = pulp.PULP_CBC_CMD(timeLimit=self.time_limit, msg=False)
        status = prob.solve(solver)

        return {
            "status": pulp.LpStatus[status],
            "objective_value": pulp.value(prob.objective),
            "is_optimal": status == pulp.constants.LpStatusOptimal,
        }
