"""
Methane Slip Accounting Module.
Section 19: Explicitly tracks mass (kg, g), energy (MJ), and GWP CO2-equivalents.
Dimensional consistency:
  fuel_mass_kg * (LHV_MJ_per_kg) = fuel_energy_MJ
  fuel_mass_kg * methane_slip_fraction = unburned_methane_mass_kg
  unburned_methane_mass_kg * 1000 = unburned_methane_mass_g
  unburned_methane_mass_g * GWP_CH4 = emissions_g_co2e
  emissions_g_co2e / fuel_energy_MJ = intensity_g_co2e_per_mj
"""

from typing import Dict


def calculate_methane_slip(
    fuel_mass_kg: float,
    methane_slip_fraction: float,
    lhv_mj_per_kg: float,
    methane_gwp100: float = 29.8,
) -> Dict[str, float]:
    """
    Calculate methane slip emissions with explicit dimensional tracking.

    Inputs:
        fuel_mass_kg: Total consumed fuel mass (kg)
        methane_slip_fraction: Fraction of fuel mass slipping unburned [-] (e.g. 0.022 for LPDF)
        lhv_mj_per_kg: Lower Heating Value of fuel (MJ/kg)
        methane_gwp100: Global Warming Potential of methane (100-yr AR6 basis) [-]

    Returns:
        Dict containing:
            fuel_mass_kg: Consumed fuel mass (kg)
            fuel_energy_mj: Total lower heating value energy (MJ)
            unburned_methane_kg: Mass of escaped methane (kg)
            unburned_methane_g: Mass of escaped methane (g)
            methane_emissions_g_co2e: GWP-weighted methane emissions (g CO2e)
            methane_emissions_tonnes_co2e: GWP-weighted methane emissions (metric tonnes CO2e)
            methane_intensity_g_co2e_per_mj: Methane lifecycle intensity contribution (g CO2e / MJ)
    """
    if fuel_mass_kg <= 0.0 or methane_slip_fraction <= 0.0:
        return {
            "fuel_mass_kg": fuel_mass_kg,
            "fuel_energy_mj": fuel_mass_kg * lhv_mj_per_kg,
            "unburned_methane_kg": 0.0,
            "unburned_methane_g": 0.0,
            "methane_emissions_g_co2e": 0.0,
            "methane_emissions_tonnes_co2e": 0.0,
            "methane_intensity_g_co2e_per_mj": 0.0,
        }

    fuel_energy_mj = fuel_mass_kg * lhv_mj_per_kg
    unburned_methane_kg = fuel_mass_kg * methane_slip_fraction
    unburned_methane_g = unburned_methane_kg * 1000.0

    methane_emissions_g_co2e = unburned_methane_g * methane_gwp100
    methane_emissions_tonnes_co2e = methane_emissions_g_co2e / 1e6
    methane_intensity_g_co2e_per_mj = methane_emissions_g_co2e / max(fuel_energy_mj, 1e-6)

    return {
        "fuel_mass_kg": fuel_mass_kg,
        "fuel_energy_mj": fuel_energy_mj,
        "unburned_methane_kg": unburned_methane_kg,
        "unburned_methane_g": unburned_methane_g,
        "methane_emissions_g_co2e": methane_emissions_g_co2e,
        "methane_emissions_tonnes_co2e": methane_emissions_tonnes_co2e,
        "methane_intensity_g_co2e_per_mj": methane_intensity_g_co2e_per_mj,
    }
