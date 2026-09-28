# SIH26138 — Dataset Target Provenance & Measurement Lineage Audit
**Document ID:** `PROVENANCE-TARGET-001`  
**Audit Date:** `2026-09-12`  
**Platform Version:** `0.2.1`  
**Auditor Role:** Forensic Scientific Data Auditor  

---

## 1. Executive Summary & Provenance Classification

The central research mandate for SIH26138 is to validate the instantaneous fuel prediction task:
$$\hat{F}(t) = f(X(t))$$
where the target $F(t)$ is the true instantaneous fuel mass flow rate ($\text{kg/h}$ or $\text{kg/s}$).

A critical pitfall in previous predictive modeling literature is **circular target derivation**: training a machine learning model to predict a target that was synthetically generated from an analytical formula (such as Holtrop-Mennen resistance multiplied by a polynomial Specific Fuel Consumption curve). Such an evaluation merely measures the ML model's ability to invert the generating formula, yielding zero scientific evidence of operational real-world validity.

This audit establishes the exact physical and mechanical provenance of target variables across all examined datasets.

---

## 2. Summary Provenance Table

| Dataset | Target Column Name | Engineering Units | Sampling Frequency | Provenance Classification | Physical Measurement Mechanism | Sensor Lineage & Aggregation | Circularity Risk |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- | :---: |
| **FuelCast** | `Consumer_Total_MomentaryFuel` | $\text{kg/s}$ | $5\text{ min}$ ($\Delta t = 300\text{ s}$) | **`REAL_OBSERVED`** | Dual Coriolis Mass Flow Meters (KROHNE OPTIMASS) | $\Delta \dot{m} = \sum (\dot{m}_{\text{inlet}} - \dot{m}_{\text{outlet}})$ across all consumers | **ZERO** (Direct mass flow sensors) |
| **M/S Smyril** | `fuelVolumeFlowRate` $\times$ `fuelDensity` | $\text{L/s} \times \text{kg/L} \to \text{kg/s}$ | $\sim 1.0\text{ s}$ ($\sim 1\text{ Hz}$) | **`REAL_OBSERVED`** | Positive Displacement Flow Meter + Inline Resonant Density Sensor | $\dot{m}(t) = \dot{V}_{\text{fuel}}(t) \cdot \rho_{\text{fuel}}(t)$ | **ZERO** (Direct physical volume & density) |
| **Shifts 2.0** | `power` | $\text{kW}$ | $1\text{ min}$ ($\Delta t = 60\text{ s}$) | **`REAL_OBSERVED`** *(Power Only)* | Optical / Strain Gauge Shaft Torsionmeter | $P_{\text{shaft}}(t) = 2\pi \cdot n_{\text{shaft}}(t) \cdot Q_{\text{shaft}}(t)$ | **N/A** (NO fuel target present) |
| **PONTOS-Hub** | `enginemain_fuelcons_lph` | $\text{L/h}$ | $1\text{ s} - 1\text{ min}$ | **`NOT_PUBLICLY_VERIFIED`** | Flow meter / ECU fuel rack position | Unknown (Telemetry stream is authenticated/gated) | High (Data unverified) |
| **UTAS-WMU** | `fuel_consumption_tonnes` | $\text{tonnes/voyage}$ | $24\text{ h}$ / Voyage | **`REAL_DERIVED`** | Bunker tank soundings / Daily noon reports | Daily manual tank soundings averaged over 24 hours | Moderate (Averaging smears out all hydrodynamics) |

---

## 3. Forensic Deep Dive: FuelCast Target Lineage

### 3.1 Target Variable Definition
- **Column Name**: `Consumer_Total_MomentaryFuel`
- **Native Stored Units**: $\text{kg/s}$ (Double-precision float `f64`)
- **Conversion to SIH26138 Canonical Unit**:
  $$\text{fuel\_mass\_flow\_kg\_h} = \text{Consumer\_Total\_MomentaryFuel} \times 3600.0$$

### 3.2 Sensor Apparatus & Physical Lineage
From the primary publication (Justus Viga, Penelope Mueck, Alexander Löser, Torben Weis, arXiv:2510.08217v1, Section 3.2):
> *"Each ship has multiple consumers that contribute to the total momentary fuel consumption. These can be engines for propulsion and power generation or other consumer like boilers and incinerators. For the measurement of consumption we use accurate KROHNE Coriolis mass-flow meters. For each engine we measure inlet and outlet and combine these using the difference to calculate exact consumption."*

### 3.3 Operating Principle of the Coriolis Flow Measurement System
Marine heavy fuel oil (HFO/VLSFO) and marine diesel oil (MDO) recirculate in continuous pressurized loops to keep the fuel heated and maintain injection viscosity.
Consequently, an engine supply line carries both consumed fuel and surplus recirculating fuel:
1. An **inlet Coriolis meter** measures total mass flow entering the engine rail: $\dot{m}_{\text{inlet}}$ ($\text{kg/s}$).
2. An **outlet Coriolis meter** measures surplus unburnt fuel returning to the day tank: $\dot{m}_{\text{outlet}}$ ($\text{kg/s}$).
3. The KROHNE EcoMATE™ engine monitoring computer computes the instantaneous consumed fuel mass flow in real time:
   $$\dot{m}_{\text{engine}, i}(t) = \dot{m}_{\text{inlet}, i}(t) - \dot{m}_{\text{outlet}, i}(t)$$
4. The total momentary fuel consumption across all consumers (engines, auxiliary generators, boilers) is aggregated:
   $$F_{\text{total}}(t) = \sum_{i \in \text{engines}} \dot{m}_{\text{engine}, i}(t) + \sum_{j \in \text{boilers}} \dot{m}_{\text{boiler}, j}(t)$$
5. The measurement directly registers **inertial mass flow** via the Coriolis effect (vibrating measuring tube phase shift), completely eliminating temperature-induced density expansion errors that plague volumetric flow meters.
6. Target Provenance Classification: **`REAL_OBSERVED`** (Tier 1 physical ground truth).

### 3.4 Target Distribution & Sanity Audit
Auditing the 173,986 actual downloaded records:
- **Missing / Null Count**: Exactly 0 across all three vessels ($0.00\%$).
- **Zero Values**:
  - `CPS_Poseidon`: 27 zero records ($0.03\%$).
  - `CPS_Triton`: 20 zero records ($0.08\%$).
  - `OSS_Ceto`: 27 zero records ($0.06\%$).
  These correspond to cold harbor shutdown / shore power periods.
- **Physical Rate Bounds**:
  - `CPS_Poseidon` (70,000 GT Cruise Ship): Mean = $0.782\text{ kg/s}$ ($2,815.4\text{ kg/h}$); Max = $2.392\text{ kg/s}$ ($8,609.8\text{ kg/h}$). This aligns with multi-megawatt medium-speed diesel generator plants at sea.
  - `CPS_Triton` (11,000 GT Small Cruise Ship): Mean = $0.176\text{ kg/s}$ ($635.1\text{ kg/h}$); Max = $0.352\text{ kg/s}$ ($1,265.8\text{ kg/h}$).
  - `OSS_Ceto` (24,000 GT Offshore Support Ship): Mean = $0.188\text{ kg/s}$ ($675.6\text{ kg/h}$); Max = $0.750\text{ kg/s}$ ($2,700.0\text{ kg/h}$).

---

## 4. Forensic Deep Dive: M/S Smyril Target Lineage

### 4.1 Target Variable Definition
- **File Components**:
  - `fuelVolumeFlowRate.csv`: Volumetric flow rate $\dot{V}(t)$ in Liters per second ($\text{L/s}$).
  - `fuelDensity.csv`: Inline measured fuel density $\rho(t)$ in kilograms per Liter ($\text{kg/L}$).
  - `fuelTemp.csv`: Inline fuel temperature $T(t)$ in degrees Celsius ($^\circ\text{C}$).
- **Instantaneous Mass Flow Synthesis**:
  $$\dot{m}_{\text{fuel}}(t) = \dot{V}(t) \cdot \rho(t) \quad [\text{kg/s}]$$
  $$\text{fuel\_mass\_flow\_kg\_h}(t) = \dot{V}(t) \cdot \rho(t) \times 3600.0 \quad [\text{kg/h}]$$

### 4.2 Physical Apparatus & Calibration
- As documented by Petersen et al. (COMPIT'11 and DTU 2011 documentation):
  - Volumetric flow rate was measured using positive displacement flow meters installed on the main engine fuel supply lines.
  - An inline density sensor continuously registered the temperature-dependent density of the heavy fuel oil ($\sim 0.947\text{ kg/L}$ at operating temperature).
  - Data was logged at 1-second resolution via an onboard industrial PC interfaced with the automation system.
- Target Provenance Classification: **`REAL_OBSERVED`** (Calculated from physical volume and physical density sensors).

---

## 5. Forensic Deep Dive: Shifts 2.0 Target Lineage

### 5.1 Target Variable Definition
- **Column Name**: `power`
- **Native Stored Units**: $\text{kW}$ (Kilowatts)
- **Sensor Source**: DeepSea Technologies IoT edge device (`Neuro`) interfacing with the onboard propulsion shaft torsionmeter.
- **Physical Mechanism**: Optical or strain gauge measurement of shaft torsional deflection under load:
  $$P_{\text{shaft}} = 2\pi \cdot n_{\text{shaft}} \cdot Q_{\text{shaft}}$$
  where $n_{\text{shaft}}$ is rotational speed (rev/s) and $Q_{\text{shaft}}$ is torque ($\text{N}\cdot\text{m}$).
- Target Provenance Classification: **`REAL_OPERATIONAL_POWER_DATA`**.
- **Crucial Negative Finding**: **NO FUEL FLOW DATA EXISTS IN SHIFTS 2.0**.
  It is physically impossible to calibrate or validate a fuel consumption model $\hat{F}(t)$ against Shifts 2.0 without injecting an unverified, hypothetical Specific Fuel Consumption (SFC) curve. Doing so would re-introduce synthetic bias.

---

## 6. Synthesis: Target Usability for $X(t) \to F(t)$

1. **FuelCast** is the **gold standard primary target** for operational fuel mass flow validation:
   - Measured by world-class industrial Coriolis mass flow meters.
   - True differential inlet minus outlet mass accounting.
   - Covers three independent vessels with zero missing target rows.
2. **M/S Smyril** provides an **independent high-frequency validation target**:
   - Continuous 1-second physical volume and density logging.
   - Provides granular transient and steady-state hydrodynamic responses.
3. **Shifts 2.0** must **not be used as a fuel-flow target**:
   - Classified exclusively as an auxiliary benchmark for hydrodynamic resistance and shaft power modeling.
