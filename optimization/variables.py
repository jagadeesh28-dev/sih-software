"""
Solution Chromosome Representation for Mixed-Variable Green Fleet Optimization.
Section A: Formally defined chromosome supporting mixed continuous and discrete decisions:
[vessel_assignment, fuel_choice, speed, cargo, operating_mode, shore_power_state]
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

# Canonical Fuel Mapping
FUEL_MAP = {
    0: "vlsfo",
    1: "fossil_lng",
    2: "bio_methanol",
    3: "green_ammonia",
    4: "liquid_hydrogen",
}
REV_FUEL_MAP = {v: k for k, v in FUEL_MAP.items()}

# Canonical Operating Mode Mapping
MODE_MAP = {
    0: "transit",
    1: "maneuvering",
    2: "dp",
    3: "port",
}
REV_MODE_MAP = {v: k for k, v in MODE_MAP.items()}


@dataclass
class VesselAssignmentDecision:
    """Decisions for an individual vessel on an assigned voyage leg."""
    vessel_id: str
    leg_id: str
    assigned: bool = True
    speed_knots: float = 14.0
    fuel_type: str = "vlsfo"
    cargo_allocation_teu: float = 800.0
    operating_mode: str = "transit"
    use_shore_power_at_dest: bool = False

    def to_array(self) -> np.ndarray:
        """
        Continuous/discrete numeric array:
        [speed_knots, cargo_allocation_teu, fuel_idx, mode_idx, shore_power_int]
        """
        fuel_idx = float(REV_FUEL_MAP.get(self.fuel_type.lower(), 0))
        mode_idx = float(REV_MODE_MAP.get(self.operating_mode.lower(), 0))
        shore_int = 1.0 if self.use_shore_power_at_dest else 0.0
        return np.array([
            self.speed_knots,
            self.cargo_allocation_teu,
            fuel_idx,
            mode_idx,
            shore_int,
        ], dtype=float)

    @classmethod
    def from_array(
        cls,
        vec: np.ndarray,
        vessel_id: str,
        leg_id: str,
        assigned: bool = True,
    ) -> "VesselAssignmentDecision":
        """Reconstruct decision from numeric vector."""
        speed = float(vec[0])
        cargo = max(0.0, float(vec[1]))
        fuel_idx = int(np.clip(np.round(vec[2]), 0, len(FUEL_MAP) - 1))
        mode_idx = int(np.clip(np.round(vec[3]), 0, len(MODE_MAP) - 1))
        shore_bool = bool(vec[4] >= 0.5)

        return cls(
            vessel_id=vessel_id,
            leg_id=leg_id,
            assigned=assigned,
            speed_knots=speed,
            cargo_allocation_teu=cargo,
            fuel_type=FUEL_MAP[fuel_idx],
            operating_mode=MODE_MAP[mode_idx],
            use_shore_power_at_dest=shore_bool,
        )


@dataclass
class SolutionChromosome:
    """Complete fleet assignment chromosome across vessels and legs."""
    assignments: List[VesselAssignmentDecision] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_continuous_vector(self) -> np.ndarray:
        """Flatten continuous variables (speed, cargo) for metaheuristic optimization."""
        vec = []
        for a in self.assignments:
            vec.append(a.speed_knots)
            vec.append(a.cargo_allocation_teu)
        return np.array(vec, dtype=float)

    def to_full_vector(self) -> np.ndarray:
        """Flatten all decision variables into a 1D numeric array."""
        arrays = [a.to_array() for a in self.assignments]
        if not arrays:
            return np.array([], dtype=float)
        return np.concatenate(arrays)

    @classmethod
    def from_flat_vector(
        cls,
        vec: np.ndarray,
        template_vessels: List[str],
        leg_id: str,
    ) -> "SolutionChromosome":
        """Construct chromosome from flat continuous array (speed, cargo pairs)."""
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

    @classmethod
    def from_full_vector(
        cls,
        vec: np.ndarray,
        template_vessels: List[str],
        leg_ids: List[str],
    ) -> "SolutionChromosome":
        """Construct chromosome from full 5-variable-per-leg vector."""
        stride = 5
        assignments = []
        total_items = len(template_vessels)
        for i in range(total_items):
            sub_vec = vec[i * stride : (i + 1) * stride]
            v_id = template_vessels[i]
            l_id = leg_ids[i] if i < len(leg_ids) else f"leg_{i+1}"
            assignments.append(
                VesselAssignmentDecision.from_array(sub_vec, vessel_id=v_id, leg_id=l_id)
            )
        return cls(assignments=assignments)
