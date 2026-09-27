# EGREEN QUANTA — OPERATIONAL LIMITATIONS & TECHNICAL BOUNDARIES
**SIH26138 — Quantum-Inspired Fuel Consumption Prediction and Green Fleet Optimization**
**Integrity Disclosure for SIH 2026 Evaluators & Marine Technical Auditors**

---

## 1. Statement of Technical Integrity

In accordance with maritime engineering ethics and scientific verification rigor, this document details the exact technical boundaries, assumptions, and limitations of the **EGREEN QUANTA** system.

EGREEN QUANTA is designed as a **decision-support advisory console** for fleet superintendents and ship operators. It is **not** an autonomous navigation autopilot, nor is it currently type-certified for safety-of-life-at-sea (SOLAS) equipment installations.

---

## 2. Explicit Operational Limitations

### 2.1 Telemetry Feed & Live Shipboard Connectivity
- **Current Status**: The system currently operates on **calibrated replay of recorded sea-trial telemetry** from the DTU/FuelCast research repository, augmented with deterministic operational presets.
- **Limitation**: There is no live NMEA 0183 / NMEA 2000 / Modbus TCP serial bus connected to physical shipboard fuel flow meters or GPS transponders in the current prototype.
- **HMI Safeguard**: The console explicitly labels all telemetry states as `CALIBRATED REPLAY` or `SIMULATION DATA`. It never fabricates simulated real-time telemetry or claims live satellite tracking when disconnected.

### 2.2 Alternative Fuel Modeling Basis
- **Current Status**: Modeling for alternative fuels (Bio-Methanol, Liquid Hydrogen, Green Ammonia, Fossil LNG) is computed using an **invariant shaft work energy conversion basis**:
  $$m_{\text{fuel}} = m_{\text{VLSFO}} \cdot \frac{\text{LHV}_{\text{VLSFO}}}{\text{LHV}_{\text{fuel}}}$$
  coupled with IMO MEPC.391(81) Well-to-Wake (WtW) lifecycle emission factors.
- **Limitation**: No measured physical fuel consumption data exists in the maritime industry for commercial cruise vessels operating on 100% liquid hydrogen or pure green ammonia at scale.
- **HMI Safeguard**: All alternative fuel outputs are strictly tagged with the badge `SCENARIO ESTIMATE`. The console never presents alternative fuel outcomes as "measured consumption".

### 2.3 Maritime Regulatory Certification
- **Current Status**: EGREEN QUANTA is an **academic and research prototype** submitted to Smart India Hackathon (SIH) 2026.
- **Limitation**: The software has not undergone Type Approval certification by classification societies (e.g., DNV, Lloyd's Register, American Bureau of Shipping, Bureau Veritas) under IEC 61174 (ECDIS) or ISO 16425 standards.
- **HMI Safeguard**: Prominent disclaimers state: `DECISION ADVISORY — HUMAN APPROVAL REQUIRED`. The system requires explicit human operator confirmation before committing any dispatch recommendation.

### 2.4 Autonomous Control & Actuator Interfaces
- **Current Status**: The optimization engine produces recommended setpoints (steaming speed, route demand assignment, bunker selection, shore power activation).
- **Limitation**: The system does not interface with Electronic Governor Controllers (ECUs), automated propeller pitch actuators, or bridge steering consoles. It does not possess direct throttle control.
- **Operational Protocol**: The master or fleet superintendent remains solely responsible for vessel navigation, safe speed in accordance with COLREGs Rule 6, and seamanship safety.

### 2.5 Training Data Scope & Envelope Extrapolation
- **Current Status**: Machine learning surrogate models are trained on chronological partitions of Danish passenger ferries, cruise vessels, and offshore support vessels.
- **Limitation**: Extrapolation to naval hull forms significantly outside the training domain (e.g., ultra-large container ships > 24,000 TEU, bulk carriers, planing catamarans) will trigger Out-of-Domain (OOD) detection.
- **HMI Safeguard**: When input parameters breach $d_{\text{env}} > 1.50$, the system automatically withholds the ML prediction, flags `OUT OF DOMAIN`, and diverts to physics-based reference models.

### 2.6 Dynamic Meteorological Forecasting (Weather Routing)
- **Current Status**: Voyage scenarios evaluate hydrodynamic resistance using user-specified wave height ($H_s$), wind speed ($V_w$), and water depth across voyage legs.
- **Limitation**: The prototype does not ingest live dynamic GRIB2 binary weather forecast grids or compute isochrone wave spectrum diffraction in real time.
- **HMI Safeguard**: All environmental parameters are clearly marked as `SCENARIO INPUTS` with full visibility in the parameters drawer.

### 2.7 Access Control & Security Model
- **Current Status**: Prototype role semantics (`OPERATOR`, `ENGINEER`, `ADMIN`) are implemented client-side for interface demonstration.
- **Limitation**: Enterprise-grade identity providers (OAuth2, SAML 2.0, multi-factor hardware tokens, RBAC database tables) are not deployed in this standalone evaluation environment.
- **HMI Safeguard**: The role selector is explicitly labeled `Access Control — Prototype simulation`.

---

## 3. Evaluator Summary

| Claim | Factually Supported? | Production Reality |
| :--- | :--- | :--- |
| "Predicts fuel with < 5% error on verified hulls" | **YES** | Verified: Test MAE 252.8 kg/h, $R^2 = 0.948$ on FuelCast test split |
| "Optimizes fleet multi-objectively in seconds" | **YES** | Verified: QIEA/QPSO converges in 2,500 evaluations on classical CPU |
| "Autonomously steers ships across the ocean" | **NO** | Disclaimed: Strictly advisory decision support with human approval |
| "Directly measured green hydrogen consumption" | **NO** | Disclaimed: Calculated as energy-equivalent scenario estimates |
| "Runs on a physical 1,000-qubit quantum computer" | **NO** | Disclaimed: Quantum-inspired algorithms running on classical hardware |
| "Zero mock data on operational dashboard" | **YES** | Verified: 100% of KPIs originate from executable Python backend |
