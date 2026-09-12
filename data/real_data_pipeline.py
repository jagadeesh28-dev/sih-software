"""
Real Maritime Telemetry Data Pipeline (FuelCast & In-situ Ingestion).
Stages 1 - 7:
- Ingestion of raw FuelCast parquet archives from data/external/fuelcast/
- Target conversion: Consumer_Total_MomentaryFuel (kg/s) -> fuel_mass_flow_kg_h (kg/h)
- Doppler log vs Vector Speed Through Water (STW) validation and derivation
- Canonical schema normalization matching SIH26138 data contract
- Operational regime classification
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from common.logger import get_logger

logger = get_logger(__name__)

VESSEL_SPECS = {
    "CPS_Poseidon": {
        "vessel_id": "CPS_Poseidon",
        "vessel_type": "passenger_cruise",
        "gt": 70000.0,
        "length_m": 260.0,
        "beam_m": 32.2,
        "design_draft_m": 7.5,
        "displacement_t": 42000.0,
        "rated_power_kw": 34000.0,
        "fuel_type": "vlsfo",
        "stw_source": "DIRECT_DOPPLER",
    },
    "CPS_Triton": {
        "vessel_id": "CPS_Triton",
        "vessel_type": "passenger_cruise_small",
        "gt": 11000.0,
        "length_m": 135.0,
        "beam_m": 20.0,
        "design_draft_m": 5.0,
        "displacement_t": 8500.0,
        "rated_power_kw": 5600.0,
        "fuel_type": "vlsfo",
        "stw_source": "DERIVED_VECTOR",
    },
    "OSS_Ceto": {
        "vessel_id": "OSS_Ceto",
        "vessel_type": "offshore_supply",
        "gt": 24000.0,
        "length_m": 90.0,
        "beam_m": 19.0,
        "design_draft_m": 6.0,
        "displacement_t": 6000.0,
        "rated_power_kw": 14500.0,
        "fuel_type": "mgo",
        "stw_source": "DERIVED_BEARING_VECTOR",
    },
}


def compute_vector_stw(
    sog_ms: np.ndarray,
    bearing_or_heading_deg: np.ndarray,
    curr_spd_ms: np.ndarray,
    curr_dir_deg: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute Speed Through Water vector from ground velocity and ocean current vectors.
    All velocities in m/s, angles in degrees (navigational azimuth).
    Returns (stw_ms, v_water_x, v_water_y).
    """
    theta_rad = np.radians(np.nan_to_num(bearing_or_heading_deg, nan=0.0))
    phi_rad = np.radians(np.nan_to_num(curr_dir_deg, nan=0.0))

    # Ground velocity vector (East, North)
    vg_x = sog_ms * np.sin(theta_rad)
    vg_y = sog_ms * np.cos(theta_rad)

    # Ocean current velocity vector (East, North)
    vc_x = curr_spd_ms * np.sin(phi_rad)
    vc_y = curr_spd_ms * np.cos(phi_rad)

    # Water-track velocity vector: V_water = V_ground - V_current
    vw_x = vg_x - vc_x
    vw_y = vg_y - vc_y

    stw_ms = np.sqrt(vw_x**2 + vw_y**2)
    return stw_ms, vw_x, vw_y


def classify_operating_regimes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Classify each observation into mutually exclusive primary operational regime,
    plus multi-label environmental tags.
    """
    sog = df["sog_kn"].values
    wave_h = df["wave_height_m"].values
    wind_s = df["wind_speed_ms"].values

    regimes = []
    for s, h, w in zip(sog, wave_h, wind_s):
        if s < 1.0:
            regimes.append("STOPPED_HARBOR")
        elif s < 6.0:
            regimes.append("MANEUVERING")
        elif s >= 18.0:
            regimes.append("HIGH_SPEED")
        elif h >= 2.5:
            regimes.append("ROUGH_SEA_CRUISING")
        else:
            regimes.append("NORMAL_CRUISING")

    df["operating_regime"] = regimes
    df["is_rough_sea"] = wave_h >= 2.5
    df["is_calm_sea"] = (wave_h < 1.0) & (sog >= 6.0)
    df["is_high_wind"] = wind_s >= 12.0
    df["is_low_wind"] = wind_s < 5.0
    return df


class RealMaritimeDataPipeline:
    """
    End-to-end ingestion, forensic validation, and canonical mapping for FuelCast.
    """

    def __init__(self, raw_dir: Path, processed_dir: Path):
        self.raw_dir = Path(raw_dir)
        self.processed_dir = Path(processed_dir)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def process_vessel(self, filename: str) -> pd.DataFrame:
        raw_path = self.raw_dir / filename
        if not raw_path.exists():
            raise FileNotFoundError(f"Raw dataset file not found: {raw_path}")

        vessel_key = Path(filename).stem
        specs = VESSEL_SPECS[vessel_key]
        logger.info(f"Processing real telemetry for {vessel_key} from {raw_path}")

        df_raw = pd.read_parquet(raw_path)

        # 1. Clean tail padding / invalid index rows
        if "index" in df_raw.columns:
            valid_idx_mask = df_raw["index"].notna()
            df = df_raw[valid_idx_mask].copy()
        else:
            df = df_raw.copy()

        # 2. Chronological sorting
        if "index" in df.columns:
            df["index"] = df["index"].astype(int)
            df = df.sort_values("index").reset_index(drop=True)

        n_rows = len(df)
        # Construct ISO-8601 UTC timestamp: 5-minute sampling interval (Delta t = 300 s)
        base_timestamp = pd.Timestamp("2024-01-01T00:00:00Z")
        df["timestamp"] = [
            (base_timestamp + pd.Timedelta(seconds=i * 300)).isoformat()
            for i in range(n_rows)
        ]

        # 3. Target provenance conversion: Consumer_Total_MomentaryFuel (kg/s) -> (kg/h)
        # F_kg_h = F_kg_s * 3600.0
        fuel_kg_s = df["Consumer_Total_MomentaryFuel"].astype(float).values
        df["fuel_mass_flow_kg_h"] = np.maximum(0.0, fuel_kg_s * 3600.0)

        # 4. Speeds (m/s -> knots, 1 m/s = 1.94384 kn)
        raw_sog = pd.to_numeric(df["Ship_SpeedOverGround"], errors="coerce").ffill().bfill().fillna(0.0)
        sog_ms = np.maximum(0.0, raw_sog.values)
        df["sog_ms"] = sog_ms
        df["sog_kn"] = sog_ms * 1.94384

        raw_curr_v = pd.to_numeric(df["Weather_OceanCurrentVelocity"], errors="coerce").ffill().bfill().fillna(0.0)
        curr_spd_ms = np.maximum(0.0, raw_curr_v.values)
        curr_dir_deg = pd.to_numeric(df["Weather_OceanCurrentDirection"], errors="coerce").ffill().bfill().fillna(0.0).values
        df["current_speed_ms"] = curr_spd_ms
        df["current_direction_deg"] = curr_dir_deg

        if "Ship_Heading" in df.columns:
            heading_deg = pd.to_numeric(df["Ship_Heading"], errors="coerce").ffill().bfill().fillna(0.0).values
        else:
            heading_deg = pd.to_numeric(df["Ship_Bearing"], errors="coerce").ffill().bfill().fillna(0.0).values
        bearing_deg = pd.to_numeric(df["Ship_Bearing"], errors="coerce").ffill().bfill().fillna(0.0).values
        df["heading_deg"] = heading_deg
        df["bearing_deg"] = bearing_deg

        # Vector STW calculation across all vessels
        vector_stw_ms, _, _ = compute_vector_stw(
            sog_ms, heading_deg, curr_spd_ms, curr_dir_deg
        )
        vector_stw_ms = np.nan_to_num(vector_stw_ms, nan=0.0)
        df["vector_stw_ms"] = vector_stw_ms
        df["vector_stw_kn"] = vector_stw_ms * 1.94384

        # Specific STW assignment based on sensor audit
        if vessel_key == "CPS_Poseidon":
            # Direct Doppler speed log with vector fallback for port / acoustic dropout periods
            raw_stw = pd.to_numeric(df["Ship_SpeedThroughWater"], errors="coerce")
            stw_ms = np.where(raw_stw.notna(), raw_stw.values, vector_stw_ms)
            stw_ms = np.maximum(0.0, np.nan_to_num(stw_ms, nan=0.0))
            df["stw_ms"] = stw_ms
            df["stw_kn"] = stw_ms * 1.94384
            df["stw_status"] = "DIRECT_DOPPLER"
            df["stw_vector_residual_ms"] = np.abs(stw_ms - vector_stw_ms)
        elif vessel_key == "CPS_Triton":
            # Doppler log is corrupted/frozen at exactly 1.0 kn (0.5144 m/s)
            df["stw_raw_kn"] = (
                pd.to_numeric(df["Ship_SpeedThroughWater"], errors="coerce").fillna(0.514444).values * 1.94384
            )
            df["stw_ms"] = vector_stw_ms
            df["stw_kn"] = df["vector_stw_kn"]
            df["stw_status"] = "DERIVED_VECTOR"
        else:  # OSS_Ceto
            # Direct STW missing
            df["stw_ms"] = vector_stw_ms
            df["stw_kn"] = df["vector_stw_kn"]
            df["stw_status"] = "DERIVED_BEARING_VECTOR"

        # 5. Draft and displacement
        if (
            "Ship_DraftFore" in df.columns
            and "Ship_DraftAft" in df.columns
            and df["Ship_DraftFore"].notna().any()
        ):
            d_fore = df["Ship_DraftFore"].astype(float).values
            d_aft = df["Ship_DraftAft"].astype(float).values
            df["draft_fore_m"] = d_fore
            df["draft_aft_m"] = d_aft
            df["draft_m"] = (d_fore + d_aft) / 2.0
        else:
            df["draft_m"] = specs["design_draft_m"]
            df["draft_fore_m"] = specs["design_draft_m"]
            df["draft_aft_m"] = specs["design_draft_m"]

        df["displacement_t"] = specs["displacement_t"]

        # 6. Machinery features (Machinery-Aware CONFIG-B)
        if "Propeller_Total_ShaftPower" in df.columns:
            p_w = np.maximum(
                0.0, df["Propeller_Total_ShaftPower"].astype(float).values
            )
        elif "Consumer_Total_ShaftPower" in df.columns:
            p_w = np.maximum(
                0.0, df["Consumer_Total_ShaftPower"].astype(float).values
            )
        else:
            p_w = np.zeros(n_rows)
        df["shaft_power_kw"] = p_w / 1000.0

        # RPM
        rpm_cols = [c for c in df.columns if "RotationSpeed" in c]
        prop_rpm_cols = [c for c in rpm_cols if "Propeller" in c]
        if prop_rpm_cols:
            df["rpm"] = df[prop_rpm_cols].mean(axis=1).fillna(0.0).values
        elif rpm_cols:
            df["rpm"] = df[rpm_cols].mean(axis=1).fillna(0.0).values
        else:
            df["rpm"] = 0.0

        # Torque (Nm)
        if vessel_key == "CPS_Poseidon":
            port_t = df["Propeller_Port_ShaftTorque"].astype(float).fillna(0.0)
            stbd_t = df["Propeller_Starboard_ShaftTorque"].astype(float).fillna(0.0)
            df["shaft_torque_nm"] = (port_t + stbd_t).values
        elif vessel_key == "CPS_Triton":
            port_t = df["Propeller_Port_ShaftTorque"].astype(float).fillna(0.0)
            stbd_t = df["Propeller_Starboard_ShaftTorque"].astype(float).fillna(0.0)
            df["shaft_torque_nm"] = ((port_t + stbd_t) * 1000.0).values
        else:  # OSS_Ceto
            # Compute torque from shaft power and RPM
            rpm_safe = np.where(df["rpm"].values > 10.0, df["rpm"].values, np.nan)
            omega = 2.0 * np.pi * (rpm_safe / 60.0)
            torque_calc = (df["shaft_power_kw"].values * 1000.0) / omega
            df["shaft_torque_nm"] = np.nan_to_num(torque_calc, nan=0.0)

        # Engine load fraction
        rated_p = specs["rated_power_kw"]
        df["engine_load_pct"] = np.clip(
            (df["shaft_power_kw"].values / rated_p) * 100.0, 0.0, 110.0
        )

        # 7. Environmental Metocean
        w_spd = pd.to_numeric(df["Weather_WindSpeed10M"], errors="coerce").ffill().bfill().fillna(0.0).values
        df["wind_speed_ms"] = np.maximum(0.0, w_spd)

        w_dir = pd.to_numeric(df["Weather_WindDirection10M"], errors="coerce").ffill().bfill().fillna(0.0).values
        df["wind_direction_deg"] = w_dir % 360.0

        w_h = pd.to_numeric(df["Weather_WaveHeight"], errors="coerce").ffill().bfill().fillna(0.0).values
        df["wave_height_m"] = np.maximum(0.0, w_h)

        w_p = pd.to_numeric(df["Weather_WavePeriod"], errors="coerce").ffill().bfill().fillna(5.0).values
        df["wave_period_s"] = np.maximum(1.0, w_p)

        w_d = pd.to_numeric(df["Weather_WaveDirection"], errors="coerce").ffill().bfill().fillna(0.0).values
        df["wave_direction_deg"] = w_d % 360.0

        depth = pd.to_numeric(df["Environment_SeaFloorDepth"], errors="coerce").ffill().bfill().fillna(100.0).values
        df["water_depth_m"] = np.maximum(5.0, depth)

        # 8. Categoricals / Identifiers
        df["vessel_id"] = specs["vessel_id"]
        df["vessel_type"] = specs["vessel_type"]
        df["fuel_type"] = specs["fuel_type"]

        # 9. Regime classification
        df = classify_operating_regimes(df)

        # Save processed parquet
        out_path = self.processed_dir / f"{vessel_key}.parquet"
        df.to_parquet(out_path, index=False)
        logger.info(
            f"Successfully saved {len(df)} processed rows for {vessel_key} to {out_path}"
        )
        return df

    def run_all(self) -> Dict[str, pd.DataFrame]:
        datasets = {}
        for vessel_file in ["CPS_Poseidon.parquet", "CPS_Triton.parquet", "OSS_Ceto.parquet"]:
            df = self.process_vessel(vessel_file)
            datasets[Path(vessel_file).stem] = df
        return datasets
