"""
FuelEU Maritime Compliance Module (Regulation (EU) 2023/1805).
Strictly decoupled from IMO CII. FuelEU is based on Well-to-Wake GHG intensity per energy unit (g CO2e / MJ).
"""

from typing import Dict, Any


def calculate_fueleu_compliance(
    energy_consumed_mj: float,
    wtw_ghg_emissions_tonnes_co2e: float,
    target_intensity_g_co2e_per_mj: float = 89.34,  # 2% reduction below 91.16 baseline
    penalty_rate_eur_per_t_vlsfo_equiv: float = 2400.0,
    vlsfo_energy_density_mj_per_tonne: float = 41000.0,
    eur_to_usd_rate: float = 1.08,
) -> Dict[str, Any]:
    """
    Calculate FuelEU compliance balance and financial penalties.

    Inputs:
        energy_consumed_mj: Total propulsion and auxiliary energy consumed within EU scope (MJ)
        wtw_ghg_emissions_tonnes_co2e: Total Well-to-Wake emissions within EU scope (tonnes CO2e)
        target_intensity_g_co2e_per_mj: Required GHG intensity limit (g CO2e / MJ)
        penalty_rate_eur_per_t_vlsfo_equiv: Statutory penalty per tonne VLSFO equivalent (2400 EUR)
        vlsfo_energy_density_mj_per_tonne: Reference energy per tonne VLSFO (41,000 MJ/t)
        eur_to_usd_rate: Currency conversion multiplier

    Returns:
        Dict containing attained intensity, compliance deficit, and financial penalty.
    """
    if energy_consumed_mj <= 0.0:
        return {
            "attained_intensity_g_co2e_per_mj": 0.0,
            "target_intensity_g_co2e_per_mj": target_intensity_g_co2e_per_mj,
            "compliance_balance_g_co2e": 0.0,
            "penalty_eur": 0.0,
            "penalty_usd": 0.0,
            "is_compliant": True,
        }

    # Attained intensity = total grams CO2e / total MJ
    attained_intensity = (wtw_ghg_emissions_tonnes_co2e * 1e6) / energy_consumed_mj

    # Compliance Balance (CB) = (Target - Attained) * Energy
    compliance_balance_g = (target_intensity_g_co2e_per_mj - attained_intensity) * energy_consumed_mj

    if compliance_balance_g >= 0.0:
        # Surplus banking / compliance achieved
        penalty_eur = 0.0
        penalty_usd = 0.0
        is_compliant = True
    else:
        # Deficit penalization
        deficit_g = abs(compliance_balance_g)
        deficit_metric_tonnes_vlsfo_equiv = (deficit_g / target_intensity_g_co2e_per_mj) / vlsfo_energy_density_mj_per_tonne
        penalty_eur = deficit_metric_tonnes_vlsfo_equiv * penalty_rate_eur_per_t_vlsfo_equiv
        penalty_usd = penalty_eur * eur_to_usd_rate
        is_compliant = False

    return {
        "attained_intensity_g_co2e_per_mj": attained_intensity,
        "target_intensity_g_co2e_per_mj": target_intensity_g_co2e_per_mj,
        "compliance_balance_g_co2e": compliance_balance_g,
        "is_compliant": is_compliant,
        "penalty_eur": penalty_eur,
        "penalty_usd": penalty_usd,
    }
