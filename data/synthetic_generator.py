"""
Controlled Synthetic Telemetry Generator with Model Mismatch.
Section 8: Generates physically plausible maritime operational records ONLY for software validation.
Explicitly labels all data with dataset_type = 'SYNTHETIC_TEST_DATA'.
Injects controlled model mismatch:
  F_synthetic = F_physics_reference + operational_residual + measurement_noise
incorporating non-linear load-dependent SFC variations, hull fouling/aging variance,
environmental non-linear interactions, and measurement noise to prevent circular verification.
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np
import pandas as pd


def generate_synthetic_maritime_dataset(
    n_records: int = 1200,
    seed: int = 42,
    output_path: Optional[Path] = None,
    inject_anomalies: bool = True,
    inject_model_mismatch: bool = True,
) -> pd.DataFrame:
    """
    Generate synthetic maritime observation dataset adhering strictly to canonical schema.
    Incorporates controlled model mismatch to prevent circular validation with theoretical physics.
    """
    rng = np.random.default_rng(seed)

    vessel_configs = [
        {
            "vessel_id": "VESSEL_FE_01",
            "vessel_type": "container_feeder",
            "sister_group_id": "CLASS_FEEDER_1000",
            "mean_speed": 15.0,
            "mean_draft": 8.0,
            "displacement": 15200.0,
            "max_power": 15000.0,
            "base_sfc": 178.0,
            "calm_coeff": 0.48,
        },
        {
            "vessel_id": "VESSEL_FE_02",  # Sister vessel to 01
            "vessel_type": "container_feeder",
            "sister_group_id": "CLASS_FEEDER_1000",
            "mean_speed": 14.8,
            "mean_draft": 8.1,
            "displacement": 15300.0,
            "max_power": 15000.0,
            "base_sfc": 180.0,
            "calm_coeff": 0.49,
        },
        {
            "vessel_id": "VESSEL_HM_03",
            "vessel_type": "bulk_handymax",
            "sister_group_id": "CLASS_HANDYMAX_50K",
            "mean_speed": 13.5,
            "mean_draft": 11.5,
            "displacement": 58000.0,
            "max_power": 9000.0,
            "base_sfc": 172.0,
            "calm_coeff": 0.58,
        },
    ]

    records = []
    start_time = datetime(2026, 3, 1, 0, 0, 0, tzinfo=timezone.utc)
    interval_seconds = 300  # 5 minute sampling

    records_per_vessel = n_records // len(vessel_configs)

    for v_cfg in vessel_configs:
        curr_time = start_time
        lat = 18.9220  # Near Mumbai
        lon = 72.8347
        heading_deg = 65.0  # Nominal northeast passage

        for i in range(records_per_vessel):
            # 1. Speed Through Water (STW) is the primary hydrodynamic speed
            stw_kn = float(np.clip(rng.normal(v_cfg["mean_speed"], 1.2), 7.5, 21.0))

            # Environmental conditions
            wave_h = float(np.clip(rng.normal(1.5, 0.5), 0.2, 5.5))
            wave_p = float(np.clip(rng.normal(7.0, 1.2), 3.0, 14.0))
            wave_dir = float(rng.uniform(0.0, 360.0))
            wind_s = float(np.clip(rng.normal(7.5, 2.5), 1.0, 22.0))
            wind_dir = float(rng.uniform(0.0, 360.0))
            curr_s = float(np.clip(rng.normal(0.5, 0.2), 0.0, 2.2))  # m/s
            curr_dir = float(rng.uniform(0.0, 360.0))

            # Current in knots and along-track velocity component
            curr_kn = curr_s * 1.94384
            curr_along_kn = curr_kn * float(np.cos(np.radians(curr_dir - heading_deg)))

            # Speed Over Ground (SOG): Vector sum of STW and along-track current
            sog_kn = float(np.clip(stw_kn + curr_along_kn + rng.normal(0.0, 0.04), 4.5, 23.0))

            # Headway drift based on SOG
            lat += (sog_kn * 0.514444 * interval_seconds / 111139.0) * 0.3
            lon += (sog_kn * 0.514444 * interval_seconds / 111139.0) * 0.7

            # Draft & displacement
            draft_m = float(v_cfg["mean_draft"] + rng.normal(0.0, 0.05))
            displacement_t = float(v_cfg["displacement"])

            # 2. Physics Reference Power (using STW)
            # Cubic calm-water resistance
            p_calm_ref = v_cfg["calm_coeff"] * (stw_kn ** 3.0) * ((draft_m / v_cfg["mean_draft"]) ** 0.6)
            # Added resistance from wave and wind
            rel_wave_angle = np.radians(wave_dir - heading_deg)
            p_wave_ref = (wave_h ** 2.0) * 110.0 * float(np.maximum(0.2, np.cos(rel_wave_angle)))
            rel_wind_angle = np.radians(wind_dir - heading_deg)
            p_wind_ref = 0.4 * (wind_s ** 2.0) * float(np.maximum(0.1, np.cos(rel_wind_angle)))
            p_phys_ref = p_calm_ref + p_wave_ref + p_wind_ref

            if inject_model_mismatch:
                # Controlled Model Mismatch:
                # a) Non-linear model-form mismatch: wave-making hump changes effective power exponent to ~3.15
                power_mismatch = 0.05 * (stw_kn ** 3.15) - 0.04 * (stw_kn ** 3.0)
                # b) Environmental non-linear coupling: wave-wind interaction increases resistance non-linearly
                env_interaction = 12.0 * (wave_h * wind_s / 10.0)
                # c) Operational power with engine efficiency variance
                engine_efficiency_drift = float(rng.normal(0.0, 0.02))
                power_kw = float(np.clip(
                    (p_phys_ref + power_mismatch + env_interaction) * (1.0 + engine_efficiency_drift),
                    450.0,
                    v_cfg["max_power"],
                ))

                load_pct = float(np.clip((power_kw / v_cfg["max_power"]) * 100.0, 8.0, 96.0))
                load_frac = load_pct / 100.0

                # d) Non-linear SFC bathtub curve deviation: higher SFC at very low and very high loads
                sfc_mismatch = v_cfg["base_sfc"] * (1.0 + 0.30 * ((load_frac - 0.75) ** 2.0) - 0.04 * ((load_frac - 0.5) ** 3.0))
                # e) Telemetry sensor measurement noise
                meas_noise = float(rng.normal(0.0, 5.0))

                fuel_flow_kg_h = float(np.clip(
                    (power_kw * sfc_mismatch / 1000.0) + meas_noise,
                    120.0,
                    3600.0,
                ))
            else:
                power_kw = float(np.clip(p_phys_ref, 450.0, v_cfg["max_power"]))
                load_pct = float(np.clip((power_kw / v_cfg["max_power"]) * 100.0, 8.0, 96.0))
                fuel_flow_kg_h = float(np.clip((power_kw * v_cfg["base_sfc"] / 1000.0), 120.0, 3600.0))

            rpm = float(np.clip(68.0 + 3.6 * stw_kn, 38.0, 142.0))

            rec = {
                "dataset_type": "SYNTHETIC_TEST_DATA",
                "timestamp": curr_time.isoformat(),
                "vessel_id": v_cfg["vessel_id"],
                "vessel_type": v_cfg["vessel_type"],
                "sister_group_id": v_cfg["sister_group_id"],
                "latitude": float(lat),
                "longitude": float(lon),
                "sog_kn": sog_kn,
                "stw_kn": stw_kn,
                "draft_m": draft_m,
                "displacement_t": displacement_t,
                "rpm": rpm,
                "shaft_power_kw": power_kw,
                "shaft_torque_nm": float((power_kw * 1000.0) / (2.0 * np.pi * (rpm / 60.0))),
                "fuel_mass_flow_kg_h": fuel_flow_kg_h,
                "wind_speed_ms": wind_s,
                "wind_direction_deg": wind_dir,
                "wave_height_m": wave_h,
                "wave_period_s": wave_p,
                "wave_direction_deg": wave_dir,
                "current_speed_ms": curr_s,
                "current_direction_deg": curr_dir,
                "water_depth_m": float(rng.uniform(40.0, 800.0)),
                "cargo_mass_t": float(v_cfg["displacement"] * 0.65),
                "cargo_demand_t": float(v_cfg["displacement"] * 0.65),
                "engine_load_pct": load_pct,
                "fuel_type": "vlsfo",
            }
            records.append(rec)
            curr_time += timedelta(seconds=interval_seconds)

    df = pd.DataFrame(records)

    # --- Controlled Anomaly Injections for Quality Auditor Validation ---
    if inject_anomalies:
        n = len(df)
        # 1. Missing values in fuel_mass_flow_kg_h and water_depth_m
        df.loc[rng.choice(n, size=5, replace=False), "fuel_mass_flow_kg_h"] = np.nan
        df.loc[rng.choice(n, size=10, replace=False), "water_depth_m"] = np.nan

        # 2. Duplicate records (duplicate 3 random rows)
        dup_indices = rng.choice(n, size=3, replace=False)
        dups = df.iloc[dup_indices].copy()
        df = pd.concat([df, dups], ignore_index=True)

        # 3. Impossible coordinates (lat > 90, lon < -180)
        df.loc[10, "latitude"] = 95.5
        df.loc[11, "longitude"] = -195.0

        # 4. Negative fuel flow & negative wave height
        df.loc[25, "fuel_mass_flow_kg_h"] = -120.0
        df.loc[26, "wave_height_m"] = -2.5

        # 5. Timestamp gap: push one timestamp 4 hours forward
        t_jump = pd.to_datetime(df.loc[50, "timestamp"]) + timedelta(hours=4)
        df.loc[50, "timestamp"] = t_jump.isoformat()

        # 6. Impossible combination: high speed with 0 power & 0 RPM
        df.loc[80, "sog_kn"] = 22.0
        df.loc[80, "shaft_power_kw"] = 0.0
        df.loc[80, "rpm"] = 0.0

        # 7. SOG / STW / Current consistency anomalies
        df.loc[27, "stw_kn"] = -4.0
        df.loc[28, "sog_kn"] = -2.0
        df.loc[29, "current_speed_ms"] = 9.5
        df.loc[30, "sog_kn"] = 20.0
        df.loc[30, "stw_kn"] = 8.0
        df.loc[30, "current_speed_ms"] = 0.2  # 12 kn gap with 0.2 m/s current

    if output_path:
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out_p, index=False)

    return df


if __name__ == "__main__":
    out_file = Path(__file__).resolve().parent / "synthetic" / "synthetic_vessel_telemetry.csv"
    df_gen = generate_synthetic_maritime_dataset(output_path=out_file)
    print(f"Generated {len(df_gen)} synthetic telemetry records at {out_file}")
