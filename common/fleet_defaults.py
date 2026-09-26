"""
Default operating states for the three FuelCast vessels, shared by the Streamlit
dashboard and the HTTP API. vessel_type matches the dataset; other values are
illustrative UI defaults (provenance: ASSUMED), not telemetry records.
"""

from typing import Any, Dict, List


def get_default_fleet_state() -> List[Dict[str, Any]]:
    """
    Representative default operating states for the three FuelCast vessels.
    vessel_type matches the dataset; the other values are illustrative UI defaults,
    not specific telemetry records.
    """
    return [
        {
            "id": "CPS_Poseidon",
            "name": "CPS_Poseidon",
            "vessel_type": "passenger_cruise",
            "fuel_type": "vlsfo",
            "speed_kn": 14.5,
            "stw_kn": 14.5,
            "sog_kn": 14.5,
            "draft_m": 7.5,
            "displacement_t": 35000.0,
            "gross_tonnage": 38000,
            "length_m": 196.0,
            "beam_m": 28.0,
            "engine_power_kw": 21600.0,
            "hotel_load_kw": 1800.0,
            "wind_speed_ms": 5.0,
            "wave_height_m": 1.0,
            "water_depth_m": 60.0,
            "route": "Rotterdam -> Bergen (North Sea)",
            "schedule_status": "ON TIME (+0.0 h)",
            "status": "ACTIVE_VOYAGE",
        },
        {
            "id": "CPS_Triton",
            "name": "CPS_Triton",
            "vessel_type": "passenger_cruise_small",
            "fuel_type": "vlsfo",
            "speed_kn": 14.0,
            "stw_kn": 14.0,
            "sog_kn": 14.2,
            "draft_m": 5.2,
            "displacement_t": 12000.0,
            "gross_tonnage": 14500,
            "length_m": 132.0,
            "beam_m": 21.0,
            "engine_power_kw": 10800.0,
            "hotel_load_kw": 900.0,
            "wind_speed_ms": 6.2,
            "wave_height_m": 1.2,
            "water_depth_m": 45.0,
            "route": "Stavanger -> Lerwick",
            "schedule_status": "ON TIME (+0.0 h)",
            "status": "ACTIVE_VOYAGE",
        },
        {
            "id": "OSS_Ceto",
            "name": "OSS_Ceto",
            "vessel_type": "offshore_supply",
            "fuel_type": "vlsfo",
            "speed_kn": 12.5,
            "stw_kn": 12.5,
            "sog_kn": 12.3,
            "draft_m": 4.8,
            "displacement_t": 4500.0,
            "gross_tonnage": 4800,
            "length_m": 88.0,
            "beam_m": 19.0,
            "engine_power_kw": 6400.0,
            "hotel_load_kw": 450.0,
            "wind_speed_ms": 7.5,
            "wave_height_m": 1.5,
            "water_depth_m": 85.0,
            "route": "Aberdeen -> Forties Alpha Field",
            "schedule_status": "ON TIME (+0.0 h)",
            "status": "ACTIVE_VOYAGE",
        },
    ]
