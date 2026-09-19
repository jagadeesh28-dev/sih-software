# Data Card: DTU FuelCast Maritime Telemetry
### SIH26138 — Egreen Quanta (v1.0.0)

This data card details the origin, sampling characteristics, preprocessing provenance, and operational boundaries of the empirical maritime sensor telemetry used in Egreen Quanta.

---

## 1. Dataset Overview & Provenance

- **Origin / Custodian:** Technical University of Denmark (DTU) & Marine Data Research Consortium.
- **Dataset Name:** DTU FuelCast High-Frequency Commercial Maritime Sensor Archive.
- **Licensing:** Open Academic Research License (non-commercial benchmarking permitted).
- **Physical Sampling Duration:** 604 operational vessel-days.
- **Telemetry Frequency:** 1-minute to 5-minute continuous sensor logging aggregated into high-fidelity tabular observations.

---

## 2. Canonical Record Count Reconciliation

| Telemetry Partition | Physical Hull Category | Raw Ingested Records | Dropped Padding Rows | Validated Operational Records |
| :--- | :--- | :---: | :---: | :---: |
| **`CPS_Poseidon`** | Container Ship (Feeder) | 105,422 | 0 | **105,422** |
| **`CPS_Triton`** | Small Container / Feeder | 25,351 | 4 | **25,347** |
| **`OSS_Ceto`** | Bulk Handymax / Offshore Service | 43,213 | 8 | **43,205** |
| **Total Fleet** | **3 Commercial Vessels** | **173,986** | **12** | **173,974** |

**Canonical Terminology:**
- **RAW DATASET SIZE:** `173,986` records.
- **VALIDATED EXPERIMENTAL SAMPLE SIZE:** `173,974` operational records.
- **Explanation of Difference:** Exactly 12 trailing padding rows contained null timestamps and sensor dropouts caused by recording device shutdown; safely dropped during Phase 2.3 data quality cleaning (`PHASE7/results/data_count_reconciliation.csv`).

---

## 3. Sensor Instrumentation & Measured Target

- **Target Variable:** `fuel_mass_flow_kg_h` (Main engine instantaneous fuel consumption rate in kilograms per hour).
- **Measurement Instrumentation:** Direct onboard Coriolis mass flow meters (independent of volumetric fuel density fluctuations).
- **Key Predictors:**
  - `stw_kn`: Doppler acoustic water-track log measuring Speed Through Water.
  - `sog_kn`: Differential GPS navigation measuring Speed Over Ground.
  - `draft_m` & `displacement_t`: Hydrostatic pressure transducers and draft sensors.
  - `wind_speed_ms` & `wind_direction_deg`: Ultrasonic mast anemometers.
  - `wave_height_m` & `wave_period_s`: ECMWF ERA5 wave reanalysis synced to GPS coordinates.
  - `current_speed_ms` & `current_direction_deg`: Ocean surface drift models.
  - `water_depth_m`: Multibeam bathymetric sounder.

---

## 4. Known Biases & Generalization Boundaries

1. **Weather Bias:** The majority of operational voyages took place in European coastal waters (North Sea, Baltic Sea, English Channel). High sea states ($H_s > 6\text{ m}$) are underrepresented.
2. **Fuel Type:** Sensor telemetry was recorded exclusively on conventional bunker oils (VLSFO and MGO). Alternative fuels are modeled as thermodynamic scenarios via invariant mechanical shaft work.
3. **Zero-Shot Transfer Limitation:** Models trained on one hull cannot be transferred zero-shot to a different hull without recalibration due to unique hydrodynamic block coefficients ($C_B$) and engine curves.
