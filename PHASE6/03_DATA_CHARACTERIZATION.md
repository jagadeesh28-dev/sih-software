# PHASE 6 — STEP 3: EMPIRICAL TELEMETRY CHARACTERIZATION
## SIH26138 — Egreen Quanta
### High-Frequency Sensor Telemetry, Operating Regimes, and Distributional Analysis

**Date:** September 19, 2026  
**Dataset:** DTU FuelCast Open Commercial Shipping Telemetry  
**Total Records:** 173,974 valid observations  
**Vessels:** *CPS_Poseidon*, *CPS_Triton*, *OSS_Ceto*  
**Measurement Method:** Direct Coriolis mass-flow meters, dual Doppler log / EM log Speed Through Water (STW), GPS Speed Over Ground (SOG), metocean hindcast.

---

## 1. Fleet Telemetry Summary & Inventory

The real experimental dataset comprises 173,974 observations collected across three distinct commercial vessels operating in European and North Atlantic waters. The target variable is instantaneous fuel mass flow rate ($\text{kg/h}$), measured continuously by calibrated Coriolis mass-flow meters.

| Vessel Name | Vessel Class | Deadweight / Displacement | Telemetry Observations | Active Duration | Sampling Rate | Missingness (CONFIG_REAL_A) | Target Mean $\pm$ Std (kg/h) | Target Median (IQR) (kg/h) | STW Mean / P95 (kn) | Target Outliers (IQR) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Combined Fleet** | Multi-Class | Multi-Class | **173,974** | 366.0 days | 300 s (5 min) | **0.0007%** | **1,966.34 $\pm$ 1,648.51** | **1,351.34 (2,100.75)** | 7.96 / 20.20 kn | 4,402 (2.53%) |
| **CPS_Poseidon** | Container Feeder | 42,000 tonnes | 105,422 (60.6%) | 366.0 days | 300 s | 0.0000% | 2,815.40 $\pm$ 1,607.50 | 2,433.26 (2,168.88) | 9.81 / 20.64 kn | 1,249 (1.18%) |
| **CPS_Triton** | Container Feeder | 26,000 tonnes | 25,347 (14.6%) | 88.0 days | 300 s | 0.0025% | 635.14 $\pm$ 233.67 | 721.63 (290.93) | 10.20 / 15.20 kn | 210 (0.83%) |
| **OSS_Ceto** | Handymax Bulk | 45,000 tonnes | 43,205 (24.8%) | 150.0 days | 300 s | 0.0013% | 675.57 $\pm$ 375.32 | 631.09 (244.56) | 2.14 / 10.54 kn | 3,671 (8.50%) |

---

## 2. Statistical Analysis of Kinematic, Machinery, and Metocean Variables

### 2.1 Fuel Mass Flow Rate Distribution
- **Heavy-Tailed Skewness:** The combined fleet fuel flow shows a positive skewness of $+1.207$. *CPS_Poseidon* exhibits broad bimodal operational behavior corresponding to port/maneuvering standby ($<800\text{ kg/h}$) and full open-sea cruising ($2,500\text{--}5,500\text{ kg/h}$).
- In contrast, *CPS_Triton* displays negative skewness ($-0.901$), operating within a consistent coastal transit speed envelope with fuel consumption clustered tightly around $721\text{ kg/h}$.
- *OSS_Ceto* features high positive skewness ($+2.327$) with a long right tail up to $1,377\text{ kg/h}$ during ballast transit, with low baseline consumption due to extensive offshore idling and low-speed loitering.

### 2.2 Speed Through Water (STW) vs. Speed Over Ground (SOG)
- Across the fleet, mean STW ($7.96\text{ kn}$) and mean SOG ($7.66\text{ kn}$) show a consistent $+0.30\text{ kn}$ net current drift.
- The 95th percentile STW reaches $20.64\text{ kn}$ on *CPS_Poseidon*, $15.20\text{ kn}$ on *CPS_Triton*, and $10.54\text{ kn}$ on *OSS_Ceto*.
- High-speed cruising displays the characteristic cubic hydrodynamic resistance response ($P_B \propto V^3$), clearly visible in the empirical scatter profile.

### 2.3 Environmental Metocean Distributions
- **Wind Speed:** Fleet mean wind speed is $4.10\text{ m/s}$ (Beaufort Force 3), with severe gale peaks exceeding $22.0\text{ m/s}$. *CPS_Triton* experienced higher average wind exposure ($6.16\text{ m/s}$) during its winter North Sea voyages.
- **Wave Significant Height ($H_s$):** Fleet mean $H_s = 0.78\text{ m}$, with 95th percentile at $2.45\text{ m}$ and storm peaks up to $6.80\text{ m}$.

---

## 3. Operational Regimes & Outlier Decomposition

Telemetry was stratified into four primary operational regimes based on speed, maneuvering dynamics, and weather severity:
1. **Cruising ($V_{STW} \ge 8.0\text{ kn}, H_s < 3.0\text{ m}$):** Open-sea transit under steady hydrodynamic conditions. Governed primarily by calm-water resistance and engine load efficiency curves.
2. **Maneuvering ($2.0\text{ kn} \le V_{STW} < 8.0\text{ kn}$):** Harbor approach, pilotage, and channel navigation. Characterized by high transient engine acceleration and dynamic propeller slip.
3. **Stopped / Idling ($V_{STW} < 2.0\text{ kn}$):** Anchorages, port berthing, and dynamic positioning standby. Fuel flow is dominated by auxiliary boiler/generator loads rather than main propulsion.
4. **Rough Sea ($H_s \ge 3.0\text{ m}$ or $W \ge 15.0\text{ m/s}$):** Severe sea state with heavy ship motions, slamming risk, and added wave resistance.

### Sensor Anomalies and Quality Filtering:
- **Direct Coriolis Validation:** Fuel mass flow is direct gravimetric/mass measurement, eliminating volumetric thermal expansion errors typical of volumetric flowmeters.
- **Outlier Bounds:** Target outliers (2.53% of fleet) are physically valid high-power transient bursts during heavy sea conditions or rapid acceleration, rather than sensor dropouts.

---

## 4. Diagnostic Characterization Figures

The following diagnostic figures have been generated and stored in `PHASE6/results/figures/`:
1. `char_fig1_fuel_flow_distribution.png`: Empirical probability density distribution of Coriolis fuel mass flow across all three vessels.
2. `char_fig2_speed_vs_fuel.png`: Hydrodynamic cubic response profile comparing STW vs. fuel flow rate.
3. `char_fig3_engine_load_vs_fuel.png`: Empirical machinery load fraction vs. fuel consumption.
4. `char_fig4_vessel_distributions.png`: Telemetry boxplots highlighting median, interquartile ranges, and operational envelopes.
5. `char_fig5_temporal_drift.png`: 7-day rolling mean fuel flow over 366 days demonstrating seasonal and fouling drift.
6. `char_fig6_regime_distributions.png`: Operating regime frequency breakdown across the fleet.

---

## 5. Scientific Implications for Prediction Architecture

1. **Heterogeneity Barrier:** The significant variance in vessel displacement (26,000 t vs 45,000 t) and operational profiles means a pure data-driven model trained on one vessel cannot generalize to another without physics-based dimensionless scaling.
2. **First-Principles Necessity:** Because *OSS_Ceto* operates primarily at low speeds ($2.14\text{ kn}$ mean) while *CPS_Poseidon* cruises at high speeds ($9.81\text{ kn}$ mean), an empirical regression model risks severe extrapolation distortion unless constrained by first-principles resistance laws.
3. **Role of Quantum-Inspired Feature Selection:** With 14 candidate hydrodynamic and metocean features, evolutionary exploration (QIEA) must identify the subset that preserves cross-vessel invariance without overfitting to vessel-specific sensor correlations.
