"""
Phase 4 Heterogeneous Fleet Optimization Architecture.
Defines real-telemetry calibrated vessel profiles, synthetic operational cargo demands,
weather uncertainty scenarios, fuel compatibility matrices, and CVaR robustness models.
Label: REAL_TELEMETRY_CALIBRATED / SYNTHETIC_OPERATIONAL_SCENARIO
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from .canonical_mapper import canonicalize_vessel_type, canonicalize_fuel_type
from .variables import FUEL_MAP, REV_FUEL_MAP, MODE_MAP, REV_MODE_MAP


@dataclass(frozen=True)
class FleetVesselProfile:
    """Rigorous naval architectural profile for a fleet vessel."""
    vessel_id: str
    name: str
    class_family: str
    gross_tonnage: float
    deadweight_tonnes: float
    design_draft_m: float
    displacement_t: float
    min_speed_knots: float
    max_speed_knots: float
    hotel_load_kw: float
    compatible_fuels: Tuple[str, ...]
    passenger_capacity: int = 0
    deck_cargo_capable: bool = False
    source_provenance: str = "REAL_TELEMETRY_CALIBRATED"


@dataclass(frozen=True)
class CargoDemand:
    """Operational transport demand requirement."""
    demand_id: str
    name: str
    origin: str
    destination: str
    distance_nm: float
    cargo_quantity_tonnes: float
    passengers_count: int
    deadline_hours: float
    required_vessel_family: str
    cargo_type: str  # "luxury_passengers", "coastal_passengers", "offshore_deck_cargo"
    source_provenance: str = "SYNTHETIC_OPERATIONAL_SCENARIO"


@dataclass(frozen=True)
class WeatherScenario:
    """Environmental condition scenario with probability weight."""
    scenario_id: str
    name: str
    wave_height_m: float
    wave_period_s: float
    wind_speed_ms: float
    wind_direction_deg: float
    current_speed_ms: float
    current_direction_deg: float
    water_depth_m: float
    probability: float
    source_provenance: str = "SYNTHETIC_OPERATIONAL_SCENARIO"


# =========================================================================
# 1. REAL-TELEMETRY CALIBRATED VESSEL REGISTRY
# =========================================================================
FLEET_VESSELS: Dict[str, FleetVesselProfile] = {
    "CPS_Poseidon": FleetVesselProfile(
        vessel_id="CPS_Poseidon",
        name="Crown Princess Poseidon",
        class_family="passenger_cruise",
        gross_tonnage=70000.0,
        deadweight_tonnes=8500.0,
        design_draft_m=7.5,
        displacement_t=42000.0,
        min_speed_knots=8.0,
        max_speed_knots=22.0,
        hotel_load_kw=6500.0,
        compatible_fuels=("vlsfo", "fossil_lng", "bio_methanol"),
        passenger_capacity=3800,
        deck_cargo_capable=False,
        source_provenance="REAL_TELEMETRY_CALIBRATED",
    ),
    "CPS_Triton": FleetVesselProfile(
        vessel_id="CPS_Triton",
        name="Coastal Princess Triton",
        class_family="passenger_cruise_small",
        gross_tonnage=11000.0,
        deadweight_tonnes=1800.0,
        design_draft_m=5.0,
        displacement_t=8500.0,
        min_speed_knots=6.0,
        max_speed_knots=18.0,
        hotel_load_kw=1800.0,
        compatible_fuels=("vlsfo", "bio_methanol"),
        passenger_capacity=1400,
        deck_cargo_capable=False,
        source_provenance="REAL_TELEMETRY_CALIBRATED",
    ),
    "OSS_Ceto": FleetVesselProfile(
        vessel_id="OSS_Ceto",
        name="Ocean Supply Ship Ceto",
        class_family="offshore_supply",
        gross_tonnage=24000.0,
        deadweight_tonnes=5200.0,
        design_draft_m=6.0,
        displacement_t=6000.0,
        min_speed_knots=4.0,
        max_speed_knots=15.0,
        hotel_load_kw=800.0,
        compatible_fuels=("vlsfo", "mgo", "bio_methanol", "green_ammonia"),
        passenger_capacity=0,
        deck_cargo_capable=True,
        source_provenance="REAL_TELEMETRY_CALIBRATED",
    ),
}

# =========================================================================
# 2. SYNTHETIC OPERATIONAL CARGO DEMANDS
# =========================================================================
OPERATIONAL_DEMANDS: Dict[str, CargoDemand] = {
    "DEMAND-A": CargoDemand(
        demand_id="DEMAND-A",
        name="Mainline Luxury Cruise Tour",
        origin="Southampton",
        destination="Bergen",
        distance_nm=550.0,
        cargo_quantity_tonnes=1200.0,
        passengers_count=3200,
        deadline_hours=32.0,  # Requires speed >= 17.2 kn
        required_vessel_family="passenger_cruise",
        cargo_type="luxury_passengers",
        source_provenance="SYNTHETIC_OPERATIONAL_SCENARIO",
    ),
    "DEMAND-B": CargoDemand(
        demand_id="DEMAND-B",
        name="Fjord Expedition Eco-Cruise",
        origin="Stavanger",
        destination="Tromso",
        distance_nm=680.0,
        cargo_quantity_tonnes=450.0,
        passengers_count=1100,
        deadline_hours=48.0,  # Requires speed >= 14.2 kn
        required_vessel_family="passenger_cruise_small",
        cargo_type="coastal_passengers",
        source_provenance="SYNTHETIC_OPERATIONAL_SCENARIO",
    ),
    "DEMAND-C": CargoDemand(
        demand_id="DEMAND-C",
        name="Offshore Energy Platform Deck Equipment",
        origin="Aberdeen",
        destination="Ekofisk Complex",
        distance_nm=180.0,
        cargo_quantity_tonnes=3200.0,
        passengers_count=0,
        deadline_hours=18.0,  # Requires speed >= 10.0 kn
        required_vessel_family="offshore_supply",
        cargo_type="offshore_deck_cargo",
        source_provenance="SYNTHETIC_OPERATIONAL_SCENARIO",
    ),
}

# =========================================================================
# 3. WEATHER UNCERTAINTY SCENARIOS (Strictly within domain envelope Hs <= 3.5m)
# =========================================================================
WEATHER_SCENARIOS: List[WeatherScenario] = [
    WeatherScenario(
        scenario_id="SCEN-W1",
        name="Calm Sea / Light Breeze",
        wave_height_m=1.0,
        wave_period_s=5.5,
        wind_speed_ms=4.0,
        wind_direction_deg=45.0,
        current_speed_ms=0.2,
        current_direction_deg=30.0,
        water_depth_m=120.0,
        probability=0.35,
        source_provenance="SYNTHETIC_OPERATIONAL_SCENARIO",
    ),
    WeatherScenario(
        scenario_id="SCEN-W2",
        name="Moderate Sea / Moderate Breeze",
        wave_height_m=1.8,
        wave_period_s=7.0,
        wind_speed_ms=8.5,
        wind_direction_deg=90.0,
        current_speed_ms=0.5,
        current_direction_deg=60.0,
        water_depth_m=120.0,
        probability=0.35,
        source_provenance="SYNTHETIC_OPERATIONAL_SCENARIO",
    ),
    WeatherScenario(
        scenario_id="SCEN-W3",
        name="Rough Sea / Strong Wind",
        wave_height_m=2.6,
        wave_period_s=8.2,
        wind_speed_ms=12.0,
        wind_direction_deg=180.0,
        current_speed_ms=0.7,
        current_direction_deg=120.0,
        water_depth_m=120.0,
        probability=0.20,
        source_provenance="SYNTHETIC_OPERATIONAL_SCENARIO",
    ),
    WeatherScenario(
        scenario_id="SCEN-W4",
        name="Severe Sea / Near Gale",
        wave_height_m=3.4,
        wave_period_s=9.5,
        wind_speed_ms=14.5,
        wind_direction_deg=225.0,
        current_speed_ms=0.9,
        current_direction_deg=180.0,
        water_depth_m=120.0,
        probability=0.10,
        source_provenance="SYNTHETIC_OPERATIONAL_SCENARIO",
    ),
]


# =========================================================================
# 4. CONDITIONAL VALUE AT RISK (CVaR) CALCULATOR
# =========================================================================
def compute_cvar_risk(
    losses: np.ndarray,
    probabilities: np.ndarray,
    alpha: float = 0.80,
) -> Tuple[float, float, float]:
    """
    Computes Expected Loss, VaR_alpha, and CVaR_alpha.
    RiskMetric = CVaR_alpha - ExpectedLoss.
    """
    p_norm = probabilities / np.sum(probabilities)
    expected_loss = float(np.sum(losses * p_norm))

    # Sort losses ascending
    sort_idx = np.argsort(losses)
    sorted_losses = losses[sort_idx]
    sorted_p = p_norm[sort_idx]
    cum_p = np.cumsum(sorted_p)

    # Find VaR_alpha: smallest loss where cum_p >= alpha
    var_idx = np.searchsorted(cum_p, alpha)
    var_idx = min(var_idx, len(sorted_losses) - 1)
    var_alpha = float(sorted_losses[var_idx])

    # Compute CVaR_alpha (expected loss in the upper (1 - alpha) tail)
    tail_mask = sorted_losses >= var_alpha
    if np.sum(sorted_p[tail_mask]) > 1e-9:
        cvar_alpha = float(np.sum(sorted_losses[tail_mask] * sorted_p[tail_mask]) / np.sum(sorted_p[tail_mask]))
    else:
        cvar_alpha = var_alpha

    risk_metric = max(0.0, cvar_alpha - expected_loss)
    return expected_loss, cvar_alpha, risk_metric


# =========================================================================
# 5. DECISION VECTOR ENCODING & PARSING
# =========================================================================
# Each vessel decision vector x_i has 6 dimensions:
# 0: assigned_demand_idx (0: Unassigned, 1: Demand-A, 2: Demand-B, 3: Demand-C)
# 1: cargo_tonnes (Continuous: 0 to vessel.deadweight_tonnes)
# 2: speed_knots (Continuous: min_speed to max_speed)
# 3: fuel_idx (0: vlsfo, 1: fossil_lng, 2: bio_methanol, 3: green_ammonia, 4: liquid_hydrogen)
# 4: operating_mode_idx (0: transit, 1: maneuvering, 2: dp, 3: port)
# 5: shore_power_int (0: False, 1: True)
DECISION_DIMS_PER_VESSEL = 6

DEMAND_KEYS = ["UNASSIGNED", "DEMAND-A", "DEMAND-B", "DEMAND-C"]
REV_DEMAND_KEYS = {k: i for i, k in enumerate(DEMAND_KEYS)}


def get_fleet_bounds(vessels: List[FleetVesselProfile]) -> Tuple[np.ndarray, np.ndarray]:
    """Generates continuous/discrete search hypercube bounds for heterogeneous fleet."""
    xl_list, xu_list = [], []
    for v in vessels:
        xl_list.extend([
            0.0,                    # assigned_demand_idx min (0 = Unassigned)
            0.0,                    # cargo min
            v.min_speed_knots,      # speed min
            0.0,                    # fuel_idx min
            0.0,                    # mode_idx min
            0.0,                    # shore_power min
        ])
        xu_list.extend([
            float(len(DEMAND_KEYS) - 1),  # assigned_demand_idx max (3)
            v.deadweight_tonnes,           # cargo max
            v.max_speed_knots,             # speed max
            float(len(FUEL_MAP) - 1),      # fuel_idx max (4)
            float(len(MODE_MAP) - 1),      # mode_idx max (3)
            1.0,                           # shore_power max (1)
        ])
    return np.array(xl_list, dtype=float), np.array(xu_list, dtype=float)


@dataclass
class DecodedVesselDecision:
    vessel_id: str
    assigned_demand: str  # "UNASSIGNED", "DEMAND-A", "DEMAND-B", "DEMAND-C"
    cargo_tonnes: float
    speed_knots: float
    fuel_type: str
    operating_mode: str
    use_shore_power: bool
    is_compatible: bool
    incompatibility_reason: str = ""


def decode_fleet_vector(
    X_fleet: np.ndarray,
    vessels: List[FleetVesselProfile],
) -> List[DecodedVesselDecision]:
    """Decodes flat numeric decision array into structured fleet decisions."""
    decisions = []
    n_v = len(vessels)
    for i, v in enumerate(vessels):
        sub = X_fleet[i * DECISION_DIMS_PER_VESSEL : (i + 1) * DECISION_DIMS_PER_VESSEL]
        demand_idx = int(np.clip(np.round(sub[0]), 0, len(DEMAND_KEYS) - 1))
        demand_key = DEMAND_KEYS[demand_idx]
        raw_cargo = float(sub[1])
        raw_speed = float(sub[2])
        fuel_idx = int(np.clip(np.round(sub[3]), 0, len(FUEL_MAP) - 1))
        fuel_str = FUEL_MAP[fuel_idx]
        mode_idx = int(np.clip(np.round(sub[4]), 0, len(MODE_MAP) - 1))
        mode_str = MODE_MAP[mode_idx]
        shore_power = bool(sub[5] >= 0.5)

        is_comp = True
        reason = ""

        # Check raw speed bounds
        if raw_speed < v.min_speed_knots or raw_speed > v.max_speed_knots:
            is_comp = False
            reason = f"Speed {raw_speed:.1f} kn outside safe domain operating limits [{v.min_speed_knots}, {v.max_speed_knots}] for {v.name} (infeasible speed / deadline breach)"

        # Check raw cargo bounds
        if raw_cargo < 0.0 or raw_cargo > v.deadweight_tonnes:
            is_comp = False
            reason = f"Cargo {raw_cargo:.1f} t exceeds deadweight capacity [0, {v.deadweight_tonnes}] for {v.name}"

        # Check vessel-fuel compatibility
        if is_comp and fuel_str not in v.compatible_fuels:
            is_comp = False
            reason = f"Incompatible fuel {fuel_str} for {v.name} (authorized: {list(v.compatible_fuels)})"

        # Check vessel-demand compatibility
        if is_comp and demand_key != "UNASSIGNED":
            dem = OPERATIONAL_DEMANDS[demand_key]
            # Family match check
            if dem.required_vessel_family == "passenger_cruise":
                if v.class_family != "passenger_cruise":
                    is_comp = False
                    reason = f"Incompatible assignment: Demand {demand_key} requires luxury passenger cruise vessel, but {v.name} is {v.class_family}"
            elif dem.required_vessel_family == "passenger_cruise_small":
                if v.class_family not in ["passenger_cruise", "passenger_cruise_small"]:
                    is_comp = False
                    reason = f"Incompatible assignment: Demand {demand_key} requires passenger vessel, but {v.name} is {v.class_family}"
            elif dem.required_vessel_family == "offshore_supply":
                if not v.deck_cargo_capable:
                    is_comp = False
                    reason = f"Incompatible assignment: Demand {demand_key} requires offshore deck cargo capability, not supported by {v.name}"

            # Capacity check
            if dem.cargo_quantity_tonnes > v.deadweight_tonnes:
                is_comp = False
                reason = f"Cargo demand ({dem.cargo_quantity_tonnes} t) exceeds {v.name} deadweight capacity ({v.deadweight_tonnes} t)"

            # A voyage leg can only be completed while under way. "port" and "dp" model a stationary
            # vessel (fixed 2 h / 1 h, no distance covered), so they cannot fulfil an assigned demand.
            if is_comp and mode_str in ("port", "dp"):
                is_comp = False
                reason = f"Operating mode '{mode_str}' cannot complete the {dem.distance_nm:.0f} nm leg of {demand_key} (vessel is stationary)"

        # Exactly-once assignment means the assigned vessel carries the whole demand, so the carried cargo is
        # determined by the assignment. The raw cargo dimension is retained for vector compatibility but is inert.
        carried = OPERATIONAL_DEMANDS[demand_key].cargo_quantity_tonnes if demand_key != "UNASSIGNED" else 0.0

        decisions.append(DecodedVesselDecision(
            vessel_id=v.vessel_id,
            assigned_demand=demand_key,
            cargo_tonnes=carried,
            speed_knots=raw_speed,
            fuel_type=fuel_str,
            operating_mode=mode_str,
            use_shore_power=shore_power,
            is_compatible=is_comp,
            incompatibility_reason=reason,
        ))
    return decisions
