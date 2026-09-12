"""
Fleet objective evaluation engine.
Computes:
1. Total fuel consumption (tonnes)
2. Total operational cost (USD, including fuel, carbon tax, shore power)
3. Well-to-Wake lifecycle GHG emissions (tonnes CO2e)
4. Risk metric: CVaR_0.95(schedule delay)
"""

from typing import Dict, Any, List
import numpy as np
from physics.resistance_model import VesselResistanceModel
from lca.well_to_wake import calculate_well_to_wake
from lca.fuel_registry import FuelPathwayRegistry
from .cvar import compute_schedule_delay_cvar
from .variables import SolutionChromosome


def evaluate_fleet_objectives(
    chromosome: SolutionChromosome,
    voyage_distance_nm: float,
    deadline_hours: float,
    carbon_price_usd_per_tonne: float,
    weather_scenarios: List[Dict[str, float]],
    registry: FuelPathwayRegistry,
    vessel_model: VesselResistanceModel,
) -> Dict[str, float]:
    """
    Evaluate all fleet objectives for a candidate solution chromosome.
    """
    total_fuel_tonnes = 0.0
    total_fuel_cost = 0.0
    total_wtw_ghg_tonnes = 0.0
    transit_times_list = []

    for assignment in chromosome.assignments:
        speed = assignment.speed_knots
        fuel_type = assignment.fuel_type
        pathway = registry.get_pathway(fuel_type)

        # Transit time in calm sea
        transit_time_h = voyage_distance_nm / max(speed, 1.0)

        # Baseline fuel consumption across weather scenarios
        scenario_transit_times = []
        for sc in weather_scenarios:
            # Weather resistance calculation
            res = vessel_model.compute_total_resistance(
                speed_knots=speed,
                wave_height_m=sc.get("significant_wave_height_m", 0.0),
                wave_period_s=sc.get("peak_wave_period_s", 0.0),
                wind_speed_m_s=sc.get("wind_speed_m_s", 0.0),
            )
            fuel_kg_h = res["fuel"]["total_fuel_kg_h"]

            # Effective speed reduction due to involuntary speed loss in head waves
            actual_speed = max(5.0, speed - 0.2 * sc.get("significant_wave_height_m", 0.0))
            sc_transit_time = voyage_distance_nm / actual_speed
            scenario_transit_times.append(sc_transit_time)

        mean_transit_h = float(np.mean(scenario_transit_times))
        transit_times_list.extend(scenario_transit_times)

        leg_fuel_kg = fuel_kg_h * mean_transit_h
        leg_fuel_tonnes = leg_fuel_kg / 1000.0
        total_fuel_tonnes += leg_fuel_tonnes

        # Fuel cost
        fuel_price = pathway.get("price_usd_per_tonne", 650.0)
        total_fuel_cost += leg_fuel_tonnes * fuel_price

        # WtW LCA GHG emissions
        wtw_res = calculate_well_to_wake(
            fuel_mass_kg=leg_fuel_kg,
            fuel_type=fuel_type,
            registry=registry,
        )
        total_wtw_ghg_tonnes += wtw_res["wtw_total_tonnes_co2e"]

    # Carbon tax cost
    carbon_tax_cost = total_wtw_ghg_tonnes * carbon_price_usd_per_tonne
    total_opex = total_fuel_cost + carbon_tax_cost

    # CVaR risk
    cvar_res = compute_schedule_delay_cvar(
        transit_times_hours=np.array(transit_times_list),
        deadline_hours=deadline_hours,
        alpha=0.95,
    )

    return {
        "total_fuel_consumption_tonnes": total_fuel_tonnes,
        "total_operational_cost_usd": total_opex,
        "well_to_wake_ghg_emissions_tonnes_co2e": total_wtw_ghg_tonnes,
        "cvar_schedule_delay_hours": cvar_res["cvar_alpha_hours"],
        "mean_delay_hours": cvar_res["mean_delay_hours"],
    }
