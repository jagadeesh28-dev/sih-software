"""
Constraint Repair and Boundary Projection Operator.
Implements the repair hierarchy: 1. repair -> 2. projection -> 3. penalty.
"""

from typing import Dict, List, Any
import numpy as np
from .variables import SolutionChromosome


class SolutionRepairOperator:
    """Repairs infeasible continuous and discrete decision variables."""

    def __init__(
        self,
        min_speed_knots: float = 10.0,
        max_speed_knots: float = 20.0,
        max_vessel_capacity_teu: float = 1000.0,
        total_cargo_demand_teu: float = 850.0,
    ):
        self.min_speed = min_speed_knots
        self.max_speed = max_speed_knots
        self.max_capacity = max_vessel_capacity_teu
        self.demand = total_cargo_demand_teu

    def repair_chromosome(self, chrom: SolutionChromosome) -> SolutionChromosome:
        """
        1. Projects speeds to allowable physical limits.
        2. Normalizes / scales cargo allocations to meet total cargo demand without exceeding vessel capacity.
        """
        repaired = chrom

        # 1. Speed projection
        for a in repaired.assignments:
            a.speed_knots = float(np.clip(a.speed_knots, self.min_speed, self.max_speed))
            a.cargo_allocation_teu = float(np.clip(a.cargo_allocation_teu, 0.0, self.max_capacity))

        # 2. Demand reconciliation
        current_total = sum(a.cargo_allocation_teu for a in repaired.assignments)
        if current_total > 0 and abs(current_total - self.demand) > 1e-3:
            scale = self.demand / current_total
            for a in repaired.assignments:
                a.cargo_allocation_teu = min(self.max_capacity, a.cargo_allocation_teu * scale)

        return repaired
