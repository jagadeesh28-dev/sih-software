"""
Voyage Scenarios & Baseline Operational Policies.
Defines standard evaluation scenarios (SCEN-01 through SCEN-05)
and fixed baseline policies (BASELINE-1 through BASELINE-6) for fair comparison.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import numpy as np

from .variables import SolutionChromosome, VesselAssignmentDecision


@dataclass
class VoyageScenario:
    scenario_id: str
    name: str
    vessel_id: str
    vessel_class: str
    distance_nm: float
    deadline_hours: float
    cargo_demand_tonnes: float
    wave_height_m: float
    wave_period_s: float
    wind_speed_ms: float
    current_speed_ms: float
    water_depth_m: float
    carbon_price_usd_tonne: float = 90.0
    fuel_price_override: Optional[Dict[str, float]] = None


# Standard Benchmark Scenarios
BENCHMARK_SCENARIOS = {
    "SCEN-01": VoyageScenario(
        scenario_id="SCEN-01",
        name="North Sea Cruise Transit",
        vessel_id="CPS_Poseidon",
        vessel_class="cruise_passenger",
        distance_nm=450.0,
        deadline_hours=28.0,
        cargo_demand_tonnes=0.0,
        wave_height_m=2.0,
        wave_period_s=7.5,
        wind_speed_ms=9.0,
        current_speed_ms=0.6,
        water_depth_m=80.0,
        carbon_price_usd_tonne=90.0,
    ),
    "SCEN-02": VoyageScenario(
        scenario_id="SCEN-02",
        name="Atlantic Cruise Crossing",
        vessel_id="CPS_Poseidon",
        vessel_class="cruise_passenger",
        distance_nm=1200.0,
        deadline_hours=72.0,
        cargo_demand_tonnes=0.0,
        wave_height_m=3.8,
        wave_period_s=9.5,
        wind_speed_ms=14.0,
        current_speed_ms=0.8,
        water_depth_m=2500.0,
        carbon_price_usd_tonne=90.0,
    ),
    "SCEN-03": VoyageScenario(
        scenario_id="SCEN-03",
        name="Offshore Supply Station",
        vessel_id="OSS_Ceto",
        vessel_class="offshore_supply",
        distance_nm=120.0,
        deadline_hours=14.0,
        cargo_demand_tonnes=2500.0,
        wave_height_m=1.2,
        wave_period_s=6.0,
        wind_speed_ms=6.0,
        current_speed_ms=0.4,
        water_depth_m=120.0,
        carbon_price_usd_tonne=90.0,
    ),
    "SCEN-04": VoyageScenario(
        scenario_id="SCEN-04",
        name="Multi-Fuel Decarbonization",
        vessel_id="CPS_Triton",
        vessel_class="cruise_passenger",
        distance_nm=600.0,
        deadline_hours=36.0,
        cargo_demand_tonnes=0.0,
        wave_height_m=0.8,
        wave_period_s=5.0,
        wind_speed_ms=4.0,
        current_speed_ms=0.3,
        water_depth_m=150.0,
        carbon_price_usd_tonne=120.0,
    ),
    "SCEN-05": VoyageScenario(
        scenario_id="SCEN-05",
        name="Stress / Storm Scenario",
        vessel_id="CPS_Poseidon",
        vessel_class="cruise_passenger",
        distance_nm=500.0,
        deadline_hours=32.0,
        cargo_demand_tonnes=0.0,
        wave_height_m=5.5,
        wave_period_s=11.0,
        wind_speed_ms=18.0,
        current_speed_ms=1.2,
        water_depth_m=200.0,
        carbon_price_usd_tonne=90.0,
    ),
}


def create_baseline_policy(
    policy_id: str,
    scenario: VoyageScenario,
) -> SolutionChromosome:
    """
    Construct standardized operational baseline policies:
    - BASELINE-1: Max permitted speed (V_max) on VLSFO
    - BASELINE-2: Nominal design cruising speed on VLSFO
    - BASELINE-3: Fuel-minimizing speed satisfying deadline on VLSFO
    - BASELINE-4: Cost-minimizing speed
    - BASELINE-5: Green decarbonized strategy (Bio-methanol with cold ironing)
    - BASELINE-6: Random feasible strategy
    """
    v_id = scenario.vessel_id
    # Determine reference speeds based on vessel class
    if "poseidon" in v_id.lower():
        v_max, v_nom, v_min = 21.5, 19.5, 12.0
    elif "triton" in v_id.lower():
        v_max, v_nom, v_min = 17.5, 15.0, 10.0
    elif "ceto" in v_id.lower():
        v_max, v_nom, v_min = 14.5, 12.0, 8.0
    else:
        v_max, v_nom, v_min = 18.5, 16.0, 11.0

    p_upper = policy_id.upper()

    if "BASELINE-1" in p_upper or "MAX" in p_upper:
        speed = v_max
        fuel = "vlsfo"
        shore = False
    elif "BASELINE-2" in p_upper or "NOMINAL" in p_upper:
        speed = v_nom
        fuel = "vlsfo"
        shore = False
    elif "BASELINE-3" in p_upper or "FUEL" in p_upper:
        # Minimum speed satisfying distance / speed <= deadline
        speed_req = scenario.distance_nm / max(1.0, scenario.deadline_hours - 2.0)
        speed = max(v_min, min(speed_req, v_nom))
        fuel = "vlsfo"
        shore = True
    elif "BASELINE-4" in p_upper or "COST" in p_upper:
        speed = (v_min + v_nom) / 2.0
        fuel = "vlsfo"
        shore = True
    elif "BASELINE-5" in p_upper or "GREEN" in p_upper:
        speed = v_min
        fuel = "bio_methanol"
        shore = True
    else:  # BASELINE-6 / Random Feasible
        np.random.seed(42)
        speed = float(np.random.uniform(v_min, v_nom))
        fuel = "vlsfo"
        shore = True

    dec = VesselAssignmentDecision(
        vessel_id=v_id,
        leg_id=f"{scenario.scenario_id}_leg1",
        assigned=True,
        speed_knots=speed,
        fuel_type=fuel,
        cargo_allocation_teu=scenario.cargo_demand_tonnes,
        operating_mode="transit",
        use_shore_power_at_dest=shore,
    )
    return SolutionChromosome(assignments=[dec], metadata={"policy": policy_id})
