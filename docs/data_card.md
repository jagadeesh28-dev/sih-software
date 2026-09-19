# Data Card: Egreen Quanta Telemetry & Preprocessing Specification
**Dataset Identifier**: FuelCast-Maritime-Real-v1.0  
**Status**: Frozen & Verified | **Audit Date**: September 2026  

---

## 1. Dataset Overview & High-Level Summary
The dataset underpinning the **Egreen Quanta** maritime fuel consumption prediction platform comprises real-world continuous sensor telemetry acquired from three commercial vessels operating under real oceanic conditions.

- **Raw Ingested Records**: `173,986` rows
- **Validated Cleaned Records**: `173,974` rows
- **Total Removed Records**: `12` rows ($0.0069\%$)
- **Data Source**: Commercial European ferry and offshore operations (FuelCast open telemetry corpus).

### Vessel Breakdown

| Vessel Identifier | Vessel Class | Telemetry Duration | Validated Record Count | SHA256 Data Hash (First 16 chars) |
|:------------------|:-------------|:-------------------|:-----------------------|:-----------------------------------|
| **CPS_Poseidon** | Large Passenger/RoPax Cruise Ferry | ~14 months | `105,422` | `da85f2e21b6e8724...` |
| **CPS_Triton** | Small Passenger Cruise Ferry | ~4 months | `25,347` | `fa8cc7f9f6a92d33...` |
| **OSS_Ceto** | Offshore Supply & Support Vessel | ~7 months | `43,205` | `ac3f8d5e865f11cd...` |
| **Fleet Total** | **3 Vessels** | **Multi-Season** | **173,974** | **Verified Frozen** |

---

## 2. Raw to Validated Cleaning Reconciliation
During the initial forensic data audit, an exact 12-row discrepancy was identified and cataloged between raw telemetry ingests (173,986) and downstream analysis sets (173,974):

### The 12 Removed Rows
- **Location**: Trailing rows at logger shutdown boundaries.
- **Root Cause**: Sensor dropout during automated telemetry daemon shutdown, resulting in `NULL` timestamps, invalid negative engine RPM, and NaN GPS coordinates.
- **Action**: Deterministically pruned during initial data validation. Zero interior records were discarded.
- **Reconciliation Audit**:
  $$\text{Raw Records (173,986)} - \text{Logger Shutdown Dropouts (12)} = \text{Validated Records (173,974)}$$

---

## 3. Sensor Provenance & Feature Definitions

### Target Variable
- **Feature Name**: `fuel_mass_flow_kg_h` (alias `fuel_oil_mass_flow_engine_total_kg_h`)
- **Physical Meaning**: Total mass flow rate of fuel consumed by main propulsion engines.
- **Measurement Units**: Kilograms per hour ($\text{kg/h}$).
- **Sensor Provenance**: Coriolis mass flow meters installed on engine fuel supply and return lines, computing $\dot{m}_{\text{net}} = \dot{m}_{\text{in}} - \dot{m}_{\text{out}}$.

### Input Features Contract (CONFIG_REAL_A)

| Feature Name | Physical Dimension | Standard Units | Physical Bound | Sensor / Source Description |
|:-------------|:-------------------|:---------------|:---------------|:----------------------------|
| `stw_kn` | Speed Through Water | Knots ($\text{kn}$) | $[0.0, 35.0]$ | Acoustic Doppler Current Profiler (ADCP) / Pitot log |
| `sog_kn` | Speed Over Ground | Knots ($\text{kn}$) | $[0.0, 35.0]$ | Differential GPS (DGPS) satellite navigation |
| `draft_m` | Mean Hull Draught | Meters ($\text{m}$) | $[1.0, 25.0]$ | Hydrostatic pressure transducers forward/aft |
| `displacement_t` | Vessel Total Displacement | Metric Tonnes ($\text{t}$) | $[500.0, 400000.0]$ | Calculated from draught and hydrostatic loading table |
| `wind_speed_ms` | Relative Wind Velocity | Meters/sec ($\text{m/s}$) | $[0.0, 60.0]$ | Ultrasonic mast-head anemometer |
| `wind_direction_deg` | Relative Wind Angle | Degrees ($^\circ$) | $[0.0, 360.0]$ | Mast-head wind vane |
| `wave_height_m` | Significant Wave Height ($H_s$) | Meters ($\text{m}$) | $[0.0, 20.0]$ | Marine radar / Copernicus Marine Service (CMEMS) reanalysis |
| `wave_period_s` | Peak Wave Period ($T_p$) | Seconds ($\text{s}$) | $[1.0, 30.0]$ | Marine radar / ECMWF hindcast |
| `wave_direction_deg` | Mean Wave Heading | Degrees ($^\circ$) | $[0.0, 360.0]$ | CMEMS wave direction relative to true north |
| `current_speed_ms` | Ocean Surface Current Speed | Meters/sec ($\text{m/s}$) | $[0.0, 6.0]$ | CMEMS ocean hydrodynamic current model |
| `current_direction_deg`| Current Direction | Degrees ($^\circ$) | $[0.0, 360.0]$ | CMEMS hydrodynamic vector bearing |
| `water_depth_m` | Bathymetric Water Depth | Meters ($\text{m}$) | $[2.0, 11000.0]$ | Echo sounder / GEBCO bathymetric chart |
| `vessel_type` | Vessel Operational Category | Categorical | 3 classes | `passenger_cruise`, `passenger_cruise_small`, `offshore_supply` |
| `fuel_type` | Conventional Bunkered Fuel | Categorical | 2 classes | `vlsfo` (Very Low Sulphur Fuel Oil), `mgo` (Marine Gas Oil) |

---

## 4. Train, Validation, and Test Splitting Protocol
To guarantee strict real-world applicability and eliminate data leakage, random k-fold cross-validation is strictly forbidden.

- **Protocol**: **Forward Temporal Split** executed independently per vessel.
- **Split Ratios**:
  - **Train**: First $60\%$ chronologically ($\mathbf{104,384\text{ rows}}$)
  - **Validation**: Subsequent $20\%$ chronologically ($\mathbf{34,794\text{ rows}}$)
  - **Test**: Final $20\%$ chronologically ($\mathbf{34,796\text{ rows}}$)
- **Leakage Prevention**:
  - Zero future data in training splits.
  - Conformal prediction quantiles calibrated *strictly* on the Validation split ($34,794$ records); zero test set tuning.
  - Domain envelope boundaries established exclusively from the Training split ($104,384$ records).

---

## 5. Known Limitations & Domain Constraints
1. **Limited Vessel Sample Size**: Telemetry represents exactly three specific hull geometries. Cross-vessel generalization to container mega-ships, bulkers, or VLCCs without vessel-specific fine-tuning is unverified.
2. **Conventional Fuel Ground Truth**: All empirical telemetry represents conventional petroleum hydrocarbons (`vlsfo`, `mgo`). Green fuel telemetry (methanol, ammonia, liquid hydrogen) is **not present** in the real data.
3. **Sensor Drift & Fouling**: Hull bio-fouling and propeller degradation over the 14-month recording span are implicit in the data and not separated from environmental resistance.
4. **Autonomous Control Prohibition**: This data is intended solely for offline decision-support, route evaluation, and operational advisory prototypes. It is not approved or certified for closed-loop autonomous ship navigation.
