"""
Well-to-Tank (WtT) upstream GHG accounting.
Evaluates feedstock extraction, processing, transport, and bunkering emissions.
"""

from typing import Dict


def calculate_wtt_emissions(
    fuel_mass_kg: float,
    lhv_mj_per_kg: float,
    wtt_factor_g_co2e_per_mj: float,
) -> Dict[str, float]:
    """
    Calculate Well-to-Tank upstream emissions.

    Inputs:
        fuel_mass_kg: Consumed fuel mass (kg)
        lhv_mj_per_kg: Lower Heating Value (MJ/kg)
        wtt_factor_g_co2e_per_mj: Upstream GHG factor (g CO2e / MJ)

    Returns:
        Dict containing:
            fuel_energy_mj: Fuel energy (MJ)
            wtt_emissions_tonnes_co2e: Upstream emissions (metric tonnes CO2e)
    """
    fuel_energy_mj = fuel_mass_kg * lhv_mj_per_kg
    wtt_emissions_g_co2e = fuel_energy_mj * wtt_factor_g_co2e_per_mj
    wtt_emissions_tonnes = wtt_emissions_g_co2e / 1e6

    return {
        "fuel_energy_mj": fuel_energy_mj,
        "wtt_emissions_tonnes_co2e": wtt_emissions_tonnes,
    }
