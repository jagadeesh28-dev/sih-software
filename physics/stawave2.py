"""
Added resistance in regular and irregular waves using ITTC STAWAVE-2 method.
Reference: ITTC Recommended Procedure 7.5-02-07-02.2 (2021).
"""

import math
from typing import Dict


def calculate_added_wave_resistance(
    wave_height_m: float,
    wave_period_s: float,
    wave_direction_rad: float,
    beam_m: float,
    lwl_m: float,
    draft_m: float,
    speed_m_s: float,
    gravity_m_s2: float = 9.80665,
    seawater_density_kg_m3: float = 1025.0,
) -> Dict[str, float]:
    """
    Calculate added resistance in waves using the STAWAVE-2 formulation.

    Inputs:
        wave_height_m: Significant wave height Hs (m)
        wave_period_s: Peak wave period Tp (s)
        wave_direction_rad: Relative wave direction (0 = head waves, pi = following) (rad)
        beam_m: Moulded breadth (m)
        lwl_m: Length on waterline (m)
        draft_m: Vessel draft (m)
        speed_m_s: Vessel speed through water (m/s)
        gravity_m_s2: Gravitational acceleration (m/s^2)
        seawater_density_kg_m3: Seawater density (kg/m^3)

    Returns:
        Dict containing:
            wavelength_m: Deep water wavelength (m)
            r_wave_added_newtons: Added resistance in waves (N)
    """
    if wave_height_m <= 0.0 or wave_period_s <= 0.0:
        return {"wavelength_m": 0.0, "r_wave_added_newtons": 0.0}

    # Deep water dispersion relation: lambda = g * T^2 / (2 * pi)
    wavelength = (gravity_m_s2 * (wave_period_s ** 2)) / (2.0 * math.pi)

    # Wave frequency omega = 2 * pi / T
    omega = (2.0 * math.pi) / wave_period_s
    # Wave number k = 2 * pi / lambda
    k = (2.0 * math.pi) / max(wavelength, 1.0)

    # Head sea encounter effect cos(wave_direction_rad)
    head_sea_factor = max(0.0, math.cos(wave_direction_rad))

    # STAWAVE-2 diffraction/reflection component (raw_reflection)
    # Raw = 1/16 * rho * g * Hs^2 * B * alpha_1 * (1 + 5 * sqrt(L/g) * V / L)
    v_factor = 1.0 + 5.0 * (speed_m_s / math.sqrt(gravity_m_s2 * lwl_m))
    r_diffraction = (1.0 / 16.0) * seawater_density_kg_m3 * gravity_m_s2 * (wave_height_m ** 2) * beam_m * v_factor

    # Motion transfer function (peaked around resonance lambda / Lwl approx 1.0 to 1.2)
    lambda_ratio = wavelength / max(lwl_m, 1.0)
    # Motion peak factor
    motion_factor = math.exp(-((lambda_ratio - 1.1) ** 2) / 0.15)

    r_motion = 0.5 * seawater_density_kg_m3 * gravity_m_s2 * (wave_height_m ** 2) * (beam_m ** 2 / lwl_m) * motion_factor * v_factor

    total_added_resistance = (r_diffraction + r_motion) * head_sea_factor

    return {
        "wavelength_m": wavelength,
        "r_diffraction_newtons": r_diffraction,
        "r_motion_newtons": r_motion,
        "r_wave_added_newtons": total_added_resistance,
    }
