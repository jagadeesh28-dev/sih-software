"""
Moderate and monsoon weather scenario definitions.
"""

from typing import Dict, Any


def get_moderate_scenario() -> Dict[str, Any]:
    return {
        "name": "Moderate Sea (Beaufort 4)",
        "significant_wave_height_m": 1.5,
        "peak_wave_period_s": 7.0,
        "mean_wave_direction_deg": 15.0,
        "wind_speed_m_s": 7.5,
        "wind_direction_deg": 20.0,
        "current_speed_m_s": 0.5,
        "current_direction_deg": 10.0,
        "is_synthetic": True,
        "source": "Standard synthetic calibrated benchmark (WMO Sea State Code 4)",
    }


def get_monsoon_scenario() -> Dict[str, Any]:
    return {
        "name": "Monsoon Season Sea (Beaufort 6)",
        "significant_wave_height_m": 3.5,
        "peak_wave_period_s": 9.5,
        "mean_wave_direction_deg": 30.0,
        "wind_speed_m_s": 13.0,
        "wind_direction_deg": 35.0,
        "current_speed_m_s": 1.2,
        "current_direction_deg": 25.0,
        "is_synthetic": True,
        "source": "Standard synthetic calibrated benchmark (Arabian Sea SW Monsoon conditions)",
    }
