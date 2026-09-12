"""
Solution Chromosome Representation for Mixed-Variable Fleet Optimization.
Encodes discrete (assignments, fuel types, shore power) and continuous (speeds, cargo allocations) decisions.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any
import numpy as np


@dataclass
class VesselAssignmentDecision:
    """Decisions for an individual vessel on an assigned voyage leg."""
    vessel_id: str
    leg_id: str
    assigned: bool = True
    speed_knots: float = 14.0
    fuel_type: str = "vlsfo"
    cargo_allocation_teu: float = 800.0
    use_shore_power_at_dest: bool = False


@dataclass
class SolutionChromosome:
    """Complete fleet assignment chromosome."""
    assignments: List[VesselAssignmentDecision] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_continuous_vector(self) -> np.ndarray:
        """Flatten continuous variables (speed, cargo) for metaheuristic optimization."""
        vec = []
        for a in self.assignments:
            vec.append(a.speed_knots)
            vec.append(a.cargo_allocation_teu)
        return np.array(vec, dtype=float)

    @classmethod
    def from_flat_vector(cls, vec: np.ndarray, template_vessels: List[str], leg_id: str):
        """Construct chromosome from flat continuous array and template identifiers."""
        assignments = []
        n_vessels = len(template_vessels)
        for i in range(n_vessels):
            speed = float(vec[2 * i])
            cargo = float(vec[2 * i + 1])
            assignments.append(
                VesselAssignmentDecision(
                    vessel_id=template_vessels[i],
                    leg_id=leg_id,
                    speed_knots=speed,
                    cargo_allocation_teu=cargo,
                )
            )
        return cls(assignments=assignments)
