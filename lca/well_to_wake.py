"""
Well-to-Wake (WtW) lifecycle GHG integration.
Equation: WtW = WtT + TtW_CO2 + TtW_CH4 + TtW_N2O
Complies with IMO Resolution MEPC.391(81).
"""

from typing import Dict
from .wtt import calculate_wtt_emissions
from .ttw import calculate_ttw_emissions
from .fuel_registry import FuelPathwayRegistry


def calculate_well_to_wake(
    fuel_mass_kg: float,
    fuel_type: str,
    registry: FuelPathwayRegistry,
) -> Dict[str, float]:
    """
    Calculate comprehensive Well-to-Wake lifecycle GHG emissions.

    Inputs:
        fuel_mass_kg: Consumed fuel mass (kg)
        fuel_type: Fuel key in registry ('vlsfo', 'fossil_lng', 'bio_methanol', etc.)
        registry: Configured FuelPathwayRegistry instance

    Returns:
        Dict detailing WtT, TtW, and total WtW emissions (tonnes CO2e) and intensity (g CO2e/MJ).
    """
    pathway = registry.get_pathway(fuel_type)
    gwp = registry.gwp_factors

    wtt = calculate_wtt_emissions(
        fuel_mass_kg=fuel_mass_kg,
        lhv_mj_per_kg=pathway["lhv_mj_kg"],
        wtt_factor_g_co2e_per_mj=pathway["wtt_ghg_g_co2e_mj"],
    )

    ttw = calculate_ttw_emissions(
        fuel_mass_kg=fuel_mass_kg,
        lhv_mj_per_kg=pathway["lhv_mj_kg"],
        ttw_co2_factor_g_per_g=pathway["ttw_co2_g_per_g_fuel"],
        ttw_ch4_factor_g_per_g=pathway.get("ttw_ch4_g_per_g_fuel", 0.0),
        ttw_n2o_factor_g_per_g=pathway.get("ttw_n2o_g_per_g_fuel", 0.0),
        methane_slip_fraction=pathway.get("methane_slip_fraction", 0.0),
        ch4_gwp100=gwp["ch4_gwp100"],
        n2o_gwp100=gwp["n2o_gwp100"],
    )

    wtw_total_tonnes = wtt["wtt_emissions_tonnes_co2e"] + ttw["ttw_total_tonnes_co2e"]
    total_energy_mj = wtt["fuel_energy_mj"]
    wtw_intensity_g_co2e_per_mj = (wtw_total_tonnes * 1e6) / max(total_energy_mj, 1e-6)

    return {
        "fuel_type": fuel_type,
        "fuel_mass_tonnes": fuel_mass_kg / 1000.0,
        "total_energy_mj": total_energy_mj,
        "wtt_tonnes_co2e": wtt["wtt_emissions_tonnes_co2e"],
        "ttw_co2_tonnes": ttw["co2_tonnes"],
        "ttw_ch4_tonnes_co2e": ttw["ch4_tonnes_co2e"],
        "ttw_n2o_tonnes_co2e": ttw["n2o_tonnes_co2e"],
        "ttw_total_tonnes_co2e": ttw["ttw_total_tonnes_co2e"],
        "wtw_total_tonnes_co2e": wtw_total_tonnes,
        "wtw_intensity_g_co2e_per_mj": wtw_intensity_g_co2e_per_mj,
    }
