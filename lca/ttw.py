"""
Tank-to-Wake (TtW) operational emissions accounting.
Aggregates combustion CO2, uncombusted CH4, and combustion N2O.
"""

from typing import Dict
from .methane_slip import calculate_methane_slip


def calculate_ttw_emissions(
    fuel_mass_kg: float,
    lhv_mj_per_kg: float,
    ttw_co2_factor_g_per_g: float,
    ttw_ch4_factor_g_per_g: float = 0.0,
    ttw_n2o_factor_g_per_g: float = 0.0,
    methane_slip_fraction: float = 0.0,
    ch4_gwp100: float = 29.8,
    n2o_gwp100: float = 273.0,
) -> Dict[str, float]:
    """
    Calculate combustion emissions at sea.

    Inputs:
        fuel_mass_kg: Consumed fuel mass (kg)
        lhv_mj_per_kg: LHV (MJ/kg)
        ttw_co2_factor_g_per_g: g CO2 / g fuel
        ttw_ch4_factor_g_per_g: g CH4 baseline / g fuel
        ttw_n2o_factor_g_per_g: g N2O / g fuel
        methane_slip_fraction: Engine methane slip fraction [-]
        ch4_gwp100: GWP100 for methane
        n2o_gwp100: GWP100 for nitrous oxide

    Returns:
        Dict containing emissions broken down by species in metric tonnes CO2e.
    """
    fuel_mass_g = fuel_mass_kg * 1000.0

    # CO2 emissions
    co2_emissions_g = fuel_mass_g * ttw_co2_factor_g_per_g
    co2_tonnes = co2_emissions_g / 1e6

    # CH4 slip / combustion emissions
    slip_data = calculate_methane_slip(
        fuel_mass_kg=fuel_mass_kg,
        methane_slip_fraction=methane_slip_fraction,
        lhv_mj_per_kg=lhv_mj_per_kg,
        methane_gwp100=ch4_gwp100,
    )
    ch4_baseline_tonnes = (fuel_mass_g * ttw_ch4_factor_g_per_g * ch4_gwp100) / 1e6
    total_ch4_tonnes_co2e = slip_data["methane_emissions_tonnes_co2e"] + ch4_baseline_tonnes

    # N2O emissions
    n2o_emissions_g = fuel_mass_g * ttw_n2o_factor_g_per_g
    n2o_tonnes_co2e = (n2o_emissions_g * n2o_gwp100) / 1e6

    ttw_total_tonnes_co2e = co2_tonnes + total_ch4_tonnes_co2e + n2o_tonnes_co2e

    return {
        "co2_tonnes": co2_tonnes,
        "ch4_tonnes_co2e": total_ch4_tonnes_co2e,
        "n2o_tonnes_co2e": n2o_tonnes_co2e,
        "ttw_total_tonnes_co2e": ttw_total_tonnes_co2e,
    }
