"""
Aerodynamic wind resistance model for merchant vessels.
Reference: Blendermann (1994) empirical wind resistance dataset / Fujiwara et al. (1998).
"""

import math
from typing import Dict


def calculate_wind_resistance(
    relative_wind_speed_m_s: float,
    relative_wind_direction_rad: float,
    transverse_area_m2: float,
    lateral_area_m2: float,
    air_density_kg_m3: float = 1.225,
    cx_head: float = 0.70,
    cy_beam: float = 0.85,
) -> Dict[str, float]:
    """
    Calculate aerodynamic wind resistance on vessel superstructure.

    Inputs:
        relative_wind_speed_m_s: Apparent wind speed at reference height (m/s)
        relative_wind_direction_rad: Apparent wind angle (0 = head wind, pi = tail wind) (rad)
        transverse_area_m2: Frontal projected area above waterline (m^2)
        lateral_area_m2: Lateral projected area above waterline (m^2)
        air_density_kg_m3: Air density (kg/m^3)
        cx_head: Longitudinal drag coefficient in head wind [-]
        cy_beam: Transverse drag coefficient in beam wind [-]

    Returns:
        Dict containing:
            cx: Effective longitudinal drag coefficient [-]
            r_wind_longitudinal_newtons: Longitudinal wind force opposing motion (N)
    """
    if relative_wind_speed_m_s <= 0.0:
        return {"cx": 0.0, "r_wind_longitudinal_newtons": 0.0}

    # Blendermann approximation for longitudinal wind coefficient:
    # Cx(psi) = -CDl * cos(psi) / (1 - 0.5 * delta * sin^2(2*psi))
    # Standard simplified form:
    cos_psi = math.cos(relative_wind_direction_rad)
    sin_psi = math.sin(relative_wind_direction_rad)

    cx = cx_head * cos_psi / (1.0 - 0.18 * (sin_psi ** 2))

    dynamic_pressure = 0.5 * air_density_kg_m3 * (relative_wind_speed_m_s ** 2)
    r_wind_longitudinal = dynamic_pressure * transverse_area_m2 * cx

    return {
        "cx": cx,
        "r_wind_longitudinal_newtons": r_wind_longitudinal,
    }
