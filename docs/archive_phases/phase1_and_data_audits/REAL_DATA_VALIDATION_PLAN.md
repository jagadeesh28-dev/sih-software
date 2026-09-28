# Real Maritime Operational Telemetry Validation Plan
**Document ID:** `PLAN-REAL-DATA-001`  
**Objective:** Define the definitive data specification and experimental protocol required to transition the Egreen Quanta prediction engine from `SYNTHETIC_TEST_DATA` to validated operational deployment.  
**Software Version:** 0.2.1 | **Git Commit:** `febed1ae38a3b2be34235dc6436b5fc7d493808b`  

---

## 1. Required Sensor Channels & Telemetry Schema

| Parameter | Required Field Name | Engineering Units | Sensor Source | Accuracy / Calibration Standard |
| :--- | :--- | :---: | :--- | :--- |
| **Timestamp** | `timestamp` | UTC ISO-8601 | GPS Clock / Integrated Bridge | <= 1.0 s synchronization error |
| **Vessel Identifier** | `vessel_id` | String | Static IMO Number | Unique vessel registration |
| **Fuel Mass Flow** | `fuel_mass_flow_kg_h` | kg/h | Coriolis Mass Flow Meter | ISO 11631 / +/- 0.2% mass flow accuracy |
| **Speed Through Water** | `stw_kn` | kn | Dual-axis Acoustic Doppler Log | +/- 0.1 kn, calibrated clean hull |
| **Speed Over Ground** | `sog_kn` | kn | DGPS / GNSS Receiver | +/- 0.05 kn |
| **Vessel Heading** | `heading_deg` | Degrees (0-360) | Gyrocompass / Satellite Compass | +/- 0.5 deg true heading |
| **Shaft Power** | `shaft_power_kw` | kW | Optical / Strain Gauge Torsionmeter | +/- 1.0% rated power |
| **Shaft RPM** | `rpm` | min^-1 | Inductive / Optical Shaft Encoder | +/- 0.2 RPM |
| **Shaft Torque** | `shaft_torque_nm` | N*m | Shaft Torsionmeter | +/- 1.0% |
| **Engine Load** | `engine_load_pct` | % | Engine Automation System (ECU) | +/- 1.0% MCR |
| **Static Draft (Fwd/Aft)** | `draft_m` | m | Radar / Pressure Draft Gauges | +/- 0.05 m (trimmed mean) |
| **Displacement** | `displacement_t` | Metric Tons (t) | Loading Computer / Hydrostatics | +/- 1.0% |
| **Significant Wave Height**| `wave_height_m` | m | X-Band Marine Wave Radar / Copernicus | +/- 0.2 m |
| **Peak Wave Period** | `wave_period_s` | s | Wave Radar / Reanalysis Metocean | +/- 0.5 s |
| **Wave Direction** | `wave_direction_deg` | Degrees (0-360) | Wave Radar / Metocean Hindcast | +/- 10 deg |
| **True Wind Speed** | `wind_speed_ms` | m/s | Ultrasonic Anemometer (height-corrected) | +/- 0.2 m/s at 10 m elevation |
| **True Wind Direction** | `wind_direction_deg` | Degrees (0-360) | Ultrasonic Anemometer | +/- 2.0 deg relative to true north |
| **Surface Current Speed** | `current_speed_ms` | m/s | Oceanographic Drift Reanalysis / ADCP | +/- 0.05 m/s |
| **Surface Current Direction**| `current_direction_deg`| Degrees (0-360) | Oceanographic Hindcast (Copernicus) | +/- 5.0 deg |
| **Fuel Type** | `fuel_type` | Categorical | Bunker Delivery Note (BDN) | ISO 8217 specification (HFO/VLSFO/MGO/LNG) |

---

## 2. Sampling Frequency & Data Volume Criteria
1. Raw sensor sampling rate >= 0.1 Hz (every 10 seconds), filtered to **15-minute steady-state operational averages** (ISO 19030).
2. Exclude maneuvering and transient states: STW >= 8.0 kn, |delta_rudder| <= 3.0 deg, |d(STW)/dt| <= 0.05 kn/min.
3. Minimum volume: >= 12 consecutive months per vessel; >= 25,000 steady-state operational intervals per vessel class.

---

## 3. Fleet Diversity & Holdout Requirements
1. Minimum 3 commercial shipping sectors with >= 2 sister vessels per class (Container Feeder, Bulk Carrier, MR2 Tanker).
2. Strict holdout: 6 months train -> 2 months val -> 4 months test; sister-vessel and cross-class holdout testing.

---

## 4. Operational Acceptance Criteria (Real-Data Gate)
1. ML-Only In-Domain: Test MAE <= 15.0 kg/h (MAPE <= 2.5%, R^2 >= 0.95).
2. Sister-Vessel Transfer: Test MAE <= 25.0 kg/h (MAPE <= 4.0%).
3. Calibrated Prediction Intervals: Nominal 90% coverage PICP in [86.0%, 94.0%].
4. Energy Conservation: Non-negative fuel rate and power across all operational states.

---

## 5. Current Data Status: Clear Boundary Classification

| Telemetry Component | Currently Available (Phase 2) | Required for Real Validation | Status |
| :--- | :--- | :--- | :---: |
| **Dataset Classification** | `SYNTHETIC_TEST_DATA` (DS-SYNTH-2026-01) | Real Vessel IoT Telemetry (Auto-logged) | **MISSING** |
| **Vessels Represented** | 3 synthetic hulls (FE_01, FE_02, HM_03) | >= 6 real physical commercial hulls | **MISSING** |
| **Time Horizon** | Short synthetic cruise series (N=1,203) | 12+ continuous months per vessel (N >= 25,000) | **MISSING** |
| **Sensor Accuracy** | Simulated Gaussian noise (+/- 5 kg/h) | Real Coriolis meter drift & sensor dropouts | **MISSING** |
| **Metocean Coupling** | Synthetic formulas (Hs^2, V_wind^2) | Real wave radar & Copernicus marine hindcasts | **MISSING** |
