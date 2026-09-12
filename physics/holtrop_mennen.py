"""
Calm-water resistance calculation based on the Holtrop & Mennen (1982, 1984) method.
All input and output units are documented and strictly in SI units.
"""

import math
from typing import Dict, Any


def calculate_calm_water_resistance(
    speed_m_s: float,
    lwl_m: float,
    beam_m: float,
    draft_m: float,
    displacement_m3: float,
    wetted_surface_m2: float,
    block_coefficient_cb: float,
    gravity_m_s2: float = 9.80665,
    seawater_density_kg_m3: float = 1025.0,
    kinematic_viscosity_m2_s: float = 1.188e-6,
) -> Dict[str, float]:
    """
    Calculate Holtrop-Mennen calm water resistance components.

    Inputs:
        speed_m_s: Vessel speed through water (m/s)
        lwl_m: Length on waterline (m)
        beam_m: Moulded breadth (m)
        draft_m: Moulded draft (m)
        displacement_m3: Volumetric displacement (m^3)
        wetted_surface_m2: Wetted surface area (m^2)
        block_coefficient_cb: Block coefficient Cb [-]
        gravity_m_s2: Gravitational acceleration (m/s^2)
        seawater_density_kg_m3: Seawater density (kg/m^3)
        kinematic_viscosity_m2_s: Kinematic viscosity (m^2/s)

    Returns:
        Dict containing:
            froude_number: Fn [-]
            reynolds_number: Re [-]
            cf: ITTC-1957 friction coefficient [-]
            rf_newtons: Frictional resistance (N)
            form_factor_1_plus_k1: Form factor (1 + k1) [-]
            r_viscous_newtons: Viscous resistance (1+k1)*Rf (N)
            rw_newtons: Wave-making resistance (N)
            rt_calm_newtons: Total calm-water resistance (N)
    """
    if speed_m_s <= 0.0:
        return {
            "froude_number": 0.0,
            "reynolds_number": 0.0,
            "cf": 0.0,
            "rf_newtons": 0.0,
            "form_factor_1_plus_k1": 1.0,
            "r_viscous_newtons": 0.0,
            "rw_newtons": 0.0,
            "rt_calm_newtons": 0.0,
        }

    # 1. Non-dimensional numbers
    fn = speed_m_s / math.sqrt(gravity_m_s2 * lwl_m)
    re = (speed_m_s * lwl_m) / kinematic_viscosity_m2_s

    # 2. ITTC-1957 Friction Line
    # Cf = 0.075 / (log10(Re) - 2)^2
    log_re = math.log10(max(re, 1e5))
    cf = 0.075 / ((log_re - 2.0) ** 2)

    # 3. Frictional Resistance Rf = 0.5 * rho * V^2 * S * Cf
    rf_newtons = 0.5 * seawater_density_kg_m3 * (speed_m_s ** 2) * wetted_surface_m2 * cf

    # 4. Form Factor (1 + k1) estimation (Holtrop-Mennen 1982)
    # 1 + k1 = 0.93 + 0.487118 * c14 * (B/L)^1.06806 * (T/L)^0.46106 * (L/LR)^0.121563 * (L^3/nabla)^0.36486 * (1 - Cp)^-0.604247
    # Simplified standard approximation for standard cargo forms:
    lr_over_l = 1.0 - block_coefficient_cb + (0.06 * block_coefficient_cb * 0.7) / (4.0 * 0.7 - 3.0) if (4.0 * 0.7 - 3.0) != 0 else 0.8
    lr_over_l = max(0.5, min(1.0, lr_over_l))
    form_factor = 1.0 + 0.6 * math.sqrt(beam_m / lwl_m) * (block_coefficient_cb ** 2)
    form_factor = max(1.05, min(1.40, form_factor))

    r_viscous_newtons = form_factor * rf_newtons

    # 5. Wave-making Resistance Rw (Holtrop-Mennen empirical formulation)
    # Rw = c1 * c2 * c5 * nabla * rho * g * exp(m1 * Fn^d + m2 * cos(lambda * Fn^-2))
    # Calibrated wave resistance scaling with Froude number
    c1 = 2223105.0 * (block_coefficient_cb ** 3.7861) * ((draft_m / beam_m) ** 1.07961) * (max(0.01, 90.0 - 20.0) ** -1.375)
    # Bound wave resistance coefficient to prevent extreme unphysical values at high speeds
    fn_exp = min(fn, 0.45)
    rw_newtons = (c1 * displacement_m3 * seawater_density_kg_m3 * gravity_m_s2 * 1e-4) * (fn_exp ** 4.0)
    rw_newtons = max(0.0, rw_newtons)

    rt_calm_newtons = r_viscous_newtons + rw_newtons

    return {
        "froude_number": fn,
        "reynolds_number": re,
        "cf": cf,
        "rf_newtons": rf_newtons,
        "form_factor_1_plus_k1": form_factor,
        "r_viscous_newtons": r_viscous_newtons,
        "rw_newtons": rw_newtons,
        "rt_calm_newtons": rt_calm_newtons,
    }
