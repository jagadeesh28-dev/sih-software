"""
Physics-Only Baseline Fuel Consumption Predictor.
Section 2 & 3: Hydrodynamic first-principles pipeline locked strictly to STW:
  stw_kn -> calm-water resistance -> wave added resistance -> wind resistance
         -> total resistance -> effective power -> delivered/shaft power
         -> engine brake power -> SFC -> fuel_mass_flow_kg_h.

Silent substitution of SOG for STW is strictly forbidden.
Returns:
- predicted_fuel_kg_h
- predicted_power_kw
- total_resistance_n
- resistance_components
- physics_diagnostics
"""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

import warnings

from physics.resistance_model import VesselResistanceModel

# Hull profiles with published dimensions in configs/physics.yaml.
REFERENCE_HULL_PROFILES = {"container_feeder", "bulk_handymax"}

# The FuelCast vessels have no public hull dimensions, so the physics baseline runs on a
# declared proxy hull. MODEL-REAL-04 / QI-C1 residuals were trained against exactly this
# proxy baseline and absorb the hull mismatch; changing it invalidates the frozen models.
PROXY_HULL_PROFILES = {
    "passenger_cruise": "container_feeder",        # CPS_Poseidon
    "passenger_cruise_small": "container_feeder",  # CPS_Triton
    "offshore_supply": "container_feeder",         # OSS_Ceto
}


def resolve_hull_profile(vessel_type: str, default: str = "container_feeder") -> tuple:
    """Return (hull_profile, is_proxy). Unknown vessel types warn instead of mapping silently."""
    if vessel_type in REFERENCE_HULL_PROFILES:
        return vessel_type, False
    if vessel_type in PROXY_HULL_PROFILES:
        return PROXY_HULL_PROFILES[vessel_type], True
    warnings.warn(
        f"No hull profile for vessel_type '{vessel_type}'; physics baseline uses generic "
        f"'{default}' hull. Treat physics output as low-confidence.",
        RuntimeWarning,
        stacklevel=3,
    )
    return default, True


class PhysicsFuelPredictor:
    """
    Theoretical first-principles hydrodynamic and propulsion fuel predictor.
    Requires no ML training; evaluates naval architecture models using Speed Through Water (STW).
    """

    def __init__(self, default_vessel_type: str = "container_feeder"):
        self.default_vessel_type = default_vessel_type
        # Cache models for each vessel type to avoid reloading configs per record
        self._vessel_models: Dict[str, VesselResistanceModel] = {}
        self._hull_profiles: Dict[str, tuple] = {}

    def _get_model(self, vessel_type: str) -> VesselResistanceModel:
        if vessel_type not in self._vessel_models:
            profile, is_proxy = resolve_hull_profile(vessel_type, self.default_vessel_type)
            self._hull_profiles[vessel_type] = (profile, is_proxy)
            self._vessel_models[vessel_type] = VesselResistanceModel(vessel_type=profile)
        return self._vessel_models[vessel_type]

    def predict_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a single telemetry observation through the hydrodynamic pipeline.
        STW is strictly required as the primary hydrodynamic speed.
        """
        if "stw_kn" not in record or record["stw_kn"] is None or pd.isna(record["stw_kn"]):
            raise ValueError(
                "Missing 'stw_kn': Hydrodynamic physics pipeline requires Speed Through Water (STW). "
                "Silent substitution with SOG is forbidden to prevent hydrodynamic velocity distortion."
            )

        stw_kn = float(record["stw_kn"])
        v_type = str(record.get("vessel_type", self.default_vessel_type))
        model = self._get_model(v_type)

        wave_h = float(record.get("wave_height_m", 0.0))
        wave_p = float(record.get("wave_period_s", 0.0))
        wave_d = float(record.get("wave_direction_deg", 0.0))
        wind_s = float(record.get("wind_speed_ms", 0.0))
        wind_d = float(record.get("wind_direction_deg", 0.0))

        # Full resistance and propulsion pipeline
        res = model.compute_total_resistance(
            speed_knots=stw_kn,
            wave_height_m=wave_h,
            wave_period_s=wave_p,
            wave_direction_deg=wave_d,
            wind_speed_m_s=wind_s,
            wind_direction_deg=wind_d,
        )

        r_total = float(res["r_total_newtons"])
        pb_kw = float(res["power"]["pb_kw"])
        fuel_kg_h = float(res["fuel"]["total_fuel_kg_h"])

        return {
            "predicted_fuel_kg_h": fuel_kg_h,
            "predicted_power_kw": pb_kw,
            "total_resistance_n": r_total,
            "resistance_components": {
                "r_calm_newtons": float(res["r_calm_newtons"]),
                "r_wave_newtons": float(res["r_wave_newtons"]),
                "r_wind_newtons": float(res["r_wind_newtons"]),
                "r_total_newtons": r_total,
            },
            "physics_diagnostics": {
                "stw_kn": stw_kn,
                "speed_m_s": float(res["speed_m_s"]),
                "pe_kw": float(res["power"]["pe_kw"]),
                "pd_kw": float(res["power"]["pd_kw"]),
                "pb_kw": pb_kw,
                "eta_d": float(res["power"]["eta_d"]),
                "eta_s": float(res["power"].get("eta_s", 0.98)),
                "engine_load_fraction": float(res["fuel"]["load_fraction"]),
                "effective_sfc_g_kwh": float(res["fuel"]["effective_sfc_g_kwh"]),
                "hull_profile": self._hull_profiles[v_type][0],
                "hull_profile_is_proxy": self._hull_profiles[v_type][1],
            },
        }

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """
        Vectorized/batch prediction returning array of predicted fuel mass flow rates (kg/h).
        Requires 'stw_kn' in df.
        """
        predictions = []
        for _, row in df.iterrows():
            rec = row.to_dict()
            out = self.predict_record(rec)
            predictions.append(out["predicted_fuel_kg_h"])
        return np.array(predictions, dtype=float)

    def predict_detailed(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Batch prediction returning full diagnostic DataFrame.
        """
        records = []
        for idx, row in df.iterrows():
            rec = row.to_dict()
            out = self.predict_record(rec)
            records.append({
                "predicted_fuel_kg_h": out["predicted_fuel_kg_h"],
                "predicted_power_kw": out["predicted_power_kw"],
                "total_resistance_n": out["total_resistance_n"],
                "r_calm_n": out["resistance_components"]["r_calm_newtons"],
                "r_wave_n": out["resistance_components"]["r_wave_newtons"],
                "r_wind_n": out["resistance_components"]["r_wind_newtons"],
                "r_total_n": out["resistance_components"]["r_total_newtons"],
                "stw_kn": out["physics_diagnostics"]["stw_kn"],
                "engine_load_fraction": out["physics_diagnostics"]["engine_load_fraction"],
                "effective_sfc_g_kwh": out["physics_diagnostics"]["effective_sfc_g_kwh"],
            })
        return pd.DataFrame(records, index=df.index)
