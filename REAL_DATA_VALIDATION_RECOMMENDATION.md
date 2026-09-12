# SIH26138 — Real Maritime Data Validation Strategy & Architecture Recommendation
**Document ID:** `STRAT-VALIDATION-001`  
**Audit Date:** `2026-09-12`  
**Platform Version:** `0.2.1`  
**Auditor Role:** Forensic Scientific Data Auditor  

---

## 1. Executive Summary & Final Scientific Recommendation

Based on forensic verification of primary empirical artifacts (T1/T2), the project recommends:

### **RECOMMENDED STRATEGY: OPTION 2 — DUAL-TIER DATASET STACK**

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    SIH26138 REAL-DATA VALIDATION STACK                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│   TIER 1: PRIMARY OPERATIONAL FUEL FLOW BENCHMARK                               │
│   Dataset: FuelCast (krohnedigital/FuelCast)                                    │
│   Role: Synchronous X(t) -> F(t) Fuel Consumption Validation                    │
│   Telemetry: 173,986 records across 3 physical commercial vessels               │
│   Target: Coriolis mass flow (Consumer_Total_MomentaryFuel, kg/s)               │
│   Sampling: 5-minute steady-state operational sequences                         │
│                                                                                 │
│   TIER 2: HIGH-FREQUENCY HYDRODYNAMIC BENCHMARK                                │
│   Dataset: M/S Smyril (DTU Cognitive Systems / Petersen)                       │
│   Role: Hydrodynamic Resistance, Direct Doppler STW & Wave Validation           │
│   Telemetry: ~5,184,000 records at ~1.0 Hz continuous sensor logging             │
│   Target: Inline Volume Flow * Fuel Density (L/s * kg/L)                        │
│   Sensors: Direct Acoustic Doppler Log STW, Inclinometer Trim, Draft Port/Stbd  │
│                                                                                 │
│   TIER 3: AUXILIARY PROPULSION PHYSICS BENCHMARK                                │
│   Dataset: Shifts 2.0 (vpower)                                                  │
│   Role: Pure Shaft Power Validation X(t) -> P_shaft(t) (Zero SFC coupling)     │
│   Target: Optical Shaft Torsionmeter Power (kW)                                 │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

This stack cleanly separates:
1. **Direct Fuel Mass Flow State Estimation**: Handled by **FuelCast** with dual-sensor Coriolis ground truth.
2. **High-Frequency Hydrodynamics & Wave Response**: Handled by **M/S Smyril** with true 1-second Doppler STW and inclinometer trim.
3. **Pure Propulsion & Torsionmeter Physics**: Handled by **Shifts 2.0** without corrupting fuel-flow metrics with unverified Specific Fuel Consumption (SFC) formulas.

---

## 2. Final Candidate Classification & Decision Matrix

| Candidate Dataset | Forensic Classification | Recommended Operational Role | Strategic Decision |
| :--- | :--- | :--- | :---: |
| **FuelCast** | `REAL_OBSERVED` (Coriolis mass flow) | Primary benchmark for instantaneous $X(t) \to F(t)$ | **`GO WITH LIMITATIONS`** |
| **M/S Smyril** | `REAL_OBSERVED` (Volume $\times$ Density) | Benchmark for hydrodynamic resistance & high-frequency dynamics | **`GO WITH LIMITATIONS`** |
| **Shifts 2.0** | `REAL_OPERATIONAL_POWER_DATA` (Power only) | Auxiliary benchmark for shaft power $X(t) \to P(t)$ | **`AUXILIARY ONLY`** |
| **PONTOS-Hub** | `NOT_PUBLICLY_VERIFIED` (Telemetry Gated) | None (Data blocked behind proprietary JWT token) | **`DO NOT USE`** |
| **UTAS-WMU** | `TASK_INCOMPATIBLE` (Voyage Aggregates) | None (Incapable of instantaneous state estimation) | **`DO NOT USE`** |

---

## 3. Final Scientific Rankings

### RANK A: Best Verified Dataset for Direct Fuel-Flow Validation
**Winner: FuelCast (`krohnedigital/FuelCast`)**
- *Justification*: Direct industrial Coriolis mass flow measurement (`Consumer_Total_MomentaryFuel` in kg/s) computed via calibrated inlet minus outlet differential flow. 173,986 records, zero nulls on target, verified across 3 physical commercial hulls.

### RANK B: Best Verified Dataset for Hydrodynamic / Physics Validation
**Winner: M/S Smyril (`DTU Cognitive Systems`)**
- *Justification*: Direct Acoustic Doppler speed log (`longitudinalWaterSpeed` in knots) sampled at ~1.0 Hz, coupled with dual level sensors (`level1median`, `level2median`) and dynamic trim angle (`inclinometer-raw`). Captures fine-grained hull-water interaction.

### RANK C: Best Verified Dataset for Cross-Vessel Generalization
**Winner: FuelCast (`krohnedigital/FuelCast`)**
- *Justification*: The only publicly available, fully verified operational dataset containing multiple distinct physical commercial vessels:
  - `CPS_Poseidon`: 70,000 GT Large Cruise Ship
  - `CPS_Triton`: 11,000 GT Medium Cruise Ship
  - `OSS_Ceto`: 24,000 GT Offshore Supply Ship

### RANK D: Best Practical SIH Dataset
**Winner: FuelCast (`krohnedigital/FuelCast`)**
- *Justification*: Pre-packaged into high-performance Apache Parquet format (16.7 MB total download), pre-joined with Copernicus Marine Environment Monitoring Service (CMEMS) wave/current hindcasts and OpenMeteo satellite weather reanalysis. Ready for schema-mapped ingestion.

### RANK E: Best Dataset Stack
**Winner: Dual Stack: FuelCast (Primary Operational) + M/S Smyril (Hydrodynamic Validation)**
- *Justification*: Provides end-to-end empirical coverage from high-frequency wave-induced speed loss (~1 Hz) to steady-state multi-vessel operational cruise consumption (5-min).

---

## 4. Feature Leakage Quarantine: Config-Real-A vs Config-Real-B

Fuel flow is mechanically determined by engine shaft power and brake specific fuel consumption:
$$\dot{m}_{\text{fuel}}(t) \approx P_{\text{shaft}}(t) \times \text{BSFC}(P_{\text{shaft}}(t))$$

Including measured shaft power or engine load as an input feature trivializes the machine learning task into fitting a one-dimensional engine fuel map, completely bypassing the ship hydrodynamics (hull resistance, wave added resistance, aerodynamic drag).

To prevent scientific deception, all future real-data experiments must maintain **strict feature quarantine**:

```
                              ┌─────────────────────────────┐
                              │     ALL RAW TELEMETRY       │
                              └──────────────┬──────────────┘
                                             │
                     ┌───────────────────────┴───────────────────────┐
                     ▼                                               ▼
     ┌───────────────────────────────┐               ┌───────────────────────────────┐
     │         CONFIG-REAL-A         │               │         CONFIG-REAL-B         │
     │     Kinematic + Environmental │               │   Full Operational Telemetry  │
     │      (Pure Hydrodynamic)      │               │     (Includes Propulsion)     │
     ├───────────────────────────────┤               ├───────────────────────────────┤
     │ • Speed Through Water (STW)   │               │ • All CONFIG-REAL-A features  │
     │ • Speed Over Ground (SOG)     │               │ • Propeller Shaft Power (kW)  │
     │ • True Heading / Bearing      │               │ • Engine Shaft Power (kW)     │
     │ • Static Draft (Fwd/Aft)      │               │ • Propeller RPM               │
     │ • Displacement / Hull Class   │               │ • Engine Rotation Speed (RPM) │
     │ • Significant Wave Height     │               │ • Propeller Shaft Torque (Nm) │
     │ • Peak Wave Period & Direction│               │ • Engine Load (% MCR)         │
     │ • True Wind Speed & Direction │               │                               │
     │ • Current Speed & Direction   │               │                               │
     │ • Bathymetric Sea Depth       │               │                               │
     │                               │               │                               │
     │ [STRICTLY EXCLUDED]:          │               │ [STRICTLY EXCLUDED]:          │
     │ ❌ Shaft Power (kW)           │               │ ❌ Consumer Momentary Fuels   │
     │ ❌ Engine Load (%)            │               │ ❌ Fuel rack position         │
     │ ❌ Shaft Torque (Nm)          │               │ ❌ Direct target derivatives  │
     │ ❌ Shaft RPM                  │               │                               │
     └───────────────────────────────┘               └───────────────────────────────┘
```

### Scientific Questions Answered by the Two Configurations:
- **CONFIG-REAL-A** evaluates: *"Can environmental conditions, vessel loading, and navigation speed accurately predict fuel demand without engine room sensors?"* (Essential for pre-voyage chartering and route weather routing).
- **CONFIG-REAL-B** evaluates: *"Given measured propulsion power delivered to the water, how accurately does the engine conversion model predict fuel burn?"* (Essential for machinery health monitoring and hull fouling diagnosis).

---

## 5. Real-Data Experimental Validation Suite

When Phase 2 transition execution commences, the verified data stack can support the following 7 validation protocols:

### REAL-PRED-01: Temporal Holdout Validation
- **Protocol**: Train on the first 70% of chronological timesteps; evaluate on the final 30% held-out chronological sequence for each vessel.
- **Scientific Purpose**: Detect degradation caused by seasonal weather shifts and gradual biofouling.

### REAL-PRED-02: Leave-Vessel-Out (LVO) Generalization
- **Protocol**: Train strictly on 2 vessels (e.g. `CPS_Poseidon` + `OSS_Ceto`); test strictly on the unseen held-out vessel (`CPS_Triton`).
- **Critical Caution**: Because the fleet consists of 3 distinct hulls (2 cruise ships, 1 offshore supply vessel), LVO represents a **vessel-domain shift**, not a sister-vessel test. Performance drops must be analyzed as domain divergence, not model failure.

### REAL-PRED-03: Physics vs ML Baseline Comparison
- **Protocol**: Benchmark the Holtrop-Mennen physical resistance model against LightGBM and Random Forest on real data under `CONFIG-REAL-A`.
- **Falsification Criterion**: If uncalibrated physics achieves higher error than simple mean baselines, document Holtrop-Mennen calibration limits on non-standard hulls.

### REAL-PRED-04: Hybrid Residual Architecture Falsification
- **Protocol**: Test whether $\hat{F}_{\text{hybrid}}(t) = F_{\text{physics}}(t) + \hat{\epsilon}_{\text{ML}}(t)$ outperforms pure ML on real telemetry.
- **Falsification Rule**: As established in Phase 2.1, do not force the hybrid model to win. If pure ML achieves lower MAE due to physics bias, report the finding transparently.

### REAL-PRED-05: Uncertainty Prediction Interval Calibration
- **Protocol**: Evaluate nominal 90% conformal / quantile prediction intervals on real sensor noise.
- **Validation Metric**: Prediction Interval Coverage Probability (PICP) must fall within $[86.0\%, 94.0\%]$ with tight Mean Prediction Interval Width (MPIW).

### REAL-PRED-06: Environmental Domain Shift Testing
- **Protocol**: Partition test sets into calm seas ($H_s < 1.0\text{ m}$) vs heavy weather ($H_s > 3.0\text{ m}$).
- **Evaluation**: Measure whether error scales linearly or exponentially under hydrodynamic disturbance.

### REAL-PRED-07: Optimization Validity Envelope Verification
- **Protocol**: Feed real data clusters into the Phase 2.2 `DomainChecker` and evaluate `SafeFuelObjective` penalty activation on real out-of-distribution states.
