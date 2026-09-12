"""
Propulsion efficiency and engine power / fuel consumption rate engine.
Converts total hydrodynamic resistance into required brake power and fuel flow.
"""

from typing import Dict


def calculate_propulsion_power(
    total_resistance_newtons: float,
    speed_m_s: float,
    eta_0: float = 0.68,
    eta_h: float = 1.05,
    eta_r: float = 1.00,
    eta_s: float = 0.98,
) -> Dict[str, float]:
    """
    Convert vessel resistance into brake power delivered at the engine shaft.

    Inputs:
        total_resistance_newtons: Total hydrodynamic resistance (N)
        speed_m_s: Vessel speed (m/s)
        eta_0: Propeller open water efficiency [-]
        eta_h: Hull efficiency = (1 - t) / (1 - w) [-]
        eta_r: Relative rotative efficiency [-]
        eta_s: Shaft mechanical transmission efficiency [-]

    Returns:
        Dict containing:
            pe_kw: Effective power (tow-rope power) (kW)
            eta_d: Quasi-propulsive efficiency (eta_0 * eta_h * eta_r) [-]
            pd_kw: Delivered power to propeller (kW)
            pb_kw: Brake power required at engine coupling (kW)
    """
    if speed_m_s <= 0.0 or total_resistance_newtons <= 0.0:
        return {"pe_kw": 0.0, "eta_d": eta_0 * eta_h * eta_r, "pd_kw": 0.0, "pb_kw": 0.0}

    # Pe = R_t * V (Watts) -> convert to kW
    pe_kw = (total_resistance_newtons * speed_m_s) / 1000.0

    # Quasi-propulsive efficiency
    eta_d = eta_0 * eta_h * eta_r

    # Delivered power
    pd_kw = pe_kw / max(eta_d, 0.1)

    # Brake power
    pb_kw = pd_kw / max(eta_s, 0.1)

    return {
        "pe_kw": pe_kw,
        "eta_d": eta_d,
        "pd_kw": pd_kw,
        "pb_kw": pb_kw,
    }


def calculate_fuel_rate(
    brake_power_kw: float,
    nominal_sfc_g_kwh: float = 165.0,
    mcr_kw: float = 15000.0,
    auxiliary_power_kw: float = 450.0,
    aux_sfc_g_kwh: float = 210.0,
    boiler_rate_kg_h: float = 80.0,
) -> Dict[str, float]:
    """
    Calculate fuel oil consumption rate accounting for main engine SFC curve,
    auxiliary diesel generators, and boiler loads.

    Inputs:
        brake_power_kw: Main engine brake power output (kW)
        nominal_sfc_g_kwh: Baseline SFC at 75-85% MCR (g/kWh)
        mcr_kw: Maximum Continuous Rating (kW)
        auxiliary_power_kw: Hotel and auxiliary electrical load (kW)
        aux_sfc_g_kwh: Auxiliary engine specific fuel consumption (g/kWh)
        boiler_rate_kg_h: In-transit/service boiler fuel consumption (kg/h)

    Returns:
        Dict containing:
            load_fraction: Engine load Pb / MCR [-]
            effective_sfc_g_kwh: Load-adjusted main engine SFC (g/kWh)
            main_fuel_kg_h: Main engine fuel rate (kg/h)
            aux_fuel_kg_h: Auxiliary generator fuel rate (kg/h)
            total_fuel_kg_h: Total voyage fuel consumption rate (kg/h)
            total_fuel_tonnes_per_day: Fuel rate in metric tonnes / day
    """
    load_fraction = brake_power_kw / max(mcr_kw, 1.0)

    # Standard parabolic SFC correction curve relative to optimum load (~75-80% MCR)
    # At low load (<40%), SFC increases significantly; at optimal load it dips to nominal
    load_clamped = max(0.1, min(1.1, load_fraction))
    sfc_factor = 1.0 + 0.35 * ((load_clamped - 0.78) ** 2) / (0.78 ** 2)
    effective_sfc = nominal_sfc_g_kwh * sfc_factor

    main_fuel_kg_h = (brake_power_kw * effective_sfc) / 1000.0
    aux_fuel_kg_h = (auxiliary_power_kw * aux_sfc_g_kwh) / 1000.0
    total_fuel_kg_h = main_fuel_kg_h + aux_fuel_kg_h + boiler_rate_kg_h
    total_tonnes_per_day = (total_fuel_kg_h * 24.0) / 1000.0

    return {
        "load_fraction": load_fraction,
        "effective_sfc_g_kwh": effective_sfc,
        "main_fuel_kg_h": main_fuel_kg_h,
        "aux_fuel_kg_h": aux_fuel_kg_h,
        "boiler_fuel_kg_h": boiler_rate_kg_h,
        "total_fuel_kg_h": total_fuel_kg_h,
        "total_fuel_tonnes_per_day": total_tonnes_per_day,
    }
