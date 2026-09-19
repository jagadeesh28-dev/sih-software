"""
Decision Variable Types and Partitions for Fleet Optimization.
Explicitly defines every decision variable as CONTINUOUS, INTEGER, BINARY, or CATEGORICAL.
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple
import numpy as np


class VariableType(Enum):
    CONTINUOUS = "CONTINUOUS"
    INTEGER = "INTEGER"
    BINARY = "BINARY"
    CATEGORICAL = "CATEGORICAL"


@dataclass(frozen=True)
class VariableDefinition:
    index: int
    name: str
    vessel_id: str
    var_type: VariableType
    lower_bound: float
    upper_bound: float
    description: str


def get_heterogeneous_fleet_partitions(n_vessels: int = 3) -> List[VariableDefinition]:
    """
    Returns the formal definition for each dimension in the fleet decision vector.
    Each vessel has 6 dimensions:
      0: assigned_demand (CATEGORICAL, [0, 3])
      1: cargo_tonnes (CONTINUOUS, [0, DWT])
      2: speed_knots (CONTINUOUS, [min_speed, max_speed])
      3: fuel_type (CATEGORICAL, [0, 4])
      4: operating_mode (CATEGORICAL, [0, 3])
      5: use_shore_power (BINARY, [0, 1])
    """
    vessel_specs = [
        ("CPS_Poseidon", 8500.0, 8.0, 22.0),
        ("CPS_Triton", 1800.0, 6.0, 18.0),
        ("OSS_Ceto", 5200.0, 4.0, 15.0),
    ]

    definitions: List[VariableDefinition] = []
    idx = 0
    for v_idx in range(n_vessels):
        v_id, dwt, min_spd, max_spd = vessel_specs[v_idx % len(vessel_specs)]
        prefix = f"{v_id}_"
        definitions.extend([
            VariableDefinition(idx, prefix + "assigned_demand", v_id, VariableType.CATEGORICAL, 0.0, 3.0, "Cargo Demand (0:None, 1:Dem-A, 2:Dem-B, 3:Dem-C)"),
            VariableDefinition(idx + 1, prefix + "cargo_tonnes", v_id, VariableType.CONTINUOUS, 0.0, dwt, f"Payload cargo tonnes (max {dwt}t)"),
            VariableDefinition(idx + 2, prefix + "speed_knots", v_id, VariableType.CONTINUOUS, min_spd, max_spd, f"Commanded speed ({min_spd}-{max_spd} kn)"),
            VariableDefinition(idx + 3, prefix + "fuel_type", v_id, VariableType.CATEGORICAL, 0.0, 4.0, "Fuel selection (0:VLSFO, 1:LNG, 2:Methanol, 3:Ammonia, 4:LH2)"),
            VariableDefinition(idx + 4, prefix + "operating_mode", v_id, VariableType.CATEGORICAL, 0.0, 3.0, "Operating mode (0:Transit, 1:Maneuver, 2:DP, 3:Port)"),
            VariableDefinition(idx + 5, prefix + "use_shore_power", v_id, VariableType.BINARY, 0.0, 1.0, "Cold ironing / Shore power (0:No, 1:Yes)"),
        ])
        idx += 6
    return definitions
