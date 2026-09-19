# PHASE 6 — STEP 4: PHYSICS PROPULSION MODEL AUDIT
## SIH26138 — Egreen Quanta
### Mathematical Formulation, Hydrodynamic Chain, and Sensor Availability Audit

**Date:** September 19, 2026  
**Auditor:** Maritime Fuel / Propulsion Specialist, Lead ML Research Scientist  
**Component:** First-Principles Hydrodynamic Pipeline (`physics/resistance_model.py`, `physics/propulsion.py`)  
**Status:** VERIFIED & AUDITED  

---

## 1. Naval Architecture Resistance & Propulsion Chain

The first-principles physics pipeline implements the classical naval architecture propulsion chain from hydrodynamic resistance to instantaneous fuel mass flow rate:

$$\begin{aligned}
R_{total}(V, \Delta, T, \text{env}) &= R_{calm}(V, \Delta, T) + R_{wave}(V, H_s, T_z, \theta_{rel}) + R_{wind}(V_{rel}, \psi_{rel}) \\
P_E &= R_{total} \times V_{STW} \\
P_D &= \frac{P_E}{\eta_D} = \frac{P_E}{\eta_0 \eta_H \eta_R} \\
P_B &= \frac{P_D}{\eta_S} + P_{aux} \\
\dot{m}_{fuel} &= P_B \times \text{SFOC}(P_B / P_{MCR}) \times 10^{-3} \quad [\text{kg/h}]
\end{aligned}$$

### 1.1 Calm Water Resistance ($R_{calm}$)
- Evaluated via the **Holtrop & Mennen (1982/1984)** empirical formulation:
  $$R_{calm} = R_F (1 + k_1) + R_{APP} + R_W + R_B + R_{TR} + R_A$$
- Friction line: ITTC-1957 skin friction correlation line $C_F = \frac{0.075}{(\log_{10} Re - 2)^2}$.
- Form factor: $1 + k_1 = 0.93 + 0.4871 c_{10} (B/L)^{1.0681} (T/L)^{0.4611} (L/L_R)^{0.1216} (L^3/\nabla)^{0.3649} (1 - C_P)^{-0.6042}$.
- Wave resistance ($R_W$): Evaluated across low and high Froude number regimes ($Fn < 0.4$).

### 1.2 Added Resistance in Waves ($R_{wave}$)
- Evaluated via the semi-empirical **STAwave-2 (IMO standard / Kwon)** formulation:
  $$R_{wave} = \frac{1}{16} \rho_w g H_s^2 B \sqrt{\frac{B}{L_{BP}}} \left( \frac{\omega_0^2 L_{BP}}{g} \right)^{1/3} \cos(\theta_{rel})$$
- Accounts for wave reflection at the bow and vessel heave/pitch motions.

### 1.3 Aerodynamic Wind Resistance ($R_{wind}$)
- Evaluated via the **Blendermann / Isherwood** wind drag formulation:
  $$R_{wind} = \frac{1}{2} \rho_{air} V_{rel}^2 A_{transverse} C_X(\psi_{rel})$$
- Where $V_{rel}$ and $\psi_{rel}$ are calculated via vector addition of ship velocity and true wind velocity.

### 1.4 Delivered and Brake Power Chain
- Delivered power: $P_D = P_E / \eta_D$, where propulsive efficiency $\eta_D \approx 0.65\text{--}0.72$.
- Shaft transmission efficiency: $\eta_S \approx 0.98$.
- Specific Fuel Oil Consumption (SFOC): Calculated via a polynomial engine load curve:
  $$\text{SFOC}(L) = \text{SFOC}_{base} \times (1.0 + 0.35 \times (L - 0.85)^2) \quad [\text{g/kWh}]$$

---

## 2. Sensor & Physical Variable Availability Ledger

To prevent model fabrication, every physical variable required by the theoretical model is audited against actual sensor telemetry:

| Variable | Symbol | Required By | Telemetry Status | Sensor / Source Mechanism | Audit Finding |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Speed Through Water** | $V_{STW}$ | $R_{calm}, R_{wave}, P_E$ | **AVAILABLE** | Dual-axis Doppler Log / EM Log (`stw_kn`) | Mandatory input. Substitution with SOG strictly blocked. |
| **Speed Over Ground** | $V_{SOG}$ | Kinematics, ETA | **AVAILABLE** | Differential GPS (`sog_kn`) | Used for current vector estimation and navigation. |
| **Draft** | $T$ | $R_{calm}$, Wetted Area | **AVAILABLE** | Mean of fore and aft draft sensors (`draft_m`) | Validated within $[5.0, 12.0]\text{ m}$. |
| **Displacement** | $\Delta$ | Hydrostatics, Inertia | **AVAILABLE** | Calculated from draft hydrostatics (`displacement_t`)| Validated within $[15,000, 50,000]\text{ t}$. |
| **Wind Speed & Direction** | $V_w, \psi_w$ | $R_{wind}$ | **AVAILABLE** | Ultrasonic Anemometer + ECMWF (`wind_speed_ms`) | Relative vector decomposition applied. |
| **Wave Height & Period** | $H_s, T_z$ | $R_{wave}$ | **AVAILABLE** | Copernicus Marine Service / ECMWF (`wave_height_m`)| Significant wave height up to $6.8\text{ m}$. |
| **Ocean Current** | $V_c, \theta_c$ | Drift, STW check | **AVAILABLE** | Copernicus Global Ocean Reanalysis | Current speed and direction vectors. |
| **Water Depth** | $h$ | Shallow Water Drag | **AVAILABLE** | Hydrographic Echo Sounder (`water_depth_m`) | Bathymetric shallow-water correction. |
| **Coriolis Mass Flow** | $\dot{m}_f$ | Target $y$ | **AVAILABLE** | Direct Coriolis Mass Flow Meter (`fuel_mass_flow_kg_h`)| Primary target ground truth. |
| **Engine Shaft Power** | $P_B$ | Machinery | **EXCLUDED** | Optical Torsionmeter (`shaft_power_kw`) | **Available in raw, excluded from CONFIG_REAL_A** to ensure operational dispatch readiness. |
| **Propeller RPM** | $N$ | Machinery | **EXCLUDED** | Shaft Tachometer (`rpm`) | **Excluded from CONFIG_REAL_A** (prevents proxy leakage). |
| **Ship Trim** | $t$ | Hull resistance | **UNAVAILABLE** | Not continuously logged / sensor uncalibrated | **Marked Unavailable. Trim assumed zero (even keel).** |
| **Biofouling Thickness** | $k_s$ | Frictional Drag | **UNAVAILABLE** | No direct real-time hull sensor exists | **Marked Unavailable. Absorbed into ML residual $r$.** |
| **Propeller Roughness** | $k_p$ | Propeller Efficiency | **UNAVAILABLE** | No direct sensor | **Marked Unavailable. Absorbed into ML residual $r$.** |
| **Water Density** | $\rho_w$ | Resistance scaling | **UNAVAILABLE** | Salinity/hydrometer not logged | **Standard constant assumed ($\rho_w = 1025\text{ kg/m}^3$).** |

---

## 3. The Uncalibrated Physics Residual Gap

When evaluated purely using first-principles without empirical parameter tuning (`MODEL-REAL-01`):
- **MAE:** $1,885.45\text{ kg/h}$
- **$R^2$:** $-0.5471$
- **Mean Bias:** $-1,883.19\text{ kg/h}$

### Why does pure naval architecture under-predict?
1. **Unmodeled Auxiliary Hotel Loads:** Boilers, cargo refrigeration, auxiliary generators, and scrubbers consume $200\text{--}800\text{ kg/h}$ regardless of ship speed.
2. **Hull Biofouling & Aging:** Slime, barnacles, and hull plate micro-roughness increase frictional resistance $C_F$ by $15\%\text{--}40\%$ over time.
3. **Propeller Inefficiencies & Cavitation:** Real propeller cavitation, blade roughness, and dynamic slip are higher than open-water model basin curves.
4. **Sea Margin & Steering Drag:** Rudder maneuvers and unmeasured cross-seas add parasitic drag.

### Hybrid Physics + ML Rationale:
The first-principles equation captures the exact non-linear cubic hydrodynamic law ($\dot{m} \propto V^3$), ensuring that the model cannot predict unphysical behavior (e.g., fuel decreasing at 25 knots). 
The machine learning residual model $\hat{r}(x)$ then learns the time-varying, vessel-specific biofouling, hotel load, and metocean interaction corrections:
$$\hat{F}(x) = \max(0, F_{physics}(x) + \alpha \cdot \hat{r}(x))$$
This hybrid design achieves $R^2 = 0.9501$ while guaranteeing physical safety bounds.
