"""
Calm weather metocean scenario definition.
Beaufort 2 baseline sea state.
"""

from typing import Dict, Any


def get_calm_scenario() -> Dict[str, Any]:
    return {
        "name": "Calm Sea (Beaufort 2)",
        "significant_wave_height_m": 0.5,
        "peak_wave_period_s": 5.0,
        "mean_wave_direction_deg": 0.0,
        "wind_speed_m_s": 3.0,
        "wind_direction_deg": 0.0,
        "current_speed_m_s": 0.2,
        "current_direction_deg": 0.0,
        "is_synthetic": True,
        "source": "Standard synthetic calibrated benchmark (WMO Sea State Code 2)",
    }
